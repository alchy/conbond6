# Hypotézy před změnou (I‑10)

Formát: `## <datum> · <úkol>` · **Změna:** … · **Hypotéza:** které číslo se pohne, kterým směrem, o kolik. · **Výsledek:** doplní se po benchi (commit).

## 2026-08-17 · Task 0 · výchozí bod
**Změna:** žádná — conbond6 = klon conbond5 (HEAD 60ad1c9), balíček `cb6`.
**Výchozí čísla (conbond5 v1 uzavřený, HEAD c503b68, `mereni/bench-vse.md`):** 43 dokumentů se zlatými otázkami, 13 899 vět, 46 256 výroků, zbytek 8,6 % tokenů, otevřené 11 839 (0,85/větu), QA 440/722 = 60,9 %. **Neměřeno:** yield, věrnost výroků (unsupported), statusy, dosah, audit grafu — to je práce conbond6.

## 2026-08-17 · Task 5 · precision audit — výchozí bod (před triáží)
**Změna:** žádná v jádře; přibyl audit (soudce gemma4 přes Ollama, keš verdiktů, lidská smyčka).
**Výchozí čísla (alois_jirásek + karel_čapek, strop 40 řádků, vzorek 100 SAFE výroků, soudce gemma4):**
unsupported **76,5 %** [66,8–83,3]; hlavní predikace 76 % (n=57), vedlejší `nmod` 80 % (n=35), `appos` 67 % (n=3), fragment 60 % (n=5).
Yield hl./vše 160/298 na 1 000 slov; QA 12/17 (kurátorované 3/3); graf 0 porušení; determinismus ano.
**Nálezy:** (a) vedlejší `nmod`/fragmenty/typovací `X ∈ X` vydávané za znalost; (b) obsah vnořených predikací (xcomp/ccomp) jako fakt; (c) pro‑drop volí špatný podmět; (d) iniciály „T. G.“ → entita „G“; (e) soudce je přísný na pro‑drop z kontextu a na životopisné závorky (prompt v2).
**Hypotéza pro Task 6 (triáž):** unsupported hlavních klesne pod 40 %, vedlejší `nmod` zmizí ze SAFE (→ REJECTED s důvodem), yield_main klesne o 20–40 %, QA hits −0 až −2 (typování zůstává pro uzávěry).

## 2026-08-17 · Task 6 · triáž + soudce v2 + opravy čtení
**Změny (tři commity):** (1) triáž — podmínka→pravidlo, vnořený obsah→reported, disjunkce/kardinalita→REJECTED, vedlejší nmod→REJECTED, fragment mimo znalost, typing zvlášť; logika čte jen `knowledge()`; (2) soudce prompt v2 (nevyslovený podmět z kontextu, závorka s roky za jménem osoby); (3) životopisná závorka jen u osob s tvarem „A – B“ bez slovesa, přivlastnění→`mít` jako HYPOTHESIS, částečná shoda jména jen s příjmením.
**Hypotéza (před):** unsupported hlavních < 40 %, yield_main −20–40 %, QA −0…−2.
**Výsledek (alois_jirásek + karel_čapek, strop 40, vzorek 100):** unsupported 76,5 → 63,0 (triáž) → 37,5 (soudce v2) → **29,0 %** [21,0–38,5]; hlavní 27 % (n=96); yield hl./vše 160/298 → **89/94**; SAFE 889 → 282, HYPOTHESIS 0 → 61, REJECTED 0 → 374; QA **12/17 beze změny**; graf 0 porušení; determinismus ano.
**Zelený řádek:** ano — méně výroků, méně nepodložených, dotazovatelnost stejná. Zbývající chyby: kvantifikátor ∀ z „všechna jeho dramata“, koordinace plošně, vztažné věty (`kdo:∀sousoší`), participia jako predikáty.

## 2026-08-17 · Task 7–8 · pravidla + registr referentů + segmenty
**Změna:** `derive()` (pevný bod pravidel z podmínek), zamítnutí/hypotézy v odpovědi (`Verdict.notes`); registr referentů jako pohled nad hranami `mention`, nejednoznačná koreference → jádro bez termu + HYPOTHESIS alternativy + OPEN; segmenty (nadpis/prázdný řádek), okno registru = tento + předchozí segment; dosah zná pásmo „jiný segment“.
**Hypotéza:** unsupported hlavních klesne (méně chybných pro‑drop podmětů), HYPOTHESIS vzroste, QA beze změny.
**Výsledek (tytéž 2 dokumenty, strop 40, vzorek 100):** unsupported 30,5 → **23,0 %** [15,8–32,1], hlavní 22 %; HYPOTHESIS 61 → 69; QA 12/17 beze změny; yield 89/94 beze změny; graf 0 porušení; determinismus ano.

## 2026-08-17 · Task 10 · dialog G — nálezy
- **G‑1** otázka „Kdy napsal R.U.R.?“: parser čte R.U.R. jako podmět (kdo) → NEVÍM. Mez čtení otázek s pro‑dropem a PROPN předmětem (řešit v čtení otázek, měřený tah).
- **G‑2** „Čapek se narodil v Praze.“ po Svatoňovicích → zapsáno bez konfliktu: otevřený svět nezná funkční role. Kandidát: `FUNCTIONAL_ROLES` jako data (narodit_se.kde/kdy, zemřít.kde/kdy) → hlásit KONFLIKT jako hypotézu nesrovnalosti.
- **G‑3** „Jeho bratr Josef Čapek“ → entita „bratr Josef Čapek“ (přístavek přilepen ke jménu).
- **G‑4** „Kde pracoval Čapek?“ → NEVÍM: `v+Loc: noviny` není místo → role zůstává povrchová (správně dle specu; učení `!role v+Loc = kde` nebo tabulka institucí jako míst).

## 2026-08-17 · Task 13 · první plný běh (wiki 43 dok. + korpus Vesmír/Hudba; soudce na 8 dokumentech)
**Běh 1 (commit d8cd6df):** 14 734 vět, 182 853 slov; yield hl./vše **76,8 / 86,8**; SAFE 26 630 · HYPOTHESIS 3 218 · REJECTED 21 087; zbytek 8,5 %; open/větu 0,93; pravidel 59, odvozeno 4; QA 174/334 = 52,1 % — po sadách: conbond 8/8, etalon 14/32, **korpus 7/90**, otazky‑filtr 145/204 (71 %); kurátorované 29/130 = 22,3 %; dosah 0: 49/94 · 1‑3: 16/41 · 4‑10: 18/24 · >10: 13/16 · jiný segment: 74/139; precision audit 400 výroků → **unsupported 34,9 %** [30,2–39,5], hlavní 35 % (n=342), appos 33 %; determinismus ano; **audit grafu 33 porušení** (status 8 = zamítnutý nmod v důkazu wh‑odpovědi; osiřelost 24 = uzly založené dotazy; rekonstrukce 1 = krok `restricts`).
**Oprava (5646e5b):** `describe`/`enumerate` jen nad znalostí (SAFE nmod „místo uvnitř fráze“ je jediná povolená výjimka), `prune_orphans` po dotazu do pevného bodu, graphcheck zná krok `restricts` → 0 porušení na postižených dokumentech.
**Poznámky:** (a) srovnání s conbond5 60,9 % není srovnání — jiná sada (682 auto → 204 filtrovaných + kurátorované + korpus); na filtrovaných auto je to 71 %; (b) korpus 7/90 je poctivý výchozí bod na těžších otázkách (Vesmír, Hudba: „Jakou rychlostí v km/s na megaparsek…“); (c) unsupported 34,9 % na 8 dokumentech vs 23 % na dvou — širší vzorek, těžší texty; hlavní zbývající chyby viz Task 6.

**Běh 2 (commit 5646e5b, po opravě auditu):** QA 173/334 = 51,8 % (jeden zásah přes zamítnutý nmod odpadl — poctivě); kurátorované 29/130; unsupported 32,8 % [28,3–37,5] (hlavní 35 %, appos 26 %, nmod‑místo 17 %); **audit grafu 0 porušení**; determinismus ano; zpráva `mereni/2026-08-17-5646e5b.md`.

## 2026-08-17 · tah: ∀ jen v jednoduché obecné větě
**Nález (audit plného běhu, 150 nepodložených):** 18 % je kvantifikátor ∀ z „holý podmět + prézens“ ve větách, které nejsou obecné (vedlejší věty, výčty, věty s vlastními jmény): `být(kdo:∀odvaha+∀statečnost…)`, `¬mít(kdo:∀tma, co:∃stín)` z názvu povídky. Další třídy: kopula/přístavek s odpadem („The“, „6.“, „např.“) 15 %, koordinace v podmětu 5 %, participia 3 %, uvozovky/citace 6 %; zbytek smíšený.
**Změna:** `_generic_context` v `read.py`: ∀ jen když je predikace kořen věty, podmět není koordinovaný a věta nemá žádné PROPN; jinak `·` (epizoda). Dialogy E/B („Ptáci létají“, „Ovoce obsahuje vitamíny“) zůstávají ∀ (testy zelené).
**Hypotéza:** unsupported plného běhu klesne o 3–6 bodů (∀ třída zmizí z větší části), QA beze změny nebo −1…−2 (otázky přes ∀ distribuci na encyklopedickém textu jsou vzácné).
**Výsledek ∀‑tahu (a341eb1, ještě seed=commit):** QA 173 → 175/334; unsupported 32,8 → 33,1 % celkem, hlavní 35 → 31 %, appos 26 → 45 % — ale jiných 400 výroků (seed = commit) → v šumu; poučení: měřidlo bylo nesrovnatelné napříč commity.
**Oprava měřidla (b… „vzorek po větách, seed = dokument“) a stabilní baseline (234ca26):** unsupported **31,4 %** [26,9–35,9] (hlavní 32 %, appos 37 %, nmod‑místo 13 %); QA 175/334 (kurátorované 29/130); audit grafu 0; determinismus ano. **Od teď se všechny další tahy srovnávají s tímto vzorkem (tytéž věty).**

## 2026-08-17 · tah: znalostní vazby jako data — krok 1 (lexikon: `třída` + `implikace`)
**Změna:** nový modul `cb6/lexicon.py` (řádky `{id, op, args, síla, autorita, zdroj}`; operátory `třída` a `implikace`; shoda predikátů dotaz × výrok přes reprezentanta třídy a uzávěr implikací; líná materializace použitých řádků do grafu jako uzly `kind="vazba"`, u odvozených výroků hrana `uses_rule`, u odpovědí tvrdý krok `lex` ověřovaný graphcheckem z exportu). Seed `cb6/lexikon/synonyma.jsonl` vzniká **migrací `defaults.SYNONYMS` se sílou**: `same` 32 jen u vidových dvojic a skutečných záměn (říci/říkat, umřít/zemřít, sepsat/napsat…), `implies` 32 tam, kde je jen jeden směr (bydlet ⇒ žít, vystudovat ⇒ studovat, obdržet ⇒ získat, emigrovat ⇒ odejít, obsahovat ⇒ mít…), `related` 24 tam, kde tabulka lhala (vydat ≁ napsat, padnout ≁ zemřít, chodit ≁ studovat, dělat ≁ pracovat, vzít_si ≁ oženit_se…). `Memory.learned["synonyms"]` zaniká → `!uč a = b | a => b | a ~ b` píše řádky `autorita=said` (staré JSON paměti se převedou při načtení). `defaults.SYNONYMS`/`synonym_class` mizí z kódu. `bench run --bez-lexikonu` = ablace seed vrstvy.
**Hypotéza:** QA 175/334 beze změny (±1 — vazby, které se zpřísní na `related`, by neměly nést kurátorovanou odpověď; kde ponesou, rozhodne význam páru, ne počet); unsupported hlavních predikací na stabilním vzorku neroste (audituje se výrok, ne shoda — vliv nulový až mírně kladný přes `derive()`); audit grafu 0 (nový krok `lex` musí být rekonstruovatelný z uzlů `vazba`); determinismus ano; ablace `--bez-lexikonu` na 2 dok. ukáže, kolik zásahů seed vrstva nese (očekávám 0–2 z 17).
**Výsledek (ad5d41b, plný běh, stabilní vzorek):** QA **175 → 178/334** (kurátorované 29/130 beze změny; otazky‑filtr 146 → 149/204); všechny tři zisky jsou z *přitvrzení* síly, ne z nových vazeb: „Kdy publikoval V. Vančura?“ dřív ANO 1937 (přes `napsat`), teď 1920 (`vydat`); „Kdy publikoval J. Škvorecký?“ 1955 → 1990; „Kdy studoval J. Vrchlický?“ 1861 (`chodit`/`navštěvovat`) → 1862 (`studovat`). Žádná ztráta. Krok `lex` v důkazu u 11 otázek (9 správně; 2 špatné byly špatné i před tahem, tytéž výplně): působit ~ pracovat 5×, bydlet ⇒ žít 3×, usadit_se ⇒ bydlet/žít 2×, obsahovat ⇒ mít 1×. Unsupported **31,4 %** [26,9–35,9] beze změny (hlavní 32 %, appos 37 %, nmod‑místo 13 % — tytéž výroky, audit se shodou predikátů nesouvisí); yield 76,84/89,76 beze změny; SAFE 27 175 · HYP 3 287 · REJ 20 553; pravidel 59, odvozeno 4; audit grafu **0** (krok `lex` rekonstruovaný z uzlů `vazba`); determinismus ano. Rychlá smyčka 2 dok.: 12/17, 15,5 % beze změny; ablace `--bez-lexikonu` na 2 dok. totožná. Zpráva `mereni/2026-08-17-ad5d41b.md`. **Ablace `--bez-lexikonu` na plné sadě (jen QA):** 177/334 (kurátorované 28/130, etalon 13/32) — seed vrstva nese přesně **1 zásah**: „Kolik zubů má mléčný chrup kočky?“ přes `obsahovat ⇒ mít`; ostatních 10 otázek s krokem `lex` má i přímý výrok. Poučení: přínos synonym pro QA je dnes malý (1/334), přínos přitvrzení pro precision odpovědí reálný (+3); hodnota lexikonu je hlavně v tom, že je to jedno místo s proveniencí pro kroky 2–5.

