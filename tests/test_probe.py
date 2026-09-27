"""`bench.probe._token_labels` — mapování token → jméno role z `read.py`
(bez NN, bez `sklearn`; ty se testují jen kouřovou zkouškou v `build_examples`
níž, `sklearn`/`spacy` ať test nevyžaduje). Rozbor ruční (stejný důvod jako
`tests/test_lex_teach.py`)."""

from bench.probe import _token_labels
from cb6.oracle import Parse, Token
from cb6.read import read

ZET_MANZEL_DCERY = Parse("Zeť je manžel dcery.", (
    Token(1, "Zeť", "zeť", "NOUN", 3, "nsubj", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    Token(2, "je", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"))),
    Token(3, "manžel", "manžel", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
    Token(4, "dcery", "dcera", "NOUN", 3, "nmod", (("Case", "Gen"), ("Gender", "Fem"), ("Number", "Sing"))),
    Token(5, ".", ".", "PUNCT", 3, "punct", ()),
), "ruční UD (ověřeno) — test")


def test_token_labels_zahrnuje_ci_z_genitivu() -> None:
    reading = read(ZET_MANZEL_DCERY, "assert", learned_roles={})
    labels = _token_labels(reading.main)
    assert labels[1] == "kdo"   # „Zeť“ — podmět
    assert labels[3] == "co"    # „manžel“ — predikátový nominál
    assert labels[4] == "čí"    # „dcery“ — genitivní argument (krok 3), ne „co“


def test_token_bez_role_neni_v_mape() -> None:
    reading = read(ZET_MANZEL_DCERY, "assert", learned_roles={})
    labels = _token_labels(reading.main)
    assert 2 not in labels and 5 not in labels  # spona a tečka nesou žádnou roli
