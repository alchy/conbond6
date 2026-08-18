# conbond6 — handover (živý)

*Aktualizuje se po každém významnějším tahu. Poslední aktualizace: 18. 8. 2026 (ráno).*

## 1. Kde co je

| co | kde |
|---|---|
| repo | `~/Projects/conbond6` · https://github.com/alchy/conbond6 (větve `main` = `v1`) |
| **úvod a orientace v kódu** (pojmy, cesta věty grafem, příkazy) | `docs/UVOD.md` |
| **ukázky ze živého běhu** (12 scén; přegenerovat `python -m bench ukazky` po tahu, který mění odpovědi) | `docs/UKAZKY.md` (generátor `bench/ukazky.py`) |
| zadání, invarianty I‑1…I‑12 | `docs/superpowers/specs/2026-08-17-conbond6-design.md` |
| znalostní vazby jako data (návrh) | `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md` |
| lexikon vazeb (krok 1 + `podřazení`) | `cb6/lexicon.py` (operátory `třída`, `implikace`, `podřazení`; loader, shoda, materializace) · seed `cb6/lexikon/synonyma.jsonl` (88 ř.) + `podrazeni.jsonl` (18 ř., žánry ⊆ dílo) · dialog `!uč a = b | a => b | a ~ b | a < b` |
| výpisové otázky (k ověření J.) | `bench/gold/gen-{alois_jirásek,karel_čapek,božena_němcová}.json` (9, `curated: False`, sada `gen`) → `python -m bench gold-gen --overit --dok …` |
| koncept (proč takhle) | `docs/KONCEPT.md` |
| plán v1 + stav provedení | `docs/superpowers/plans/2026-08-17-conbond6-v1.md` |
| hypotézy a výsledky tahů | `mereni/HYPOTEZY.md` |
| zprávy benche | `mereni/<datum>-<commit>.md/.json` (poslední plný, **stabilní vzorek**: `2026-08-18-3cd63e4`; předchozí `b75d8d5`, `ad5d41b`, `234ca26`) |
| lidské odpovědi auditu | `mereni/audit-<dokument>.json` (otisk → [verdikt, pozn, chápu‑z‑grafu a/n]) |
| keš verdiktů soudce | `mereni/audit-cache.json` (klíč = otisk · soudce · verze promptu) |
| zlaté otázky | `bench/gold/` (+ `PROVENIENCE.md`, `otazky-filtr.log.md`, `gen-*.json`) |
| jádro | `cb6/` — `oracle chronos defaults lexicon read triage discourse memory ground logic recall render dialog cli viewbase_app` |
| bench | `bench/` — `data gold gold_gen qa metrics run graphcheck audit judge diff __main__` |
| testy | `tests/` (167 + 2 xfail; hermetické — rozbory `tests/data/parses.json`) |
| data mimo repo | `data/corpus/conBond2` (klon), `data/cache/parses.json` (keš UDPipe, ~75 MB), `data/pamet-graf.json` |
| paralelní větev | conbond5 (`~/Projects/conbond5`, jiné sezení, HEAD c503b68) — do něj nesahat |
| související | inventura conbond0–4: artefakt „Inventura conBond 0–5“ (Claude artifacts, 17. 8.) |

## 2. Prostředí a služby

- Python 3.11, `.venv` (`pip install -e '.[dev]'`), závislost jen `networkx` (+ dev pytest/mypy/pylint; viewbase editable z `~/Projects/viewBase2/python`).
- **UDPipe** služba z conBond3 na `127.0.0.1:42200` (model `cs_all-ud-2.17-251125`) — jen pro nové rozbory a bench; testy jedou z keše.
- **Ollama** `gemma4:latest` na `127.0.0.1:11434` — soudce auditu a `gold-gen` (27B qwen se do 24 GiB nevejde vedle UDPipe).
- **Živý graf:** `.venv/bin/python -m cb6.viewbase_app --pamet data/pamet-graf.json --port 8081` → http://127.0.0.1:8081/ (viewBase2; dnes paměť se třemi články: Jirásek, Karel Čapek, Josef Čapek). **Pozor (17. 8. večer):** viewBase2 HEAD (3c22e4c) má f‑string se zpětným lomítkem → na Pythonu 3.11 `SyntaxError`; demo proto běží z `.venv314` (Python 3.14: `python3.14 -m venv .venv314 && .venv314/bin/pip install -e . -e ~/Projects/viewBase2/python`), dokud viewBase2 nebude 3.11‑kompatibilní. Ukončovat `kill -INT <pid>` (uloží paměť); démon nesmí být zabit bez INT.

