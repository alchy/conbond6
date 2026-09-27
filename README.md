# conbond6 — měřitelná cesta od psaného textu ke znalosti

Šestý pokus o systém, který **z českého textu získá znalost, věrnou zdroji,
vysvětlitelnou, dotazovatelnou a bezpečnou vůči domýšlení** — a který to
o sobě dokáže *změřit*. Vychází z conbond5 (klon s historií, balíček `cb5 →
cb6`); mění se měřítko, ne motor.

- **Koncept (proč takhle):** [`docs/KONCEPT.md`](docs/KONCEPT.md) · **Handover (stav, jak pokračovat):** [`docs/HANDOVER.md`](docs/HANDOVER.md)
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

Předpoklad pro plné rozbory: služba UDPipe z conBond3 na `127.0.0.1:42200`
(jen pro nové rozbory a bench; testy jedou z nahraných rozborů) a pro
precision audit Ollama s modelem `gemma4:latest`, nebo `claude-cli`/`haiku`
jako soudce bez Ollamy (viz `bench/config.json`). **Bez těchhle služeb**
(např. cloudové sezení): `pytest -q` běží vždy hermeticky; `bench run
--parser spacy` (`pip install cs_core_news_sm`) dá náhradní český NN
parser, funkční i bez sítě na LINDAT/UDPipe — čísla s ním NEJSOU
srovnatelná s UDPipe2 (jiná provenience, I‑12), ale stačí na fragmentové
a real-corpus hypotézy, viz `docs/HANDOVER.md` § 2.

```bash
python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q                       # hermetické testy
.venv/bin/python -m cb6 chat                        # REPL: vlož text, ptej se, !ukaž, !hypotéza, !statusy, !otevřené
.venv/bin/python -m bench run --sada wiki --strop 40 --dok alois_jirásek --soudce   # rychlá smyčka s auditem
.venv/bin/python -m bench run --vse --dvakrat --soudce --audit-doky 8               # plný běh → mereni/
.venv/bin/python -m bench audit --dok alois_jirásek --rucne                          # lidský vzorek (I‑12 otázka)
.venv/bin/python -m bench diff mereni/A.json mereni/B.json
.venv/bin/python -m bench gold-filter               # přegenerovat vyfiltrované automatické otázky
.venv/bin/python -m bench vazby                     # pokročilost "chápání vazeb" podle mechanismu (příkaz/věta/korekce/graf)
.venv/bin/python -m bench graf-audit --strop 60      # mechanismus `graf` na reálném korpusu, k ručnímu posouzení
.venv/bin/python -m bench probe --features edge      # lineární sonda: role z read.py ← NN embedding (bez tréninku)
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
cb6/       oracle chronos defaults lexicon read triage discourse memory ground logic recall render dialog cli
           viewbase_app · lang/ (jazyková pravidla jako data, cb6/lang/cs.json)
bench/     data gold gold_gen qa metrics run graphcheck audit judge diff vazby distill probe graf_audit __main__
           · gold/ (zlaté otázky) · config.json
tests/     hermetické (nahrané rozbory v tests/data/parses.json; nové věty: sentences.txt + python -m cb6.record)
mereni/    HYPOTEZY.md · zprávy · audit-<doc>.json (lidské odpovědi) · audit-cache.json (soudce)
```

## Znalost jako data (lexikon vazeb)

Vazby mezi predikáty (synonyma, implikace, podřazení, překryv, inverze
příbuzenství, můstková pravidla) nejsou natvrdo v kódu ani ve slovníku typu
`SYNONYMS` — jsou to řádky dat (`cb6/lexicon.py`: `{id, op, args, síla,
autorita, zdroj}`, seed `cb6/lexikon/*.jsonl`), materializované do grafu
jen když se použijí (uzel `vazba`, tvrdý krok `lex` v důkazu — audit grafu
je ověří). `!uč a = b | a => b | a ~ b | a < b | překryv a => b | inverze
a => b` je explicitní/debug kanál; věta typu „Bydlet je synonymum žít.“
totéž naučí bez příkazu. `python -m bench vazby` měří, ODKUD se poznatek
vzal (příkaz / věta / oprava v dialogu / parafráze v grafu), ne jedním
číslem. Podrobně `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md`,
stav a čísla `docs/HANDOVER.md` § 5.

## Stav

Poslední plný běh se stabilním vzorkem (8 dok., UDPipe2): unsupported
**30,1 %** [25,7–34,7], yield 76,8/89,7 na 1000 slov, QA 184/343, audit
grafu 0 porušení, determinismus ano (baseline conbond5 na dvou dokumentech:
unsupported 76,5 % → 23,0 %). Aktuální čísla, otevřené tahy a deník
rozhodnutí jsou v `docs/HANDOVER.md` (živý dokument — čti ten, ne tohle
README, pro stav "teď").
