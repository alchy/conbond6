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
