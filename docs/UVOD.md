# conbond6 — úvod a orientace v kódu

*Pro koho: pro J. (a pro nové sezení), když už se ve všech principech nedá orientovat z hlavy.
Tohle je mapa: co systém dělá, jak jde věta grafem, co znamenají pojmy, kde co v kódu je a
jak si to pustit. Ukázky ze živého běhu jsou v `docs/UKAZKY.md` (generované, ne opsané —
`python -m bench ukazky`). Proč je to postavené takhle: `docs/KONCEPT.md`. Stav, čísla,
otevřené tahy: `docs/HANDOVER.md`. Zadání a invarianty I‑1…I‑12: spec
`docs/superpowers/specs/2026-08-17-conbond6-design.md`. Pravidla sezení: `CLAUDE.md`.*

---

## 1. Co to je jednou větou

Systém, který **z běžného psaného českého textu získá znalost věrnou zdroji, vysvětlitelnou,
dotazovatelnou a bezpečnou vůči domýšlení — a umí to o sobě změřit.** Paměť je graf a nic než
graf; každá odpověď je rekonstruovatelná jen z exportu grafu; jazykový model není zdroj
znalosti (jen soudce auditu a generátor otázek); a každý tah se měří benchem.

Tři věci, které to odlišují od „další verze motoru“:

1. **Nic se nedomýšlí potichu.** Každá výchozí volba (kdo je „on“, jaká role je `v+Loc`, že
   „ptáci létají“ je obecná věta) je zapsaná u výroku a vypsaná v odpovědi. Když text
   interpretaci neurčuje, výrok je *hypotéza* nebo *zamítnutí s důvodem* — a odpověď to
   řekne, místo aby mlčela nebo lhala.
2. **Důkaz je součást odpovědi.** ANO/NE/NEVÍM nikdy nepřijde bez toho, který výrok, jaká
   věta, jaké kroky (uzávěry, pravidla, vazby) a jaký stupeň (přečteno / řečeno / odvozeno).
   Audit (`bench/graphcheck.py`) ověřuje, že důkaz je cesta v exportovaném grafu — bez
   přístupu k Python objektům.
3. **Znalost jako data, ne kód.** Synonyma, podřazení tříd, můstková pravidla, výjimky,
   role — všechno jsou řádky, které jdou napsat do souboru nebo říct z konzole (`!uč`,
   `!pravidlo`, `!výjimka`, `!role`) a které mají v grafu provenienci. Kód drží jen
   *operátory* (malou uzavřenou množinu) a *čtení*.

---

## 2. Cesta věty grafem (a kde je to v kódu)

```
 text ──► oracle ──► read ──► triage ──► ground ──► memory (graf) ──► logic ──► render ──► odpověď
          UDPipe     čtení    status     zakotvení   uzly + výroky      verdikt    čeština
          (keš)      věty     výroku     identita    + provenience      + důkaz    + zdroj
                                          registr                        ▲
                                          čas, místa                     │ recall (propad),
                                                                          │ lexicon (vazby),
                              dialog.Session řídí celý tah  ─────────────┘ derive (pravidla)
```

