# conbond6 — ukázky (generováno z živého běhu)

*Vygenerováno `python -m bench ukazky` — vstupy jdou do čerstvé paměti přes UDPipe, výstupy jsou skutečné odpovědi systému v okamžiku generování. Vysvětlení u scén jsou ručně psané; když se výstup změní tahem, přegeneruj (docs jsou živé). Základní principy a pojmy: `docs/UVOD.md`.*

Čtení výstupu: `✓ zapsáno [s0001] …` = výrok v grafu (id, predikát, role); `[…]` = přiznané výchozí volby; `čtu: …` = jak systém přečetl otázku; `→` = výplň/odpověď; `↳` = krok důkazu; `zdroj:` = věta a dokument; `[přečteno z textu | řečeno | odvozeno z: …]` = stupeň důkazu.

## 1. Věta se zapíše, otázka se zodpoví — s důkazem a zdrojem

*Co ukazuje:* Základní smyčka: text → UDPipe → čtení (predikát + role) → zápis do grafu jako *výrok* s proveniencí (dokument, věta). Otázka je výrok s dírou; odpověď je shoda s výroky paměti a **vždy nese důkaz**: který výrok, jaké kroky, jaké výchozí volby, jaký stupeň (přečteno / řečeno / odvozeno). „Celý život pracoval…“ nemá podmět — doplní se z registru referentů (koreference) a odpověď to přizná.

```
» [dokument „alois_jirásek“]
» Alois Jirásek se narodil ve východočeském Hronově u Náchoda.
» Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.
věta: Alois Jirásek se narodil ve východočeském Hronově u Náchoda.
  čtu: narodit_se(kdo:·Alois Jirásek, kde:·Hronov[východočeský])
  ✓ [s0001] narodit_se(kdo:·Alois Jirásek, kde:·Hronov)
  ✓ [s0002] nmod:u+Gen(kdo:·Hronov, co:·Náchod)
věta: Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.
  čtu: pracovat(kdo:·∅, jak_dlouho:·život[celý], jako:∃učitel, kde:∃gymnázium+·Litomyšl+·Praha, pořadí:·nejprve+·poté)
  ✓ [s0003] pracovat(kdo:·Alois Jirásek, jak_dlouho:·život, jako:∃učitel, kde:∃gymnázium+∃Litomyšl+∃Praha, pořadí:·nejprve+·poté)
  ✓ [s0004] nmod:Gen(kdo:·učitel, co:∃dějepis) [REJECTED]
  [kdo:pro-drop z kontextu; kdo: „nevyslovený podmět“ = Alois Jirásek (koref: registr, téma dokumentu)]
```
```
» Kde se narodil Alois Jirásek?
čtu: narodit_se(kde:?, kdo:·Alois Jirásek)
→ Hronov
   - narodit_se(kdo: Alois Jirásek, kde: Hronov)  [s0001]
       zdroj: „Alois Jirásek se narodil ve východočeském Hronově u Náchoda.“ (alois_jirásek, věta 1)
   [přečteno z textu]
```
```
» Kde pracoval Alois Jirásek?
čtu: pracovat(kde:?, kdo:·Alois Jirásek)
→ gymnázium; Litomyšl; Praha
   - pracovat(kdo: Alois Jirásek, jak dlouho: život, jako: ∃učitel, kde: ∃gymnázium + ∃Litomyšl + ∃Praha, pořadí: nejprve + poté)  [s0003]
       zdroj: „Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.“ (alois_jirásek, věta 2)
   [přečteno z textu; kdo:pro-drop z kontextu; kdo: „nevyslovený podmět“ = Alois Jirásek (koref: registr, téma dokumentu)]
```
```
» Jako co pracoval?
čtu: pracovat(kdo:·∅, jako:?)
→ učitel
   - pracovat(kdo: Alois Jirásek, jak dlouho: život, jako: ∃učitel, kde: ∃gymnázium + ∃Litomyšl + ∃Praha, pořadí: nejprve + poté)  [s0003]
       zdroj: „Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze.“ (alois_jirásek, věta 2)
   [přečteno z textu; kdo:pro-drop z kontextu; kdo: „nevyslovený podmět“ = Alois Jirásek (koref: registr, téma dokumentu)]
```

*Všimni si:* Všimni si hranatých závorek: `[přečteno z textu; kdo: „nevyslovený podmět“ = … (koref …)]` — každá výchozí volba je přiznaná (I‑8), nic se nedomýšlí potichu.

