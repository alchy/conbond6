"""Task 9 — !ukaž, !hypotéza, !statusy, doložky statusu."""
from cb6.dialog import Session
from cb6.oracle import RecordedOracle

O = RecordedOracle("tests/data/parses.json")


def test_ukaz_vypise_zdroj_status_defaulty_a_okoli():
    s = Session(oracle=O)
    s.ingest("Alois Jirásek se narodil v Hronově.\nZemřel v Praze.", "d")
    sid = [x for x in s.memory.knowledge() if x.pred == "zemřít"][0].id
    out = s.say(f"!ukaž {sid}").text
    for needle in ("SAFE", "přečteno z textu", "Zemřel v Praze.", "koref: registr", "role:kdo", "source"):
        assert needle in out, needle


def test_hypoteza_potvrd_a_statusy():
    s = Session(oracle=O)
    s.ingest("Karel a Josef Čapkovi byli bratři.\nOn namaloval obraz.", "d")
    hyp = [x for x in s.memory.by_claim("HYPOTHESIS") if x.pred == "namalovat"]
    josef = [h for h in hyp if "Josef" in s.memory.render_short(h)][0]
    other = [h for h in hyp if h.id != josef.id][0]
    out = s.say(f"!hypotéza {josef.id} potvrď").text
    assert "SAFE" in out
    assert s.memory.statements[josef.id].claim == "SAFE"
    assert s.memory.statements[other.id].claim == "REJECTED"
    assert s.say("Namaloval Josef obraz?").verdict.value == "ANO"
    st = s.say("!statusy").text
    assert "HYPOTHESIS" in st and "REJECTED" in st


def test_hypoteza_v_propadu_je_oznacena():
    s = Session(oracle=O)
    s.ingest("Karel a Josef Čapkovi byli bratři.\nOn namaloval obraz.", "d")
    a = s.say("Kdo namaloval obraz?")
    assert not a.verdict.fillers
    assert "hypotéza" in a.text.lower()


def test_dolozka_statusu_v_renderu():
    s = Session(oracle=O)
    s.ingest("Petr řekl, že Marie přijde.", "d")
    a = s.say("Přijde Marie?")
    assert a.verdict.value == "NEVÍM"
    assert "obsah promluvy" in a.text or "hypotéza" in a.text.lower() or "vím" in a.text
