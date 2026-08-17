# Znalostní vazby jako data — synonyma, antonyma, příbuzenství, míry, čas

*Návrhová poznámka (17. 8. 2026). Odpověď na otázku J.: jak přijmout myšlenku
conbond5 „Q(A,B) ⇐ TEST(hodnota u A, hodnota u B)“ tak, aby vazby byly
oddělené od kódu, snadno rozšiřitelné a přitom platily invarianty I‑9…I‑12.
Doplňuje spec `2026-08-17-conbond6-design.md`; nic v ní neruší.*

## 0. Kritický nález: dnes máme čtyři místa, kde „vazby“ žijí

| kde | co | provenience v grafu | rozšíření |
|---|---|---|---|
| `cb6/defaults.py`, `cb6/chronos.py` (Python tabulky) | `SYNONYMS`, `PLACE_NOUNS`, `TIME_NOUNS`, `ROLE_BY_CASE`, `MONTHS`… | **žádná** — důkaz řekne `[synonymum: kázat ~ hlásat]`, ale graf nemá uzel, odkud to je | commit do kódu |
| `Memory.learned` (slovník `roles`, `synonyms`) | `!role`, `!synonymum` | **žádná** — je v JSON paměti, ale ne v exportu grafu; graphcheck ho nevidí | dialog |
| `Memory.rules` (seznam `Rule`) | `!pravidlo jet(kam:X) => být(kde:X)` | částečná (`uses_rule` na id `r…`, ale uzel `r…` v exportu není výrok s proveniencí) | dialog |
| výroky `kind="rule"` (z textu, triáž) | podmínky `pokud/pak` | **úplná** (`source`, `nested_in`, `uses_rule`, `derived_from`) | text |

To je přesně ten „split brain“, na který se J. ptá. Přijmout návrh conbond5
naivně (pátý slovník `learned["tests"]`) by ho prohloubilo. **Cíl integrace
je počet míst snížit na jedno**, ne přidat další.

Druhý nález: `SYNONYMS` je dnes *ekvivalence* (`napsat ~ vydat ~ publikovat`),
ale „vydal knihu“ ≠ „napsal knihu“. To je měřitelný únik precision, který
vznikl tím, že tabulka nezná sílu vazby. Návrh ji zavádí.

## 1. Rozhodnutí: operátory v kódu, vazby v datech, použití v grafu

Tři vrstvy s ostrou hranicí:

1. **Operátory (kód, uzavřená malá množina).** Deterministické funkce nad
   hodnotami a uzly. Nová vazba operátor *nepřidává*, jen ho *používá*.
   ```
   třída        (ekvivalence: symetrická + tranzitivní → reprezentant)      synonyma predikátů, jednotek
   implikace    (jednosměrná: p ⇒ q; q se ptá, p odpovídá)                    napsat ⇒ vytvořit; role kam ⇒ kde
   protiklad    (symetrická; komplementární = negace, kontrérní = jen NE)      velký × malý; živý × mrtvý
   inverze      (r(a,b) ⇔ r⁻¹(b,a); s rodem)                                   rodič ↔ dítě; bratr/sestra ↔ sourozenec
   skládání     (r∘s ⇒ t)                                                      bratr∘rodič ⇒ strýc; rodič∘rodič ⇒ prarodič
   podřazení    (x ⊆ y, tranzitivní)                                            město ⊆ sídlo; km ⊆ jednotka délky
   překryv      (intervaly na téže ose se protínají)                           žít.kdy × žít.kdy ⇒ potkat_se (možnost)
   porovnání    (≤ ≥ = rozdíl na téže dimenzi, po převodu jednotek)           délka(A) ≤ délka(B) ⇒ vejít_se; „delší než“
   ```
   Osm operátorů pokryje vše, co J. jmenuje (synonyma, antonyma, rodinné
   vztahy, míry, váhy, čas). Čas už operátory má (`before`, `within` v
   chronosu) — přidá se `overlap`; míry a váhy jsou *jedna* věc: veličina
   = (hodnota, jednotka → dimenze).
2. **Vazby (data, jeden řádkový formát).** Každá vazba je jeden řádek:
   ```json
   {"id": "lex:syn:0042", "op": "třída", "args": ["kázat", "hlásat"], "síla": "same",
    "autorita": "seed", "zdroj": "cb6/lexikon/synonyma.jsonl#42", "pozn": "…"}
   ```
   - `op` = jeden z osmi operátorů; `args` = predikáty / lemmata / role /
     jednotky / osy podle operátoru.
   - `síla`: `same` (zaměnitelné ve verdiktu), `implies` (jednosměrné),
     `related` (jen pro recall/nápovědu, **nikdy ve verdiktu**). Většina
     dnešních `SYNONYMS` půjde do `implies`/`related`, ne `same`.
   - `autorita`: `seed` (soubory v repu, verzované), `said` (`!uč` v dialogu,
     tah), `read` (věta typu „X je synonymum Y“, „A je bratr B“ — vazba i
     fakt), `derived` (složená vazba). Přesně vrstvy 0–3 z conbond5, jen jako
     atribut, ne jako architektura.
   - `zdroj`: soubor+řádek / věta / tah — bez zdroje řádek neexistuje.
   Formát je pro seed i pro dialog **stejný**: `!uč` jen zapíše řádek
   s `autorita=said` do paměti; `Memory.learned` a `Memory.rules` zanikají
   (převedou se na řádky). Import/export souboru řádků je triviální.
