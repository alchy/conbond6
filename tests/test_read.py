"""Čtení: predikace, role, negace, modalita, kopula, fragment, závorka, zbytek.

Každý test navíc drží pojistku „nic se neztrácí“: každý token má právě
jedno místo v `placement()`.
"""

from pathlib import Path

import pytest

from cb6.oracle import RecordedOracle
from cb6.read import Predication, Reading, read

DATA = Path(__file__).parent / "data" / "parses.json"
SENTENCES = Path(__file__).parent / "data" / "sentences.txt"


@pytest.fixture(scope="module")
def oracle() -> RecordedOracle:
    return RecordedOracle(DATA)


def R(oracle: RecordedOracle, text: str) -> Reading:
    r = read(oracle.parse(text))
    placed = r.placement()
    missing = [t.form for t in r.parse.tokens if t.index not in placed]
    assert not missing, f"tokeny bez místa: {missing}"
    return r


def terms(p: Predication, role: str) -> list[str]:
    r = p.role(role)
    assert r is not None, f"role {role} chybí v {p}"
    return [t.label() for t in r.terms]


def test_simple_verb_with_place(oracle: RecordedOracle) -> None:
    r = R(oracle, "Petr bydlí v Praze.")
    m = r.main
    assert m.pred == "bydlet" and m.kind == "verb" and not m.neg and m.mood == "assert"
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].kind == "entity" and kdo.terms[0].quant == "·"
    kde = m.role("kde")
    assert kde and kde.surface == "v+Loc" and kde.authority == "default" and kde.terms[0].kind == "place"
    assert r.residue == []


def test_reflexive_and_nmod_secondary(oracle: RecordedOracle) -> None:
    r = R(oracle, "Alois Jirásek se narodil ve východočeském Hronově u Náchoda.")
    m = r.main
    assert m.pred == "narodit_se"
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].name_lemmas == ("Alois", "Jirásek") and kdo.terms[0].name_tokens == (1, 2)
    kde = m.role("kde")
    assert kde and kde.terms[0].lemma == "Hronov" and kde.terms[0].attrs == ("východočeský",)
    assert r.residue == []
    assert any(s.kind == "nmod" and s.pred == "nmod:u+Gen" for s in m.secondary)


def test_negation_and_generic_quantifier(oracle: RecordedOracle) -> None:
    m = R(oracle, "Tučňák nelétá.").main
    assert m.pred == "létat" and m.neg
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].quant == "∀" and kdo.terms[0].quant_authority.startswith("default")
    assert any("generický" in d for d in m.defaults)


def test_modality_advcl_and_negated_aux(oracle: RecordedOracle) -> None:
    r = R(oracle, "Chov domácích zvířat může mít negativní dopad na jejich zdraví, pokud nejsou splněny určité požadavky.")
    m = r.main
    assert m.pred == "mít" and m.modality == "možnost"
    assert terms(m, "kdo") == ["chov"]
    co = m.role("co")
    assert co and co.terms[0].lemma == "dopad" and co.terms[0].attrs == ("negativní",)
    adv = m.role("advcl:pokud")
    assert adv and adv.nested is not None and adv.nested.pred == "splněný" and adv.nested.neg
    assert terms(adv.nested, "co") == ["požadavek"]
    assert r.residue == []
    kinds = {s.pred for s in m.secondary}
    assert "nmod:Gen" in kinds and "nmod:na+Acc" in kinds


def test_time_name_and_direction(oracle: RecordedOracle) -> None:
    m = R(oracle, "Petr jel v pondělí do Prahy.").main
    kdy = m.role("kdy")
    assert kdy and kdy.terms[0].kind == "time" and kdy.terms[0].time is not None and kdy.terms[0].time.label == "pondělí"
    assert terms(m, "kam") == ["Praha"]


def test_count(oracle: RecordedOracle) -> None:
    m = R(oracle, "Dospělý pes má 42 zubů.").main
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].lemma == "pes" and kdo.terms[0].attrs == ("dospělý",) and kdo.terms[0].quant == "∀"
    co = m.role("co")
    assert co and co.terms[0].lemma == "zub" and co.terms[0].count == 42 and co.terms[0].quant == "∃"


