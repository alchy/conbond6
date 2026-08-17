# conbond6 — měřitelná cesta od psaného textu ke znalosti

Šestý pokus o systém, který **z českého textu získá znalost, věrnou zdroji,
vysvětlitelnou, dotazovatelnou a bezpečnou vůči domýšlení** — a který to
o sobě dokáže *změřit*. Vychází z conbond5 (klon s historií, balíček `cb5 →
cb6`); mění se měřítko, ne motor.

- **Zadání a invarianty I‑1…I‑12:** [`docs/superpowers/specs/2026-08-17-conbond6-design.md`](docs/superpowers/specs/2026-08-17-conbond6-design.md)
- **Plán v1:** [`docs/superpowers/plans/2026-08-17-conbond6-v1.md`](docs/superpowers/plans/2026-08-17-conbond6-v1.md)
- **Hypotézy a výsledky každého tahu:** [`mereni/HYPOTEZY.md`](mereni/HYPOTEZY.md) · zprávy `mereni/<datum>-<commit>.md`

## Jedna věta

Text → čtení (UDPipe → tabulkové čtení, nic se neztrácí) → **triáž** (co je
tvrzení, co podmínka, co obsah promluvy, co fráze) → **graf** (výroky
s proveniencí, statusem `SAFE / HYPOTHESIS / REJECTED`, stupněm `read / said /
derived`, výchozími volbami) → logika (ANO / NE / NEVÍM s důkazem, jen nad
`SAFE`) → odpověď, jejíž cesta je v grafu vidět (`!ukaž s0042`).

## Běh za 5 minut

Předpoklad: služba UDPipe z conBond3 na `127.0.0.1:42200` (jen pro nové
rozbory a bench; testy jedou z nahraných rozborů) a pro precision audit
Ollama s modelem `gemma4:latest` (viz `bench/config.json`).

```bash
python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q                       # hermetické testy
.venv/bin/python -m cb6 chat                        # REPL: vlož text, ptej se, !ukaž, !hypotéza, !statusy, !otevřené
.venv/bin/python -m bench run --sada wiki --strop 40 --dok alois_jirásek --soudce   # rychlá smyčka s auditem
.venv/bin/python -m bench run --vse --dvakrat --soudce --audit-doky 8               # plný běh → mereni/
.venv/bin/python -m bench audit --dok alois_jirásek --rucne                          # lidský vzorek (I‑12 otázka)
.venv/bin/python -m bench diff mereni/A.json mereni/B.json
.venv/bin/python -m bench gold-filter               # přegenerovat vyfiltrované automatické otázky
```

## Co bench měří (spec § 5)

| metrika | co říká |
|---|---|
| **knowledge yield** hl./vše | `SAFE` výroků na 1 000 slov — hlavní predikace / všechny (bez pravidel a typování) |
| statusy | `SAFE` · `HYPOTHESIS` · `REJECTED` (+ nálady `pattern`, `reported`) |
| zbytek %, open/větu | co čtení neumístilo; otevřené položky (backlog) |
| QA | správně / otázek; **kurátorované** zvlášť (hlavní číslo); dosah 0 / 1‑3 / 4‑10 / >10 / jiný segment |
| **precision audit** | vzorek `SAFE` výroků × zdrojová věta → *tvrdí / netvrdí / částečně*; soudce (Ollama) + člověk; unsupported = (netvrdí + ½ částečně)/n s Wilsonovým intervalem; shoda soudce/člověk; „nechápu z grafu“ % |
| **audit grafu** | provenience, derivace, statusy, osiřelost, otevřené; **rekonstrukce odpovědi jen z exportu** (I‑12) |
| determinismus | dva běhy = týž otisk paměti |
| diff | proti předchozí zprávě (i proti conbond5 `bench-vse.json`) |

Zlaté otázky (`bench/gold/`, s proveniencí): kurátorované `etalon` 40 a
`conbond` 95 z conBond2 beze změny; automatické `otazky.json` 682 po
valenčním filtru **204** (`otazky-filtr.log.md` — proč které padly);
conBondCorpus 120 otázek (Vesmír, Hudba). Kurátorované a automatické se
vykazují zvlášť; automatické mají i chybné odpovědi (nález), do hlavního
čísla nejdou.

## Invarianty, které hlídají testy

| | invariant | test |
|---|---|---|
| I‑1 | žádná brána zápisu | `test_dialog_g` (každá věta zapsána), bench `written_pct` |
| I‑3 | hypotéza nikdy ve verdiktu | `tests/bench/test_i3.py`, `test_discourse`, `test_render_show` |
| I‑4 | zamítnutí není neznalost | `test_rules::test_zamitnuti_se_hlasi_ne_mlci` |
| I‑7 | determinismus, replay | `test_rules`, `test_dialog_g`, bench `--dvakrat` |
| I‑8 | nevolit význam kvůli počtu | `test_triage` (podmínka, disjunkce), `test_discourse` (dva kandidáti → hypotézy) |
| I‑11 | paměť je graf | `test_graph_export`, `bench/graphcheck` |
| I‑12 | odpověď rekonstruovatelná z grafu | `tests/bench/test_graphcheck`, `bench/graphcheck.check_answer` |

## Kde co je

```
cb6/       oracle chronos defaults read triage discourse memory ground logic recall render dialog cli viewbase_app
bench/     data gold qa metrics run graphcheck audit judge diff __main__ · gold/ (zlaté otázky) · config.json
tests/     hermetické (nahrané rozbory v tests/data/parses.json; nové věty: sentences.txt + python -m cb6.record)
mereni/    HYPOTEZY.md · zprávy · audit-<doc>.json (lidské odpovědi) · audit-cache.json (soudce)
```

## Stav (17. 8. 2026, dva dokumenty, strop 40 řádků, vzorek 100 výroků)

conbond5 výchozí: unsupported **76,5 %**, yield 160/298 · po triáži, opravách
čtení a registru referentů: unsupported **23,0 %** [15,8–32,1], yield **89/94**,
QA 12/17 beze změny, graf 0 porušení, determinismus ano. Plný běh a lidský
audit: `mereni/`.
