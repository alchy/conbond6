"""Výchozí volby čtení jako DATA (spec § 2/3, § 5).

Proč zvláštní modul: tohle je přesně to, co conbond4 odmítal rozhodnout bez
člověka („v+Loc není v osivu, aby se systém zeptal“). conbond5 rozhoduje
sám, ale **každou volbu označí** (`authority="default"`) a dialog ji může
přepsat (`!role v+Loc = kde`) nebo odvolat. Nic z toho není zadrátované
v kódu čtení — čtení tabulky jen čte.

Konvence: klíče rolí jsou česká slova (`kde`, `kam`, `kdy`, `kdo`, `co`,
`komu`, `čím`, `s_kým`, `jak`), protože je pak render i otázka „kde“ čte
stejně; povrchové jméno role je `předložka+Pád` (`v+Loc`) nebo holý pád.
"""

from __future__ import annotations

#: (předložka, Pád) → jméno role podle druhu výplně: `place` / `time` / `*`.
#: Chybí-li klíč, role si nechá povrchové jméno a vznikne otevřená položka.
ROLE_BY_CASE: dict[tuple[str, str], dict[str, str]] = {
    ("v", "Loc"): {"place": "kde", "time": "kdy", "duration": "kdy", "*": "v+Loc"},
    ("v", "Acc"): {"time": "kdy", "*": "v+Acc"},
    ("na", "Loc"): {"place": "kde", "time": "kdy", "*": "na+Loc"},
    ("na", "Acc"): {"place": "kam", "*": "na+Acc"},
    ("do", "Gen"): {"place": "kam", "time": "do_kdy", "*": "do+Gen"},
    ("z", "Gen"): {"place": "odkud", "time": "od_kdy", "*": "z+Gen"},
    ("od", "Gen"): {"place": "odkud", "time": "od_kdy", "*": "od+Gen"},
    ("k", "Dat"): {"place": "kam", "*": "k+Dat"},
    ("u", "Gen"): {"place": "kde", "*": "u+Gen"},
    ("s", "Ins"): {"*": "s_kým"},
    ("o", "Loc"): {"*": "o_čem"},
    ("o", "Acc"): {"*": "o+Acc"},
    ("po", "Loc"): {"place": "kudy", "time": "po_kdy", "*": "po+Loc"},
    ("před", "Ins"): {"place": "kde", "time": "před_kdy", "*": "před+Ins"},
    ("za", "Gen"): {"time": "kdy", "*": "za+Gen"},
    ("za", "Ins"): {"place": "kde", "*": "za+Ins"},
    ("během", "Gen"): {"time": "kdy", "duration": "kdy", "*": "během+Gen"},
    ("po", "Acc"): {"duration": "jak_dlouho", "time": "jak_dlouho", "*": "po+Acc"},
    ("za", "Acc"): {"time": "kdy", "duration": "jak_dlouho", "*": "za+Acc"},
    ("mezi", "Ins"): {"place": "kde", "time": "kdy", "*": "mezi+Ins"},
    ("přes", "Acc"): {"place": "kudy", "*": "přes+Acc"},
    ("kolem", "Gen"): {"time": "kdy", "place": "kde", "*": "kolem+Gen"},
    ("okolo", "Gen"): {"time": "kdy", "place": "kde", "*": "okolo+Gen"},
    ("při", "Loc"): {"time": "kdy", "*": "při+Loc"},
    ("nad", "Ins"): {"place": "kde", "*": "nad+Ins"},
    ("pod", "Ins"): {"place": "kde", "*": "pod+Ins"},
    ("vedle", "Gen"): {"place": "kde", "*": "vedle+Gen"},
    ("uvnitř", "Gen"): {"place": "kde", "*": "uvnitř+Gen"},
    ("blízko", "Gen"): {"place": "kde", "*": "blízko+Gen"},
    ("pro", "Acc"): {"*": "pro_koho"},
    ("bez", "Gen"): {"*": "bez+Gen"},
    ("podle", "Gen"): {"*": "podle+Gen"},
    ("proti", "Dat"): {"*": "proti+Dat"},
    ("díky", "Dat"): {"*": "díky+Dat"},
    ("kvůli", "Dat"): {"*": "kvůli+Dat"},
    ("jako", ""): {"*": "jako"},
    ("", "Ins"): {"*": "čím"},
    ("", "Dat"): {"*": "komu"},
    ("", "Gen"): {"time": "kdy", "duration": "jak_dlouho", "*": "čeho"},
    ("", "Acc"): {"time": "kdy", "duration": "jak_dlouho", "*": "obl:Acc"},
    ("", "Loc"): {"place": "kde", "time": "kdy", "*": "obl:Loc"},
    ("", "Nom"): {"*": "obl:Nom"},
}

