"""Generátor ukotvených zlatých otázek (I‑9: LM smí generovat otázky, ne znalost).

Proč: automatická sada conBond2 má otázky bez hlavy a paty a místy i špatné
odpovědi („Kde zemřel Karel Čapek? → Čech“). Kurátorovaných je málo (40 + 95).
Tady LM (Ollama) dostane **jednu větu** a vytvoří jednu otázku, jejíž odpověď je
doslova ve větě; přijme se jen, když odpověď ve větě opravdu je a otázka je
úplná (≥ 4 slova, končí „?“, obsahuje jméno tématu nebo je o něm zjevně).
Výsledek jde do `bench/gold/gen-<doc>.json` s `curated=False`; teprve lidské
ověření (`python -m bench gold-gen --overit --dok X`) přepne položku na
`curated=True` — do hlavního čísla QA jdou jen ověřené.

    python -m bench gold-gen --dok alois_jirásek --n 12
    python -m bench gold-gen --overit --dok alois_jirásek
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

from bench.data import Doc, HERE, load_config, load_sada
from bench.qa import norm

GEN_PROMPT = """Jsi tvůrce testových otázek pro čtení s porozuměním. Dostaneš JEDNU českou větu z encyklopedického textu o osobě/tématu „{topic}“.
Vytvoř JEDNU jednoduchou, gramaticky správnou otázku česky, na kterou věta PŘÍMO odpovídá, a odpověď.
Pravidla:
- odpověď musí být krátká (jméno, místo, rok, datum, číslo, jedno slovo nebo krátká fráze) a musí být DOSLOVA obsažena ve větě (stejný tvar);
- otázka musí být úplná a jednoznačná i bez kontextu: pojmenuj osobu/téma jménem („Kde se narodil Alois Jirásek?“), ne „on“;
- neptej se na nic, co ve větě není; nevymýšlej;
- když z věty žádná dobrá otázka nejde, vrať {{"otazka": "", "odpoved": ""}}.
Odpověz jen JSON: {{"otazka": "...", "odpoved": "..."}}"""


def _ollama(cfg: dict[str, Any], system: str, user: str) -> str:
    j = cfg.get("judge", {})
    body = {"model": j.get("model", "gemma4:latest"), "stream": False, "think": False, "format": "json",
            "options": {"temperature": 0.2, "num_predict": 200},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(j.get("endpoint", "http://127.0.0.1:11434").rstrip("/") + "/api/chat",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode())
    return str(data.get("message", {}).get("content", ""))


def _sentences(doc: Doc, oracle) -> list[tuple[int, str]]:
    """(číslo věty v našem číslování, text) — přes keš rozborů (stejná segmentace jako ingest)."""
    out: list[tuple[int, str]] = []
    no = 0
    for line in doc.text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        raw = raw.strip("= ").strip() or raw
        try:
            parses = oracle.segment(raw)
        except KeyError:
            continue
        for p in parses:
            no += 1
            out.append((no, p.text))
    return out


def generate(doc: Doc, oracle, cfg: dict[str, Any], n: int, *, every: int = 3) -> list[dict[str, Any]]:
    """Vytvoř až `n` otázek z každé `every`-té věty s ≥ 6 slovy; přijmi jen ověřitelné."""
    out: list[dict[str, Any]] = []
    sents = [(no, t) for no, t in _sentences(doc, oracle) if len(t.split()) >= 6]
    for i, (no, text) in enumerate(sents):
        if len(out) >= n:
            break
        if i % every:
            continue
        try:
            raw = _ollama(cfg, GEN_PROMPT.format(topic=doc.topic), f"Věta: „{text}“")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"gold-gen: LM selhal ({exc})", file=sys.stderr)
            break
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            continue
        try:
            d = json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
        q, a = str(d.get("otazka", "")).strip(), str(d.get("odpoved", "")).strip()
        if not q or not a or not q.endswith("?") or len(q.split()) < 4:
            continue
        if norm(a) not in norm(text):
            continue  # odpověď není doslova ve větě → nepřijato
        if len(a.split()) > 6:
            continue
        out.append({"q": q, "expect": [a], "dok": doc.name, "veta": no, "source_sentence": text,
                    "model": cfg.get("judge", {}).get("model", ""), "curated": False})
    return out


def gold_path(doc: str) -> Path:
    """Soubor generovaných otázek dokumentu (v repu, s proveniencí modelu)."""
    return HERE / "gold" / f"gen-{doc}.json"


def verify_loop(doc: str) -> int:
    """Lidské ověření: 1 = dobrá otázka i odpověď · 2 = špatná (vyřadit) · e = upravit odpověď · q = konec."""
    p = gold_path(doc)
    if not p.exists():
        print(f"{p} není", file=sys.stderr)
        return 2
    items = json.loads(p.read_text(encoding="utf-8"))
    todo = [it for it in items if not it.get("curated") and not it.get("rejected")]
    print(f"{len(todo)} k ověření (1 dobrá · 2 vyřadit · e upravit odpověď · q konec)")
    for i, it in enumerate(todo, 1):
        print(f"\n[{i}/{len(todo)}] VĚTA: {it['source_sentence']}\n   OTÁZKA: {it['q']}\n   ODPOVĚĎ: {it['expect'][0]}")
        ans = input("   > ").strip().lower()
        if ans == "q":
            break
        if ans == "1":
            it["curated"] = True
        elif ans == "2":
            it["rejected"] = True
        elif ans == "e":
            new = input("   nová odpověď> ").strip()
            if new:
                it["expect"] = [new]
                it["curated"] = True
        p.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def main(argv: list[str]) -> int:
    """CLI (viz docstring modulu)."""
    import argparse  # pylint: disable=import-outside-toplevel
    from bench.run import make_oracle  # pylint: disable=import-outside-toplevel
    ap = argparse.ArgumentParser(prog="bench gold-gen")
    ap.add_argument("--dok", nargs="+", required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--overit", action="store_true")
    args = ap.parse_args(argv)
    if args.overit:
        return max(verify_loop(d) for d in args.dok)
    cfg = load_config()
    oracle = make_oracle(cfg)
    docs = [d for s in ("wiki", "korpus") for d in load_sada(s, cfg, only=args.dok) if d.name in args.dok]
    for d in docs:
        items = generate(d, oracle, cfg, args.n)
        p = gold_path(d.name)
        old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
        seen = {(o["q"], o["dok"]) for o in old}
        merged = old + [it for it in items if (it["q"], it["dok"]) not in seen]
        p.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{d.name}: +{len(merged) - len(old)} otázek (celkem {len(merged)}, ověřených {sum(1 for x in merged if x.get('curated'))})", file=sys.stderr)
    return 0
