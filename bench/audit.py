"""Precision audit (spec § 5.4): vzorek `SAFE` výroků proti zdrojové větě.

Proč: bench měří zápis (recall) a QA; bez auditu by „429/429 vět zapsáno“
mohlo skrývat výroky, které text netvrdí. Audit dává **unsupported rate** =
(netvrdí + ½·částečně) / posouzeno, s Wilsonovým intervalem (malé n nesmí
vypadat jako jistota), a **shodu soudce s člověkem** na průniku vzorku.

Vzorek je deterministický (seed z otisku commitu) — dva běhy na témž commitu
auditují tytéž výroky. Lidské odpovědi žijí v `mereni/audit-<doc>.json`
(otisk → [verdikt, pozn]) a při dalším běhu se na ně už neptá.

Ke každému auditovanému výroku jde soudci i člověku render + věta; člověk
navíc odpoví na tvrdou otázku I‑12 („chápu z grafu, proč?“) — podíl „ne“ je
metrika čitelnosti.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

from cb6.memory import Memory, Statement

from bench.judge import Judge, fingerprint

__all__ = ["fingerprint", "wilson", "sample", "run_audit", "human_loop", "load_human", "save_human", "render_for_audit"]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilsonův interval spolehlivosti podílu k/n."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / denom, (centre + half) / denom)


def render_for_audit(m: Memory, st: Statement) -> str:
    """Čitelný výrok pro soudce/člověka: labely místo id (`Memory.render_short`)."""
    return m.render_short(st)


def sample(memory: Memory, n: int, seed: str) -> list[Statement]:
    """Deterministický vzorek znalosti (`knowledge()`, jen `read`; pravidla ne)."""
    pool = sorted((s for s in memory.knowledge() if s.grade == "read" and s.kind not in ("rule", "typing") and s.sentence), key=lambda s: s.id)
    rnd = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16))  # noqa
    if len(pool) <= n:
        return pool
    return sorted(rnd.sample(pool, n), key=lambda s: s.id)


def _sentence_text(m: Memory, st: Statement) -> str:
    """Text zdrojové věty výroku (z uzlu věty, jinak z provenience)."""
    z = m.nodes.get(st.sentence)
    return z.text if z else st.prov.text


def _context(m: Memory, st: Statement, topic: str = "") -> str:
    """Téma dokumentu + předchozí věta (pro nevyslovený podmět a zájmena)."""
    z = m.nodes.get(st.sentence)
    parts = [f"téma textu: {topic}"] if topic else []
    if z:
        try:
            no = int(z.lemma.rsplit("#", 1)[-1])
        except ValueError:
            no = -1
        for n in m.nodes.values():
            if n.kind == "sentence" and n.doc == z.doc and n.lemma.endswith(f"#{no - 1}"):
                parts.append(f"předchozí věta: {n.text}")
                break
    return "; ".join(parts)


def load_human(path: Path) -> dict[str, list[str]]:
    """Lidské odpovědi: otisk → [verdikt, pozn, (chápu z grafu a/n)]."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_human(path: Path, data: dict[str, list[str]]) -> None:
    """Ulož lidské odpovědi (po každé odpovědi — smyčka se dá kdykoli přerušit)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")


def run_audit(memory: Memory, doc: str, judge: Judge | None, human_path: Path, n: int, seed: str, *, topic: str = "") -> dict[str, Any]:
    """Audit jednoho dokumentu.

    Args:
        memory: paměť po ingestu; doc: jméno dokumentu; judge: soudce (nebo None
        = jen lidské odpovědi); human_path: soubor lidských odpovědí; n: velikost
        vzorku; seed: otisk commitu.
    Returns:
        `n`, `judged`, `tvrdí`, `netvrdí`, `částečně`, `unsupported`, `wilson`,
        `human_n`, `human_unsupported`, `agreement`, `judge`, `readable_no_pct`,
        `items` (sid, render, sentence, fp, judge, human).
    """
    human = load_human(human_path)
    items: list[dict[str, Any]] = []
    counts = {"tvrdí": 0, "netvrdí": 0, "částečně": 0}
    judged = 0
    agree = 0
    both = 0
    hcounts = {"tvrdí": 0, "netvrdí": 0, "částečně": 0}
    readable_no = 0
    readable_n = 0
    for st in sample(memory, n, seed):
        render = render_for_audit(memory, st)
        sentence = _sentence_text(memory, st)
        fp = fingerprint(render, sentence)
        row: dict[str, Any] = {"sid": st.id, "render": render, "sentence": sentence, "fp": fp, "judge": None, "human": None,
                               "kind": st.kind, "main": st.kind in ("verb", "copula")}
        if judge is not None:
            try:
                v, note = judge.judge(render, sentence, _context(memory, st, topic))
                row["judge"] = [v, note]
                counts[v] += 1
                judged += 1
            except RuntimeError as exc:
                row["judge"] = None
                row["judge_error"] = str(exc)
                judge = None  # soudce padl — dál bez něj, ale zpráva to řekne
                print(f"bench: soudce selhal ({exc}) — audit pokračuje bez soudce", file=sys.stderr)
        h = human.get(fp)
        if h:
            row["human"] = h
            hcounts[h[0]] += 1
            if len(h) > 2 and h[2]:
                readable_n += 1
                readable_no += h[2] == "n"
            jv = row["judge"]
            if jv:
                both += 1
                agree += jv[0] == h[0]
        items.append(row)
    def rate(c: dict[str, int]) -> tuple[float | None, int]:
        tot = sum(c.values())
        if not tot:
            return None, 0
        return (c["netvrdí"] + 0.5 * c["částečně"]) / tot, tot
    uns, _ = rate(counts)
    huns, hn = rate(hcounts)
    # rozklad podle druhu výroku: hlavní predikace (verb/copula) × vedlejší (nmod/appos/fragment)
    by_kind: dict[str, dict[str, Any]] = {}
    for it in items:
        if not it["judge"]:
            continue
        key = "hlavní" if it["main"] else f"vedlejší:{it['kind']}"
        b = by_kind.setdefault(key, {"tvrdí": 0, "netvrdí": 0, "částečně": 0})
        b[it["judge"][0]] += 1
    for b in by_kind.values():
        u, tot = rate(b)
        b["n"] = tot
        b["unsupported"] = None if u is None else round(u, 3)
    lo, hi = wilson(counts["netvrdí"] + counts["částečně"] // 2, judged) if judged else (0.0, 1.0)
    return {
        "doc": doc, "n": len(items), "judged": judged, **counts,
        "unsupported": None if uns is None else round(uns, 4), "wilson": [round(lo, 4), round(hi, 4)],
        "human_n": hn, "human_unsupported": None if huns is None else round(huns, 4),
        "agreement": round(agree / both, 3) if both else None, "agreement_n": both,
        "judge": getattr(judge, "name", None) if judge is not None else (items and any(i.get("judge") for i in items) and "částečný" or None),
        "readable_no_pct": round(100.0 * readable_no / readable_n, 1) if readable_n else None,
        "by_kind": by_kind,
        "items": items,
    }


def human_loop(items: list[dict[str, Any]], human_path: Path, *, show_graph=None) -> int:
    """Terminálová smyčka pro člověka: 1 = tvrdí · 2 = netvrdí · 3 = částečně ·
    q = konec; po verdiktu ještě „chápu z grafu proč? a/n“ (I‑12). Ukládá po
    každé odpovědi. Vrací počet zodpovězených.

    Args:
        items: položky z `run_audit` (jen ty bez `human` se ptají).
        human_path: soubor odpovědí.
        show_graph: volitelná funkce sid → text (okolí výroku v grafu, `!ukaž`).
    """
    human = load_human(human_path)
    done = 0
    todo = [i for i in items if i["fp"] not in human]
    print(f"{len(todo)} výroků k posouzení ({len(items) - len(todo)} už zodpovězeno). 1=tvrdí 2=netvrdí 3=částečně q=konec")
    for i, it in enumerate(todo, 1):
        print(f"\n[{i}/{len(todo)}] VĚTA: {it['sentence']}\n        VÝROK: {it['render']}")
        if show_graph is not None:
            try:
                print("        GRAF:  " + show_graph(it["sid"]).replace("\n", "\n               "))
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        while True:
            ans = input("        verdikt> ").strip().lower()
            if ans in ("q", "quit", "konec"):
                save_human(human_path, human)
                return done
            if ans in ("1", "2", "3"):
                break
        v = {"1": "tvrdí", "2": "netvrdí", "3": "částečně"}[ans]
        readable = input("        chápu z grafu proč? (a/n, enter=přeskočit)> ").strip().lower()
        note = input("        pozn (enter=nic)> ").strip()
        human[it["fp"]] = [v, note, readable if readable in ("a", "n") else ""]
        save_human(human_path, human)
        done += 1
    return done