## 2. NEVÍM není lež — otázka nesmí dostat víc, než paměť má

*Co ukazuje:* Chyba conbond4 byla „Bydlí Petr v Brně? → ANO“ (shoda jen na predikátu). Tady musí **každá role otázky** mít protějšek ve výroku; výrok smí mít role navíc, otázka ne. Rok 2020 v otázce nemá ve výroku protějšek → NEVÍM s tím, co paměť ví (propad = recall nad týmž grafem).

```
» Petr bydlí v Praze.
✓ zapsáno [s0001] bydlet(kdo: Petr, kde: Praha)
```
```
» Bydlí Petr v Brně?
čtu: bydlet(kdo:·Petr, kde:·Brno)
→ NEVÍM
   chybí: o Brno nevím nic
   vím:
   - bydlet(kdo: Petr, kde: Praha)  — zdroj: „Petr bydlí v Praze.“ (dialog, věta 1)
```
```
» Bydlí Petr v Praze v roce 2020?
čtu: bydlet(kdo:·Petr, kde:·Praha, kdy:·2020)
→ NEVÍM
   vím:
   - bydlet(kdo: Petr, kde: Praha)  — zdroj: „Petr bydlí v Praze.“ (dialog, věta 1)
```
```
» Kde žije Petr?
čtu: žít(kde:?, kdo:·Petr)
→ Praha
   - bydlet(kdo: Petr, kde: Praha)  [s0001]
       zdroj: „Petr bydlí v Praze.“ (dialog, věta 1)
   ↳ implikace: bydlet ⇒ žít [lex:syn:0031]
   [odvozeno z: řekls to]
```

*Všimni si:* „Kde žije Petr?“ odpoví přes **lexikon**: řádek `bydlet ⇒ žít` (implikace, ne synonymum — kdo někde bydlí, tam žije, ne naopak); důkaz ukáže `[lex:syn:0031]` a stupeň klesne na *odvozeno*.

## 3. Třídy, kvantifikátory a sylogismus; NE jen z disjunktnosti

*Co ukazuje:* „Každý spisovatel je člověk“ = podmnožina (∀), „Hrabal je spisovatel“ = členství. Otázka „Je Hrabal stroj?“ dostane **NE** jen proto, že text říká „Žádný stroj není člověk“ (disjunktnost tříd) — jinak by bylo NEVÍM. „Napsal Postřižiny i nějaký stroj?“ je poctivé NEVÍM: nikdo to neřekl.

```
» Každý spisovatel je člověk.
✓ zapsáno [s0001] být(kdo: ∀spisovatel, co: ∃člověk) ⟨subset⟩
   [kernel:subset (obecný podmět)]
```
```
» Žádný stroj není člověk.
✓ zapsáno [s0002] ne-být(kdo: ∀stroj, co: ∃člověk) ⟨subset⟩
   [kernel:subset (obecný podmět)]
```
```
» Hrabal je spisovatel.
✓ zapsáno [s0003] být(kdo: Hrabal, co: ∃spisovatel) ⟨member⟩
   [kernel:member (určitý podmět)]
```
```
» Hrabal napsal Postřižiny.
✓ zapsáno [s0004] být(kdo: postřižina, co: ∃postřižina) ⟨member⟩
   [instance: členství z neurčité zmínky]
✓ zapsáno [s0005] napsat(kdo: Hrabal, co: ∃postřižina)
   [co: nová instance e0002 ∈ postřižina (neurčitá zmínka)]
```
```
» Je Hrabal stroj?
čtu: být(kdo:·Hrabal, co:∃stroj) ⟨member⟩
→ NE
   protože:
   - být(kdo: Hrabal, co: ∃spisovatel) ⟨member⟩  [s0003]
       zdroj: „Hrabal je spisovatel.“ (dialog, věta 3)
   - ne-být(kdo: ∀stroj, co: ∃člověk) ⟨subset⟩  [s0002]
       zdroj: „Žádný stroj není člověk.“ (dialog, věta 2)
   ↳ Hrabal ∈ spisovatel
   ↳ spisovatel ∦ stroj
   [odvozeno z: řekls to]
```
```
» Napsal Postřižiny spisovatel?
čtu: napsat(co:∃postřižina, kdo:·spisovatel)
→ ANO
   protože:
   - napsat(kdo: Hrabal, co: ∃postřižina)  [s0005]
       zdroj: „Hrabal napsal Postřižiny.“ (dialog, věta 4)
   - být(kdo: postřižina, co: ∃postřižina) ⟨member⟩  [s0004]
       zdroj: „Hrabal napsal Postřižiny.“ (dialog, věta 4)
   - být(kdo: Hrabal, co: ∃spisovatel) ⟨member⟩  [s0003]
       zdroj: „Hrabal je spisovatel.“ (dialog, věta 3)
   ↳ postřižina ∈ postřižina
   ↳ Hrabal ∈ spisovatel
   [odvozeno z: řekls to; co: nová instance e0002 ∈ postřižina (neurčitá zmínka)]
```
```
» Napsal Postřižiny i nějaký stroj?
čtu: napsat(co:∃postřižina, kdo:∃stroj)
→ NEVÍM
   vím:
   - napsat(kdo: Hrabal, co: ∃postřižina)  — zdroj: „Hrabal napsal Postřižiny.“ (dialog, věta 4)
   - ne-být(kdo: ∀stroj, co: ∃člověk) ⟨subset⟩  — zdroj: „Žádný stroj není člověk.“ (dialog, věta 2)
   - být(kdo: postřižina, co: ∃postřižina) ⟨member⟩  — zdroj: „Hrabal napsal Postřižiny.“ (dialog, věta 4)
```
```
» Kdo je Hrabal?
čtu: být(kdo:·Hrabal, co:?)
→ spisovatel
   - být(kdo: Hrabal, co: ∃spisovatel) ⟨member⟩  [s0003]
       zdroj: „Hrabal je spisovatel.“ (dialog, věta 3)
   [řekls to; kernel:member (určitý podmět)]
```

