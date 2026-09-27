"""Krok „render odpovědí — méně dat, víc klidu“ (27. 9. 2026, J.): NEVÍM
nemá být report. `render_answer` ukáže nejvýš `KNOWN_SHOWN_MAX` blízkých
výroků bez zdroje (ten dá `!ukaž <id>` tomu, kdo ho chce), víc jich jen
spočítá. Ruční `Statement`/`Memory` — stejný žánr jako `test_prekryv.py`."""

from cb6.logic import Verdict
from cb6.memory import Memory, Provenance, Role, Statement
from cb6.render import KNOWN_SHOWN_MAX, render_answer


def _fact(m: Memory, no: int, pred: str, kdo_jmeno: str) -> Statement:
    kdo, _ = m.ensure_entity([kdo_jmeno], doc="d")
    st = Statement("", pred, "verb", roles=[Role("kdo", [kdo.id])], grade="said",
                    mood="assert", claim="SAFE", sentence="", prov=Provenance("d", no, f"{kdo_jmeno} {pred}.", no, "test"))
    m.attach(st)
    return st


def test_nevim_ukaze_nejvys_strop_znamych_a_spocita_zbytek() -> None:
    m = Memory()
    known = [_fact(m, i, "žít", f"Osoba{i}") for i in range(1, KNOWN_SHOWN_MAX + 3)]
    v = Verdict("NEVÍM", near=[st.id for st in known])
    text = render_answer(m, v, wh=False)
    # bez zdroje — jen samotný výrok (I-4: NEVÍM je NEVÍM, ne skrytá odpověď)
    assert "zdroj:" not in text
    assert text.count("žít(kdo:") == KNOWN_SHOWN_MAX
    assert f"+ {len(known) - KNOWN_SHOWN_MAX} další" in text


def test_nevim_pod_stropem_nic_nepocita() -> None:
    m = Memory()
    known = [_fact(m, i, "žít", f"Osoba{i}") for i in range(1, KNOWN_SHOWN_MAX + 1)]
    v = Verdict("NEVÍM", near=[st.id for st in known])
    text = render_answer(m, v, wh=False)
    assert text.count("žít(kdo:") == KNOWN_SHOWN_MAX
    assert "další" not in text


def test_missing_a_notes_se_slouci_do_jedne_radky() -> None:
    m = Memory()
    v = Verdict("NEVÍM", missing=["o Brno nevím nic", "o roku 2020 nevím nic"], notes=["poznámka jedna", "poznámka dvě"])
    text = render_answer(m, v, wh=False)
    lines = text.splitlines()
    missing_lines = [l for l in lines if "chybí" in l]
    note_lines = [l for l in lines if l.strip().startswith("⚠")]
    assert len(missing_lines) == 1 and "Brno" in missing_lines[0] and "2020" in missing_lines[0]
    assert len(note_lines) == 1 and "jedna" in note_lines[0] and "dvě" in note_lines[0]
