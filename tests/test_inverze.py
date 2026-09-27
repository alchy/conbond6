"""Fragmentový úkol (krok 3, poslední kus — vztahový operátor `inverze`):
ověřuje, že fakt `zdroj(kdo=X, čí=Y)` (např. `bratr`, viz G-3) dá ANO na
otázku „Je Y <cíl> X?“ (např. „Je Karel Čapek sourozenec Josefa Čapka?“)
přes seed `cb6/lexikon/inverze.jsonl`. Věty samy nejsou čtené parserem —
stejný důvod jako `test_prekryv.py`: čtecí strana (rozpoznat takovou
otázku z reálného textu) čeká na reálné otázky (HANDOVER § 6/8, 27. 9.
2026 — „vědomě NEimplementováno“), tenhle test ověřuje jen logickou
vrstvu (`Lexicon.inverze_rules_by_target` + `Evaluator.inverze_verdict`)
a její doložitelnost z exportu grafu (I‑12).
"""

from bench.graphcheck import check_answer, check_graph
from cb6.logic import evaluate
from cb6.memory import Memory, Provenance, Role, Statement


def _fact(m: Memory, doc: str, no: int, pred: str, kdo_jmeno: list[str], ci_jmeno: list[str]) -> None:
    """Zapiš „<kdo_jmeno> je <pred> <ci_jmeno>.“ přímo jako výrok (G-3 tvar:
    kdo=entita, čí=entita) — fragment bez čtení z textu."""
    sent = m.new_sentence(doc, no, f"{' '.join(kdo_jmeno)} je {pred} {' '.join(ci_jmeno)}.")
    kdo, _ = m.ensure_entity(kdo_jmeno, doc=doc)
    ci, _ = m.ensure_entity(ci_jmeno, doc=doc)
    m.note_mention(sent.id, kdo.id, "kdo", " ".join(kdo_jmeno))
    m.note_mention(sent.id, ci.id, "čí", " ".join(ci_jmeno))
    st = Statement("", pred, "verb", roles=[Role("kdo", [kdo.id]), Role("čí", [ci.id])],
                   grade="said", mood="assert", claim="SAFE", sentence=sent.id,
                   prov=Provenance(doc, no, f"{' '.join(kdo_jmeno)} je {pred} {' '.join(ci_jmeno)}.", no, "test"))
    m.attach(st)


def _je_cil_ci(m: Memory, kdo_id: str, cil_lemma: str, ci_id: str) -> Statement:
    """„Je <kdo> <cíl> <čí>?“ — dotaz s rolí `co` = skupina pojmenovaná `cil_lemma`."""
    skupina = m.ensure_group(cil_lemma)
    return Statement("", "být", "copula", mood="question",
                      roles=[Role("kdo", [kdo_id]), Role("co", [skupina.id]), Role("čí", [ci_id])])


def test_bratr_da_ano_na_sourozenec_v_obracenem_smeru() -> None:
    m = Memory()
    _fact(m, "d", 1, "bratr", ["Josef", "Čapek"], ["Karel", "Čapek"])  # Josef je bratr Karla
    josef = m.find_entity(["josef", "čapek"])[0]
    karel = m.find_entity(["karel", "čapek"])[0]
    # „Je Karel Čapek sourozenec Josefa Čapka?“ — obrácený směr; otázka
    # nesmí měnit bázi (I-12) — skupina `sourozenec`, kterou dotaz založí,
    # se po odpovědi odklidí stejně jako v produkci (`Session._answer`).
    before = m.snapshot()
    v = evaluate(m, _je_cil_ci(m, karel.id, "sourozenec", josef.id))
    m.prune_orphans(before)
    assert v.value == "ANO" and v.proofs[0].grade == "derived"
    hard_kinds = {k for k, _, _ in v.proofs[0].hard}
    assert {"role:kdo", "role:čí", "lex"} <= hard_kinds
    g = m.graph()
    assert not check_graph(g)
    assert not check_answer(g, list(v.proofs[0].statements), list(v.proofs[0].hard))
    # bez materializace řádku `inverze` by krok `lex` nebyl doložený (I-12)
    lex_nodes = [n for n, d in g.nodes(data=True) if d.get("kind") == "vazba" and d.get("op") == "inverze"]
    assert lex_nodes
    g.remove_node(lex_nodes[0])
    assert [x.check for x in check_answer(g, list(v.proofs[0].statements), list(v.proofs[0].hard))] == ["rekonstrukce"]


def test_manzel_manzelka_presny_par() -> None:
    m = Memory()
    _fact(m, "d", 1, "manžel", ["Jan", "Novák"], ["Marie", "Nováková"])  # Jan je manžel Marie
    jan = m.find_entity(["jan", "novák"])[0]
    marie = m.find_entity(["marie", "nováková"])[0]
    v = evaluate(m, _je_cil_ci(m, marie.id, "manželka", jan.id))
    assert v.value == "ANO"


def test_chybejici_fakt_dava_nevim_ne_falesne_ano() -> None:
    """Bez opačného faktu se `inverze` nesmí uhodnout — NEVÍM, ne ANO."""
    m = Memory()
    neznamy_x, _ = m.ensure_entity(["Neznámý", "X"], doc="d")
    neznamy_y, _ = m.ensure_entity(["Neznámý", "Y"], doc="d")
    v = evaluate(m, _je_cil_ci(m, neznamy_x.id, "sourozenec", neznamy_y.id))
    assert v.value == "NEVÍM"


def test_spatny_smer_dava_nevim() -> None:
    """Fakt `bratr(kdo=Josef, čí=Karel)` odpovídá na „Je KAREL sourozenec
    JOSEFA?“ (obrácený směr), ne na „Je JOSEF sourozenec Karla?“ (stejný
    směr — to by byl jiný, nepodložený závěr)."""
    m = Memory()
    _fact(m, "d", 1, "bratr", ["Josef", "Čapek"], ["Karel", "Čapek"])
    josef = m.find_entity(["josef", "čapek"])[0]
    karel = m.find_entity(["karel", "čapek"])[0]
    v = evaluate(m, _je_cil_ci(m, josef.id, "sourozenec", karel.id))
    assert v.value == "NEVÍM"
