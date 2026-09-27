"""Task 10 — akceptační dialog G: encyklopedický text, koreference, sylogismus, negace,
introspekce grafu, replay. Co padá, je NÁLEZ (xfail s odkazem), ne důvod měnit test."""
import pytest

from cb6.dialog import Session
from cb6.oracle import RecordedOracle

O = RecordedOracle("tests/data/parses.json")
TEXT = ("Karel Čapek (9. ledna 1890 Malé Svatoňovice – 25. prosince 1938 Praha) byl český spisovatel, novinář a dramatik.\n"
        "Narodil se v rodině lékaře.\nStudoval filozofii v Praze, Berlíně a Paříži.\nJeho bratr Josef Čapek byl malíř.\n"
        "V roce 1920 napsal drama R.U.R.\nČapek pracoval v Lidových novinách.\nNebyl nikdy členem žádné politické strany.")


def _labels(s, v):
    return {s.memory.node(t).label() for t, _ in v.fillers if not t.startswith("count:")}


@pytest.fixture()
def sess():
    s = Session(oracle=O)
    rep = s.ingest(TEXT, "g")
    assert all(r.get("statements") for r in rep)          # I‑1: každá věta zapsána
    return s


def test_kdo_byl(sess):
    v = sess.say("Kdo byl Karel Čapek?").verdict
    labels = {l.split("[")[0].split(" (")[0].strip() for l in _labels(sess, v)}
    assert {"spisovatel", "novinář", "dramatik"} <= labels


def test_kde_se_narodil_ze_zavorky(sess):
    v = sess.say("Kde se narodil Karel Čapek?").verdict
    assert any("Svatoňovice" in l for l in _labels(sess, v))
    assert any("životopisná závorka" in d for p in [p for _, p in v.fillers] for d in p.defaults)


def test_kde_studoval_prodrop_pres_registr(sess):
    v = sess.say("Kde studoval?").verdict
    assert {"Praha", "Berlín", "Paříž"} <= _labels(sess, v)
    assert any("koref" in d for _, p in v.fillers for d in p.defaults)


@pytest.mark.xfail(reason="NÁLEZ G‑1: v otázce „Kdy napsal R.U.R.?“ čte parser R.U.R. jako podmět (kdo), ne předmět; mez čtení otázek s pro‑dropem + PROPN předmětem", strict=True)
def test_kdy_napsal_rur(sess):
    v = sess.say("Kdy napsal R.U.R.?").verdict
    assert any("1920" in l for l in _labels(sess, v))


def test_byl_malir_je_nevim_ne_ano(sess):
    assert sess.say("Byl Čapek malíř?").verdict.value == "NEVÍM"     # malíř je Josef, holé „Čapek“ sedí na oba


def test_g3_pristavek_je_vztah_ne_slepene_jmeno(sess):
    """NÁLEZ G‑3 opraven (27. 9. 2026, krok 3): „Jeho bratr Josef Čapek“ dřív
    slepilo přístavek do jednoho jména skupiny („bratr Josef Čapek“) — teď je
    Josef Čapek SAMOSTATNÁ entita (⊆ bratr, „malíř“ visí na něm, ne na
    Karlovi) a vzniká skutečný vztahový výrok `bratr(kdo=Josef Čapek,
    čí=Karel Čapek)`, ne jen typing."""
    m = sess.memory
    josef = next(n for n in m.nodes.values() if n.kind == "entity" and "Josef Čapek" in n.names)
    karel = next(n for n in m.nodes.values() if n.kind == "entity" and n.names and n.names[0] == "Karel Čapek")
    assert josef.id != karel.id
    bratr = next(st for st in m.statements.values() if st.pred == "bratr")
    assert bratr.claim == "SAFE"
    assert bratr.role("kdo") is not None and bratr.role("kdo").terms == [josef.id]  # type: ignore[union-attr]
    assert bratr.role("čí") is not None and bratr.role("čí").terms == [karel.id]  # type: ignore[union-attr]
    malir = next(st for st in m.statements.values() if st.pred == "být" and any(
        m.nodes[c].lemma == "malíř" for r in st.roles if r.name == "co" for c in r.terms))
    assert malir.role("kdo") is not None and malir.role("kdo").terms == [josef.id]  # type: ignore[union-attr]


def test_sylogismus_pres_dialog(sess):
    assert sess.say("Byl Čapek člověk?").verdict.value == "NEVÍM"
    sess.say("Spisovatel je člověk.")
    a = sess.say("Byl Čapek člověk?")
    assert a.verdict.value == "ANO" and a.verdict.proofs[0].grade in ("derived", "said")


def test_negace_zadny_clen(sess):
    assert sess.say("Byl Čapek členem nějaké strany?").verdict.value == "NE"


@pytest.mark.xfail(reason="NÁLEZ G‑2: „Čapek se narodil v Praze.“ po Svatoňovicích nehlásí konflikt — otevřený svět nezná funkční role (narodit_se.kde je jedno místo); kandidát na měřený tah: funkční role jako data", strict=True)
def test_konflikt_narozeni(sess):
    a = sess.say("Čapek se narodil v Praze.")
    assert a.conflict is not None


def test_ukaz_a_otevrene_a_replay(sess):
    sid = [x for x in sess.memory.knowledge() if x.pred == "studovat"][0].id
    out = sess.say(f"!ukaž {sid}").text
    assert "source" in out and "koref" in out
    assert "role_name" in sess.say("!otevřené").text          # „v rodině lékaře“ / „v Lidových novinách“
    j = sess.journal_json()
    s2 = Session.replay(j, O)
    assert s2.memory.program() == sess.memory.program()
