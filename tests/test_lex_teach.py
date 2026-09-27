"""Věta učí lexikon z promluvy, ne z příkazu `!uč` (J. 27. 9. 2026: „vše by
mělo být z kontextu diskuse, bez příkazu“). Rozbor věty „Bydlet je synonymum
žít.“ tu je RUČNĚ sestavený podle univerzálních závislostí (ověřeno, ne
odhad) — tahle konstrukce (infinitiv jako podmět kopuly) není v žádném
zaznamenaném korpusu (`tests/data/parses.json`) a dostupný parser v tomhle
sezení (spaCy `cs_core_news_sm`, náhrada za nedostupné UDPipe/LINDAT) na ní
měřitelně selhává (viz `mereni/HYPOTEZY.md` 2026-09-27: 16,9 % tokenů se liší
od skutečného UDPipe2 na existujícím korpusu) — proto rozbor po ruce, ne
z nespolehlivého výstupu.
"""

from cb6.dialog import Session
from cb6.lexicon import Lexicon
from cb6.memory import Memory
from cb6.oracle import Parse, Token


def _parse(text: str, tokens: list[tuple[str, str, str, int, str, tuple[tuple[str, str], ...]]]) -> Parse:
    """`tokens`: (form, lemma, upos, head, deprel, feats) — 1-indexed pořadím v seznamu."""
    toks = tuple(Token(i + 1, form, lemma, upos, head, deprel, feats)
                 for i, (form, lemma, upos, head, deprel, feats) in enumerate(tokens))
    return Parse(text, toks, "ruční UD (ověřeno) — test, ne UDPipe/spaCy")


BYDLET_SYNONYMUM_ZIT = _parse("Bydlet je synonymum žít.", [
    ("Bydlet", "bydlet", "VERB", 3, "nsubj", (("Aspect", "Imp"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
    ("je", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"))),
    ("synonymum", "synonymum", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Neut"), ("Number", "Sing"))),
    ("žít", "žít", "VERB", 3, "xcomp", (("Aspect", "Imp"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
    (".", ".", "PUNCT", 3, "punct", ()),
])

VYDAT_NEZNAMENA = _parse("Vydat není synonymum napsat.", [
    ("Vydat", "vydat", "VERB", 3, "nsubj", (("Aspect", "Perf"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
    ("není", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"), ("Polarity", "Neg"))),
    ("synonymum", "synonymum", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Neut"), ("Number", "Sing"))),
    ("napsat", "napsat", "VERB", 3, "xcomp", (("Aspect", "Perf"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
    (".", ".", "PUNCT", 3, "punct", ()),
])


class _FixedOracle:
    """Vrací vždy tentýž ruční rozbor — nahrazuje živé orákulum jen pro tenhle test."""

    def __init__(self, parse: Parse) -> None:
        self._parse = parse

    def parse(self, _text: str) -> Parse:
        return self._parse


def test_veta_uci_lexikon_bez_prikazu() -> None:
    m = Memory()
    s = Session(m, _FixedOracle(BYDLET_SYNONYMUM_ZIT))  # type: ignore[arg-type]
    reps = s.ingest("Bydlet je synonymum žít.", "d")
    assert len(reps) == 1
    lx = Lexicon.for_memory(m)
    assert lx.match("žít", "bydlet") is not None and lx.match("bydlet", "žít") is not None  # `same` obousměrně
    said = [l for l in m.links.values() if l.authority == "read"]
    assert len(said) == 1 and said[0].args == ("bydlet", "žít") and said[0].strength == "same"
    # výrok je zapsaný (source/sentence pro I-12), ale NENÍ tvrzení o světě
    st = next(st for st in m.statements.values() if st.kind == "lex_teach")
    assert st.mood == "pattern" and st not in list(m.knowledge())


def test_zaporna_veta_se_nenauci_nic() -> None:
    """„Vydat není synonymum napsat.“ — záporná: raději nic než obráceně špatně."""
    m = Memory()
    s = Session(m, _FixedOracle(VYDAT_NEZNAMENA))  # type: ignore[arg-type]
    s.ingest("Vydat není synonymum napsat.", "d")
    assert not [l for l in m.links.values() if l.authority == "read"]
    assert Lexicon.for_memory(m).match("napsat", "vydat") is None
