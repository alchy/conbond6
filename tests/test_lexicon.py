"""Lexikon znalostních vazeb: řádky, operátory `třída`/`implikace`, shoda predikátů, materializace."""

from pathlib import Path

import pytest

from cb6.lexicon import Lexicon, Link, load_seed, parse_teach, set_seed_enabled
from cb6.memory import Memory


def rows() -> list[Link]:
    return [
        Link("lex:t:1", "třída", ("říci", "říkat"), "same", "seed", "test#1"),
        Link("lex:t:2", "třída", ("říci", "pravit"), "same", "seed", "test#2"),
        Link("lex:i:3", "implikace", ("tvrdit", "říci"), "implies", "seed", "test#3"),
        Link("lex:i:4", "implikace", ("bydlet", "žít"), "implies", "seed", "test#4"),
        Link("lex:r:5", "třída", ("vydat", "napsat"), "related", "seed", "test#5"),
    ]


def test_trida_je_symetricka_a_tranzitivni() -> None:
    lx = Lexicon(rows())
    assert lx.rep("říkat") == lx.rep("pravit") == lx.rep("říci")
    m = lx.match("pravit", "říkat")
    assert m is not None and [l.id for l in m.links] == ["lex:t:1", "lex:t:2"] and "~" in m.step
    assert lx.match("říkat", "pravit") is not None  # obráceně také
    assert lx.match("říci", "říci") is not None and lx.match("říci", "říci").links == ()


def test_implikace_je_jednosmerna() -> None:
    lx = Lexicon(rows())
    # fakt „bydlí“ odpovídá na otázku „žije“, ne naopak
    m = lx.match("žít", "bydlet")
    assert m is not None and m.derived and "⇒" in m.step and m.links[0].id == "lex:i:4"
    assert lx.match("bydlet", "žít") is None
    # řetěz: tvrdit ⇒ říci ~ říkat
    m2 = lx.match("říkat", "tvrdit")
    assert m2 is not None and [l.id for l in m2.links] == ["lex:i:3", "lex:t:1"]


def test_related_nikdy_ve_verdiktu_jen_pro_recall() -> None:
    lx = Lexicon(rows())
    assert lx.match("napsat", "vydat") is None and lx.match("vydat", "napsat") is None
    assert lx.related("vydat", "napsat") and lx.related("napsat", "vydat")
    assert lx.related("bydlet", "žít") and lx.related("pravit", "říkat")
    assert not lx.related("bydlet", "napsat")


def test_neznamy_predikat_je_levny_a_nic_nedela() -> None:
    lx = Lexicon(rows())
    assert lx.match("plavat", "běžet") is None and not lx.related("plavat", "běžet")


def test_validace_radku() -> None:
    with pytest.raises(ValueError):
        Lexicon([Link("x", "třída", ("a", "b"), "implies", "seed", "z")])
    with pytest.raises(ValueError):
        Lexicon([Link("x", "implikace", ("a", "b"), "same", "seed", "z")])
    with pytest.raises(ValueError):
        Lexicon([Link("x", "kouzlo", ("a", "b"), "same", "seed", "z")])
    with pytest.raises(ValueError):
        Lexicon([Link("x", "třída", ("a",), "same", "seed", "z")])
    with pytest.raises(ValueError):
        Lexicon([Link("x", "třída", ("a", "b"), "same", "seed", "")])  # bez zdroje řádek neexistuje


def test_json_radku_ma_ceske_klice() -> None:
    l = Link("lex:t:1", "třída", ("říci", "říkat"), "same", "seed", "test#1", "vid")
    d = l.to_json()
    assert set(d) == {"id", "op", "args", "síla", "autorita", "zdroj", "pozn"}
    assert Link.from_json(d) == l


def test_seed_se_nacte_a_je_konzistentni() -> None:
    seed = load_seed()
    assert len(seed) > 50
    ids = [l.id for l in seed]
    assert len(ids) == len(set(ids)) and all(l.source for l in seed)
    lx = Lexicon(seed)
    # to, kvůli čemu tabulka vznikala: bydlet ⇒ žít; vydat ≁ napsat; padnout ≁ zemřít
    assert lx.match("žít", "bydlet") is not None
    assert lx.match("napsat", "vydat") is None and lx.related("napsat", "vydat")
    assert lx.match("zemřít", "padnout") is None
    assert lx.match("zemřít", "umřít") is not None and not lx.match("zemřít", "umřít").derived


def test_parse_teach() -> None:
    assert parse_teach("kázat = hlásat") == ("třída", ("kázat", "hlásat"), "same")
    assert parse_teach("bydlet => žít") == ("implikace", ("bydlet", "žít"), "implies")
    assert parse_teach("vydat ~ napsat") == ("třída", ("vydat", "napsat"), "related")
    assert parse_teach("nesmysl") is None


