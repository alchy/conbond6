"""Task 3 — regresní rozdíl zpráv (nový i starý formát)."""
from bench.diff import diff_reports, render_diff


def test_diff_totals_a_render():
    prev = {"totals": {"yield": 3.0, "hits": 10, "questions": 20, "unsupported": None}, "rows": [{"doc": "a", "ingest": {"yield": 3.0}, "qa": {"hits": 10, "questions": 20}}]}
    cur = {"totals": {"yield": 3.4, "hits": 12, "questions": 20, "unsupported": 0.02}, "rows": [{"doc": "a", "ingest": {"yield": 3.4}, "qa": {"hits": 12, "questions": 20}}]}
    d = diff_reports(prev, cur)
    assert d["totals"]["yield"] == (3.0, 3.4)
    out = render_diff(d)
    assert "yield 3→3.4" in out and "QA 10→12" in out


def test_diff_umi_stary_format_conbond5():
    old = [{"doc": "a", "sentences": 10, "statements": 30, "hits": 5, "questions": 8, "residue_tokens": 10, "tokens": 100, "open": 5}]
    cur = {"totals": {"yield": 3.4, "hits": 6, "questions": 8, "unsupported": None, "residue_pct": 9.0, "open_per_sent": 0.4},
           "rows": [{"doc": "a", "ingest": {"yield": 3.4, "safe": 28, "residue_pct": 9.0, "open_per_sent": 0.4}, "qa": {"hits": 6, "questions": 8}}]}
    d = diff_reports(old, cur)
    assert d["rows"]["a"]["hits"] == (5, 6) and d["rows"]["a"]["residue_pct"] == (10.0, 9.0)
