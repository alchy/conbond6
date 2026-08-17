"""Bench: porovnání očekávané odpovědi s výplněmi (jména, tvary, letopočty, počty)."""

from bench.qa import answer_matches
from cb6.chronos import TimeSpec
from cb6.memory import Memory


def test_answer_matches_forms_years_counts() -> None:
    m = Memory()
    hronov = m.ensure_place(["Hronov"], ["Hronově"])
    t = m.ensure_time(TimeSpec("point", "23. 8. 1851", (1851, 8, 23), (1851, 8, 23)))
    ok, _ = answer_matches(m, ["Hronově"], [hronov.id], "")
    assert ok
    ok, _ = answer_matches(m, ["roce 1851"], [t.id], "")
    assert ok
    ok, _ = answer_matches(m, ["42"], ["count:42"], "")
    assert ok
    ok, text_ok = answer_matches(m, ["Praze"], [hronov.id], "vím: bydlet(kde: Praha)")
    assert not ok and not text_ok  # „Praze“ není v textu doslova; text_hit je přísný
    ok, text_ok = answer_matches(m, ["1930"], [], "zemřít(kdy: 12. 3. 1930)")
    assert not ok and text_ok


def test_hard_path_member_zrcadli_member_star() -> None:
    """Audit musí zrcadlit paměť: `member_star` smí před `member` jít po `same_as`
    (třída jmen prvku) a za ním po `subset`/`restricts`/`same_as` — jinak by
    krok, který paměť udělala, audit z téhož grafu neuznal (nález 17. 8., výpis)."""
    import networkx as nx
    from bench.graphcheck import hard_path
    g = nx.MultiDiGraph()
    for n in ("e1", "e2", "g1", "g2", "g3"):
        g.add_node(n, kind="entity" if n.startswith("e") else "group")
    g.add_edge("e1", "e2", type="same_as")      # Jan Žižka = Jan Hus (třída jmen)
    g.add_edge("e2", "g1", type="member")       # Jan Hus ∈ hra[historický]
    g.add_edge("g1", "g2", type="restricts")    # hra[historický] → hra
    g.add_edge("g3", "g2", type="same_as")      # g3 = hra
    assert hard_path(g, "member", "e1", "g1") is not None
    assert hard_path(g, "member", "e1", "g2") is not None
    assert hard_path(g, "member", "e1", "g3") is not None
    assert hard_path(g, "member", "e1", "e2") is None    # bez hrany member to není členství
    assert hard_path(g, "subset", "g1", "g3") is not None
