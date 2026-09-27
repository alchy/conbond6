"""Bench: pokročilost „chápání vazeb“ (lexikon) podle MECHANISMU, ne jedním číslem.

Proč (J. 27. 9. 2026): „nastav měření pro NN heuristiku, aby šlo měřit
pokročilost strategie chápání vazeb z grafových dat a příkazů a cíleně
určit směr rozvoje projektu.“ Jedno číslo („kolik vazeb systém zná“) by
schovalo ODKUD vazba přišla — a právě to je teď sporné (J.: „vše z kontextu
diskuse, bez příkazu, bez klíčových slov“). Tenhle bench proto řadí každou
zlatou úlohu k mechanismu a vykazuje je ZVLÁŠŤ — číslo pro každý mechanismus
řekne přesně, kam vývoj cílit (nejnižší skóre = největší mezera).

Mechanismy (`zdroj`), od nejvíc k nejmíň „command‑like“:
    prikaz   — explicitní `!uč` (debug/fallback kanál, krok 1, 17. 8. 2026)
    veta     — deklarativní věta s klíčovým slovem („X je synonymum Y“,
               27. 9. 2026) — pořád klíčové slovo, jen ne příkaz; J. ho
               chce časem nahradit, ne jím skončit
    korekce  — oprava v dialogu („Ne, X namísto Y“ o TÉMŽ predikátu) má
               naučit vazbu mezi starým a novým predikátem — CÍL, dnes 0
    graf     — vzorec ve grafu (dvě věty, stejné role/termy, jiný predikát)
               → hypotéza vazby bez jakékoli věty o samotné vazbě — CÍL, dnes 0

Běží hermeticky (bez UDPipe): případy „veta“/„korekce“/„graf“ mají ručně
sestavený rozbor — stejná poctivost jako `tests/test_lex_teach.py` (viz
`mereni/HYPOTEZY.md` 2026‑09‑27 proč ne nespolehlivý náhradní parser).
Spustit: `python -m bench vazby`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import Parse, Token


def _t(index: int, form: str, lemma: str, upos: str, head: int, deprel: str,
       feats: tuple[tuple[str, str], ...] = ()) -> Token:
    return Token(index, form, lemma, upos, head, deprel, feats)


class _DictOracle:
    """Vrací ruční rozbor podle přesného textu věty — žádná síť, žádný odhad.
    Neznámou větu odmítne nahlas (`KeyError`), aby se úloha nikdy tiše
    nepřeskočila kvůli překlepu ve zdrojovém textu."""

    def __init__(self, parses: dict[str, Parse]) -> None:
        self._parses = parses

    def parse(self, text: str) -> Parse:
        """Vrať uložený rozbor přesně této věty. Vstup: text. Výstup: `Parse`."""
        return self._parses[text]


_PARSES = {
    # Skutečný UDPipe2 rozbor (tests/data/parses.json) — beze změny, jen sem zkopírovaný,
    # aby bench/ nezávisel na tests/.
    "Petr bydlí v Praze.": Parse("Petr bydlí v Praze.", (
        _t(1, "Petr", "Petr", "PROPN", 2, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(2, "bydlí", "bydlet", "VERB", 0, "root", (("Aspect", "Imp"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"), ("Polarity", "Pos"), ("Tense", "Pres"), ("VerbForm", "Fin"), ("Voice", "Act"))),
        _t(3, "v", "v", "ADP", 4, "case", (("AdpType", "Prep"), ("Case", "Loc"))),
        _t(4, "Praze", "Praha", "PROPN", 2, "obl", (("Case", "Loc"), ("Gender", "Fem"), ("NameType", "Geo"), ("Number", "Sing"))),
        _t(5, ".", ".", "PUNCT", 2, "punct", ()),
    ), "udpipe2 (zkopírováno z tests/data/parses.json)"),
    # Ručně sestaveno: stejná stavba jako výše, jen sloveso "žít" místo "bydlet" —
    # ověřeno křížově proti skutečnému "Petr žil v Praze." v tests/data/parses.json.
    "Ne, Petr žil v Praze.": Parse("Ne, Petr žil v Praze.", (
        _t(1, "Ne", "ne", "PART", 4, "advmod:emph", ()),  # tvar+pozice ze skutečného "Ne, Petr bydlí v Brně."
        _t(2, ",", ",", "PUNCT", 1, "punct", ()),
        _t(3, "Petr", "Petr", "PROPN", 4, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(4, "žil", "žít", "VERB", 0, "root", (("Aspect", "Imp"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        _t(5, "v", "v", "ADP", 6, "case", (("AdpType", "Prep"), ("Case", "Loc"))),
        _t(6, "Praze", "Praha", "PROPN", 4, "obl", (("Case", "Loc"), ("Gender", "Fem"), ("NameType", "Geo"), ("Number", "Sing"))),
        _t(7, ".", ".", "PUNCT", 4, "punct", ()),
    ), "ruční UD (ověřeno křížově proti skutečnému rozboru) — test, ne UDPipe"),
    "Karel Čapek napsal román Krakatit.": Parse("Karel Čapek napsal román Krakatit.", (
        _t(1, "Karel", "Karel", "PROPN", 3, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(2, "Čapek", "Čapek", "PROPN", 1, "flat", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(3, "napsal", "napsat", "VERB", 0, "root", (("Aspect", "Perf"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        _t(4, "román", "román", "NOUN", 3, "obj", (("Animacy", "Inan"), ("Case", "Acc"), ("Gender", "Masc"), ("Number", "Sing"))),
        _t(5, "Krakatit", "krakatit", "NOUN", 4, "nmod", (("Animacy", "Inan"), ("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
        _t(6, ".", ".", "PUNCT", 3, "punct", ()),
    ), "udpipe2 (zkopírováno z tests/data/parses.json)"),
    # Ručně sestaveno: přesně tatáž stavba, jen "vytvořit" místo "napsat" (obojí VERB, Aspect=Perf).
    "Karel Čapek vytvořil román Krakatit.": Parse("Karel Čapek vytvořil román Krakatit.", (
        _t(1, "Karel", "Karel", "PROPN", 3, "nsubj", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(2, "Čapek", "Čapek", "PROPN", 1, "flat", (("Animacy", "Anim"), ("Case", "Nom"), ("Gender", "Masc"), ("NameType", "Giv"), ("Number", "Sing"))),
        _t(3, "vytvořil", "vytvořit", "VERB", 0, "root", (("Aspect", "Perf"), ("Gender", "Masc"), ("Number", "Sing"), ("Polarity", "Pos"), ("Tense", "Past"), ("VerbForm", "Part"), ("Voice", "Act"))),
        _t(4, "román", "román", "NOUN", 3, "obj", (("Animacy", "Inan"), ("Case", "Acc"), ("Gender", "Masc"), ("Number", "Sing"))),
        _t(5, "Krakatit", "krakatit", "NOUN", 4, "nmod", (("Animacy", "Inan"), ("Case", "Nom"), ("Gender", "Masc"), ("Number", "Sing"))),
        _t(6, ".", ".", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno křížově proti skutečnému rozboru) — test, ne UDPipe"),
    "Bydlet je synonymum žít.": Parse("Bydlet je synonymum žít.", (
        _t(1, "Bydlet", "bydlet", "VERB", 3, "nsubj", (("Aspect", "Imp"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
        _t(2, "je", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"))),
        _t(3, "synonymum", "synonymum", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Neut"), ("Number", "Sing"))),
        _t(4, "žít", "žít", "VERB", 3, "xcomp", (("Aspect", "Imp"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
        _t(5, ".", ".", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno) — test, ne UDPipe/spaCy"),
    # Stejná stavba, jen kopula záporná (Polarity=Neg na "není") — jiné dva
    # slovesné lemma, aby se nepletlo se seed vazbou vydat≁napsat (related, ne same).
    "Vydat není synonymum napsat.": Parse("Vydat není synonymum napsat.", (
        _t(1, "Vydat", "vydat", "VERB", 3, "nsubj", (("Aspect", "Perf"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
        _t(2, "není", "být", "AUX", 3, "cop", (("Tense", "Pres"), ("VerbForm", "Fin"), ("Mood", "Ind"), ("Number", "Sing"), ("Person", "3"), ("Polarity", "Neg"))),
        _t(3, "synonymum", "synonymum", "NOUN", 0, "root", (("Case", "Nom"), ("Gender", "Neut"), ("Number", "Sing"))),
        _t(4, "napsat", "napsat", "VERB", 3, "xcomp", (("Aspect", "Perf"), ("VerbForm", "Inf"), ("Polarity", "Pos"))),
        _t(5, ".", ".", "PUNCT", 3, "punct", ()),
    ), "ruční UD (ověřeno) — test, ne UDPipe/spaCy"),
}


@dataclass
class VazbaCase:
    """Jedna zlatá úloha: scénář (dialog/příkazy) → očekávaná vazba (nebo `None`
    = nic se nemá naučit)."""

    id: str
    zdroj: str  # prikaz | veta | korekce | graf
    popis: str
    run: Callable[[], Memory]
    ocekavano: tuple[str, tuple[str, str], str] | None  # (op, args, síla)


def _run_prikaz(*prikazy: str) -> Callable[[], Memory]:
    def go() -> Memory:
        m = Memory()
        s = Session(m)  # příkazy `!...` nepotřebují orákulum
        for p in prikazy:
            s.say(p)
        return m
    return go


def _run_veta(*vety: str) -> Callable[[], Memory]:
    def go() -> Memory:
        m = Memory()
        s = Session(m, _DictOracle(_PARSES))  # type: ignore[arg-type]
        for v in vety:
            s.say(v)
        return m
    return go


CASES: tuple[VazbaCase, ...] = (
    VazbaCase("prikaz:trida", "prikaz", "!uč a = b (třída/same)",
              _run_prikaz("!uč napsat = stvořit"), ("třída", ("napsat", "stvořit"), "same")),
    VazbaCase("prikaz:implikace", "prikaz", "!uč a => b (implikace/implies)",
              _run_prikaz("!uč bydlet => žít"), ("implikace", ("bydlet", "žít"), "implies")),
    VazbaCase("prikaz:prekryv", "prikaz", "!uč překryv a => b (krok 2, modalita možnost)",
              _run_prikaz("!uč překryv žít => potkat_se"), ("překryv", ("žít", "potkat_se"), "implies")),
    VazbaCase("veta:synonymum_kladne", "veta", "„Bydlet je synonymum žít.“ učí bez příkazu",
              _run_veta("Bydlet je synonymum žít."), ("třída", ("bydlet", "žít"), "same")),
    VazbaCase("veta:synonymum_zaporne", "veta", "„Vydat není synonymum napsat.“ neučí nic (raději nic než obráceně)",
              _run_veta("Vydat není synonymum napsat."), None),
    VazbaCase("korekce:oprava_predikatu", "korekce",
              "„Petr bydlí v Praze.“ + „Ne, Petr žil v Praze.“ — oprava STEJNÉ role jiným predikátem "
              "učí bydlet~žít (síla `related` — opatrně, jedna oprava nestačí na `same`/`implies`)",
              _run_veta("Petr bydlí v Praze.", "Ne, Petr žil v Praze."), ("třída", ("bydlet", "žít"), "related")),
    VazbaCase("graf:parafraze", "graf",
              "„Karel Čapek napsal román Krakatit.“ + „…vytvořil román Krakatit.“ — stejné role kdo+co, "
              "jiný predikát → hypotéza vazby bez věty o vazbě samotné (síla `related`, dvojice seřazená)",
              _run_veta("Karel Čapek napsal román Krakatit.", "Karel Čapek vytvořil román Krakatit."),
              ("třída", ("napsat", "vytvořit"), "related")),
)


def check(case: VazbaCase) -> bool:
    """Splnil scénář očekávání? `None` = žádná (nová) vazba se nesmí objevit.

    Počítá se jen autorita `said`/`read` (nová vazba z TOHOTO scénáře), ne
    `seed` — `bydlet⇒žít` je v seedu od kroku 1 (`implies`), takže případ
    testuje přesně novou, samostatně naučenou vazbu (`same`), ne to, co
    lexikon uměl už předtím (jinak by test „prošel“ i bez nové schopnosti)."""
    m = case.run()
    said_read = {(l.op, l.args, l.strength) for l in m.links.values() if l.authority in ("said", "read")}
    if case.ocekavano is None:
        return not said_read
    return case.ocekavano in said_read


@dataclass
class CaseResult:
    """Výsledek jedné zlaté úlohy (viz `VazbaCase`) po spuštění."""

    id: str
    zdroj: str
    popis: str
    ok: bool


@dataclass
class VazbyReport:
    """Skóre podle mechanismu (`{zdroj: (hits, n)}`) + detail na úlohu."""

    mechanismy: dict[str, tuple[int, int]]
    detail: list[CaseResult]
    celkem: tuple[int, int]


def report() -> VazbyReport:
    """Spusť všechny zlaté úlohy a spočítej skóre podle mechanismu.
    Vstup: nic (bere `CASES`). Výstup: `VazbyReport`."""
    by_zdroj: dict[str, list[bool]] = {}
    detail: list[CaseResult] = []
    for case in CASES:
        ok = check(case)
        by_zdroj.setdefault(case.zdroj, []).append(ok)
        detail.append(CaseResult(case.id, case.zdroj, case.popis, ok))
    by_mech = {z: (sum(v), len(v)) for z, v in by_zdroj.items()}
    return VazbyReport(by_mech, detail, (sum(1 for d in detail if d.ok), len(detail)))


def render(rep: VazbyReport) -> str:
    """Čitelný výpis zprávy (skóre podle mechanismu + detail na úlohu).
    Vstup: `VazbyReport`. Výstup: text."""
    lines = ["vazby — pokročilost chápání podle mechanismu (méně command-like ↓):"]
    for z in ("prikaz", "veta", "korekce", "graf"):
        if z in rep.mechanismy:
            h, n = rep.mechanismy[z]
            lines.append(f"  {z:8s} {h}/{n}")
    for d in rep.detail:
        mark = "✓" if d.ok else "✗"
        lines.append(f"    {mark} [{d.zdroj}] {d.id}: {d.popis}")
    lines.append(f"celkem {rep.celkem[0]}/{rep.celkem[1]}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:  # pragma: no cover — tenká CLI fasáda
    """`python -m bench vazby` — vytiskni zprávu. Vždy vrací 0 (informační bench)."""
    del argv
    print(render(report()))
    return 0  # informační bench, ne brána — korekce/graf jsou cíl vývoje, ne dnešní požadovaný stav


if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(main(sys.argv[1:]))
