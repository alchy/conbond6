"""Dialog: vkládání, otázky, opravy, backlog, příkazy, propad, render, replay."""

from pathlib import Path

import pytest

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import RecordedOracle
from cb6.recall import recall

DATA = Path(__file__).parent / "data" / "parses.json"


@pytest.fixture()
def s() -> Session:
    return Session(Memory(), RecordedOracle(DATA))


def test_ingest_then_ask_with_source(s: Session) -> None:
    reps = s.ingest("Alois Jirásek se narodil ve východočeském Hronově u Náchoda.\nCelý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.", "alois_jirásek")
    assert len(reps) == 2 and all(r["statements"] for r in reps)
    a = s.say("Kde se narodil Alois Jirásek?")
    assert a.verdict is not None and a.verdict.value == "ANO"
    assert "Hronov" in a.text and "zdroj: „Alois Jirásek se narodil" in a.text and "alois_jirásek, věta 1" in a.text
    b = s.say("Kde pracoval Alois Jirásek?")
    assert "Litomyšl" in b.text and "Praha" in b.text and "nevyslovený podmět" in b.text


def test_unknown_stays_unknown_and_correction(s: Session) -> None:
    s.say("Petr bydlí v Praze.")
    a = s.say("Bydlí Petr v Brně?")
    assert a.verdict is not None and a.verdict.value == "NEVÍM" and "vím:" in a.text and "Praha" in a.text
    c = s.say("Ne, Petr bydlí v Brně.")
    assert c.revoked == ["s0001"] and c.statements
    assert "Brno" in s.say("Kde bydlí Petr?").text
    assert s.memory.statements["s0001"].status == "revoked"
    # oprava MÍSTA, ne predikátu (stejné sloveso „bydlet“) — nesmí se naučit žádná vazba
    assert not [l for l in s.memory.links.values() if l.authority == "read"]


