"""Zlaté otázky s hlavou a patou (`bench/gold/`).

Požadavek J. (17. 8. 2026): věty a otázky, na kterých se testuje a učí,
musí mít smysl. conbond5 převzal automaticky generovanou sadu conBond2
(`otazky.json`, 682 kde/kdy) a s ní i paskvily typu „Kdy vytvořil Josef
Čapek?“ nebo „Kdy se seznámil Josef Čapek?“ — otázka bez předmětu, který
věta má. Takové otázky měří šum, ne porozumění.

Proto:
* kurátorované sady (`etalon.json` 40, `conbond.json` 95 — psané člověkem)
  jsou v repu beze změny, s proveniencí (`PROVENIENCE.md`);
* automatická sada projde **valenčním filtrem** (`filter_auto`): otázka se
  udrží jen tehdy, když ve zdrojové větě sloveso *nemá* doplnění, které
  otázka zamlčela (`obj`, `iobj`, `ccomp`, `xcomp`, `obl:arg`, `csubj`),
  a sloveso není fázové / modální / lehké / zvratné s povinným doplněním
  (`BLACKLIST`). Výsledek `otazky-filtr.json` nese pro každou otázku zdrojovou
  větu a důvod přijetí; zamítnuté jdou do `otazky-filtr.log.md` s důvodem —
  filtr je auditovatelný;
* bench vykazuje kurátorované a automatické odděleně; hlavní číslo QA je jen
  z kurátorovaných (`metrics.qa_metrics` → `curated_hits`).

Filtr je deterministický a jede jen z keše rozborů (otázky i věty už
v keši jsou z běhů conbond5); chybějící rozbor = otázka se zamítne
s důvodem „bez rozboru“.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any

from cb6.oracle import CachedOracle, Parse

from bench.data import HERE, ensure_wiki_corpus, load_config
from bench.qa import norm, years

GOLD = HERE / "gold"

#: Slovesa, u nichž otázka „Kde/Kdy <sloveso> <jméno>?“ nemá smysl bez
#: doplnění (fázová, modální, lehká, zvratná s povinným doplněním, sponová).
BLACKLIST = {
    "začít", "začínat", "přestat", "přestávat", "muset", "moci", "smět", "chtít", "mít", "být", "bývat",
    "stát_se", "stávat_se", "podívat_se", "dívat_se", "dát", "dát_se", "dávat", "dostat", "dostávat",
    "snažit_se", "pokusit_se", "pokoušet_se", "rozhodnout_se", "rozhodovat_se", "dokázat", "umět", "dovést",
    "pokračovat", "patřit", "stát", "seznámit_se", "seznamovat_se", "setkat_se", "setkávat_se", "věnovat_se",
    "zúčastnit_se", "účastnit_se", "podílet_se", "zabývat_se", "zajímat_se", "stýkat_se", "spolupracovat",
    "považovat", "jít", "chodit", "jet", "jezdit", "přijít", "odejít", "vrátit_se", "vracet_se", "vydat_se",
    "dělat", "udělat", "činit", "konat", "konat_se", "trvat", "zůstat", "zůstávat", "nechat", "nechávat",
    "vzít", "brát", "držet", "vést", "nést", "přinést", "dojít", "docházet", "získat", "získávat", "ztratit",
    "prohlásit", "říci", "říkat", "tvrdit", "uvést", "uvádět", "napsat", "psát", "vydat", "vydávat", "vytvořit",
    "vytvářet", "založit", "zakládat", "hrát", "věnovat", "poslat", "posílat", "číst", "přečíst",
}
#: Doplnění, jehož přítomnost u slovesa znamená, že otázka něco zamlčela.
ARG_DEPRELS = ("obj", "iobj", "ccomp", "xcomp", "obl:arg", "csubj", "csubj:pass")
#: Předložky, po nichž je `obl` odpovědí na „kde“ (ne „kam/odkud“).
LOC_PREPS = {"v", "na", "u", "při", "nad", "pod", "mezi", "vedle", "poblíž", "blízko", "uprostřed"}
#: Lemmata, která dělají z `obl` odpověď na „kdy“.
TIME_LEMMAS = {"rok", "roku", "den", "léto", "století", "měsíc", "týden", "doba", "období", "leden", "únor", "březen", "duben",
               "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad", "prosinec", "začátek", "konec", "polovina"}


def _verb_lemma(parse: Parse) -> str:
    """Lemma přísudku (s `_se` u zvratných) — z rozboru otázky."""
    root = parse.root()
    head = root
    if root.upos != "VERB":
        for c in parse.children(root.index):
            if c.upos == "VERB":
                head = c
                break
    lemma = head.lemma
    for c in parse.children(head.index):
        if c.deprel == "expl:pv":
            lemma += "_se"
    return lemma


def _find_source(lines: list[str], oracle: CachedOracle, expect: str, verb: str) -> tuple[Parse | None, str]:
    """Věta v dokumentu, která obsahuje odpověď a sloveso; `("", důvod)`, když
    není nebo není v keši."""
    stem = verb.split("_")[0]
    stem = stem[:-2] if len(stem) > 5 else stem[:-1]
    for line in lines:
        ln = norm(line)
        if not (norm(expect) in ln or (years(expect) and years(expect) & years(line))):
            continue
        try:
            parses = oracle.segment(line)
        except KeyError:
            return None, "bez rozboru"
        for p in parses:
            pn = norm(p.text)
            if not (norm(expect) in pn or (years(expect) and years(expect) & years(p.text))):
                continue
            for t in p.tokens:
                if t.upos == "VERB" and (t.lemma == verb.split("_")[0] or t.lemma.startswith(stem)):
                    return p, ""
    return None, "věta s odpovědí a slovesem nenalezena"


def _check(parse: Parse, verb: str, expect: str, wh: str, q_reflexive: bool) -> tuple[bool, str]:
    """Sedí otázka na zdrojovou větu?

    1. sloveso ve větě nemá doplnění, které otázka zamlčela (`ARG_DEPRELS`);
    2. zvratnost otázky odpovídá větě („Kdy se vystoupil X?“ je paskvil);
    3. odpověď je `obl` přímo pod slovesem, a u „kde“ po místní předložce
       (ne `do`/`z`/`k` — to by byla otázka „kam/odkud/ke komu“), u „kdy“
       s časovým lemmatem nebo letopočtem.
    """
    base = verb.split("_")[0]
    exp_norm = norm(expect)
    exp_years = years(expect)
    for t in parse.tokens:
        if t.upos != "VERB" or t.lemma != base:
            continue
        kids = parse.children(t.index)
        deps = [c.deprel for c in kids]
        bad = [d for d in deps if d in ARG_DEPRELS]
        if bad:
            return False, "sloveso má doplnění " + ", ".join(sorted(set(bad)))
        has_refl = any(c.deprel == "expl:pv" for c in kids)
        if has_refl != q_reflexive:
            return False, "zvratnost otázky nesedí na větu"
        obls = [c for c in kids if c.deprel.startswith("obl") or c.deprel in ("advmod", "nmod")]
        for o in obls:
            sub = parse.subtree(o.index)
            text = " ".join(x.form for x in sub)
            if not (exp_norm in norm(text) or (exp_years and exp_years & years(text))):
                continue
            case = [c.lemma for c in parse.children(o.index) if c.deprel == "case"]
            if wh == "kde":
                if case and case[0] in LOC_PREPS:
                    return True, "valence ok, kde po místní předložce"
                if not case and o.upos == "PROPN":
                    return True, "valence ok, kde bez předložky"
                return False, f"odpověď na „kde“ není místní určení (předložka {case[0] if case else '—'})"
            if wh == "kdy":
                lem = {x.lemma for x in sub}
                if exp_years & years(text) or lem & TIME_LEMMAS:
                    return True, "valence ok, kdy s časem"
                return False, "odpověď na „kdy“ není časové určení"
            return True, "valence ok"
        return False, "odpověď není doplněním slovesa"
    return False, "sloveso v rozboru nenalezeno"


def filter_auto(oracle: CachedOracle, cfg: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], Counter[str]]:
    """Projdi `otazky.json` conBond2 a vrať přijaté otázky + počty důvodů zamítnutí."""
    cfg = cfg or load_config()
    root = ensure_wiki_corpus(cfg)
    src = json.loads((root / cfg["wiki"]["gold"] / "otazky.json").read_text(encoding="utf-8"))
    raw = root / cfg["wiki"]["raw"]
    kept: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    docs_lines: dict[str, list[str]] = {}
    for item in src:
        q, doc, expect = str(item["text"]), str(item["dok"]), str(item["odpoved"])
        try:
            qp = oracle.parse(q)
        except KeyError:
            reasons["otázka bez rozboru"] += 1
            continue
        verb = _verb_lemma(qp)
        wh = q.split()[0].lower()
        q_reflexive = any(t.lemma == "se" and t.deprel == "expl:pv" for t in qp.tokens) or " se " in f" {q.lower()} "
        if verb in BLACKLIST or verb.split("_")[0] in BLACKLIST:
            reasons[f"sloveso na černé listině ({verb})"] += 1
            continue
        if doc not in docs_lines:
            p = raw / f"{doc}.txt"
            docs_lines[doc] = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []
        sp, why = _find_source(docs_lines[doc], oracle, expect, verb)
        if sp is None:
            reasons[why] += 1
            continue
        ok, why = _check(sp, verb, expect, wh, q_reflexive)
        if not ok:
            reasons[why] += 1
            continue
        kept.append({"q": q, "expect": [expect], "dok": doc, "veta": item.get("veta"), "typ": item.get("typ", ""),
                     "verb": verb, "source_sentence": sp.text, "reason": why})
    return kept, reasons


def write_filtered(kept: list[dict[str, Any]], reasons: Counter[str], total: int) -> None:
    """Zapiš `otazky-filtr.json` + `otazky-filtr.log.md`."""
    GOLD.mkdir(exist_ok=True)
    (GOLD / "otazky-filtr.json").write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"# otazky-filtr — {len(kept)} přijato z {total} automatických otázek conBond2", "",
             "Filtr: sloveso není na černé listině a ve zdrojové větě nemá `obj`/`iobj`/`ccomp`/`xcomp`/`obl:arg`/`csubj`.", "",
             "| důvod zamítnutí | počet |", "|---|---:|"]
    for k, v in reasons.most_common():
        lines.append(f"| {k} | {v} |")
    (GOLD / "otazky-filtr.log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:  # pylint: disable=unused-argument
    """`python -m bench gold-filter` — přegeneruje vyfiltrovanou sadu."""
    from bench.run import make_oracle  # pylint: disable=import-outside-toplevel  (cyklus)
    cfg = load_config()
    oracle = make_oracle(cfg)
    kept, reasons = filter_auto(oracle, cfg)
    total = len(kept) + sum(reasons.values())
    write_filtered(kept, reasons, total)
    oracle.flush()
    print(f"přijato {len(kept)} / {total}; zamítnuto: " + ", ".join(f"{k} {v}" for k, v in reasons.most_common(8)), file=sys.stderr)
    return 0