*Všimni si:* Symbol `∦` v důkazu = disjunktní třídy; `∈`/`⊆` jsou tvrdé cesty v grafu, které audit (`bench/graphcheck.py`) ověřuje jen z exportu — bez přístupu k Pythonu.

## 4. Co z textu neplyne — ∃ není ∀

*Co ukazuje:* „Ovoce obsahuje vitamíny“ říká, že nějaké vitamíny — ne vitamín C. Systém rozlišuje „nějaký vitamín“ (∃, ANO přes ovoce ⊇ citron) a konkrétní vitamín C (NEVÍM, dokud to text neřekne).

```
» Citron je ovoce.
✓ zapsáno [s0001] být(kdo: ∀citron, co: ∃ovoce) ⟨subset⟩
   [kdo:∀ generický prézens; kernel:subset (obecný podmět)]
```
```
» Ovoce obsahuje vitamíny.
✓ zapsáno [s0002] obsahovat(kdo: ∀ovoce, co: ∃vitamín)
   [kdo:∀ generický prézens]
```
```
» Vitamín C je vitamín.
✓ zapsáno [s0003] být(kdo: ∀vitamín C, co: ∃vitamín) ⟨subset⟩
   [kdo:∀ generický prézens; kernel:subset (obecný podmět)]
```
```
» Obsahuje citron vitamín C?
čtu: obsahovat(kdo:∀citron, co:∃vitamín C)
→ NEVÍM
   vím:
   - obsahovat(kdo: ∀ovoce, co: ∃vitamín)  — zdroj: „Ovoce obsahuje vitamíny.“ (dialog, věta 2)
   - být(kdo: ∀vitamín C, co: ∃vitamín) ⟨subset⟩  — zdroj: „Vitamín C je vitamín.“ (dialog, věta 3)
   - být(kdo: ∀citron, co: ∃ovoce) ⟨subset⟩  — zdroj: „Citron je ovoce.“ (dialog, věta 1)
```
```
» Obsahuje citron nějaký vitamín?
čtu: obsahovat(kdo:∀citron, co:∃vitamín)
→ ANO
   protože:
   - obsahovat(kdo: ∀ovoce, co: ∃vitamín)  [s0002]
       zdroj: „Ovoce obsahuje vitamíny.“ (dialog, věta 2)
   - být(kdo: ∀citron, co: ∃ovoce) ⟨subset⟩  [s0001]
       zdroj: „Citron je ovoce.“ (dialog, věta 1)
   ↳ citron ⊆ ovoce (∀ se přenáší dolů)
   [odvozeno z: řekls to; kdo:∀ generický prézens]
```
```
» Citron obsahuje vitamín C.
✓ zapsáno [s0004] obsahovat(kdo: ∀citron, co: ∃vitamín C)
   [kdo:∀ generický prézens]
```
```
» Obsahuje citron vitamín C?
čtu: obsahovat(kdo:∀citron, co:∃vitamín C)
→ ANO
   protože:
   - obsahovat(kdo: ∀citron, co: ∃vitamín C)  [s0004]
       zdroj: „Citron obsahuje vitamín C.“ (dialog, věta 4)
   [řekls to; kdo:∀ generický prézens]
```

