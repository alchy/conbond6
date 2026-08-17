"""Výpis: „která/jaká N“ (omezení výplně skupinou), imperativ „vyjmenuj“, `podřazení` z lexikonu,
nominativ jmenovací („drama R.U.R.“ → R.U.R. ∈ drama). Vše rekonstruovatelné z exportu grafu."""

from pathlib import Path

import pytest

from bench.graphcheck import check_answer, check_graph
from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import RecordedOracle
from cb6.read import read

DATA = Path(__file__).parent / "data" / "parses.json"


@pytest.fixture(scope="module")
def oracle() -> RecordedOracle:
    return RecordedOracle(DATA)


@pytest.fixture()
def s(oracle: RecordedOracle) -> Session:
    s = Session(Memory(), oracle)
    s.ingest("Karel Čapek napsal drama R.U.R.\nKarel Čapek napsal román Krakatit.\nPetr bydlí v Praze.", "karel_čapek")
    return s


def labels(s: Session, a) -> list[str]:
    return [s.memory.node(t).label() for t, _ in a.verdict.fillers]


def test_cteni_ktera_N_je_dira_s_omezenim(oracle: RecordedOracle) -> None:
    m = read(oracle.parse("Která díla napsal Karel Čapek?")).main
    co = m.role("co")
    assert m.mood == "question" and co and co.wh and co.wh_kind == "filler" and [t.lemma for t in co.terms] == ["dílo"]
    assert m.role("který") is None
    # místa nechávají rodinu rolí, jak je (žádné omezení)
    m2 = read(oracle.parse("Jaké je Filipovo auto?")).main
    assert m2.role("jaký") is not None and m2.role("jaký").wh


def test_cteni_imperativ_vypisu_je_otazka_list(oracle: RecordedOracle) -> None:
    m = read(oracle.parse("Vyjmenuj všechna díla Karla Čapka.")).main
    assert m.mood == "question" and m.kind == "list" and m.pred is None
    co, ci = m.role("co"), m.role("čí")
    assert co and co.wh and [t.lemma for t in co.terms] == ["dílo"] and co.terms[0].quant == "∀"
    assert ci and [t.label() for t in ci.terms] == ["Karel Čapek"]
    m2 = read(oracle.parse("Vyjmenuj všechna dramata.")).main
    assert m2.kind == "list" and m2.role("čí") is None


def test_nominativ_jmenovaci_je_entita_v_tride(oracle: RecordedOracle) -> None:
    r = read(oracle.parse("Karel Čapek napsal drama R.U.R."))
    co = r.main.role("co")
    assert co and co.terms[0].kind == "entity" and co.terms[0].cls == ("drama", ()) and co.terms[0].forms == ("R.U.R.",)
    assert not r.residue


def test_ktera_dila_pres_podrazeni_a_rekonstrukce(s: Session) -> None:
    a = s.say("Která díla napsal Karel Čapek?")
    assert set(labels(s, a)) == {"R.U.R.", "Krakatit"}
    p = a.verdict.fillers[0][1]
    assert any(st.startswith("podřazení:") for st in p.steps) and ("lex", "drama", "dílo") in p.hard or ("lex", "román", "dílo") in p.hard
    g = s.memory.graph()
    assert check_graph(g) == []
    for _, p in a.verdict.fillers:
        assert check_answer(g, list(p.statements), list(p.hard)) == []
    # užší třída bez lexikonu: jen romány
    b = s.say("Které romány napsal Karel Čapek?")
    assert labels(s, b) == ["Krakatit"] and not any(h[0] == "lex" for h in b.verdict.fillers[0][1].hard)
    # o Petrovi žádná díla → NEVÍM, ne „Praha“
    c = s.say("Která díla napsal Petr?")
    assert c.verdict.fillers == []


def test_vyjmenuj_dila_karla_capka_nezapisuje_a_vypise(s: Session) -> None:
    n = len(s.memory.statements)
    a = s.say("Vyjmenuj všechna díla Karla Čapka.")
    assert len(s.memory.statements) == n  # rozkaz se nezapsal
    assert set(labels(s, a)) == {"R.U.R.", "Krakatit"}
    assert any(st.startswith("napsat(kdo: Karel Čapek") for st in a.verdict.fillers[0][1].steps)
    g = s.memory.graph()
    for _, p in a.verdict.fillers:
        assert check_answer(g, list(p.statements), list(p.hard)) == []
    b = s.say("Vypiš romány Karla Čapka.")
    assert labels(s, b) == ["Krakatit"]
    c = s.say("Vyjmenuj všechna dramata.")
    assert labels(s, c) == ["R.U.R."]


def test_uc_podrazeni_z_konzole_rozsiri_vypis(s: Session) -> None:
    s.say("Krakatit je román.")
    r = s.say("!uč román < próza")
    assert "román ⊆ próza" in r.text
    # „próza“ ⊇ román je i v seedu; řečený řádek má přednost (týž směr) — výpis próz jde
    a = s.say("Vypiš prózy Karla Čapka.")
    assert labels(s, a) == ["Krakatit"]
    assert any(l.authority == "said" for _, p in a.verdict.fillers for l in [s.memory.links[i] for i in p.links])


def test_vypis_podle_tematu_dokumentu_je_priznany(oracle: RecordedOracle) -> None:
    """Text díla jen vyjmenovává (typing z appos), autorství neříká: výpis podle tématu je výchozí volba."""
    s = Session(Memory(), oracle)
    s.ingest("Karel Čapek se narodil v Malých Svatoňovicích.\nKrakatit je román.", "karel_čapek")
    # téma dokumentu = Karel Čapek (drží ho uzel dokumentu)
    assert s.topics.get("karel_čapek") and s.memory.ensure_document("karel_čapek").base == s.topics["karel_čapek"]
    a = s.say("Vyjmenuj všechna díla Karla Čapka.")
    # „Krakatit je román“ se čte jako obecná věta (krakatit ⊆ román), přesto je to člen dílo přes podřazení
    if a.verdict.fillers:
        assert any("výpis podle tématu dokumentu" in d for _, p in a.verdict.fillers for d in p.defaults)