| krok | modul | co dělá | co z toho vidíš |
|---|---|---|---|
| **rozbor** | `cb6/oracle.py` | UDPipe (služba `127.0.0.1:42200`) přes keš `data/cache/parses.json`; testy jedou z nahrávky `tests/data/parses.json` (`RecordedOracle`) — hermeticky, bez sítě | rozbor má provenienci (model), dá se přehrát |
| **čtení** | `cb6/read.py` (+ tabulky `cb6/defaults.py`, čas `cb6/chronos.py`) | jeden rozbor → `Predication` (predikát, druh, role `RoleFill` s termy `TermSpec`, negace, modalita, čas); **nic se neztrácí** — co nemá místo, je *zbytek* nebo *částice*; otázka = predikace s dírou; „která N“ = díra omezená skupinou; rozkaz výpisu = otázka druhu `list` | `čtu: napsat(co:?, kdo:·Karel Čapek)` |
| **triáž** | `cb6/triage.py` | struktura ≠ tvrzení: podmínka → pravidlo, obsah promluvy → `reported`, disjunkce/kardinalita → `REJECTED` s důvodem, vedlejší `nmod` → `REJECTED`, fragment mimo znalost, typování zvlášť | `[zamítnuto]`, `[obsah promluvy, ne fakt]` |
| **zakotvení** | `cb6/ground.py` (+ registr `cb6/discourse.py`) | slova → uzly: identita jmen („Jirásek“ = „Alois Jirásek“), zájmena a nevyslovený podmět (registr referentů = pohled nad hranami `mention`, aktivace jen řadí), instance z neurčité zmínky, nominativ jmenovací („drama R.U.R.“ → R.U.R. ∈ drama), výčty; zapíše výroky s proveniencí | `[kdo: „nevyslovený podmět“ = Alois Jirásek (koref: registr, téma dokumentu)]` |
| **paměť** | `cb6/memory.py` | graf uzlů a výroků; uzávěry (`same_as*`, `member*`, `subset*`, `within*`, čas), aktivace, JSON (`to_json`/`load`), **export grafu** `Memory.graph()` pro viewBase i audit | `!ukaž s0042`, `!program`, `!graf g.json` |
| **logika** | `cb6/logic.py` (+ `cb6/lexicon.py`) | `evaluate` (ANO/NE/NEVÍM/KONFLIKT/MOŽNÁ), `enumerate` (wh‑díry, výpis), `describe` („Kdo je X?“), `derive` (pevný bod pravidel z textu); shoda predikátů přes lexikon; každý verdikt nese `Proof` | `→ ANO … protože: … ↳ krok … [odvozeno z: přečteno z textu]` |
| **propad** | `cb6/recall.py` | když není ANO/NE: co paměť o věcech z otázky ví (týž graf, řazení překryvem, stupněm, čerstvostí) — nikdy netvrdí | `vím: - …` |
| **render** | `cb6/render.py` | šablony jako data; vypíše jen to, co je ve struktuře důkazu | celý text odpovědi |
| **dialog** | `cb6/dialog.py` | `Session.ingest` (dokument, stupeň `read`), `Session.say` (tvrzení `said` / otázka bez zápisu / oprava „Ne, …“ = odvolání + zápis / `!příkazy`), žurnál tahů, `replay` (deterministicky týž program) | REPL `python -m cb6 chat`, demo |
| **rozhraní** | `cb6/cli.py`, `cb6/viewbase_app.py` | terminál; živý 3D graf (viewBase2) s terminálem a detailem uzlu na klik | http://127.0.0.1:8081/ |
| **měření** | `bench/` | sady dokumentů + zlaté otázky, yield, QA s dosahem, statusy, audit grafu, precision audit se soudcem (Ollama gemma4) i člověkem, determinismus, diff | `mereni/<datum>-<commit>.md` |

---

## 3. Základní pojmy (slovníček)

### Uzly grafu (`Node`, id podle druhu)
- **entita** `e…` — anonymní identita se jmény (`names`), rod, číslo, dokument. „Alois Jirásek“, „R.U.R.“, i anonymní instance („Filipovo auto“ = `a ∈ auto` bez jména).
- **group** `g…` — množina podle lemmatu, případně zúžená přívlastky (`kniha[první]` → hrana `restricts` na `kniha`). „spisovatel“, „román“, „dílo“.
- **místo** `p…`, **čas** `t…` (`TimeSpec`: bod/interval, `before`/`within`), **hodnota** `v…`.
- **dokument** `d…` › **segment** (nadpis / prázdný řádek) › **věta** `z…` — provenience; věta má hrany `mention` na uzly, které v ní byly jmenovány (to je registr referentů).
- **výrok** `s…` — reifikovaná predikace (viz dál); **open** `o…` — otevřená položka (co systém neuměl umístit); **vazba** `lex:…` — použitý řádek lexikonu.

### Výrok (`Statement`) — řádek programu
`pred` (lemma slovesa / `být` / `∅` u fragmentu) · `kind` (`verb`, `copula`, `fragment`, `nmod`, `appos`, `rule`, `typing`, `list` jen u otázek) · `roles` (jméno role, id termů, kvantifikátor, autorita jména, povrchový tvar, vnořený výrok, díra) · `neg`, `modality` (možnost/nutnost/vůle/fáze), `tense` · `kernel` (viz jádra) · **`grade`** (odkud: `read` z textu / `said` z dialogu / `derived` odvozením) · **`claim`** (co s ním logika smí: `SAFE` znalost / `HYPOTHESIS` nikdy neodpovídá / `REJECTED` viditelné zamítnutí s `reason`) · **`mood`** (`assert` tvrzení / `question` / `pattern` vzor pravidla / `reported` obsah promluvy) · `defaults` (přiznané výchozí volby, text) · `prov` (dokument, číslo věty, text, tah, model) · `derived_from` + `rule` + `links` (řetěz odvození: z kterého výroku, kterým pravidlem, přes které řádky lexikonu) · `parent` (vnoření: vztažná věta, obsah promluvy, vzor pravidla) · `alternatives` (hypotéza je alternativou k jádru téže věty) · `status` (`active` / `revoked` — historie zůstává) · `residue`, `open`.

