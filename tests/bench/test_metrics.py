"""Task 3 — metriky benche nad ručně postavenou pamětí (bez UDPipe)."""
from cb6.memory import Memory, Statement, Role, Provenance

from bench.metrics import ingest_metrics, qa_metrics, reach


def _mem():
    m = Memory()
    m.ensure_document("d")
    z1 = m.new_sentence("d", 1, "Alois Jirásek se narodil v Hronově.")
    z2 = m.new_sentence("d", 2, "Zemřel v Praze.")
    e = m.new_node("entity", "Jirásek", names=["Alois Jirásek"])
    p = m.new_node("place", "Hronov", names=["Hronov"])
    m.attach(Statement("", "narodit_se", "verb", sentence=z1.id, prov=Provenance("d", 1), roles=[Role("kdo", [e.id]), Role("kde", [p.id])]))
    m.attach(Statement("", "zemřít", "verb", sentence=z2.id, prov=Provenance("d", 2), roles=[Role("kdo", [e.id])], claim="HYPOTHESIS"))
    m.attach(Statement("", "žít", "verb", sentence=z2.id, prov=Provenance("d", 2), claim="REJECTED", reason="disjunkce"))
    m.add_open("reference", "∅", "Kdo?", "s0002")
    return m


def test_ingest_metrics_yield_a_statusy():
    m = _mem()
    r = ingest_metrics(m, n_words=100, reports=[
        {"statements": ["s0001"], "residue": [("prý", "advmod")], "open": []},
        {"statements": ["s0002", "s0003"], "residue": [], "open": ["o0001"]},
    ])
    assert r["yield"] == 10.0
    assert r["claims"] == {"SAFE": 1, "HYPOTHESIS": 1, "REJECTED": 1}
    assert r["open_per_sent"] == 0.5 and r["written_pct"] == 100.0
    assert r["pct_with_place"] == 100.0


def test_reach_pocita_vzdalenost_od_posledni_plne_zminky():
    m = _mem()
    sents = [n for n in m.nodes.values() if n.kind == "sentence"]
    assert reach(m, 2, ["Alois", "Jirásek"], sents) == 1
    assert reach(m, 1, ["Alois", "Jirásek"], sents) == 0
    assert reach(m, 2, ["Božena", "Němcová"], sents) is None


def test_qa_metrics_pasma_a_kuratorovane():
    r = qa_metrics([
        {"ok": True, "reach": 0, "coverage": True, "sada": "etalon", "curated": True},
        {"ok": False, "reach": 5, "coverage": True, "why": "bez výroku", "sada": "otazky", "curated": False},
        {"ok": False, "reach": None, "coverage": False, "sada": "conbond", "curated": True},
    ])
    assert r["coverage"] == 2 and r["hits"] == 1
    assert r["by_reach"]["0"] == [1, 1] and r["by_reach"]["4-10"] == [0, 1] and r["by_reach"]["?"] == [0, 1]
    assert r["curated_questions"] == 2 and r["curated_hits"] == 1
    assert r["by_sada"]["otazky"] == [0, 1]