#: Naučené přepisy povrchových jmen rolí (dialog `!role přes+Acc = kudy`)
#: drží PAMĚŤ (`Memory.learned["roles"]`) a čtení je dostane parametrem —
#: žádný globální stav, dvě paměti se nesmějí ovlivnit.

#: Determinátor → kvantifikátor. `∀neg` = „žádný“: ∀ + negace predikace.
DETERMINER_QUANT: dict[str, str] = {
    "každý": "∀", "všechen": "∀", "všechno": "∀", "veškerý": "∀", "kterýkoli": "∀",
    "žádný": "∀neg", "nikdo": "∀neg", "nic": "∀neg",
    "ten": "·", "tento": "·", "tenhle": "·", "onen": "·", "tamten": "·",
    "nějaký": "∃", "některý": "∃", "jeden": "∃", "jistý": "∃", "leckterý": "∃",
    "mnohý": "∃", "několik": "∃", "málokterý": "∃",
}

#: Přivlastňovací determinátory a zájmena — odkaz na aktivní uzel.
POSSESSIVE = frozenset({"jeho", "její", "jejich", "můj", "tvůj", "náš", "váš", "svůj"})

#: Částice a příslovce bez role: neztrácejí se (jsou „particle“), ale
#: nemění strukturu. `ne` se čte jako negace, ne částice.
PARTICLES = frozenset(
    {"také", "též", "taky", "i", "jen", "pouze", "už", "již", "ještě", "asi", "prý",
     "však", "ale", "tedy", "totiž", "například", "zejména", "hlavně", "především",
     "přece", "snad", "přitom", "vůbec", "právě", "zase", "opět", "spíše", "spíš",
     "dokonce", "možná", "vlastně", "prostě", "ovšem", "sice", "zřejmě", "patrně",
     "pravděpodobně", "často", "obvykle", "většinou", "zpravidla", "někdy", "vždy",
     "nikdy", "stále", "pořád", "dále", "dál", "tak", "také", "ano", "ne", "nikoli", "nikoliv"}
)

#: Příslovce pořadí a času, která NEjsou částice: nesou roli.
SEQUENCE_ADVERBS = frozenset(
    {"nejprve", "nejdřív", "nejdříve", "poté", "pak", "potom", "později", "nakonec",
     "tehdy", "kdysi", "dříve", "dřív", "následně", "posléze", "mezitím", "současně",
     "zároveň", "brzy", "záhy", "hned", "ihned", "okamžitě", "nedávno", "dosud", "doposud"}
)

#: Modální slovesa: lemma → druh modality (příznak výroku, ne operátor).
MODAL_VERBS: dict[str, str] = {
    "moci": "možnost", "smět": "možnost", "lze": "možnost", "dokázat": "možnost",
    "umět": "možnost", "muset": "nutnost", "mít": "povinnost", "chtít": "vůle",
    "hodlat": "vůle", "začít": "fáze", "začínat": "fáze", "přestat": "fáze",
    "pokračovat": "fáze", "snažit_se": "vůle", "pokusit_se": "vůle",
}

#: Tázací slovo → (jméno role, druh díry). Druh: `filler` (chce výplň),
#: `count` (chce počet), `attr` (chce vlastnost).
WH: dict[str, tuple[str, str]] = {
    "kde": ("kde", "filler"), "kam": ("kam", "filler"), "odkud": ("odkud", "filler"),
    "kudy": ("kudy", "filler"), "kdy": ("kdy", "filler"), "odkdy": ("od_kdy", "filler"),
    "dokdy": ("do_kdy", "filler"), "kdo": ("kdo", "filler"), "co": ("co", "filler"),
    "koho": ("co", "filler"), "komu": ("komu", "filler"), "čím": ("čím", "filler"),
    "kolik": ("count", "count"), "jaký": ("jaký", "attr"), "který": ("který", "attr"),
    "proč": ("advcl:protože", "filler"), "čí": ("čí", "filler"), "jak": ("jak", "filler"),
    "jak_dlouho": ("jak_dlouho", "filler"),
}