## 2026-08-17 · tah: výpis („která/jaká N“, imperativ, `podřazení` z konzole)
**Nález (demo, J.):** „Která díla napsal Karel Čapek?“ → NEVÍM, protože čtení otázky ztratí podstatné jméno (díra `který:?` místo `co:?` omezené na skupinu *dílo*); „Vyjmenuj všechna díla Karla Čapka.“ se čte jako tvrzení a zapíše se (imperativ chybí); a i při správném čtení chybí *drama ⊆ dílo* — to je znalost, kterou má jít říct z konzole (návrh vazeb, operátor `podřazení`). Text článku o Čapkovi díla neuvádí větou „napsal X“, ale výčtem „Krakatit (1924) – román.“ → typing `Krakatit ∈ román`; autorství je jen tématem článku.
**Změna:** (1) čtení: `který/jaký + N` v otázce → díra v roli N (`co:?`), N jako omezení (terms díry, wh_kind filler); imperativ výpisu (`vyjmenovat/vypsat/uvést/jmenovat`, Mood=Imp) → otázka druhu `list`: díra omezená skupinou N, volitelně přivlastnění (`díla Karla Čapka`) — nezapisuje se. (2) lexikon: operátor `podřazení` (`args [pod, nad]`, síla implies, orientovaně), `!uč drama < dílo`, seed `cb6/lexikon/podrazeni.jsonl` (literární žánry ⊆ dílo, malý), graphcheck `lex_path` bere `podřazení` po směru. (3) logika: omezení výplní díry — výplň sedí, je‑li `member*/subset*` do skupiny omezení (tvrdý krok) nebo přes `podřazení` v lexikonu (krok `lex`, materializace); druh `list`: členové skupiny (přes uzávěr + podřazení), kteří sdílí SAFE výrok s přivlastňovanou entitou, nebo — přiznaně jako výchozí volba — jsou z dokumentu, jehož tématem entita je.
**Hypotéza:** QA na dnešní sadě beze změny (±1; tvar „která N“ tam skoro není); nová sada `gen-*.json` (výpisové otázky psané z textu, `curated=False` do ověření J.) 0/N → ≥ N/2; unsupported hlavních beze změny (čtení tvrzení se nemění, jen otázek); audit grafu 0 (krok `lex` přes `podřazení` rekonstruovatelný); determinismus ano.
**Výsledek (b75d8d5, plný běh, stabilní vzorek; 4 commity: 66f5541 výpis, cfc7c4a audit zrcadlí paměť + výčty, 94cdd21 letopočty výčtu, b75d8d5 skupina‑jedinec):** QA **178 → 184/343** — stará sada 179/334 (+1: „Kde bydlel Petr Bezruč?“ „obec“ → „Koloredov u Místku“ — nominativ jmenovací „obec Koloredov“), **gen 5/9** (Vyjmenuj romány/dramata/díla Aloise Jiráska ✓, Vyjmenuj romány/díla Karla Čapka ✓ — Krakatit, Továrna; „Které povídky napsal Jirásek?“ ✗ jen „povídka“ (anonymní instance, text neříká „napsal Marylu“), „Vyjmenuj povídky Boženy Němcové“ ✗ (Pohorská vesnice nezachycena), „Které komedie napsal Čapek?“ ✗ (Loupežník je typován, ale bez výroku napsat — „Vyjmenuj komedie Karla Čapka“ by šlo), „Která díla napsal Čapek?“ ✗ (jen „první kniha“ — článek díla nepřipisuje větou)); kurátorované 29/130 beze změny. Unsupported **31,4 → 30,5 %** [26,2–35,2] (hlavní 32 → 31 %, appos 37 → 35 %; nominativ jmenovací a výčty s letopočty čtou líp: „drama R.U.r.“ jako jméno zmizelo, „hra[historický] = Jan Žižka“ → ∈); yield 89,76 → 89,65; SAFE 27 175 → 27 771 (typing z názvů), REJ 20 553 → 19 747; **audit grafu 0** (po cestě: 6 porušení rekonstrukce → audit `hard_path` teď zrcadlí `member_star` — `same_as` před `member`; 3 osiřelé letopočty → role `kdy` výčtu); determinismus ano. Zpráva `mereni/2026-08-17-b75d8d5.md`.
**Poučení:** (1) `list_verdict` musel zpřísnit asociaci na výrok `kdo: vlastník, co: kandidát` — sdílení libovolného výroku dávalo „Josef Čapek je dílo Karla Čapka“; (2) výpis podle tématu dokumentu je nutný a poctivě přiznaný — články díla vyjmenovávají, nepřipisují; (3) audit grafu odhalil dvě neshody sémantiky paměť × audit, které dřív nebyly vidět, protože je žádná odpověď nepoužila.

## 2026-08-18 · docs: UVOD + UKAZKY (generované) + dvě opravy z ukázek
**Změna:** `docs/UVOD.md` (orientace: cesta věty grafem, pojmy, znalost jako data, audit, bench, příkazy, symboly), `bench/ukazky.py` → `docs/UKAZKY.md` (12 scén ze živého běhu, přegenerovat po tahu). Ukázky odhalily: (a) popisek názvu z nominativu jmenovacího zůstal malým písmem, když entitu založila sonda před zápisem („krakatit“) → přesun povrchového tvaru dopředu bez podmínky `new`; (b) „Kdo napsal Krakatit?“ NEVÍM — holé obecné jméno v otázce (parser NOUN) se zakotvilo jako skupina, i když entita toho jména existuje → `ground`: holý term bez přívlastků/počtu/přivlastnění, jehož lemma/tvar je jménem právě jedné entity, je ta entita (přiznaná volba „jméno známé entity“).
**Hypotéza:** QA ±1 (otázky s názvem díla jako předmětem), unsupported beze změny (mění se zakotvení jmen, ne čtení tvrzení), graf 0, determinismus ano. Rychlá smyčka 2 dok.: 13/25, 16,0 %, graf 0 — beze změny.
**Výsledek (3cd63e4, plný běh):** QA 184/343 beze změny (žádná otázka se neotočila), unsupported **30,5 → 30,1 %** [25,7–34,7] (hlavní 31 → 30 % — pár tvrzení s názvem se zakotvilo na známou entitu místo nové skupiny), yield/SAFE beze změny, audit grafu 0, determinismus ano. Zpráva `mereni/2026-08-18-3cd63e4.md`.

## 2026-09-27 · nové sezení (cloud, bez služeb) — prostředí + jazyk jako data + `chronos.overlap`

**Nález o prostředí:** tohle sezení běží v jednorázovém cloudovém kontejneru bez
`.venv` (vytvořen znovu), bez UDPipe (`127.0.0.1:42200`), bez Ollama
(`127.0.0.1:11434`) a bez `data/corpus`/`data/cache` (gitignored, jsou jen na
stroji J.). **Bench, audit, `gold-gen`, `cb6.record` (nové rozbory) tedy tuhle
relaci neběží** — jen `pytest` hermeticky z `tests/data/parses.json` (168 + 2
xfail, zeleno). Nejde tedy udělat „plný bench po“ na krok, který mění čtení
reálných vět; níže je proto jen refaktor beze změny chování (měřeno pytestem,
ne QA/unsupported číslem) a čistě výpočetní přírůstek (`overlap`).

**Podnět J. (mid-session):** systém má být multilingvní — jazyková pravidla
oddělená per jazyk jako JSON; NN (parser/LLM) smí dělat „skoro vše“ — strukturu,
extrakci, konverzaci, i pro víc jazyků — ale nikdy „znalost“: ta zůstává
výhradně v grafu (rozšíření I‑9: LM/NN „jen soudce auditu a generátor otázek“
→ „NN jen struktura, nikdy fakt“, teď bez ohledu na jazyk). Cíl: systém, co si
touhle cestou umí průběžně/autonomně rozšiřovat znalostní bázi (extrakce grafu
z libovolného textu), a pořád platí I‑11/I‑12 (rekonstrukce jen z exportu).

**Změna (refaktor, beze změny chování):**
1. `cb6/lang/` — nový modul: `LanguageRules` (dataclass), `load_language(code)`
   (kešované, `FileNotFoundError` na neznámý jazyk — žádný tichý fallback),
   `available_languages()`. `cb6/lang/cs.json` — doslovný přepis dosavadních
   tabulek `defaults.py` (`ROLE_BY_CASE`, `DETERMINER_QUANT`, `PARTICLES`, `WH`,
   `LIST_VERBS`, `PLACE_NOUNS`, `CONDITIONAL_MARKERS`, `ATTITUDE_VERBS`… — 18
   tabulek) a `chronos.py` (`MONTHS`, `WEEKDAYS`, `SEASONS`, `RELATIVE_DAYS`,
   `TIME_NOUNS` základ) do JSON, žádná hodnota se nezměnila.
2. `defaults.py`/`chronos.py` teď jen `load_language("cs")` a re‑exportují
   tabulky pod stejnými jmény → **žádný spotřebitel** (`read.py` 28 míst,
   `triage.py` 7, `logic.py`, `memory.py`) se nemusel měnit. Vnitřní klíče rolí
   (`kde`, `kdo`, `co`…) zůstávají opaque symboly grafu, ne „čeština“ — mění se
   jen ČTENÍ z povrchového tvaru. Operátory a schéma grafu beze změny.
3. `cb6/chronos.overlap(a, b) -> bool | None` — protnou se dva časové
   body/intervaly? Primitiv pro budoucí lexikonový operátor `překryv`
   (`žít.kdy × žít.kdy ⇒ potkat_se`, spec krok 2, `možnost`); vlastní funkce,
   ne `not before(a,b) and not before(b,a)` (dvojitá negace by tiše změnila
   „nevím“ na „ano“ u nesrovnatelných párů).
4. `pyproject.toml`: `cb6.lang` mezi packages, `*.json` do package-data.

**Hypotéza:** čistý refaktor — pytest beze změny počtu **kromě** nových testů
(`tests/test_lang.py` 5, `tests/test_chronos.py::test_overlap` 1 → **168+2xfail
→ 174+2xfail**), mypy/pylint čisté (`cb6/lang` nový modul 10/10), **žádné
QA/unsupported číslo se nehýbe** (nejde bez korpusu/UDPipe měřit — a stejně by
se nemělo, je to jen přesun dat, čtení se nezměnilo).
**Výsledek:** přesně tak — 174 passed + 2 xfailed (bylo 168+2), mypy 32
souborů čisté, `cb6/lang` pylint 10.00/10, `chronos.py` 9.66/10 (beze
regrese — 4 nálezy byly už v baseline, nová funkce nepřidala žádný). Žádná
existující tabulka nezměnila hodnotu (`test_defaults_reexportuje_nactene_tabulky`
porovnává `defaults.*`/`chronos.*` s načteným jazykem 1:1).
**Poučení / co zůstává otevřené:** (a) skutečné wiring „NN → extrakce grafu“
a druhý jazyk potřebují UDPipe/Ollama a bench — příští sezení se službami má
navázat přímo na krok 2 spec (`překryv`+`porovnání`+veličiny, `cb6/lexicon.py`
teď má `overlap` primitiv připravený) a na multilingvní krok 2 (anglická
`cb6/lang/en.json` + ověření, že `read.py` neobsahuje nic natvrdo českého mimo
`D.*`/`chronos.*` — dnešní průchod všech 28+7 míst v `read.py`/`triage.py`
potvrdil, že jsou); (b) `docs/HANDOVER.md` a spec dostaly zápis rozhodnutí, ale
krok 2 samotný (operátory `překryv`/`porovnání` v `lexicon.py`, čtení „Jaká je
délka…“/„Mohli se potkat?“) **není hotový** — jen jeho časový primitiv.

## 2026-09-27 · pokračování · `překryv` (operátor + query-time join) na fragmentech, bez UDPipe

**Podnět J.:** UDPipe je prý dostupné online (veřejné) — zkoušel jsem
`lindat.mff.cuni.cz`, ale síťová politika tohoto kontejneru CONNECT zamítla
(403 na proxy) — hlášeno J., čeká na rozšíření Network access v nastavení
prostředí. Ollama netřeba (žádný druhý model — J.: „projekt by se bez něj měl
obejít“). J.: „pokračuj samostatně, kriticky hodnoť architekturu, měřením
postup (na fragmentech textu a úloh)“ — bez korpusu/UDPipe měřím na **ručně
sestavených úlohách** (`Statement`/`Memory` přímou konstrukcí, ne přes NL
čtení — poctivě přiznáno v docstringu testu, ne vydáváno za rozbor).

**Změna:**
1. `cb6/lexicon.py`: `Link.modality` (JSON klíč `modalita`, jen když
   vyplněná — zpětná kompatibilita), validace `překryv` (2 argy, síla jen
   `implies`, modalita musí být `"možnost"` — jinak by NEVÍM tiše sklouzlo na
   jistotu), `Lexicon._overlap`/`overlap_targets`/`overlap_rules_by_target`,
   `links_for_graph` píše `modalita` do exportu. Seed `cb6/lexikon/prekryv.jsonl`
   (1 řádek: `žít ⇒ potkat_se`, možnost).
2. `cb6/logic.py`: `Evaluator._time_role` (najde výrok o entitě s predikátem
   a jedinou výplní role `kdy` typu `time`), `Evaluator.overlap_verdict` —
   **query-time join** (ne `derive()`‑style persistovaný odvozený výrok):
   dotaz s `modality == "možnost"` a rolí `kdo` o přesně 2 termech zkusí
   `chronos.overlap` na jejich `žít.kdy`; protnutí ⇒ ANO, neprotnutí ⇒ **NE**
   (spec: „Nepřekryv ⇒ NE je silné a správné“), nesrovnatelné/chybí ⇒ `None`
   (spadne do obecného NEVÍM). Zapojeno do `evaluate()` vedle `kernel_verdict`.
   **Architektonické rozhodnutí (proč query-time, ne `derive()`):**
   `Statement.derived_from` je jednorodičovské — `derive()` odvozuje z JEDNÉ
   premisy; `překryv` potřebuje DVĚ (výrok o A, výrok o B). Násilné natažení
   `derived_from` na dva rodiče by bylo neověřené riziko (dotklo by se
   `revoke()`, `render.py`, `viewbase_app.py`, `check_graph`u derivace) bez
   možnosti to tu bez služeb prověřit na reálném textu. Query-time join
   (jako už existující „pravidla“/můstky v `evaluate()`) žádnou trvalou
   derivaci nepíše — `Proof` nese oba zdrojové výroky přímo, graf zůstává
   beze změny schématu. Tohle je obecnější zjištění: **`derive()` (fixní bod
   z textových pravidel) a bridging v `evaluate()` (query-time, víc premis)
   jsou dva různé rozšiřovací body** a spec krok 2 patří pod druhý, ne první.
