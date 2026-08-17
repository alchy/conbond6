"""Sady dokumentů a zlatých otázek pro bench.

Proč zvlášť: data leží mimo repo (korpus conBond2 se klonuje do `data/`,
conBondCorpus je v `~/Projects`), zlaté otázky s hlavou a patou leží
**v repu** (`bench/gold/`, viz `gold.py`) — bench musí umět říct, nad
čím přesně běžel (otisk obsahu jde do zprávy, I‑7).

Sady:
    wiki    – 66 wiki dokumentů conBond2 (`data/raw/*.txt`) + kurátorované otázky
              `etalon` (40) a `conbond` (95) + vyfiltrované automatické `otazky-filtr`
    korpus  – conBondCorpus (35 dokumentů: NZ po knihách, spisovatelé, věda,
              Vesmír, Hudba) + 120 otázek s číslem věty a lemmatem odpovědi
    cb4     – v v1 není (texty conbond4 se překrývají s `wiki`, zlatá sada 135
              otázek není v čitelném formátu) — `load_sada` vrátí [] s varováním

Vstup: `bench/config.json` (cesty). Výstup: seznam `Doc` s otázkami.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG_PATH = HERE / "config.json"


@dataclass
class Question:
    """Jedna zlatá otázka: text, očekávané řetězce (stačí jeden), sada,
    případně číslo věty s odpovědí v původním číslování sady (jen orientačně —
    dosah se počítá nad naším číslováním, viz `metrics.reach`)."""

    q: str
    expect: list[str]
    sada: str
    sent_no: int | None = None
    kind: str = ""
    #: kurátorovaná = člověk ji napsal nebo ověřil; automatická = generátor + filtr
    curated: bool = True


@dataclass
class Doc:
    """Dokument pro bench: jméno, sada, text (řádky = odstavce/věty jako v raw),
    otázky, cesta (kvůli otisku)."""

    name: str
    sada: str
    text: str
    questions: list[Question] = field(default_factory=list)
    path: Path | None = None
    #: jméno tématu (kotva pro dosah), např. „Alois Jirásek“ z `alois_jirásek`
    topic: str = ""

    def words(self) -> int:
        """Počet slov textu (jmenovatel knowledge yield)."""
        return sum(len(line.split()) for line in self.text.splitlines())


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Načti `bench/config.json`; relativní cesty jsou vůči kořeni repa."""
    cfg = json.loads(path.read_text(encoding="utf-8"))
    return cfg


def _abs(p: str) -> Path:
    q = Path(p).expanduser()
    return q if q.is_absolute() else ROOT / q


def ensure_wiki_corpus(cfg: dict[str, Any]) -> Path:
    """Korpus conBond2 se klonuje mělce do `data/corpus/conBond2`, když chybí."""
    root = _abs(cfg["wiki"]["root"])
    if not root.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", cfg["wiki"]["git"], str(root)], check=True)
    return root


def topic_from_name(name: str) -> str:
    """`alois_jirásek` → „Alois Jirásek“ (kotva pro dosah u životopisů)."""
    return " ".join(w.capitalize() for w in name.split("_"))


def _gold_json(name: str) -> list[dict[str, Any]]:
    p = HERE / "gold" / name
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def load_wiki(cfg: dict[str, Any], *, only: list[str] | None = None, with_auto: bool = True) -> list[Doc]:
    """Dokumenty `wiki` s otázkami ze tří sad; bez otázek se dokument vynechá
    (bench měří i ingest, ale bez QA by číslo nemělo protějšek — dokumenty
    bez otázek se přidají jen na výslovné `--dok`)."""
    root = ensure_wiki_corpus(cfg)
    raw = root / cfg["wiki"]["raw"]
    by_doc: dict[str, list[Question]] = {}
    for item in _gold_json("etalon.json"):
        by_doc.setdefault(str(item["dok"]), []).append(Question(item["q"], list(item["expect"]), "etalon", kind=str(item.get("kind", ""))))
    for item in _gold_json("conbond.json"):
        if not item.get("src"):
            continue  # honest-negative bez dokumentu („Kdo napsal Hamleta?“ → nevím) — v1 mimo bench
        by_doc.setdefault(str(item["src"]), []).append(Question(item["q"], list(item["expect"]), "conbond", kind=str(item.get("kind", ""))))
    if with_auto:
        for item in _gold_json("otazky-filtr.json"):
            by_doc.setdefault(str(item["dok"]), []).append(Question(item["q"], list(item["expect"]), "otazky", sent_no=item.get("veta"), kind=str(item.get("typ", "")), curated=False))
    names = sorted(by_doc) if not only else list(only)
    docs: list[Doc] = []
    for name in names:
        p = raw / f"{name}.txt"
        if not p.exists():
            print(f"bench: dokument {name} v {raw} není — přeskočen", file=sys.stderr)
            continue
        docs.append(Doc(name, "wiki", p.read_text(encoding="utf-8"), by_doc.get(name, []), p, topic_from_name(name)))
    return docs


def load_korpus(cfg: dict[str, Any], *, only: list[str] | None = None) -> list[Doc]:
    """conBondCorpus: `korpus-NNN.json` (bloky s textem) + `otazky-NNN.json`
    (otázky s `sentence` a `answer_lemma`). Text = bloky za sebou, blok = odstavec."""
    root = _abs(cfg["korpus"]["root"])
    if not root.exists():
        print(f"bench: sada korpus není ({root}) — přeskočena", file=sys.stderr)
        return []
    docs: list[Doc] = []
    for kp in sorted(root.glob("korpus-*.json")):
        name = kp.stem
        if only and name not in only:
            continue
        d = json.loads(kp.read_text(encoding="utf-8"))
        blocks = [str(b.get("text", "")) for b in d.get("blocks", []) if isinstance(b, dict)]
        text = "\n\n".join(blocks)
        qs: list[Question] = []
        qp = root / f"otazky-{name.split('-', 1)[1]}.json"
        if qp.exists():
            qd = json.loads(qp.read_text(encoding="utf-8"))
            for item in qd.get("questions", []):
                if not item.get("answerable", True):
                    continue
                qs.append(Question(str(item["text"]), [str(item.get("answer_lemma", ""))], "korpus", sent_no=item.get("sentence")))
        if not qs and not only:
            continue
        topic = ""
        if blocks and d.get("blocks"):
            topic = str(d["blocks"][0].get("topic", "")).split(" · ", maxsplit=1)[0].split(".txt", maxsplit=1)[0].replace("_", " ").strip()
        docs.append(Doc(name, "korpus", text, qs, kp, topic))
    return docs


def load_sada(name: str, cfg: dict[str, Any], *, only: list[str] | None = None, with_auto: bool = True) -> list[Doc]:
    """Načti sadu podle jména; neznámá nebo chybějící sada → [] s varováním."""
    if name == "wiki":
        return load_wiki(cfg, only=only, with_auto=with_auto)
    if name == "korpus":
        return load_korpus(cfg, only=only)
    print(f"bench: sada {name} v v1 není k dispozici — přeskočena", file=sys.stderr)
    return []


def data_fingerprint(docs: list[Doc]) -> str:
    """Otisk obsahu textů i otázek (I‑7: zpráva říká, nad čím běžela)."""
    h = hashlib.sha256()
    for d in sorted(docs, key=lambda x: (x.sada, x.name)):
        h.update(d.name.encode())
        h.update(d.text.encode())
        for q in d.questions:
            h.update(q.q.encode())
            h.update("|".join(q.expect).encode())
    return h.hexdigest()[:12]