## 5. Konflikt se hlásí, výjimka se učí — bez default logic

*Co ukazuje:* „Ptáci létají“ je obecná věta (∀ z generického prézentu) → „Létá tučňák?“ ANO přes ∀. Když přijde „Tučňák nelétá“, systém **před zápisem** zjistí konflikt a řekne to. Výjimku doučí člověk (`!výjimka létat pták tučňák`): obecný výrok pak pro tučňáka neplatí, pro vrabce ano.

```
» Ptáci létají.
✓ zapsáno [s0001] létat(kdo: ∀pták)
   [kdo:∀ generický prézens]
```
```
» Tučňák je pták.
✓ zapsáno [s0002] být(kdo: ∀tučňák, co: ∃pták) ⟨subset⟩
   [kdo:∀ generický prézens; kernel:subset (obecný podmět)]
```
```
» Létá tučňák?
čtu: létat(kdo:∀tučňák)
→ ANO
   protože:
   - létat(kdo: ∀pták)  [s0001]
       zdroj: „Ptáci létají.“ (dialog, věta 1)
   - být(kdo: ∀tučňák, co: ∃pták) ⟨subset⟩  [s0002]
       zdroj: „Tučňák je pták.“ (dialog, věta 2)
   ↳ tučňák ⊆ pták (∀ se přenáší dolů)
   [odvozeno z: řekls to; kdo:∀ generický prézens]
```
```
» Tučňák nelétá.
✓ zapsáno [s0003] ne-létat(kdo: ∀tučňák)
   [kdo:∀ generický prézens]
⚠ to si odporuje s tím, co už vím:
   - létat(kdo: ∀pták)  — zdroj: „Ptáci létají.“ (dialog, věta 1)  [s0001]
   - být(kdo: ∀tučňák, co: ∃pták) ⟨subset⟩  — zdroj: „Tučňák je pták.“ (dialog, věta 2)  [s0002]
   ↳ tučňák ⊆ pták (∀ se přenáší dolů)
   (nechávám obojí; otázky na to budou hlásit KONFLIKT — oprav `!zapomeň s…`, nebo zúž `!výjimka <predikát> <skupina> <výjimka>`)
```
```
» !výjimka létat pták tučňák
výjimka: létat o pták neplatí pro tučňák
```
```
» Vrabec je pták.
✓ zapsáno [s0004] být(kdo: ∀vrabec, co: ∃pták) ⟨subset⟩
   [kdo:∀ generický prézens; kernel:subset (obecný podmět)]
```
```
» Létá vrabec?
čtu: létat(kdo:∀vrabec)
→ ANO
   protože:
   - létat(kdo: ∀pták)  [s0001]
       zdroj: „Ptáci létají.“ (dialog, věta 1)
   - být(kdo: ∀vrabec, co: ∃pták) ⟨subset⟩  [s0004]
       zdroj: „Vrabec je pták.“ (dialog, věta 4)
   ↳ vrabec ⊆ pták (∀ se přenáší dolů)
   [odvozeno z: řekls to; kdo:∀ generický prézens]
```
```
» Létá tučňák?
čtu: létat(kdo:∀tučňák)
→ NE
   protože:
   - ne-létat(kdo: ∀tučňák)  [s0003]
       zdroj: „Tučňák nelétá.“ (dialog, věta 3)
   [řekls to; kdo:∀ generický prézens]
```

## 6. Prostor a čas; můstkové pravidlo z konzole

*Co ukazuje:* Místa mají uzávěr `within` (Praha ⊆ Česko), časy obsažení intervalů. „Byl Petr v pondělí v Česku?“ je nejdřív NEVÍM — text říká *jel do*, ne *byl v*. Pravidlo `!pravidlo jet(kam:X) => být(kde:X)` je řádek dat (ne kód): otázka na `být` se zkusí jako `jet` s přemapovanou rolí, důkaz to přizná a stupeň je *odvozeno*. Ve středu nikam nejel → NEVÍM.