3. `bench/graphcheck.py`: `lex_path` navíc chodí po hranách `překryv`
   (jednořádková změna — už bylo obecné pro `implies`); nová jádra `overlap`/
   `no_overlap` v `check_answer` (`_time_overlap` — zrcadlí `chronos.overlap`
   čistě z atributů `t_start`/`t_end`, bez importu `cb6`, jak modul vyžaduje).
4. `tests/test_prekryv.py` — 4 fragmenty: protnuté životy → ANO (`derived`,
   `check_graph`/`check_answer` 0, materializovaný řádek `lex:prekryv:0001`
   ověřený i negativně — bez uzlu `vazba` je krok `rekonstrukce`); neprotnuté
   → NE silné (`check_answer` 0); faktická otázka bez modality → NEVÍM (i
   při protnutí — overlap není důkaz skutečného setkání); chybějící údaj o
   jedné osobě → NEVÍM. `tests/test_lexicon.py` +5 (validace, JSON, seed).

**Hypotéza:** pytest +9 (182+2xfail), mypy/pylint beze regrese (`bench/
graphcheck.py`, `cb6/lexicon.py` 10/10; `cb6/logic.py` stejný počet nálezů
jako baseline, žádný nový). Žádné bench/QA číslo — čtení „Mohli se potkat?“
z reálné věty (`read.py`) čeká na UDPipe, tenhle tah je jen logická vrstva.
**Výsledek:** přesně tak — 182 passed + 2 xfailed (bylo 174), mypy 32 souborů
čisté, `bench/graphcheck.py`/`cb6/lexicon.py` 10.00/10 beze změny, `cb6/logic.py`
14 nálezů před i po (0 nových — `overlap_verdict`/`_time_role` mají
docstringy). Fragmenty potvrzují: primitivum (`chronos.overlap`) + datový
model (`Lexicon` `překryv`) + query-time join (`Evaluator.overlap_verdict`)
skládají se do správné, auditovatelné odpovědi na malé úloze bez jediné
řádky natvrdo v kódu (řádek lexikonu je jediné místo, které o `žít ⇒
potkat_se` něco ví).
**Kritické hodnocení architektury (na žádost J.), krátce — dlouhá verze v
HANDOVER § 9:** (1) `Statement.derived_from` (jednorodičovská derivace) je
reálný dluh, jakmile začnou přibývat vícepremisová odvození (krok 3
příbuzenství — `skládání`, bratr∘rodič ⇒ strýc — bude potřebovat TŘI
premisy: bratr(X,Y), rodič(Y,Z) ⇒ strýc(X,Z); query-time join to zvládne
znovu, ale je to už druhý takový případ → stojí za zvážení, jestli si
`derive()` nezaslouží zobecnění na n‑premisové odvození místo dalšího
obcházení); (2) `list_verdict`/`fits_class` a čtecí heuristiky (`výchozí
volba“) v `read.py`/`logic.py` přibývají rychleji než klesá unsupported %
(30,1 % po ~10 tazích) — to je varovný signál, že cesta „oprava za opravou“
míří k platu; krok 2/3 (operátory) je systematičtější směr, ale i ten roste
case-by-case (dnes 1 seed řádek `žít⇒potkat_se`) — bez druhého jazyka/NN
extraktoru hrozí, že se lexikon stane novou verzí `SYNONYMS` tabulky, jen
rozdělenou do víc souborů; (3) role-klíče (`kde`,`kdo`,`co`…) jsou opaque, ale
jejich VÝZNAM (case frames, co je "kdy" vs "kde") je zabudovaný do dvou
modulů (`ground.py` typuje, `logic.py` PLACE_FAMILY/TIME_FAMILY) — druhý
jazyk možná bude potřebovat jiné rodiny rolí (např. jazyk bez pádů řeší
"kdy/kde" jinak) — dnešní refaktor (`cb6/lang/`) řeší jen SLOVNÍ ZÁSOBU
čtení, ne úplně tohle.

## 2026-09-27 · pokračování · `!uč překryv a => b` — dialogová vstupní strana

**Změna:** `Memory.add_link` dostal volitelný parametr `modality` (výchozí
`""`, zpětně kompatibilní se všemi existujícími voláními); `dialog.py`
rozpozná `!uč překryv X => Y` jako vlastní slovo v příkazu (ne symbol z
`parse_teach`'s mini-jazyka — nese modalitu `"možnost"`, kterou symbolická
gramatika `= / => / ~ / <` neumí vyjádřit bez páté značky). Dřív šel operátor
`překryv` naučit jen ze seedu (JSONL), teď i z dialogu, jako `třída`/
`implikace`/`podřazení` od kroku 1.
**Hypotéza:** pytest +1 (`test_dialog.py::test_prekryv_command`), mypy/pylint
beze regrese (jen posun čísel řádků).
**Výsledek:** přesně tak — 183 passed + 2 xfailed (bylo 182), mypy čisté,
pylint diff `cb6/dialog.py`/`cb6/memory.py` beze nového nálezu (ověřeno
`diff` baseline vs. po změně, ne jen skóre — skóre samo nerozliší posun
řádků od nového nálezu, poučení z předchozího kroku téhle relace).

## 2026-09-27 · nález (NE tah): spaCy `cs_core_news_sm` jako možná náhrada UDPipe — změřeno, NE nasazeno

**Motivace:** UDPipe (127.0.0.1:42200) je nedostupné (jiný stroj), veřejný
`lindat.mff.cuni.cz` zamítla síťová politika kontejneru (403). PyPI
(`pypi.org`, `files.pythonhosted.org`) v `noProxy` je, takže `pip install`
funguje bez omezení — zkusil jsem, jestli existuje český UD parser
instalovatelný čistě odsud (bez LINDAT/GitHubu, oboje jinak blokované).
`cs_core_news_sm` (spaCy pipeline, PyPI balíček `cs_core_news_sm==0.2.1`) jde
nainstalovat a natrénovaný model je součástí balíčku (žádné další stahování).

**Měření (ne hypotéza — šlo o zjištění, ne o tah, který mění cb6):** rozbor
všech 177 vět z `tests/data/parses.json` spaCy modelem, token po tokenu
porovnáno s uloženým skutečným rozborem UDPipe2 (lemma, upos, head, deprel;
`ROOT`→`root` normalizováno) — **shoda 90/177 vět přesně (50,8 %), 754/907
tokenů (83,1 %)**; UPOS sada, deprel jména (`nsubj`,`obl`,`expl:pv`,`flat`…) a
rysy (`Case`,`Gender`,`Animacy`,`NameType`…) jsou stejná UD schémata — není to
jiný tagset, jen jiný model se liší v konkrétních rozhodnutích (lemmatizace
přechýlených tvarů, přiřazení přívlastků u dat/závorek, struktura otázek —
právě první nesouhlasící věty byly datum v závorce a otázka).
**Rozhodnutí:** **NEnasazovat jako tichou náhradu** — 16,9 % rozdílu v
tokenech by znečistilo srovnání s historickými čísly (byla by to směs dvou
parserů, ne jedna proměnná) a porušilo by ducha „čte se z tokenů rozboru,
nikdy odhadem“ (`chronos.py` docstring, `oracle.py` provenience — `model?=`
značka existuje přesně proto, aby se neztotožnila identita modelu). Možné
užší použití příště: **jen pro zcela nové věty**, kde žádné historické číslo
neexistuje k porušení (např. krok 2 `překryv` — „X žil v letech…“, „Mohli se
X a Y potkat?“), s proveniencí jasně odlišnou (`spacy model=cs_core_news_sm-0.2.1`,
nikdy `udpipe2`) a s ručním ověřením KAŽDÉ nové věty token po tokenu (přesně
duch pravidla „testovací věty musí mít hlavu a patu“ — tady jsem to ověření
já, ne LM generující bez kontroly). Nerozhodnuto bez J.: stojí to za tu
práci (napsat `SpacyOracle`, ověřit ručně), nebo je lepší čekat na
rozšíření síťové politiky pro `lindat.mff.cuni.cz`/`127.0.0.1:42200`?

## 2026-09-27 · pokračování · věta učí lexikon bez příkazu (J.: „vše z kontextu diskuse, bez příkazu“)

**Podnět J.:** „příkazy typu !uč — vše by mělo být z kontextu diskuse, bez
příkazu.“ `cb6/lexicon.py` už od kroku 1 jmenuje autoritu `read` („věta typu
„X je synonymum Y“ — zatím nečteme“) — přesně tohle je teď implementované.
`!uč`/`!role`/`!pravidlo` zůstávají (debug/explicitní kanál, testy na nich
stojí), ale k tomu přibyla cesta z běžné promluvy.

**Změna:** `cb6/read.py` — `Predication.lex_teach: (op, args, síla) | None`;
`Reader._lex_teach` v `_copula` rozpozná „X je synonymum/synonymem Y“
(podmět = infinitiv VERB, druhý infinitiv se hledá v podstromu kořene —
robustně vůči kolísání stromu `xcomp` vs. `nmod→acl`, stejný duch jako
`chronos.time_from_tokens`); záporná věta („X není synonymum Y“) se
**nenaučí nic** (radši nic než obráceně špatně). `cb6/ground.py` —
`ground_predication` takovou predikaci nezakotví jako běžný výrok, zapíše
řádek lexikonu (`Memory.add_link(..., "read", …)`) a vrátí placeholder
výrok `kind="lex_teach"`, `mood="pattern"` (mimo `knowledge()`, ale se
`source`/`sentence` pro I‑12 — je to výrok grafu, jen ne tvrzení o světě).

**Metodická poznámka (proč rozbor ručně, ne ze zkoušeného spaCy):** tahle
konstrukce (infinitiv jako podmět kopuly) není v žádném zaznamenaném
korpusu a dostupný náhradní parser (viz nález výše, spaCy `cs_core_news_sm`)
na ní viditelně selhává (např. „Bydlet a žít jsou synonyma.“ dostal UPOS
`PROPN`/`ADV` místo `VERB`/`NOUN`) — rozbor testovací věty je proto sestavený
ručně podle univerzálních závislostí (křížově ověřeno part proti spaCy
tam, kde spaCy vyšlo správně), ne převzatý naslepo. Přesně duch pravidla
„testovací věty musí mít hlavu a patu“ — tady jsem ověřovatel já.

**Hypotéza:** pytest +2 (`tests/test_lex_teach.py`), mypy/pylint beze
regrese na `read.py`/`ground.py` (jen posun řádků, ověřeno diffem).
**Výsledek:** přesně tak — 185 passed + 2 xfailed (bylo 183), mypy čisté
(1 nový `type: ignore[arg-type]` na stejném vzoru jako ostatní `Statement(...)`
volání v `ground.py`), `diff` pylintu na `read.py`/`ground.py` beze nového
nálezu. „Bydlet je synonymum žít.“ → `Lexicon.match("žít","bydlet")` i
naopak (`same`, obousměrně); „Vydat není synonymum napsat.“ → nic se
nenaučilo.
**Otevřené (příští tah, měřeno, ne dohadem):** jiné formulace („X znamená
totéž co Y“, „X a Y jsou synonyma“) mají jinou stromovou strukturu (kořen
`znamenat`, ne kopula) — čekají na vlastní rozpoznávač a vlastní hypotézu;
`podřazení`/`implikace`/`překryv` z promluvy (ne jen `třída`) taky.

## 2026-09-27 · pokračování · `bench vazby` — měření pokročilosti chápání vazeb podle mechanismu

**Podnět J.:** „nastav měření pro NN heuristiku, aby bylo možné měřit
pokročilost strategie chápání vazeb z grafových dat a příkazů a cíleně
určit směr rozvoje projektu.“ Bezprostředně předtím J. upřesnil: „příkazy
učení nebo rozšiřování znalosti musí vycházet z kontextu věty nebo dialogu
a nesmí to být klíčová slova“ — čímž retroaktivně řadí i právě dokončené
„X je synonymum Y“ (klíčové slovo `synonymum`) jako MEZIKROK, ne cílový stav.

**Změna:** `bench/vazby.py` (+ `python -m bench vazby`) — zlaté úlohy
„naučit vazbu“ řazené podle MECHANISMU, ne jedno číslo:
- `prikaz` — `!uč a = b` / `a => b` / `překryv a => b` (existuje od kroku 1/2);
- `veta` — „X je synonymum Y“ (klíčové slovo, dokončeno dnes dřív, ale J.
  ho teď explicitně řadí jako mezikrok);
- `korekce` — oprava v dialogu má naučit vazbu mezi starým a novým
  predikátem (**cíl, dnes 0**);
- `graf` — parafráze ve dvou větách (stejné role/termy, jiný predikát) →
  hypotéza vazby bez jakékoli věty o vazbě (**cíl, dnes 0**).

Případy `veta`/`korekce`/`graf` běží na ručně sestavených rozborech (stejná
poctivost jako `tests/test_lex_teach.py`); `korekce`/`graf` reuse skutečné
recorded věty z `tests/data/parses.json` („Petr bydlí v Praze.“, „Karel
Čapek napsal román Krakatit.“) + ručně sestavený protějšek s jiným
slovesem, křížově ověřený proti skutečným tokenům.

**Hypotéza:** `prikaz`/`veta` 5/5 (existující schopnost), `korekce`/`graf`
0/2 (dosud neimplementováno — číslo má ukázat mezeru, ne selhat skrytě).
Regresní test (`tests/test_bench_vazby.py`) zamkne přesně tenhle poměr, ať
se příští session dozví hned, když se něco z tohohle tiše změní.
**Výsledek:** přesně tak — `prikaz` 3/3, `veta` 2/2, `korekce` 0/1, `graf`
0/1, celkem 5/7. Pytest 185+2xfail → 187+2xfail, mypy čisté, `bench/vazby.py`
nový modul 10/10 (nulová regrese v `bench/__main__.py` — diff jen posun
řádků, ověřeno).
**Poučení:** měření podle mechanismu (ne jedno číslo „kolik vazeb systém
zná“) je přesně to, co J. chtěl — dá se z něj přímo číst, kam příští tah
cílit (§ 6 v HANDOVER, položka „‑1“: `korekce` a `graf`, oba 0/1, jsou teď
nejvyšší priorita). Vedlejší poučení: „veta“ mechanismus (dokončený
minulý tah) sám o sobě ještě nesplňuje „bez klíčových slov“ — bench to
teď drží viditelné, aby se to nezapomnělo vydávat za hotovo.

## 2026-09-27 · pokračování · mechanismus `korekce` implementován (bench vazby 5/7 → 6/7)

**Změna:** `cb6/dialog.py Session._learn_from_correction` — když oprava
v dialogu (`main.correction`, „Ne, X namísto Y“) odvolá starý výrok a
zapíše nový SE STEJNOU rolí `kdo` (a beze změny všech ostatních sdílených
rolí) ale JINÝM predikátem, zapíše se řádek lexikonu `třída`/`related`,
autorita `read` — bez klíčového slova, bez příkazu. Síla **`related`
záměrně**, ne `same`/`implies`: jedna oprava může stejně dobře znamenat
aktualizovaný fakt („bydlí už jinde“) jako parafrázi téže události —
`related` nikdy nevstupuje do verdiktu (I‑3), takže riziko falešně
pozitivní vazby se do QA nepropíše, jen do recall/nápovědy. Doplněn strážný
test: pokud i ODLIŠNÁ role (ne jen predikát) se mezi starým a novým
výrokem změní zároveň, link se NEnaučí (moc slabý/nejednoznačný signál).
**Hypotéza:** `bench vazby` `korekce` 0/1 → 1/1, `prikaz`/`veta` beze
změny (3/3, 2/2), `graf` beze změny (0/1); zbytek pytestu beze změny
(žádná existující korekce v testech nezíská navíc řádek lexikonu, protože
vyžaduje JINÝ predikát se STEJNÝMI rolemi — `test_unknown_stays_unknown_
and_correction`ova „Ne, Petr bydlí v Brně.“ mění MÍSTO, ne predikát, takže
první podmínka `old.pred == new.pred` ji vyřadí hned).
**Výsledek:** přesně tak — `bench vazby` 6/7 (`korekce` 1/1, `graf` pořád
0/1), pytest 187+2xfail → 188+2xfail (nový test `tests/test_dialog.py::
test_korekce_uci_vazbu_mezi_predikaty` + rozšířený `test_unknown_stays_
unknown_and_correction` o kontrolu „místní oprava nic nenaučí“), mypy
čisté, `cb6/dialog.py` diff beze nového pylint nálezu (jen posun řádků).
**Poučení:** rozšiřovací bod pro „vazba z kontextu dialogu“ byl přesně tam,
kde ho `bench vazby` ukázal (`Session._assert`, větev `main.correction`) —
měření samo řeklo, KDE v kódu zasáhnout, ne jen ŽE se má něco zlepšit.
`graf` mechanismus (parafráze bez jakékoli opravné věty) zůstává jediný
otevřený cíl — vyžaduje procházet `Memory.knowledge()` a hledat páry
výroků se shodnými termy a různým predikátem, bez signálu „tohle je
oprava“ z dialogu; to je systematicky náročnější (potenciálně O(n²) přes
celou paměť) a je na samostatný tah s vlastní hypotézou o výkonu i
precision (kolik falešných párů by to navrhlo na reálném textu).

## 2026-09-27 · pokračování · mechanismus `graf` implementován (bench vazby 6/7 → 7/7, všechny čtyři hotové)

**Změna:** `cb6/dialog.py Session._suggest_link_from_graph` — po zápisu
KAŽDÉHO nového výroku (`_ingest_sentence` i `_assert`, ne jen při opravě)
se pomocí `Memory.statements_about` (existující index, O(k) na term, ne
plný O(n²) sken paměti) podívá po jiných aktivních výrocích sdílejících
roli `kdo` A JEŠTĚ JEDNU DALŠÍ roli (např. `co`) se STEJNÝMI termy, ale
JINÝM predikátem — a pokud najde, zapíše řádek lexikonu `třída`/`related`,
autorita `read`, deduplikovaně (nenavrhne tutéž dvojici predikátů dvakrát).
Bez dialogového signálu „tohle je oprava/totéž“ je vyžadování DRUHÉ shodné
role klíčové (jinak by každá druhá věta o téže osobě navrhla vazbu —
`test_ingest_then_ask_with_source`, kde „narodit_se“/„pracovat“ sdílí jen
`kdo“, jinou roli ne, teď explicitně ověřeno jako negativní případ).
**Hypotéza:** `bench vazby` 6/7 → 7/7 (všechny čtyři mechanismy); zbytek
pytestu beze změny (síla `related` nikdy nevstupuje do verdiktu, takže
žádná existující QA/verdikt asercí se nemůže rozbít — jen `memory.links`
přibude, což nic netestuje, dokud to test výslovně nekontroluje).
**Výsledek:** přesně tak — `bench vazby` **7/7**, pytest 188+2xfail →
189+2xfail (nový `tests/test_dialog.py::test_graf_uci_vazbu_z_parafraze_
bez_opravy` + rozšířený `test_ingest_then_ask_with_source` o negativní
kontrolu), mypy čisté, `cb6/dialog.py` diff beze nového pylint nálezu
(jen posun řádků — ověřeno, ne jen skóre). Celá zbylá sada (187 testů)
prošla BEZE ZMĚNY navzdory tomu, že `_suggest_link_from_graph` teď běží
na každém zapsaném výroku v `ingest()`/`say()` — žádný test nezaznamenal
vedlejší efekt, protože `related` je navržený tak, aby nemohl nic pokazit.
**Poučení / co zůstává nevalidováno:** tenhle mechanismus NIKDY neběžel
na reálném korpusu (žádný tu není) — `statements_about` drží náklad na
term, ne na celou paměť, ale kolik falešných párů by to navrhlo na
180 000 slovech reálného textu (dvě různé osoby se stejným jménem místa,
apod.) je **neměřeno**. Priorita pro sezení se službami: `bench run
--vse` s `--bez-lexikonu` i bez, porovnat počet `read`-autoritních řádků
a ručně posoudit vzorek — přesně ten typ měření, který `bench/vazby.py`
sám nemůže nahradit (je to fragmentový bench, ne zátěžový).

