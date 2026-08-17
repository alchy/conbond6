"""Běh benche nad dokumenty a sadami; zpráva JSON + Markdown do `mereni/`.

Jeden dokument = jedna čerstvá paměť (otázky jsou vázané na dokument).
Pořadí kroků za dokument: ingest → metriky ingestu → QA (každá otázka
`Session.say`) → dosah → (Task 4) audit grafu → (Task 5) precision audit.
Zpráva nese commit, otisk dat, časy a — je‑li k dispozici předchozí zpráva
— regresní rozdíl (`diff.py`).

Determinismus (I‑7): `twice=True` vloží dokument podruhé do čerstvé paměti
a porovná otisk JSON paměti; nerovnost je chyba běhu.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import CachedOracle, OracleUnavailable, UDPipeOracle
from cb6.render import describe_node

from bench.audit import run_audit
from bench.data import Doc, ROOT, data_fingerprint, load_config, load_sada
from bench.graphcheck import check_answer, check_graph
from bench.judge import Judge
from bench.metrics import ingest_metrics, qa_metrics, reach
from bench.qa import anchor_words, answer_matches, classify_miss, find_answer_sentence, last_anchor_sentence, norm, years


def git_info() -> tuple[str, str, bool]:
    """(datum posledního commitu YYYY-MM-DD, krátký hash, dirty?) — žádné hodiny."""
    try:
        date = subprocess.run(["git", "log", "-1", "--format=%cs"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
        return date, h, dirty
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "0000-00-00", "nogit", True


def make_oracle(cfg: dict[str, Any]) -> CachedOracle:
    """UDPipe s keší na disku; bez služby jede jen z keše (a hlásí to)."""
    cache = ROOT / cfg["cache"]
    try:
        return CachedOracle(UDPipeOracle(), cache)
    except OracleUnavailable:
        print("bench: služba UDPipe neběží — jedu jen z keše", file=sys.stderr)
        return CachedOracle(None, cache)


def memory_fingerprint(memory: Memory) -> str:
    """Otisk paměti pro determinismus."""
    return hashlib.sha256(json.dumps(memory.to_json(), ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def _segment_of(memory: Memory, doc: str, no: int | None) -> str | None:
    """Segment (uzel) věty číslo `no` v dokumentu, nebo None."""
    if no is None:
        return None
    for n in memory.nodes.values():
        if n.kind == "sentence" and n.doc == doc and n.lemma == f"{doc}#{no}":
            base = memory.nodes.get(n.base or "")
            return n.base if base is not None and base.kind == "segment" else None
    return None


def _sentences(memory: Memory) -> list[Any]:
    return sorted((n for n in memory.nodes.values() if n.kind == "sentence"), key=lambda n: int(n.lemma.rsplit("#", 1)[-1]))


def ingest_doc(doc: Doc, oracle: CachedOracle, strop: int) -> tuple[Session, list[dict[str, Any]], float, int]:
    """Vlož dokument (nejvýš `strop` řádků) do čerstvé paměti."""
    lines = doc.text.splitlines()
    if strop:
        kept: list[str] = []
        n = 0
        for l in lines:
            if l.strip():
                n += 1
                if n > strop:
                    break
            kept.append(l)
        lines = kept
    text = "\n".join(lines)  # prázdné řádky zůstávají — segmentace (spec § 4.2)
    n_words = sum(len(l.split()) for l in lines)
    session = Session(Memory(), oracle)
    t0 = time.time()
    reports = session.ingest(text, doc.name)
    return session, reports, time.time() - t0, n_words


def run_doc(doc: Doc, oracle: CachedOracle, *, strop: int = 0, twice: bool = False,
            judge: Judge | None = None, audit_n: int = 0, audit_dir: Path | None = None, seed: str = "") -> dict[str, Any]:
    """Celý běh nad jedním dokumentem: ingest, metriky, QA s dosahem, audit grafu,
    precision audit, determinismus.

    Args:
        doc: dokument se zlatými otázkami; oracle: UDPipe s keší;
        strop: nejvýš N řádků (0 = vše); twice: druhý běh pro determinismus;
        judge: soudce věrnosti (None = jen lidské odpovědi); audit_n: velikost
        vzorku (0 = bez auditu); audit_dir: adresář lidských odpovědí; seed:
        otisk commitu pro deterministický vzorek.
    Returns:
        Řádek zprávy: `doc`, `sada`, `ingest` (metriky), `qa` (souhrn),
        `results` (za otázku), `fingerprint`, `determinism`, časy.
    """
    session, reports, t_ingest, n_words = ingest_doc(doc, oracle, strop)
    m = session.memory
    fp = memory_fingerprint(m)  # před otázkami — dotazy mění aktivaci
    ing = ingest_metrics(m, n_words, reports)
    sentences = _sentences(m)
    pairs = [(int(n.lemma.rsplit("#", 1)[-1]), n.text) for n in sentences]
    doc_text_norm = norm("\n".join(t for _, t in pairs))
    results: list[dict[str, Any]] = []
    t1 = time.time()
    for q in doc.questions:
        row: dict[str, Any] = {"q": q.q, "expect": q.expect, "sada": q.sada, "curated": q.curated}
        row["coverage"] = any(norm(e) in doc_text_norm or (years(e) and years(e) & years(doc_text_norm)) for e in q.expect)
        ans_no = find_answer_sentence(pairs, q.expect)
        row["answer_sent"] = ans_no
        anchor = anchor_words(q.q, doc.topic)
        row["reach"] = reach(m, ans_no, anchor, sentences) if ans_no is not None else None
        if ans_no is not None and row["reach"] is not None:
            last = last_anchor_sentence(pairs, ans_no, anchor)
            row["other_segment"] = _segment_of(m, doc.name, ans_no) != _segment_of(m, doc.name, last) if last is not None else False
        try:
            a = session.say(q.q)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # bench nesmí spadnout na jedné otázce
            row.update({"ok": False, "text_ok": False, "why": f"pád: {type(exc).__name__}: {exc}"})
            results.append(row)
            continue
        v = a.verdict
        fillers = [t for t, _ in v.fillers] if v is not None else []
        ok, text_ok = answer_matches(m, list(q.expect), fillers, a.text)
        row.update({
            "ok": ok, "text_ok": text_ok, "verdict": v.value if v else None,
            "fillers": [describe_node(m, f) if not f.startswith("count:") else f for f in fillers][:6],
            "why": "" if ok else classify_miss(v), "reading": a.reading,
            "proof_statements": sorted({sid for p in (v.proofs if v else []) for sid in p.statements} | {sid for _, p in (v.fillers if v else []) for sid in p.statements}),
            "hard": sorted({h for p in (v.proofs if v else []) for h in p.hard} | {h for _, p in (v.fillers if v else []) for h in p.hard}),
        })
        results.append(row)
    t_ask = time.time() - t1
    # audit grafu (I‑11, I‑12) — jen nad exportem
    g = m.graph()
    violations = [v.__dict__ for v in check_graph(g)]
    for row in results:
        if row.get("verdict") in ("ANO", "NE", "KONFLIKT") or row.get("fillers"):
            vs = check_answer(g, list(row.get("proof_statements", [])), [tuple(h) for h in row.get("hard", [])])
            row["graph_violations"] = len(vs)
            violations.extend({**v.__dict__, "q": row["q"]} for v in vs)
    by_check: dict[str, int] = {}
    for viol in violations:
        by_check[str(viol["check"])] = by_check.get(str(viol["check"]), 0) + 1
    audit: dict[str, Any] | None = None
    if audit_n and audit_dir is not None:
        audit = run_audit(m, doc.name, judge, audit_dir / f"audit-{doc.name}.json", audit_n, seed or doc.name, topic=doc.topic)
    determinism: bool | None = None
    if twice:
        s2, _, _, _ = ingest_doc(doc, oracle, strop)
        determinism = memory_fingerprint(s2.memory) == fp
    return {
        "doc": doc.name, "sada": doc.sada, "ingest": ing, "qa": qa_metrics(results), "results": results,
        "fingerprint": fp, "determinism": determinism, "t_ingest": round(t_ingest, 1), "t_ask": round(t_ask, 1),
        "graph_violations": len(violations), "graph_violations_by_check": by_check, "graph_violation_examples": violations[:25],
        "audit": audit,
        "session": session,  # pro audit grafu a precision audit (Task 4–5); do JSON se nezapisuje
    }


def totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Součty přes dokumenty (yield vážený slovy)."""
    words = sum(r["ingest"]["words"] for r in rows)
    safe = sum(r["ingest"]["safe"] for r in rows)
    safe_main = sum(r["ingest"]["safe_main"] for r in rows)
    sents = sum(r["ingest"]["sentences"] for r in rows)
    toks = sum(r["ingest"]["tokens"] for r in rows)
    res = sum(r["ingest"]["residue_tokens"] for r in rows)
    opn = sum(r["ingest"]["open"] for r in rows)
    claims = {k: sum(r["ingest"]["claims"].get(k, 0) for r in rows) for k in ("SAFE", "HYPOTHESIS", "REJECTED")}
    qa = [r["qa"] for r in rows]
    by_reach: dict[str, list[int]] = {}
    by_sada: dict[str, list[int]] = {}
    for q in qa:
        for k, (h, n) in q["by_reach"].items():
            by_reach.setdefault(k, [0, 0])
            by_reach[k][0] += h
            by_reach[k][1] += n
        for k, (h, n) in q["by_sada"].items():
            by_sada.setdefault(k, [0, 0])
            by_sada[k][0] += h
            by_sada[k][1] += n
    return {
        "docs": len(rows), "sentences": sents, "words": words, "safe": safe,
        "yield": round(1000.0 * safe / words, 2) if words else 0.0,
        "yield_main": round(1000.0 * safe_main / words, 2) if words else 0.0, "safe_main": safe_main,
        "claims": claims, "derived": sum(r["ingest"]["derived"] for r in rows), "rules": sum(r["ingest"]["rules"] for r in rows),
        "residue_pct": round(100.0 * res / toks, 1) if toks else 0.0,
        "open_per_sent": round(opn / sents, 2) if sents else 0.0,
        "written_pct": round(100.0 * sum(1 for r in rows if r["ingest"]["written_pct"] >= 100.0) / len(rows), 1) if rows else 0.0,
        "questions": sum(q["questions"] for q in qa), "coverage": sum(q["coverage"] for q in qa),
        "hits": sum(q["hits"] for q in qa), "text_hits": sum(q["text_hits"] for q in qa),
        "curated_questions": sum(q["curated_questions"] for q in qa), "curated_hits": sum(q["curated_hits"] for q in qa),
        "by_reach": by_reach, "by_sada": by_sada,
        "determinism": all(r["determinism"] is not False for r in rows),
        **_audit_totals(rows),
        "graph_violations": sum(r.get("graph_violations", 0) for r in rows),
        "graph_violations_by_check": _sum_dicts(r.get("graph_violations_by_check", {}) for r in rows),
    }


