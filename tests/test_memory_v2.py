"""Task 1 — paměť v2: druhá osa výroku (`claim`), alternativy, pravidlo, vnoření."""
from cb6.memory import Memory, Statement, Provenance


def _st(pred, claim="SAFE", mood="assert", **kw):
    return Statement("", pred, "verb", claim=claim, mood=mood, prov=Provenance("d", 1, "věta"), **kw)


def test_knowledge_filtruje_claim_a_mood():
    m = Memory()
    a = m.attach(_st("přijít"))
    h = m.attach(_st("přijít", claim="HYPOTHESIS"))
    r = m.attach(_st("přijít", claim="REJECTED", reason="disjunkce"))
    p = m.attach(_st("přijít", mood="pattern"))
    assert [s.id for s in m.knowledge()] == [a.id]
    assert [s.id for s in m.by_claim("HYPOTHESIS")] == [h.id]
    assert m.statements[r.id].reason == "disjunkce"
    assert p.id not in [s.id for s in m.knowledge()]


def test_set_claim_meni_status_a_zapisuje_duvod():
    m = Memory()
    h = m.attach(_st("přijít", claim="HYPOTHESIS"))
    m.set_claim(h.id, "SAFE", "potvrzeno dialogem (tah 3)")
    assert m.statements[h.id].claim == "SAFE"
    assert "potvrzeno" in m.statements[h.id].defaults[-1]


def test_revoke_kaskaduje_pres_parent_i_rule():
    m = Memory()
    main = m.attach(_st("říci"))
    nested = m.attach(_st("přijít", mood="reported", parent=main.id))
    rule = m.attach(Statement("", None, "rule", prov=Provenance("d", 2, "pokud…")))
    derived = m.attach(_st("přijít", grade="derived", rule=rule.id, derived_from=main.id))
    assert set(m.revoke(main.id, "test")) == {main.id, nested.id, derived.id}
    m2 = Memory()
    r2 = m2.attach(Statement("", None, "rule", prov=Provenance("d", 2, "pokud…")))
    d2 = m2.attach(_st("přijít", grade="derived", rule=r2.id))
    assert set(m2.revoke(r2.id, "test")) == {r2.id, d2.id}


def test_json_v2_round_trip_a_cteni_v1():
    m = Memory()
    m.attach(_st("přijít", claim="HYPOTHESIS", alternatives=["s0009"]))
    d = m.to_json()
    assert d["format"] == "conbond6-memory/2"
    m2 = Memory.from_json(d)
    assert m2.statements["s0001"].claim == "HYPOTHESIS" and m2.statements["s0001"].alternatives == ["s0009"]
    d1 = dict(d)
    d1["format"] = "conbond5-memory/1"
    for s in d1["statements"]:
        for k in ("claim", "alternatives", "rule", "parent"):
            s.pop(k, None)
    m3 = Memory.from_json(d1)
    assert m3.statements["s0001"].claim == "SAFE"
