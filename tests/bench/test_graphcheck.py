"""Task 4 — audit grafu jen nad exportem (I‑11, I‑12)."""
import networkx as nx

from bench.graphcheck import check_answer, check_graph, hard_path


def _g():
    g = nx.MultiDiGraph()
    g.add_node("d0001", kind="document")
    g.add_node("z0001", kind="sentence", text="…")
    g.add_edge("z0001", "d0001", type="part_of")
    g.add_node("e0001", kind="entity")
    g.add_edge("z0001", "e0001", type="mention", role="kdo", form="Petr", segment="")
    g.add_node("s0001", kind="statement", claim="SAFE", grade="read", life="active", mood="assert", defaults=[], residue=[], reason="", role_authorities={"kdo": "structural"})
    g.add_edge("s0001", "z0001", type="source")
    g.add_edge("s0001", "e0001", type="role:kdo", authority="structural")
    return g


def test_cisty_graf_bez_poruseni():
    assert check_graph(_g()) == []


def test_vyrok_bez_source_a_osirely_uzel():
    g = _g()
    g.add_node("s0002", kind="statement", claim="SAFE", grade="read", life="active", mood="assert", defaults=[], residue=[], reason="", role_authorities={})
    g.add_node("g0001", kind="group")
    v = {(x.check, x.node) for x in check_graph(g)}
    assert ("provenience", "s0002") in v and ("osiřelost", "g0001") in v


def test_derived_bez_pravidla_rejected_bez_duvodu_hypoteza_v_dukazu():
    g = _g()
    g.add_node("s0003", kind="statement", claim="SAFE", grade="derived", life="active", mood="assert", defaults=[], residue=[], reason="", role_authorities={})
    g.add_edge("s0003", "z0001", type="source")
    g.add_node("s0005", kind="statement", claim="REJECTED", grade="read", life="active", mood="assert", defaults=[], residue=[], reason="", role_authorities={})
    g.add_edge("s0005", "z0001", type="source")
    checks = {x.check for x in check_graph(g)}
    assert "derivace" in checks and "status" in checks
    g.add_node("s0004", kind="statement", claim="HYPOTHESIS", grade="read", life="active", mood="assert", defaults=[], residue=[], reason="", role_authorities={})
    g.add_edge("s0004", "z0001", type="source")
    assert any(x.check == "status" for x in check_answer(g, ["s0004"], []))


def test_check_answer_uzaver_je_cesta_v_grafu():
    g = _g()
    g.add_node("g0001", kind="group")
    g.add_node("g0002", kind="group")
    g.add_edge("e0001", "g0001", type="member", statement="s0001")
    g.add_edge("g0001", "g0002", type="subset", statement="s0001")
    g.add_edge("z0001", "g0001", type="mention", role="co", form="", segment="")
    g.add_edge("z0001", "g0002", type="mention", role="co", form="", segment="")
    assert hard_path(g, "member", "e0001", "g0002") == ["e0001", "g0001", "g0002"]
    assert check_answer(g, ["s0001"], [("member", "e0001", "g0001"), ("subset", "g0001", "g0002"), ("member", "e0001", "g0002")]) == []
    assert any(x.check == "rekonstrukce" for x in check_answer(g, ["s0001"], [("subset", "e0001", "g0002")]))


def test_check_answer_cas_a_disjunkce():
    g = _g()
    g.add_node("t0001", kind="time", t_kind="point", t_start=[1851, 8, 23], t_end=None)
    g.add_node("t0002", kind="time", t_kind="year", t_start=[1851, 1, 1], t_end=[1851, 12, 31])
    g.add_node("g0001", kind="group"); g.add_node("g0002", kind="group")
    g.add_edge("g0001", "g0002", type="disjoint", statement="s0001")
    for n in ("t0001", "t0002", "g0001", "g0002"):
        g.add_edge("z0001", n, type="mention", role="x", form="", segment="")
    assert check_answer(g, ["s0001"], [("time", "t0001", "t0002"), ("disjoint", "g0001", "g0002")]) == []
    assert any(x.check == "rekonstrukce" for x in check_answer(g, ["s0001"], [("time", "t0002", "t0001")]))