## 3. Jak se pracuje (smyčka jednoho tahu)

1. Do `mereni/HYPOTEZY.md` zapsat **hypotézu**: co se změní a které číslo se má pohnout, kterým směrem.
2. Změna + testy (`pytest -q`, `mypy cb6 bench`, `pylint` u nových modulů 10/10).
3. **Rychlá smyčka:** `python -m bench run --sada wiki --strop 40 --dok alois_jirásek karel_čapek --soudce` (~1–3 min; verdikty se kešují).
4. **Plný běh před sloučením:** `python -m bench run --vse --dvakrat --soudce --audit-doky 8` (~30 min napoprvé, pak méně) → `mereni/`.
5. Zpráva: yield, unsupported (+ shoda soudce/člověk), statusy, QA (kurátorované zvlášť, dosah), audit grafu (musí být 0), determinismus (ano), diff.
6. Commit s číslem v předmětu; `git push` (main = v1).
7. Když tah mění odpovědi: `python -m bench ukazky` (docs/UKAZKY.md jsou živé), a doplnit scénu, je‑li nová schopnost.

Zelený řádek: víc pravdivé (unsupported neroste), doložitelné (každý zásah má důkaz), dotazovatelné (QA hits/coverage rostou nebo yield roste při stejné precision). Recall ↑ + precision ↓ = regrese, dokud není v commitu přijatý trade‑off.

## 4. Stav čísel (17. 8. 2026)

| měřítko | conbond5 (výchozí) | conbond6 v1 |
|---|---|---|
| unsupported, 2 dok. / vzorek 100 (soudce gemma4) | **76,5 %** | **23,0 %** [15,8–32,1] |
| unsupported, plný běh 8 dok. / 400 (**stabilní vzorek po větách od 234ca26**) | — | **30,1 %** [25,7–34,7] (3cd63e4; hlavní 30 %, appos 35 %, nmod‑místo 13 %; b75d8d5 30,5 %, ad5d41b 31,4 %) |
| yield hl./vše (2 dok.) | 160 / 298 | 89 / 94 |
| yield hl./vše (plný běh, 182 853 slov) | — | 76,8 / 89,7 |
| statusy (plný běh) | — | SAFE 27 771 · HYPOTHESIS 3 271 · REJECTED 19 747; pravidel 59, odvozeno 4 |
| QA stejné 2 dok. | 12/17 | 12/17 |
| QA plný běh | 60,9 % na staré sadě (682 auto) | **184/343** (3cd63e4 = b75d8d5): stará sada 179/334 (ad5d41b 178, 234ca26 175), **gen výpis 5/9** (neověřené); **kurátorované 29/130** (etalon 14/32, conbond 8/8, korpus 7/90); otazky‑filtr 150/204 (74 %) |
| audit grafu | — | 0 porušení (bylo 33, opraveno; krok `lex` se rekonstruuje z uzlů `vazba`) |
| lexikon v odpovědích (plný běh) | — | krok `lex` u 11/334 otázek (9 správně); ablace `--bez-lexikonu`: 177/334 → seed vrstva nese 1 zásah (obsahovat ⇒ mít) |
| determinismus | — | ano |
| lidský audit | — | 1 výrok (J.), shoda se soudcem 1/1 — **potřeba ≥ 30 na dokument** |

Čísla se nedají přímo srovnat s conbond5 60,9 % — sada se změnila (auto otázky filtrované, přibyl korpus s těžkými otázkami). Srovnatelné jsou dvě věci: tytéž 2 dokumenty (QA beze změny, unsupported 76,5 → 23 %) a filtrované auto (71 %).