3. **Použití (graf).** Řádek se **materializuje do grafu líně**: v okamžiku,
   kdy ho verdikt nebo `derive()` použije, vznikne uzel `kind="vazba"` s
   atributy řádku a hrana `uses_rule` z odvozeného výroku / kroku důkazu.
   Nepoužité seed řádky graf nezatěžují (tisíce synonym by zničily čitelnost
   i „osiřelost“ v graphchecku); použité jsou v exportu s proveniencí až na
   soubor a řádek. Deterministické (stejný text → stejné použité řádky).

Odpověď na hlavní otázku J.: **oddělení od kódu** = nová vazba je řádek,
nikdy Python (Python se sahá jen na nový *operátor*, což má být výjimka a
má se zdůvodnit v HYPOTEZY); **rozšiřitelnost** = tentýž řádek napíše člověk
do souboru, dialog přes `!uč`, nebo čtení z generické věty; **provenience**
= graf ukáže, který řádek a odkud verdikt použil.

## 2. Co se z návrhu conbond5 přebírá a co se mění

Přebírá se: pravidlo jako datový řádek místo prózy; nabídka šablony jen
když oba operandy existují (`potkat_se(A,B)` → oba mají `žít.kdy`);
odpověď s řetězem premis. Mění se:

- **Modalita do řádku.** `překryv` odvozuje *možnost* (`potkat_se` = mohli),
  ne skutečnost; řádek nese `modalita: možnost`, aby „Potkali se?“ zůstalo
  NEVÍM a „Mohli se potkat?“ dalo ANO/NE. Nepřekryv ⇒ NE je silné a správné.
- **Přiznaný zjednodušující předpoklad.** `vejít_se ⇐ délka ≤` je pravidlo
  jen o jedné dimenzi; kladný verdikt nese výchozí volbu „porovnání jen délky
  (řekls to, tah N)“; záporný je jistý.
- **Uzel v grafu, ne slovník.** Viz § 1.3; jinak I‑11/I‑12 padnou.
- **Test i sílu měří bench**, ne rozum: každý odvozený výrok jde do auditu
  zvlášť (rozklad podle `grade=derived` a podle `op`).

## 3. Kde je riziko a co ho hlídá

| riziko | hlídač |
|---|---|
| ontologický plíživý růst (víc řádků → víc odpovědí → víc nepodložených) | každý přírůstek řádků je tah s číslem; audit má rozklad podle `op` a `autorita`; `bench run --bez-lexikonu` = ablace seed vrstvy (musí být vidět, co seed přináší) |
| `same` tam, kde je jen `implies` (dnešní `SYNONYMS`) | migrace tabulky do řádků *snižuje* sílu na `implies`, kde není jistá zaměnitelnost; číslo před/po |
| skládání příbuzenství generuje fakta, která text neřekl (strýc z bratr∘rodič) | odvozené jsou `derived` s `uses_rule`; nikdy `read`; soudce dostává premisy + řádek; do yieldu se nepočítají |
| kontrérní antonymum vyhodnoceno jako komplementární („není velký“ ⇒ „malý“) | operátor `protiklad` má dva režimy, řádek musí říct který; výchozí je kontrérní (jen NE, nikdy ANO) |
| převody jednotek a zaokrouhlení | výsledek je `derived` s krokem „převod km→m ×1000 (lex:jed:…)“, hodnota nezaokrouhlená, prezentace ano |
| druhý jazyk pro pravidla (past conBond3: politika > kód) | žádný výrazový jazyk: jen 8 operátorů a řádky; když nestačí, je to hypotéza pro nový operátor, ne DSL |

## 4. Pořadí tahů (každý s hypotézou a číslem)

1. **Formát + načítání + `třída`/`implikace`** — `cb6/lexicon.py` (loader,
   materializace, `!uč` zápis), `cb6/lexikon/synonyma.jsonl` migrací
   `SYNONYMS` se sílou; `Memory.learned["synonyms"]` → řádky `said`.
   Hypotéza: QA beze změny, unsupported hlavních predikací neroste (spíš klesne
   o `vydat≠napsat`), graf ukáže `uses_rule` na `lex:` uzly, graphcheck 0.
2. **`překryv` + `porovnání` + veličiny** (hodnota, jednotka, dimenze;
   `!uč překryv …`, `!uč porovnání …`; „Jaká je délka …?“, „Je A delší než B?“,
   „Mohli se potkat?“). Hypotéza: etalon 14/32 → ≥ 18/32 (otázky na veličiny),
   unsupported hlavních beze změny.
3. **`inverze` + `skládání` pro příbuzenství** spolu s nálezem G‑3 (přístavek
   „jeho bratr Josef Čapek“ → `bratr(Josef, Karel)`), řádky `vztahy.jsonl`.
   Hypotéza: nové QA „Kdo byl bratr K. Č.?“; derived unsupported měřen zvlášť.
4. **`protiklad`** (antonyma, dva režimy) — až bude v gold sadě otázka, která
   ho potřebuje; jinak zůstává řádek bez uplatnění (nekódovat dopředu).
5. `Memory.rules` (můstky) → řádky `implikace` s mapou rolí; `ROLE_BY_CASE`,
   `PLACE_NOUNS`, `TIME_NOUNS`, `MONTHS` → řádky `podřazení`/třídy jen tehdy,
   když se ukáže, že je někdo chce rozšiřovat bez kódu (zatím se nemění —
   nejsou to znalostní vazby, ale čtecí tabulky; hranice: *co mění verdikt*
   patří do lexikonu, *co mění čtení* zůstává v `defaults.py`).

## 5. Co se nemění

Čtení (UDPipe + `read.py`), triáž, statusy `SAFE/HYPOTHESIS/REJECTED`,
`derive()` jako pevný bod, bench jako brána. Lexikon je další zdroj
řádků pro tutéž logiku, ne nová logika.
