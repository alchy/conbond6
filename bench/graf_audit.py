"""Audit mechanismu `graf` (`Session._suggest_link_from_graph`) na reálném
korpusu — HANDOVER § 6 bod -1 (nejvyšší priorita, 27. 9. 2026): dosud běžel
jen na fragmentech (`bench/vazby.py`), NIKDY na reálném textu. Riziko:
falešné páry (dvě různé osoby stejného jména, náhodná shoda role) by
zaplevelily lexikon šumem — síla `related` škodu limituje (nikdy ve
verdiktu, I‑3), ale čitelnost/užitečnost lexikonu by klesla.

Nástroj jen SBÍRÁ návrhy (a dohledá zdrojové věty pro ruční posouzení) —
verdikt „je to šum, nebo ne“ dává člověk/LM čtením vět, ne heuristika zde.

Výsledek prvního měření (27. 9. 2026, `mereni/HYPOTEZY.md`): 16 dokumentů
wiki (~180 000 slov), 80 návrhů; ruční čtení zdrojových vět u vzorku (~35)
neukázalo ani jednu skutečnou parafrázi — vždy dvě věty o téže osobě/tématu
sdílející `kdo` + náhodou i další roli (místo, datum, předmět), ne totéž
řečeno jinak. Mechanismus je proto od téhož dne VYPNUTÝ ve výchozím stavu
(`cb6.dialog._GRAF_SUGGESTIONS_ENABLED = False`, `bench run --se-grafem`
ho zapne pro přeměření po zpřesnění kritéria). Tenhle nástroj zůstává pro
budoucí přeměření, jakmile bude kritérium jiné než „shoda dvou rolí“.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bench.data import Doc, load_config, load_wiki
from bench.run import make_oracle
from cb6.dialog import Session
from cb6.memory import Memory


@dataclass
class GrafLink:
    """Jeden návrh mechanismu `graf`, s dohledanými zdrojovými větami obou
    stran (pro ruční posouzení — link samotný nese jen predikáty, ne věty)."""

    doc: str
    link_id: str
    args: tuple[str, ...]
    source: str
    examples: list[tuple[str, str]] = field(default_factory=list)  # (věta A, věta B)


def _example_sentences(session: Session, pred_a: str, pred_b: str, *, limit: int = 2) -> list[tuple[str, str]]:
    """Dohledej dvojice vět (predikát A, predikát B) se shodným `kdo`, které
    mohly `graf` návrh spustit — jen pro čtení člověkem, ne pro verdikt."""
    m = session.memory
    by_pred: dict[str, list[Any]] = {}
    for st in m.statements.values():
        if st.pred in (pred_a, pred_b) and st.mood == "assert":
            by_pred.setdefault(st.pred, []).append(st)
    out: list[tuple[str, str]] = []
    for a in by_pred.get(pred_a, []):
        kdo_a = a.role("kdo")
        if not kdo_a or not kdo_a.terms:
            continue
        for b in by_pred.get(pred_b, []):
            kdo_b = b.role("kdo")
            if kdo_b and set(kdo_b.terms) == set(kdo_a.terms):
                out.append((a.sentence and m.nodes.get(a.sentence).text or a.prov.text,  # type: ignore[union-attr]
                             b.sentence and m.nodes.get(b.sentence).text or b.prov.text))  # type: ignore[union-attr]
                if len(out) >= limit:
                    return out
    return out


def scan(docs: list[Doc], oracle: Any, *, strop: int = 0) -> list[GrafLink]:
    """Projeď dokumenty, po ingestu sesbírej řádky mechanismu `graf`
    (autorita `read`, zdroj začíná „graf (tah“ — odlišeno od `korekce`
    a `věta učí lexikon`, což jsou jiné mechanismy stejné autority)."""
    out: list[GrafLink] = []
    for doc in docs:
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
        session = Session(Memory(), oracle)
        session.ingest("\n".join(lines), doc.name)
        m = session.memory
        for link in m.links.values():
            if link.authority != "read" or not link.source.startswith("graf (tah"):
                continue
            examples = _example_sentences(session, link.args[0], link.args[1])
            out.append(GrafLink(doc=doc.name, link_id=link.id, args=link.args, source=link.source, examples=examples))
    return out


def render(rows: list[GrafLink]) -> str:
    """Čitelný výpis: souhrn + každý návrh se zdrojovými větami k posouzení."""
    lines = [f"mechanismus `graf` na reálném korpusu: {len(rows)} návrhů"]
    for r in rows:
        lines.append(f"\n[{r.doc}] {r.link_id}: {r.args[0]} ~ {r.args[1]}")
        for a, b in r.examples:
            lines.append(f"    „{a}“")
            lines.append(f"    „{b}“")
        if not r.examples:
            lines.append("    (zdrojové věty nedohledány)")
    return "\n".join(lines)


def main(argv: list[str]) -> int:  # pragma: no cover — tenká CLI fasáda
    """`python -m bench graf-audit [--strop N] [--dok jméno...]` — sesbírej
    návrhy mechanismu `graf` na reálném korpusu a vypiš k ručnímu posouzení.
    Vždy vrací 0 (informační bench)."""
    import argparse  # pylint: disable=import-outside-toplevel

    ap = argparse.ArgumentParser(prog="bench graf-audit")
    ap.add_argument("--strop", type=int, default=0, help="nejvýš N neprázdných řádků na dokument (0 = vše)")
    ap.add_argument("--dok", nargs="*", help="jen tyto dokumenty (jinak celá sada wiki)")
    ap.add_argument("--parser", choices=["udpipe", "spacy"], default="spacy",
                     help="výchozí spacy — UDPipe v cloudovém sezení neběží (viz HANDOVER)")
    args = ap.parse_args(argv)
    cfg = load_config()
    oracle = make_oracle(cfg, parser=args.parser)
    docs = load_wiki(cfg, only=args.dok, with_auto=False)
    print(render(scan(docs, oracle, strop=args.strop)))
    return 0