## 5. Co je hotové (v1)

Paměť v2 (`claim`, `mood`, `parent`, `rule`, `alternatives`; JSON v2 čte v1) · export grafu s proveniencí (source, part_of, nested_in, derived_from, uses_rule, alternative_of, about, residue_of, mention; časy s atributy; `disjoint`) · `bench/` (sady wiki+korpus, gold v repu, valenční filtr auto 204/682, yield, statusy, QA s dosahem, precision audit soudce+člověk s Wilsonem a rozkladem podle druhu, audit grafu + rekonstrukce odpovědi, diff, determinismus, `gold-gen`) · triáž (podmínka→pravidlo if/only_if/iff, `když` jen v prézentu; vnořený obsah→reported; disjunkce/kardinalita→REJECTED; nmod→REJECTED kromě „místo uvnitř fráze“; fragment mimo znalost; typing zvlášť) · `derive()` (pevný bod, odvolání kaskáduje) · registr referentů (projekce hran `mention`, ambiguita → hypotézy + OPEN, segmenty) · `!ukaž` / `!hypotéza potvrď|zamítni` / `!statusy` · doložky statusu v odpovědích, zamítnutí a hypotézy hlášené (Verdict.notes) · dialogy G (7 zelených, 2 xfail nálezy) a H · viewBase2 adaptér.

**Lexikon vazeb, krok 1** (`cb6/lexicon.py`): vazby jako řádky dat `{id, op, args, síla, autorita, zdroj, pozn}`; operátory `třída` (union‑find → reprezentant) a `implikace` (orientované hrany), shoda predikátů = cesta od výroku k dotazu po `same` (oběma směry) a `implies` (po směru), `related` jen pro recall; seed `cb6/lexikon/synonyma.jsonl` migrací `SYNONYMS` — 88 řádků, z toho `same` 32 (vidové dvojice, skutečné záměny), `implies` 32 (bydlet ⇒ žít, obsahovat ⇒ mít, vystudovat ⇒ studovat…), `related` 24 (kde tabulka lhala: vydat ≁ napsat, padnout ≁ zemřít, chodit ≁ studovat…); líná materializace použitých řádků do paměti (`Memory.links`) → uzly `kind="vazba"` v exportu, `uses_rule` z odvozených výroků, tvrdý krok `lex` v důkazu ověřovaný graphcheckem jen z exportu (`lex_path`); `!uč` píše řádky `said` (`Memory.learned["synonyms"]` zaniklo, staré JSON se převedou při načtení); `defaults.SYNONYMS`/`synonym_class` odstraněny; `bench run --bez-lexikonu` = ablace seed vrstvy.

**Výpis (17. 8. večer, nález J. z dema):** čtení `který/jaký + N` v otázce = díra v roli N (`co:?`) s N jako omezením výplně (místa/časy beze změny); imperativ `vyjmenuj/vypiš/uveď/jmenuj N (X‑gen)` = otázka druhu `list` (nezapisuje se): členové skupiny (přes `member*/subset*` a `podřazení` v lexikonu, krok `lex`), u vlastníka jen ti s výrokem `kdo: vlastník, co: kandidát`, nebo — přiznaně jako výchozí volba — pojmenované entity z dokumentu, jehož je vlastník tématem (téma = `base` uzlu dokumentu, přežije uložení); operátor `podřazení` v lexikonu (`!uč drama < dílo`, seed 18 ř.); nominativ jmenovací („drama R.U.R.“, „román Továrna na absolutno“ → entita s názvem ∈ skupina hlavy, typing „třída z nominativu jmenovacího“) místo dřívějšího paskvilu „drama R.U.r.“ jako jména.

Opravy precision v čtení/zakotvení (jen věci, které lhaly): životopisná závorka jen u osob s tvarem „A – B“ bez slovesa; přivlastnění → `mít` jako HYPOTHESIS; částečná shoda jména jen s příjmením; tvary jmen jako jedno jméno; výčet „děti: Helena, Josef…“ = member, ne same_as; typing není odpověď; otázky nezanechávají osiřelé uzly.