def _audit_totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Souhrn precision auditu přes dokumenty (vážený počtem posouzených)."""
    from bench.audit import wilson  # pylint: disable=import-outside-toplevel
    auds = [r["audit"] for r in rows if r.get("audit")]
    judged = sum(a["judged"] for a in auds)
    ne = sum(a["netvrdí"] for a in auds)
    cast = sum(a["částečně"] for a in auds)
    hn = sum(a["human_n"] for a in auds)
    hun = [a["human_unsupported"] * a["human_n"] for a in auds if a["human_unsupported"] is not None]
    agree_n = sum(a["agreement_n"] for a in auds)
    agree = sum((a["agreement"] or 0) * a["agreement_n"] for a in auds)
    rn = [a for a in auds if a.get("readable_no_pct") is not None]
    lo, hi = wilson(ne + cast // 2, judged) if judged else (0.0, 1.0)
    by_kind: dict[str, dict[str, int]] = {}
    for a in auds:
        for k, b in (a.get("by_kind") or {}).items():
            t = by_kind.setdefault(k, {"tvrdí": 0, "netvrdí": 0, "částečně": 0})
            for v in ("tvrdí", "netvrdí", "částečně"):
                t[v] += b.get(v, 0)
    kind_rates = {k: {"n": sum(b[v] for v in ("tvrdí", "netvrdí", "částečně")),
                      "unsupported": round((b["netvrdí"] + 0.5 * b["částečně"]) / max(1, sum(b[v] for v in ("tvrdí", "netvrdí", "částečně"))), 3)}
                  for k, b in by_kind.items()}
    return {
        "audit_by_kind": kind_rates,
        "audit_n": sum(a["n"] for a in auds), "audit_judged": judged,
        "unsupported": round((ne + 0.5 * cast) / judged, 4) if judged else None, "unsupported_wilson": [round(lo, 4), round(hi, 4)],
        "human_n": hn, "human_unsupported": round(sum(hun) / hn, 4) if hn and hun else None,
        "agreement": round(agree / agree_n, 3) if agree_n else None, "agreement_n": agree_n,
        "judge": next((a["judge"] for a in auds if a.get("judge")), None),
        "readable_no_pct": round(sum(a["readable_no_pct"] for a in rn) / len(rn), 1) if rn else None,
    }


def _sum_dicts(ds: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return out


def run(sady: list[str], *, strop: int = 0, docs: list[str] | None = None, twice: bool = False,
        with_auto: bool = True, cfg: dict[str, Any] | None = None, verbose: bool = False,
        judge: Judge | None = None, audit_n: int = 0, audit_docs: int = 0) -> dict[str, Any]:
    """Běh nad sadami; vrací zprávu (bez `session` objektů — ty jdou volajícímu
    v `rows_live` pro audity).

    Returns:
        `{"commit","date","dirty","data_fingerprint","sady","strop","rows","totals","rows_live"}`
    """
    cfg = cfg or load_config()
    oracle = make_oracle(cfg)
    all_docs: list[Doc] = []
    for s in sady:
        all_docs.extend(load_sada(s, cfg, only=docs, with_auto=with_auto))
    if docs:
        all_docs = [d for d in all_docs if d.name in docs]
    date, h, dirty = git_info()
    audit_set = {d.name for d in all_docs}
    if audit_docs and audit_docs < len(all_docs):
        # deterministický výběr dokumentů k auditu (rozprostřený, ne abecední začátek)
        audit_set = set(sorted((d.name for d in all_docs), key=lambda n: hashlib.sha1(n.encode()).hexdigest())[:audit_docs])
    mereni_dir = ROOT / cfg.get("mereni", "mereni")
    rows: list[dict[str, Any]] = []
    for d in all_docs:
        print(f"… {d.sada}/{d.name} ({len(d.questions)} otázek)", file=sys.stderr, flush=True)
        try:
            row = run_doc(d, oracle, strop=strop, twice=twice, judge=judge,
                          audit_n=audit_n if d.name in audit_set else 0, audit_dir=mereni_dir, seed=h)
        except KeyError as exc:  # chybějící rozbor bez služby
            print(f"   přeskočeno: {exc}", file=sys.stderr)
            continue
        oracle.flush()
        if judge is not None and hasattr(judge, "flush"):
            judge.flush()
        rows.append(row)
        if verbose:
            for r in row["results"]:
                mark = "✓" if r["ok"] else ("~" if r.get("text_ok") else "✗")
                print(f"  {mark} [{r['sada']}] {r['q']}  →  {r.get('fillers')}  (čekáno {r['expect']}) {r.get('why', '')} dosah={r.get('reach')}")
    report = {
        "commit": h, "date": date, "dirty": dirty, "data_fingerprint": data_fingerprint(all_docs),
        "sady": sady, "strop": strop, "with_auto": with_auto,
        "rows": [{k: v for k, v in r.items() if k != "session"} for r in rows],
        "totals": totals(rows),
        "rows_live": rows,
    }
    return report


def render_report(report: dict[str, Any]) -> str:
    """Markdown zpráva: tabulka po dokumentech + celkem + rozklad."""
    t = report["totals"]
    head = (f"# bench {report['date']} · {report['commit']}{' (dirty)' if report.get('dirty') else ''} · sady {', '.join(report['sady'])}"
            f" · strop {report['strop'] or '—'} · data {report['data_fingerprint']}\n\n")
    cols = "| dokument | vět | slov | yield hl./vše | SAFE | HYP | REJ | zbytek % | open/větu | otázek | správně | kurát. | pokrytí | dosah 0 / 1‑3 / 4‑10 / >10 / jiný seg. | unsupp. | graf |"
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|"
    lines = [head, cols, sep]
    for r in report["rows"]:
        i, q = r["ingest"], r["qa"]
        br = q["by_reach"]
        reach_s = " / ".join(f"{br[b][0]}/{br[b][1]}" for b in ("0", "1-3", "4-10", ">10", "jiný segment"))
        uns = (r.get("audit") or {}).get("unsupported")
        gv = r.get("graph_violations")
        lines.append(f"| {r['doc']} | {i['sentences']} | {i['words']} | {i['yield_main']} / {i['yield']} | {i['claims']['SAFE']} | {i['claims']['HYPOTHESIS']} | {i['claims']['REJECTED']} | {i['residue_pct']} | {i['open_per_sent']} | {q['questions']} | {q['hits']} | {q['curated_hits']}/{q['curated_questions']} | {q['coverage']} | {reach_s} | {'—' if uns is None else f'{100*uns:.1f} %'} | {'—' if gv is None else gv} |")
    br = t["by_reach"]
    reach_s = " / ".join(f"{br.get(b, [0, 0])[0]}/{br.get(b, [0, 0])[1]}" for b in ("0", "1-3", "4-10", ">10", "jiný segment"))
    uns = t.get("unsupported")
    lines.append(f"| **celkem** | {t['sentences']} | {t['words']} | **{t['yield_main']} / {t['yield']}** | {t['claims']['SAFE']} | {t['claims']['HYPOTHESIS']} | {t['claims']['REJECTED']} | {t['residue_pct']} | {t['open_per_sent']} | {t['questions']} | **{t['hits']}** | **{t['curated_hits']}/{t['curated_questions']}** | {t['coverage']} | {reach_s} | {'—' if uns is None else f'{100*uns:.1f} %'} | {'—' if t.get('graph_violations') is None else t['graph_violations']} |")
    lines.append("")
    pct = f"{100.0 * t['hits'] / t['questions']:.1f} %" if t["questions"] else "—"
    cpct = f"{100.0 * t['curated_hits'] / t['curated_questions']:.1f} %" if t["curated_questions"] else "—"
    lines.append(f"QA: {t['hits']}/{t['questions']} = {pct} (kurátorované {t['curated_hits']}/{t['curated_questions']} = {cpct}); po sadách: "
                 + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(t["by_sada"].items())))
    misses: dict[str, int] = {}
    for r in report["rows"]:
        for k, v in r["qa"]["misses"].items():
            misses[k] = misses.get(k, 0) + v
    lines.append("Rozklad chyb: " + ("; ".join(f"{k}: {v}" for k, v in sorted(misses.items(), key=lambda x: -x[1])) or "—"))
    lines.append(f"Determinismus: {'ano' if t['determinism'] else 'NE'} · pravidel {t['rules']} · odvozeno {t['derived']} · zapsáno 100 % vět u {t['written_pct']} % dokumentů")
    gv = t.get("graph_violations")
    lines.append(f"Audit grafu: {'0 porušení' if not gv else f'{gv} porušení — ' + ', '.join(f'{k} {v}' for k, v in sorted(t['graph_violations_by_check'].items()))}")
    if t.get("audit_n"):
        uns = t.get("unsupported")
        w = t.get("unsupported_wilson") or [0, 0]
        hu = t.get("human_unsupported")
        uns_s = "—" if uns is None else f"{100 * uns:.1f} % [{100 * w[0]:.1f}–{100 * w[1]:.1f}]"
        hu_s = "—" if hu is None else f"{100 * hu:.1f} %"
        ag = t.get("agreement")
        ag_s = "—" if ag is None else f"{100 * ag:.0f} % (n={t['agreement_n']})"
        rd = t.get("readable_no_pct")
        rd_s = "—" if rd is None else f"{rd} %"
        lines.append(f"Precision audit: vzorek {t['audit_n']} výroků · soudce {t.get('judge') or '—'} posoudil {t['audit_judged']} → unsupported {uns_s}"
                     f" · člověk {t['human_n']} → {hu_s} · shoda soudce/člověk {ag_s} · „nechápu z grafu“ {rd_s}")
        bk = t.get("audit_by_kind") or {}
        if bk:
            lines.append("  podle druhu: " + " · ".join(f"{k} {100 * v['unsupported']:.0f} % (n={v['n']})" for k, v in sorted(bk.items())))
    if report.get("diff_md"):
        lines.append("\n" + report["diff_md"])
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], mereni: Path) -> tuple[Path, Path]:
    """Ulož zprávu jako `mereni/<datum>-<hash>[-dirty][-strop].json` + `.md`."""
    mereni.mkdir(exist_ok=True)
    stem = f"{report['date']}-{report['commit']}" + ("-dirty" if report.get("dirty") else "") + (f"-strop{report['strop']}" if report.get("strop") else "")
    if report.get("label"):
        stem += f"-{report['label']}"
    j = mereni / f"{stem}.json"
    m = mereni / f"{stem}.md"
    payload = {k: v for k, v in report.items() if k not in ("rows_live", "diff_md")}
    j.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    m.write_text(render_report(report), encoding="utf-8")
    return j, m
