# conbond6 — zadání pro nové sezení v tomto adresáři

Čteš to jako Claude Code při startu v `~/Projects/conbond6`. Tohle je celé
zadání; podrobnosti jsou v odkazovaných souborech, ne tady.

## Co to je a jaký je cíl

Šestý pokus J. o systém, který **z běžného psaného českého textu získá znalost
věrnou zdroji, vysvětlitelnou, dotazovatelnou a bezpečnou vůči domýšlení — a umí
to o sobě změřit.** Není to „další verze motoru“; úkol je *prokázat porozumění*
čísly. Paměť je graf a nic než graf. Zadání J. doslova: spec § 0
(`docs/superpowers/specs/2026-08-17-conbond6-design.md`), invarianty I‑1…I‑12 tamtéž.

## Pravidla spolupráce (od J., platí bez výjimky)

1. **J. dává cíle, cestu rozhoduješ ty a rozhodčí je bench.** Neptej se na
   schválení dílčích návrhů, nenabízej „chceš, abych…“, nedeklaruj schopnosti —
   udělej, změř, ukaž číslo. Všechny cesty otevřené (i NN trénovaná na korpusu),
   rozhoduje měření.
2. **Každý tah = hypotéza před, plný bench po, číslo v commitu.** Zelený řádek:
   víc pravdivé (unsupported neroste), doložitelné (důkaz v grafu), dotazovatelné
   (QA). Recall ↑ + precision ↓ = regrese. Nikdy nevolit význam kvůli počtu.
3. **Nic mimo graf** (I‑11/I‑12): každá odpověď musí být rekonstruovatelná jen z
   exportu grafu; `bench/graphcheck.py` to hlídá a musí být 0 porušení.
4. **LM není zdroj znalosti** (I‑9) — jen soudce auditu a generátor otázek.
5. **Testovací a učební věty i otázky musí mít hlavu a patu** — žádné auto‑otázky
   typu „Kdy vytvořil Josef Čapek?“; LM‑generované otázky až po lidském ověření.
6. **conbond5** (`~/Projects/conbond5`) běží v jiném sezení; smí inspirovat,
   **nesahat do něj**. Vše nové jde do conbond6.
7. **Commit + push po každém tahu** na https://github.com/alchy/conbond6
   (`main` = `v1`, `git push origin v1 && git push origin v1:main`). Dovoleno bez ptaní.
8. **Docs jsou živé:** po tahu doplnit `docs/HANDOVER.md` (§ 4 čísla, § 5 hotovo,
   § 6 tahy, § 7 deník) a `mereni/HYPOTEZY.md`. Česky, bohaté docstringy
   (proč/co, vstup, výstup) pod každou funkcí.

## Kde co je (čti v tomto pořadí)

1. `docs/HANDOVER.md` — stav, čísla, otevřené tahy, deník rozhodnutí, checklist.
2. `docs/KONCEPT.md` — proč je to postavené takhle (5 zásad, kde je stavovost);
   `docs/UVOD.md` — orientace v kódu (pojmy, cesta věty grafem, příkazy);
   `docs/UKAZKY.md` — ukázky ze živého běhu (`python -m bench ukazky` po tahu, který mění odpovědi).
3. `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md` — návrh
   znalostních vazeb jako data (krok 1 hotový, kroky 2–5 čekají).
4. Poslední záznam v `mereni/HYPOTEZY.md` a poslední zpráva `mereni/<datum>-<commit>.md`.
5. Kód: `cb6/` (oracle chronos defaults lexicon read triage discourse memory ground
   logic recall render dialog cli viewbase_app; seed `cb6/lexikon/*.jsonl`), `bench/`, `tests/` (hermetické,
   rozbory v `tests/data/parses.json`; nové věty → `sentences.txt` + `python -m cb6.record`).

## Prostředí (ověř na začátku)

