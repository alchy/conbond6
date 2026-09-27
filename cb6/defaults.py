"""Výchozí volby čtení jako DATA (spec § 2/3, § 5) — jazyk zvenčí, kód beze změny.

Proč zvláštní modul: tohle je přesně to, co conbond4 odmítal rozhodnout bez
člověka („v+Loc není v osivu, aby se systém zeptal“). conbond5 rozhoduje
sám, ale **každou volbu označí** (`authority="default"`) a dialog ji může
přepsat (`!role v+Loc = kde`) nebo odvolat. Nic z toho není zadrátované
v kódu čtení — čtení tabulky jen čte.

Konvence: klíče rolí jsou česká slova (`kde`, `kam`, `kdy`, `kdo`, `co`,
`komu`, `čím`, `s_kým`, `jak`), protože je pak render i otázka „kde“ čte
stejně; povrchové jméno role je `předložka+Pád` (`v+Loc`) nebo holý pád.
Tyhle klíče jsou opaque jména hran grafu, ne „čeština“ — zůstávají stejné
bez ohledu na jazyk zdroje.

Od 27. 9. 2026 (rozhodnutí J.): samotné tabulky (které povrchové tvary na
tyhle role/kvantifikátory/spojky mapují) žijí jako DATA per jazyk
v `cb6/lang/<kód>.json` (`cb6/lang/__init__.py`), stejně jako vazby
v `cb6/lexicon.py` — NN má dělat strukturu v libovolném jazyce, graf zůstává
jediné místo se znalostí. Tenhle modul jen načte jazyk (dnes `cs`, jediný,
co je) a re‑exportuje tabulky pod stejnými jmény, aby se nemusel měnit
žádný spotřebitel (`read.py`, `triage.py`, `logic.py`).
"""

from __future__ import annotations

from cb6.lang import load_language

_L = load_language("cs")

#: (předložka, Pád) → jméno role podle druhu výplně: `place` / `time` / `*`.
#: Chybí-li klíč, role si nechá povrchové jméno a vznikne otevřená položka.
ROLE_BY_CASE: dict[tuple[str, str], dict[str, str]] = _L.role_by_case

#: Naučené přepisy povrchových jmen rolí (dialog `!role přes+Acc = kudy`)
#: drží PAMĚŤ (`Memory.learned["roles"]`) a čtení je dostane parametrem —
#: žádný globální stav, dvě paměti se nesmějí ovlivnit.

#: Determinátor → kvantifikátor. `∀neg` = „žádný“: ∀ + negace predikace.
DETERMINER_QUANT: dict[str, str] = _L.determiner_quant

#: Přivlastňovací determinátory a zájmena — odkaz na aktivní uzel.
POSSESSIVE: frozenset[str] = _L.possessive

#: Částice a příslovce bez role: neztrácejí se (jsou „particle“), ale
#: nemění strukturu. `ne` se čte jako negace, ne částice.
PARTICLES: frozenset[str] = _L.particles

#: Příslovce pořadí a času, která NEjsou částice: nesou roli.
SEQUENCE_ADVERBS: frozenset[str] = _L.sequence_adverbs

#: Modální slovesa: lemma → druh modality (příznak výroku, ne operátor).
MODAL_VERBS: dict[str, str] = _L.modal_verbs

#: Tázací slovo → (jméno role, druh díry). Druh: `filler` (chce výplň),
#: `count` (chce počet), `attr` (chce vlastnost).
WH: dict[str, tuple[str, str]] = _L.wh

#: Slovesa výpisu v rozkazu („Vyjmenuj všechna díla Karla Čapka.“): věta je otázka
#: druhu `list` (díra omezená skupinou předmětu, volitelně přivlastnění), ne tvrzení.
LIST_VERBS: frozenset[str] = _L.list_verbs

#: Obecná jména míst — výplň v `v+Loc` apod. je pak MÍSTO i bez NameType=Geo.
PLACE_NOUNS: frozenset[str] = _L.place_nouns

#: Předložky, po nichž je PROPN skoro jistě místo (i bez NameType).
PLACE_PREPS: frozenset[str] = _L.place_preps

#: Zájmena, která odkazují (osobní), a jejich rod/číslo pro shodu.
PERSONAL_PRONOUNS: frozenset[str] = _L.personal_pronouns

#: Synonyma predikátů tu už NEJSOU: jsou to znalostní vazby (mění verdikt), a ty
#: žijí jako řádky dat v `cb6/lexikon/*.jsonl` (`cb6/lexicon.py`) — se sílou
#: `same/implies/related` a proveniencí v grafu. Tady zůstávají jen čtecí tabulky.


# ---- triáž (spec conbond6 § 3.3) — tabulky jako data ---------------------------

#: Podmínkové spojky (`advcl` s `mark`) → hlavní klauze není tvrzení, vzniká pravidlo.
#: Hodnota říká, jak spojku číst: `if` = A ⇒ B vždy; `if_or_when` = podmínka jen
#: v prézentu/futuru (v minulém čase je to čas: „Když pršelo, zůstal doma.“).
CONDITIONAL_MARKERS: dict[str, str] = _L.conditional_markers
#: „jen pokud / pouze když“ → obrácený směr (only if): B ⇒ A.
ONLY_IF_ADVERBS: frozenset[str] = _L.only_if_adverbs
#: „právě když / tehdy a jen tehdy, když“ → ekvivalence (oba směry).
IFF_ADVERBS: frozenset[str] = _L.iff_adverbs
#: Spojky vedlejších vět, jejichž obsah text NEtvrdí (účel, přání): jde o obsah, ne o svět.
PURPOSE_MARKS: frozenset[str] = _L.purpose_marks
#: Slovesa postoje / mluvení: vnořený obsah („že …“) je obsah promluvy, ne fakt o světě.
ATTITUDE_VERBS: frozenset[str] = _L.attitude_verbs
#: Souřadné spojky vylučovací → disjunkce (v1 bez prostoru modelů → REJECTED).
DISJUNCTION_CC: frozenset[str] = _L.disjunction_cc
#: Kardinalita („aspoň jeden“, „nejvýše dva“, „právě jeden“) → REJECTED (v1).
CARDINALITY_ADVERBS: frozenset[str] = _L.cardinality_adverbs
