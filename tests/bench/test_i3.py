"""Task 11 — I‑3 v logice i v benchi: hypotéza nikdy ve verdiktu; audit grafu to hlídá."""
from cb6.logic import evaluate
from cb6.memory import Memory, Provenance, Role, Statement

from bench.graphcheck import check_answer


def test_hypoteza_nikdy_ve_verdiktu():
    m = Memory()
    m.ensure_document("d")
    z = m.new_sentence("d", 1, "On namaloval obraz.")
    e = m.new_node("entity", "Josef", names=["Josef"])
    g = m.new_node("group", "obraz")
    hyp = m.attach(Statement("", "namalovat", "verb", sentence=z.id, prov=Provenance("d", 1), claim="HYPOTHESIS",
                             roles=[Role("kdo", [e.id], "·"), Role("co", [g.id], "∃")]))
    q = Statement("", "namalovat", "verb", mood="question", roles=[Role("kdo", [e.id], "·"), Role("co", [g.id], "∃")])
    v = evaluate(m, q)
    assert v.value == "NEVÍM" and hyp.id not in [s for p in v.proofs for s in p.statements]
    assert any("hypotéza" in n for n in v.notes)
    # kdyby se hypotéza do důkazu dostala, audit grafu to chytí (I‑12 rekonstrukce)
    assert any(x.check == "status" for x in check_answer(m.graph(), [hyp.id], []))
