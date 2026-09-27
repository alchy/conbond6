"""Destilační dataset: (UD parse → `Predication`) z `read.py` jako „učitel“.

Proč (J. 27. 9. 2026, „lze read.py nahradit vztahovou NN? na základě
poznatku v read.py už trénovat NN, pak read.py konzervovat a učit další
vztahy přes NN“): dřív, než jde cokoli trénovat, musí existovat dataset
(parse, zlatá struktura) — dnes NEEXISTUJE, `read.py` počítá `Predication`
za běhu a testuje se ad hoc asercemi (`tests/test_*.py`), ne jako uložené
páry. Tenhle nástroj používá `read.py` jako učitele (žádné ruční značení)
přes reálný korpus a změří, kolik z toho je „čisté“ (bez residua, bez
otevřených položek, hlavní výrok SAFE) — HORNÍ MEZ toho, co by šlo naučit
napodobováním. `read()` je čistá funkce (parse + naučené role → Predication,
žádný stav paměti) — přesně ten krok, který spec myslí „NN dělá strukturu“
(I‑9 zobecněné): dataset je (parse, Predication), ne (text, znalost).

Provenience (`--parser spacy`, ne UDPipe2) se nese jako u zbytku benche
(I‑12) — čísla NEsrovnávat mezi parsery ani s historickými zprávami.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from bench.data import ROOT, Doc, load_config, load_wiki
from bench.run import make_oracle
from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import CachedOracle, OracleError, SegmentationError
from cb6.read import read as read_parse

#: Kam se píše syrový dataset (velký, regenerovatelný z korpusu — negituje se
#: stejně jako `data/cache`/`data/corpus`, viz `.gitignore`).
DEFAULT_OUT = ROOT / "data" / "distill"


@dataclass
class Row:
    """Jeden trénovací příklad: věta, rozbor (provenience), `Predication`
    (jako JSON přes `dataclasses.asdict` — samé prosté dataclassy) a signál
    kvality (`clean`), podle kterého se řádky filtrují na učení."""

    doc: str
    text: str
    provenance: str
    predication: dict[str, Any]
    kind: str
    residue: list[list[str]]
    open_items: int
    claims: list[str]
    clean: bool


@dataclass
class DistillSummary:
    """Souhrn pokrytí — kolik z korpusu je „čistý“ učitelský signál."""

    docs: int
    sentences: int
    tokens: int
    residue_tokens: int
    clean: int
    by_kind: dict[str, int] = field(default_factory=dict)
    by_kind_clean: dict[str, int] = field(default_factory=dict)

    @property
    def clean_pct(self) -> float:
        """Podíl vět bez residua/otevřených položek se SAFE hlavním výrokem."""
        return round(100.0 * self.clean / self.sentences, 1) if self.sentences else 0.0

    @property
    def residue_pct(self) -> float:
        """Podíl tokenů v residuu (nezakotveno do žádné role)."""
        return round(100.0 * self.residue_tokens / self.tokens, 1) if self.tokens else 0.0


def build_rows(docs: list[Doc], oracle: CachedOracle, *, strop: int = 0) -> list[Row]:
    """Projeď dokumenty, pro každou větu ulož (parse, Predication, kvalita).

    Věta se čte DVAKRÁT: jednou uvnitř `Session.ingest` (zápis do paměti —
    dá `residue`/`open`/`claim` přes existující bench metriky), podruhé
    přímo přes `read_parse` (čistá funkce, žádný zápis) pro `Predication`
    samotnou. Oracle je kešovaný, takže druhé čtení nestojí nový rozbor.
    """
    rows: list[Row] = []
    for doc in docs:
        session = Session(Memory(), oracle)
        lines = doc.text.splitlines()
        if strop:
            kept: list[str] = []
            n = 0
            for line in lines:
                if line.strip():
                    n += 1
                    if n > strop:
                        break
                kept.append(line)
            lines = kept
        text = "\n".join(lines)
        reports = session.ingest(text, doc.name)
        m = session.memory
        learned = m.learned.get("roles", {})
        for rep in reports:
            if "error" in rep:
                continue
            sent_text = str(rep["text"])
            try:
                parse = oracle.parse(sent_text)
            except (OracleError, SegmentationError, KeyError):
                continue  # věta z více vět (segmentace) — přeskoč, jde jen o metriku
            reading = read_parse(parse, "assert", learned_roles=learned)
            statements = cast(list, rep["statements"])
            open_items = cast(list, rep["open"])
            claims: list[str] = [m.statements[sid].claim for sid in statements if sid in m.statements]
            clean = (not reading.residue and not open_items and bool(claims)
                     and all(c == "SAFE" for c in claims) and reading.main.kind != "fragment")
            rows.append(Row(
                doc=doc.name, text=parse.text, provenance=parse.provenance,
                predication=asdict(reading.main), kind=reading.main.kind,
                residue=[list(x) for x in reading.residue], open_items=len(open_items),
                claims=claims, clean=clean,
            ))
    return rows


def summarize(rows: list[Row]) -> DistillSummary:
    """Souhrn přes všechny řádky — pokrytí podle druhu predikace."""
    tokens = sum(len(r.text.split()) for r in rows)
    residue = sum(len(r.residue) for r in rows)
    by_kind: dict[str, int] = {}
    by_kind_clean: dict[str, int] = {}
    for r in rows:
        by_kind[r.kind] = by_kind.get(r.kind, 0) + 1
        if r.clean:
            by_kind_clean[r.kind] = by_kind_clean.get(r.kind, 0) + 1
    return DistillSummary(
        docs=len({r.doc for r in rows}), sentences=len(rows), tokens=tokens,
        residue_tokens=residue, clean=sum(1 for r in rows if r.clean),
        by_kind=by_kind, by_kind_clean=by_kind_clean,
    )


def render(s: DistillSummary) -> str:
    """Čitelný výpis souhrnu (bez per-řádkových dat — ta jsou v JSONL)."""
    lines = [
        f"destilační dataset (read.py jako učitel): {s.docs} dok., {s.sentences} vět, {s.tokens} slov",
        f"  residuum: {s.residue_pct} % tokenů ({s.residue_tokens})",
        f"  čisté (bez residua, bez otevřených položek, SAFE, ne fragment): {s.clean}/{s.sentences} = {s.clean_pct} %",
        "  podle druhu predikace (čisté/celkem):",
    ]
    for kind in sorted(s.by_kind):
        c, n = s.by_kind_clean.get(kind, 0), s.by_kind[kind]
        lines.append(f"    {kind:10s} {c}/{n}")
    return "\n".join(lines)


def write_dataset(rows: list[Row], out_dir: Path = DEFAULT_OUT, *, label: str = "spacy") -> Path:
    """Zapiš řádky jako JSONL (jeden trénovací příklad na řádek).
    Vstup: řádky, adresář, značka provenience. Výstup: cesta k souboru."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"dataset-{label}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    return path


def main(argv: list[str]) -> int:  # pragma: no cover — tenká CLI fasáda
    """`python -m bench distill [--strop N] [--dok jméno...]` — sestav dataset
    a vypiš souhrn pokrytí. Vždy vrací 0 (informační bench)."""
    import argparse  # pylint: disable=import-outside-toplevel

    ap = argparse.ArgumentParser(prog="bench distill")
    ap.add_argument("--strop", type=int, default=0, help="nejvýš N neprázdných řádků na dokument (0 = vše)")
    ap.add_argument("--dok", nargs="*", help="jen tyto dokumenty (jinak celá sada wiki)")
    ap.add_argument("--parser", choices=["udpipe", "spacy"], default="spacy",
                     help="výchozí spacy — UDPipe v cloudovém sezení neběží (viz HANDOVER)")
    args = ap.parse_args(argv)
    cfg = load_config()
    oracle = make_oracle(cfg, parser=args.parser)
    docs = load_wiki(cfg, only=args.dok, with_auto=False)
    rows = build_rows(docs, oracle, strop=args.strop)
    path = write_dataset(rows, label=args.parser)
    print(render(summarize(rows)))
    print(f"dataset: {path} ({len(rows)} řádků)")
    return 0