```
» Petr jel v pondělí do Prahy.
✓ zapsáno [s0001] jet(kdo: Petr, kdy: pondělí, kam: Praha)
```
```
» V úterý jel Petr do Brna.
✓ zapsáno [s0002] jet(kdy: úterý, kdo: Petr, kam: Brno)
```
```
» Praha je v Česku.
✓ zapsáno [s0003] být(kdo: Praha, kde: Česko) ⟨within⟩
   [kernel:within (místo v místě)]
```
```
» Byl Petr v pondělí v Česku?
čtu: být(kdo:·Petr, kde:·Česko, kdy:·pondělí)
→ NEVÍM
   vím:
   - být(kdo: Praha, kde: Česko) ⟨within⟩  — zdroj: „Praha je v Česku.“ (dialog, věta 3)
   - jet(kdo: Petr, kdy: pondělí, kam: Praha)  — zdroj: „Petr jel v pondělí do Prahy.“ (dialog, věta 1)
   - jet(kdy: úterý, kdo: Petr, kam: Brno)  — zdroj: „V úterý jel Petr do Brna.“ (dialog, věta 2)
```
```
» !pravidlo jet(kam:X) => být(kde:X)
pravidlo r0001: jet(kam) ⇒ být(kde)
```
```
» Byl Petr v pondělí v Česku?
čtu: být(kdo:·Petr, kde:·Česko, kdy:·pondělí)
→ ANO
   protože:
   - jet(kdo: Petr, kdy: pondělí, kam: Praha)  [s0001]
       zdroj: „Petr jel v pondělí do Prahy.“ (dialog, věta 1)
   - být(kdo: Praha, kde: Česko) ⟨within⟩  [s0003]
       zdroj: „Praha je v Česku.“ (dialog, věta 3)
   ↳ Praha ⊆ Česko (místo)
   ↳ pravidlo r0001: jet→být
   [odvozeno z: řekls to]
```
```
» Kam jel Petr v pondělí?
čtu: jet(kam:?, kdo:·Petr, kdy:·pondělí)
→ Praha
   - jet(kdo: Petr, kdy: pondělí, kam: Praha)  [s0001]
       zdroj: „Petr jel v pondělí do Prahy.“ (dialog, věta 1)
   [řekls to]
```
```
» Kdy jel Petr do Prahy?
čtu: jet(kdy:?, kdo:·Petr, kam:·Praha)
→ pondělí
   - jet(kdo: Petr, kdy: pondělí, kam: Praha)  [s0001]
       zdroj: „Petr jel v pondělí do Prahy.“ (dialog, věta 1)
   [řekls to]
```
```
» Byl Petr ve středu v Česku?
čtu: být(kdo:·Petr, kde:·Česko, kdy:·středa)
→ NEVÍM
   vím:
   - být(kdo: Praha, kde: Česko) ⟨within⟩  — zdroj: „Praha je v Česku.“ (dialog, věta 3)
   - jet(kdo: Petr, kdy: pondělí, kam: Praha)  — zdroj: „Petr jel v pondělí do Prahy.“ (dialog, věta 1)
   - jet(kdy: úterý, kdo: Petr, kam: Brno)  — zdroj: „V úterý jel Petr do Brna.“ (dialog, věta 2)
```

## 7. Pravidla z textu („pokud“) a pevný bod odvození

*Co ukazuje:* Podmínková věta není tvrzení o světě (I‑8): „Karel přijde, pokud přijde Jana“ zapíše **pravidlo** (vzory `mood=pattern`), ne fakt. Jakmile paměť dostane „Petr přijde“, `derive()` odvodí řetěz Jana → Karel; odvozené výroky mají `derived_from` + `uses_rule` (v grafu vidět).

```
» [dokument „h“]
» Karel přijde na oslavu, pokud přijde Jana.
» Jana přijde, pokud přijde Petr.
věta: Karel přijde na oslavu, pokud přijde Jana.
  čtu: přijít(kdo:·Karel, na+Acc:∃oslava, advcl:pokud:[přijít(kdo:·Jana)])
  ✓ [s0001] ∅(pokud:[s0002], pak:[s0003])
  ✓ [s0002] přijít(kdo:·Jana)
  ✓ [s0003] přijít(kdo:·Karel, na+Acc:∃oslava)
  [pravidlo z podmínky „pokud“ (if)]
věta: Jana přijde, pokud přijde Petr.
  čtu: přijít(kdo:·Jana, advcl:pokud:[přijít(kdo:·Petr)])
  ✓ [s0004] ∅(pokud:[s0005], pak:[s0006])
  ✓ [s0005] přijít(kdo:·Petr)
  ✓ [s0006] přijít(kdo:·Jana)
  [pravidlo z podmínky „pokud“ (if)]
```
```
» Přijde Karel?
čtu: přijít(kdo:·Karel)
→ NEVÍM
   chybí: o „přijít“ nemám žádný výrok
```
```
» Petr přijde.
✓ zapsáno [s0007] přijít(kdo: Petr)
   ⇒ odvozeno [s0008] přijít(kdo: Jana)
   ⇒ odvozeno [s0009] přijít(kdo: Karel, na+Acc: ∃oslava)
```
```
» Přijde Karel?
čtu: přijít(kdo:·Karel)
→ ANO
   protože:
   - přijít(kdo: Karel, na+Acc: ∃oslava)  [s0009]
       zdroj: „Karel přijde na oslavu, pokud přijde Jana.“ (h, věta 1)
   [odvozeno z: odvozeno; pravidlo z podmínky „pokud“ (if); odvozeno pravidlem s0001 z s0008]
```
```
» !statusy
SAFE 9 (z toho znalost 5) · HYPOTHESIS 0 · REJECTED 0 · nálady: assert 5, pattern 4 · otevřené 1
```

