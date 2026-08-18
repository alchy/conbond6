"""Generátor `docs/UKAZKY.md` — ukázky schopností a principů z živého běhu.

    python -m bench ukazky            # přepíše docs/UKAZKY.md

Proč generovat, ne psát ručně: ukázky v dokumentaci musí sedět s kódem. Každá
scéna je seznam vstupů (věty, otázky, `!příkazy`), které se pošlou do čerstvé
`Session` (UDPipe přes keš `data/cache/parses.json`), a do dokumentu jde
**skutečný výstup** systému. Vysvětlující text ke každé scéně je tady v kódu
(česky, krátce): co scéna ukazuje a proč se systém chová právě takhle.
Přegenerovat po každém tahu, který mění odpovědi (`docs` jsou živé).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import live_or_recorded

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "cache" / "parses.json"
OUT = HERE / "docs" / "UKAZKY.md"


@dataclass
class Scene:
    """Jedna ukázka: nadpis, vysvětlení (co ukazuje, proč), vstupy v pořadí.

    `ingest` = text vložený jako dokument (víc vět najednou, s pro‑dropem
    a registrem referentů); `steps` = jednotlivé řádky dialogu (věta, otázka,
    `!příkaz`); `after` = poznámka pod výstupem (co si všimnout)."""

    title: str
    why: str
    steps: list[str] = field(default_factory=list)
    ingest: tuple[str, str] | None = None
    after: str = ""


SCENES: list[Scene] = [
    Scene(
        "Věta se zapíše, otázka se zodpoví — s důkazem a zdrojem",
        "Základní smyčka: text → UDPipe → čtení (predikát + role) → zápis do grafu jako *výrok* "
        "s proveniencí (dokument, věta). Otázka je výrok s dírou; odpověď je shoda s výroky paměti "
        "a **vždy nese důkaz**: který výrok, jaké kroky, jaké výchozí volby, jaký stupeň "
        "(přečteno / řečeno / odvozeno). „Celý život pracoval…“ nemá podmět — doplní se z registru "
        "referentů (koreference) a odpověď to přizná.",
        ingest=("alois_jirásek", "Alois Jirásek se narodil ve východočeském Hronově u Náchoda.\n"
                "Celý život pracoval jako učitel dějepisu na gymnáziu, nejprve v Litomyšli a poté v Praze."),
        steps=["Kde se narodil Alois Jirásek?", "Kde pracoval Alois Jirásek?", "Jako co pracoval?"],
        after="Všimni si hranatých závorek: `[přečteno z textu; kdo: „nevyslovený podmět“ = … (koref …)]` — "
              "každá výchozí volba je přiznaná (I‑8), nic se nedomýšlí potichu.",
    ),
    Scene(
        "NEVÍM není lež — otázka nesmí dostat víc, než paměť má",
        "Chyba conbond4 byla „Bydlí Petr v Brně? → ANO“ (shoda jen na predikátu). Tady musí **každá "
        "role otázky** mít protějšek ve výroku; výrok smí mít role navíc, otázka ne. Rok 2020 v otázce "
        "nemá ve výroku protějšek → NEVÍM s tím, co paměť ví (propad = recall nad týmž grafem).",
        steps=["Petr bydlí v Praze.", "Bydlí Petr v Brně?", "Bydlí Petr v Praze v roce 2020?", "Kde žije Petr?"],
        after="„Kde žije Petr?“ odpoví přes **lexikon**: řádek `bydlet ⇒ žít` (implikace, ne synonymum — kdo "
              "někde bydlí, tam žije, ne naopak); důkaz ukáže `[lex:syn:0031]` a stupeň klesne na *odvozeno*.",
    ),
    Scene(
        "Třídy, kvantifikátory a sylogismus; NE jen z disjunktnosti",
        "„Každý spisovatel je člověk“ = podmnožina (∀), „Hrabal je spisovatel“ = členství. Otázka „Je "
        "Hrabal stroj?“ dostane **NE** jen proto, že text říká „Žádný stroj není člověk“ (disjunktnost tříd) "
        "— jinak by bylo NEVÍM. „Napsal Postřižiny i nějaký stroj?“ je poctivé NEVÍM: nikdo to neřekl.",
        steps=["Každý spisovatel je člověk.", "Žádný stroj není člověk.", "Hrabal je spisovatel.",
               "Hrabal napsal Postřižiny.", "Je Hrabal stroj?", "Napsal Postřižiny spisovatel?",
               "Napsal Postřižiny i nějaký stroj?", "Kdo je Hrabal?"],
        after="Symbol `∦` v důkazu = disjunktní třídy; `∈`/`⊆` jsou tvrdé cesty v grafu, které audit "
              "(`bench/graphcheck.py`) ověřuje jen z exportu — bez přístupu k Pythonu.",
    ),
    Scene(
        "Co z textu neplyne — ∃ není ∀",
        "„Ovoce obsahuje vitamíny“ říká, že nějaké vitamíny — ne vitamín C. Systém rozlišuje "
        "„nějaký vitamín“ (∃, ANO přes ovoce ⊇ citron) a konkrétní vitamín C (NEVÍM, dokud to text neřekne).",
        steps=["Citron je ovoce.", "Ovoce obsahuje vitamíny.", "Vitamín C je vitamín.",
               "Obsahuje citron vitamín C?", "Obsahuje citron nějaký vitamín?", "Citron obsahuje vitamín C.",
               "Obsahuje citron vitamín C?"],
    ),
    Scene(
        "Konflikt se hlásí, výjimka se učí — bez default logic",
        "„Ptáci létají“ je obecná věta (∀ z generického prézentu) → „Létá tučňák?“ ANO přes ∀. Když "
        "přijde „Tučňák nelétá“, systém **před zápisem** zjistí konflikt a řekne to. Výjimku doučí "
        "člověk (`!výjimka létat pták tučňák`): obecný výrok pak pro tučňáka neplatí, pro vrabce ano.",
        steps=["Ptáci létají.", "Tučňák je pták.", "Létá tučňák?", "Tučňák nelétá.",
               "!výjimka létat pták tučňák", "Vrabec je pták.", "Létá vrabec?", "Létá tučňák?"],
    ),
    Scene(
        "Prostor a čas; můstkové pravidlo z konzole",
        "Místa mají uzávěr `within` (Praha ⊆ Česko), časy obsažení intervalů. „Byl Petr v pondělí v "
        "Česku?“ je nejdřív NEVÍM — text říká *jel do*, ne *byl v*. Pravidlo `!pravidlo jet(kam:X) => "
        "být(kde:X)` je řádek dat (ne kód): otázka na `být` se zkusí jako `jet` s přemapovanou rolí, "
        "důkaz to přizná a stupeň je *odvozeno*. Ve středu nikam nejel → NEVÍM.",
        steps=["Petr jel v pondělí do Prahy.", "V úterý jel Petr do Brna.", "Praha je v Česku.",
               "Byl Petr v pondělí v Česku?", "!pravidlo jet(kam:X) => být(kde:X)",
               "Byl Petr v pondělí v Česku?", "Kam jel Petr v pondělí?", "Kdy jel Petr do Prahy?",
               "Byl Petr ve středu v Česku?"],
    ),
    Scene(
        "Pravidla z textu („pokud“) a pevný bod odvození",
        "Podmínková věta není tvrzení o světě (I‑8): „Karel přijde, pokud přijde Jana“ zapíše "
        "**pravidlo** (vzory `mood=pattern`), ne fakt. Jakmile paměť dostane „Petr přijde“, `derive()` "
        "odvodí řetěz Jana → Karel; odvozené výroky mají `derived_from` + `uses_rule` (v grafu vidět).",
        ingest=("h", "Karel přijde na oslavu, pokud přijde Jana.\nJana přijde, pokud přijde Petr."),
        steps=["Přijde Karel?", "Petr přijde.", "Přijde Karel?", "!statusy"],
    ),
    Scene(
        "Instance, popis a vlastnost",
        "„Filip má auto“ založí anonymní instanci (a1 ∈ auto — typovací výrok, slouží uzávěrům, není to "
        "„znalost z textu“). „Filipovo auto je modré“ přivlastnění rozřeší na tutéž instanci. "
        "„Co má Filip?“ popíše instanci i s vlastností.",
        steps=["Filip má auto.", "Filipovo auto je modré.", "Co má Filip?", "Jaké je Filipovo auto?"],
    ),
    Scene(
        "Lexikon vazeb: znalost jako řádky dat, ne kód",
        "Čtyři místa, kde dřív žily „vazby“ (tabulka synonym v kódu, naučené dvojice, můstky, pravidla "
        "z textu), se sjednocují do **řádků** `{op, args, síla, autorita, zdroj}`. Operátory dnes: "
        "`třída` (~), `implikace` (⇒), `podřazení` (⊆). Síla `same/implies/related`; `related` nikdy "
        "neodpovídá, jen napovídá. Řádek se použije → v grafu vznikne uzel `vazba` s proveniencí až na "
        "soubor a řádek (líná materializace). Z konzole: `!uč a = b | a => b | a ~ b | a < b`.",
        steps=["Karel Čapek napsal drama R.U.R.", "Karel Čapek napsal román Krakatit.",
               "Která díla napsal Karel Čapek?", "Vyjmenuj všechna dramata.",
               "!uč veselohra < komedie", "Karel Čapek napsal veselohru Loupežník.", "Vypiš dramata Karla Čapka.",
               "Kdo napsal Krakatit?"],
        after="„drama R.U.R.“ je *nominativ jmenovací*: název je entita, hlava je její třída (R.U.R. ∈ drama). "
              "„Která díla“ = díra omezená skupinou *dílo* — R.U.R. je dílo přes seed řádek `drama ⊆ dílo` "
              "(`lex:pod:0002`), Loupežník řetězem tvůj řádek `veselohra ⊆ komedie` (`lex:said:0001`) → seed `komedie ⊆ drama`. "
              "„Vyjmenuj…“ je otázka druhu `list`, nezapíše se.",
    ),
    Scene(
        "Statusy: hypotéza, zamítnutí, obsah promluvy — nic se nedomýšlí potichu",
        "Každý výrok má `claim`: SAFE (znalost), HYPOTHESIS (nikdy neodpovídá), REJECTED (viditelné "
        "zamítnutí s důvodem). Disjunkce „Petr nebo Jana přijde“ v1 nemá prostor modelů → REJECTED, "
        "a odpověď to **řekne** místo mlčení. „Marie řekla, že…“ je obsah promluvy (`mood=reported`), "
        "ne fakt o světě.",
        steps=["Petr nebo Jana přijde.", "Přijde Petr?", "Marie řekla, že Petr přijde.", "Přijde Petr?",
               "!statusy"],
    ),
    Scene(
        "Oprava, odvolání, zapomenutí — historie zůstává v grafu",
        "„Ne, …“ odvolá poslední řečený výrok a zapíše nový; `!zapomeň s…` odvolá výrok explicitně "
        "(kaskádou i odvozené). Odvolané výroky se z grafu nemažou — mají `life=revoked`, aby bylo "
        "vidět, co se kdy vědělo.",
        steps=["Petr bydlí v Praze.", "Ne, Petr bydlí v Brně.", "Kde bydlí Petr?", "!program"],
    ),
    Scene(
        "Introspekce: `!ukaž`, `!otevřené`, `!odpověz`, `!role`",
        "Každý výrok jde vypsat s celou proveniencí (`!ukaž s0001`): zdrojová věta, výchozí volby, "
        "hrany. Co systém nevěděl, jak umístit, není ztraceno — je to *otevřená položka* "
        "(`!otevřené`), a člověk ji může zodpovědět (`!odpověz`) nebo doučit roli (`!role`).",
        steps=["Alois Jirásek psal v Lidových novinách.", "!otevřené", "!role v+Loc = kde",
               "Kde psal Alois Jirásek?", "!ukaž s0001"],
    ),
]


def run_scene(sc: Scene, oracle: object) -> list[tuple[str, str]]:
    """Proběhni scénu v čerstvé paměti; vrať dvojice (vstup, výstup)."""
    s = Session(Memory(), oracle)  # type: ignore[arg-type]
    out: list[tuple[str, str]] = []
    if sc.ingest is not None:
        doc, text = sc.ingest
        reps = s.ingest(text, doc)
        lines = []
        for r_ in reps:
            r: dict[str, Any] = dict(r_)  # zpráva za větu (klíče text/reading/statements/defaults/residue)
            lines.append(f"věta: {r.get('text', '')}")
            lines.append(f"  čtu: {r.get('reading', '')}")
            for sid in list(r.get("statements") or []):
                st = s.memory.statements[str(sid)]
                flag = "" if st.claim == "SAFE" else f" [{st.claim}]"
                lines.append(f"  ✓ [{sid}] {s.memory.render_short(st)}{flag}")
            if r.get("defaults"):
                lines.append("  [" + "; ".join(str(d) for d in list(r["defaults"])) + "]")
            if r.get("residue"):
                lines.append("  zbytek: " + ", ".join(f"„{f}“" for f, _ in list(r["residue"])))
        out.append((f"[dokument „{doc}“]\n{text}", "\n".join(lines)))
    for step in sc.steps:
        a = s.say(step)
        out.append((step, a.text))
    return out


def render(scenes: list[Scene], oracle: object) -> str:
    """Celý dokument v Markdownu."""
    parts = [
        "# conbond6 — ukázky (generováno z živého běhu)",
        "",
        "*Vygenerováno `python -m bench ukazky` — vstupy jdou do čerstvé paměti přes UDPipe, výstupy jsou "
        "skutečné odpovědi systému v okamžiku generování. Vysvětlení u scén jsou ručně psané; když se "
        "výstup změní tahem, přegeneruj (docs jsou živé). Základní principy a pojmy: `docs/UVOD.md`.*",
        "",
        "Čtení výstupu: `✓ zapsáno [s0001] …` = výrok v grafu (id, predikát, role); `[…]` = přiznané "
        "výchozí volby; `čtu: …` = jak systém přečetl otázku; `→` = výplň/odpověď; `↳` = krok důkazu; "
        "`zdroj:` = věta a dokument; `[přečteno z textu | řečeno | odvozeno z: …]` = stupeň důkazu.",
        "",
    ]
    for i, sc in enumerate(scenes, 1):
        parts.append(f"## {i}. {sc.title}")
        parts.append("")
        parts.append(f"*Co ukazuje:* {sc.why}")
        parts.append("")
        for inp, outp in run_scene(sc, oracle):
            parts.append("```")
            for ln in inp.splitlines():
                parts.append(f"» {ln}")
            parts.append(outp.rstrip())
            parts.append("```")
        if sc.after:
            parts.append("")
            parts.append(f"*Všimni si:* {sc.after}")
        parts.append("")
    return "\n".join(parts) + "\n"


def main(argv: list[str]) -> int:
    """CLI: přegeneruj `docs/UKAZKY.md` (nebo cestu z argv[0])."""
    out = Path(argv[0]) if argv else OUT
    oracle = live_or_recorded(CACHE)
    md = render(SCENES, oracle)
    out.write_text(md, encoding="utf-8")
    try:
        oracle.flush()  # type: ignore[attr-defined]
    except AttributeError:
        pass
    print(f"zapsáno {out} ({len(SCENES)} scén, {md.count(chr(10))} řádků)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