#: Obecná jména míst — výplň v `v+Loc` apod. je pak MÍSTO i bez NameType=Geo.
PLACE_NOUNS = frozenset(
    {"město", "vesnice", "ves", "obec", "země", "stát", "říše", "království", "kraj",
     "oblast", "region", "provincie", "okres", "čtvrť", "ulice", "náměstí", "řeka",
     "hora", "pohoří", "ostrov", "moře", "oceán", "jezero", "les", "pole", "louka",
     "škola", "gymnázium", "univerzita", "fakulta", "akademie", "ústav", "institut",
     "kavárna", "hospoda", "dům", "byt", "vila", "zámek", "hrad", "klášter", "kostel",
     "divadlo", "nemocnice", "továrna", "závod", "podnik", "kancelář", "redakce",
     "dálnice", "silnice", "cesta", "most", "nádraží", "letiště", "přístav", "vězení",
     "tábor", "fronta", "kontinent", "světadíl", "svět", "vesmír", "domov", "exil",
     "emigrace", "zahraničí", "venkov", "centrum", "střed", "okraj", "sever", "jih",
     "východ", "západ", "Evropa", "Amerika", "Asie", "Afrika"}
)

#: Předložky, po nichž je PROPN skoro jistě místo (i bez NameType).
PLACE_PREPS = frozenset({"v", "do", "z", "u", "na", "k", "od", "přes", "po", "za", "mezi", "nad", "pod", "vedle", "před", "kolem", "okolo"})

#: Zájmena, která odkazují (osobní), a jejich rod/číslo pro shodu.
PERSONAL_PRONOUNS = frozenset({"on", "ona", "ono", "oni", "ony", "já", "ty", "my", "vy", "sebe"})

#: Synonyma predikátů tu už NEJSOU: jsou to znalostní vazby (mění verdikt), a ty
#: žijí jako řádky dat v `cb6/lexikon/*.jsonl` (`cb6/lexicon.py`) — se sílou
#: `same/implies/related` a proveniencí v grafu. Tady zůstávají jen čtecí tabulky.


# ---- triáž (spec conbond6 § 3.3) — tabulky jako data ---------------------------

#: Podmínkové spojky (`advcl` s `mark`) → hlavní klauze není tvrzení, vzniká pravidlo.
#: Hodnota říká, jak spojku číst: `if` = A ⇒ B vždy; `if_or_when` = podmínka jen
#: v prézentu/futuru (v minulém čase je to čas: „Když pršelo, zůstal doma.“).
CONDITIONAL_MARKERS: dict[str, str] = {
    "pokud": "if", "jestliže": "if", "li": "if", "-li": "if", "kdyby": "if", "pakliže": "if", "když": "if_or_when",
}
#: „jen pokud / pouze když“ → obrácený směr (only if): B ⇒ A.
ONLY_IF_ADVERBS = frozenset({"jen", "pouze", "jenom"})
#: „právě když / tehdy a jen tehdy, když“ → ekvivalence (oba směry).
IFF_ADVERBS = frozenset({"právě"})
#: Spojky vedlejších vět, jejichž obsah text NEtvrdí (účel, přání): jde o obsah, ne o svět.
PURPOSE_MARKS = frozenset({"aby", "ať", "kéž"})
#: Slovesa postoje / mluvení: vnořený obsah („že …“) je obsah promluvy, ne fakt o světě.
ATTITUDE_VERBS = frozenset({
    "říci", "říkat", "tvrdit", "prohlásit", "prohlašovat", "myslet", "myslit", "věřit", "doufat", "domnívat_se",
    "předpokládat", "slíbit", "slibovat", "napsat", "psát", "uvést", "uvádět", "oznámit", "oznamovat", "sdělit",
    "vysvětlit", "vysvětlovat", "dodat", "odpovědět", "zeptat_se", "ptát_se", "tvrdívat", "soudit", "cítit",
    "chtít", "přát_si", "obávat_se", "bát_se", "očekávat", "navrhnout", "navrhovat", "žádat", "požadovat",
    "rozhodnout", "rozhodnout_se", "znemožnit", "umožnit", "dovolit", "zakázat", "nařídit", "doporučit",
    "plánovat", "hodlat", "snažit_se", "pokusit_se", "zdát_se", "vypadat", "považovat", "pokládat",
})
#: Souřadné spojky vylučovací → disjunkce (v1 bez prostoru modelů → REJECTED).
DISJUNCTION_CC = frozenset({"nebo", "anebo", "či", "buď"})
#: Kardinalita („aspoň jeden“, „nejvýše dva“, „právě jeden“) → REJECTED (v1).
CARDINALITY_ADVERBS = frozenset({"aspoň", "alespoň", "nejvýše", "nanejvýš", "nejméně", "minimálně", "maximálně", "přinejmenším"})
