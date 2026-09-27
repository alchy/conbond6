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
    """Jeden token jako trénovací příklad sondy: embedding + role-štítek.

    `head_vector`/`deprel` nesou HRANU (rodič v závislostním stromu), ne jen
    uzel — `read.py` se rozhoduje přesně podle týchž dvou věcí (`t.head`,
    `c.base_deprel`), ne podle tokenu izolovaně (J. 27. 9. 2026: „conditioning
    je abstrakce nad daty“ — patří do VSTUPU sondy, ne do množství dat)."""

    doc: str
    sentence: str
    form: str
    upos: str
    deprel: str
    label: str
    vector: Any  # np.ndarray, 96-dim (tok2vec) — typ Any, aby modul nezávisel na numpy v type-checku
    head_vector: Any  # totéž pro rodiče v závislostním stromu (nuly, je-li token kořen)


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
                    head_vec = toks[tok.head - 1].vector if tok.head else _zeros_like(toks[i].vector)
                    out.append(Example(
                        doc=doc.name, sentence=parse.text, form=tok.form, upos=tok.upos,
                        deprel=tok.base_deprel, label=labels.get(tok.index, "O"),
                        vector=toks[i].vector, head_vector=head_vec,
                    ))
    return out


def _zeros_like(vector: Any) -> Any:
    """Nulový vektor stejného tvaru — kořen věty nemá rodiče (import `numpy`
    zůstává líný, viz modul výše — `bench.probe` na něm nezávisí natvrdo)."""
    import numpy as np  # pylint: disable=import-outside-toplevel
    return np.zeros_like(vector)


def _feature_matrix(examples: list[Example], idx: Any, features: str, deprel_vocab: list[str]) -> Any:
    """Sestav vstup sondy pro daný výběr příkladů (`idx`).

    `"token"` = jen embedding tokenu (původní sonda). `"edge"` = token +
    rodič + one-hot deprelu — vstup zapíná právě to, na čem se rozhoduje
    `read.py` (`t.head`, `c.base_deprel`), ne víc dat, jiný VSTUP (J. 27. 9.
    2026: „conditioning je abstrakce nad daty“). `deprel_vocab` je pevná
    (z trénovacích dat, ne dotažená z testu — jinak by šlo o únik informace)."""
    import numpy as np  # pylint: disable=import-outside-toplevel

    vec = np.stack([examples[i].vector for i in idx])
    if features == "token":
        return vec
    head = np.stack([examples[i].head_vector for i in idx])
    onehot = np.zeros((len(idx), len(deprel_vocab) + 1))
    pos = {d: i for i, d in enumerate(deprel_vocab)}
    for row, i in enumerate(idx):
        onehot[row, pos.get(examples[i].deprel, len(deprel_vocab))] = 1.0
    return np.concatenate([vec, head, onehot], axis=1)


