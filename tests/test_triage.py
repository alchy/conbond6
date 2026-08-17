"""Task 6 — triáž: podmínka ≠ tvrzení, obsah promluvy ≠ fakt, disjunkce → REJECTED,
vedlejší nmod → REJECTED, fragment mimo znalost, typing mimo yield."""
import pytest

from cb6.ground import ground, ground_triaged
from cb6.memory import Memory, Provenance
from cb6.oracle import RecordedOracle
from cb6.read import read
from cb6.triage import triage

O = RecordedOracle("tests/data/parses.json")


def _t(s):
    return triage(read(O.parse(s), "assert"))


def _mem(*sentences):
    m = Memory()
    for i, s in enumerate(sentences, 1):
        ground(read(O.parse(s), "assert"), m, Provenance("d", i, s), "read")
    return m


def test_podminka_je_pravidlo_ne_tvrzeni():
    t = _t("Karel přijde na oslavu, pokud přijde Jana.")
    assert len(t.rules) == 1 and t.rules[0].kind == "if"
    assert t.rules[0].cond.pred == "přijít" and t.rules[0].cons.pred == "přijít"
    m = Memory()
    ground_triaged(t, m, Provenance("d", 1, "…"), "read")
    kinds = [s.kind for s in m.knowledge()]
    assert kinds == ["rule"]                     # jediná znalost je pravidlo
    assert {s.mood for s in m.active()} == {"assert", "pattern"}
    rule = next(s for s in m.knowledge())
    assert rule.role("pokud").nested and rule.role("pak").nested


def test_jen_pokud_obraci_smer():
    t = _t("Petr přijde jen pokud přijde Karel.")
    assert t.rules and t.rules[0].kind == "only_if"


def test_kdyz_v_minulem_case_je_cas_ne_podminka():
    t = _t("Když pršelo, zůstal doma.")
    assert not t.rules
    m = Memory()
    ground_triaged(t, m, Provenance("d", 1, "…"), "read")
    assert any(s.pred == "zůstat" for s in m.knowledge())


def test_kdyz_v_prezentu_je_podminka_s_vychozi_volbou():
    t = _t("Petr a Karel přijdou, když nepřijde Marie.")
    assert t.rules and t.rules[0].kind == "if"
    assert any("když" in n for n in t.notes)


def test_obsah_promluvy_neni_fakt():
    m = _mem("Petr řekl, že Marie přijde.")
    preds = {(s.pred, s.mood) for s in m.active()}
    assert ("říci", "assert") in preds and ("přijít", "reported") in preds
    assert [s.pred for s in m.knowledge()] == ["říci"]


def test_vnoreny_obsah_jinych_sloves_take_neni_fakt():
    m = _mem("Bylo rozhodnuto konat pohřební obřady bez účasti kněze.", "Nemoc mu znemožnila psát.")
    know = {s.pred for s in m.knowledge()}
    assert "konat" not in know and "psát" not in know
    assert any(s.pred == "konat" and s.mood == "reported" for s in m.active())


def test_disjunkce_a_kardinalita_jsou_zamitnute_a_dohledatelne():
    for s in ("Petr nebo Jana přijde.", "Přijde aspoň jeden z nich."):
        t = _t(s)
        d = t.decision(t.reading.main)
        assert d.claim == "REJECTED" and "prostoru modelů" in d.reason
    m = _mem("Petr nebo Jana přijde.")
    assert list(m.knowledge()) == []
    assert m.by_claim("REJECTED")


def test_vedlejsi_nmod_je_zamitnut_fragment_mimo_znalost():
    m = _mem("Manifest českých spisovatelů a vyhlášení samostatnosti", "Život")
    assert list(m.knowledge()) == []
    rej = m.by_claim("REJECTED")
    assert rej and all("vedlejší vztah" in s.reason for s in rej)
    frag = [s for s in m.active() if s.kind == "fragment"]
    assert frag and all(s.claim == "SAFE" for s in frag)   # fragment je viditelný, ale není znalost


def test_typing_vyrok_je_safe_ale_oznaceny():
    m = _mem("Jako jeden z prvních podepsal Manifest českých spisovatelů.")
    typing = [s for s in m.active() if s.kind == "typing"]
    assert typing and all(s.claim == "SAFE" and s.kernel == "member" for s in typing)
    assert any(s.pred == "podepsat" for s in m.knowledge())


@pytest.mark.parametrize("sentence", ["Alois Jirásek se narodil v Hronově.", "Petr přijde."])
def test_prosta_veta_je_safe(sentence):
    m = _mem(sentence)
    assert [s.claim for s in m.knowledge()] == ["SAFE"]
