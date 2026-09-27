# conbond6 — handover (živý)

*Aktualizuje se po každém významnějším tahu. Poslední aktualizace: 27. 9. 2026.*

## 1. Kde co je

| co | kde |
|---|---|
| repo | `~/Projects/conbond6` · https://github.com/alchy/conbond6 (větve `main` = `v1`) |
| **úvod a orientace v kódu** (pojmy, cesta věty grafem, příkazy) | `docs/UVOD.md` |
| **ukázky ze živého běhu** (12 scén; přegenerovat `python -m bench ukazky` po tahu, který mění odpovědi) | `docs/UKAZKY.md` (generátor `bench/ukazky.py`) |
| zadání, invarianty I‑1…I‑12 | `docs/superpowers/specs/2026-08-17-conbond6-design.md` |
| znalostní vazby jako data (návrh) | `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md` |
| lexikon vazeb (krok 1 + `podřazení` + `překryv`) | `cb6/lexicon.py` (operátory `třída`, `implikace`, `podřazení`, `překryv` s modalitou; loader, shoda, materializace, `overlap_targets`/`overlap_rules_by_target`) · seed `synonyma.jsonl` (88 ř.) + `podrazeni.jsonl` (18 ř.) + `prekryv.jsonl` (1 ř., `žít⇒potkat_se`) · dialog `!uč a = b \| a => b \| a ~ b \| a < b \| překryv a => b` · `cb6/logic.py Evaluator.overlap_verdict` (query-time join, ne `derive()` — viz HANDOVER § 8/1) |
| výpisové otázky (k ověření J.) | `bench/gold/gen-{alois_jirásek,karel_čapek,božena_němcová}.json` (9, `curated: False`, sada `gen`) → `python -m bench gold-gen --overit --dok …` |
| koncept (proč takhle) | `docs/KONCEPT.md` |
| plán v1 + stav provedení | `docs/superpowers/plans/2026-08-17-conbond6-v1.md` |
| hypotézy a výsledky tahů | `mereni/HYPOTEZY.md` |
| zprávy benche | `mereni/<datum>-<commit>.md/.json` (poslední plný, **stabilní vzorek**: `2026-08-18-3cd63e4`; předchozí `b75d8d5`, `ad5d41b`, `234ca26`) |
| lidské odpovědi auditu | `mereni/audit-<dokument>.json` (otisk → [verdikt, pozn, chápu‑z‑grafu a/n]) |
| keš verdiktů soudce | `mereni/audit-cache.json` (klíč = otisk · soudce · verze promptu) |
| zlaté otázky | `bench/gold/` (+ `PROVENIENCE.md`, `otazky-filtr.log.md`, `gen-*.json`) |
| jádro | `cb6/` — `oracle chronos defaults lexicon read triage discourse memory ground logic recall render dialog cli viewbase_app` + `lang/` (jazyková pravidla jako data, `cb6/lang/cs.json`) |
| bench | `bench/` — `data gold gold_gen qa metrics run graphcheck audit judge diff vazby __main__` |
| **pokročilost chápání vazeb podle mechanismu** (`python -m bench vazby`) | `bench/vazby.py` — zlaté úlohy řazené `prikaz`/`veta`/`korekce`/`graf`; dnes **7/7** (všechny čtyři mechanismy hotové; `graf` validováno na reálném korpusu 27. 9. 2026 — 80/80 návrhů byl šum, proto VYPNUT ve výchozím stavu, `bench run --se-grafem` ho zapne, viz § 6 „‑1“) |
| testy | `tests/` (226 + 2 xfail; hermetické — rozbory `tests/data/parses.json`) |
| data mimo repo | `data/corpus/conBond2` (klon), `data/cache/parses.json` (keš UDPipe, ~75 MB), `data/pamet-graf.json` |
| paralelní větev | conbond5 (`~/Projects/conbond5`, jiné sezení, HEAD c503b68) — do něj nesahat |
| související | inventura conbond0–4: artefakt „Inventura conBond 0–5“ (Claude artifacts, 17. 8.) |

## 2. Prostředí a služby

- **Pozor (27. 9. 2026):** cloudové sezení (claude.ai/code) dostane repo bez
  `.venv`, bez UDPipe, bez Ollama a bez `data/corpus`/`data/cache` (gitignored,
  žijí jen na stroji J.) — `bench`, `audit`, `gold-gen`, `cb6.record` (nové
  rozbory) tam nejdou spustit, jen `pytest` hermeticky z `tests/data/parses.json`.
  Nové sezení v cloudu: `python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'`,
  ověřit `pytest -q`, a v HYPOTEZY/HANDOVER napsat, že měření tahu je jen
  pytest/mypy/pylint (ne QA/unsupported) — dokud služby nejsou po ruce.
  Síťová politika kontejneru zamítá `lindat.mff.cuni.cz` (veřejný UDPipe) i
  `huggingface.co`; `pypi.org`/`files.pythonhosted.org` fungují a **`github.com`
  jde naklonovat přímo** (`git clone https://github.com/...`, anonymní čtení
  veřejných repozitářů přes proxy — funguje i bez `add_repo`; release assety
  a API zůstávají přes `add_repo`). **Nález:** `pip install cs_core_news_sm`
  (spaCy, čistě z PyPI) dá český UD parser bez sítě na LINDAT — ale změřená
  shoda se skutečným UDPipe2 na 177 zaznamenaných větách je jen 50,8 % vět
  přesně / 83,1 % tokenů (`mereni/HYPOTEZY.md` 2026‑09‑27) →
  **nepoužívat na historická čísla** (smísilo by dva parsery v jednom
  srovnání). **`cb6/oracle.py SpacyOracle`** (NN, ne LLM — J.: „systém by
  však měl pracovat bez external LLM“) funguje a je otestovaný (`tests/
  test_spacy_oracle.py`, volitelný extra `spacy-cs`).
  **`bench run --sada wiki --parser spacy` teď FUNGUJE end‑to‑end na
  reálném korpusu** (`data/corpus/conBond2` se v cloudu naklonuje samo —
  `bench/data.py ensure_wiki_corpus` používá plain `git clone`, stejná
  cesta) — vlastní keš (`cache_spacy`), nikdy sdílená s UDPipe2, zpráva má
  nepřehlédnutelné varování v hlavičce a diff proti historii se přeskočí
  (I‑12). Smoke test (2 dok., strop 15): yield 79,64/90,31, audit grafu 0,
  determinismus ano. Použití: nové věty i **skutečné korpusové dokumenty**
  k ověření hypotéz (viz nález níže), pořád NE k nahrazení historických
  UDPipe2 čísel.