Do verdiktu jde jen **`SAFE` + `assert` + aktivní** (`Memory.knowledge()`); typovací výroky (`kind="typing"`, „x ∈ x“ z neurčité zmínky) slouží uzávěrům, ale nejsou odpověď ani se nepočítají do výtěžku.

### Role a kvantifikátory
Jména rolí jsou česká slova (`kdo`, `co`, `kde`, `kam`, `odkud`, `kudy`, `kdy`, `od_kdy`, `do_kdy`, `jak_dlouho`, `komu`, `čím`, `s_kým`, `jako`, `jak`, `pořadí`, `čí`…) nebo — když tabulka `ROLE_BY_CASE` nezná předložku+pád — povrchové (`v+Loc`); povrchová role vytvoří *otevřenou položku* a jde doučit (`!role v+Loc = kde`). Kvantifikátor termu: `∀` (každý, žádný, generický prézens v jednoduché obecné větě), `∃` (nějaký, neurčitá zmínka), `·` (určitý / vlastní jméno). Autorita role: `structural` / `default` / `learned` / `surface`.

### Jádra (`kernel`) = tvrdé hrany, po kterých teče pravdivost
`member` (Hrabal ∈ spisovatel), `subset` (spisovatel ⊆ člověk; negované = `disjoint`), `within` (Praha ⊆ Česko, místa), `same_as` (dvě jména téže věci), `before` (čas), `name`. Uzávěry (`member_star`, `subset_star`, `within_star`, `same_as_star`, `time_within`, `disjoint`) jsou v `memory.py`; `restricts` (zúžená skupina → základ) se počítá jako `subset`.

### Verdikt a důkaz (`Verdict`, `Proof`)
`ANO` (shoda), `NE` (jen z opačné polarity, disjunktnosti nebo jiného počtu — nikdy „z ticha“), `NEVÍM` (s tím, co chybí a co je blízko + propad), `KONFLIKT` (obojí), `MOŽNÁ` (výrok je jen modální). `Proof`: `statements` (id výroků), `steps` (text kroků: `Hrabal ∈ spisovatel`, `implikace: bydlet ⇒ žít [lex:syn:0031]`, `pravidlo r0001: jet→být`), `hard` (strojově: `(jádro, a, b)` — `member`/`subset`/`within`/`same_as`/`time`/`disjoint`/`lex`; audit je ověřuje jen z exportu), `defaults`, `grade` (nejslabší premisa), `links` (id řádků lexikonu). Otázka je *přechod bez zápisu*: aktivuje kontext, ale bázi nemění (uzly založené jen dotazem se uklidí).

### Aktivace, registr, segmenty (stavovost)
Text je hierarchie stavů dokument › segment › věta. Věta mění registr referentů (hrany `mention`), aktivaci (kontext, s útlumem `Memory.DECAY`) a znalost. **Aktivace řadí, registr rozhoduje** (kdo připadá v úvahu — rod, číslo, okno tento + předchozí segment), pravidla odvozují (pevný bod). Nejednoznačná koreference → jádro bez termu + `HYPOTHESIS` alternativy + otevřená položka.

### Znalost jako data
| co | kde | jak přidat | provenience v grafu |
|---|---|---|---|
| **vazby predikátů a tříd** — `třída` (~ same), `implikace` (⇒), `podřazení` (⊆); síla `same`/`implies`/`related` (jen recall) | `cb6/lexicon.py`, seed `cb6/lexikon/*.jsonl` | `!uč kázat = hlásat` · `!uč bydlet => žít` · `!uč vydat ~ napsat` · `!uč drama < dílo` | uzel `vazba` (líně, až při použití), krok `lex`, `uses_rule` |
| **můstková pravidla** (dotaz na X zkus jako Y s přemapovanými rolemi) | `Memory.rules` | `!pravidlo jet(kam:X) => být(kde:X)` | krok `pravidlo r…` (sjednocení s lexikonem = plánovaný krok 5) |
| **pravidla z textu** („pokud/když/jestliže“, `only if`, `iff`) | výroky `kind="rule"` se vzory | text | `derived_from`, `uses_rule` |
| **výjimky** z ∀ | `Memory.exceptions` | `!výjimka létat pták tučňák` | doložka v důkazu |
| **role** | `Memory.learned["roles"]` | `!role v+Loc = kde` | `authority=learned`, `defaults` |
| **čtecí tabulky** (role podle předložky+pádu, determinátory, částice, místa, spojky podmínek, slovesa postoje, slovesa výpisu…) | `cb6/defaults.py` | commit | — (mění čtení, ne verdikt — proto zůstávají tabulkou) |

