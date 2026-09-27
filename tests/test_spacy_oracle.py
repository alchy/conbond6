"""`SpacyOracle` (cb6/oracle.py) — NN parser, ne LLM, záchranná cesta pro
prostředí bez UDPipe (viz mereni/HYPOTEZY.md 2026-09-27). Volitelná
závislost (`pip install -e '.[spacy-cs]'`) — přeskočí se, když chybí,
ať hlavní sada na ní nezávisí.
"""

import json
from pathlib import Path

import pytest

pytest.importorskip("cs_core_news_sm")

from cb6.oracle import OracleError, SegmentationError, SpacyOracle  # noqa: E402  # pylint: disable=wrong-import-position


@pytest.fixture(scope="module")
def oracle() -> SpacyOracle:
    return SpacyOracle()


def test_provenience_je_jasne_odlisena_od_udpipe(oracle: SpacyOracle) -> None:
    assert oracle.provenance == "spacy model=cs_core_news_sm"
    assert "udpipe" not in oracle.provenance.lower()


def test_parse_jedne_vety_ma_koren(oracle: SpacyOracle) -> None:
    p = oracle.parse("Alois Jirásek se narodil v Hronově.")
    assert p.root().form == "narodil" and p.root().head == 0
    assert p.root().lemma == "narodit"


def test_vic_vet_v_parse_da_segmentation_error(oracle: SpacyOracle) -> None:
    with pytest.raises(SegmentationError):
        oracle.parse("Petr bydlí v Praze. Karel žije v Brně.")


def test_prazdny_text_selze_nahlas(oracle: SpacyOracle) -> None:
    with pytest.raises(OracleError):
        oracle.parse("")


def test_segment_rozdeli_spravne_na_dve_vety_s_vlastnim_korenem(oracle: SpacyOracle) -> None:
    """Vlastní věta-splitting: parser modelu bez něj druhou větu za tečkou
    umí přilepit jako `conj` k první (zjištěno prakticky) — tenhle test by
    bez opravy selhal na `len(parses) == 1`."""
    parses = oracle.segment("Petr bydlí v Praze. Karel žije v Brně.")
    assert len(parses) == 2
    assert parses[0].root().form == "bydlí" and parses[1].root().form == "žije"
    assert [t.form for t in parses[0].tokens] == ["Petr", "bydlí", "v", "Praze", "."]


def test_shoda_s_udpipe2_na_zaznamenanem_korpusu_je_stabilni() -> None:
    """Zamyká změřenou shodu (mereni/HYPOTEZY.md 2026-09-27: 50,8 % vět
    přesně, 83,1 % tokenů) — NE proto, aby se tahle cesta nasadila na
    historická čísla (výslovně se nenasazuje), ale aby tichá regrese/
    zlepšení modelu bylo vidět hned, ne až při příštím ručním přepočtu."""
    oracle = SpacyOracle()
    data = json.loads((Path(__file__).parent / "data" / "parses.json").read_text(encoding="utf-8"))
    total_tok = mismatch_tok = sent_exact = sent_total = 0
    for text, gold in data.items():
        sent_total += 1
        try:
            parse = oracle.parse(text)
        except (OracleError, SegmentationError):
            continue
        if len(parse.tokens) != len(gold["tokens"]):
            continue
        ok = True
        for t, g in zip(parse.tokens, gold["tokens"]):
            total_tok += 1
            if (t.lemma, t.upos, t.head, t.deprel) != (g["lemma"], g["upos"], g["head"], g["deprel"]):
                mismatch_tok += 1
                ok = False
        sent_exact += ok
    assert sent_total == 177
    assert sent_exact == 90
    assert mismatch_tok == 153
