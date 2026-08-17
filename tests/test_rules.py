"""Task 7 — pravidla nad entitami: pevný bod, derived_from + rule, zamítnutí se hlásí; dialog H."""
from cb6.dialog import Session
from cb6.oracle import RecordedOracle

O = RecordedOracle("tests/data/parses.json")


def _labels(s: Session, v) -> set[str]:
    return {s.memory.node(t).label() for t, _ in v.fillers if not t.startswith("count:")}


def test_retez_pravidel_odvodi_a_nese_derivaci():
    s = Session(oracle=O)
    s.ingest("Karel přijde na oslavu, pokud přijde Jana.\nJana přijde, pokud přijde Petr.", "h")
    assert s.say("Přijde Karel?").verdict.value == "NEVÍM"          # I‑8: podmínka není tvrzení
    s.say("Petr přijde.")
    a = s.say("Přijde Karel?")
    assert a.verdict.value == "ANO" and a.verdict.proofs[0].grade == "derived"
    d = [st for st in s.memory.knowledge() if st.grade == "derived"]
    assert len(d) == 2 and all(st.rule and st.derived_from for st in d)


def test_negovana_podminka_a_koordinace_dusledku():
    s = Session(oracle=O)
    s.ingest("Petr a Karel přijdou, když nepřijde Marie.\nMarie nepřijde.", "h")
    v = s.say("Kdo přijde?").verdict
    assert _labels(s, v) == {"Petr", "Karel"}


def test_zamitnuti_se_hlasi_ne_mlci():
    s = Session(oracle=O)
    s.ingest("Petr nebo Jana přijde.", "h")
    a = s.say("Přijde Petr?")
    assert a.verdict.value == "NEVÍM"
    assert any("interpretaci neurčuje" in n for n in a.verdict.notes)
    assert "neurčuje" in a.text


def test_odvolani_faktu_odvola_dusledek():
    s = Session(oracle=O)
    s.ingest("Jana přijde, pokud přijde Petr.", "h")
    a = s.say("Petr přijde.")
    sid = a.statements[0]
    assert s.say("Přijde Jana?").verdict.value == "ANO"
    s.say(f"!zapomeň {sid}")
    assert s.say("Přijde Jana?").verdict.value == "NEVÍM"


def test_dialog_h_oslava_a_replay():
    s = Session(oracle=O)
    s.ingest("Karel přijde na oslavu, pokud přijde Jana.\nJana přijde, pokud přijde Petr.\nPetr a Karel přijdou, když nepřijde Marie.\nMarie nepřijde.", "h")
    v = s.say("Kdo přijde?").verdict
    assert _labels(s, v) == {"Petr", "Karel", "Jana"}
    # přísně: „na oslavu“ text říká jen o Karlovi (I‑8 — nedomýšlíme)
    v2 = s.say("Kdo přijde na oslavu?").verdict
    assert _labels(s, v2) == {"Karel"}
    j = s.journal_json()
    s2 = Session.replay(j, O)
    assert s2.memory.program() == s.memory.program()