Hranice: **co mění verdikt, patří do lexikonu; co mění čtení, zůstává tabulkou v `defaults.py`.**

---

## 4. Jak vzniká odpověď (krok za krokem)

1. Otázka se přečte jako predikace s dírou (`kde:?`, `co:?filler:∃dílo` = díra omezená skupinou, `co:?count:∃zub` = počet, `jaký:?` = vlastnost) a zakotví **bez zápisu**.
2. `derive()` doběhne pevný bod pravidel z textu (kdyby přibyla premisa).
3. **Wh‑otázka** → `enumerate`: pro každý výrok znalosti se stejným predikátem (přesně, nebo přes lexikon — `Lexicon.match(dotaz, výrok)`: `same` oběma směry, `implies`/`podřazení` jen od výroku k dotazu, řetěz ≤ 4) se zkusí shoda rolí (`match`): každá role dotazu musí mít protějšek, termy se porovnají přes uzávěry; výplně díry se posbírají (s omezením skupinou přes `fits_class` — `member*/subset*` nebo `podřazení`); dál můstková pravidla, rodina rolí (`kde` bez `kde` → `kam/odkud/kudy` s přiznáním). Otázka druhu `list` („Vyjmenuj díla X“) → `list_verdict`: členové skupiny, u vlastníka jen ti s výrokem `kdo: X, co: kandidát`, nebo přiznaně jedinci z dokumentu, jehož je X tématem.
4. **Ano/ne otázka** → `evaluate`: přímá shoda; jádrové otázky („Je Hrabal stroj?“) přes uzávěry a disjunktnost; počet; modalita; můstková pravidla; `pos`+`neg` → `KONFLIKT`.
5. Není‑li ANO/NE: **propad** (`recall`) vypíše, co paměť ví, a `rejected_notes` řekne, kde text mluví, ale interpretaci neurčuje (zamítnutí, hypotézy).
6. **Render**: verdikt, výplně, výroky se zdrojem, kroky `↳`, doložka stupně `[přečteno z textu | řekls to | odvozeno z: …; výchozí volby]`.
7. Použité řádky lexikonu se **materializují** do paměti (uzly `vazba`), aby audit našel krok `lex` v exportu; uzly založené jen dotazem se uklidí.

---

## 5. Nic mimo graf — export a audit

`Memory.graph()` vrací `networkx.MultiDiGraph` se **vším**, co paměť drží: uzly termů, výroků (atributy `claim`, `grade`, `life`, `mood`, `defaults`, `reason`…), dokumentů/segmentů/vět, otevřených položek, vazeb; hrany `role:<jméno>`, jádra (`member`, `subset`, `disjoint`, `within`, `same_as`…), strukturní `source`, `part_of`, `nested_in`, `derived_from`, `uses_rule`, `alternative_of`, `about`, `residue_of`, `mention`, `restricts`, měkké `co_mention`. Totéž vidí viewBase i audit.

`bench/graphcheck.py`: **`check_graph`** (provenience každého výroku až na dokument, derivace má `derived_from`+`uses_rule` a SAFE premisy, `REJECTED` má důvod, žádný osiřelý term ani věta, `open` má `about`, `vazba` má zdroj) a **`check_answer`** (výroky důkazu existují a jsou znalost, každý tvrdý krok je cesta v grafu — `hard_path` zrcadlí `member_star`/`subset_star`, `lex` je cesta po uzlech `vazba`). Musí být **0 porušení**; když není, je to chyba, ne šum.

---

## 6. Jak se to měří (bench)

`python -m bench run --sada wiki --strop 40 --dok alois_jirásek karel_čapek --soudce` (rychlá smyčka, 1–3 min) · `python -m bench run --vse --dvakrat --soudce --audit-doky 8` (plný běh, ~30 min; zpráva `mereni/<datum>-<commit>.md/.json`).

