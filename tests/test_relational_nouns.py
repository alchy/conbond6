"""Krok 3 znalostních vazeb (`2026-08-17-znalostni-vazby-design.md`):
vztahová substantiva (`cb6/lang/cs.json relational_nouns`) — genitivní
doplněk vztahového jména („manžel **dcery**“) je určující argument, ne
vedlejší vztah k zahození (`cb6/read.py Reader._term`, `cb6/ground.py
ground_predication`).

Rozbory tu jsou RUČNĚ sestavené podle univerzálních závislostí (ověřeno,
ne odhad) — stejný důvod jako `tests/test_lex_teach.py`: konstrukce není
(v tomhle sezení) ověřitelná spolehlivým parserem nad živým textem.

Nález, který tenhle krok řeší (`mereni/HYPOTEZY.md` 27. 9. 2026,
`vztahy_příbuzenské.txt`): bez tohohle rozlišení byl hlavní výrok „zeť ⊆
manžel“ SAFE, zatímco sesterský výrok nesoucí „čí manžel“ (dcery) byl
REJECTED jako „vedlejší vztah bez sémantiky“ — podstatná část věty se
tak ztrácela, i když verdikt vypadal jistě.
"""

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import Parse, Token


def _parse(text: str, tokens: list[tuple[str, str, str, int, str, tuple[tuple[str, str], ...]]]) -> Parse:
    """`tokens`: (form, lemma, upos, head, deprel, feats) — 1-indexed pořadím v seznamu."""
    toks = tuple(Token(i + 1, form, lemma, upos, head, deprel, feats)
                 for i, (form, lemma, upos, head, deprel, feats) in enumerate(tokens))
    return Parse(text, toks, "ruční UD (ověřeno) — test, ne UDPipe/spaCy")


ZET_MANZEL_DCERY = _parse("Zeť je manžel dcery.", [
    ("Zeť", "zeť", "NOUN", 3, "nsubj", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    ("je", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"))),
    ("manžel", "manžel", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    ("dcery", "dcera", "NOUN", 3, "nmod", (("Case", "Gen"), ("Gender", "Fem"), ("Number", "Sing"))),
    (".", ".", "PUNCT", 3, "punct", ()),
])

TCHAN_OTEC_DISJUNKCE = _parse("Tchán je otec manžela nebo manželky.", [
    ("Tchán", "tchán", "NOUN", 3, "nsubj", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    ("je", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"))),
    ("otec", "otec", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    ("manžela", "manžel", "NOUN", 3, "nmod", (("Case", "Gen"), ("Gender", "Masc"), ("Number", "Sing"))),
    ("nebo", "nebo", "CCONJ", 6, "cc", ()),
    ("manželky", "manželka", "NOUN", 4, "conj", (("Case", "Gen"), ("Gender", "Fem"), ("Number", "Sing"))),
    (".", ".", "PUNCT", 3, "punct", ()),
])


class _FixedOracle:
    """Vrací vždy tentýž ruční rozbor — nahrazuje živé orákulum jen pro tenhle test."""

    def __init__(self, parse: Parse) -> None:
        self._parse = parse

    def parse(self, _text: str) -> Parse:
        return self._parse


def test_genitiv_vztahoveho_substantiva_je_role_ci() -> None:
    """„Zeť je manžel dcery.“ — genitiv „dcery“ je role `čí` na TÉMŽ výroku,
    ne samostatná (dřív REJECTED) vedlejší predikace `nmod:Gen`."""
    m = Memory()
    s = Session(m, _FixedOracle(ZET_MANZEL_DCERY))  # type: ignore[arg-type]
    s.ingest("Zeť je manžel dcery.", "d")
    # žádná sesterská (dřív REJECTED) predikace z genitivu — jen jeden výrok
    assert len(m.statements) == 1
    st = next(iter(m.statements.values()))
    assert st.claim == "SAFE" and st.kernel == "subset"
    ci = st.role("čí")
    assert ci is not None and ci.terms
    assert m.nodes[ci.terms[0]].lemma == "dcera"


def test_koordinovany_genitiv_zustava_vedlejsi_a_disjunkce_zamitne() -> None:
    """Souřadění pod genitivem („manžela NEBO manželky“) se nepřebírá jako
    `čí` (ztratilo by se, který ze dvou) — zůstává vedlejší predikací, a
    disjunkce ji (i hlavní výrok) zamítne beze změny (known limitation)."""
    m = Memory()
    s = Session(m, _FixedOracle(TCHAN_OTEC_DISJUNKCE))  # type: ignore[arg-type]
    s.ingest("Tchán je otec manžela nebo manželky.", "d")
    assert all(st.claim == "REJECTED" and st.reason == "disjunkce bez prostoru modelů" for st in m.statements.values())
    assert not any(st.role("čí") for st in m.statements.values())
