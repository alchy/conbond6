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
