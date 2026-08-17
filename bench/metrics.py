"""Metriky benche (spec § 5.3, 5.5).

Ingest: knowledge yield (SAFE výroků / 1 000 slov), počty podle statusu,
podíl zbytku, otevřené položky na větu, role na výrok, podíl výroků s časem
a místem, podíl zapsaných vět (musí být 100 %, I‑1).
QA: pokrytí (otázky, jejichž odpověď v textu je), zásahy, zásahy podle
pásma dosahu, rozklad chyb.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from cb6.memory import Memory, Node

from bench.qa import last_anchor_sentence

REACH_BANDS = ("0", "1-3", "4-10", ">10", "jiný segment", "?")


def ingest_metrics(memory: Memory, n_words: int, reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Metriky ingestu nad pamětí jednoho dokumentu.

    Args:
        memory: paměť po `Session.ingest`.
        n_words: počet slov vloženého textu (jmenovatel yieldu).
        reports: zprávy za větu z `Session.ingest` (klíče `statements`,
            `residue`, `open`, `error`).
    Returns:
        Slovník s klíči `yield`, `safe`, `derived`, `claims`, `pattern`,
        `reported`, `residue_pct`, `open_per_sent`, `open_closed`,
        `roles_per_stmt`, `pct_with_time`, `pct_with_place`, `written_pct`,
        `sentences`, `words`, `statements_active`.
    """
    know = [s for s in memory.knowledge() if s.grade in ("read", "said") and s.kind not in ("rule", "typing")]
    typing = sum(1 for s in memory.knowledge() if s.kind == "typing")
    #: hlavní predikace (sloveso, kopula) — bez vedlejších `nmod`/`appos`/fragmentů
    know_main = [s for s in know if s.kind in ("verb", "copula")]
    rules = [s for s in memory.knowledge() if s.kind == "rule"]
    derived = [s for s in memory.knowledge() if s.grade == "derived"]
    claims = Counter(s.claim for s in memory.active() if s.mood == "assert")
    pattern = sum(1 for s in memory.active() if s.mood == "pattern")
    reported = sum(1 for s in memory.active() if s.mood == "reported")
    n_sent = sum(1 for r in reports if not r.get("error"))
    written = sum(1 for r in reports if r.get("statements"))
    n_residue = sum(len(r.get("residue", [])) for r in reports)
    n_tokens = sum(len(n.text.split()) for n in memory.nodes.values() if n.kind == "sentence")
    n_open = sum(len(r.get("open", [])) for r in reports)
    open_all = list(memory.open_items_.values())
    closed = sum(1 for o in open_all if o.answer is not None)
    roles = [len([r for r in s.roles if r.terms or r.nested]) for s in know]
    with_time = sum(1 for s in know if any(r.name in ("kdy", "od_kdy", "do_kdy") and r.terms for r in s.roles))
    with_place = sum(1 for s in know if any(r.name in ("kde", "kam", "odkud") and r.terms for r in s.roles))
    return {
        "sentences": n_sent, "words": n_words,
        "written_pct": round(100.0 * written / n_sent, 1) if n_sent else 0.0,
        "yield": round(1000.0 * len(know) / n_words, 2) if n_words else 0.0,
        "safe": len(know), "safe_main": len(know_main), "rules": len(rules), "derived": len(derived),
        "yield_main": round(1000.0 * len(know_main) / n_words, 2) if n_words else 0.0,
        "claims": {k: claims.get(k, 0) for k in ("SAFE", "HYPOTHESIS", "REJECTED")},
        "pattern": pattern, "reported": reported, "typing": typing,
        "statements_active": sum(1 for _ in memory.active()),
        "residue_pct": round(100.0 * n_residue / n_tokens, 1) if n_tokens else 0.0,
        "residue_tokens": n_residue, "tokens": n_tokens,
        "open_per_sent": round(n_open / n_sent, 2) if n_sent else 0.0,
        "open": n_open, "open_closed": closed,
        "roles_per_stmt": round(sum(roles) / len(roles), 2) if roles else 0.0,
        "pct_with_time": round(100.0 * with_time / len(know), 1) if know else 0.0,
        "pct_with_place": round(100.0 * with_place / len(know), 1) if know else 0.0,
    }


def reach(memory: Memory, answer_sent_no: int, anchor: list[str], sentences: list[Node]) -> int | None:  # pylint: disable=unused-argument
    """Dosah otázky: vzdálenost věty s odpovědí od poslední předchozí věty
    (včetně), kde je téma jmenováno kotvou. 0 = táž věta; `None` = kotva
    před odpovědí není (odpověď se váže jen přes koreferenci od začátku).

    Args:
        memory: paměť (kvůli segmentům vět).
        answer_sent_no: číslo věty s odpovědí (naše číslování, 1‑based).
        anchor: slova jména tématu.
        sentences: uzly vět dokumentu.
    """
    pairs = [(int(n.lemma.rsplit("#", 1)[-1]), n.text) for n in sentences]
    pairs.sort()
    last = last_anchor_sentence(pairs, answer_sent_no, anchor)
    if last is None:
        return None
    return answer_sent_no - last


def reach_band(r: int | None, *, other_segment: bool = False) -> str:
    """Pásmo dosahu pro zprávu."""
    if other_segment:
        return "jiný segment"
    if r is None:
        return "?"
    if r == 0:
        return "0"
    if r <= 3:
        return "1-3"
    if r <= 10:
        return "4-10"
    return ">10"


def qa_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Souhrn QA nad výsledky (`ok`, `text_ok`, `coverage`, `reach`, `why`,
    `sada`, `curated`).

    Returns:
        `questions`, `coverage`, `hits`, `text_hits`, `by_reach` (pásmo →
        [zásahy, otázky]), `by_sada` (sada → [zásahy, otázky]), `curated_hits`
        / `curated_questions` (hlavní číslo — jen kurátorované), `misses`.
    """
    by_reach: dict[str, list[int]] = {b: [0, 0] for b in REACH_BANDS}
    by_sada: dict[str, list[int]] = {}
    misses: Counter[str] = Counter()
    hits = text_hits = coverage = 0
    cur_h = cur_n = 0
    for r in results:
        ok = bool(r.get("ok"))
        hits += ok
        text_hits += bool(r.get("text_ok"))
        coverage += bool(r.get("coverage", True))
        band = reach_band(r.get("reach"), other_segment=bool(r.get("other_segment")))
        by_reach[band][1] += 1
        by_reach[band][0] += ok
        sada = str(r.get("sada", "?"))
        by_sada.setdefault(sada, [0, 0])
        by_sada[sada][1] += 1
        by_sada[sada][0] += ok
        if r.get("curated", True):
            cur_n += 1
            cur_h += ok
        if not ok:
            misses[str(r.get("why", "?"))] += 1
    return {
        "questions": len(results), "coverage": coverage, "hits": hits, "text_hits": text_hits,
        "curated_questions": cur_n, "curated_hits": cur_h,
        "by_reach": by_reach, "by_sada": by_sada, "misses": dict(misses),
    }