## 8. Instance, popis a vlastnost

*Co ukazuje:* „Filip má auto“ založí anonymní instanci (a1 ∈ auto — typovací výrok, slouží uzávěrům, není to „znalost z textu“). „Filipovo auto je modré“ přivlastnění rozřeší na tutéž instanci. „Co má Filip?“ popíše instanci i s vlastností.

```
» Filip má auto.
✓ zapsáno [s0001] být(kdo: auto, co: ∃auto) ⟨member⟩
   [instance: členství z neurčité zmínky]
✓ zapsáno [s0002] mít(kdo: Filip, co: ∃auto)
   [co: nová instance e0002 ∈ auto (neurčitá zmínka)]
```
```
» Filipovo auto je modré.
✓ zapsáno [s0003] být(kdo: auto (modrý), jaký: ∃modrý)
   [kdo: „Filipův auto“ → vlastník Filip]
```
```
» Co má Filip?
čtu: mít(co:?, kdo:·Filip)
→ auto (modrý)
   - mít(kdo: Filip, co: ∃auto (modrý))  [s0002]
       zdroj: „Filip má auto.“ (dialog, věta 1)
   [řekls to; co: nová instance e0002 ∈ auto (neurčitá zmínka)]
```
```
» Jaké je Filipovo auto?
čtu: být(kdo:·auto⟨Filipův⟩, jaký:?)
→ modrý
   - být(kdo: auto (modrý), jaký: ∃modrý)  [s0003]
       zdroj: „Filipovo auto je modré.“ (dialog, věta 2)
   [řekls to; kdo: „Filipův auto“ → vlastník Filip]
```

## 9. Lexikon vazeb: znalost jako řádky dat, ne kód

*Co ukazuje:* Čtyři místa, kde dřív žily „vazby“ (tabulka synonym v kódu, naučené dvojice, můstky, pravidla z textu), se sjednocují do **řádků** `{op, args, síla, autorita, zdroj}`. Operátory dnes: `třída` (~), `implikace` (⇒), `podřazení` (⊆). Síla `same/implies/related`; `related` nikdy neodpovídá, jen napovídá. Řádek se použije → v grafu vznikne uzel `vazba` s proveniencí až na soubor a řádek (líná materializace). Z konzole: `!uč a = b | a => b | a ~ b | a < b`.

