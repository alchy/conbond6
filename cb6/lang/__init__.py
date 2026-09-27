"""Jazyková pravidla čtení jako DATA, oddělená per jazyk (JSON).

Proč (rozhodnutí J., 27. 9. 2026): má-li NN dělat *strukturu* (parsing,
extrakci, konverzaci) a graf zůstat jediným místem, kde žije *znalost*
(rozšíření I‑9 z „LM je jen soudce a generátor otázek“ na „NN nikdy fakt,
jen strukturu — v libovolném jazyce“), nesmí být čtecí pravidla natvrdo
česká slova v Pythonu. Dosud byla (`cb6/defaults.py`, `cb6/chronos.py`):
pády→role, měsíce, modální slovesa, částice… Tenhle modul je jedno místo,
odkud se čtou — stejný vzorec jako `cb6/lexicon.py` (vazby jako data):
jeden JSON soubor na jazyk (`cb6/lang/<kód>.json`), `defaults.py`/
`chronos.py` jen re‑exportují načtené tabulky pod stejnými jmény, aby se
nemusel měnit žádný spotřebitel (`read.py`, `triage.py`, `logic.py`).

Co se NEmění: vnitřní klíče rolí (`kde`, `kdo`, `co`…) a graf zůstávají
opaque symboly — nejsou to „česká slova", jsou to jména hran; jazykové je
jen jejich ČTENÍ z povrchového tvaru. Operátory (`cb6/lexicon.py`,
`cb6/chronos.py` `before/within/overlap`) jsou jazykově neutrální beze
změny.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

#: Adresář jazykových souborů (`<kód>.json`, jeden na jazyk).
LANG_DIR = Path(__file__).parent


@dataclass(frozen=True)
class LanguageRules:
    """Jedna sada čtecích tabulek pro jazyk `code` (viz `load_language`).

    Pole odpovídají 1:1 dosavadním tabulkám v `defaults.py`/`chronos.py`;
    typy (frozenset/dict/tuple) jsou stejné, jen zdroj je JSON, ne literál."""

    code: str
    role_by_case: dict[tuple[str, str], dict[str, str]]
    determiner_quant: dict[str, str]
    possessive: frozenset[str]
    particles: frozenset[str]
    sequence_adverbs: frozenset[str]
    modal_verbs: dict[str, str]
    wh: dict[str, tuple[str, str]]
    list_verbs: frozenset[str]
    place_nouns: frozenset[str]
    place_preps: frozenset[str]
    personal_pronouns: frozenset[str]
    conditional_markers: dict[str, str]
    only_if_adverbs: frozenset[str]
    iff_adverbs: frozenset[str]
    purpose_marks: frozenset[str]
    attitude_verbs: frozenset[str]
    disjunction_cc: frozenset[str]
    cardinality_adverbs: frozenset[str]
    months: dict[str, int]
    weekdays: tuple[str, ...]
    seasons: tuple[str, ...]
    relative_days: tuple[str, ...]
    time_nouns_base: frozenset[str]


@lru_cache(maxsize=8)
def load_language(code: str) -> LanguageRules:
    """Načti čtecí tabulky jazyka `code` z `cb6/lang/<code>.json` (kešované —
    soubor se za běhu nemění, stejně jako `cb6.lexicon.load_seed`).

    Vstup: kód jazyka (`"cs"`). Výstup: `LanguageRules`.
    `FileNotFoundError`, když jazyk nemá soubor — žádný tichý fallback na
    češtinu (I‑9: chybějící jazyk je otevřená položka, ne domněnka)."""
    path = LANG_DIR / f"{code}.json"
    d: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    role_by_case = {(r["prep"], r["case"]): dict(r["roles"]) for r in d["role_by_case"]}
    wh = {k: (v[0], v[1]) for k, v in d["wh"].items()}
    return LanguageRules(
        code=code,
        role_by_case=role_by_case,
        determiner_quant=dict(d["determiner_quant"]),
        possessive=frozenset(d["possessive"]),
        particles=frozenset(d["particles"]),
        sequence_adverbs=frozenset(d["sequence_adverbs"]),
        modal_verbs=dict(d["modal_verbs"]),
        wh=wh,
        list_verbs=frozenset(d["list_verbs"]),
        place_nouns=frozenset(d["place_nouns"]),
        place_preps=frozenset(d["place_preps"]),
        personal_pronouns=frozenset(d["personal_pronouns"]),
        conditional_markers=dict(d["conditional_markers"]),
        only_if_adverbs=frozenset(d["only_if_adverbs"]),
        iff_adverbs=frozenset(d["iff_adverbs"]),
        purpose_marks=frozenset(d["purpose_marks"]),
        attitude_verbs=frozenset(d["attitude_verbs"]),
        disjunction_cc=frozenset(d["disjunction_cc"]),
        cardinality_adverbs=frozenset(d["cardinality_adverbs"]),
        months=dict(d["months"]),
        weekdays=tuple(d["weekdays"]),
        seasons=tuple(d["seasons"]),
        relative_days=tuple(d["relative_days"]),
        time_nouns_base=frozenset(d["time_nouns_base"]),
    )


def available_languages() -> tuple[str, ...]:
    """Kódy jazyků, pro které existuje soubor. Vstup: nic. Výstup: n‑tice kódů."""
    return tuple(sorted(p.stem for p in LANG_DIR.glob("*.json")))
