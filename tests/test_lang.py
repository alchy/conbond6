"""Jazyková pravidla jako data (`cb6/lang`): loader, re-export beze změny chování."""

import pytest

from cb6 import chronos, defaults
from cb6.lang import LanguageRules, available_languages, load_language


def test_cesky_jazyk_se_nacte() -> None:
    lx = load_language("cs")
    assert isinstance(lx, LanguageRules) and lx.code == "cs"
    assert lx.role_by_case[("v", "Loc")] == {"place": "kde", "time": "kdy", "duration": "kdy", "*": "v+Loc"}
    assert lx.wh["kde"] == ("kde", "filler")
    assert lx.months["srpen"] == 8
    assert "pondělí" in lx.weekdays and "jaro" in lx.seasons
    assert lx.possessive_suffixes == ("ův", "ova", "ovo", "in", "ina", "ino")


def test_kesovano_je_tentyz_objekt() -> None:
    assert load_language("cs") is load_language("cs")


def test_neznamy_jazyk_selze_nahlas() -> None:
    with pytest.raises(FileNotFoundError):
        load_language("xx")


def test_dostupne_jazyky() -> None:
    assert "cs" in available_languages()


def test_defaults_reexportuje_nactene_tabulky() -> None:
    """`defaults.py` a `chronos.py` po refaktoru (27. 9. 2026) jen re-exportují
    `cb6/lang/cs.json` pod starými jmény — žádný spotřebitel (`read.py`,
    `triage.py`, `logic.py`) se nemusel měnit."""
    lx = load_language("cs")
    assert defaults.ROLE_BY_CASE == lx.role_by_case
    assert defaults.WH == lx.wh
    assert defaults.LIST_VERBS == lx.list_verbs
    assert defaults.ATTITUDE_VERBS == lx.attitude_verbs
    assert defaults.POSSESSIVE_SUFFIXES == lx.possessive_suffixes
    assert chronos.MONTHS == lx.months
    assert chronos.WEEKDAYS == lx.weekdays
    assert chronos.TIME_NOUNS >= lx.time_nouns_base
    assert set(chronos.MONTHS) <= chronos.TIME_NOUNS and set(chronos.WEEKDAYS) <= chronos.TIME_NOUNS
