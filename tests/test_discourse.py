"""Task 8 — registr referentů jako projekce grafu, hypotézy koreference, segmenty."""
from cb6.dialog import Session
from cb6.discourse import Registry
from cb6.oracle import RecordedOracle

O = RecordedOracle("tests/data/parses.json")


def test_jeden_kandidat_je_safe_s_defaultem_a_mention_hranou():
    s = Session(oracle=O)
    s.ingest("Alois Jirásek se narodil v Hronově.\nZemřel v Praze.", "d")
    st = [x for x in s.memory.knowledge() if x.pred == "zemřít"][0]
    assert any("koref: registr" in d for d in st.defaults)
    g = s.memory.graph()
    assert any(d["type"] == "mention" and d["role"] == "kdo" for _, _, d in g.edges(data=True))
    reg = Registry(s.memory)
    c = reg.candidates(gender="Masc", number="Sing", segment=None)
    assert c and c[0].node.label() == "Alois Jirásek"


def test_dva_kandidati_daji_jadro_hypotezy_a_open():
    s = Session(oracle=O)
    s.ingest("Karel a Josef Čapkovi byli bratři.\nOn namaloval obraz.", "d")
    m = s.memory
    core = [x for x in m.knowledge() if x.pred == "namalovat"]
    hyp = [x for x in m.by_claim("HYPOTHESIS") if x.pred == "namalovat"]
    assert len(core) == 1 and core[0].role("kdo").terms == []
    assert len(hyp) == 2 and all(core[0].id in h.alternatives for h in hyp)
    assert any(o.kind == "reference" for o in m.open_items())
    assert s.say("Namaloval Josef Čapek obraz?").verdict.value == "NEVÍM"     # I‑3
    a = s.say("Kdo namaloval obraz?")
    assert a.verdict.value == "NEVÍM" or not a.verdict.fillers
    assert any("hypotéza" in n for n in a.verdict.notes)


def test_rod_rozhodne_mezi_kandidaty():
    s = Session(oracle=O)
    s.ingest("Božena Němcová napsala Babičku.\nAlois Jirásek se narodil v Hronově.\nOna zemřela v Praze.", "d")
    st = [x for x in s.memory.knowledge() if x.pred == "zemřít"][0]
    assert s.memory.node(st.role("kdo").terms[0]).label() == "Božena Němcová"


def test_segmenty_v_grafu():
    s = Session(oracle=O)
    s.ingest("Život\nAlois Jirásek se narodil v Hronově.\n\nDílo\nZemřel v Praze.", "d")
    g = s.memory.graph()
    segs = [n for n, d in g.nodes(data=True) if d["kind"] == "segment"]
    assert len(segs) == 2
    types = {(u, v, d["type"]) for u, v, d in g.edges(data=True)}
    sent = [n for n, d in g.nodes(data=True) if d["kind"] == "sentence"]
    assert all(any((z, sg, "part_of") in types for sg in segs) for z in sent)