- `.venv` (Python 3.11): `.venv/bin/python -m pytest -q` musí být zelené (167 + 2 xfail).
- UDPipe služba z conBond3 na `127.0.0.1:42200` (bench, nové rozbory).
- Ollama `gemma4:latest` na `127.0.0.1:11434` (soudce auditu, `gold-gen`).
- Živý graf: `.venv/bin/python -m cb6.viewbase_app --pamet data/pamet-graf.json --port 8081`
  (viewBase2 je zase 3.11‑kompatibilní, `.venv314` netřeba; uživatel `workbench`
  z `VIEWBASE_USER`, tajemství jen v `~/.viewbase/`; ukončit `kill -INT`).
- Rychlá smyčka: `python -m bench run --sada wiki --strop 40 --dok alois_jirásek karel_čapek --soudce`;
  plný běh: `python -m bench run --vse --dvakrat --soudce --audit-doky 8`.

## Kde to stojí (17. 8. 2026, večer) a co je další tah

- Stabilní baseline `3cd63e4` (zpráva `mereni/2026-08-18-3cd63e4.md`): unsupported
  **30,1 %** [25,7–34,7] na 400 výrocích (8 dok.), yield 77/90, QA **184/343**
  (stará sada 179/334, gen výpis 5/9 neověřené; kurátorované 29/130, etalon 14/32),
  audit grafu 0, determinismus ano. Podrobně HANDOVER § 4.
- **Hotový krok 1 znalostních vazeb:** `cb6/lexicon.py` (operátory `třída`,
  `implikace`; řádky `{id, op, args, síla, autorita, zdroj}`), seed
  `cb6/lexikon/synonyma.jsonl` (88 ř.: same 32 · implies 32 · related 24), líná
  materializace použitých řádků do grafu (uzly `vazba`, `uses_rule`, tvrdý krok
  `lex` v graphchecku), `!uč a = b | a => b | a ~ b`; `defaults.SYNONYMS` a
  `Memory.learned["synonyms"]` zanikly. Přitvrzení síly dalo +3 QA (napsat ≠
  publikovat, chodit ≠ studovat), 0 ztrát, unsupported beze změny.
- **Hotový tah „výpis“ (večer, nález J. z dema):** „Která díla napsal…?“ = díra
  s omezením skupinou, „Vyjmenuj všechna díla Karla Čapka.“ = otázka druhu `list`
  (nezapisuje se), operátor `podřazení` v lexikonu (`!uč drama < dílo`, seed
  `podrazeni.jsonl`), nominativ jmenovací („drama R.U.R.“ → R.U.R. ∈ drama),
  téma dokumentu v grafu. Nové výpisové otázky `bench/gold/gen-*.json` (9) čekají
  na ověření J. (`bench gold-gen --overit --dok …`). Čísla: HANDOVER § 4 / HYPOTEZY.
- **Další tah = krok 2 návrhu:** operátory `překryv` + `porovnání` a veličiny
  (hodnota, jednotka → dimenze; `!uč překryv …`, `!uč porovnání …`; otázky
  „Jaká je délka …?“, „Je A delší než B?“, „Mohli se potkat?“ s modalitou
  *možnost* v řádku). Hypotéza do HYPOTEZY: etalon 14/32 → ≥ 18/32, unsupported
  hlavních beze změny, graphcheck 0. Pak krok 3 (příbuzenství: `inverze` +
  `skládání` + nález G‑3), krok 5 (`Memory.rules` → řádky `implikace` s mapou rolí).
- Vstupy, které čekají na J. (měření, ne návrh): lidský audit
  `python -m bench audit --dok alois_jirásek --rucne` (≥ 30 výroků) a ověření
  otázek `python -m bench gold-gen --dok karel_čapek --n 12` → `--overit`.

## Checklist startu

1. `git status`, `git log --oneline -5`; přečíst HANDOVER § 4–7 a poslední HYPOTEZY.
2. Ověřit služby a `pytest -q`.
3. Rychlá smyčka na dvou dokumentech, porovnat s čísly v HANDOVER § 4.
4. Zapsat hypotézu tahu, dělat, měřit, commit s číslem, push, doplnit docs.