def test_pamet_drzi_a_materializuje_radky() -> None:
    m = Memory()
    lx = Lexicon.for_memory(m)
    assert lx.match("žít", "bydlet") is not None  # seed
    m.use_links(lx.match("žít", "bydlet").links)
    said = m.add_link("třída", ("kázat", "hlásat"), "same", "said", "dialog tah 1")
    assert said.id.startswith("lex:said:")
    lx2 = Lexicon.for_memory(m)
    assert lx2.match("hlásat", "kázat") is not None
    g = m.graph()
    vazby = [n for n, d in g.nodes(data=True) if d.get("kind") == "vazba"]
    assert set(vazby) == set(m.links)  # v exportu jsou jen použité + řečené
    d = g.nodes[said.id]
    assert d["op"] == "třída" and d["síla"] == "same" and d["zdroj"] == "dialog tah 1" and d["autorita"] == "said"
    # JSON tam a zpět
    m2 = Memory.from_json(m.to_json())
    assert set(m2.links) == set(m.links) and Lexicon.for_memory(m2).match("hlásat", "kázat") is not None


def test_stara_pamet_s_learned_synonyms_se_prevede() -> None:
    d = Memory().to_json()
    d["learned"] = {"roles": {}, "synonyms": {"stvořit": "napsat"}}
    m = Memory.from_json(d)
    assert any(l.args == ("stvořit", "napsat") and l.authority == "said" for l in m.links.values())
    assert Lexicon.for_memory(m).match("napsat", "stvořit") is not None


def test_ablace_seed() -> None:
    set_seed_enabled(False)
    try:
        assert Lexicon.for_memory(Memory()).match("žít", "bydlet") is None
    finally:
        set_seed_enabled(True)
    assert Lexicon.for_memory(Memory()).match("žít", "bydlet") is not None


def test_odpoved_pres_lexikon_je_rekonstruovatelna_z_exportu() -> None:
    """I‑12: krok `lex` ověří audit jen z uzlů `vazba` v exportu; nematerializovaný řádek = porušení."""
    from bench.graphcheck import check_answer, check_graph, lex_path
    from cb6.dialog import Session
    from cb6.oracle import RecordedOracle
    s = Session(Memory(), RecordedOracle(Path(__file__).parent / "data" / "parses.json"))
    s.ingest("Petr bydlí v Praze.", "t")
    a = s.say("Kde žije Petr?")
    v = a.verdict
    assert v is not None and v.fillers
    p = v.fillers[0][1]
    g = s.memory.graph()
    assert check_graph(g) == []
    assert check_answer(g, list(p.statements), list(p.hard)) == []
    assert lex_path(g, "bydlet", "žít") == ["lex:syn:0031"] and lex_path(g, "žít", "bydlet") is None
    # bez materializace by krok nebyl doložený
    g.remove_node("lex:syn:0031")
    assert [x.check for x in check_answer(g, list(p.statements), list(p.hard))] == ["rekonstrukce"]


def test_derive_pres_lexikon_nese_uses_rule_na_vazbu() -> None:
    """Odvození pravidlem přes implikaci: odvozený výrok má `links` → hrana `uses_rule` na uzel `vazba`."""
    from bench.graphcheck import check_graph
    from cb6.dialog import Session
    from cb6.oracle import RecordedOracle
    s = Session(Memory(), RecordedOracle(Path(__file__).parent / "data" / "parses.json"))
    s.ingest("Pokud Petr žije v Praze, platí Petr daně v Praze.\nPetr bydlí v Praze.", "t")
    d = [st for st in s.memory.knowledge() if st.grade == "derived"]
    assert len(d) == 1 and d[0].links == ["lex:syn:0031"] and any(x.startswith("implikace: bydlet ⇒ žít") for x in d[0].defaults)
    g = s.memory.graph()
    assert (d[0].id, "lex:syn:0031") in {(u, v) for u, v, x in g.edges(data=True) if x["type"] == "uses_rule"}
    assert check_graph(g) == []
    assert s.say("Platí Petr daně?").verdict.value == "ANO"


def test_podrazeni_je_orientovane_a_tranzitivni() -> None:
    """`podřazení`: drama ⊆ dílo — fakt „x ∈ drama“ sedí na dotaz „dílo“, ne naopak; řetězí se."""
    lx = Lexicon([
        Link("lex:p:1", "podřazení", ("drama", "dílo"), "implies", "seed", "t#1"),
        Link("lex:p:2", "podřazení", ("komedie", "drama"), "implies", "seed", "t#2"),
    ])
    m = lx.match("dílo", "komedie")
    assert m is not None and [l.id for l in m.links] == ["lex:p:2", "lex:p:1"] and m.derived and "⊆" in m.step
    assert lx.match("komedie", "dílo") is None
    assert parse_teach("drama < dílo") == ("podřazení", ("drama", "dílo"), "implies")
    with pytest.raises(ValueError):
        Lexicon([Link("x", "podřazení", ("a", "b"), "same", "seed", "z")])
    seed = Lexicon(load_seed())
    assert seed.match("dílo", "román") is not None and seed.match("dílo", "drama") is not None