def test_korekce_uci_vazbu_mezi_predikaty(s: Session) -> None:
    """Oprava „Ne, X namísto Y“ o TÉMŽ podmětu a MÍSTĚ, jen jiným slovesem,
    je kontextový důkaz vztahu mezi predikáty — bez klíčového slova, bez
    příkazu (J. 27. 9. 2026; `bench/vazby.py` mechanismus `korekce`).
    Rozbor druhé věty ručně sestavený (stejná poctivost jako
    `tests/test_lex_teach.py` — viz `mereni/HYPOTEZY.md` 2026‑09‑27)."""
    from cb6.oracle import Parse, Token
    zil = Parse("Ne, Petr žil v Praze.", (
        Token(1, "Ne", "ne", "PART", 4, "advmod:emph", ()),
        Token(2, ",", ",", "PUNCT", 1, "punct", ()),
        Token(3, "Petr", "Petr", "PROPN", 4, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        Token(4, "žil", "žít", "VERB", 0, "root", (("Aspect", "Imp"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        Token(5, "v", "v", "ADP", 6, "case", (("AdpType", "Prep"), ("Case", "Loc"))),
        Token(6, "Praze", "Praha", "PROPN", 4, "obl", (("Case", "Loc"), ("Gender", "Fem"), ("NameType", "Geo"), ("Number", "Sing"))),
        Token(7, ".", ".", "PUNCT", 4, "punct", ()),
    ), "ruční UD (ověřeno) — test, ne UDPipe")

    class _Then:
        def parse(self, text: str) -> Parse:
            assert text == zil.text
            return zil
    s.say("Petr bydlí v Praze.")
    s.oracle = _Then()  # druhá věta není v tests/data/parses.json — ruční rozbor jen pro ni
    s.say("Ne, Petr žil v Praze.")
    said = [l for l in s.memory.links.values() if l.authority == "read"]
    # síla `related`: nikdy ve verdiktu (I-3, ověřeno obecně v test_lexicon.py) — jen nápověda
    assert len(said) == 1 and said[0].args == ("bydlet", "žít") and said[0].strength == "related"


def test_denial_revokes_last(s: Session) -> None:
    s.say("Pes štěká.")
    a = s.say("To není pravda.")
    assert a.revoked == ["s0001"]
    assert s.say("Štěká pes?").verdict.value == "NEVÍM"  # type: ignore[union-attr]


def test_conflict_is_reported_and_exception_narrows(s: Session) -> None:
    s.say("Ptáci létají.")
    s.say("Tučňák je pták.")
    assert s.say("Létá tučňák?").verdict.value == "ANO"  # type: ignore[union-attr]
    a = s.say("Tučňák nelétá.")
    assert a.conflict is not None and "odporuje" in a.text
    assert s.say("Létá tučňák?").verdict.value == "KONFLIKT"  # type: ignore[union-attr]
    assert "výjimka" in s.say("!výjimka létat pták tučňák").text
    assert s.say("Létá tučňák?").verdict.value == "NE"  # type: ignore[union-attr]
    s.say("Vrabec je pták.")
    assert s.say("Létá vrabec?").verdict.value == "ANO"  # type: ignore[union-attr]


def test_role_learning_closes_open_item(s: Session) -> None:
    a = s.say("Vesmír se rozšířil do dnešní podoby.")
    assert any(o.kind == "role_name" and o.about == "do+Gen" for o in a.open)
    assert "o0001" in s.say("!otevřené").text
    r = s.say("!role do+Gen = kam")
    assert "přejmenováno v 1" in r.text
    assert s.say("!otevřené").text == "žádné otevřené položky"
    st = s.memory.statements["s0001"]
    assert st.role("kam") is not None


def test_rule_command_bridges(s: Session) -> None:
    s.say("Petr jel v pondělí do Prahy.")
    s.say("Praha je v Česku.")
    assert s.say("Byl Petr v pondělí v Česku?").verdict.value == "NEVÍM"  # type: ignore[union-attr]
    assert "pravidlo r0001" in s.say("!pravidlo jet(kam:X) => být(kde:X)").text
    a = s.say("Byl Petr v pondělí v Česku?")
    assert a.verdict.value == "ANO" and "pravidlo r0001" in a.text  # type: ignore[union-attr]


def test_synonym_command(s: Session) -> None:
    """`!uč` píše řádek lexikonu s autoritou `said` — jen do této paměti, ne do seedu."""
    from cb6.lexicon import Lexicon
    r = s.say("!uč napsat = stvořit")
    assert "naučeno lex:said:" in r.text and "napsat ~ stvořit" in r.text
    assert Lexicon.for_memory(s.memory).match("napsat", "stvořit") is not None
    assert Lexicon.for_memory(Memory()).match("napsat", "stvořit") is None  # bez paměti nic
    r2 = s.say("!uč vydat ~ napsat")
    assert "related" in r2.text
    assert "užití" in s.say("!uč nesmysl").text


def test_prekryv_command(s: Session) -> None:
    """`!uč překryv a => b` (krok 2) — vlastní slovo v příkazu, ne symbol
    (nese modalitu `možnost`, kterou mini-jazyk `parse_teach` neumí)."""
    from cb6.lexicon import Lexicon
    r = s.say("!uč překryv bydlet => setkat_se")
    assert "naučeno lex:said:" in r.text and "možnost" in r.text
    link = Lexicon.for_memory(s.memory).overlap_rules_by_target("setkat_se")
    assert len(link) == 1 and link[0].args == ("bydlet", "setkat_se") and link[0].modality == "možnost"


def test_quantifier_fix(s: Session) -> None:
    s.say("Ptáci létají.")
    a = s.say("Ne každý pták.")
    assert "∀ → ∃" in s.memory.statements["s0001"].defaults[-1]
    s.say("Tučňák je pták.")
    assert s.say("Létá tučňák?").verdict.value == "NEVÍM"  # type: ignore[union-attr]


def test_recall_returns_related(s: Session) -> None:
    s.say("Alois Jirásek se narodil ve východočeském Hronově u Náchoda.")
    s.say("Jirásek zemřel v Praze.")
    jir = s.memory.find_entity(["Jirásek"])[0]
    got = recall(s.memory, [jir.id], 2)
    assert len(got) == 2 and {g.pred for g in got} == {"narodit_se", "zemřít"}


def test_program_save_load_and_graph(s: Session, tmp_path: Path) -> None:
    s.say("Jezevčík je pes.")
    assert "s0001" in s.say("!program").text
    assert "uloženo" in s.say(f"!ulož {tmp_path / 'm.json'}").text
    s2 = Session(Memory.load(tmp_path / "m.json"), RecordedOracle(DATA))
    assert s2.say("Je jezevčík pes?").verdict.value == "ANO"  # type: ignore[union-attr]
    assert "uzlů" in s.say(f"!graf {tmp_path / 'g.json'}").text


def test_replay_gives_same_program(s: Session) -> None:
    s.ingest("Alois Jirásek se narodil ve východočeském Hronově u Náchoda.\nCelý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.", "alois_jirásek")
    s.say("Petr bydlí v Praze.")
    s.say("Ne, Petr bydlí v Brně.")
    s.say("Kde bydlí Petr?")
    s.say("!role do+Gen = kam")
    again = Session.replay(s.journal_json(), RecordedOracle(DATA))
    assert again.memory.program() == s.memory.program()
    assert again.memory.to_json()["statements"] == s.memory.to_json()["statements"]