**Doplněk (týž tah): ablační přepínač `--bez-graf`.** Přesně proto, že
`graf` mechanismus je neměřený na reálném textu, dostal hned ablaci —
stejný vzor jako `cb6.lexicon.set_seed_enabled`/`bench run --bez-lexikonu`:
`cb6.dialog.set_graf_suggestions_enabled(bool)` (modulový přepínač),
`bench run --bez-graf` ho vypne a přidá `-bez-graf` do labelu zprávy.
Test `tests/test_dialog.py::test_graf_ablace`. Pytest 189+2xfail →
190+2xfail, mypy čisté, `cb6/dialog.py`/`bench/__main__.py` diff beze
nového pylint nálezu (jen posun řádků).

## 2026-09-27 · pokračování · oprava I‑8 díry: `_resolve_possessed` skrytý odhad vlastníka

**Podnět:** vlastní shrnutí + priorita z kritického přezkumu (HANDOVER § 8,
nález 4a subagenta): `ground.py._resolve_possessed` u víceznačného
přivlastnění (víc entit odpovídajících stonku, srovnatelná aktivace)
tiše vybíralo `max(..., key=activation)` — bez `HYPOTHESIS`/open-item,
na rozdíl od analogické nejednoznačnosti u zájmen (`_resolve_pron`, které
tohle řeší už od dřívějška). Bezslužbový fix (nepotřebuje UDPipe/Ollama —
jen graf a existující zaznamenané věty), první bod souhrnu „další kroky“.

**Změna:** `Grounder._owner_candidates` — nová metoda, zrcadlí
`discourse.ambiguous` (poměr aktivace prvního/druhého kandidáta, mez 0,6)
nad uzly přímo (kandidáti na vlastníka nemají metadata `Candidate` z
registru zmínek, přišli ze jmenné shody stonku). `_resolve_possessed`:
(1) existující vlastnictví (`mít`/`vlastnit`) se teď hledá přes VŠECHNY
kandidáty, ne jen přes odhad — nalezená jistota vyhrává nad hypotézou;
(2) když žádné existující vlastnictví není a kandidátů je víc, vznikne
HYPOTHESIS `mít` na KAŽDÉHO kandidáta (ne jen na odhad) + otevřená
položka („Čí je …? Kandidáti: …“) — přesně tvar disclosure jako u
`_resolve_pron`, jen adaptovaný (ambiguity je o VLASTNÍKOVI, ne o termu
role samotné, takže `self._ambiguous`/alternativy sdílené s koreferencí
nešly použít 1:1 — vlastní, ale analogický mechanismus).
**Hypotéza:** stávající test (`test_indefinite_object_instantiates`,
jediný vlastník, jednoznačné) beze změny; nový test (dvě entity „Filip“,
stejná aktivace) dá HYPOTHESIS `mít` na obě + open item; zbytek pytestu
beze změny (nikde jinde nejsou v testech dvě jmenovsky se překrývající
entity s přivlastněním).
**Výsledek:** přesně tak — 190 → **191 passed** + 2 xfailed (nový
`tests/test_ground.py::test_ambiguous_owner_gets_hypothesis_not_silent_
guess`), mypy čisté, `cb6/ground.py` diff beze nového pylint nálezu (jen
posun řádků + 1 dočasná `unused-variable`, hned opravená). Žádná
existující sada (191 testů) se nezměnila — nejednoznačnost vlastníka se
dřív v žádném testu neobjevila, takže díra byla neviditelná, přesně jak
subagent popsal.
**Poučení:** tohle je druhý případ (po `Statement.derived_from`
jednorodičovském) „stejný tvar chyby na dvou místech, jedno má disclosure,
druhé ne“ — `_resolve_pron` a `_resolve_possessed` řeší strukturně
identickou nejednoznačnost (víc kandidátů, blízká aktivace), ale jen
jedno z nich to přiznávalo. Stojí za prověření, jestli podobný vzorec
(nejednoznačnost → tichý `max()`/`[0]` bez HYPOTHESIS) není i jinde v
`ground.py`/`discourse.py` — dnešní fix řešil jen ten jeden konkrétní
nález, ne systematický audit všech míst, která by týž vzorec mohla mít.

## 2026-09-27 · pokračování · `cb6/quantity.py` — primitiv pro `porovnání` (krok 2), operátor záměrně NE

**Motivace:** další bod „krok 2“ (`překryv` hotový, `porovnání` chybí) je
na roadmapě, ale plný operátor (spec: „délka(A) ≤ délka(B) ⇒ vejít_se“)
má nejasnou otevřenou otázku — KTERÝ směr porovnání (`≤`/`≥`/`=`) patří
ke kterému derivovanému predikátu — a to bez reálného textu na ověření
nejde rozhodnout, jen uhodnout (přesně to, co §8/3 v HANDOVER varuje před
lexikonem rostoucím dohadem, ne měřením). Proto jen primitiv, stejný krok
jako `chronos.overlap` před plným `překryv` dřív v týhle relaci.

**Změna:** `cb6/quantity.py` — `Quantity(hodnota, jednotka)`,
`dimension_of`/`to_base`/`compare` (`<`/`=`/`>`, nebo `None` u různé
dimenze či neznámé jednotky — „delší než těžší“ nesmí tiše porovnat čísla
bez ohledu na jednotku). Jednotky (`UNITS`, dnes jen délka+hmotnost) jsou
česká slova natvrdo — poznamenáno v docstringu, že se mají přesunout do
`cb6/lang/cs.json` AŽ se operátor zapojí do čtení (přesun bez testu, který
by ho ověřil, by byl práce navíc — stejná disciplína jako u `cb6/lang/`
refaktoru, dělat datovou vrstvu, až ji něco skutečně používá).
**Hypotéza:** pytest +5 (`tests/test_quantity.py`), mypy/pylint čisté
(nový modul 10/10), žádné bench/QA číslo (primitiv se nikde nepoužívá).
**Výsledek:** přesně tak — 191 → **196 passed** + 2 xfailed, mypy 34
souborů čisté, `cb6/quantity.py` 10.00/10.
**Otevřené (příští tah, ne teď):** lexikonový operátor `porovnání` sám
(řádek s dimenzí + derivovaným predikátem + směrem porovnání, `Lexicon`
přístup analogický `overlap_targets`, `Evaluator` query-time join
analogický `overlap_verdict`) — čeká na konkrétní větu ze skutečného
textu („Je Praha větší než Brno?“, „Věž je vysoká 100 metrů.“), ne na
vymyšlený příklad.

## 2026-09-27 · pokračování · krok 3 (příbuzenství) narazil na závislost; místo toho drobný úklid dat

**Zjištění (ne tah):** zkusil jsem navázat na krok 3 (`inverze`/`skládání`,
G‑3 „Jeho bratr Josef Čapek“) a narazil na skutečnou závislost: čtení
dnes z téhle konstrukce nevytáhne žádný vztahový predikát (`bratr(Josef,
Karel)`) — jen typování `Josef Čapek ∈ bratr` (nominativ jmenovací z
kroku 1) a obecné `mít` z přivlastnění. Bez toho nemá `inverze`/`skládání`
na čem pracovat. V `tests/data/parses.json` je navíc jen JEDNA taková věta
(„Jeho bratr Josef Čapek byl malíř.“) — moc tenký vzorek na to stavět
novou čtecí konstrukci a věřit jí bez druhého/třetího ověření. Rozhodnutí:
neimplementovat teď (riziko dohadu na jednom vzorku), zapsat jako
prerekvizitu kroku 3 v HANDOVER § 6.

**Místo toho:** drobný, bezpečný úklid ze stejného kritického přezkumu
(HANDOVER § 8/4a, poslední neopravená položka „malá“): `ground.py:232`
mělo natvrdo českou příponovou tabulku přivlastňovacích přídavných jmen
(`ův/ova/ovo/in/ina/ino`), zatímco `cb6/lang/cs.json` už podobnou vrstvu
nese (`possessive` — jiná věc, zájmena). Přidán klíč `possessive_suffixes`
(vlastní, ne splynutý s `possessive` — jsou to dva různé jevy: zájmena
vs. derivační přípona ze jména), `cb6.lang.LanguageRules`/`defaults.
POSSESSIVE_SUFFIXES`, `ground.py` re-exportovanou tabulku používá místo
literálu.
**Hypotéza:** beze změny chování (přesný přepis hodnot), pytest beze
změny počtu (jen 2 nové asserce v existujících testech), mypy/pylint
beze regrese.
**Výsledek:** přesně tak — 196 passed + 2 xfailed (beze změny), mypy
34 souborů čisté, `cb6/ground.py`/`cb6/defaults.py`/`cb6/lang` diff beze
nového pylint nálezu (jen posun řádků).
**Poučení:** subagentův nález 4a je teď z devíti položek `derived_from`
(otevřeno), `Registry.candidates` okno (otevřeno, potřebuje reálný
korpus na vyladění), `_resolve_possessed` (opraveno), `Session.topics`/
`_last_said` souběh (otevřeno, potřebuje rozhodnutí o modelu souběhu),
`render.py` literály (otevřeno, velký refaktor s nejistým přínosem bez
2. jazyka), `ground.py` přípony (opraveno) — **2 ze 6 hotové bez služeb,
zbytek buď potřebuje reálný text na vyladění, nebo je to větší
architektonické rozhodnutí, které by J. měl chtít vidět, ne dostat
hotové.**