```
» Karel Čapek napsal drama R.U.R.
✓ zapsáno [s0001] být(kdo: R.U.R., co: ∃drama) ⟨member⟩
   [třída z nominativu jmenovacího: R.U.R. ∈ drama]
✓ zapsáno [s0002] napsat(kdo: Karel Čapek, co: R.U.R.)
```
```
» Karel Čapek napsal román Krakatit.
✓ zapsáno [s0003] být(kdo: Krakatit, co: ∃román) ⟨member⟩
   [třída z nominativu jmenovacího: Krakatit ∈ román]
✓ zapsáno [s0004] napsat(kdo: Karel Čapek, co: Krakatit)
```
```
» Která díla napsal Karel Čapek?
čtu: napsat(co:?filler:∃dílo, kdo:·Karel Čapek)
→ R.U.R.
   - napsat(kdo: Karel Čapek, co: R.U.R.)  [s0002]
       zdroj: „Karel Čapek napsal drama R.U.R.“ (dialog, věta 1)
   - být(kdo: R.U.R., co: ∃drama) ⟨member⟩  [s0001]
       zdroj: „Karel Čapek napsal drama R.U.R.“ (dialog, věta 1)
   ↳ R.U.R. ∈ drama
   ↳ podřazení: drama ⊆ dílo [lex:pod:0002]
   [odvozeno z: řekls to]
→ Krakatit
   - napsat(kdo: Karel Čapek, co: Krakatit)  [s0004]
       zdroj: „Karel Čapek napsal román Krakatit.“ (dialog, věta 2)
   - být(kdo: Krakatit, co: ∃román) ⟨member⟩  [s0003]
       zdroj: „Karel Čapek napsal román Krakatit.“ (dialog, věta 2)
   ↳ Krakatit ∈ román
   ↳ podřazení: román ⊆ dílo [lex:pod:0001]
   [odvozeno z: řekls to]
```
```
» Vyjmenuj všechna dramata.
čtu: ∅(co:?filler:∀drama)
→ R.U.R.
   - být(kdo: R.U.R., co: ∃drama) ⟨member⟩  [s0001]
       zdroj: „Karel Čapek napsal drama R.U.R.“ (dialog, věta 1)
   ↳ R.U.R. ∈ drama
   [odvozeno z: řekls to]
```
```
» !uč veselohra < komedie
naučeno lex:said:0001: veselohra ⊆ komedie (podřazení, implies)
```
```
» Karel Čapek napsal veselohru Loupežník.
✓ zapsáno [s0005] být(kdo: Loupežník, co: ∃veselohra) ⟨member⟩
   [třída z nominativu jmenovacího: Loupežník ∈ veselohra]
✓ zapsáno [s0006] napsat(kdo: Karel Čapek, co: Loupežník)
```
```
» Vypiš dramata Karla Čapka.
čtu: ∅(co:?filler:drama, čí:·Karel Čapek)
→ R.U.R.
   - být(kdo: R.U.R., co: ∃drama) ⟨member⟩  [s0001]
       zdroj: „Karel Čapek napsal drama R.U.R.“ (dialog, věta 1)
   - napsat(kdo: Karel Čapek, co: R.U.R.)  [s0002]
       zdroj: „Karel Čapek napsal drama R.U.R.“ (dialog, věta 1)
   ↳ R.U.R. ∈ drama
   ↳ napsat(kdo: Karel Čapek, co: R.U.R.)
   [odvozeno z: řekls to]
→ Loupežník
   - být(kdo: Loupežník, co: ∃veselohra) ⟨member⟩  [s0005]
       zdroj: „Karel Čapek napsal veselohru Loupežník.“ (dialog, věta 3)
   - napsat(kdo: Karel Čapek, co: Loupežník)  [s0006]
       zdroj: „Karel Čapek napsal veselohru Loupežník.“ (dialog, věta 3)
   ↳ Loupežník ∈ veselohra
   ↳ podřazení: veselohra ⊆ drama [lex:said:0001, lex:pod:0013]
   ↳ napsat(kdo: Karel Čapek, co: Loupežník)
   [odvozeno z: řekls to]
```
```
» Kdo napsal Krakatit?
čtu: napsat(kdo:?, co:∃krakatit)
→ Karel Čapek
   - napsat(kdo: Karel Čapek, co: Krakatit)  [s0004]
       zdroj: „Karel Čapek napsal román Krakatit.“ (dialog, věta 2)
   [řekls to]
```

*Všimni si:* „drama R.U.R.“ je *nominativ jmenovací*: název je entita, hlava je její třída (R.U.R. ∈ drama). „Která díla“ = díra omezená skupinou *dílo* — R.U.R. je dílo přes seed řádek `drama ⊆ dílo` (`lex:pod:0002`), Loupežník řetězem tvůj řádek `veselohra ⊆ komedie` (`lex:said:0001`) → seed `komedie ⊆ drama`. „Vyjmenuj…“ je otázka druhu `list`, nezapíše se.

## 10. Statusy: hypotéza, zamítnutí, obsah promluvy — nic se nedomýšlí potichu

*Co ukazuje:* Každý výrok má `claim`: SAFE (znalost), HYPOTHESIS (nikdy neodpovídá), REJECTED (viditelné zamítnutí s důvodem). Disjunkce „Petr nebo Jana přijde“ v1 nemá prostor modelů → REJECTED, a odpověď to **řekne** místo mlčení. „Marie řekla, že…“ je obsah promluvy (`mood=reported`), ne fakt o světě.

