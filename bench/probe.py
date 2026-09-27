"""Lineární sonda: jsou vztahy `read.py` přítomné v embeddingu NN parseru?

Proč (J. 27. 9. 2026, „jde mi o embeding read vztahu do nn“): než se řeší
architektura NN, co by `read.py` nahradila, je poctivější napřed zjistit,
jestli informace, kterou `read.py` z rozboru VYTAHUJE (role `kdo`/`co`/
`kde`/`čí`…), je vůbec **přítomná v embeddingu**, který NN parser (spaCy
`cs_core_news_sm`, `tok2vec`, 96 dimenzí na token) už dnes počítá — bez
tréninku čehokoli nového, jen diagnostickou sondou (standardní metoda v
NLP: „probing classifier“). Vysoká přesnost sondy = relace jsou v
embeddingu lineárně čitelné (silný signál, že učení by mohlo fungovat);
nízká = embedding tuhle informaci nenese (ne tenhle model, ne takhle).

`read.py` je tu učitel (I‑9 zobecněné — NN dělá jen strukturu, žádná
znalost se neukládá do grafu); štítek = jméno role, kterou `read.py`
tokenu přiřadil, ne nic ověřovaného člověkem — proto se bere z reálného
korpusu ve VELKÉM (stovky vět), ne z pár ručně vybraných.

Provenience: `spacy model=cs_core_news_sm` — jiná provenience než UDPipe2
(I‑12), čísla se nesrovnávají s historickými zprávami.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from bench.data import Doc, load_config, load_wiki
from cb6.oracle import Parse, Token
from cb6.read import Predication, read as read_parse

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])")


def _sentences_with_vectors(nlp: Any, text: str):
    """Stejné dělení na věty jako `cb6.oracle.SpacyOracle` (musí sedět token
    po tokenu), ale vrací i spaCy `Doc` (nese `tok2vec` embedding na token) —
    `SpacyOracle.parse()` embedding zahazuje (`Parse`/`Token` jsou bez něj,
    záměrně minimální, viz `oracle.py`)."""
    for piece in _SENT_SPLIT.split(text.strip()):
        piece = piece.strip()
        if not piece:
            continue
        doc = nlp(piece)
        toks = list(doc)
        if not toks:
            continue
        local = {t.i: i + 1 for i, t in enumerate(toks)}
        tokens = tuple(
            Token(i + 1, t.text, t.lemma_, t.pos_,
                  0 if t.head == t or t.head.i not in local else local[t.head.i],
                  "root" if t.dep_ == "ROOT" else t.dep_,
                  tuple(sorted(t.morph.to_dict().items())))
            for i, t in enumerate(toks)
        )
        parse = Parse(doc.text, tokens, "spacy model=cs_core_news_sm")
        yield parse, toks


def _token_labels(p: Predication) -> dict[int, str]:
    """Token (1-indexovaný) → jméno role, kterou mu `read.py` přiřadil — z
    hlavní predikace i jejích vnořených/vedlejších. Díra (`wh`) se přeskočí
    (nic nekonzumovala); token beze role zůstává bez klíče (= „O“ dál)."""
    labels: dict[int, str] = {}

    def walk(pred: Predication) -> None:
        for role in pred.roles:
            if role.wh:
                continue
            for term in role.terms:
                for idx in term.tokens:
                    labels[idx] = role.name
                if term.rel_owner is not None:
                    # krok 3 (genitiv u vztahového substantiva): `rel_owner` je
                    # spotřebovaný jako součást termu hlavy (`manžel dcery`), ale
                    # jméno role „čí“ nese sám o sobě — jinak by sonda vůbec
                    # neviděla, že tahle konstrukce existuje (`ground.py` ji
                    # materializuje jako roli až na výroku, ne na predikaci).
                    for idx in term.rel_owner.tokens:
                        labels[idx] = "čí"
            if role.nested is not None:
                walk(role.nested)
        for sec in pred.secondary:
            walk(sec)

    walk(p)
    return labels


@dataclass
class Example:
    """Jeden token jako trénovací příklad sondy: embedding + role-štítek."""

    doc: str
    sentence: str
    form: str
    upos: str
    label: str
    vector: Any  # np.ndarray, 96-dim (tok2vec) — typ Any, aby modul nezávisel na numpy v type-checku


def build_examples(docs: list[Doc], nlp: Any, *, strop: int = 0) -> list[Example]:
    """Projeď dokumenty, pro každý token ulož (embedding, role-štítek).
    `read()` je čistá funkce parse→Predication — žádná paměť, žádný stav
    mezi větami (na rozdíl od `bench.distill`, které jde přes `Session` kvůli
    kvalitě/residuu); tady stačí přímo."""
    out: list[Example] = []
    for doc in docs:
        lines = doc.text.splitlines()
        if strop:
            kept: list[str] = []
            n = 0
            for line in lines:
                if line.strip():
                    n += 1
                    if n > strop:
                        break
                kept.append(line)
            lines = kept
        for raw in lines:
            line = raw.strip("= ").strip()
            if not line:
                continue
            for parse, toks in _sentences_with_vectors(nlp, line):
                try:
                    reading = read_parse(parse, "assert", learned_roles={})
                except Exception:  # pylint: disable=broad-exception-caught
                    continue  # sonda měří embedding, ne odolnost čtení — pár pádů se přeskočí
                labels = _token_labels(reading.main)
                for i, tok in enumerate(parse.tokens):
                    out.append(Example(
                        doc=doc.name, sentence=parse.text, form=tok.form, upos=tok.upos,
                        label=labels.get(tok.index, "O"), vector=toks[i].vector,
                    ))
    return out


def run_probe(examples: list[Example], *, min_support: int = 60, test_size: float = 0.25, seed: int = 0) -> dict[str, Any]:
    """Natrénuj lineární sondu (`LogisticRegression`) na (embedding → role) a
    změř přesnost proti triviální většinové základně. Třídy s málo příklady
    (`< min_support`) se sloučí do zbytku (jinak `train_test_split` na pár
    kusech spadne, a číslo by beztak nic neříkalo; dlouhý ocas povrchových
    předložkových jmen — `role_by_case` fallback bez přiřazení — jinak
    zamlží čitelnost tabulky beze změny závěru).

    Dvě čísla o přesnosti, ne jedno — jsou nesrovnatelná napřímo:
    `accuracy_plain` (obyčejná LR, srovnatelná s většinovou základnou 1:1)
    a `accuracy_balanced` (`class_weight="balanced"`, kompenzuje `O`/`co`
    dominanci — ukazuje signál u ŘÍDKÝCH rolí, ale POD základnou, protože
    cíleně obětuje přesnost na většinové třídě).
    Vstup: příklady, práh podpory třídy, podíl testu, seed (determinismus).
    Výstup: dict se souhrnem (obě přesnosti/základna, `sklearn` report)."""
    import numpy as np  # pylint: disable=import-outside-toplevel
    from sklearn.linear_model import LogisticRegression  # pylint: disable=import-outside-toplevel
    from sklearn.metrics import balanced_accuracy_score, classification_report  # pylint: disable=import-outside-toplevel
    from sklearn.model_selection import train_test_split  # pylint: disable=import-outside-toplevel

    counts = Counter(e.label for e in examples)
    kept_labels = {lab for lab, n in counts.items() if n >= min_support}

    def _lab(e: Example) -> str:
        return e.label if e.label in kept_labels else ("O" if e.label == "O" else "jiné")

    x = np.stack([e.vector for e in examples])
    y = np.array([_lab(e) for e in examples])
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=test_size, random_state=seed, stratify=y)
    baseline = Counter(yte).most_common(1)[0][1] / len(yte)
    plain = LogisticRegression(max_iter=2000)
    plain.fit(xtr, ytr)
    acc_plain = plain.score(xte, yte)
    balanced = LogisticRegression(max_iter=2000, class_weight="balanced")
    balanced.fit(xtr, ytr)
    acc_balanced = balanced.score(xte, yte)
    bal_acc = balanced_accuracy_score(yte, balanced.predict(xte))
    return {
        "n": len(examples), "n_train": len(xtr), "n_test": len(xte),
        "label_counts": dict(counts), "kept_labels": sorted(kept_labels),
        "baseline_majority": round(baseline, 4),
        "accuracy_plain": round(acc_plain, 4), "accuracy_balanced": round(acc_balanced, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "report": classification_report(yte, balanced.predict(xte), zero_division=0),
    }


def render(result: dict[str, Any]) -> str:
    """Čitelný výpis souhrnu sondy (přesnosti + `sklearn` report na roli)."""
    lines = [
        f"sonda (read.py role ← tok2vec embedding, {result['n']} tokenů, "
        f"{result['n_train']} trénink / {result['n_test']} test, "
        f"{len(result['kept_labels'])} tříd + O + jiné):",
        f"  většinová základna (jen O)         : {result['baseline_majority']:.1%}",
        f"  sonda, obyčejná LR (srovnej s výše) : {result['accuracy_plain']:.1%}",
        f"  sonda, class_weight=balanced        : {result['accuracy_balanced']:.1%} "
        f"(obětuje přesnost na O za recall na řídkých třídách)",
        f"  balanced accuracy (průměr recall přes třídy, fér vůči nevyváženosti): {result['balanced_accuracy']:.1%}",
        "  podpora podle role (před sloučením řídkých, top 20):",
    ]
    for lab, n in sorted(result["label_counts"].items(), key=lambda x: -x[1])[:20]:
        lines.append(f"    {lab:10s} {n}")
    lines.append("")
    lines.append(result["report"])
    return "\n".join(lines)


def main(argv: list[str]) -> int:  # pragma: no cover — tenká CLI fasáda
    """`python -m bench probe [--strop N] [--dok jméno...]` — natrénuj sondu
    a vypiš přesnost. Vždy vrací 0 (informační bench)."""
    import argparse  # pylint: disable=import-outside-toplevel

    import cs_core_news_sm  # pylint: disable=import-outside-toplevel

    ap = argparse.ArgumentParser(prog="bench probe")
    ap.add_argument("--strop", type=int, default=0, help="nejvýš N neprázdných řádků na dokument (0 = vše)")
    ap.add_argument("--dok", nargs="*", help="jen tyto dokumenty (jinak celá sada wiki)")
    args = ap.parse_args(argv)
    cfg = load_config()
    docs = load_wiki(cfg, only=args.dok, with_auto=False)
    nlp = cs_core_news_sm.load()
    examples = build_examples(docs, nlp, strop=args.strop)
    print(render(run_probe(examples)))
    return 0
