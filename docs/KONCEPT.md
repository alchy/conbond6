# conbond6 — koncept

*Živý dokument. Říká, proč je systém postavený takhle; co přesně dělá kód, říkají
docstringy a spec (`docs/superpowers/specs/2026-08-17-conbond6-design.md`).*

## 1. Co je cíl a co cíl není

Cíl: **z běžného psaného českého textu získat znalost, která je věrná zdroji,
vysvětlitelná, dotazovatelná a bezpečná vůči domýšlení — a umět to o sobě
změřit.** Zadání J. (17. 8. 2026) je doslova v spec § 0.

Cíl není: chatbot, obecné znalosti mimo vložený text, plynulá čeština na výstupu,
ani „umět víc konstrukcí“. Šest iterací před conbond6 ukázalo, že přidávání
konstrukcí bez měřítka vede buď k systému, který nic nezapíše (conbond4:
8/238), nebo k systému, který zapíše všechno včetně toho, co text neřekl
(conbond5: 76 % vzorku nepodložených).

## 2. Jedna cesta, čtyři přechody

```
text ──čtení──▶ predikace ──triáž──▶ výroky se statusem ──zakotvení──▶ GRAF ──logika──▶ odpověď s cestou v grafu
       (UDPipe,        (co je tvrzení,       (identita, registr        (jen SAFE,        (verdikt + důkaz +
        tabulky,        co podmínka,          referentů, segmenty)      uzávěry,           zdrojová věta +
        nic se           co obsah,                                        pravidla)          výchozí volby)
        neztrácí)        co fráze)
```

Každý přechod je deterministický a jeho rozhodnutí zůstávají v grafu jako
data (výchozí volby, statusy, hrany). Nic se neschovává do „skrytého stavu“.

## 3. Pět zásad, na kterých to stojí

1. **Čtení se vždy zapíše (I‑1).** Co parser přečetl, jde do paměti; co se
   nepodařilo umístit, jde tam jako *zbytek* na téže větě + otevřená položka.
   Žádná brána zápisu. (Poučení conbond4.)
2. **Zápis není znalost (I‑2, I‑3, I‑4).** Výrok má dvě osy: `grade`
   (odkud: `read` / `said` / `derived`) a **`claim`** (co s ním logika smí):
   `SAFE` je znalost; `HYPOTHESIS` nikdy neodpovídá; `REJECTED` je viditelné
   zamítnutí s důvodem. K tomu `mood`: `assert` (tvrzení), `pattern` (vzor
   pravidla), `reported` (obsah promluvy). Do verdiktu jde jen `SAFE`+`assert`.
   (Poučení conbond5.)
3. **Nevolit význam kvůli počtu (I‑8).** Když věta nabízí víc čtení
   (zájmeno se dvěma kandidáty, disjunkce), zapíše se bezpečné jádro a zbytek
   zůstane hypotéza / otevřené. Vyšší výtěžek za cenu nepodložených výroků je
   regrese.
4. **Paměť je graf a nic než graf (I‑11, I‑12).** Registr referentů,
   alternativy, pravidla, zbytek, otevřené položky — všechno jsou uzly a hrany.
   Odpověď musí být rekonstruovatelná jen z exportu grafu; bench to ověřuje
   (`bench/graphcheck.py`) bez přístupu k Python objektům. Kontrolní otázka:
   *„Když se podívám jen na graf a jeho provenienci, chápu, proč systém této
   větě rozumí právě takto — a odliším, co text řekl, co systém odvodil, co jen
   předpokládá a co stále neví?“*
5. **Benchmark je první třída (I‑10).** Každý tah: hypotéza → změna → celý
   bench → zpráva (yield, unsupported, statusy, QA, audit grafu, determinismus,
   diff) → commit s číslem. Zelený řádek = víc pravdivé, doložitelné a
   dotazovatelné znalosti bez nárůstu halucinací. Slovní hodnocení není důvod
   ke schválení.

## 4. Kde je „stavovost“ (o kterou J. od začátku šlo)

Text není proud vět, je to hierarchie stavů: dokument › segment › věta ›
mluvčí. Každá věta je přechod: mění registr referentů (hrany `mention`),
aktivaci (kontext, po hranách s útlumem) a znalost (nové výroky, případně
odvození pravidly). Aktivace *řadí* (kdo je „on“ nejspíš), registr
*rozhoduje* (kdo vůbec připadá v úvahu — rod, číslo, segment), pravidla
*odvozují* (pevný bod). Otázka je také přechod: aktivuje kontext, ale bázi
nemění (a uzly, které si při rozřešení založí, po sobě uklidí).

## 5. Kde je jazykový model a kde není

- **Není** ve čtení ani v rozhodování o znalosti (I‑9). Čtení je UDPipe
  (neuronový parser jako externí orákulum) + tabulky jako data.
- **Je** jako *měřidlo*: soudce věrnosti extrakce (Ollama `gemma4`, prompt
  s verzí; každý verdikt kešovaný podle otisku výrok+věta) a jako *generátor
  otázek* (`bench gold-gen`), přičemž otázka je kurátorovaná až po lidském
  ověření.
- Neuronová složka trénovaná na našem korpusu v v1 není (conbond0/1 se na
  etalonech této velikosti přeučily); přehodnocení je datově podmíněné —
  až audit nashromáždí ≥ 2 000 označených výroků, zkusí se *naučená triáž*,
  která smí status jen snižovat.

## 6. Co bench měří a proč zrovna to

| číslo | proč |
|---|---|
| **unsupported rate** (soudce + člověk, Wilsonův interval) | jediné číslo, které chrání před conbond5 pastí „zapsáno = pochopeno“ |
| **knowledge yield** hl./vše na 1 000 slov | aby úbytek za precision byl vidět a byl vědomý |
| statusy SAFE / HYPOTHESIS / REJECTED, `pattern`, `reported` | kolik z textu je znalost, kolik nejistota, kolik přiznané „neumím“ |
| **audit grafu** (provenience, derivace, statusy v důkazu, osiřelost, rekonstrukce odpovědi z exportu) | I‑11/I‑12 — chytil 33 porušení hned v prvním plném běhu |
| QA správně / otázek, **kurátorované zvlášť**, dosah po pásmech | dotazovatelnost; dosah je metr diskurzové vrstvy |
| determinismus, diff proti minulé zprávě | reprodukovatelnost a poctivé srovnání tahů |

Zlaté otázky mají provenienci a musí mít hlavu a patu (požadavek J.):
kurátorované z conBond2 beze změny, automatické po valenčním filtru a
vykazované zvlášť, LM‑generované až po ověření člověkem.

## 7. Přiznané meze v1

Koreference jen registr + aktivace (mluvčí přímé řeči a určité popisy ne);
čas jen body/roky/intervaly; bez prostoru modelů (disjunkce je zamítnutá,
ne řešená); modalita jako příznak; šablonová čeština na výstupu; `read.py`
z conbond5 beze změny konstrukcí (opravovaly se jen věci, které lhaly:
životopisná závorka, přivlastnění, scelování jmen, výčty). Každá mez se
v odpovědi hlásí, nikdy tiše.