## 6. Otevřené tahy (pořadí podle toho, co ukázal bench)

1. **Lidský audit** — J.: `python -m bench audit --dok alois_jirásek --rucne` (a druhý dokument), min. 30 výroků; pak zpráva hlásí shodu soudce/člověk a „nechápu z grafu“ %.
2. **Ověření generovaných otázek** — `python -m bench gold-gen --dok karel_čapek --n 12` → `--overit` (kurátorované číslo 29/130 je malé a korpus 7/90 tvrdý).
3. Zbývající chyby precision (z auditu): kvantifikátor ∀ z „všechna jeho dramata“ (∀ bez omezení přivlastněním), plošná koordinace (`kdo: Petr+Karel` i tam, kde jde o dvě klauze — „otcem byl Josef…, matkou Vincencie“), vztažné věty (`kdo:∀sousoší`), participia jako predikáty.
4. Nálezy dialogu G: G‑1 otázka „Kdy napsal R.U.R.?“ čte R.U.R. jako podmět; G‑2 funkční role (narodit_se.kde/kdy) → hlásit konflikt; G‑3 „Jeho bratr Josef Čapek“ → přístavek přilepen ke jménu (rodinné vztahy tak v grafu nejsou); G‑4 `v Lidových novinách` není místo (učení role / instituce).
5. Prostor modelů pro disjunkci/ekvivalenci/kardinalitu (přenos `conBond3/cb_logic/models.py`) — dnes REJECTED s důvodem.
6. Adaptéry conbond1/conbond4 pro zpětný běh QA (Task 12 — neproveden).
7. Valence jako data (`valence.json` conbond1 / VALLEX), relativní čas (conbond1 chronos), nominalizace, rekurze v dotazu (jellyAI3 SubQuery) — každý jako měřený tah, až bench ukáže potřebu.
8. **Znalostní vazby jako data** (návrh `2026-08-17-znalostni-vazby-design.md`): **krok 1 hotový** (synonyma se sílou, lexikon, materializace — viz § 5), **`podřazení` hotové** (výpis). Dál: krok 2 překryv/porovnání + veličiny ("mohli se potkat", "vejde se", "Jaká je délka") → krok 3 příbuzenství (inverze/skládání, G‑3) → antonyma až na otázku → krok 5 `Memory.rules` (můstky) jako řádky `implikace` s mapou rolí. Zbývá sjednotit dvě dnešní místa (`Memory.rules`, `kind=rule`) s lexikonem.
9. **Výpis — zbytky z reálného textu:** typing z nadpisů/seznamů („Wikilivres: Josef Čapek: díla“ → Josef Čapek ∈ dílo — paskvil z appos), „Krakatit je román.“ čtené jako obecná věta (⊆ místo ∈; velké písmeno na začátku věty není důkaz jména), „R.U.R. (… 1920) –“ → `zemřít(R.U.R., 1920)` (životopisná závorka u díla); imperativ s vedlejší větou („Vyjmenuj, co napsal…“); ověření 9 gen otázek J.
10. **Převzít z conbond5 po jedné konstrukci** (srovnávací slova, veličiny s jednotkami, definice/vztahová jména z textu, meta‑otázky, obnova diakritiky, elipsa přísudku) — každou s číslem před/po na stabilním vzorku; etalon 14/32 vs conbond5 24/32 je přesně tento rozdíl.

## 7. Deník rozhodnutí