## 2026-09-27 · pokračování · `ClaudeCliJudge` — Ollamu nahradí menší Claude model (J. pokyn)

**Podnět J.:** „Ollamu může zastoupit nižší model Claude.“ Soudce auditu
(I‑9: LM je jen soudce, nikdy zdroj znalosti) dřív měl dvě cesty:
`OllamaJudge` (lokální služba, nedostupná v cloudu) a `ClaudeJudge`
(Anthropic SDK, potřebuje syrový `ANTHROPIC_API_KEY` — tahle relace má
jen harness OAuth, SDK by na klíč selhal — ověřeno: `pip show anthropic`
nic nenašlo, žádný `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` v prostředí).
Řešení: `claude` CLI je v tomhle sandboxu k dispozici a běží přes
autentizaci, kterou relace už má (`claude -p --model haiku ...`).

**Změna:** `bench/judge.py ClaudeCliJudge` — headless `claude -p`
(`--tools ""` bez přístupu k souborům/shellu, `--json-schema` strukturovaný
výstup místo spoléhání na markdown formátování, `cwd=tempfile.gettempdir()`
**mimo repo** — jinak by CLAUDE.md tohohle projektu soudce nasměrovalo
jako asistenta na conbond6 místo nestranného soudce věty×výroku, ověřeno
prakticky: volání z `/home/user/conbond6` vrátilo „Ahoj, jsem Claude
Haiku 4.5, ready to work on conbond6…“ místo JSON verdiktu). Výchozí
model **`haiku`**, ne `opus`/`sonnet` — soudce je klasifikace, ne úkol
pro největší model (přesně duch J. pokynu „nižší model“). `make_judge`
dostal nový `kind="claude-cli"`; `bench/config.json` defaultní soudce
přepnut z `ollama`/`gemma4` na `claude-cli`/`haiku` (starý ollama nastavení
zachováno v `_ollama_puvodni` klíči, ne smazáno — J. ho možná na svém
stroji chce zpátky).
**Hypotéza:** pytest +7 (`tests/test_judge.py`, `subprocess.run` nahraný
— žádné skutečné volání CLI v testech, drahé a nehermetické), mypy/pylint
čisté (`bench/judge.py` diff beze regrese). Živé ověření (1 skutečné
volání, mimo pytest): „Alois Jirásek se narodil v Hronově.“ + shodný
výrok → „tvrdí“ se správným zdůvodněním.
**Výsledek:** přesně tak — 196 → **203 passed** + 2 xfailed, mypy 34
souborů čisté, `bench/judge.py` diff beze nového pylint nálezu. Živé
ověření prošlo (viz výše).
**Poučení:** tohle NEotevírá `bench run --vse --soudce` (pořád chybí
korpus/UDPipe pro samotné rozbory), ale odstraňuje JEDNU ze dvou překážek
plného měření — až bude korpus/UDPipe po ruce (lokálně, nebo rozšířením
síťové politiky), audit s soudcem půjde spustit rovnou, bez čekání na
Ollamu. Cena za volání je reálná (haiku ~0,001–0,005 $/dotaz, viz živé
ověření) — `audit_sample` v configu (dnes 50) limituje běžný audit na
desítky dolarů max, `CachedJudge` navíc nesoudí týž výrok dvakrát.

## 2026-09-27 · pokračování · `SpacyOracle` opraveno a otestováno (J.: „systém by však měl pracovat bez external LLM“)

**Podnět J.:** po `ClaudeCliJudge` (LLM přes CLI, ale JEN pro bench/audit)
upřesnění: „systém by však měl pracovat bez external LLM.“ Čteno jako
potvrzení I‑9 (LM je jen soudce/generátor otázek, nikdy za běhu součást
odpovídání) a jako směr pro „krok 6“ (NN extraktor struktury) — extrakce
má stát na skutečné NN (trénovaný parser), ne na živém volání LLM. Přesně
to spaCy `cs_core_news_sm` je: lokální síť, žádná síť za běhu, žádný LLM.

**Nález + oprava dvou chyb v `SpacyOracle`** (byl navržený, ne dokončený
dřív tuhle relaci — dnes dotažen a otestován):
1. Kořen věty vycházel s `head≠0` — `t.head is t` (identita) u spaCy
   Token objektů nesedí (`token.head` vrací pokaždé nový wrapper), musí
   být `t.head == t` (spaCy `Token.__eq__` porovnává index). Bez opravy
   by `Parse.root()` v každém rozboru selhalo.
2. `doc.sents` u tohohle malého modelu nespolehlivě dělí věty — prakticky
   ověřeno: „Petr bydlí v Praze. Karel žije v Brně.“ dá JEDNU větu, druhý
   kořen „žije“ se přilepí jako `conj` k prvnímu přes tečku. Oprava:
   vlastní rozdělení na věty regexem PŘED parserem (`(?<=[.!?])\s+(?=
   [A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])`), každá věta se parsuje zvlášť — parser pak
   nemá šanci slévat věty, protože sousední větu vůbec nevidí. Cena:
   slabší heuristika hranic (neumí zkratky „T. G. Masaryk“) — přiznaný
   kompromis náhradní cesty, ne tichá aproximace.

**Změna:** `cb6/oracle.py SpacyOracle` (`parse`/`segment`/`_parses`,
`provenance="spacy model=…"`, nikdy `udpipe2` — I‑12 provenience).
`pyproject.toml` volitelný extra `spacy-cs`. `tests/test_spacy_oracle.py`
(`pytest.importorskip` — hlavní sada na tom nezávisí): kořen, `segment`
na dvě věty se správným kořenem KAŽDÉ, prázdný text selže nahlas, a
**zámek na shodu s UDPipe2** (90/177 vět přesně, 153/907 tokenů jinak) —
ne aby se nasadilo na historická čísla (výslovně ne), ale aby tichá
regrese/zlepšení modelu bylo vidět hned.
**Hypotéza:** pytest +6 (podmíněně, jen když je `cs_core_news_sm`
nainstalovaný), mypy/pylint beze regrese na `cb6/oracle.py` (jen posun
řádků).
**Výsledek:** přesně tak — 203 → **209 passed** + 2 xfailed (`cs_core_
news_sm` je v tomhle sezení nainstalovaný, takže testy běžely, ne jen
přeskočily), mypy 34 souborů čisté, `cb6/oracle.py` diff beze nového
nálezu (`tests/test_spacy_oracle.py` nálezy odpovídají zavedené konvenci
— `W0621` na fixture `oracle`, stejný tvar jako fixture `s` v `test_
dialog.py`).
**Poučení:** `SpacyOracle` teď FUNGUJE korektně (dřív měl dvě tiché
chyby, které by se projevily až na první reálné použití) — ale pořád
platí rozhodnutí nenasazovat na historická čísla (83,1 % shoda tokenů
je málo na míchání s UDPipe2 daty). Použitelný je teď pro přesně to, co
`tests/test_lex_teach.py`/`bench/vazby.py` dělaly ručně: nové věty,
s ručním ověřením neobvyklé stavby, ne naslepo. Otevřené: zapojit jako
volitelné orákulum do `cb6.record`/`bench` s explicitním `--parser spacy`
přepínačem (nikdy jako tichý fallback za UDPipe), až bude jasné, na
kterou konkrétní novou konstrukci se má použít.

## 2026-09-27 · pokračování · reálný korpus JDE naklonovat (git proxy) + `bench run --parser spacy` funguje end-to-end

**Zásadní zjištění (odpověď na „jak dále při současných omezeních“):**
`git clone https://github.com/alchy/conBond2.git` prošel bez problémů —
proxy servíruje anonymní čtení veřejných GitHub repozitářů (jiná cesta
než blokovaná `lindat.mff.cuni.cz` REST API). `bench/data.py
ensure_wiki_corpus` dělá přesně tohle automaticky, takže stačilo spustit
`bench run` — korpus (66 dokumentů, `data/corpus/conBond2/`) se naklonoval
sám. UDPipe (parser) zůstává blokovaný (jiná síťová cesta), ale **skutečný
text + `SpacyOracle` (NN, ne LLM)** dohromady poprvé umožňují spustit
plný bench pipeline (ingest → QA → audit grafu) na reálných datech
v týhle relaci.

**Změna:** `bench/run.py make_oracle(cfg, parser=...)` — `parser="spacy"`
staví `CachedOracle(SpacyOracle(), cache_spacy)`, **vlastní keš**
(`bench/config.json cache_spacy`), nikdy sdílená s UDPipe2 keší (I‑12
provenience na úrovni souboru, ne jen řetězce). `run()`/`report` nesou
`parser`/`oracle_provenance`; `render_report` dá **nepřehlédnutelné
varování** do hlavičky zprávy, když `parser≠udpipe`. `bench/__main__.py
--parser {udpipe,spacy}`; diff proti historii se s `--parser spacy`
**přeskočí úplně** (ne jen potichu srovná nesrovnatelné) — vypíše proč.
**Hypotéza:** mechanické — pytest beze změny počtu (jen wiring, žádná
nová testovaná jednotka logiky), mypy/pylint beze regrese; ŽÁDNÉ QA/
unsupported číslo z tohohle wiringu samotného (to je věc SAMOTNÉHO běhu,
ne kódu).
**Výsledek (smoke test, `--strop 15 --dok alois_jirásek karel_čapek`):**
funguje — yield 79,64/90,31 na 1000 slov (řádově blízko historickému
76,8/89,7 z UDPipe2, i když nesrovnatelné napřímo), QA 9/25, **audit
grafu 0 porušení**, determinismus ano. pytest 209 beze změny, mypy čisté,
`bench/run.py`/`bench/__main__.py`/`cb6/oracle.py` diff beze nového
pylint nálezu.

**Vedlejší nález (na `vztahy_příbuzenské.txt`, real text, ne fragment):**
zkoušel jsem tenhle dokument (definice typu „Tchán je otec manžela nebo
manželky.“) jako test krok‑3 prerekvizity. Skutečný nález je JINÝ, než
jsem čekal a PŘESNĚJŠÍ: 14/16 vět má „X nebo Y“ (disjunkce) → **správně**
REJECTED s důvodem „disjunkce bez prostoru modelů“ (už known limitation,
HANDOVER § 6 bod 5, ne nová chyba). Ale bez disjunkce („Zeť je manžel
dcery.“, „Snacha je manželka syna.“) je nález skutečný:
`být(kdo:∀zeť, co:∃manžel) ⟨subset⟩` je **SAFE** (zeť ⊆ manžel), zatímco
sesterský `nmod:Gen` „dcery“ (KDO je manžel, ne jen manžel obecně) je
REJECTED „vedlejší vztah bez sémantiky“ — **hlavní tvrzení SAFE, i když
podstatná část věty (čí manžel) se zahodila.** Soudce by tohle pravděpodobně
označil „částečně“, ne „tvrdí“. **Hypotéza pro prevalenci:** změřit napříč
korpusem podíl vět, kde SAFE hlavní výrok sdílí uzel se sesterským
REJECTED `nmod` výrokem — čekal jsem menšinový jev (řádově desítky
procent unsupported), který by odůvodnil cílenou opravu.

**Výsledek (skript `prevalence_scan.py`, `--parser spacy`, strop 60
řádků/dok., 28/65 dokumentů než škrtnut časem, 4020 vět):** naivní proxy
(„SAFE + REJECTED na stejné entitě, libovolný `nmod`“) je **83 % vět**
(3340/4020) — ale to je špatná otázka, ne nález o kinship‑vazbě.
Přečtení vzorku důvodů ukázalo, že drtivá většina jsou `nmod` PRÁVEM
zahozené jako vedlejší (`nmod:na+Loc`, `nmod:o+`, časová určení…) — to
je systém, jak má fungovat, ne díra. Skutečný nález z `vztahy_
příbuzenské.txt` je užší a specifičtější: ne „SAFE vedle REJECTED
existuje“, ale konkrétně **`nmod:Gen` u vztahového substantiva
(manžel/otec/dcera…), kde genitiv NENÍ ozdoba, ale určující argument**
(„manžel **dcery**“ ≠ „manžel“) — tohle číslo vyžaduje rozlišit
vztahová substantiva od ostatních, ne jen počítat souběh SAFE/REJECTED.
**Poučení:** naivní prevalence je zavádějící metrika (měřila by 83 %
„problém“ tam, kde 82 z 83 procentních bodů je správné chování) —
skutečný krok 3 potřebuje napřed seznam vztahových substantiv (lexikon,
ne heuristiku nad `nmod`), teprve pak má smysl počítat prevalenci JEN
nad touhle podmnožinou. Neimplementoval jsem opravu bez tohohle rozlišení
— riziko falešné jistoty vyšší než přínos. Plný 65/65 běh jsem zastavil
(dával by jen přesnější číslo špatné metriky, ne odpověď na otázku).
**Další krok (krok 3, upřesněno):** lexikon vztahových substantiv
(`!uč vztah manžel(X, Y)` nebo podobně) + operátor, který genitivní
doplněk vztahového substantiva ADOPTUJE do role, místo aby ho zahodil
jako `nmod`; teprve pak měřit prevalenci a případně inverzi/skládání.

## 2026-09-27 · pokračování · krok 3: lexikon vztahových substantiv (data) + role `čí`

