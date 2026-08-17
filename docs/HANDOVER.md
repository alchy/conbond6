# conbond6 — handover (živý)

*Aktualizuje se po každém významnějším tahu. Poslední aktualizace: 17. 8. 2026.*

## 1. Kde co je

| co | kde |
|---|---|
| repo | `~/Projects/conbond6` · https://github.com/alchy/conbond6 (větve `main` = `v1`) |
| zadání, invarianty I‑1…I‑12 | `docs/superpowers/specs/2026-08-17-conbond6-design.md` |
| koncept (proč takhle) | `docs/KONCEPT.md` |
| plán v1 + stav provedení | `docs/superpowers/plans/2026-08-17-conbond6-v1.md` |
| hypotézy a výsledky tahů | `mereni/HYPOTEZY.md` |
| zprávy benche | `mereni/<datum>-<commit>.md/.json` (poslední plný, **stabilní vzorek**: `2026-08-17-234ca26`) |
| lidské odpovědi auditu | `mereni/audit-<dokument>.json` (otisk → [verdikt, pozn, chápu‑z‑grafu a/n]) |
| keš verdiktů soudce | `mereni/audit-cache.json` (klíč = otisk · soudce · verze promptu) |
| zlaté otázky | `bench/gold/` (+ `PROVENIENCE.md`, `otazky-filtr.log.md`, `gen-*.json`) |
| jádro | `cb6/` — `oracle chronos defaults read triage discourse memory ground logic recall render dialog cli viewbase_app` |
| bench | `bench/` — `data gold gold_gen qa metrics run graphcheck audit judge diff __main__` |
| testy | `tests/` (146 + 2 xfail; hermetické — rozbory `tests/data/parses.json`) |
| data mimo repo | `data/corpus/conBond2` (klon), `data/cache/parses.json` (keš UDPipe, ~75 MB), `data/pamet-graf.json` |
| paralelní větev | conbond5 (`~/Projects/conbond5`, jiné sezení, HEAD c503b68) — do něj nesahat |
| související | inventura conbond0–4: artefakt „Inventura conBond 0–5“ (Claude artifacts, 17. 8.) |

## 2. Prostředí a služby

- Python 3.11, `.venv` (`pip install -e '.[dev]'`), závislost jen `networkx` (+ dev pytest/mypy/pylint; viewbase editable z `~/Projects/viewBase2/python`).
- **UDPipe** služba z conBond3 na `127.0.0.1:42200` (model `cs_all-ud-2.17-251125`) — jen pro nové rozbory a bench; testy jedou z keše.
- **Ollama** `gemma4:latest` na `127.0.0.1:11434` — soudce auditu a `gold-gen` (27B qwen se do 24 GiB nevejde vedle UDPipe).
- **Živý graf:** `.venv/bin/python -m cb6.viewbase_app --pamet data/pamet-graf.json --port 8081` → http://127.0.0.1:8081/ (viewBase2; dnes paměť se třemi články: Jirásek, Karel Čapek, Josef Čapek).

## 3. Jak se pracuje (smyčka jednoho tahu)

1. Do `mereni/HYPOTEZY.md` zapsat **hypotézu**: co se změní a které číslo se má pohnout, kterým směrem.
2. Změna + testy (`pytest -q`, `mypy cb6 bench`, `pylint` u nových modulů 10/10).
3. **Rychlá smyčka:** `python -m bench run --sada wiki --strop 40 --dok alois_jirásek karel_čapek --soudce` (~1–3 min; verdikty se kešují).
4. **Plný běh před sloučením:** `python -m bench run --vse --dvakrat --soudce --audit-doky 8` (~30 min napoprvé, pak méně) → `mereni/`.
5. Zpráva: yield, unsupported (+ shoda soudce/člověk), statusy, QA (kurátorované zvlášť, dosah), audit grafu (musí být 0), determinismus (ano), diff.
6. Commit s číslem v předmětu; `git push` (main = v1).

Zelený řádek: víc pravdivé (unsupported neroste), doložitelné (každý zásah má důkaz), dotazovatelné (QA hits/coverage rostou nebo yield roste při stejné precision). Recall ↑ + precision ↓ = regrese, dokud není v commitu přijatý trade‑off.

## 4. Stav čísel (17. 8. 2026)

| měřítko | conbond5 (výchozí) | conbond6 v1 |
|---|---|---|
| unsupported, 2 dok. / vzorek 100 (soudce gemma4) | **76,5 %** | **23,0 %** [15,8–32,1] |
| unsupported, plný běh 8 dok. / 400 (**stabilní vzorek po větách, 234ca26**) | — | **31,4 %** [26,9–35,9] (hlavní 32 %, appos 37 %, nmod‑místo 13 %) |
| yield hl./vše (2 dok.) | 160 / 298 | 89 / 94 |
| yield hl./vše (plný běh, 182 853 slov) | — | 77 / 90 |
| statusy (plný běh) | — | SAFE 27 164 · HYPOTHESIS 3 218 · REJECTED 20 553; pravidel 59, odvozeno 4 |
| QA stejné 2 dok. | 12/17 | 12/17 |
| QA plný běh | 60,9 % na staré sadě (682 auto) | 175/334; **kurátorované 29/130** (etalon 14/32, conbond 8/8, korpus 7/90); otazky‑filtr 146/204 (72 %) |
| audit grafu | — | 0 porušení (bylo 33, opraveno) |
| determinismus | — | ano |
| lidský audit | — | 1 výrok (J.), shoda se soudcem 1/1 — **potřeba ≥ 30 na dokument** |

