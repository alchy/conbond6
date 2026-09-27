"""Veličiny: hodnota+jednotka → dimenze, převod, porovnání (spec krok 2, operátor `porovnání` — primitiv, ne operátor sám)."""

from cb6.quantity import Quantity, compare, dimension_of, to_base


def test_dimension_of() -> None:
    assert dimension_of("metr") == "délka" and dimension_of("kilometr") == "délka"
    assert dimension_of("kilogram") == "hmotnost"
    assert dimension_of("banán") is None


def test_to_base() -> None:
    assert to_base(Quantity(1, "kilometr")) == 1000.0
    assert to_base(Quantity(150, "centimetr")) == 1.5
    assert to_base(Quantity(5, "banán")) is None


def test_compare_stejna_dimenze() -> None:
    assert compare(Quantity(2, "kilometr"), Quantity(500, "metr")) == ">"
    assert compare(Quantity(500, "metr"), Quantity(2, "kilometr")) == "<"
    assert compare(Quantity(1000, "metr"), Quantity(1, "kilometr")) == "="


def test_compare_ruzna_dimenze_je_none() -> None:
    """„Delší než těžší“ nedává smysl — nesmí tiše porovnat čísla bez jednotky."""
    assert compare(Quantity(5, "kilogram"), Quantity(3, "metr")) is None


def test_compare_neznama_jednotka_je_none() -> None:
    assert compare(Quantity(5, "banán"), Quantity(3, "banán")) is None