```
» Petr nebo Jana přijde.
✓ zapsáno [s0001] přijít(kdo: Petr + Jana) [zamítnuto]
   [koordinace:kdo:distribuce]
```
```
» Přijde Petr?
čtu: přijít(kdo:·Petr)
→ NEVÍM
   chybí: o „přijít“ nemám žádný výrok
   ⚠ text o tom mluví (věta 1: „Petr nebo Jana přijde.“), ale interpretaci neurčuje: disjunkce bez prostoru modelů
```
```
» Marie řekla, že Petr přijde.
✓ zapsáno [s0002] říci(kdo: Marie, co: [přijít(kdo: Petr) [obsah promluvy, ne fakt]])
```
```
» Přijde Petr?
čtu: přijít(kdo:·Petr)
→ NEVÍM
   chybí: o „přijít“ nemám žádný výrok
   ⚠ text o tom mluví (věta 1: „Petr nebo Jana přijde.“), ale interpretaci neurčuje: disjunkce bez prostoru modelů
   vím:
   - přijít(kdo: Petr) [obsah promluvy, ne fakt]  — zdroj: „Marie řekla, že Petr přijde.“ (dialog, věta 2)
```
```
» !statusy
SAFE 2 (z toho znalost 1) · HYPOTHESIS 0 · REJECTED 1 · nálady: assert 2, reported 1 · otevřené 0
```

## 11. Oprava, odvolání, zapomenutí — historie zůstává v grafu

*Co ukazuje:* „Ne, …“ odvolá poslední řečený výrok a zapíše nový; `!zapomeň s…` odvolá výrok explicitně (kaskádou i odvozené). Odvolané výroky se z grafu nemažou — mají `life=revoked`, aby bylo vidět, co se kdy vědělo.

```
» Petr bydlí v Praze.
✓ zapsáno [s0001] bydlet(kdo: Petr, kde: Praha)
```
```
» Ne, Petr bydlí v Brně.
odvolávám: s0001
✓ zapsáno [s0002] bydlet(kdo: Petr, kde: Brno)
```
```
» Kde bydlí Petr?
čtu: bydlet(kde:?, kdo:·Petr)
→ Brno
   - bydlet(kdo: Petr, kde: Brno)  [s0002]
       zdroj: „Ne, Petr bydlí v Brně.“ (dialog, věta 2)
   [řekls to]
```
```
» !program
s0001: bydlet(kdo:·Petr, kde:·Praha) @said @dialog#1 ✗(oprava (tah 2): Ne, Petr bydlí v Brně.)
s0002: bydlet(kdo:·Petr, kde:·Brno) @said @dialog#2
```

## 12. Introspekce: `!ukaž`, `!otevřené`, `!odpověz`, `!role`

*Co ukazuje:* Každý výrok jde vypsat s celou proveniencí (`!ukaž s0001`): zdrojová věta, výchozí volby, hrany. Co systém nevěděl, jak umístit, není ztraceno — je to *otevřená položka* (`!otevřené`), a člověk ji může zodpovědět (`!odpověz`) nebo doučit roli (`!role`).

```
» Alois Jirásek psal v Lidových novinách.
✓ zapsáno [s0001] psát(kdo: Alois Jirásek, v+Loc: ∃noviny (lidový))
   ? o0001: Co znamená role „v+Loc“ (v+Loc)? (kde, kdy, kudy, čím, …)
```
```
» !otevřené
o0001 [role_name] (s0001): Co znamená role „v+Loc“ (v+Loc)? (kde, kdy, kudy, čím, …)
```
```
» !role v+Loc = kde
naučeno: v+Loc = kde; přejmenováno v 1 výrocích
```
```
» Kde psal Alois Jirásek?
čtu: psát(kde:?, kdo:·Alois Jirásek)
→ noviny (lidový)
   - psát(kdo: Alois Jirásek, kde: ∃noviny (lidový))  [s0001]
       zdroj: „Alois Jirásek psal v Lidových novinách.“ (dialog, věta 1)
   [řekls to; role v+Loc → kde (naučeno, tah 3)]
```
```
» !ukaž s0001
s0001  SAFE · řekls to · aktivní · nálada assert
  psát(kdo: Alois Jirásek, kde: ∃noviny (lidový))
  source → z0001 „Alois Jirásek psal v Lidových novinách.“ (dialog, věta 1)
  defaults: role v+Loc → kde (naučeno, tah 3)
  open: o0001 Co znamená role „v+Loc“ (v+Loc)? (kde, kdy, kudy, čím, …) → kde
  role:kdo → e0001 Alois Jirásek (entity)
  role:kde → g0002 noviny (lidový) (group)
```