- Python 3.11, `.venv` (`pip install -e '.[dev]'`), závislost jen `networkx` (+ dev pytest/mypy/pylint; viewbase editable z `~/Projects/viewBase2/python`).
- **UDPipe** služba z conBond3 na `127.0.0.1:42200` (model `cs_all-ud-2.17-251125`) — jen pro nové rozbory a bench; testy jedou z keše.
- **Ollama** `gemma4:latest` na `127.0.0.1:11434` — soudce auditu a `gold-gen` (27B qwen se do 24 GiB nevejde vedle UDPipe). **Od 27. 9. 2026 výchozí soudce v `bench/config.json` je `claude-cli`/`haiku`** (`bench/judge.py ClaudeCliJudge`, headless `claude -p` — J.: „Ollamu může zastoupit nižší model Claude“), protože cloudová sezení Ollamu nemají; staré nastavení je zachované v config klíči `_ollama_puvodni`, kdyby J. chtěl Ollamu zpátky na svém stroji.
- **Živý graf:** `.venv/bin/python -m cb6.viewbase_app --pamet data/pamet-graf.json --port 8081 [--user workbench]` → http://127.0.0.1:8081/ (viewBase2; dnes paměť se třemi články: Jirásek, Karel Čapek, Josef Čapek). Ukončovat `kill -INT <pid>` (uloží paměť); démon nesmí být zabit bez INT.
  - **18. 8.:** viewBase2 je zase 3.11‑kompatibilní (f‑string se zpětným lomítkem opraven a hlídá ho tam test), takže stačí `.venv`; `.venv314` už není potřeba. Instalace: `.venv/bin/pip install -e ~/Projects/viewBase2/python` — TOTP (`pyotp`, `qrcode`) se dotáhne samo, je to standardní závislost viewBase2.
  - **Uživatel:** `VIEWBASE_USER = "workbench"` v `cb6/viewbase_app.py` (přebije `--user`). Do gitu jde jméno, ne tajemství: TOTP secret a QR vzniknou při první instanciaci v `~/.viewbase/user-<jméno>/` (0600). Naskenovat lze rovnou z konzole: `cat ~/.viewbase/user-workbench/totp-workbench.txt`. Slouží k odemykání zabezpečených oken (`secured=True`), která adaptér zatím nepoužívá.

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

**Věta učí lexikon bez příkazu** (27. 9. 2026, J.: „vše z kontextu diskuse,
bez příkazu“): `cb6/read.py Predication.lex_teach` + `Reader._lex_teach`
rozpozná „X je synonymum/synonymem Y“ (autorita `read`, jmenovaná už od
kroku 1) místo běžného výroku; `cb6/ground.py` zapíše řádek lexikonu a
vrátí placeholder výrok `mood="pattern"` (source pro I‑12, mimo `knowledge()`).
Záporná věta se nenaučí nic. `!uč`/`!role`/`!pravidlo` zůstávají jako
explicitní/debug kanál. Test `tests/test_lex_teach.py` (rozbor ručně
sestavený — viz § 2 poznámka o spaCy). **Pozor:** J. tohle vzápětí upřesnil —
„synonymum“ je pořád KLÍČOVÉ SLOVO, jen bez `!`; `bench vazby` ho proto řadí
jako mezikrok (`veta`), ne jako cíl (§ 6 položka „‑1“, § 7 deník).

**Pokročilost chápání vazeb podle mechanismu** (`python -m bench vazby`,
27. 9. 2026): `bench/vazby.py` řadí zlaté úlohy „naučit vazbu“ podle ODKUD
se poznatek vzal (`prikaz`/`veta`/`korekce`/`graf`), ne jedním číslem —
ukazuje přímo, kam vývoj cílit. **`korekce` hotovo** (`cb6/dialog.py
Session._learn_from_correction`): oprava „Ne, X namísto Y“ o TÉMŽ podmětu
(a beze změny ostatních sdílených rolí) učí vazbu mezi starým a novým
predikátem, síla **`related`** (opatrně — jedna oprava nestačí na
`same`/`implies`, I‑3). Dnes **6/7** (`graf` jediný zbývající cíl).

**Krok 2 (částečně): operátor `překryv`** (27. 9. 2026, fragmenty bez UDPipe):
`cb6/lexicon.py` — `Link.modality` (JSON `modalita`), validace `překryv`
(2 argy, síla `implies`, modalita musí být `možnost`), `Lexicon.overlap_targets`/
`overlap_rules_by_target`; seed `cb6/lexikon/prekryv.jsonl` (`žít ⇒ potkat_se`).
`cb6/logic.py` — `Evaluator.overlap_verdict` (**query-time join**, ne
`derive()`: dotaz s `modality="možnost"` a rolí `kdo` o 2 termech → `chronos.
overlap` na jejich `žít.kdy` → ANO/NE/`None`→NEVÍM; faktická otázka bez
modality NEprojde — overlap není důkaz skutečného setkání). `bench/
graphcheck.py` — `lex_path` chodí i po `překryv`, nová jádra `overlap`/
`no_overlap` (`_time_overlap` čistě z `t_start`/`t_end`). Čtení věty
(„Mohli se X a Y potkat?“ z reálného textu) **není hotové** — čeká na UDPipe;
tenhle krok je jen logická vrstva, ověřená `tests/test_prekryv.py` (4
fragmenty, `Statement`/`Memory` přímou konstrukcí, `check_graph`/`check_answer`
0). Dialogová vstupní strana (`!uč překryv a => b`, `Memory.add_link` s
volitelnou `modality`) hotová, `tests/test_dialog.py::test_prekryv_command`.
Podrobně proč query-time (ne `derive()`) v HYPOTEZY 2026-09-27 a § 8 níže.

**Jazyk jako data** (27. 9. 2026, `cb6/lang/`): čtecí tabulky (`ROLE_BY_CASE`,
`DETERMINER_QUANT`, `PARTICLES`, `WH`, `LIST_VERBS`, `PLACE_NOUNS`,
`CONDITIONAL_MARKERS`, `ATTITUDE_VERBS`… + chronosu `MONTHS`/`WEEKDAYS`/
`SEASONS`/`RELATIVE_DAYS`/`TIME_NOUNS`) přesunuty z Python literálů do
`cb6/lang/cs.json`; `load_language(code)` (kešované, `FileNotFoundError` na
neznámý jazyk), `defaults.py`/`chronos.py` jen re‑exportují pod starými jmény
→ `read.py`/`triage.py`/`logic.py`/`memory.py` beze změny. Vnitřní klíče rolí
(`kde`, `kdo`, `co`…) zůstávají opaque symboly grafu; jazykové je jen čtení
z povrchového tvaru. `cb6/chronos.overlap(a, b)` — primitiv pro budoucí
lexikonový operátor `překryv` (protnutí dvou období na časové ose).

**Krok 3 (částečně) — lexikon vztahových substantiv** (27. 9. 2026,
`cb6/lang/cs.json relational_nouns`, 34 slov: otec/matka/syn/dcera/
bratr/sestra/manžel(ka)/tchán/tchyně/zeť/snacha/švagr(ová)/děd(eček)/
bab(ička)/vnuk/vnučka/strýc/teta/synovec/neteř/…): genitivní doplněk
vztahového substantiva („manžel **dcery**“) je teď určující argument
(role `čí` na hlavním výroku, `TermSpec.rel_owner` → `ground.py`), ne
zahozená vedlejší predikace `nmod:Gen` (`Reader._is_relational_gen_arg`
v `read.py`). Koordinovaný genitiv („manžela nebo manželky“) se
NEpřebírá — zůstává staré cestě, disjunkce ji zamítne stejně jako dřív.
Ověřeno na `vztahy_příbuzenské.txt`: 2/16 nedisjunktivních vět už nemá
sesterský REJECTED výrok (`mereni/HYPOTEZY.md` 27. 9. 2026).

