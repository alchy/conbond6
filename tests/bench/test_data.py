"""Task 3 — načtení sad a otisk dat (bez sítě: jen kontrola tvaru; korpus může chybět)."""
from bench.data import Doc, Question, data_fingerprint, topic_from_name


def test_topic_a_otisk():
    assert topic_from_name("alois_jirásek") == "Alois Jirásek"
    a = Doc("a", "wiki", "Text.", [Question("Kde?", ["Praha"], "etalon")])
    b = Doc("a", "wiki", "Text.", [Question("Kde?", ["Brno"], "etalon")])
    assert data_fingerprint([a]) != data_fingerprint([b])
    assert a.words() == 1