- 17. 8. — J.: cíle dává on, cestu rozhoduje Claude a měří benchem (viz paměť `conbond-goals-only-claude-decides-how`). Všechny cesty otevřené, včetně NN, rozhoduje měření.
- 17. 8. — conbond6 = klon conbond5 s historií; obě větve běží nezávisle, smějí se inspirovat; do conbond5 conbond6 nesahá.
- 17. 8. — Statusy `SAFE/HYPOTHESIS/REJECTED` jako pole `claim` (pole `status` v conbond5 je životní cyklus); `RESIDUE`/`OPEN` jsou vrstvy, ne statusy.
- 17. 8. — Soudce = Ollama gemma4 (27B se nevejde do paměti); prompt v2 (nevyslovený podmět z kontextu, závorka s roky) — změna měřidla zapsaná v HYPOTEZY.
- 17. 8. — Kurátorované a automatické otázky se vykazují zvlášť; auto po valenčním filtru; LM‑generované jen po lidském ověření (požadavek J.: otázky s hlavou a patou).
- 17. 8. — `read.py` v1 beze změny konstrukcí; opravy jen tam, kde výroky lhaly (precision).
- 17. 8. — viewBase → viewBase2 (github.com/alchy/viewBase2), oblasti podle dokumentu (`skupina`).
- 17. 8. — Vzorek auditu se vybírá po větách se seedem = dokument (dřív seed = commit → každý commit jiných 400 výroků, ±5 b. šum). Čísla před 234ca26 nejsou navzájem srovnatelná; od 234ca26 ano.
- 17. 8. — ∀ z generického prézentu jen v jednoduché obecné větě (kořen, nekoordinovaný podmět, bez PROPN); hlavní predikace 35 → 31–32 % nepodložených.
- 17. 8. — Návrh conbond5 „Q(A,B) ⇐ TEST(…)“ přijat jako operátory `překryv`/`porovnání` v lexikonu vazeb; pravidlo je řádek dat s modalitou a proveniencí, materializovaný do grafu při použití; ne pátý slovník. Síla vazby `same/implies/related` (dnešní `SYNONYMS` je únik precision).
- 17. 8. — conbond5 (paralelně) jde cestou šíře konstrukcí (ruční otázky 59/70); conbond6 cestou věrnosti; další tah conbond6 = přebírat konstrukce z conbond5 po jedné přes bránu benche.
- 17. 8. (večer) — J.: chování jako „co znamená všechny — výpis děl“ má jít definovat měkce z konzole, ne kódem. Rozhodnutí: *znalost* (drama ⊆ dílo) je řádek lexikonu `!uč a < b` (operátor `podřazení`); *čtení* („která N“ = díra s omezením, rozkaz výpisu = otázka) zůstává kód a měří se — z konzole se parser vysvětlit nedá; „všechny“ samo nic nepotřebuje, `enumerate` vypíše všechny doložené výplně. Výpis podle tématu dokumentu je přiznaná výchozí volba (články díla jen vyjmenovávají), asociace jen přes výrok `kdo/co`, ne přes libovolný sdílený výrok (na reálném textu by „Josef Čapek“ byl dílem Karla).
- 17. 8. — Lexikon krok 1: síla vazby se rozhoduje podle významu páru, ne podle počtu zásahů (např. `pracovat ~ působit` same — životopisné „působil v/jako“; jiné významy chrání rámec rolí; `absolvovat`, `vyhrát`, `uvést`, `dostat`… zváženy jednotlivě, viz `pozn` v seedu). Shoda přes `implies` snižuje stupeň důkazu na `derived` (je to odvození, ne záměna). Otázka je vždy první argument shody (`same_pred(dotaz, výrok)`); u můstkových pravidel se pořadí opravilo (`dst_pred` je výrok). Použitý řádek se materializuje i při dotazu (uzel `vazba` v exportu) — jinak by krok `lex` nebyl z grafu doložitelný; nepoužité seed řádky graf nezatěžují.

## 8. Jak předat dál (checklist pro nové sezení)

0. Nové sezení v tomto adresáři dostane zadání automaticky z `CLAUDE.md` (pravidla spolupráce, kde co je, další tah).
1. Přečíst `docs/KONCEPT.md`, spec § 0–1, tuto stránku, poslední záznam v `mereni/HYPOTEZY.md`.
2. Ověřit služby: UDPipe 42200, Ollama 11434, `pytest -q` zelené.
3. Rychlá smyčka na dvou dokumentech (§ 3), porovnat s posledními čísly (§ 4).
4. Vybrat tah z § 6, zapsat hypotézu, měřit, commitnout s číslem, pushnout, doplnit § 4–7 tady.
