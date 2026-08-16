"""Task 2 — export grafu nese provenienci, vnoření, alternativy, otevřené položky a zbytek (I‑11)."""
from cb6.memory import Memory, Statement, Role, Provenance


def test_export_nese_zdroj_vnoreni_alternativu_open_a_zbytek():
    m = Memory()
    d = m.ensure_document("d")
    z = m.new_sentence("d", 1, "Petr řekl, že přijde.")
    main = m.attach(Statement("", "říci", "verb", sentence=z.id, prov=Provenance("d", 1), residue=[("prý", "advmod")]))
    child = m.attach(Statement("", "přijít", "verb", sentence=z.id, mood="reported", parent=main.id, prov=Provenance("d", 1)))
    hyp = m.attach(Statement("", "přijít", "verb", sentence=z.id, claim="HYPOTHESIS", alternatives=[main.id], prov=Provenance("d", 1)))
    o = m.add_open("reference", "on", "Kdo?", main.id)
    g = m.graph()
    types = {(u, v, dd["type"]) for u, v, dd in g.edges(data=True)}
    assert (main.id, z.id, "source") in types and (child.id, z.id, "source") in types and (hyp.id, z.id, "source") in types
    assert (z.id, d.id, "part_of") in types
    assert (child.id, main.id, "nested_in") in types
    assert (hyp.id, main.id, "alternative_of") in types
    assert (o.id, main.id, "about") in types
    assert (main.id, z.id, "residue_of") in types
    assert g.nodes[main.id]["claim"] == "SAFE" and g.nodes[hyp.id]["claim"] == "HYPOTHESIS"
    assert g.nodes[z.id]["kind"] == "sentence" and g.nodes[z.id]["text"].startswith("Petr")
    assert g.nodes[o.id]["kind"] == "open" and g.nodes[o.id]["question"] == "Kdo?"


def test_export_derived_ma_derived_from_a_uses_rule():
    m = Memory()
    r = m.attach(Statement("", None, "rule", prov=Provenance("d", 1)))
    f = m.attach(Statement("", "přijít", "verb", prov=Provenance("d", 2)))
    dd = m.attach(Statement("", "přijít", "verb", grade="derived", rule=r.id, derived_from=f.id, prov=Provenance("d", 2)))
    g = m.graph()
    types = {(u, v, x["type"]) for u, v, x in g.edges(data=True)}
    assert (dd.id, f.id, "derived_from") in types and (dd.id, r.id, "uses_rule") in types


def test_export_mention_a_segment():
    m = Memory()
    d = m.ensure_document("d")
    seg = m.new_segment("d", 1, "Život")
    z = m.new_sentence("d", 1, "Alois Jirásek se narodil v Hronově.", segment=seg.id)
    e = m.new_node("entity", "Jirásek", names=["Alois Jirásek"])
    m.note_mention(z.id, e.id, "kdo", "Alois Jirásek")
    g = m.graph()
    types = {(u, v, x["type"]) for u, v, x in g.edges(data=True)}
    assert (z.id, seg.id, "part_of") in types and (seg.id, d.id, "part_of") in types
    ment = [x for u, v, x in g.edges(data=True) if x["type"] == "mention" and u == z.id and v == e.id]
    assert ment and ment[0]["role"] == "kdo" and ment[0]["segment"] == seg.id


def test_role_hrana_nese_autoritu():
    m = Memory()
    e = m.new_node("entity", "Petr", names=["Petr"])
    st = m.attach(Statement("", "bydlet", "verb", prov=Provenance("d", 1), roles=[Role("kde", [e.id], "·", "default")]))
    g = m.graph()
    edge = [x for u, v, x in g.edges(data=True) if x["type"] == "role:kde"][0]
    assert edge["authority"] == "default"
    assert g.nodes[st.id]["role_authorities"] == {"kde": "default"}