**Změna:** `cb6/lang/cs.json relational_nouns` (34 slov: otec/matka/syn/
dcera/bratr/sestra/manžel/manželka/tchán/tchyně/zeť/snacha/švagr(ová)/
děd(eček)/bab(ička)/vnuk/vnučka/strýc/teta/synovec/neteř/bratranec/
sestřenice/pravnuk(-čka)/prarodič/praděd/prababička/kmotr(a)/nevlastní_
otec/nevlastní_matka — pojmenovaná data, ne graf; podobně jako `place_
nouns`/`time_nouns_base`, ne `cb6/lexicon.py` řádky, protože tohle je
ČTECÍ pravidlo „kdy genitiv u substantiva NENÍ ozdoba“, ne znalostní
vazba mezi predikáty). `cb6/read.py TermSpec.rel_owner` (nové pole) +
`Reader._is_relational_gen_arg(t, c, consumed)`: prostý genitivní NOUN/
PROPN doplněk vztahového substantiva (bez `cc`/`conj` — souřadění
zůstává staré cestě, disjunkce ji zamítne beze změny) se už nepošle do
`_pending_secondary` (→ dřív REJECTED „vedlejší vztah bez sémantiky“),
ale rozřeší se jako normální term a nese se ven jako `TermSpec.rel_
owner`. `cb6/ground.py ground_predication`: term s `rel_owner` přidá
roli `čí` PŘÍMO na hlavní výrok (`resolve_term` stejně jako každý jiný
term — žádná jmenná shoda, žádný odhad).
**Hypotéza:** `vztahy_příbuzenské.txt` (16 vět, `--parser spacy`) — 2/16
nedisjunktivní věty („Zeť je manžel dcery.“, „Snacha je manželka
syna.“) přestanou mít sesterský REJECTED nmod:Gen výrok; zůstane 1 SAFE
výrok s rolí `čí` místo 2 výroků (SAFE + REJECTED); 14/16 disjunktivních
vět beze změny (pořád REJECTED „disjunkce bez prostoru modelů“, teď i
bez `čí“ — koordinace se nepřebírá); pytest +2 (nový modul, hand-built
UD fixture jako `test_lex_teach.py`), mypy/pylint beze regrese; QA na
existujících dvou dokumentech (`alois_jirásek`, `karel_čapek`) beze
změny (relační substantiva tam nejsou frekventovaná).
**Výsledek:** přesně tak. Live test na `vztahy_příbuzenské.txt` (spaCy,
`data/cache/parses-spacy.json`): 34 výroků celkem, **2 SAFE nesou roli
`čí`** (dcera / syn), **žádný sesterský REJECTED nmod:Gen výrok pro tyhle
dvě věty už nevzniká** (dřív 2 statementy na větu, teď 1). 31 REJECTED
zůstává (14 disjunktivních hlavních + jejich koordinované vedlejší
predikace — beze změny, ověřeno testem `test_koordinovany_genitiv_
zustava_vedlejsi_a_disjunkce_zamitne`). `bench run --sada wiki --strop
40 --dok alois_jirásek karel_čapek --parser spacy`: QA 9/25 (36 %),
audit grafu **0**, determinismus ano — beze změny proti hodnotám bez
téhle změny (relační substantiva se v těchhle dvou životopisech
prakticky nevyskytují, čekaně). pytest **211 passed** + 2 xfailed (+2
nové), mypy 34 souborů čisté, pylint diff beze nového nálezu (nová
podmínka v `_term` byla `R0916` 7/5 — vytažena do pojmenované metody
`_is_relational_gen_arg`, 0 nálezů).
**Poučení:** genitiv u vztahového substantiva je přesně ten případ, kdy
„vedlejší vztah bez sémantiky“ byl špatná triáž — sémantika TAM byla,
jen se nerozpoznala jako argument vztahu. Řešení je čtecí pravidlo (jazyk
jako data), ne operátor nad grafem — shoduje se s `place_nouns`/`time_
nouns_base`, ne s `cb6/lexicon.py`. Krok 3 dál: samotné vztahy (inverze
„zeť“↔„tchán“, skládání „otec otce“→„děd“) — teď máme čistý vstup (`čí`
roli, ne zahozený zbytek), na kterém se dá stavět, ale operátor sám
ještě chybí (G‑3 pořád čeká na čtecí konstrukci „Jeho bratr Josef
Čapek“ → vztahový predikát, HANDOVER § 6/8).

## 2026-09-27 · pokračování · krok 3: G-3 opraven — „Jeho bratr Josef Čapek“ je entita + vztah, ne slepené jméno

**Zjištění před opravou** (ověření na reálném korpusu, ne jen na 1
zaznamenané větě — HANDOVER varoval, že vzorek je tenký): grep přes
`data/corpus/conBond2/data/raw/*.txt` na vzor „(Jeho|Její|Jejich)
<vztahové substantivum> <Jméno>“ našel dalších 4 reálné výskyty
(Jaroslav Hašek: „Jeho otec Josef Hašek“; Karel Havlíček Borovský:
„Jeho matka Josefína Havlíčková“; Milan Kundera: „Jeho manželka Věra“;
Petr Bezruč: „Jeho otec Antonín Vašek“) vedle testové věty — konstrukce
je běžná encyklopedická fráze, ne ojedinělost. Zdrojový rozbor
(`tests/data/parses.json`): jméno visí na vztahovém substantivu jako
`flat` (ne `nmod`/`appos`), stejně jako „vitamín C“ — proto se dřív
slepilo do jednoho jména skupiny („bratr Josef Čapek“), Josef Čapek
jako ENTITA nikdy nevznikl a „byl malíř“ viselo na neidentifikovatelné
skupině.
**Změna:** `cb6/read.py Reader._relational_name(t)` — nová „hlava“ pro
`title` (vedle `_title_of`): vztahové substantivum + přivlastnění
(zájmeno/adj, `det Poss=Yes` nebo `amod ADJ Poss=Yes`) + `flat` vlastní
jméno → `title` = jméno, přesně stejná cesta jako nominativ jmenovací
(„drama R.U.R.“): entita + `cls` (typing). `TermSpec.possessor` se tím
pádem nese i na entitu (dřív ho `_resolve_term_inner` v `entity` větvi
ignorovalo). `cb6/ground.py`: `_owner_nodes(t)` (vytažen sdílený kus
`_resolve_possessed`, beze změny chování) + nová `Grounder.
_relational_fact(t, entity_id)` — když má entita `cls` i `possessor`,
vytvoří skutečný vztahový výrok (`bratr(kdo=Josef Čapek, čí=Karel
Čapek)`, SAFE, nebo HYPOTHESIS na každého kandidáta při nejednoznačném
vlastníkovi — stejná I‑3/I‑8 disciplína jako u „Filipovo auto“).
**Hypotéza:** `tests/test_dialog_g.py` (existující fixtura, žádná nová
zaznamenaná věta) — Josef Čapek vznikne jako samostatná entita odlišná
od Karla, „malíř“ na něm, plus výrok `bratr` s rolí `čí`; existující
testy beze změny výsledku; pytest +1, mypy/pylint beze regrese;
real-corpus smoke (`--parser spacy` na `jaroslav_hašek`, `petr_bezruč`)
beze pádu, audit grafu 0.
**Výsledek:** přesně tak. Nový test
`test_g3_pristavek_je_vztah_ne_slepene_jmeno` potvrzuje: Josef Čapek ≠
Karel Čapek (různá id), `bratr(kdo=Josef Čapek, čí=Karel Čapek)` SAFE,
„být malíř“ visí na Josefovi. Všech 8 testů `test_dialog_g.py` prochází
(2 xfail beze změny — G‑1/G‑2 nesouvisí). Celkem **212 passed** + 2
xfailed (+1), mypy 34 souborů čisté, pylint diff beze nového nálezu.
Real-corpus smoke (spaCy, `jaroslav_hašek`+`petr_bezruč`, strop 30):
audit grafu 0, determinismus ano, žádný pád.
**Poučení:** stejné jako u genitivu — architektura to snesla skoro
zadarmo, protože „entita s třídou“ (`TermSpec.cls`) už existovala pro
jiný účel (nominativ jmenovací) a stačilo ji spustit i z jiného
spouštěče. Riziko bylo přesně to, co HANDOVER předvídal („moc tenký
vzorek“) — vyřešeno tím, že jsem si PŘED psaním kódu ověřil další 4
reálné výskyty v korpusu, ne jen věřil jedné zaznamenané větě.
**Zbývá (krok 3, poslední kus):** samotný vztahový OPERÁTOR nad rolí
`čí`/predikátem vztahového substantiva — inverze („X je bratr Y“ ⇒ „Y
je sourozenec X“, pozor na pohlaví), skládání („otec otce“ → „děd“,
potřebuje 2 statementy → `derive()` nejde, query-time join jako
`překryv`). Zatím žádná otázka typu „Kdo je čí tchán?“ nemá odpověď —
vztah SE ZAPÍŠE, ale nic ho zatím nedotazuje.

## 2026-09-27 · pokračování · lze `read.py` nahradit vztahovou NN? — destilační dataset + lineární sonda

**Zadání J.:** „lze read.py nahradit vztahovou NN? na základě poznatku v
read py už trénovat NN, pak read.py konzervovat a učit další vztahy
přes NN“, upřesněno: „jde mi o embeding read vztahu do nn“ — ne
trénovat transformer od nuly, ale zjistit, jestli jsou vztahy, které
`read.py` počítá pravidly, PŘÍTOMNÉ v embeddingu, který NN parser
(spaCy `cs_core_news_sm`) už dnes počítá.

**Zjištění prostředí (rozhoduje, co je vůbec realistické):** žádný
`torch`/`transformers`/GPU v tomhle kontejneru; `sklearn` jde
nainstalovat (síť na PyPI funguje). `cs_core_news_sm` ale MÁ vlastní
kontextový embedding zadarmo (`tok2vec`, 96 dimenzí/token,
`vocab.vectors` prázdné — `token.vector` je interní `tok2vec` výstup,
ne statický slovníkový vektor) — přesně to, co jde sondovat, bez
tréninku čehokoli nového.

**Změna:** dva nové bench nástroje (`python -m bench distill`,
`python -m bench probe`):
- `bench/distill.py` — pro každou větu reálného korpusu uloží (UD parse,
  `Predication` z `read.py` přes `dataclasses.asdict`, kvalita: residuum/
  otevřené položky/claim). `read()` je čistá funkce (parse → struktura,
  žádná paměť) — přesně jednotka „NN dělá strukturu“ (I‑9 zobecněné).
  Dataset jde do `data/distill/` (negitováno jako `data/cache`/`data/
  corpus` — regenerovatelné z korpusu, ne ruční značení).
- `bench/probe.py` — lineární sonda (`LogisticRegression`): štítek =
  jméno role, kterou `read.py` tokenu přiřadil (`_token_labels`, včetně
  role `čí` z genitivu — dřív zapadlá uvnitř `term.rel_owner`, teď
  zvlášť), příznak = `tok2vec` embedding TÉHOŽ tokenu.
**Hypotéza:** sonda ukáže přesnost výrazně nad většinovou základnou u
frekventovaných rolí (kdo/co/kde/kdy), slabě nebo vůbec u řídkých
(čí, dlouhý ocas povrchových předložkových rolí) — čistě informační
číslo, žádná změna běhového systému.

**Výsledek** (10 reálných dokumentů, `--parser spacy`, bez stropu,
56 243 tokenů, 42 182 trénink / 14 061 test):
- **Pokrytí (`distill`, 5 dok., strop 60, 905 vět):** 7,4 % tokenů
  residuum, **7,5 % vět „čistých“** (bez residua, bez otevřených
  položek, hlavní výrok SAFE, ne fragment) — z toho `verb` 58/638 (9 %),
  `copula` 10/92 (11 %), `fragment` 0/175 (logicky — fragment ZNAMENÁ,
  že `read.py` se vzdal). Číslo je nižší, než by čekal někdo, kdo zná
  jen „yield“ (77–90/1000 slov) — protože „čistá VĚTA“ (žádná vedlejší
  věta, žádná závorka, žádné otevřené položky) je přísnější měřítko než
  „aspoň nějaký SAFE výrok z věty“. Horní mez pro čisté napodobování je
  tedy jednotky procent vět, ne desítky.
- **Sonda (`probe`, main run, `min_support=60`, 30 tříd + O + jiné):**
  většinová základna (jen O) **52,0 %**; obyčejná LR **70,5 %** — tedy
  **+18,5 p.b. nad základnou, reálný signál, ne šum**; `class_weight=
  balanced` varianta 49,9 % (POD základnou — cíleně obětuje přesnost na
  O za recall na řídkých třídách), balanced accuracy 48,2 %. Podle role
  (recall, `balanced` model): `jak` 0,83, `pořadí` 0,76, `kdy` 0,75,
  `komu` 0,68, `od_kdy` 0,76, `s_kým` 0,58, `téma` 0,55, `v+Loc` 0,54 —
  **slušný lineární signál**; `kdo` (nejfrekventovanější obsahová role)
  jen 0,29 recall, **`co` jen 0,09 recall i přes 2594 příkladů** — embedding
  jednoho tokenu bez okolí (lineárně) `co` skoro neodliší od zbytku.
  Macro F1 jen 0,21 — většina tříd (dlouhý ocas povrchových
  předložkových rolí, `do+Gen`, `na+Loc`, `z+Gen`…) má F1 pod 0,15.
- **Role `čí` (krok 3, tenhle týden):** **45 výskytů z 56 243 tokenů**
  (0,08 %) — reálná, ale u téhle velikosti korpusu příliš řídká na
  vlastní třídu (pod `min_support=60`, spadla do `jiné`). Zvláštní běh s
  `min_support=30` jsem po ~16 min CPU (mnohem víc tříd, pomalá
  konvergence `lbfgs`) zabil — číslo pro `čí` samotnou čeká na víc dat
  nebo cílenou nadvzorku, ne na další čekání na týž běh.
**Poučení (odpověď J.):** ANO, relace JSOU částečně v embeddingu — lineární
sonda dá +18,5 b.b. nad základnou, což NENÍ nula, ale je to jen ČÁST
`read.py`. Silný signál je hlavně u méně frekventovaných, „ostřejších“
rolí (jak/pořadí/kdy/komu) — token sám o sobě je zřejmě dost
charakteristický (lemma/POS/pád, což `tok2vec` vidí). Slabý signál u
nejdůležitějších rolí (`kdo`, `co`) — to jsou přesně případy, kde
rozhoduje STRUKTURA (kdo je podmět vs. předmět stejného slovesa), ne
jen token sám — LINEÁRNÍ sonda nad jedním tokenem tohle principiálně
nemůže zachytit (chybí kontext role souseda/závislosti). Závěr: `read.py`
NELZE dnes nahradit prostou linear-probe klasifikací nad izolovaným
tokenem — embedding nese ČÁST signálu (potvrzeno číslem, ne dohadem),
ale chybí strukturální kontext (hrany stromu, ne jen uzly). Další krok,
POKUD se půjde dál: featurizovat (embedding hlavy + embedding rodiče +
deprel) místo holého tokenu — to je malý krok (numpy/sklearn stačí), ne
architektura navíc. `čí` samotná potřebuje buď víc korpusu, nebo se
prostě NEUČÍ (zůstává na `read.py` pravidle, protože 45 příkladů na
trénink nestačí, ať je architektura jakákoli).
Vedlejší oprava: `_token_labels` zprvu roli `čí` nepočítala (ležela jen
uvnitř `TermSpec.rel_owner`, ne jako vlastní `RoleFill`) — opraveno,
otestováno (`tests/test_probe.py`, ruční UD fixtura jako
`test_relational_nouns.py`).
pytest **214 passed** + 2 xfailed (+2 nové), mypy 36 souborů čisté,
pylint nových modulů 10/10.

## 2026-09-27 · pokračování · conditioning na HRANĚ, ne na tokenu (J.: „to by mělo jít už na současném vzorku“)

**Zadání J.:** „jak muzeme prevadet soucasne conditioning do modelu?
znalost conditioning je abstrakce nad daty a komunikaci, tedy by to
melo byt jiz mozne na soucasnem vzorku“ — přesný zásah do slabiny
minulého zápisu: `read.py` se u `kdo`/`co` nerozhoduje podle tokenu
samotného, ale podle HRANY (`t.head`, `c.base_deprel`, `c.feat("Case")`)
— sonda nad izolovaným tokenem tohle nemohla vidět bez ohledu na
množství dat, protože to chybělo ve VSTUPU, ne ve vzorku.
**Změna:** `bench/probe.py Example` nese navíc `head_vector` (embedding
rodiče v závislostním stromu, nuly u kořene) a `deprel`.
`_feature_matrix(examples, idx, features, deprel_vocab)` staví buď
`"token"` (původní, jen embedding) nebo `"edge"` (token + rodič +
one-hot deprelu; slovník deprelů jen z TRÉNINKOVÝCH dat, aby test
neunikal do vstupu). `--features {token,edge,compare}` — `compare`
natrénuje obě varianty na STEJNÉM rozdělení dat (čistá A/B, ne dva
nezávislé vzorky).
**Hypotéza:** `edge` vstup zlepší `co`/`kdo` konkrétně (kde se minule
ukázalo, že token sám nestačí — 0,09/0,29 recall), protože `read.py`
u nich rozhoduje podle role souseda ve stromu, ne podle vlastního
tvaru slova.
**Výsledek (2 dok., `alois_jirásek`+`karel_čapek`, strop 40, 3511
tokenů, stejné rozdělení dat pro obě varianty):** potvrzeno směrem i
velikostí. `token`: přesnost 74,0 %/základna 49,5 %, `co` recall 0,67,
balanced accuracy 60,8 %. `edge`: přesnost 75,4 %, `co` recall 0,67
(stejně — na týhle konkrétní podmnožině už `token` samo dost dobré),
**balanced accuracy 64,7 % (+3,9 b.b.)**, obyčejná LR +3,3 b.b. Menší
rozdíl, než jsem čekal na první pohled, ale směr sedí a je to jen 3511
tokenů — pokus o potvrzení na celém vzorku (10 dok., 56 243 tokenů,
`--features compare` = 4 modely na `class_weight="balanced"` + `lbfgs`)
jsem po ~11 minutách CPU (a pak znovu na 5 dok. po ~8 minutách) **zabil
— ne protože by byl nekonečný nebo nepřesvědčivý, ale protože `compare`
trénuje 4 modely a `balanced`+`lbfgs` s desítkami tříd konverguje pomalu
(stejný nález jako minule u `min_support=30`)**. Číslo z 3511 tokenů
beru jako platnou, jen menší odpověď — přesnější (z celého vzorku) čeká
na rychlejší trénink (jiný solver, nebo přeskočit `balanced` variantu
v `compare`), ne na čekání na tenhle běh.
**Poučení (odpověď J.):** ano, conditioning šel zabudovat na SOUČASNÉM
vzorku, žádná nová data — přesně jak jsi řekl. Rozdíl (i na malém
vzorku) je reálný a jde správným směrem (`co` recall stejný, ale
celková `balanced accuracy` výš — sonda se méně plete u řídkých rolí,
když vidí hranu). Otevřené: potvrdit na plném vzorku (potřebuje rychlejší
trénink, ne víc dat) a zkusit ještě bohatší hranu (prarodič ve stromu,
sourozenci — `read.py` sám na některých místech kouká i tam, např.
`_title_of`/`_relational_name` na `flat` sourozence hlavy).

## 2026-09-27 · pokračování · rychlejší solver (standardizace) + potvrzeno na plném vzorku

**Zadání J.:** „zkus rychlejší solver, potvrď na plném vzorku“.
**Zjištění (proč to bylo pomalé — ne solver, ale škála vstupu):**
`lbfgs` na SMÍŠENÉM vstupu (embedding ~N(0,1) + one-hot 0/1) konverguje
řádově pomaleji, protože Hessián je špatně podmíněný. Změřeno na 5 dok.
(26 349 tokenů, `edge`, `class_weight=balanced`): `lbfgs` bez
standardizace **84,9 s**, se standardizací (`StandardScaler`, fit jen na
trénink — bez úniku z testu) **17,5 s** (4,8×) — a přesnost STEJNÁ nebo
o chlup lepší (0,712 vs 0,707). `liblinear` na 16+ tříd rovnou spadl
(neumí multiclass bez `OneVsRestClassifier`) — nezkoušeno dál, scaling
sám stačil.
**Změna:** `run_probe` teď standardizuje `xtr`/`xte` (`StandardScaler`
fit na `xtr`) před `LogisticRegression`, `max_iter` sníženo 2000→1000
(se standardizací zbytečné víc).
**Výsledek (potvrzeno na PLNÉM vzorku — 10 dok., 56 243 tokenů, 42 182
trénink/14 061 test, `--features compare`, doběhlo v řádu minut, ne
přes 10):**
- **token, obyčejná LR: 70,6 %** (základna 52,0 %).
- **edge, obyčejná LR: 76,4 % (+5,8 b.b. proti token)** — potvrzeno,
  o něco silněji než na malém vzorku (+3,3/+3,0 b.b.).
- **token, balanced: 50,0 % / balanced accuracy 48,4 %.**
- **edge, balanced: 63,8 % (+13,8 b.b.!) / balanced accuracy 50,2 %
  (jen +1,8 b.b.)** — rozpor mezi těma dvěma čísly je sám o sobě nález:
  `accuracy_balanced` vyskočilo hodně, ale `balanced_accuracy` (makro
  průměr recall přes VŠECH 30+ tříd) sotva — protože zisk se soustředí
  do dvou nejfrekventovanějších tříd a v makro průměru přes tři desítky
  tříd se to rozředí.
- **Přesně tam, kde to mělo pomoct, to pomohlo nejvíc — `kdo`/`co`**
  (`balanced` model, recall): **`co` 0,08 → 0,37 (+29 b.b.)**, **`kdo`
  0,29 → 0,46 (+17 b.b.)**. To jsou dva nejdůležitější obsahové role
  (nejvíc příkladů, nejvíc otázek na nich stojí) a přesně ty, co token
  sám (bez rodiče/deprelu) nedokázal rozlišit — teď ANO.
- Dlouhý ocas řídkých rolí (15–40 příkladů) je smíšený, ne jednoznačně
  lepší: `jak`/`kdy`/`jaký`/`z+Gen`/`kam` zlepšené (+5 až +23 b.b.
  recall), ale `jak_dlouho`/`o_čem`/`za_Acc`/`podle+Gen` se zhoršily
  (šum na pár desítkách příkladů, ne systematický regres).
**Poučení:** conditioning na hraně přesně cílí na to, co token sám
neuměl (structural role disambiguation u `kdo`/`co`), a makro-průměrovaná
metrika (`balanced_accuracy`) tenhle konkrétní, nejdůležitější zisk
schovává — na příště: hlásit recall jmenovitě u `kdo`/`co`/`čí`, ne jen
jedno souhrnné číslo přes všechny role stejně važně. Odpověď J. je teď
úplná: read.py se dá ČÁSTEČNĚ nahradit i lineárním modelem, když vstup
nese hranu — u `kdo`/`co` už docela dobře (0,46/0,37 recall, ne dokonalé,
ale ne náhoda), u zbytku pořád slabě. Krok, který by dal víc, je bohatší
hrana (sourozenci, prarodič), ne jiný model.
pytest 214 passed + 2 xfailed beze změny, mypy/pylint čisté.

## 2026-09-27 · pokračování · krok 3 (poslední kus): operátor `inverze`

**Zadání J.:** „pokracuj sam dal, krok 3 vztahový operátor inverze“ —
výslovné pokračování i přes dřívější poznámku „vědomě NEimplementováno,
chybí reálné otázky“ (HANDOVER § 6/8, tentýž den). Vyřešeno stejně jako
`překryv` (krok 2): logická vrstva se dá poctivě otestovat na ručně
sestavené paměti (fragmenty, ne fiktivní věty prezentované jako reálné),
čtecí strana (rozpoznat otázku „Je X sourozenec Y?“ z textu) zůstává
otevřená — čeká na reálné otázky, ne na dohad.
**Změna:**
- `cb6/lexicon.py`: `inverze` dostal kód — validace (2 argy, síla jen
  `implies` — směrové pravidlo, ne nápověda), `Lexicon._inverze`
  (zdrojový vztah → řádky), `inverze_rules_by_target(lemma)` (dotaz zná
  cíl) / `inverze_targets(pred)` (zrcadlo, zná zdroj) — přesně souměrné
  s `overlap_*` u `překryv`.
- `cb6/lexikon/inverze.jsonl` (12 řádků): `bratr`/`sestra`→`sourozenec`,
  `otec`/`matka`→`dítě`, `syn`/`dcera`→`rodič`, `děd`/`bába`→`vnouče`,
  `vnuk`/`vnučka`→`prarodič` (cíl rodově NEUTRÁLNÍ — zdroj neurčuje rod
  DRUHÉ strany vztahu, konkrétní rod bez dokladu by byl tichý odhad,
  I‑3), `manžel`↔`manželka` (přesný pár, oba směry, rod obou stran daný
  už zdrojem).
- `cb6/lang/cs.json relational_nouns`: přidány cílové neutrální výrazy
  (`sourozenec`, `dítě`, `rodič`, `vnouče`) — připraveno na budoucí
  čtení genitivu u těchhle jmen stejnou cestou jako u `manžel dcery`.
- `cb6/logic.py Evaluator.inverze_verdict(q)`: query-time join (dvě role
  dotazu — `kdo`, `co`, `čí` — spojené přes lexikon, ne `derive()`,
  stejná architektura jako `overlap_verdict`). Existuje-li výrok
  `zdroj(kdo=Y, čí=X)` pro zdroj, jehož `inverze` cíl je lemma role
  `co`, dotaz „Je X <cíl> Y?“ dá ANO. Jen ANO — chybějící fakt je NEVÍM,
  ne NE (nevíme, nepopřeli jsme). Wired do `evaluate()` hned za
  `overlap_verdict`.
- `bench/graphcheck.py`: `lex_path` chodí i po `inverze` (implies
  jednosměrně, jako `překryv`); nový obecný hard krok `role:<jméno>`
  (`a`=výrok, `b`=term — přímá kontrola hrany `role:<jméno>` z exportu,
  ne odvozená cesta jako `member`/`subset` — ověřuje PŘESNÉ svázání
  faktu s argumenty, ne jen že nějaký fakt daného predikátu existuje).
- `cb6/dialog.py`: `!uč inverze bratr => sourozenec` (vlastní slovo v
  příkazu jako `překryv` — jinak by `=>` padlo na `implikace`, jinou
  sémantiku).
- `tests/test_inverze.py` (4 testy, ruční `Statement`/`Memory` — stejný
  žánr jako `test_prekryv.py`): `bratr(Josef,čí=Karel)` → ANO na „Je
  Karel sourozenec Josefa?“ (i doloženo z grafu, i bez materializace
  řádku `inverze` selže rekonstrukce — I‑12); `manžel`/`manželka` přesný
  pár; chybějící fakt → NEVÍM; ŠPATNÝ SMĚR (Josef sourozenec Karla, ne
  obráceně) → NEVÍM, ne falešné ANO.
**Hypotéza:** pytest +4, mypy/pylint beze regrese, real-corpus smoke
(`--parser spacy`, `alois_jirásek`+`karel_čapek`) beze pádu a beze
změny QA (operátor se v těhle dvou dokumentech nepoužije — čtecí strana
není zapojená).
**Výsledek:** přesně tak. pytest **218 passed** (+4) + 2 xfailed, mypy
36 souborů čisté, pylint diff beze nového nálezu (jen posun řádků —
ověřeno `git stash` diffem). Smoke test QA 9/25 beze změny, audit grafu
0, determinismus ano.
**Poučení:** krok 3 návrhu je teď HOTOVÝ na logické vrstvě (lexikon +
query-time join + graphcheck), stejně jako krok 2 (`překryv`) — obě dvě
čekají na stejnou věc: reálný text/otázky, ne na další kód. Role `čí` a
predikáty vztahových substantiv se teď ZAPISUJÍ (dnešní ráno) i
DOTAZUJÍ (teď) — jen čtecí strana otázky („Je X sourozenec Y?“ z
reálné věty) chybí, a to záměrně, dokud nebude co číst.

## 2026-09-27 · pokračování · krok 5: `Memory.rules` sjednoceno s lexikonem

**Zadání J.:** „pokracuj sam dal, krok 5 sjednotit Memory.rules s
lexikonem“. Nález ze samotného návrhu (`docs/superpowers/specs/2026-
08-17-znalostni-vazby-design.md` § 0): `Memory.rules` (můstková
pravidla z `!pravidlo jet(kam:X) => být(kde:X)`) měla provenienci
označenou jako „částečná (`uses_rule` na id `r…`, ale uzel `r…` v
exportu není výrok s proveniencí)“ — ověřil jsem přímo v kódu
(`cb6/logic.py` staré `evaluate`/`enumerate_`): most opravdu jen
`p.steps.append(f"pravidlo {rule.id}: …")`, ŽÁDNÝ `hard` krok — o
POZNÁNÍ HORŠÍ, než spec psal (ne „částečná“, ale ŽÁDNÁ strojová
rekonstrukce z grafu — I‑12 díra, ne jen kosmetika).
**Změna:**
- `cb6/lexicon.py Link`: nové pole `role_map: dict[str,str]` (jen
  `implikace`, validace hlídá) — do JSON jen když neprázdné
  (`mapa_rolí`, jako `modalita`). `Lexicon.bridge_rules()` — všechny
  `implikace` řádky s mapou rolí (volající si shodu s `args[1]` ověří
  přes `same_pred`, protože dotaz smí být i synonymem cíle, ne jen
  přesná shoda — beze změny proti starému chování).
- `cb6/memory.py`: **`Rule` třída, `Memory.rules`, `add_rule` zaniklo
  úplně** (ne jen zastaralé — smazáno; staré JSON soubory s klíčem
  `"rules"` se tiše přeskočí, žádný v repu populovaný nebyl). `add_link`
  dostal `role_map` parametr.
- `cb6/logic.py`: obě místa „pravidla“ (`evaluate`, `enumerate_`) čtou
  `self.lex.bridge_rules()` místo `m.rules` — a NAVÍC (oprava, ne jen
  refaktor) teď volají `self.m.use_links((link,))` + `p.hard.append(
  ("lex", src_pred, dst_pred))` — most je od teď STROJOVĚ
  rekonstruovatelný z exportu (dřív nebyl vůbec).
- `cb6/dialog.py`: `!pravidlo` píše `m.add_link("implikace", (src,dst),
  "implies", "said", …, role_map=…)` místo `m.add_rule` — id se změnilo
  z `r0001` na `lex:said:0001` (řádek lexikonu, ne zvláštní prostor id).
- Testy: `test_dialog.py::test_rule_command_bridges` (nový assert na
  `vazba` uzel s `mapa_rolí` v exportu), `test_logic.py::test_rule_
  bridges` (nový assert na `hard=("lex",…)` a `proof.links`),
  `tests/test_lexicon.py` (2 nové: `bridge_rules()` vrací jen řádky s
  mapou, `implikace` bez mapy funguje beze změny; validace + JSON
  round-trip mapy rolí).
**Hypotéza:** pytest beze změny počtu krom 2 aktualizovaných asercí
(chování, ne API, se mění — id formát), +2 nové v `test_lexicon.py`;
mypy/pylint beze regrese; real-corpus smoke (`--parser spacy`) beze
pádu a beze změny QA (bridge rules se v těch dokumentech nepoužívají).
**Výsledek:** přesně tak. **220 passed** (+2) + 2 xfailed (nesouvisející
G‑1/G‑2 nálezy, beze změny) — první průchod po refaktoru měl 2 selhání
přesně na starý id formát (`r0001` → `lex:said:0001`), opraveno
aktualizací asercí, ne obejito. mypy 36 souborů čisté (1 drobná
anotace typu u `Link.to_json` kvůli novému poli), pylint diff jen
posun řádků (ověřeno `git stash`) + 1 nová „missing docstring“ (stejná
konvence jako sousední testy v souboru). Smoke test QA 9/25 beze
změny, audit grafu 0.
**Poučení:** tohle byla oprava reálné I‑12 díry, ne jen úklid — most
`!pravidlo` dřív nešel doložit z grafu vůbec, teď jde (`vazba` uzel +
tvrdý krok `lex`). `kind="rule"` (podmínkové věty z textu, `derive()`)
jsem VĚDOMĚ nesjednotil — je to jiná věc: vzor s KONKRÉTNÍMI vázanými
termy (entitami), ne čistě jméno-na-jméno predikátová vazba jako
lexikon; navíc už je plně graf-viditelný (`derived_from`, `uses_rule`,
`source`) už dnes. Násilné sloučení by nic nezlepšilo, jen zamlžilo
rozdíl mezi „vazba mezi predikáty“ a „odvození nad konkrétním faktem“.
Krok 5 návrhu je tím hotový — počet míst, kde „vazby“ žily, kleslo ze
čtyř (`SYNONYMS`, `Memory.learned`, `Memory.rules`, `kind=rule`) na dvě
(lexikon jako data + `kind=rule` jako odvození nad entitami), přesně
jak návrh chtěl („cíl integrace je počet míst snížit na jedno“ — jedno
by smazalo skutečný rozdíl mezi nimi; dvě se zbytkovým, ODLIŠNÝM
významem je správný cíl, ne kompromis).

## 2026-09-27 · pokračování · krok 6: render odpovědí — méně dat, víc klidu

**Zadání J.:** filosofická řada zpráv o „moudrosti, ne chytrosti“, „partner
pro moudro, ne databáze“ — a pak konkrétně: „krok 6 render odpovědí —
méně dat, víc klidu“. Necílil jsem na PROSU (spec § 9 výslovně chce
strukturovaný výpis „role: výplň“, protože hezká věta bez krytí je přesně
ten paskvil, co conbond4 § 8 poučil) — cílil jsem na to, co dělá odpověď
REPORTEM místo klidné věty: kolik řádků a kolik dat na řádek.
**Rozbor před změnou:** `answer_matches` (bench QA) čte hlavně STRUKTUROVANÁ
data (`fillers`), text jen jako slabší `text_hit` (substring) — takže
`render.py` šlo bezpečně přeformátovat beze změny QA čísel. Pinovaných
testů na PŘESNÝ text NEVÍM/MOŽNÁ výstupu nebylo (`verdict.notes`/`.missing`
se testují jako data, ne přes `.text`) — jen ANO/NE proof-rendering má
pinované asercie (zdroj, statement id) → nechal jsem ho beze změny (bezpečnější,
větší riziko regrese), soustředil se na NEVÍM/MOŽNÁ, kde je „hodně dat, málo
klidu“ nejvíc vidět (`docs/UKAZKY.md` „vím:“ sekce — až 5 plných výroků se
zdrojem u KAŽDÉHO).
**Změna (`cb6/render.py`):**
- `KNOWN_SHOWN_MAX = 3` (dřív natvrdo 5): u NEVÍM se blízké/vyvolané výroky
  ukážou nejvýš 3×, bez zdroje (`with_source=False` — `!ukaž <id>` dá zdroj
  i celý výrok tomu, kdo ho chce); zbytek se jen SPOČÍTÁ („+ N další“), ne
  zahodí — nic z I‑12 se neztrácí, jen se nezobrazuje defaultně navíc.
- `missing`/`notes` (může jich být víc) se slučují do JEDNÉ řádky (`"; "`
  join) místo jedné řádky na položku — stejná informace, míň vizuální váhy.
- `tests/test_render_answer.py` (3, ruční `Statement`/`Memory`/`Verdict`):
  strop + počítadlo zbytku, pod stropem se nic nepočítá, missing/notes
  sloučené do jedné řádky každé.
**Hypotéza:** pytest +3, mypy/pylint beze regrese (ověřeno `git stash`
diffem); `docs/UKAZKY.md` čeká na regeneraci (potřebuje UDPipe/spaCy
keš na konkrétní věty scén — zablokováno stejným chybějícím prostředím
jako zbytek dneška, ne mou změnou).
**Výsledek:** přesně tak. **223 passed** (+3) + 2 xfailed beze změny, mypy
36 souborů čisté, pylint diff jen posun řádků. Ruční ověření na reálném
scénáři (`RecordedOracle tests/data/parses.json`, „Bydlí Petr v Brně?“):
před — `- bydlet(kdo: Petr, kde: Praha)  — zdroj: „Petr bydlí v Praze.“
(dialog, věta 1)`; po — `- bydlet(kdo: Petr, kde: Praha)` (zdroj pryč,
zbytek věty stejný). `docs/UKAZKY.md` se NEregenerovalo (`bench ukazky`
spadlo na `segmentace … není v data/cache/parses.json` — scény potřebují
přesné věty z živého UDPipe, které tahle relace nemá) — zapsáno jako
otevřený dluh, ne obejito náhradou za spaCy (jiná provenience by
kanonický demo dokument tiše zkreslila, I‑12).
**Poučení:** „klid“ v odpovědi nejde přidat jako styl navrch — je to
otázka, KOLIK toho systém řekne, když už neví. Zdroj/plný výrok pro
KAŽDÝ blízký fakt byl užitečný pro AUDIT (`!ukaž`), ne pro ODPOVĚĎ — dvě
různé potřeby, dřív slité do jedné šablony. Rozdělení (odpověď stručná,
`!ukaž` beze změny vyčerpávající) je přesně ten typ úpravy, co J. myslel
„moudrostí“: neztratit nic, jen neukazovat všechno najednou tomu, kdo se
jen zeptal.

## 2026-09-27 · pokračování · validace mechanismu `graf` na reálném korpusu — vypnut ve výchozím stavu

**Podnět:** HANDOVER § 6 bod „‑1“ (nejvyšší priorita, otevřeno od kroku 3):
`Session._suggest_link_from_graph` běžel dosud jen na fragmentech
(`bench/vazby.py`, 7/7) — nikdy na reálném textu. Riziko pojmenované už
tehdy: shoda `kdo` + 1 další role u dvou vět o téže osobě nemusí znamenat
parafrázi, může to být náhoda (jiná událost sdílející místo/datum/objekt).

**Hypotéza:** postavit `bench/graf_audit.py` (sbírá návrhy + dohledá
zdrojové věty obou stran, samo verdikt nevynáší), spustit na celé reálné
sadě wiki (16 dokumentů, ~180 000 slov, `--parser spacy` — UDPipe v
tomhle sezení neběží), ručně přečíst vzorek. Očekávání bylo otevřené
(„buď je to použitelné, nebo ne — bench rozhodne, ne dohad“), ale
dvojitá role byla navržená jako opatrnější než `korekce` (jeden signál
navíc), takže jsem čekal menšinový, ne 100% šum.

**Výsledek:** **80 návrhů** na 16 dokumentech (rozpětí 0–21 na dokument;
`antarktida`, `fyzika_gravitace` 0; `božena_němcová` 21, `sopka` 16
nejvíc). Ruční čtení dohledaných vět u vzorku (~35 návrhů, napříč
`alois_jirásek`, `bohumil_hrabal`, `božena_němcová`, `karel_čapek`,
`sopka`): **žádný jeden nebyl skutečná parafráze**. Vzorec, co se
opakoval: dvě věty o téže entitě v jiné souvislosti sdílející náhodou
i druhou roli — `pokračovat`~`zemřít` (`kde`=Praha ve dvou různých
větách o Jiráskovi), `mít`~`zaměřovat` (`co`=„prózy“ jen v jedné,
shoda přes jiný sdílený term), `konat_se`~`uskutečnit_se` (dvě různé
svatby, sdílí jen kostel), `sopka`: `jednat_se`~`odehrávat_se`,
`docházet`~`nastávat` a další — impersonální/reflexivní věty o
tématu dokumentu (ne o osobě), kde `kdo` zjevně drží nějaké téma
dokumentu misto aby byla role prázdná, což dvojici vět bez jakéhokoli
sémantického vztahu dá shodu obou rolí. Jeden nález stojí za
samostatné prošetření jindy: `božena_němcová` „naleznout ~ oslovit“
spároval větu, kde je Němcová `kdo` slovesa `naleznout`, s větou, kde
`kdo` slovesa `oslovit` je gramaticky Josef Wenzig (ne Němcová) —
možná chyba přiřazení role u elipsy podmětu v `read.py`/`ground.py`,
ne u mechanismu `graf` samotného; nezkoumáno dál v tomhle tahu.

**Rozhodnutí:** `cb6.dialog._GRAF_SUGGESTIONS_ENABLED` výchozí `False`
(dřív `True`) — pravidlo 2 („recall ↑ + precision ↓ = regrese, nikdy
nevolit význam kvůli počtu“) platí i mimo verdikt: síla `related` sice
nemůže poškodit odpověď (I‑3), ale 80 šumových řádků na 16 dokumentech
by lexikon zbytečně zaplevelilo bez jediného zisku. Kód i zlatá úloha
`bench vazby` (`graf:parafraze`) zůstávají — dokazují, že MECHANISMUS
funguje, jen se nepoužívá produkčně, dokud nebude kritérium přesnější
než topologická shoda dvou rolí (návrh pro příště: sousednost vět nebo
sémantická blízkost predikátů, ne čistě shoda termů). Přejmenoval jsem
ablaci z `--bez-graf` (vypínal by něco, co už je vypnuté) na
`--se-grafem` (zapíná pro budoucí přeměření) — `bench run --se-grafem`.
**Testy:** `tests/test_dialog.py::test_graf_uci_vazbu_z_parafraze_bez_
opravy` upraven (dočasně zapíná mechanismus přes nový getter
`graf_suggestions_enabled()`/setter, ne natvrdo — oprava i latentní
chyby v `test_graf_ablace`, který dřív obnovoval natvrdo `True` bez
ohledu na to, jaký byl stav PŘED testem), nový
`test_graf_vypnuty_ve_vychozim_stavu` (bez explicitního zapnutí — týž
scénář, žádná vazba). `bench/vazby.py::_run_veta` dostal parametr
`graf: bool = False` (dočasné zapnutí/obnova pro zlatou úlohu).
Pytest **223 passed + 2 xfailed** (beze změny počtu — `test_graf_ablace`
nahrazen `test_graf_vypnuty_ve_vychozim_stavu`, jinak stejná sada), mypy
čisté (`cb6/dialog.py`, `bench/vazby.py`, `bench/__main__.py`,
`bench/graf_audit.py`, `tests/test_dialog.py`), pylint diff (`git stash`)
beze nového nálezu.
**Poučení:** opatrnostní návrh („dvě role místo jedné“) fragmentový test
prošel, ale na reálném textu neobstál — encyklopedická próza je plná vět
o téže osobě/tématu, které náhodou sdílí dvě role a přitom o ničem
společném nemluví; skutečná parafráze („X udělal A“ / „X udělal B téhož
A“ jinými slovy) je na reálném textu vzácná, ne běžná. Měření na
fragmentech dokazuje jen že KÓD dělá, co má — nedokazuje, že HEURISTIKA
je na reálném vstupu dost ostrá. Bench, co mate tyhle dvě věci, by
takovouhle regresi (ticho šumu do lexikonu) nezachytil vůbec — proto
`graf_audit.py` zůstává jako samostatný, opakovatelný nástroj, ne
jednorázový skript.
