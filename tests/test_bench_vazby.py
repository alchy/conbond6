"""`bench/vazby.py` — pokročilost chápání vazeb podle mechanismu; regrese
zamčí dnešní stav (všechny čtyři mechanismy hotové, 7/7), ať se příští
úprava dozví okamžitě, když se něco z tohohle tiše rozbije."""

from bench.vazby import CASES, check


def test_vsechny_mechanismy_prochazi() -> None:
    by_case = {c.id: check(c) for c in CASES}
    assert all(by_case.values()), f"selhalo: {[k for k, v in by_case.items() if not v]}"


def test_kazdy_pripad_ma_jednoznacny_mechanismus() -> None:
    assert {c.zdroj for c in CASES} <= {"prikaz", "veta", "korekce", "graf"}
    assert len({c.id for c in CASES}) == len(CASES)
