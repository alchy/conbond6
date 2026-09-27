"""`bench/vazby.py` — pokročilost chápání vazeb podle mechanismu; regrese
zamčí dnešní stav (příkaz/věta hotovo, korekce/graf cíl), ať se příští
úprava dozví okamžitě, když se něco z tohohle tiše rozbije nebo zlepší."""

from bench.vazby import CASES, check


def test_prikaz_a_veta_prochazi_korekce_a_graf_jeste_ne() -> None:
    by_case = {c.id: check(c) for c in CASES}
    hotovo = {k: v for k, v in by_case.items() if k.startswith(("prikaz:", "veta:"))}
    cil = {k: v for k, v in by_case.items() if k.startswith(("korekce:", "graf:"))}
    assert all(hotovo.values()), f"selhalo, co má fungovat: {[k for k, v in hotovo.items() if not v]}"
    assert not any(cil.values()), (
        f"cílový mechanismus teď prochází ({[k for k, v in cil.items() if v]}) — "
        "pokud je to skutečná nová schopnost, aktualizuj HYPOTEZY/HANDOVER, ne jen tenhle test"
    )


def test_kazdy_pripad_ma_jednoznacny_mechanismus() -> None:
    assert {c.zdroj for c in CASES} <= {"prikaz", "veta", "korekce", "graf"}
    assert len({c.id for c in CASES}) == len(CASES)