**G‑3 opraven** (27. 9. 2026, tentýž krok, pokračování): „Jeho bratr
Josef Čapek byl malíř.“ dřív slepilo přístavek do jednoho jména skupiny
(„bratr Josef Čapek“) — Josef Čapek jako entita nikdy nevznikl, „byl
malíř“ viselo na neidentifikovatelné skupině. `Reader._relational_name`
(nová „hlava“ pro `title` vedle `_title_of`): vztahové substantivum +
přivlastnění (zájmeno/adj) + `flat` vlastní jméno → stejná cesta jako
nominativ jmenovací (entita + `cls`). `Grounder._relational_fact`:
entita s `cls` i `possessor` dostane navíc SKUTEČNÝ vztahový výrok
(`bratr(kdo=Josef Čapek, čí=Karel Čapek)`, SAFE/HYPOTHESIS podle
jednoznačnosti vlastníka — `_owner_nodes` sdíleno s `_resolve_
possessed`). Ověřeno na 4 dalších reálných výskytech v korpusu (Hašek,
Havlíček Borovský, Kundera, Bezruč), ne jen na 1 zaznamenané větě, jak
HANDOVER dřív varoval. Nový test `tests/test_dialog_g.py::test_g3_
pristavek_je_vztah_ne_slepene_jmeno`.

**Operátor `inverze` hotový na logické vrstvě** (27. 9. 2026, pokračování
tentýž den): `cb6/lexicon.py` (validace, `inverze_rules_by_target`/
`inverze_targets`), seed `cb6/lexikon/inverze.jsonl` (12 řádků —
`bratr`/`sestra`→`sourozenec`, `otec`/`matka`→`dítě`, `syn`/`dcera`→
`rodič`, `děd`/`bába`→`vnouče`, `vnuk`/`vnučka`→`prarodič`, cíl rodově
neutrální kde zdroj neurčuje rod druhé strany; `manžel`↔`manželka`
přesný pár), `cb6/logic.py Evaluator.inverze_verdict` (query-time join,
stejná architektura jako `overlap_verdict`), `bench/graphcheck.py`
(`lex_path` + `inverze`, nový obecný hard krok `role:<jméno>` — ověřuje
přesné svázání faktu s argumenty, ne jen že fakt existuje), `!uč inverze
bratr => sourozenec`. Testováno `tests/test_inverze.py` (4, ruční
`Statement`/`Memory` jako `test_prekryv.py`) — včetně že ŠPATNÝ SMĚR
dá NEVÍM, ne falešné ANO. **Chybí jen čtení otázky z reálného textu**
(„Je X sourozenec Y?“) — stejná mez jako `překryv`, čeká na reálné
otázky (od J. nebo nález v korpusu), ne na dohad.

## 6. Otevřené tahy (pořadí podle toho, co ukázal bench)

-1. **(VALIDOVÁNO 27. 9. 2026 — mechanismus `graf` vypnut ve výchozím stavu,
   viz HYPOTEZY.)** `bench/graf_audit.py` (nový nástroj) proběhl na celé
   reálné sadě wiki (16 dokumentů, ~180 000 slov, `--parser spacy`, žádný
   `--strop`): **80 návrhů**. Ruční čtení dohledaných zdrojových vět u
   vzorku (~35, rozprostřeno přes `alois_jirásek`, `bohumil_hrabal`,
   `božena_němcová`, `sopka`) **neukázalo ani jednu skutečnou parafrázi** —
   vzorec „stejné `kdo` + 1 další role, jiný predikát“ na reálném textu
   skoro vždy chytí dvě věty o téže osobě/tématu v jiné souvislosti
   (jiná životní událost sdílející místo/datum, jiný dílčí fakt sdílející
   objekt), ne totéž řečeno jinak — dvojitá role navíc oproti `korekce`
   nestačí. U dvou dokumentů (`božena_němcová` „naleznout ~ oslovit“,
   `sopka` řada impersonálních vazeb typu „jedná_se ~ …“) návrh navíc
   ukázal na jinou, samostatnou věc k prošetření: `kdo` role se u
   neosobních/reflexivních konstrukcí („jedná se o“, „dochází k“) zřejmě
   sbíhá na téma dokumentu místo aby zůstala prázdná — netýká se
   mechanismu `graf` samotného, ale je to potenciální zdroj přesnosti
   jinde; nezkoumáno dál v tomhle tahu.
   **Rozhodnutí (pravidlo 2 — recall bez pravdivosti se nepočítá):**
   `_GRAF_SUGGESTIONS_ENABLED` výchozí `False` (`cb6/dialog.py`); kód i
   zlatá úloha `bench vazby` (`graf:parafraze`) zůstávají a dál dokazují,
   že KÓD tuhle schopnost má, jen se nepoužívá produkčně. Zapnutelné pro
   přeměření přes `bench run --se-grafem` (dřív `--bez-graf`, obráceně).
   **Další tah, pokud se k tomu vrátit:** kritérium potřebuje víc než shodu
   dvou rolí — např. požadovat shodu VĚTNÉ POZICE (bezprostředně sousední
   věty) nebo sémantickou blízkost predikátů (embedding), ne čistě
   topologickou shodu rolí.
