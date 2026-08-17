"""bench — benchmark jako první třída systému (spec conbond6 § 5).

Proč samostatný balíček: jádro (`cb6`) na měření nezávisí, měření na jádru
ano. Bench odpovídá na jedinou otázku každého tahu (I‑10): *dostane systém
z reálného textu více pravdivé, doložitelné a dotazovatelné znalosti, aniž
by vzrostl počet tvrzení, která text neříká?* — a to čísly: knowledge
yield, statusy výroků, zbytek, otevřené položky, QA s dosahem, precision
audit, audit grafu, determinismus a regresní rozdíl proti minulému commitu.

Podbalíčky:
    data      – sady dokumentů a zlatých otázek (mimo repo, cesty v config.json)
    gold      – kurátorované a vyfiltrované zlaté otázky (v repu, s proveniencí)
    metrics   – výpočty metrik nad pamětí a výsledky QA
    qa        – shoda odpovědi, rozklad chyb, kotva pro dosah
    run       – běh nad dokumentem / sadou, zpráva JSON + MD
    diff      – regresní rozdíl dvou zpráv
    graphcheck, audit, judge – Task 4–5
"""