def test_prodrop_and_coordinated_places(oracle: RecordedOracle) -> None:
    r = R(oracle, "Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.")
    m = r.main
    assert m.pred == "pracovat"
    kdo = m.role("kdo")
    assert kdo and kdo.authority == "prodrop" and kdo.terms[0].kind == "pron" and kdo.terms[0].gender == "Masc"
    assert set(terms(m, "kde")) == {"gymnázium", "Litomyšl", "Praha"}
    assert terms(m, "jako") == ["učitel"]
    assert m.role("jak_dlouho") is not None
    assert r.residue == []


def test_neosobni_se_v_pritomnem_case_nedostane_kdo() -> None:
    """„Jedná se o pomalý pohyb.“ (`bench/graf_audit.py`, 27. 9. 2026, nález
    z reálného korpusu wiki „sopka“): sloveso s `expl:pv` (`_lemma_with_refl`
    dá `pred=jednat_se`) je neosobní — žádný `kdo` nemá existovat, natož se
    doplňovat na téma dokumentu (`ground.py._resolve_pron`). Rod v přítomném
    čase čeština neznačí vůbec (`Gender` je `None`, ne `Neut`) — `_prodrop`
    dřív tenhle případ (na rozdíl od minulého času, „stalo se“) nechytil a
    `kdo` doplnil. Ruční UD (ověřeno křížově proti `SpacyOracle` — základní
    morfologie, ne sémantický odhad), ne živý UDPipe."""
    from cb6.oracle import Parse, Token
    p = Parse("Jedná se o pomalý pohyb.", (
        Token(1, "Jedná", "jednat", "VERB", 0, "root", (("Aspect", "Imp"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"), ("Polarity", "Pos"), ("Tense", "Pres"), ("VerbForm", "Fin"), ("Voice", "Act"))),
        Token(2, "se", "se", "PRON", 1, "expl:pv", (("Case", "Acc"), ("PronType", "Prs"), ("Reflex", "Yes"), ("Variant", "Short"))),
        Token(3, "o", "o", "ADP", 5, "case", (("AdpType", "Prep"), ("Case", "Acc"))),
        Token(4, "pomalý", "pomalý", "ADJ", 5, "amod", (("Animacy", "Inan"), ("Case", "Acc"), ("Degree", "Pos"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"))),
        Token(5, "pohyb", "pohyb", "NOUN", 1, "obl:arg", (("Animacy", "Inan"), ("Case", "Acc"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(6, ".", ".", "PUNCT", 1, "punct", ()),
    ), "ruční UD (ověřeno křížově proti SpacyOracle) — test, ne živý UDPipe")
    m = read(p).main
    assert m.pred == "jednat_se"
    assert m.role("kdo") is None


def test_relational_noun_bez_privlastneni_da_entitu_ne_slepene_jmeno() -> None:
    """„Matka Božena Čapková sbírala…“ (živá ukázka 27. 9. 2026, J.): dřív
    `_relational_name` vyžadovalo přivlastnění („Jeho bratr…“), bez něj
    `_term` sloučilo „matka“+„Božena“+„Čapková“ do JEDNOHO jména (jako
    víceslovné jméno typu „Karel Čapek“) — Božena Čapková se tak nedala
    najít jako entita. Teď i bez přivlastnění vznikne entita `Božena
    Čapková ∈ matka` (typing z `cls`), jen vztahový výrok (`matka(kdo=…,
    čí=…)`) ne — ten čeká na odvození vlastníka z tématu dokumentu
    (`ground.py`), jiný, neměřený krok. Ruční UD (ověřeno křížově proti
    `SpacyOracle`), ne živý UDPipe."""
    from cb6.oracle import Parse, Token
    p = Parse("Matka Božena Čapková sbírala slovesný folklor.", (
        Token(1, "Matka", "matka", "NOUN", 4, "nsubj", (("Case", "Nom"), ("Gender", "Fem"), ("Number", "Sing"))),
        Token(2, "Božena", "Božena", "PROPN", 1, "flat", (("Case", "Nom"), ("Gender", "Fem"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(3, "Čapková", "Čapková", "PROPN", 1, "flat", (("Case", "Nom"), ("Gender", "Fem"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(4, "sbírala", "sbírat", "VERB", 0, "root", (("Aspect", "Imp"), ("Gender", "Fem,Neut"), ("Number", "Plur,Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        Token(5, "slovesný", "slovesný", "ADJ", 6, "amod", (("Animacy", "Inan"), ("Case", "Acc"), ("Degree", "Pos"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"))),
        Token(6, "folklor", "folklor", "NOUN", 4, "obj", (("Animacy", "Inan"), ("Case", "Acc"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(7, ".", ".", "PUNCT", 4, "punct", ()),
    ), "ruční UD (ověřeno křížově proti SpacyOracle) — test, ne živý UDPipe")
    m = read(p).main
    assert m.pred == "sbírat"
    kdo = m.role("kdo").terms[0]  # type: ignore[union-attr]
    assert kdo.kind == "entity" and kdo.name_lemmas == ("Božena", "Čapková") and kdo.cls == ("matka", ())
    assert kdo.possessor is None


def test_relational_gen_arg_koordinovany_popis_jedne_osoby() -> None:
    """„Byl mladším bratrem malíře a spisovatele Josefa Čapka.“ (živá ukázka
    27. 9. 2026): genitivní argument vztahového substantiva („manžel
    dcery“) se dřív u KOORDINACE vůbec nepřebíral (obrana proti „manžela
    NEBO manželky“ — dvě různé osoby) — Josef Čapek tak z výroku úplně
    zmizel. Teď se koordinace přebere, když jde o dva POPISY JEDNÉ osoby
    (jméno visí jen na jednom z konjunktů, spojka je slučovací): Josef
    Čapek je dohledatelný jako `rel_owner` role `co`. Zbytek beze změny
    (druhý konjunkt „malíře“ se jen zahodí jako popis — bohatší zpracování
    dvou tříd na jedné entitě je otevřený tah, ne dnešní oprava). Ruční UD
    (ověřeno křížově proti `SpacyOracle`), ne živý UDPipe."""
    from cb6.oracle import Parse, Token
    p = Parse("Byl mladším bratrem malíře a spisovatele Josefa Čapka.", (
        Token(1, "Byl", "být", "AUX", 3, "cop", (("Aspect", "Imp"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        Token(2, "mladším", "mladý", "ADJ", 3, "amod", (("Animacy", "Anim"), ("Case", "Ins"), ("Degree", "Pos"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"))),
        Token(3, "bratrem", "bratr", "NOUN", 0, "root", (("Animacy", "Anim"), ("Case", "Ins"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(4, "malíře", "malíř", "NOUN", 3, "nmod", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(5, "a", "a", "CCONJ", 6, "cc", ()),
        Token(6, "spisovatele", "spisovatel", "NOUN", 4, "conj", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(7, "Josefa", "Josef", "PROPN", 6, "flat", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(8, "Čapka", "Čapek", "PROPN", 6, "flat", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(9, ".", ".", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno křížově proti SpacyOracle) — test, ne živý UDPipe")
    r = read(p)
    m = r.main
    assert m.pred == "být"
    co = m.role("co").terms[0]  # type: ignore[union-attr]
    assert co.lemma == "bratr" and co.rel_owner is not None
    assert co.rel_owner.name_lemmas == ("spisovatel", "Josef", "Čapek")
    assert r.residue == []
    assert not [t.form for t in r.parse.tokens if t.index not in r.placement()]


def test_questions_have_holes(oracle: RecordedOracle) -> None:
    m = R(oracle, "Kde se narodil Alois Jirásek?").main
    assert m.mood == "question"
    kde = m.role("kde")
    assert kde and kde.wh and kde.wh_kind == "filler" and kde.terms == []
    m2 = R(oracle, "Kolik zubů má dospělý pes?").main
    co = m2.role("co")
    assert co and co.wh and co.wh_kind == "count" and co.terms[0].lemma == "zub"
    m3 = R(oracle, "Kdy se narodil Isaac Newton?").main
    assert m3.role("kdy") is not None and m3.role("kdy").wh  # type: ignore[union-attr]


def test_yes_no_question_keeps_all_roles(oracle: RecordedOracle) -> None:
    m = R(oracle, "Bydlí Petr v Brně?").main
    assert m.mood == "question" and terms(m, "kdo") == ["Petr"] and terms(m, "kde") == ["Brno"]


def test_case_ambiguity_subject(oracle: RecordedOracle) -> None:
    m = R(oracle, "Obsahuje citron vitamín C?").main
    assert terms(m, "kdo") == ["citron"] and terms(m, "co") == ["vitamín C"]
    assert any("dvojznačnost" in d for d in m.defaults)


# ---- kopula, fragment, závorka ----------------------------------------------


def test_copula_subset(oracle: RecordedOracle) -> None:
    m = R(oracle, "Jezevčík je pes.").main
    assert m.kind == "copula" and m.pred == "být" and m.kernel == "subset"
    assert terms(m, "kdo") == ["jezevčík"] and terms(m, "co") == ["pes"]
    assert m.role("kdo").terms[0].quant == "∀"  # type: ignore[union-attr]


def test_copula_question_with_nmod_wobble(oracle: RecordedOracle) -> None:
    m = R(oracle, "Je jezevčík pes?").main
    assert m.mood == "question" and m.kernel == "subset"
    assert terms(m, "kdo") == ["jezevčík"] and terms(m, "co") == ["pes"]


def test_cop_swap_nemate_definici_kdyz_korenu_ma_genitiv() -> None:
    """„Kdo byla matka Karla Čapka?“ (živá ukázka 27. 9. 2026, J.): tázací
    podmět + nominál v kořeni vypadá strukturně jako „Co je jezevčík?“
    (definiční otázka, cop-swap dá `kdo` z kořene, `co` je díra) — ale
    „matka Karla Čapka“ NENÍ definice pojmu „matka“, je to popis KONKRÉTNÍ
    osoby (kořen má holý genitivní doplněk, `_has_gen_complement`). Dřív
    cop-swap nerozlišoval a otázka vždy skončila NEVÍM (`kdo` bylo bez
    díry, `co` byla díra, kterou nic nevyplní). Ruční UD (ověřeno křížově
    proti SpacyOracle), ne živý UDPipe."""
    from cb6.oracle import Parse, Token
    p = Parse("Kdo byla matka Karla Čapka?", (
        Token(1, "Kdo", "kdo", "PRON", 3, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("PronType", "Int,Rel"))),
        Token(2, "byla", "být", "AUX", 3, "cop", (("Aspect", "Imp"), ("Gender", "Fem,Neut"), ("Number", "Plur,Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        Token(3, "matka", "matka", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Fem"), ("Number", "Sing"))),
        Token(4, "Karla", "Karel", "PROPN", 3, "nmod", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(5, "Čapka", "Čapek", "PROPN", 4, "flat", (("Animacy", "Anim"), ("Case", "Gen"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(6, "?", "?", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno křížově proti SpacyOracle) — test, ne živý UDPipe")
    m = read(p).main
    kdo, co = m.role("kdo"), m.role("co")
    assert kdo is not None and kdo.wh and not kdo.terms
    assert co is not None and not co.wh
    assert co.terms[0].lemma == "matka" and co.terms[0].rel_owner is not None
    assert co.terms[0].rel_owner.name_lemmas == ("Karel", "Čapek")


def test_cop_swap_definice_bez_genitivu_beze_zmeny() -> None:
    """Kontrola, že oprava výše nezasáhla „Co je jezevčík?“ (definiční
    otázka, kořen bez genitivního doplňku) — cop-swap dál funguje."""
    from cb6.oracle import Parse, Token
    p = Parse("Co je jezevčík?", (
        Token(1, "Co", "co", "PRON", 3, "nsubj", (("Animacy", "Inan"), ("Case", "Nom"), ("PronType", "Int,Rel"))),
        Token(2, "je", "být", "AUX", 3, "cop", (("Aspect", "Imp"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"), ("Polarity", "Pos"), ("Tense", "Pres"), ("VerbForm", "Fin"), ("Voice", "Act"))),
        Token(3, "jezevčík", "jezevčík", "NOUN", 0, "root", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
        Token(4, "?", "?", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno, zkopírováno z tests/data/parses.json) — test, ne živý UDPipe")
    m = read(p).main
    kdo, co = m.role("kdo"), m.role("co")
    assert kdo is not None and not kdo.wh and kdo.terms and kdo.terms[0].lemma == "jezevčík"
    assert co is not None and co.wh


def test_copula_determiners(oracle: RecordedOracle) -> None:
    m = R(oracle, "Každý spisovatel je člověk.").main
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].quant == "∀" and kdo.terms[0].quant_authority == "determiner"
    n = R(oracle, "Žádný stroj není člověk.").main
    assert n.neg and n.kernel == "subset" and n.role("kdo").terms[0].quant == "∀"  # type: ignore[union-attr]


def test_copula_within_and_member(oracle: RecordedOracle) -> None:
    m = R(oracle, "Praha je v Česku.").main
    assert m.kernel == "within" and terms(m, "kde") == ["Česko"]
    h = R(oracle, "Hrabal je spisovatel.").main
    assert h.kernel == "member" and terms(h, "kdo") == ["Hrabal"]


def test_bio_parenthesis(oracle: RecordedOracle) -> None:
    r = R(oracle, "Alois Jirásek (23. srpna 1851 Hronov – 12. března 1930 Praha) byl český prozaik, dramatik, středoškolský učitel, a politik.")
    m = r.main
    assert m.kernel == "member"
    assert terms(m, "co") == ["prozaik", "dramatik", "učitel", "politik"]
    assert m.role("co").terms[0].attrs == ("český",)  # type: ignore[union-attr]
    preds = {s.pred: s for s in m.secondary}
    assert set(preds) == {"narodit_se", "zemřít"}
    n = preds["narodit_se"]
    assert terms(n, "kdo") == ["Alois Jirásek"] and terms(n, "kde") == ["Hronov"]
    assert n.role("kdy").terms[0].time.start == (1851, 8, 23)  # type: ignore[union-attr]
    z = preds["zemřít"]
    assert terms(z, "kde") == ["Praha"] and z.role("kdy").terms[0].time.start == (1930, 3, 12)  # type: ignore[union-attr]
    assert "životopisná závorka" in n.defaults
    assert r.residue == []


def test_bio_parenthesis_dates_only(oracle: RecordedOracle) -> None:
    r = R(oracle, "Isaac Newton (4. ledna 1643 – 31. března 1727) byl anglický fyzik, matematik, astronom, alchymista a teolog.")
    preds = {s.pred: s for s in r.main.secondary}
    assert preds["narodit_se"].role("kdy").terms[0].time.year == 1643  # type: ignore[union-attr]
    assert preds["zemřít"].role("kdy").terms[0].time.year == 1727  # type: ignore[union-attr]
    assert terms(r.main, "co") == ["fyzik", "matematik", "astronom", "alchymista", "teolog"]
    assert r.residue == []


def test_definition_question(oracle: RecordedOracle) -> None:
    m = R(oracle, "Kdo je Isaac Newton?").main
    assert m.kind == "copula" and m.mood == "question"
    assert terms(m, "kdo") == ["Isaac Newton"]
    co = m.role("co")
    assert co and co.wh


def test_fragment_with_participle(oracle: RecordedOracle) -> None:
    r = R(oracle, "Úrazy způsobené pády.")
    assert r.main.kind == "fragment" and r.main.pred is None
    assert terms(r.main, "téma") == ["úraz"]
    sec = r.main.secondary[0]
    assert sec.pred == "způsobený" and terms(sec, "co") == ["úraz"] and terms(sec, "čím") == ["pád"]


def test_coordinated_predicates_share_subject(oracle: RecordedOracle) -> None:
    r = R(oracle, "Petr přišel a sedl si.")
    assert r.main.pred == "přijít" and terms(r.main, "kdo") == ["Petr"]
    assert r.main.secondary and r.main.secondary[0].pred.startswith("sednout") and terms(r.main.secondary[0], "kdo") == ["Petr"]


def test_possessive_and_correction_marker(oracle: RecordedOracle) -> None:
    m = R(oracle, "Filipovo auto je modré.").main
    kdo = m.role("kdo")
    assert kdo and kdo.terms[0].possessor == ("adj", "Filipův") and kdo.terms[0].quant == "·"
    assert terms(m, "jaký") == ["modrý"]
    n = R(oracle, "Ne, Petr bydlí v Brně.").main
    assert n.correction and not n.neg


def test_every_recorded_sentence_reads_and_places_all_tokens(oracle: RecordedOracle) -> None:
    lines = [l.strip() for l in SENTENCES.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    for text in lines:
        R(oracle, text)
