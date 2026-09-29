"""Charakterizační test: zamrazené chování čtení, triáže, zakotvení a logiky.

Proč: refaktor (struktura, výkon) nesmí změnit ani jednu odpověď. Místo
ručně psaných očekávání se jednou zaznamená úplný otisk chování nad všemi
nahranými rozbory (`tests/data/parses.json`, 177 vět) a každý další běh se
s ním porovná znak po znaku. Změna otisku = změna chování = musí jít do
commitu s číslem z benche, ne potichu s refaktorem.

Otisk (`tests/data/golden_behavior.json`):
* `readings` — pro každou větu: všechny predikace (`str`), zbytek, umístění
  tokenů a rozhodnutí triáže (claim/mood/reason);
* `program` — `Memory.program()` po načtení všech oznamovacích vět jako
  jednoho dokumentu (zakotvení, koreference, odvození, statusy);
* `answers` — text odpovědi na každou tázací větu nad touto pamětí;
* `graph` — počty uzlů a hran exportu podle druhu.

Obnova otisku (jen při ZÁMĚRNÉ změně chování, s benchem):
    CB6_GOLDEN_UPDATE=1 python -m pytest tests/test_golden_behavior.py
"""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import RecordedOracle, parse_from_json
from cb6.read import read
from cb6.triage import triage

DATA = Path(__file__).parent / "data"
PARSES = DATA / "parses.json"
GOLDEN = DATA / "golden_behavior.json"


def _sentences() -> list[str]:
    """Věty z nahrávky v pevném pořadí (klíče segmentace se přeskočí)."""
    raw = json.loads(PARSES.read_text(encoding="utf-8"))
    return sorted(k for k in raw if not k.startswith("§segment§"))


def _readings() -> dict[str, dict[str, object]]:
    """Otisk čtení a triáže každé věty (bez paměti — čistá funkce rozboru)."""
    raw = json.loads(PARSES.read_text(encoding="utf-8"))
    out: dict[str, dict[str, object]] = {}
    for text in _sentences():
        r = read(parse_from_json(raw[text]))
        t = triage(r)
        preds = r.all_predications()
        out[text] = {
            "predications": [str(p) for p in preds],
            "moods": [p.mood for p in preds],
            "residue": [list(x) for x in r.residue],
            "placement": {str(k): v for k, v in sorted(r.placement().items())},
            "triage": [[d.claim, d.mood, d.reason] for d in (t.decision(p) for p in preds)],
            "rules": [[x.kind, x.marker] for x in t.rules],
        }
    return out


def _dialog() -> dict[str, object]:
    """Otisk paměti po načtení všech oznámení a odpovědí na všechny otázky."""
    session = Session(Memory(), RecordedOracle(PARSES))
    texts = _sentences()
    statements = [t for t in texts if not t.rstrip().endswith("?")]
    questions = [t for t in texts if t.rstrip().endswith("?")]
    session.ingest("\n".join(statements), "golden")
    answers = {q: session.say(q, "golden").text for q in questions}
    g = session.memory.graph()
    return {
        "program": session.memory.program(),
        "answers": answers,
        "graph": {
            "nodes": dict(sorted(Counter(a.get("kind", "?") for _, a in g.nodes(data=True)).items())),
            "edges": dict(sorted(Counter(a.get("type", "?") for _, _, a in g.edges(data=True)).items())),
        },
    }


def snapshot() -> dict[str, object]:
    """Celý otisk chování (čtení + dialog). Vstup: nic. Výstup: JSON‑serializovatelný dict."""
    return {"readings": _readings(), "dialog": _dialog()}


def test_behavior_matches_golden() -> None:
    """Chování jádra je beze změny proti zamrazenému otisku."""
    current = json.loads(json.dumps(snapshot(), ensure_ascii=False))
    if os.environ.get("CB6_GOLDEN_UPDATE") == "1" or not GOLDEN.exists():
        GOLDEN.write_text(json.dumps(current, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert current["readings"].keys() == golden["readings"].keys()
    for text, want in golden["readings"].items():
        assert current["readings"][text] == want, text
    assert current["dialog"]["program"] == golden["dialog"]["program"]
    for q, want in golden["dialog"]["answers"].items():
        assert current["dialog"]["answers"][q] == want, q
    assert current["dialog"]["graph"] == golden["dialog"]["graph"]