0. **(priorita až budou služby) Multilingvnost + NN jako
   extraktor struktury** — J.: NN smí dělat skoro vše (parsing, extrakci,
   konverzaci, i pro víc jazyků), ale nikdy „znalost" — ta zůstává výhradně
   v grafu (I‑9 zobecněné). Krok 1 hotový (`cb6/lang/cs.json` — jazyk jako
   data, viz § 5, § 7). Zbývá: (a) druhý jazyk (`cb6/lang/en.json`) + ověřit,
   že `read.py`/`triage.py` fakt nemají nic natvrdo českého mimo `D.*`/
   `chronos.*` (dnešní průchod 28+7 míst to potvrdil, ale nový jazyk je
   opravdový test); (b) NN‑extraktor: buď UDPipe model pro druhý jazyk (stejná
   architektura čtení), nebo LLM extrakce do stejného schématu `Predication`
   (větší krok — potřebuje bench na obou jazycích, aby šlo měřit, že LLM
   extrakce nepřidává nepodložené výroky víc než UDPipe cesta). Blokováno tuhle
   relaci chybějícími službami (UDPipe/Ollama/korpus) — čeká na sezení se
   službami. **Dílčí odpověď 27. 9. 2026** (J.: „lze read.py nahradit
   vztahovou NN? jde mi o embeding read vztahů do nn“): `bench distill`
   (destilační dataset parse→`Predication`, `read.py` jako učitel) +
   `bench probe` (lineární sonda: role z `read.py` ← `tok2vec` embedding
   spaCy parseru, bez tréninku čehokoli nového). Výsledek na 56 243
   tokenech (10 dok.): sonda nad IZOLOVANÝM tokenem +18,5 b.b. nad
   základnou, ale slabá u nejdůležitějších rolí (`kdo` recall 0,29, `co`
   jen 0,09) — nevidí strukturu (kdo je podmět vs. předmět), jen token.
   **Krok „hrana, ne token“ (týž den, J.: „conditioning je abstrakce nad
   daty, mělo by jít už na současném vzorku“):** `Example.head_vector`/
   `deprel`, `--features edge` (token + rodič + one‑hot deprelu) —
   POTVRZENO na plném vzorku: `kdo` recall 0,29→**0,46** (+17 b.b.), `co`
   0,08→**0,37** (+29 b.b.), obyčejná LR 70,6 %→76,4 %. **Závěr:** `read.py`
   se dnes nedá nahradit prostou lineární klasifikací nad IZOLOVANÝM
   tokenem, ale s hranou (embedding + rodič + deprel) už signál pokrývá
   skoro polovinu případů — částečná, ne úplná náhrada.
   **Krok „formovatelná dialogem?“ (pokračování, J.: „nemůžeme již vyrobit
   lingvistickou DNA s využitím NN, kterou bychom mohli formovat
   dialogem?“):** `bench/probe.py::correction_experiment` (`--korekce N`)
   — vzít N špatně klasifikovaných `kdo`/`co` příkladů, KAŽDÝ zvlášť
   přesunout do tréninku („dialogová korekce“), přetrénovat, změřit
   opravu + dopad na zbytek. Výsledek (5 dok., 35 693 tokenů, 12 korekcí):
   **jen 3/12 (25 %) se opravilo** (lineární model má globální hranici,
   jeden bod z desítek tisíc ji těžko pohne, leda na okraji), ale **žádné
   zapomnění** (dopad na zbytek held‑out −0,0003 ± 0,0006, šum kolem
   nuly) — korekce nikdy neškodí, jen nejsou dost silné samy o sobě.
   **Závěr pro architekturu:** „lingvistická DNA formovaná dialogem“ ve
   smyslu „jedna oprava spolehlivě přetvoří chování" takhle NEFUNGUJE;
   potřebovala by buď exemplářovou/výjimkovou vrstvu NAD modelem (jako
   dnešní grafový lexikon — vítězí explicitně, ne hlasováním), nebo
   váhované přeučení. Ani jedno není dnešní krok. Role `čí` (krok 3) má
   jen 45 příkladů v tomhle vzorku — na učení zatím nestačí, zůstává na
   pravidle. Podrobně `mereni/HYPOTEZY.md` 27. 9. 2026 (tři pokračování).
1. **Lidský audit** — J.: `python -m bench audit --dok alois_jirásek --rucne` (a druhý dokument), min. 30 výroků; pak zpráva hlásí shodu soudce/člověk a „nechápu z grafu“ %.
2. **Ověření generovaných otázek** — `python -m bench gold-gen --dok karel_čapek --n 12` → `--overit` (kurátorované číslo 29/130 je malé a korpus 7/90 tvrdý).
3. Zbývající chyby precision (z auditu): kvantifikátor ∀ z „všechna jeho dramata“ (∀ bez omezení přivlastněním), plošná koordinace (`kdo: Petr+Karel` i tam, kde jde o dvě klauze — „otcem byl Josef…, matkou Vincencie“), vztažné věty (`kdo:∀sousoší`), participia jako predikáty.
4. Nálezy dialogu G: G‑1 otázka „Kdy napsal R.U.R.?“ čte R.U.R. jako podmět; G‑2 funkční role (narodit_se.kde/kdy) → hlásit konflikt; ~~G‑3 „Jeho bratr Josef Čapek“ → přístavek přilepen ke jménu (rodinné vztahy tak v grafu nejsou)~~ **OPRAVENO 27. 9. 2026** (§ 5 „Krok 3“, `mereni/HYPOTEZY.md`); G‑4 `v Lidových novinách` není místo (učení role / instituce).
5. Prostor modelů pro disjunkci/ekvivalenci/kardinalitu (přenos `conBond3/cb_logic/models.py`) — dnes REJECTED s důvodem.
6. Adaptéry conbond1/conbond4 pro zpětný běh QA (Task 12 — neproveden).
7. Valence jako data (`valence.json` conbond1 / VALLEX), relativní čas (conbond1 chronos), nominalizace, rekurze v dotazu (jellyAI3 SubQuery) — každý jako měřený tah, až bench ukáže potřebu.
8. **Znalostní vazby jako data** (návrh `2026-08-17-znalostni-vazby-design.md`): **krok 1 hotový** (synonyma se sílou, lexikon, materializace — viz § 5), **`podřazení` hotové** (výpis), **`překryv` hotový na logické vrstvě** (operátor + query-time join, viz § 5 „Krok 2 (částečně)“ a § 8/1) — **chybí jen čtení věty/otázky z reálného textu** (potřebuje UDPipe, žádná zdejší relace ho neměla). Dál po službách: napojit `překryv` do `read.py` (rozpoznat „Mohli se X a Y potkat?“ jako otázku s `modality=možnost`, „žil v letech…“ jako zdroj `žít.kdy`) a změřit na etalonu; **`porovnání` — primitiv hotový** (`cb6/quantity.py`: `Quantity`/`dimension_of`/`to_base`/`compare`, viz HYPOTEZY 27. 9. 2026), **operátor sám záměrně ne** — směr porovnání (`≤`/`≥`/`=`) ke kterému derivovanému predikátu čeká na reálnou větu, ne na dohad; pak veličiny do čtení ("vejde se", "Jaká je délka") → krok 3 příbuzenství (inverze/skládání, G‑3 — **pozor, potřebuje 3 premisy, viz § 8/1**). **Prerekvizita zjištěná 27. 9. 2026:** čtení dnes z „Jeho bratr Josef Čapek“ nevytáhne ŽÁDNÝ vztahový predikát (`bratr(Josef, Karel)`) — jen typování `∈ bratr` (nominativ jmenovací) + obecné `mít`; bez toho nemá `inverze`/`skládání` na čem pracovat. Jen JEDNA taková věta je zaznamenaná (`tests/data/parses.json`) — moc tenký vzorek na novou čtecí konstrukci bez druhého/třetího ověření skutečným textem. **Krok 3 = nejdřív tahle čtecí konstrukce (kinship nouns → relační predikát, ne jen typing), pak teprve operátory.** **Potvrzeno na reálném korpusu 27. 9. 2026** (`bench --parser spacy`, 28/65 dok., 4020 vět, `mereni/HYPOTEZY.md`): naivní „SAFE vedle REJECTED nmod“ je 83 % vět, ale to jen ukazuje, že `nmod` se právem zahazuje jako ozdoba skoro vždy — **jediná chybějící věc je seznam vztahových substantiv**, u nichž genitiv NENÍ ozdoba, ale určující argument (mimo `nmod`-obecnou heuristiku). Bez tohohle seznamu je jakákoli prevalence jen artefakt špatné metriky. **Seznam hotový** (`RELATIONAL_NOUNS`, § 5 „Krok 3 (částečně)“) — genitiv se teď adoptuje jako role `čí`, ověřeno na `vztahy_příbuzenské.txt`. **G‑3 taky opraven** (27. 9. 2026, § 5): „Jeho bratr Josef Čapek“ dá entitu Josef Čapek + výrok `bratr(kdo=Josef Čapek, čí=Karel Čapek)`, ne slepené jméno skupiny — ověřeno na 4 dalších reálných výskytech v korpusu (`mereni/HYPOTEZY.md`), ne jen na 1 zaznamenané větě. **Operátor `inverze` hotový na logické vrstvě** (viz § 5 výše) — role `čí` a predikáty vztahových substantiv se teď ZAPISUJÍ i DOTAZUJÍ (query-time join, `Evaluator.inverze_verdict`), otestováno na ruční paměti. **Zbývá jen čtení otázky z reálného textu** („Je X sourozenec Y?“) — stejná mez jako `překryv` (krok 2): logika hotová, čtecí strana čeká na reálné otázky (od J. nebo nález v korpusu), ne na dohad. → antonyma až na otázku.

