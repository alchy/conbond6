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
