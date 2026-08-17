"""Soudci věrnosti extrakce (spec § 5.4, I‑9).

Soudce dostane zdrojovou větu a výrok (v čitelném renderu) a řekne, zda věta
výrok **tvrdí**, **netvrdí**, nebo jen **částečně** (výrok je hrubší / má
navíc výchozí volbu, kterou věta neurčuje). Je to *měřicí nástroj* — nikdy
nezapisuje výrok a nerozhoduje verdikt (I‑9). Verze promptu jde do zprávy,
aby čísla z různých běhů byla srovnatelná.

Implementace:
    RecordedJudge  – testy: slovník otisk → (verdikt, poznámka)
    OllamaJudge    – lokální model přes `POST /api/chat` (bez závislostí)
    ClaudeJudge    – Anthropic SDK (líný import; extra `bench[judge]`)
    CachedJudge    – obal, který si pamatuje verdikty podle (otisk, soudce,
                     verze promptu) v JSON souboru — opakované běhy nesoudí
                     tytéž výroky znovu
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal, Protocol

Verdikt = Literal["tvrdí", "netvrdí", "částečně"]
VERDIKTY: tuple[Verdikt, ...] = ("tvrdí", "netvrdí", "částečně")

PROMPT_VERSION = "1"

JUDGE_PROMPT_V1 = """Jsi soudce věrnosti extrakce. Dostaneš jednu českou větu a jeden výrok, který z ní systém vytěžil.
Výrok má tvar predikát(role: hodnota, …); „kdo“ = podmět/konatel, „co“ = předmět, „kde/kdy/kam/odkud/komu/čím/s_kým“ = okolnosti,
„⟨member⟩“ = jedinec patří do skupiny, „⟨subset⟩“ = skupina je podmnožinou, „∀“ = obecné tvrzení o všech, „∃“ = o některých, „·“ = konkrétní jedinec.
Rozhodni POUZE podle toho, co věta doslova tvrdí (žádné vlastní znalosti o světě):
- „tvrdí“ — věta výrok skutečně tvrdí (role sedí, polarita sedí, jména sedí);
- „netvrdí“ — věta výrok netvrdí nebo tvrdí něco jiného (zaměněné role, jiná osoba, opačná polarita, výrok o něčem, co ve větě není);
- „částečně“ — jádro sedí, ale výrok něco zjednodušuje nebo přidává, co věta neurčuje (např. chybí důležitá okolnost, kvantifikátor „∀“ tam, kde věta mluví jen o jednom případu, časové určení přiřazené jinému ději).
Příklady:
1) Věta: „Alois Jirásek se narodil v Hronově.“ Výrok: narodit_se(kdo: Alois Jirásek, kde: Hronov) → tvrdí
2) Věta: „Jan pokřtil Ježíše v Jordánu.“ Výrok: pokřtít(kdo: Ježíš, co: Jan) → netvrdí (zaměněné role)
3) Věta: „V roce 1888 Jirásek přesídlil do Prahy.“ Výrok: přesídlit(kdo: Jirásek, kam: Praha) → částečně (chybí rok, jinak sedí)
4) Věta: „Pes štěká.“ Výrok: štěkat(kdo: ∀pes) → tvrdí (generické tvrzení)
5) Věta: „Petr řekl, že Marie přijde.“ Výrok: přijít(kdo: Marie) → netvrdí (věta tvrdí jen, že to Petr řekl)
Odpověz jen JSON: {"verdikt": "tvrdí" | "netvrdí" | "částečně", "pozn": "krátké zdůvodnění česky"}"""


def fingerprint(render: str, sentence: str) -> str:
    """Otisk (výrok, věta) — klíč lidských odpovědí a keše soudce."""
    return hashlib.sha1(f"{render}\n{sentence}".encode()).hexdigest()[:16]


class Judge(Protocol):
    """Rozhraní soudce."""

    name: str

    def judge(self, render: str, sentence: str, context: str = "") -> tuple[Verdikt, str]:
        """Posuď výrok proti větě.

        Args:
            render: čitelný výrok, např. `narodit_se(kdo: Alois Jirásek, kde: Hronov)`.
            sentence: zdrojová věta.
            context: volitelný kontext (předchozí věta, téma) — soudce ho smí
                použít jen k rozřešení zájmen, ne k doplnění faktů.
        Returns:
            (verdikt, poznámka)
        """


def _parse_verdict(text: str) -> tuple[Verdikt, str]:
    """Vytáhni JSON verdikt z odpovědi modelu (tolerantně: i když kolem je text)."""
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            v = str(d.get("verdikt", "")).strip().lower()
            for k in VERDIKTY:
                if v.startswith(k[:5]):
                    return k, str(d.get("pozn", ""))
        except json.JSONDecodeError:
            pass
    low = text.lower()
    for k in ("netvrdí", "částečně", "tvrdí"):
        if k in low:
            return k, text.strip()[:200]  # type: ignore[return-value]
    return "částečně", "neparsovatelná odpověď: " + text.strip()[:200]


def _user_message(render: str, sentence: str, context: str) -> str:
    ctx = f"\nKontext (jen pro zájmena): {context}" if context else ""
    return f"Věta: „{sentence}“{ctx}\nVýrok: {render}\nOdpověz JSON."


class RecordedJudge:
    """Soudce pro testy: verdikty jsou nahrané podle otisku (viz `audit.fingerprint`)."""

    name = "recorded"

    def __init__(self, table: dict[str, tuple[str, str]]) -> None:
        self.table = table
        self.calls = 0

    def judge(self, render: str, sentence: str, context: str = "") -> tuple[Verdikt, str]:  # pylint: disable=unused-argument
        """Vrať nahraný verdikt (KeyError, když otisk chybí — test má chybu)."""
        self.calls += 1
        v, note = self.table[fingerprint(render, sentence)]
        return v, note  # type: ignore[return-value]


class OllamaJudge:
    """Lokální model přes Ollama (`/api/chat`, teplota 0, bez „thinking“, JSON)."""

    def __init__(self, model: str = "qwen3.6:27b-mlx", endpoint: str = "http://127.0.0.1:11434", timeout: float = 180.0) -> None:
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.name = f"ollama:{model}"

    def judge(self, render: str, sentence: str, context: str = "") -> tuple[Verdikt, str]:
        """Jeden dotaz na Ollamu; chyba spojení → `RuntimeError` (audit pokračuje bez soudce)."""
        body = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": "json",
            "options": {"temperature": 0, "num_predict": 200},
            "messages": [
                {"role": "system", "content": JUDGE_PROMPT_V1},
                {"role": "user", "content": _user_message(render, sentence, context)},
            ],
        }
        req = urllib.request.Request(self.endpoint + "/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Ollama soudce nedostupný: {exc}") from exc
        text = str(data.get("message", {}).get("content", ""))
        return _parse_verdict(text)


class ClaudeJudge:
    """Soudce přes Anthropic SDK (`pip install -e '.[judge]'`); klíč z prostředí
    nebo profilu `ant auth login`. Model výchozí `claude-opus-5`."""

    def __init__(self, model: str = "claude-opus-5") -> None:
        import anthropic  # pylint: disable=import-outside-toplevel,import-error
        self._client = anthropic.Anthropic()
        self.model = model
        self.name = f"claude:{model}"

    def judge(self, render: str, sentence: str, context: str = "") -> tuple[Verdikt, str]:
        """Jeden dotaz na Claude se strukturovaným JSON výstupem; odmítnutí → „částečně“ s poznámkou."""
        resp = self._client.beta.messages.create(
            model=self.model,
            max_tokens=300,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=JUDGE_PROMPT_V1,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": {
                "type": "object",
                "properties": {"verdikt": {"type": "string", "enum": list(VERDIKTY)}, "pozn": {"type": "string"}},
                "required": ["verdikt", "pozn"], "additionalProperties": False}}},
            messages=[{"role": "user", "content": _user_message(render, sentence, context)}],
        )
        if resp.stop_reason == "refusal":
            return "částečně", "soudce odmítl (refusal)"
        text = next((b.text for b in resp.content if b.type == "text"), "")
        return _parse_verdict(text)


class CachedJudge:
    """Obal: verdikty podle (otisk, soudce, verze promptu) v JSON souboru."""

    def __init__(self, inner: Judge, path: Path) -> None:
        self.inner = inner
        self.path = path
        self.name = inner.name
        self._data: dict[str, list[str]] = {}
        if path.exists():
            self._data = json.loads(path.read_text(encoding="utf-8"))
        self.hits = 0
        self.misses = 0

    def _key(self, render: str, sentence: str) -> str:
        return f"{fingerprint(render, sentence)}|{self.name}|v{PROMPT_VERSION}"

    def judge(self, render: str, sentence: str, context: str = "") -> tuple[Verdikt, str]:
        """Z keše, nebo od vnitřního soudce (a do keše)."""
        k = self._key(render, sentence)
        if k in self._data:
            self.hits += 1
            v, note = self._data[k]
            return v, note  # type: ignore[return-value]
        self.misses += 1
        v, note = self.inner.judge(render, sentence, context)
        self._data[k] = [v, note]
        return v, note

    def flush(self) -> None:
        """Zapiš keš na disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")


def make_judge(cfg: dict) -> Judge | None:
    """Soudce podle `config.json` (`judge.kind`: none | ollama | claude), s keší."""
    j = cfg.get("judge", {})
    kind = j.get("kind", "none")
    inner: Judge | None
    if kind == "ollama":
        inner = OllamaJudge(j.get("model", "qwen3.6:27b-mlx"), j.get("endpoint", "http://127.0.0.1:11434"))
    elif kind == "claude":
        inner = ClaudeJudge(j.get("model", "claude-opus-5"))
    else:
        return None
    from bench.data import ROOT  # pylint: disable=import-outside-toplevel
    return CachedJudge(inner, ROOT / cfg.get("mereni", "mereni") / "audit-cache.json")
