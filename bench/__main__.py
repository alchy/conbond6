"""CLI benche.

    python -m bench                          # = run --sada wiki (kurátorované + filtrované auto)
    python -m bench run --sada wiki korpus --vse --dvakrat
    python -m bench run --sada wiki --strop 40 --dok alois_jirásek --vypis
    python -m bench diff mereni/A.json mereni/B.json
    python -m bench gold-filter              # přegeneruje bench/gold/otazky-filtr.json
    python -m bench audit --dok X --rucne    # Task 5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bench.data import ROOT, load_config
from bench.diff import diff_reports, render_diff


def _cmd_run(args: argparse.Namespace) -> int:
    from bench.run import render_report, run, write_report  # pylint: disable=import-outside-toplevel
    cfg = load_config()
    sady = args.sada or ["wiki"]
    if args.vse:
        sady = ["wiki", "korpus"]
    report = run(sady, strop=args.strop, docs=args.dok, twice=args.dvakrat, with_auto=not args.bez_auto, cfg=cfg, verbose=args.vypis)
    if args.label:
        report["label"] = args.label
    mereni = ROOT / cfg["mereni"]
    prev = _previous_report(mereni, args.proti)
    if prev is not None:
        report["diff_md"] = render_diff(diff_reports(prev, report))
    j, m = write_report(report, mereni)
    print(render_report(report))
    print(f"zpráva: {m} · {j}", file=sys.stderr)
    t = report["totals"]
    return 0 if t.get("determinism", True) and not t.get("graph_violations") else 1


def _previous_report(mereni: Path, explicit: str | None):
    """Předchozí zpráva pro diff: explicitní cesta, jinak poslední `mereni/*.json`
    (podle jména), jinak conbond5 `bench-vse.json`."""
    if explicit:
        return json.loads(Path(explicit).read_text(encoding="utf-8"))
    cands = sorted(p for p in mereni.glob("2*.json") if not p.name.startswith("audit-"))
    if cands:
        return json.loads(cands[-1].read_text(encoding="utf-8"))
    old = mereni / "bench-vse.json"
    if old.exists():
        return json.loads(old.read_text(encoding="utf-8"))
    return None


def _cmd_diff(args: argparse.Namespace) -> int:
    a = json.loads(Path(args.prev).read_text(encoding="utf-8"))
    b = json.loads(Path(args.cur).read_text(encoding="utf-8"))
    print(render_diff(diff_reports(a, b)))
    return 0


def _cmd_gold_filter(args: argparse.Namespace) -> int:  # pylint: disable=unused-argument
    from bench.gold import main as gold_main  # pylint: disable=import-outside-toplevel
    return gold_main([])


def main(argv: list[str]) -> int:
    """Rozparsuj argumenty a spusť podpříkaz (`run` je výchozí)."""
    ap = argparse.ArgumentParser(prog="bench", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="běh nad sadami")
    r.add_argument("--sada", nargs="*", help="wiki | korpus")
    r.add_argument("--vse", action="store_true", help="všechny sady")
    r.add_argument("--strop", type=int, default=0, help="nejvýš N řádků na dokument")
    r.add_argument("--dok", nargs="*", help="jen tyto dokumenty")
    r.add_argument("--dvakrat", action="store_true", help="determinismus: dokument dvakrát")
    r.add_argument("--bez-auto", action="store_true", help="bez automatické (filtrované) sady otázek")
    r.add_argument("--vypis", action="store_true", help="vypsat každou otázku")
    r.add_argument("--proti", help="JSON zprávy pro diff (jinak poslední v mereni/)")
    r.add_argument("--label", help="přípona jména zprávy")
    d = sub.add_parser("diff", help="rozdíl dvou zpráv")
    d.add_argument("prev")
    d.add_argument("cur")
    sub.add_parser("gold-filter", help="přegenerovat bench/gold/otazky-filtr.json")
    argv = list(argv)
    if not argv or argv[0].startswith("-"):
        argv = ["run"] + argv
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return _cmd_run(args)
    if args.cmd == "diff":
        return _cmd_diff(args)
    if args.cmd == "gold-filter":
        return _cmd_gold_filter(args)
    ap.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