Čísla se nedají přímo srovnat s conbond5 60,9 % — sada se změnila (auto otázky filtrované, přibyl korpus s těžkými otázkami). Srovnatelné jsou dvě věci: tytéž 2 dokumenty (QA beze změny, unsupported 76,5 → 23 %) a filtrované auto (71 %).

## 5. Co je hotové (v1)

Paměť v2 (`claim`, `mood`, `parent`, `rule`, `alternatives`; JSON v2 čte v1) · export grafu s proveniencí (source, part_of, nested_in, derived_from, uses_rule, alternative_of, about, residue_of, mention; časy s atributy; `disjoint`) · `bench/` (sady wiki+korpus, gold v repu, valenční filtr auto 204/682, yield, statusy, QA s dosahem, precision audit soudce+člověk s Wilsonem a rozkladem podle druhu, audit grafu + rekonstrukce odpovědi, diff, determinismus, `gold-gen`) · triáž (podmínka→pravidlo if/only_if/iff, `když` jen v prézentu; vnořený obsah→reported; disjunkce/kardinalita→REJECTED; nmod→REJECTED kromě „místo uvnitř fráze“; fragment mimo znalost; typing zvlášť) · `derive()` (pevný bod, odvolání kaskáduje) · registr referentů (projekce hran `mention`, ambiguita → hypotézy + OPEN, segmenty) · `!ukaž` / `!hypotéza potvrď|zamítni` / `!statusy` · doložky statusu v odpovědích, zamítnutí a hypotézy hlášené (Verdict.notes) · dialogy G (7 zelených, 2 xfail nálezy) a H · viewBase2 adaptér.

Opravy precision v čtení/zakotvení (jen věci, které lhaly): životopisná závorka jen u osob s tvarem „A – B“ bez slovesa; přivlastnění → `mít` jako HYPOTHESIS; částečná shoda jména jen s příjmením; tvary jmen jako jedno jméno; výčet „děti: Helena, Josef…“ = member, ne same_as; typing není odpověď; otázky nezanechávají osiřelé uzly.

## 6. Otevřené tahy (pořadí podle toho, co ukázal bench)

1. **Lidský audit** — J.: `python -m bench audit --dok alois_jirásek --rucne` (a druhý dokument), min. 30 výroků; pak zpráva hlásí shodu soudce/člověk a „nechápu z grafu“ %.
2. **Ověření generovaných otázek** — `python -m bench gold-gen --dok karel_čapek --n 12` → `--overit` (kurátorované číslo 29/130 je malé a korpus 7/90 tvrdý).
3. Zbývající chyby precision (z auditu): kvantifikátor ∀ z „všechna jeho dramata“ (∀ bez omezení přivlastněním), plošná koordinace (`kdo: Petr+Karel` i tam, kde jde o dvě klauze — „otcem byl Josef…, matkou Vincencie“), vztažné věty (`kdo:∀sousoší`), participia jako predikáty.
4. Nálezy dialogu G: G‑1 otázka „Kdy napsal R.U.R.?“ čte R.U.R. jako podmět; G‑2 funkční role (narodit_se.kde/kdy) → hlásit konflikt; G‑3 „Jeho bratr Josef Čapek“ → přístavek přilepen ke jménu (rodinné vztahy tak v grafu nejsou); G‑4 `v Lidových novinách` není místo (učení role / instituce).
5. Prostor modelů pro disjunkci/ekvivalenci/kardinalitu (přenos `conBond3/cb_logic/models.py`) — dnes REJECTED s důvodem.
6. Adaptéry conbond1/conbond4 pro zpětný běh QA (Task 12 — neproveden).
7. Valence jako data (`valence.json` conbond1 / VALLEX), relativní čas (conbond1 chronos), nominalizace, rekurze v dotazu (jellyAI3 SubQuery) — každý jako měřený tah, až bench ukáže potřebu.
8. **Převzít z conbond5 po jedné konstrukci** (srovnávací slova, veličiny s jednotkami, definice/vztahová jména z textu, meta‑otázky, obnova diakritiky, elipsa přísudku) — každou s číslem před/po na stabilním vzorku; etalon 14/32 vs conbond5 24/32 je přesně tento rozdíl.

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
- 17. 8. — conbond5 (paralelně) jde cestou šíře konstrukcí (ruční otázky 59/70); conbond6 cestou věrnosti; další tah conbond6 = přebírat konstrukce z conbond5 po jedné přes bránu benche.

## 8. Jak předat dál (checklist pro nové sezení)

1. Přečíst `docs/KONCEPT.md`, spec § 0–1, tuto stránku, poslední záznam v `mereni/HYPOTEZY.md`.
2. Ověřit služby: UDPipe 42200, Ollama 11434, `pytest -q` zelené.
3. Rychlá smyčka na dvou dokumentech (§ 3), porovnat s posledními čísly (§ 4).
4. Vybrat tah z § 6, zapsat hypotézu, měřit, commitnout s číslem, pushnout, doplnit § 4–7 tady.
