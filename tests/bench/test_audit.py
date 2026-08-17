"""Task 5 — precision audit: vzorek, soudce, lidské odpovědi, unsupported + Wilson."""
from bench.audit import fingerprint, run_audit, sample, wilson
from bench.judge import CachedJudge, RecordedJudge, _parse_verdict
from tests.bench.test_metrics import _mem


def test_wilson_interval():
    lo, hi = wilson(1, 50)
    assert 0.0 < lo < 0.02 < hi < 0.11
    assert wilson(0, 0) == (0.0, 1.0)


def test_sample_je_deterministicky_a_jen_znalost():
    m = _mem()
    a = sample(m, 10, "abc")
    b = sample(m, 10, "abc")
    assert [s.id for s in a] == [s.id for s in b] == ["s0001"]


def test_run_audit_pocita_unsupported_a_shodu(tmp_path):
    m = _mem()
    st = m.statements["s0001"]
    render = m.render_short(st)
    fp = fingerprint(render, "Alois Jirásek se narodil v Hronově.")
    judge = RecordedJudge({fp: ("tvrdí", "")})
    human = tmp_path / "audit-d.json"
    human.write_text('{"%s": ["tvrdí", "", "a"]}' % fp)
    r = run_audit(m, "d", judge, human, n=50, seed="x")
    assert r["n"] == 1 and r["judged"] == 1 and r["unsupported"] == 0.0
    assert r["human_n"] == 1 and r["agreement"] == 1.0 and r["readable_no_pct"] == 0.0


def test_cached_judge_nesoudi_dvakrat(tmp_path):
    m = _mem()
    st = m.statements["s0001"]
    render = m.render_short(st)
    fp = fingerprint(render, "Alois Jirásek se narodil v Hronově.")
    inner = RecordedJudge({fp: ("částečně", "chybí rok")})
    cj = CachedJudge(inner, tmp_path / "cache.json")
    assert cj.judge(render, "Alois Jirásek se narodil v Hronově.") == ("částečně", "chybí rok")
    assert cj.judge(render, "Alois Jirásek se narodil v Hronově.") == ("částečně", "chybí rok")
    assert inner.calls == 1
    cj.flush()
    cj2 = CachedJudge(RecordedJudge({}), tmp_path / "cache.json")
    assert cj2.judge(render, "Alois Jirásek se narodil v Hronově.")[0] == "částečně"


def test_parse_verdict_tolerantni():
    assert _parse_verdict('{"verdikt": "netvrdí", "pozn": "role"}') == ("netvrdí", "role")
    assert _parse_verdict('Podle mě: {"verdikt":"tvrdí","pozn":""}')[0] == "tvrdí"
    assert _parse_verdict("částečně, chybí rok")[0] == "částečně"
    assert _parse_verdict("nevím")[0] == "částečně"