**Krok 5 hotový** (27. 9. 2026): `Memory.rules`/`Rule` třída **zanikla úplně** — most `!pravidlo jet(kam:X) => být(kde:X)` je teď řádek lexikonu (`implikace` + `role_map`, `Lexicon.bridge_rules()`), materializovaný jako `vazba` v exportu s tvrdým krokem `lex` (dřív žádná strojová rekonstrukce — spec sám to označil za „částečnou“ provenienci, realita byla horší: žádná). `kind="rule"` (podmínkové věty z textu, `derive()`) VĚDOMĚ nesjednoceno — jiná věc (vzor s vázanými entitami, ne jméno-na-jméno vazba) a je už dnes plně graf-viditelný. Počet míst, kde „vazby“ žily, kleslo ze čtyř na dvě (lexikon jako data + `kind=rule` jako odvození nad entitami) — přesně cíl návrhu. Podrobně `mereni/HYPOTEZY.md` 27. 9. 2026.

**Krok 6 hotový — render odpovědí, méně dat víc klidu** (27. 9. 2026,
J.: „krok 6 render odpovědí — méně dat, víc klidu“): `cb6/render.py`
NEVÍM/MOŽNÁ — `KNOWN_SHOWN_MAX = 3` (dřív natvrdo 5) blízkých výroků,
bez zdroje (`!ukaž <id>` dá zdroj tomu, kdo ho chce), zbytek se jen
spočítá („+ N další“), nic se neztrácí z I‑12, jen se defaultně
neukazuje navíc; `missing`/`notes` sloučené do jedné řádky místo řádky
na položku. ANO/NE proof-rendering (má pinované testy na zdroj/id)
záměrně beze změny — bezpečnější krok, ne vyčerpání tématu. `docs/
UKAZKY.md` čeká na regeneraci (`bench ukazky` potřebuje UDPipe/keš na
přesné věty scén, chybí tuhle relaci — stejná mez jako zbytek dneška).
Podrobně `mereni/HYPOTEZY.md` 27. 9. 2026.

