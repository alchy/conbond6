"""Regresní rozdíl dvou zpráv benche (I‑10: každý tah předloží rozdíl proti
předchozímu commitu).

Umí i starý formát conbond5 (`mereni/bench-vse.json`: seznam řádků s klíči
`statements`, `hits`, `questions`, `residue_tokens`, `tokens`, `open`,
`sentences`) — aby první zpráva conbond6 měla s čím srovnat.
"""

from __future__ import annotations

from typing import Any


def _norm_report(rep: Any) -> dict[str, Any]:
    """Sjednoť starý (seznam řádků) a nový formát na `{"rows": {doc: {...}}, "totals": {...}}`."""
    if isinstance(rep, list):  # conbond5
        rows: dict[str, dict[str, Any]] = {}
        for r in rep:
            words = None
            rows[str(r["doc"])] = {
                "yield": None, "safe": r.get("statements"), "hits": r.get("hits"), "questions": r.get("questions"),
                "residue_pct": round(100.0 * r["residue_tokens"] / r["tokens"], 1) if r.get("tokens") else None,
                "open_per_sent": round(r["open"] / r["sentences"], 2) if r.get("sentences") else None,
                "unsupported": None, "claims": None, "words": words,
            }
        tot = {
            "yield": None, "safe": sum(r.get("statements", 0) for r in rep), "hits": sum(r.get("hits", 0) for r in rep),
            "questions": sum(r.get("questions", 0) for r in rep), "unsupported": None,
            "residue_pct": round(100.0 * sum(r["residue_tokens"] for r in rep) / sum(r["tokens"] for r in rep), 1) if rep else None,
            "open_per_sent": round(sum(r["open"] for r in rep) / sum(r["sentences"] for r in rep), 2) if rep else None,
            "curated_hits": None, "claims": None,
        }
        return {"rows": rows, "totals": tot}
    rows = {}
    for r in rep.get("rows", []):
        i, q = r.get("ingest", {}), r.get("qa", {})
        rows[str(r["doc"])] = {
            "yield": i.get("yield"), "safe": i.get("safe"), "hits": q.get("hits"), "questions": q.get("questions"),
            "residue_pct": i.get("residue_pct"), "open_per_sent": i.get("open_per_sent"),
            "unsupported": (r.get("audit") or {}).get("unsupported"), "claims": i.get("claims"), "words": i.get("words"),
        }
    t = rep.get("totals", {})
    tot = {k: t.get(k) for k in ("yield", "safe", "hits", "questions", "unsupported", "residue_pct", "open_per_sent", "curated_hits", "claims")}
    return {"rows": rows, "totals": tot}


def diff_reports(prev: Any, cur: Any) -> dict[str, Any]:
    """Rozdíl `cur − prev` po dokumentech a v součtu; hodnoty jako dvojice (před, po)."""
    a, b = _norm_report(prev), _norm_report(cur)
    keys = ("yield", "safe", "hits", "questions", "residue_pct", "open_per_sent", "unsupported")
    out: dict[str, Any] = {"totals": {k: (a["totals"].get(k), b["totals"].get(k)) for k in keys}, "rows": {}}
    out["totals"]["curated_hits"] = (a["totals"].get("curated_hits"), b["totals"].get("curated_hits"))
    out["totals"]["claims"] = (a["totals"].get("claims"), b["totals"].get("claims"))
    for doc in sorted(b["rows"]):  # jen dokumenty přítomné v nové zprávě
        ra, rb = a["rows"].get(doc, {}), b["rows"].get(doc, {})
        out["rows"][doc] = {k: (ra.get(k), rb.get(k)) for k in keys}
    return out


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:.0f}"
    return str(v)


def _arrow(pair: tuple[Any, Any]) -> str:
    a, b = pair
    if a is None and b is None:
        return "—"
    return f"{_fmt(a)}→{_fmt(b)}"


def render_diff(d: dict[str, Any]) -> str:
    """Markdown: řádek součtů + tabulka dokumentů, kde se něco změnilo."""
    t = d["totals"]
    lines = ["## Rozdíl proti předchozí zprávě",
             f"celkem: yield {_arrow(t['yield'])} · SAFE {_arrow(t['safe'])} · QA {_arrow(t['hits'])}/{_arrow(t['questions'])}"
             f" · unsupported {_arrow(t['unsupported'])} · zbytek % {_arrow(t['residue_pct'])} · open/větu {_arrow(t['open_per_sent'])}"]
    changed = [(doc, r) for doc, r in d["rows"].items() if any(x[0] != x[1] for x in r.values())]
    if changed:
        lines.append("")
        lines.append("| dokument | yield | SAFE | QA hits | zbytek % | open/větu | unsupported |")
        lines.append("|---|---|---|---|---|---|---|")
        for doc, r in changed:
            lines.append(f"| {doc} | {_arrow(r['yield'])} | {_arrow(r['safe'])} | {_arrow(r['hits'])} | {_arrow(r['residue_pct'])} | {_arrow(r['open_per_sent'])} | {_arrow(r['unsupported'])} |")
    else:
        lines.append("(žádný dokument se nezměnil)")
    return "\n".join(lines) + "\n"