Zpráva: **yield** (SAFE výroků / 1 000 slov, hlavní/vše), **statusy**, **QA** (zásahy; kurátorované zvlášť; sady `etalon`, `conbond`, `otazky` po valenčním filtru, `korpus`, `gen` — LM/Claudem psané do ověření), **dosah** (jak daleko je odpověď od poslední zmínky tématu), **audit grafu** (0), **precision audit** (400 výroků, stabilní vzorek po větách, soudce Ollama gemma4 + lidské odpovědi `bench audit --dok X --rucne`; *unsupported* s Wilsonovým intervalem, rozklad podle druhu), **determinismus**, **diff** proti předchozí zprávě, ablace `--bez-lexikonu`.

**Zelený řádek** = víc pravdivé (unsupported neroste), doložitelné (graf 0), dotazovatelné (QA ↑ nebo yield ↑ při stejné precision). Recall ↑ + precision ↓ = regrese. Hypotéza před změnou a výsledek po ní: `mereni/HYPOTEZY.md`.

---

## 7. Jak si to pustit

```bash
.venv/bin/python -m pytest -q                       # 168 + 2 xfail (hermetické, tests/data/parses.json)
.venv/bin/python -m cb6 chat --pamet moje.json      # REPL: věty, otázky, !příkazy (UDPipe musí běžet)
.venv/bin/python -m cb6 ingest text.txt --dok jmeno --pamet moje.json
.venv/bin/python -m cb6 ask "Kde se narodil Alois Jirásek?" --pamet moje.json
.venv/bin/python -m cb6.viewbase_app --pamet data/pamet-graf.json --port 8081      # živý graf (viz HANDOVER § 2)
.venv/bin/python -m bench ukazky                    # přegeneruj docs/UKAZKY.md
.venv/bin/python -m cb6.record tests/data/sentences.txt tests/data/parses.json  # nové věty do nahrávky pro testy
```

Příkazy v dialogu (`!nápověda`): `!zapomeň s0001` · `!role v+Loc = kde` · `!uč a = b | a => b | a ~ b | a < b` · `!pravidlo jet(kam:X) => být(kde:X)` · `!výjimka létat pták tučňák` · `!otevřené` · `!odpověz o0001 kde` · `!program` · `!popiš Jirásek` · `!ukaž s0042` · `!hypotéza s0042 potvrď|zamítni` · `!statusy` · `!ulož p.json` · `!načti p.json` · `!graf g.json`. Oprava: „Ne, …“ / „To není pravda.“ odvolá poslední řečený výrok; „Ne každý pták.“ opraví kvantifikátor.

---

## 8. Symboly ve výstupu

`✓ zapsáno [s0001] …` výrok v grafu · `[zamítnuto]` / `[obsah promluvy, ne fakt]` status · `? o0001: …` otevřená položka · `čtu:` čtení otázky · `→` výplň / verdikt · `protože:` premisy · `↳` krok důkazu · `zdroj:` věta a dokument · `[přečteno z textu | řekls to | odvozeno z: …; volby]` doložka stupně · `⚠ text o tom mluví … ale interpretaci neurčuje` zamítnutí · `vím:` propad · `∀ ∃ ·` kvantifikátory · `⟨member⟩ ⟨subset⟩ ⟨within⟩ ⟨same_as⟩` jádro · `∈ ⊆ ∦` členství / podmnožina / disjunktnost · `~ ⇒ ≈` vazba lexikonu (same / implies / related) · `[lex:syn:0031]`, `[lex:pod:0002]`, `[lex:said:0001]` id řádku lexikonu (seed synonyma / seed podřazení / řečeno) · `s… e… g… p… t… z… d… o…` id výroku / entity / skupiny / místa / času / věty / dokumentu / otevřené položky.

---

## 9. Kde hledat dál

- **Proč takhle** (5 zásad, kde je stavovost, kde je a není LM): `docs/KONCEPT.md`.
- **Stav, čísla, otevřené tahy, deník rozhodnutí, checklist**: `docs/HANDOVER.md`.
- **Návrh znalostních vazeb** (8 operátorů, řádky, materializace, pořadí kroků): `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md`.
- **Hypotézy a výsledky každého tahu**: `mereni/HYPOTEZY.md`; zprávy `mereni/`.
- **Zlaté otázky a jejich původ**: `bench/gold/PROVENIENCE.md`.
- **Testy jako dokumentace chování**: `tests/test_dialogues_af.py` (dialogy A–F), `tests/test_dialog_g.py` (článek o Čapkovi, nálezy G‑1…G‑4), `tests/test_rules.py`, `tests/test_lexicon.py`, `tests/test_vypis.py`, `tests/test_triage.py`, `tests/test_discourse.py`.