**Krok 7 hotový — neosobní `_se` v přítomném čase nedostane `kdo`** (27. 9.
2026, nález z validace mechanismu `graf` výše): `_prodrop` (`cb6/read.py`)
chtěl nedosazovat `kdo` u neosobních vět s `expl:pv` (`_lemma_with_refl`
dá `pred` s příponou `_se`/`_si` — jednat_se, odehrávat_se, vyskytovat_se,
nacházet_se…), ale podmínka žádala `Gender == "Neut"`, a čeština u
PŘÍTOMNÉHO času rod vůbec neznačí (`Gender` je `None` — jen l‑příčestí
minulého času ho nese). V praxi to znamenalo, že skoro KAŽDÁ neosobní věta
v encyklopedickém textu (převážně přítomný čas: „Jedná se o…“, „Vyskytuje
se…“, „Nachází se…“) dostala `kdo` doplněný na TÉMA DOKUMENTU
(`ground.py._resolve_pron`, poslední záchrana bez kandidáta) — přesně
mechanismus, který dělal z mechanismu `graf` (validace výše) skoro čistý
šum: dvě neosobní věty o různých faktech téhož dokumentu sdílely `kdo`
=téma, a `graf` to bralo jako parafrázi. Oprava: podmínka teď přijímá
`gender in (None, "Neut")` (bezpečné — `_se`/`_si` z `expl:pv` je podle UD
definice vždy neosobní/mediopasivní značka, ne skutečný zvratný předmět;
skutečné zvratné sloveso typu „myje se“ by mělo `se` v roli `obj`, ne
`expl:pv`, takže by `_se` příponu vůbec nedostalo — ověřeno v `_lemma_with_
refl`). Nový hermetický test `tests/test_read.py::test_neosobni_se_v_
pritomnem_case_nedostane_kdo` (ruční UD, ověřeno křížově proti `SpacyOracle`).
Reprodukce i oprava ověřeny přímo na `Session.ingest` („Jedná se o pomalý
pohyb…“ dřív dostalo `kdo=Karel Čapek“ z tématu dokumentu, teď `kdo=None`).
Pytest 223+2xfail → **224+2xfail**, mypy/pylint beze regrese. **Přeměřeno
na celém korpusu** (`bench/graf_audit.py`, mechanismus dočasně zapnutý jen
pro dobu skenu — jinak by díky vypnutí ve výchozím stavu vždy vrátil 0):
**80 → 71 návrhů** (`sopka` 16→10, `egon_hostovský` 4→2, `pes_domácí`
5→4). Pokles, ne vymizení — většina 80 (`božena_němcová` 21, beze změny)
byla biografická náhoda se SKUTEČNÝM podmětem, na tu tahle oprava nemíří.
**Nezkoumáno dál:** neosobní slovesa BEZ `se` (`docházet k`, `nastávat`)
stejný problém mít můžou, ale nemají spolehlivý morfologický/UD signál
jako `expl:pv` — potřebovaly by lexikon neosobních sloves (jako `is_time_
noun`/`PLACE_NOUNS`), ne dohad; ponecháno jako další tah. Podrobně
`mereni/HYPOTEZY.md` 27. 9. 2026 (pokračování).

**Krok 8 hotový — vztahové substantivum bez přivlastnění a koordinovaný
genitivní argument** (27. 9. 2026, nález ze živé ukázky pro J.): dvě mezery
ve stejné rodině (`cb6/read.py`, kolem G‑3/krok 3):
(a) `_relational_name` vyžadovalo přivlastnění („Jeho bratr…“) — holé
„Matka Božena Čapková sbírala…“ (bez „Jeho“) nechalo `_term` slít
„matka“+„Božena“+„Čapková“ do JEDNOHO jména jako obyčejné víceslovné
jméno (stejný vzor jako „Karel Čapek“), takže Božena Čapková nešla najít
jako entita. Uvolněno: přivlastnění zůstává NEPOVINNÉ — entita a `cls`
(„Božena Čapková ∈ matka“) vzniknou i bez něj, `_relational_fact` (vztahový
výrok „čí“) dál běží jen když přivlastnění JE (`t.possessor is not None`,
ground.py beze změny) — bez zájmena systém KOHO je čí matka nepozná, to
čeká na odvození z tématu dokumentu (jiný, neměřený krok).
(b) `_is_relational_gen_arg` odmítalo KAŽDOU koordinaci pod genitivním
argumentem („manžela nebo manželky“ — dvě různé osoby, správně odmítnuto),
ale stejně tak i „malíře A SPISOVATELE Josefa Čapka“ (dva POPISY JEDNÉ
osoby, jméno visí jen na druhém konjunktu) — Josef Čapek tak z výroku
úplně zmizel. Oprava: koordinace se přebere, jen když je slučovací (ne
„nebo“/„či“/„anebo“/„popřípadě“) A jméno (`flat` PROPN) visí přesně na
JEDNOM konjunktu (`_named_conjunct`); jinak (opravdu dvě osoby, nebo obě/
žádná se jménem) zůstává odmítnuto jako dřív. **Zbytkové zjednodušení**
(přiznané, ne opravené): `rel_owner` v tomhle případě je pořád `spisovatel
Josef Čapek“ jako skupina (ne čistá entita „Josef Čapek“ s `cls`), protože
`spisovatel`/`malíř` nejsou v `RELATIONAL_NOUNS` — širší zobecnění (`NOUN`
+ `flat` PROPN vždy = titul + jméno, ne jen u vztahových substantiv) by
zasáhlo VŠECHNY profesní tituly v korpusu bez potvrzení na reálném textu,
takže zůstává jen u vztahových substantiv (opatrnost, ne dohad). Josef
Čapek je nicméně teď DOHLEDATELNÝ (`čí` role), dřív úplně chyběl.
Ověřeno end‑to‑end (`Session.ingest`): „Matka Božena Čapková sbírala…“
→ entita `Božena Čapková ∈ matka`, výrok `sbírat(kdo=Božena Čapková)`;
„Byl mladším bratrem malíře a spisovatele Josefa Čapka.“ → `být(kdo=Karel
Čapek, co=∃bratr, čí=spisovatel Josef Čapek)`. Nové testy
`tests/test_read.py::test_relational_noun_bez_privlastneni_da_entitu_ne_
slepene_jmeno` a `::test_relational_gen_arg_koordinovany_popis_jedne_osoby`
(ruční UD, ověřeno křížově proti `SpacyOracle`). Pytest 224+2xfail →
**226+2xfail**, mypy/pylint beze regrese (jen posun řádků + kategorie už
použité jinde v souboru). Podrobně `mereni/HYPOTEZY.md` 27. 9. 2026.
9. **Výpis — zbytky z reálného textu:** typing z nadpisů/seznamů („Wikilivres: Josef Čapek: díla“ → Josef Čapek ∈ dílo — paskvil z appos), „Krakatit je román.“ čtené jako obecná věta (⊆ místo ∈; velké písmeno na začátku věty není důkaz jména), „R.U.R. (… 1920) –“ → `zemřít(R.U.R., 1920)` (životopisná závorka u díla); imperativ s vedlejší větou („Vyjmenuj, co napsal…“); ověření 9 gen otázek J.
10. **Převzít z conbond5 po jedné konstrukci** (srovnávací slova, veličiny s jednotkami, definice/vztahová jména z textu, meta‑otázky, obnova diakritiky, elipsa přísudku) — každou s číslem před/po na stabilním vzorku; etalon 14/32 vs conbond5 24/32 je přesně tento rozdíl.
11. **(housekeeping, čeká na službu) `docs/UKAZKY.md` regenerovat** (`python -m bench ukazky`) — spadne na `segmentace … není v data/cache/parses.json` (scény potřebují přesné věty z živého UDPipe/keše, které tahle relace nemá). Až bude UDPipe po ruce: přegenerovat, ověřit, že „krok 6“ (§ 5) je v ukázkách vidět (kratší NEVÍM sekce, bez zdroje u „vím:“).

## 7. Deník rozhodnutí

- 17. 8. — J.: cíle dává on, cestu rozhoduje Claude a měří benchem (viz paměť `conbond-goals-only-claude-decides-how`). Všechny cesty otevřené, včetně NN, rozhoduje měření.
- 17. 8. — conbond6 = klon conbond5 s historií; obě větve běží nezávisle, smějí se inspirovat; do conbond5 conbond6 nesahá.
- 17. 8. — Statusy `SAFE/HYPOTHESIS/REJECTED` jako pole `claim` (pole `status` v conbond5 je životní cyklus); `RESIDUE`/`OPEN` jsou vrstvy, ne statusy.
- 17. 8. — Soudce = Ollama gemma4 (27B se nevejde do paměti); prompt v2 (nevyslovený podmět z kontextu, závorka s roky) — změna měřidla zapsaná v HYPOTEZY.
- 27. 9. 2026 — J.: „Ollamu může zastoupit nižší model Claude.“ `ClaudeCliJudge` (headless `claude -p`, model `haiku`) je nový výchozí soudce (`bench/judge.py`, `bench/config.json`) — cloudová sezení nemají Ollamu ani syrový `ANTHROPIC_API_KEY` pro SDK (`ClaudeJudge`), ale mají autentizaci vlastní CLI relace. `--tools ""` + `cwd` mimo repo, aby CLAUDE.md tohohle projektu soudce nesvedlo z role (ověřeno prakticky). Viz HYPOTEZY.
- 27. 9. 2026 — J. upřesnil: „systém by však měl pracovat bez external LLM.“ Čteno jako potvrzení I‑9 pro krok 6 (NN extraktor struktury): extrakce má stát na skutečné NN (trénovaný parser jako spaCy/UDPipe), ne na živém LLM volání — LLM zůstává jen soudce/generátor otázek (bench, offline), nikdy součást odpovídání za běhu. `ClaudeCliJudge` tohle neporušuje (je jen v `bench/judge.py`). Dotaženo: `cb6.oracle.SpacyOracle` opraveno a otestováno (dvě tiché chyby nalezené a spravené), pořád NEnasazeno na historická čísla.
- 17. 8. — Kurátorované a automatické otázky se vykazují zvlášť; auto po valenčním filtru; LM‑generované jen po lidském ověření (požadavek J.: otázky s hlavou a patou).
- 17. 8. — `read.py` v1 beze změny konstrukcí; opravy jen tam, kde výroky lhaly (precision).
- 17. 8. — viewBase → viewBase2 (github.com/alchy/viewBase2), oblasti podle dokumentu (`skupina`).
- 17. 8. — Vzorek auditu se vybírá po větách se seedem = dokument (dřív seed = commit → každý commit jiných 400 výroků, ±5 b. šum). Čísla před 234ca26 nejsou navzájem srovnatelná; od 234ca26 ano.
- 17. 8. — ∀ z generického prézentu jen v jednoduché obecné větě (kořen, nekoordinovaný podmět, bez PROPN); hlavní predikace 35 → 31–32 % nepodložených.
- 17. 8. — Návrh conbond5 „Q(A,B) ⇐ TEST(…)“ přijat jako operátory `překryv`/`porovnání` v lexikonu vazeb; pravidlo je řádek dat s modalitou a proveniencí, materializovaný do grafu při použití; ne pátý slovník. Síla vazby `same/implies/related` (dnešní `SYNONYMS` je únik precision).
- 17. 8. — conbond5 (paralelně) jde cestou šíře konstrukcí (ruční otázky 59/70); conbond6 cestou věrnosti; další tah conbond6 = přebírat konstrukce z conbond5 po jedné přes bránu benche.
- 17. 8. (večer) — J.: chování jako „co znamená všechny — výpis děl“ má jít definovat měkce z konzole, ne kódem. Rozhodnutí: *znalost* (drama ⊆ dílo) je řádek lexikonu `!uč a < b` (operátor `podřazení`); *čtení* („která N“ = díra s omezením, rozkaz výpisu = otázka) zůstává kód a měří se — z konzole se parser vysvětlit nedá; „všechny“ samo nic nepotřebuje, `enumerate` vypíše všechny doložené výplně. Výpis podle tématu dokumentu je přiznaná výchozí volba (články díla jen vyjmenovávají), asociace jen přes výrok `kdo/co`, ne přes libovolný sdílený výrok (na reálném textu by „Josef Čapek“ byl dílem Karla).
- 27. 9. 2026 — J. upřesnil: „příkazy učení nebo rozšiřování znalosti musí
  vycházet z kontextu věty nebo dialogu a nesmí to být klíčová slova.“ Tím
  padá i „X je synonymum Y“ jako cílový mechanismus — je to pořád klíčové
  slovo (`synonymum`), jen bez `!`. Zavedený `bench vazby` (§ níže, nový
  soubor `bench/vazby.py`) tohle měří: řadí zlaté úlohy podle mechanismu
  (`prikaz`/`veta`/`korekce`/`graf`) a `veta` (klíčové slovo v běžné větě)
  je označená jako mezikrok, ne cíl — cíl jsou `korekce` (oprava v dialogu
  učí vazbu mezi starým a novým predikátem) a `graf` (parafráze ve dvou
  větách bez jakékoli věty o vazbě) — obojí dnes 0/1, to je ukazatel směru.
- 27. 9. 2026 — J.: systém má být multilingvní, jazyková pravidla oddělená per
  jazyk jako JSON; NN smí nést skoro celou strukturní/konverzační vrstvu
  (parsing, extrakci — i pro autonomní průběžné rozšiřování znalostní báze),
  ale nikdy „znalost" — ta zůstává výhradně v grafu. Rozhodnutí Claude: vnitřní
  klíče rolí (`kde`, `kdo`, `co`…) a schéma grafu zůstávají opaque symboly, ne
  „čeština" — neměnit je (obří, invazivní refaktor bez jasného přínosu); mění
  se jen ČTECÍ tabulky (`defaults.py`, `chronos.py`), přesně stylem, jaký už
  platil pro `cb6/lexicon.py` (vazby jako data). Sezení bez UDPipe/Ollama/
  korpusu (cloud) → hotov jen krok 1 (`cb6/lang/`), beze změny chování,
  měřeno pytestem/mypy/pylint, ne bench číslem (viz HYPOTEZY 2026‑09‑27).
- 17. 8. — Lexikon krok 1: síla vazby se rozhoduje podle významu páru, ne podle počtu zásahů (např. `pracovat ~ působit` same — životopisné „působil v/jako“; jiné významy chrání rámec rolí; `absolvovat`, `vyhrát`, `uvést`, `dostat`… zváženy jednotlivě, viz `pozn` v seedu). Shoda přes `implies` snižuje stupeň důkazu na `derived` (je to odvození, ne záměna). Otázka je vždy první argument shody (`same_pred(dotaz, výrok)`); u můstkových pravidel se pořadí opravilo (`dst_pred` je výrok). Použitý řádek se materializuje i při dotazu (uzel `vazba` v exportu) — jinak by krok `lex` nebyl z grafu doložitelný; nepoužité seed řádky graf nezatěžují.
- 27. 9. 2026 (pokračování) — Živá ukázka pro J. (dialog s reálným textem)
  ukázala dvě mezery u vztahových substantiv: bez přivlastnění se jméno
  slilo s titulem („matka Božena Čapková“ jedno jméno); koordinovaný
  genitiv u JEDNÉ osoby („malíře a spisovatele Josefa Čapka“) se zamítal
  stejně jako u dvou osob. Obojí opraveno (§ 5 „Krok 8“) — přivlastnění
  teď nepovinné (jen typing, ne vztahový výrok bez něj), koordinace se
  přebere, když jméno visí přesně na jednom konjunktu a spojka je
  slučovací. Vědomě NEzobecněno na profesní tituly mimo `RELATIONAL_
  NOUNS` (`spisovatel`, `malíř`…) — čekalo by na potvrzení na reálném
  korpusu, ne na dohad.
- 27. 9. 2026 (pokračování) — Vedlejší nález z validace `graf`: `_prodrop`
  (`cb6/read.py`) nechytil neosobní `_se` konstrukce v přítomném čase
  (čeština v přítomném čase neznačí rod, podmínka žádala `Gender=="Neut"`)
  — `kdo` se tak defaultoval na téma dokumentu i tam, kde věta (\"jedná
  se o…\", \"vyskytuje se…\") nemá logický podmět vůbec. Oprava:
  `gender in (None, "Neut")`, bezpečné díky UD `expl:pv` (vždy neosobní
  značka, ne skutečný zvratný předmět). Viz § 5 „Krok 7“, HYPOTEZY.
- 27. 9. 2026 (pokračování) — Mechanismus `graf` (§ 6 „‑1“) změřen na celém
  reálném korpusu wiki (16 dok., ~180 000 slov, `bench/graf_audit.py`): 80
  návrhů, ruční čtení vzorku ukázalo 0 skutečných parafrází — opatrnostní
  „dvě role místo jedné" fragmentový test prošel (7/7), na reálném textu
  ne. Rozhodnutí: `_GRAF_SUGGESTIONS_ENABLED` výchozí `False`; kód a zlatá
  úloha zůstávají (dokazují schopnost KÓDU), produkční ingest ho jen
  nepoužívá, dokud kritérium nebude přesnější než topologická shoda rolí.
  Ablace přejmenována `--bez-graf` → `--se-grafem` (teď je to opt-in, ne
  ablace něčeho zapnutého). Viz `mereni/HYPOTEZY.md` 2026‑09‑27.

## 8. Kritické zhodnocení architektury (J., 27. 9. 2026 — „kriticky hodnoť“)

Zapsáno po krok-2 fragmentu (`překryv`), na žádost J. Ne vyčerpávající audit —
tři konkrétní nálezy z dnešní práce, každý s návrhem, co by ho ověřilo.

1. **`Statement.derived_from` je jednorodičovské — druhá vícepremisová
   derivace (`překryv`) to už obešla query-time cestou, třetí (krok 3
   `skládání`: bratr∘rodič ⇒ strýc, tři premisy) bude potřebovat totéž znovu.**
   Dnes existují DVA rozšiřovací body odvození: `derive()` (fixní bod nad
   textovými pravidly, JEDNA premisa, persistovaný `Statement`) a bridging v
   `Evaluator.evaluate()` (`m.rules`, teď i `overlap_verdict` — query-time,
   víc premis, žádný nový `Statement`). To funguje, ale je to `implicitní`
   rozlišení, které nikde není napsané jako pravidlo — příští tah, co bude
   potřebovat derivaci z 2+ premis, si musí sám vzpomenout na tenhle
   precedens, jinak riskuje natahovat `derived_from` na seznam a rozbít
   `revoke()`/`render.py`/`viewbase_app.py`/`check_graph`ovu kontrolu
   derivace beze zkoušky na reálném textu. **Návrh:** až krok 3 přijde, buď
   se rozšiřovací bod pojmenuje explicitně (dokumentační pravidlo „derivace
   z 1 premisy → derive(), z 2+ → query-time join v evaluate()“), nebo se
   zváží, jestli `derive()` nezaslouží zobecnění.
2. **Unsupported % (30,1 %) se přes ~10 tahů měřených oprav hýbe málo —
   opravy jsou case-by-case (přivlastnění, částečná shoda jmen, appos…),
   ne systematické.** To může být buď (a) reálný strop metody (dependency
   parsing + ruční pravidla bez sémantických rolí/koreference za hranicí
   věty má fyzikální mez), nebo (b) signál, že další case-by-case oprava má
   klesající výnos a je čas na jinou vrstvu (sémantické role z UD, nebo NN
   extrakce rovnou — přesně směr, který J. navrhl 27. 9.). **Návrh:** až
   půjde bench spustit, rozložit unsupported podle PŘÍČINY (ne jen podle
   deprel jako dnes) a spočítat, kolik dnešních 30 % je „stejná chyba
   podruhé jinde“ vs. „nová třída chyby“ — to řekne, jestli case-by-case
   ještě má cenu.
3. **Krok 2 (`lexicon.py` operátory) řeší jen ČÁST toho, co J. myslel
   „vazby jako data“: lexikon sám ještě jednou roste case-by-case (dnes 1
   seed řádek `žít⇒potkat_se`, přidaný ručně, protože to je jediný pár, co
   šel bez textu ověřit).** Bez NN extraktoru, co by lexikonové řádky sám
   navrhoval z korpusu (a člověk/LM jen schvaloval — přesně I‑9 duch), se
   lexikon může stát druhou verzí `SYNONYMS` tabulky, jen rozdělenou do víc
   souborů a s lepší proveniencí. Provenience ≠ škálovatelnost. **Návrh:**
   až bude NN/UDPipe po ruce, měřit ne jen „kolik řádků lexikon má“, ale
   „kolik řádků NN navrhl vs. kolik jich člověk musel ručně dopsat“ — to je
   číslo, které řekne, jestli se cíl (autonomní růst) plní.
4a. **(subagent, nezávislý přezkum `discourse.py`/`ground.py`/`dialog.py`/
`render.py`, 27. 9. 2026) Nálezy stejného tvaru jako 1., navíc bez disclosure:**
`cb6/discourse.py:78‑84` (`Registry.candidates`) — koreferenční okno je napevno
„tento segment ∪ přesně jeden předchozí“; antecedent za dvěma segmenty
zpátky nikdy nevstoupí do kandidátů, systém to ani nenahlásí jako
nejednoznačné (tiše spadne na téma dokumentu). ~~`cb6/ground.py:201‑223`
(`_resolve_possessed`) — reálná I‑8 díra: víc kandidátů u přivlastňovacího
přídavného jména vezme `max(..., key=activation)` beze `HYPOTHESIS`/open-item~~
**OPRAVENO 27. 9. 2026** — `_owner_candidates` (zrcadlí `discourse.ambiguous`),
nejednoznačnost → `HYPOTHESIS` `mít` na každého kandidáta + open item, viz
HYPOTEZY a `tests/test_ground.py::test_ambiguous_owner_gets_hypothesis_
not_silent_guess`. `Registry.candidates`ovo okno (jeden segment zpátky) a
zbytek téhle položky **zůstávají otevřené**. **`cb6/
dialog.py:61‑63,95‑107`** — `Session.topics`/`_last_said` jsou proces-lokální
skaláry bez zámku/verze; „autonomní, průběžně rostoucí“ růst implikuje
souběžné zápisy do téže `Memory`, což by na `turn_no`/`sent_no` závodilo.
**`cb6/render.py:16‑37`** — `ROLE_LABELS`/`TEMPLATES`/`STATUS_TAGS` jsou pořád
Python literály, ne data vedle `cb6/lang/cs.json`, přestože modul sám tvrdí
„šablony jako data“ — druhý jazyk potřebuje FORK `render.py`, ne nový
soubor; to je konkrétní důkaz nálezu 4 níže. ~~`cb6/ground.py:208` má
českou příponovou tabulku natvrdo v kódu~~ **OPRAVENO 27. 9. 2026** —
`cb6/lang/cs.json` klíč `possessive_suffixes` (vlastní, ne splynutý s
`possessive` — zájmena vs. derivační přípona jsou dva jevy), `defaults.
POSSESSIVE_SUFFIXES`, viz HYPOTEZY. **Doporučení subagenta:** neopravovat `derived_from`/
`_resolve_possessed`/koreferenční okno každé zvlášť — jedno sdílené
„kandidáti s přiznanou nejistotou“ primitivum (kandidáti + HYPOTHESIS
alternativy + open item), kterým MUSÍ projít každé rozřešení, ne ad hoc
nejlepší-odhad na každém místě zvlášť.

4. **Role-klíče (`kde`,`kdo`,`co`…) jsou opaque symboly grafu (správně), ale
   jejich SÉMANTIKA (case frames — co je čas vs. místo, `ROLE_BY_CASE`) je
   zabudovaná do dvou míst (`ground.py` typuje výplň, `logic.py`
   `PLACE_FAMILY`/`TIME_FAMILY` je hardcoded tuple, ne data).** Dnešní `cb6/
   lang/` refaktor (27. 9.) přesunul do dat jen SLOVNÍ ZÁSOBU čtení
   (měsíce, částice…), ne tenhle strukturní předpoklad, že role se dají
   rozdělit do rodin „místo“/„čas“ podle univerzálních vzorů. Čeština řeší
   kde/kdy pádem a předložkou; jazyk bez pádů (angličtina) to řeší jinak
   (slovosled, jiné předložky) — ale rodiny `PLACE_FAMILY`/`TIME_FAMILY`
   samy o sobě jsou už univerzálnější (sémantické role, ne povrchové tvary)
   a možná není potřeba je stěhovat — jen to zatím nikdo neprověřil na
   druhém jazyce. **Návrh:** až bude `cb6/lang/en.json`, tohle je první věc
   k ověření (fungují `PLACE_FAMILY`/`TIME_FAMILY` beze změny, nebo ne?).

## 9. Jak předat dál (checklist pro nové sezení)

0. Nové sezení v tomto adresáři dostane zadání automaticky z `CLAUDE.md` (pravidla spolupráce, kde co je, další tah).
1. Přečíst `docs/KONCEPT.md`, spec § 0–1, tuto stránku, poslední záznam v `mereni/HYPOTEZY.md`.
2. Ověřit služby: UDPipe 42200, Ollama 11434, `pytest -q` zelené.
3. Rychlá smyčka na dvou dokumentech (§ 3), porovnat s posledními čísly (§ 4).
4. Vybrat tah z § 6, zapsat hypotézu, měřit, commitnout s číslem, pushnout, doplnit § 4–7 tady.
