"""Veličiny: hodnota + jednotka → dimenze (spec krok 2, operátor `porovnání`).

Proč vlastní modul, ne rovnou v `lexicon.py`: `porovnání` (spec: „délka(A) ≤
délka(B) ⇒ vejít_se“) potřebuje napřed umět srovnat DVĚ ČÍSLA na téže
dimenzi po převodu jednotek — to je čistý výpočet, žádná znalost o světě,
stejná role jako `chronos.before/within/overlap` pro čas. Tenhle modul dodá
primitiv (`Quantity`, `dimension_of`, `to_base`, `compare`); samotný
lexikonový operátor `porovnání` (řádek dat, derivované predikáty jako
`vejít_se`, query-time join v `Evaluator` — stejný vzor jako `překryv`) je
DALŠÍ tah, záměrně neudělaný teď (viz `docs/HANDOVER.md` § 6): která
strana porovnání (`≤`/`≥`/`=`) patří ke kterému derivovanému predikátu je
otevřená otázka bez reálného textu na ověření, ne dohad, který se má
zakódovat narychlo.

Jednotky jsou dnes česká slova natvrdo (`UNITS`) — až se tohle zapojí do
čtení, mají se stěhovat do `cb6/lang/cs.json` stejně jako `chronos.MONTHS`
(27. 9. 2026 refaktor „jazyk jako data“); dokud operátor nikdo nepoužívá,
přesun by byl práce navíc bez testu, který by ji ověřil.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

#: jednotka (lemma) → (dimenze, převodní faktor na základní jednotku dimenze).
#: Základní jednotka každé dimenze má faktor 1.0. Jen délka a hmotnost —
#: rozšířit, až bude mít krok 2 skutečný text s jinou dimenzí k měření.
UNITS: dict[str, tuple[str, float]] = {
    "milimetr": ("délka", 0.001), "centimetr": ("délka", 0.01), "metr": ("délka", 1.0),
    "kilometr": ("délka", 1000.0),
    "gram": ("hmotnost", 0.001), "kilogram": ("hmotnost", 1.0), "tuna": ("hmotnost", 1000.0),
}

Comparison = Literal["<", "=", ">"]


@dataclass(frozen=True, slots=True)
class Quantity:
    """Hodnota s jednotkou (lemma, ne povrchový tvar — „metrů“ i „metry“ = „metr“)."""

    value: float
    unit: str

    def __str__(self) -> str:
        return f"{self.value:g} {self.unit}"


def dimension_of(unit: str) -> str | None:
    """Dimenze jednotky, nebo `None` (neznámá jednotka).
    Vstup: lemma jednotky. Výstup: jméno dimenze, nebo `None`."""
    entry = UNITS.get(unit)
    return entry[0] if entry else None


def to_base(q: Quantity) -> float | None:
    """Hodnota v základní jednotce dimenze (pro porovnání různých jednotek
    téže dimenze). Vstup: veličina. Výstup: číslo, nebo `None` (neznámá jednotka)."""
    entry = UNITS.get(q.unit)
    return q.value * entry[1] if entry else None


def compare(a: Quantity, b: Quantity) -> Comparison | None:
    """Porovnej dvě veličiny po převodu na základní jednotku téže dimenze.

    Proč `None` u různých dimenzí: „delší než těžší“ nedává smysl a nesmí
    tiše spadnout na porovnání čísel bez ohledu na jednotku (5 kg vs 3 m).
    Vstup: dvě veličiny. Výstup: `'<'`/`'='`/`'>'` (`a` vůči `b`), nebo
    `None` (různá dimenze, nebo neznámá jednotka)."""
    da, db = dimension_of(a.unit), dimension_of(b.unit)
    if da is None or da != db:
        return None
    va, vb = to_base(a), to_base(b)
    if va is None or vb is None:
        return None
    if va < vb:
        return "<"
    if va > vb:
        return ">"
    return "="
