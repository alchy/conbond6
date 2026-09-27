"""Fragmentový úkol (bez UDPipe — cloudové sezení 27. 9. 2026, viz HYPOTEZY):
operátor `překryv` (spec krok 2) na ručně sestavené paměti. Věty samy nejsou
čtené parserem — jsou to přímo zapsané výroky (`Statement`), poctivě označené
jako `grade="said"`/`autorita testu`; smysl testu je ověřit, že `chronos.overlap`
+ `Lexicon.overlap_rules_by_target` + `Evaluator.overlap_verdict` spolu dají
správnou odpověď a že je doložitelná jen z exportu grafu (I‑12), ne že čtení
věty z textu funguje (to čeká na UDPipe).
"""

from bench.graphcheck import check_answer, check_graph
from cb6.chronos import TimeSpec
from cb6.logic import evaluate
from cb6.memory import Memory, Provenance, Role, Statement


def _zit(m: Memory, doc: str, no: int, jmeno: list[str], od: int, do: int) -> None:
    """Zapiš „X žil(a) <od>–<do>.“ přímo jako výrok — fragment bez UDPipe."""
    sent = m.new_sentence(doc, no, f"{' '.join(jmeno)} žil {od}–{do}.")
    osoba, _ = m.ensure_entity(jmeno, doc=doc)
    cas = m.ensure_time(TimeSpec("interval", f"{od}–{do}", (od, 0, 0), (do, 0, 0)))
    m.note_mention(sent.id, osoba.id, "kdo", " ".join(jmeno))
    m.note_mention(sent.id, cas.id, "kdy", cas.label())
    st = Statement("", "žít", "verb", roles=[Role("kdo", [osoba.id]), Role("kdy", [cas.id])],
                   grade="said", mood="assert", claim="SAFE", sentence=sent.id,
                   prov=Provenance(doc, no, f"{' '.join(jmeno)} žil {od}–{do}.", no, "test"))
    m.attach(st)


def _mohli_se_potkat(a: str, b: str) -> Statement:
    return Statement("", "potkat_se", "verb", modality="možnost", mood="question", roles=[Role("kdo", [a, b])])


def test_prekryvajici_se_zivoty_daji_ano() -> None:
    m = Memory()
    _zit(m, "d", 1, ["Alois", "Jirásek"], 1851, 1930)
    _zit(m, "d", 2, ["Karel", "Čapek"], 1890, 1938)
    jirasek = m.find_entity(["alois", "jirásek"])[0]
    capek = m.find_entity(["karel", "čapek"])[0]
    v = evaluate(m, _mohli_se_potkat(jirasek.id, capek.id))
    assert v.value == "ANO" and v.proofs[0].grade == "derived"
    assert any(k == "overlap" for k, _, _ in v.proofs[0].hard) and any(k == "lex" for k, _, _ in v.proofs[0].hard)
    g = m.graph()
    assert not check_graph(g)
    assert not check_answer(g, list(v.proofs[0].statements), list(v.proofs[0].hard))
    # bez materializace řádku by krok `lex` nebyl doložený (I-12)
    lex_nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "vazba" and d.get("op") == "překryv"]
    assert lex_nodes and g.nodes[lex_nodes[0]]["modalita"] == "možnost"
    g.remove_node(lex_nodes[0])
    assert [x.check for x in check_answer(g, list(v.proofs[0].statements), list(v.proofs[0].hard))] == ["rekonstrukce"]


def test_neprekryvajici_se_zivoty_daji_ne_silne() -> None:
    """Spec § 2: „Nepřekryv ⇒ NE je silné a správné.“"""
    m = Memory()
    _zit(m, "d", 1, ["Alois", "Jirásek"], 1851, 1930)
    _zit(m, "d", 2, ["Pozdější", "Osoba"], 1935, 1990)
    jirasek = m.find_entity(["alois", "jirásek"])[0]
    pozdejsi = m.find_entity(["pozdější", "osoba"])[0]
    v = evaluate(m, _mohli_se_potkat(jirasek.id, pozdejsi.id))
    assert v.value == "NE"
    assert any(k == "no_overlap" for k, _, _ in v.counter[0].hard)
    g = m.graph()
    assert not check_graph(g)
    assert not check_answer(g, list(v.counter[0].statements), list(v.counter[0].hard))


def test_faktickou_otazku_bez_modality_nechavaji_nevim() -> None:
    """„Potkali se?“ (bez modality) NENÍ totéž co „Mohli se potkat?“ — overlap
    dvou nezávislých životů není důkaz skutečného setkání (spec § 2)."""
    m = Memory()
    _zit(m, "d", 1, ["Alois", "Jirásek"], 1851, 1930)
    _zit(m, "d", 2, ["Karel", "Čapek"], 1890, 1938)
    jirasek = m.find_entity(["alois", "jirásek"])[0]
    capek = m.find_entity(["karel", "čapek"])[0]
    q = Statement("", "potkat_se", "verb", mood="question", roles=[Role("kdo", [jirasek.id, capek.id])])
    assert evaluate(m, q).value == "NEVÍM"


def test_chybejici_udaj_o_jednom_dava_nevim() -> None:
    m = Memory()
    _zit(m, "d", 1, ["Alois", "Jirásek"], 1851, 1930)
    jirasek = m.find_entity(["alois", "jirásek"])[0]
    neznamy, _ = m.ensure_entity(["neznámý", "člověk"], doc="d")
    assert evaluate(m, _mohli_se_potkat(jirasek.id, neznamy.id)).value == "NEVÍM"
