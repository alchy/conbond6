"""Triáž: čtení → rozhodnutí o statusu každé predikace (spec conbond6 § 3.3).

Proč zvláštní krok: `read.py` poctivě přečte *strukturu* věty — ale ne
každá struktura je tvrzení o světě. „Karel přijde, pokud přijde Jana.“ není
tvrzení, že Karel přijde; „Petr řekl, že Marie přijde.“ netvrdí, že Marie
přijde; fráze „Manifest českých spisovatelů“ netvrdí nic; „Petr nebo Jana
přijde.“ jádro v1 neumí (bez prostoru modelů) a nesmí si vybrat význam kvůli
počtu (I‑8). Precision audit conbond5 (17. 8.) ukázal, že přesně tyhle
struktury tvořily většinu „nepodložených“ výroků.

Triáž je **tabulka jako data** (`defaults.py`: `CONDITIONAL_MARKERS`,
`ATTITUDE_VERBS`, `PURPOSE_MARKS`, `DISJUNCTION_CC`, `CARDINALITY_ADVERBS`)
a rozhoduje pro každou predikaci `claim` (`SAFE` / `HYPOTHESIS` / `REJECTED`)
a `mood` (`assert` / `pattern` / `reported`); u podmínek staví pravidlo.

Vstup: `Reading` (+ jeho `Parse` kvůli spojkám). Výstup: `Triaged` — mapa
`id(predication) → Decision` a případné pravidlo. Zakotvení (`ground.py`)
rozhodnutí jen provede; nic tu nevzniká v paměti.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cb6 import defaults as D
from cb6.memory import Claim, Mood
from cb6.read import Predication, Reading, RoleFill


@dataclass
class Decision:
    """Rozhodnutí o jedné predikaci."""

    claim: Claim = "SAFE"
    mood: Mood = "assert"
    reason: str = ""
    #: poznámky do `Statement.defaults` (výchozí volby triáže, viditelné v grafu)
    defaults: list[str] = field(default_factory=list)


@dataclass
class Rule:
    """Podmínka z textu: `if cond then cons` (u `only_if` obráceně, u `iff` obojí)."""

    kind: str  # if | only_if | iff
    cond: Predication
    cons: Predication
    marker: str


@dataclass
class Triaged:
    """Výsledek triáže jednoho čtení."""

    reading: Reading
    decisions: dict[int, Decision] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def decision(self, p: Predication) -> Decision:
        """Rozhodnutí pro predikaci (výchozí `SAFE`/`assert`, když triáž nic neřekla)."""
        return self.decisions.setdefault(id(p), Decision())


def _marker_of(role: RoleFill) -> str:
    """`advcl:pokud` → `pokud`; jiné role → ""."""
    if role.name.startswith("advcl:"):
        return role.name.split(":", 1)[1]
    return ""


def _conditional_kind(reading: Reading, main: Predication, role: RoleFill) -> str | None:
    """Je vedlejší věta v této roli podmínková? Vrátí `if` / `only_if` / `iff` / None."""
    marker = _marker_of(role)
    how = D.CONDITIONAL_MARKERS.get(marker)
    if how is None or role.nested is None:
        return None
    if how == "if_or_when":
        # „když“ v minulém čase (hlavní i vedlejší) je čas, ne podmínka
        if main.tense == "Past" or role.nested.tense == "Past":
            return None
    # jen/pouze/právě před spojkou (advmod:emph na hlavě vedlejší věty)
    head = role.nested.head
    parse = reading.parse
    for t in parse.tokens:
        if t.head == head and t.deprel.startswith("advmod") and t.lemma in D.IFF_ADVERBS:
            return "iff"
        if t.head == head and t.deprel.startswith("advmod") and t.lemma in D.ONLY_IF_ADVERBS:
            return "only_if"
    return "if"


def _has_disjunction(reading: Reading) -> bool:
    """Souřadná spojka vylučovací kdekoli ve větě (v1 hrubě: celá věta)."""
    return any(t.deprel == "cc" and t.lemma in D.DISJUNCTION_CC for t in reading.parse.tokens)


def _has_cardinality(reading: Reading) -> bool:
    return any(t.deprel.startswith("advmod") and t.lemma in D.CARDINALITY_ADVERBS for t in reading.parse.tokens)


def _walk(p: Predication):
    """Všechny predikace čtení: hlavní, vnořené (role.nested) i vedlejší (secondary)."""
    yield p
    for r in p.roles:
        if r.nested is not None:
            yield from _walk(r.nested)
    for s in p.secondary:
        yield from _walk(s)


def triage(reading: Reading) -> Triaged:
    """Rozhodni statusy predikací jednoho čtení.

    Pravidla (v pořadí):
    1. disjunkce / kardinalita ve větě → hlavní predikace `REJECTED`
       („disjunkce bez prostoru modelů“), vnořené a vedlejší také;
    2. podmínková spojka u vedlejší věty → hlavní klauze není tvrzení:
       vznikne pravidlo, hlavní i vedlejší dostanou `mood="pattern"`;
    3. vnořená predikace v roli `co`/`kdo` (ccomp/xcomp) → `mood="reported"`
       (obsah, ne fakt o světě) — u postojových sloves i u ostatních;
       vedlejší věta s `aby/ať` → `reported`;
    4. vedlejší `nmod` s povrchovou rolí → `REJECTED` („vedlejší vztah bez
       sémantiky“) — fráze není tvrzení; `appos` bez jádra `member`/`same_as`
       také;
    5. jinak `SAFE`/`assert`.

    Args:
        reading: výsledek `read()`.
    Returns:
        `Triaged` s rozhodnutími pro každou predikaci a případnými pravidly.
    """
    t = Triaged(reading)
    main = reading.main
    if main.mood == "question":
        return t

    if _has_disjunction(reading) or _has_cardinality(reading):
        why = "disjunkce bez prostoru modelů" if _has_disjunction(reading) else "kardinalita bez prostoru modelů"
        for p in _walk(main):
            t.decisions[id(p)] = Decision("REJECTED", "assert", why)
        t.notes.append(why)
        return t

    # 2. podmínky
    for role in list(main.roles):
        kind = _conditional_kind(reading, main, role)
        if kind is None or role.nested is None:
            continue
        cond = role.nested
        cons = Predication(main.pred, main.kind, main.neg, main.modality, main.kernel,
                           [r for r in main.roles if r is not role], "assert", main.head, main.tokens,
                           list(main.defaults), [], main.tense, main.correction, main.pred_role_name)
        t.rules.append(Rule(kind, cond, cons, _marker_of(role)))
        t.decisions[id(main)] = Decision("SAFE", "pattern", "", [f"podmínka: {_marker_of(role)} → pravidlo ({kind})"])
        t.decisions[id(cond)] = Decision("SAFE", "pattern", "")
        t.decisions[id(cons)] = Decision("SAFE", "pattern", "")
        if D.CONDITIONAL_MARKERS.get(_marker_of(role)) == "if_or_when":
            t.notes.append("„když“ čteno jako podmínka [výchozí]")
        t.notes.append(f"pravidlo {kind}")

    # 3. vnořený obsah
    for p in _walk(main):
        for r in p.roles:
            if r.nested is None:
                continue
            marker = _marker_of(r)
            if marker and D.CONDITIONAL_MARKERS.get(marker) is not None and id(r.nested) in t.decisions:
                continue  # podmínka už rozhodnuta
            if r.name in ("co", "kdo") or marker in D.PURPOSE_MARKS:
                d = t.decision(r.nested)
                if d.mood == "assert":
                    d.mood = "reported"
                    d.defaults.append(f"obsah predikátu „{p.pred}“ — není tvrzení o světě" if r.name in ("co", "kdo") else f"vedlejší věta „{marker}“ — účel/přání, ne tvrzení")
                for q in _walk(r.nested):
                    if q is not r.nested:
                        dq = t.decision(q)
                        if dq.mood == "assert":
                            dq.mood = "reported"

    # 4. vedlejší vztahy
    for p in _walk(main):
        for s in p.secondary:
            if s.kind == "nmod":
                # výjimka: místo uvnitř fráze („gymnázium v Broumově“ → gymnázium je v Broumově)
                # je čitelné tvrzení s výchozí volbou; ostatní nmod jsou fráze bez sémantiky
                co = s.role("co")
                if s.pred in ("nmod:v+Loc", "nmod:na+Loc", "nmod:u+Gen", "nmod:ve+Loc") and co and co.terms and all(x.kind == "place" for x in co.terms):
                    t.decisions[id(s)] = Decision("SAFE", "assert", "", ["místo uvnitř fráze [výchozí]: X v místě → X je v místě"])
                    continue
                t.decisions[id(s)] = Decision("REJECTED", "assert", f"vedlejší vztah bez sémantiky ({s.pred or 'nmod'})")
            elif s.kind == "appos" and s.kernel not in ("member", "same_as", "name"):
                t.decisions[id(s)] = Decision("REJECTED", "assert", "přístavek bez jádra")
    return t
