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
from bench.judge import make_judge


def _cmd_run(args: argparse.Namespace) -> int:
    from bench.run import render_report, run, write_report  # pylint: disable=import-outside-toplevel
    cfg = load_config()
    sady = args.sada or ["wiki"]
    if args.vse:
        sady = ["wiki", "korpus"]
    judge = make_judge(cfg) if args.soudce else None
    audit_n = int(cfg.get("audit_sample", 50)) if (args.soudce or args.audit) else 0
    if args.bez_lexikonu:
        # ablace seed vrstvy lexikonu (návrh vazeb § 3): řádky `said` zůstávají, seed ne
        from cb6.lexicon import set_seed_enabled  # pylint: disable=import-outside-toplevel
        set_seed_enabled(False)
    report = run(sady, strop=args.strop, docs=args.dok, twice=args.dvakrat, with_auto=not args.bez_auto, cfg=cfg, verbose=args.vypis,
                 judge=judge, audit_n=audit_n, audit_docs=args.audit_doky)
    if args.label:
        report["label"] = args.label
    if args.bez_lexikonu:
        report["label"] = (report.get("label", "") + "-bez-lexikonu").lstrip("-")
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


def _cmd_audit(args: argparse.Namespace) -> int:
    """`bench audit --dok X [--rucne] [--soudce]` — vzorek téhož dokumentu jako
    v běhu (seed = commit), soudce a/nebo lidská smyčka, souhrn."""
    from bench.audit import human_loop, run_audit  # pylint: disable=import-outside-toplevel
    from bench.run import git_info, ingest_doc, make_oracle  # pylint: disable=import-outside-toplevel
    from bench.data import load_sada  # pylint: disable=import-outside-toplevel
    cfg = load_config()
    docs = [d for s in ("wiki", "korpus") for d in load_sada(s, cfg, only=[args.dok]) if d.name == args.dok]
    if not docs:
        print(f"dokument {args.dok} není v žádné sadě", file=sys.stderr)
        return 2
    oracle = make_oracle(cfg)
    session, _, _, _ = ingest_doc(docs[0], oracle, 0)
    _, h, _ = git_info()
    judge = make_judge(cfg) if args.soudce else None
    n = args.n or int(cfg.get("audit_sample", 50))
    human_path = ROOT / cfg.get("mereni", "mereni") / f"audit-{args.dok}.json"
    res = run_audit(session.memory, args.dok, judge, human_path, n, h)
    if judge is not None and hasattr(judge, "flush"):
        judge.flush()
    if args.rucne:
        import cb6.render as cb_render  # pylint: disable=import-outside-toplevel
        render_show = getattr(cb_render, "render_show", None)  # Task 9 doplní
        show = (lambda sid: render_show(session.memory, sid)) if render_show else None  # noqa: E731
        human_loop(res["items"], human_path, show_graph=show)
        res = run_audit(session.memory, args.dok, None, human_path, n, h)
    def pct(v, digits=1):
        return "—" if v is None else f"{100 * v:.{digits}f} %"
    print(f"{args.dok}: vzorek {res['n']} · soudce {res.get('judge') or '—'}: {res['judged']} posouzeno, unsupported "
          f"{pct(res['unsupported'])} · člověk {res['human_n']} → {pct(res['human_unsupported'])} · shoda {pct(res['agreement'], 0)}")
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
    r.add_argument("--bez-lexikonu", action="store_true", help="ablace: bez seed vrstvy lexikonu (cb6/lexikon/*.jsonl)")
    r.add_argument("--vypis", action="store_true", help="vypsat každou otázku")
    r.add_argument("--proti", help="JSON zprávy pro diff (jinak poslední v mereni/)")
    r.add_argument("--label", help="přípona jména zprávy")
    r.add_argument("--soudce", action="store_true", help="precision audit se soudcem z configu (Ollama/Claude), s keší verdiktů")
    r.add_argument("--audit", action="store_true", help="precision audit jen s lidskými odpověďmi (bez soudce)")
    r.add_argument("--audit-doky", type=int, default=0, help="auditovat jen N dokumentů (deterministický výběr)")
    a = sub.add_parser("audit", help="lidská smyčka nad vzorkem dokumentu")
    a.add_argument("--dok", required=True)
    a.add_argument("--rucne", action="store_true", help="odpovídat v terminálu")
    a.add_argument("--soudce", action="store_true", help="nechat vzorek posoudit soudcem")
    a.add_argument("--n", type=int, default=0, help="velikost vzorku (výchozí z configu)")
    d = sub.add_parser("diff", help="rozdíl dvou zpráv")
    d.add_argument("prev")
    d.add_argument("cur")
    sub.add_parser("gold-filter", help="přegenerovat bench/gold/otazky-filtr.json")
    gg = sub.add_parser("gold-gen", help="LM‑generované ukotvené otázky (+ --overit lidské ověření)")
    gg.add_argument("rest", nargs=argparse.REMAINDER)
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
    if args.cmd == "audit":
        return _cmd_audit(args)
    if args.cmd == "gold-gen":
        from bench.gold_gen import main as gg_main  # pylint: disable=import-outside-toplevel
        return gg_main(args.rest)
    ap.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