def run_probe(examples: list[Example], *, min_support: int = 60, test_size: float = 0.25, seed: int = 0,
              features: str = "edge") -> dict[str, Any]:
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
    Vstup: příklady, práh podpory třídy, podíl testu, seed (determinismus),
    `features` (`"token"` / `"edge"`, viz `_feature_matrix`).
    Výstup: dict se souhrnem (obě přesnosti/základna, `sklearn` report)."""
    import numpy as np  # pylint: disable=import-outside-toplevel
    from sklearn.linear_model import LogisticRegression  # pylint: disable=import-outside-toplevel
    from sklearn.metrics import balanced_accuracy_score, classification_report  # pylint: disable=import-outside-toplevel
    from sklearn.model_selection import train_test_split  # pylint: disable=import-outside-toplevel
    from sklearn.preprocessing import StandardScaler  # pylint: disable=import-outside-toplevel

    counts = Counter(e.label for e in examples)
    kept_labels = {lab for lab, n in counts.items() if n >= min_support}

    def _lab(e: Example) -> str:
        return e.label if e.label in kept_labels else ("O" if e.label == "O" else "jiné")

    y_all = np.array([_lab(e) for e in examples])
    all_idx = np.arange(len(examples))
    idx_tr, idx_te, ytr, yte = train_test_split(all_idx, y_all, test_size=test_size, random_state=seed, stratify=y_all)
    deprel_vocab = sorted({examples[i].deprel for i in idx_tr})
    xtr = _feature_matrix(examples, idx_tr, features, deprel_vocab)
    xte = _feature_matrix(examples, idx_te, features, deprel_vocab)
    # standardizace (jen z tréninku — únik informace z testu by číslo zkreslil):
    # `lbfgs` bez ní konverguje řádově pomaleji na smíšeném vstupu (embedding
    # + one-hot deprelu mají jinou škálu) — změřeno 27. 9. 2026 (mereni/
    # HYPOTEZY.md): 84,9 s → 17,5 s, PŘESNOST beze ztráty (spíš lehce nahoru).
    scaler = StandardScaler().fit(xtr)
    xtr, xte = scaler.transform(xtr), scaler.transform(xte)
    baseline = Counter(yte).most_common(1)[0][1] / len(yte)
    plain = LogisticRegression(max_iter=1000)
    plain.fit(xtr, ytr)
    acc_plain = plain.score(xte, yte)
    balanced = LogisticRegression(max_iter=1000, class_weight="balanced")
    balanced.fit(xtr, ytr)
    acc_balanced = balanced.score(xte, yte)
    bal_acc = balanced_accuracy_score(yte, balanced.predict(xte))
    return {
        "n": len(examples), "n_train": len(xtr), "n_test": len(xte), "features": features,
        "label_counts": dict(counts), "kept_labels": sorted(kept_labels),
        "baseline_majority": round(baseline, 4),
        "accuracy_plain": round(acc_plain, 4), "accuracy_balanced": round(acc_balanced, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "report": classification_report(yte, balanced.predict(xte), zero_division=0),
    }


def render(result: dict[str, Any]) -> str:
    """Čitelný výpis souhrnu sondy (přesnosti + `sklearn` report na roli)."""
    lines = [
        f"sonda (read.py role ← tok2vec embedding, vstup='{result['features']}', {result['n']} tokenů, "
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


def correction_experiment(examples: list[Example], *, n: int = 8, split_seed: int = 0, sample_seed: int = 1,
                          test_size: float = 0.25) -> dict[str, Any]:
    """„Dá se sonda formovat dialogem?“ (J. 27. 9. 2026): vezmi `n` NÁHODNÝCH
    špatně klasifikovaných příkladů rolí `kdo`/`co` (nejdůležitější, nejvíc
    postižené — viz `run_probe`), pro KAŽDÝ zvlášť (od stejného základního
    rozdělení) přesuň JEN JEHO do tréninku („člověk ho opravil“), přetrénuj a
    změř: (a) opravilo se PRÁVĚ tohle jedno místo? (b) nezhoršil se ZBYTEK
    held‑out množiny (zapomnělo se něco jinam)? Korekce jsou NEZÁVISLÉ (vždy
    z téhož základu), ne kumulativní — měří se síla JEDNÉ korekce, ne dialog
    o mnoha chybách najednou.

    Proč tohle, ne živé/gradientové učení za běhu: I‑9/I‑10/I‑11/I‑12 — sonda
    zůstává mimo graf (jen diagnostika), verzované PŘETRÉNOVÁNÍ z ulehčeného,
    auditovatelného seznamu příkladů je bezpečnější než tiché úpravy vah
    (viz `mereni/HYPOTEZY.md` diskuse s J.). Vstup: příklady (viz
    `build_examples`), počet korekcí, semínka (determinismus). Výstup: dict
    se souhrnem (základní přesnost, počet špatných kdo/co, na příklad opravil/
    nezhoršil zbytek, průměr/směrodatná odchylka dopadu na zbytek)."""
    import numpy as np  # pylint: disable=import-outside-toplevel
    from sklearn.linear_model import LogisticRegression  # pylint: disable=import-outside-toplevel
    from sklearn.model_selection import train_test_split  # pylint: disable=import-outside-toplevel
    from sklearn.preprocessing import StandardScaler  # pylint: disable=import-outside-toplevel

    y_all = np.array([e.label for e in examples])
    all_idx = np.arange(len(examples))
    idx_tr, idx_te, ytr, yte = train_test_split(all_idx, y_all, test_size=test_size, random_state=split_seed)
    deprel_vocab = sorted({examples[i].deprel for i in idx_tr})

    def _fit(tr_idx: Any, tr_y: Any) -> tuple[Any, Any]:
        x = _feature_matrix(examples, tr_idx, "edge", deprel_vocab)
        scaler = StandardScaler().fit(x)
        clf = LogisticRegression(max_iter=1000, class_weight="balanced")
        clf.fit(scaler.transform(x), tr_y)
        return clf, scaler

    clf0, scaler0 = _fit(idx_tr, ytr)
    xte = _feature_matrix(examples, idx_te, "edge", deprel_vocab)
    pred0 = clf0.predict(scaler0.transform(xte))
    baseline_acc = clf0.score(scaler0.transform(xte), yte)

    wrong = [i for i, (p, y) in enumerate(zip(pred0, yte)) if y in ("kdo", "co") and p != y]
    rng = np.random.default_rng(sample_seed)
    sample = rng.choice(wrong, size=min(n, len(wrong)), replace=False) if wrong else np.array([], dtype=int)

    rows: list[dict[str, Any]] = []
    for pos in sample:
        pos = int(pos)
        ex = examples[idx_te[pos]]
        true_lab = yte[pos]
        new_tr_idx = np.concatenate([idx_tr, [idx_te[pos]]])
        rest_te_idx = np.delete(idx_te, pos)
        rest_yte = np.delete(yte, pos)
        clf1, scaler1 = _fit(new_tr_idx, np.concatenate([ytr, [true_lab]]))
        own_pred = clf1.predict(scaler1.transform(_feature_matrix(examples, [idx_te[pos]], "edge", deprel_vocab)))[0]
        rest_after = clf1.score(scaler1.transform(_feature_matrix(examples, rest_te_idx, "edge", deprel_vocab)), rest_yte)
        rest_before = clf0.score(scaler0.transform(_feature_matrix(examples, rest_te_idx, "edge", deprel_vocab)), rest_yte)
        rows.append({"form": ex.form, "deprel": ex.deprel, "true": true_lab, "pred_before": pred0[pos],
                     "pred_after": own_pred, "fixed": bool(own_pred == true_lab),
                     "rest_before": rest_before, "rest_after": rest_after, "delta": rest_after - rest_before})

    deltas = [r["delta"] for r in rows]
    return {
        "n_examples": len(examples), "baseline_accuracy": round(baseline_acc, 4),
        "n_wrong_kdo_co": len(wrong), "n_tried": len(rows),
        "n_fixed": sum(1 for r in rows if r["fixed"]),
        "mean_delta": round(float(np.mean(deltas)), 5) if deltas else 0.0,
        "std_delta": round(float(np.std(deltas)), 5) if deltas else 0.0,
        "rows": rows,
    }


def render_correction(result: dict[str, Any]) -> str:
    """Čitelný výpis `correction_experiment` — na řádek, pak souhrn."""
    lines = [
        f"korekční pokus (edge sonda, {result['n_examples']} tokenů, základní přesnost {result['baseline_accuracy']:.1%}, "
        f"{result['n_wrong_kdo_co']} špatných kdo/co v testu, vyzkoušeno {result['n_tried']}):",
    ]
    for r in result["rows"]:
        mark = "OPRAVENO" if r["fixed"] else "pořád špatně"
        lines.append(f"  '{r['form']}' ({r['deprel']}): {r['true']} ← {r['pred_before']} → po opravě: {r['pred_after']} "
                     f"[{mark}] · zbytek testu {r['rest_before']:.4f} → {r['rest_after']:.4f} ({r['delta']:+.4f})")
    lines.append(f"\nshrnutí: {result['n_fixed']}/{result['n_tried']} cílených korekcí uspělo; "
                 f"průměrný dopad na zbytek held-out množiny: {result['mean_delta']:+.5f} (směrodatná odchylka {result['std_delta']:.5f})")
    return "\n".join(lines)


def main(argv: list[str]) -> int:  # pragma: no cover — tenká CLI fasáda
    """`python -m bench probe [--strop N] [--dok jméno...] [--features token|edge|compare]
    [--korekce N]` — natrénuj sondu a vypiš přesnost. `compare` natrénuje obě
    varianty na STEJNÉM rozdělení dat a ukáže rozdíl (drahý krok — dvě sondy).
    `--korekce N` místo toho spustí `correction_experiment` („dá se sonda
    formovat dialogem?“ — N nezávislých cílených oprav, viz jeho docstring).
    Vždy vrací 0 (informační bench)."""
    import argparse  # pylint: disable=import-outside-toplevel

    import cs_core_news_sm  # pylint: disable=import-outside-toplevel

    ap = argparse.ArgumentParser(prog="bench probe")
    ap.add_argument("--strop", type=int, default=0, help="nejvýš N neprázdných řádků na dokument (0 = vše)")
    ap.add_argument("--dok", nargs="*", help="jen tyto dokumenty (jinak celá sada wiki)")
    ap.add_argument("--features", choices=["token", "edge", "compare"], default="edge",
                     help="token = jen embedding; edge = + rodič + deprel (výchozí); "
                          "compare = obě, na stejném rozdělení dat")
    ap.add_argument("--korekce", type=int, default=0, help="místo sondy spusť N nezávislých cílených korekcí (0 = normální sonda)")
    args = ap.parse_args(argv)
    cfg = load_config()
    docs = load_wiki(cfg, only=args.dok, with_auto=False)
    nlp = cs_core_news_sm.load()
    examples = build_examples(docs, nlp, strop=args.strop)
    if args.korekce:
        print(render_correction(correction_experiment(examples, n=args.korekce)))
    elif args.features == "compare":
        r_token = run_probe(examples, features="token")
        r_edge = run_probe(examples, features="edge")
        print(render(r_token))
        print()
        print(render(r_edge))
        print()
        print(f"rozdíl (edge − token), obyčejná LR: {r_edge['accuracy_plain'] - r_token['accuracy_plain']:+.1%}")
        print(f"rozdíl (edge − token), balanced acc: {r_edge['balanced_accuracy'] - r_token['balanced_accuracy']:+.1%}")
    else:
        print(render(run_probe(examples, features=args.features)))
    return 0
