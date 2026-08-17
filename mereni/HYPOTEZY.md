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
