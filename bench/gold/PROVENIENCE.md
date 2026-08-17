# Zlaté otázky v repu — provenience

| soubor | počet | původ | kvalita |
|---|---:|---|---|
| `etalon.json` | 40 | conBond2 `data/gold/etalon.json` (ručně psané, 31 answer / 9 unsure; druhy zvířata, věci, životopisy, zápory, role, téma, bible) | kurátorované |
| `conbond.json` | 95 | conBond2 `data/gold/conbond.json` (z conBond1 `gold_mixed`, ručně psané s módy answer/unsure/clarify) | kurátorované |
| `otazky-filtr.json` | viz `otazky-filtr.log.md` | conBond2 `data/gold/otazky.json` (682 automaticky generovaných kde/kdy) po valenčním filtru `bench/gold.py` | automatické, filtrované — vykazují se zvlášť, do hlavního čísla QA nejdou |

Požadavek J. (17. 8. 2026): otázky i věty pro testy a učení musí mít hlavu a patu.
Automatická sada obsahovala paskvily („Kdy vytvořil Josef Čapek?“, „Kdy se seznámil
Josef Čapek?“ — bez předmětu, který věta má); filtr je odstraňuje deterministicky
a auditovatelně (důvody v logu). Další krok (plán, Task 5b): kurátorovaná sada
generovaná LM s ukotvením na větu a ověřená člověkem.
