"""Audit grafu — jen nad exportem `Memory.graph()` (I‑11, I‑12).

Proč bez přístupu k jádru: kdyby audit sahal do Python objektů paměti, měřil
by, co si jádro myslí, ne co je v grafu. Tady dostane `networkx.MultiDiGraph`
a nic víc; když v něm chybí cesta k větě, hrana pravidla nebo krok uzávěru,
je to porušení — bez ohledu na to, co jádro „ví“ jinde.

Kontroly (`check_graph`, spec § 5.7):
    provenience – každý výrok má `source` → věta → (`part_of`)* → dokument
    derivace    – `grade == derived` má `derived_from` + `uses_rule` a premisy jsou SAFE
    status      – `REJECTED` má `reason`; `HYPOTHESIS` má `alternative_of` nebo `alternatives` prázdné jen u pro‑drop (tolerováno)
    osiřelost   – term bez `mention` i bez `role:*`; věta bez `source`/`residue_of`/`mention`
    open        – uzel `open` má `about`
`check_answer` ověří odpověď: výroky důkazu existují, jsou znalost
(claim SAFE, mood assert, grade read/said/derived), mají provenienci; každý
tvrdý krok (`member`/`subset`/`within`/`same_as`/`time`/`disjoint`) je cesta
po hranách daného typu (BFS), obsažení časů z atributů `t_start`/`t_end`,
disjunkce existence hrany `disjoint` mezi nadtřídami.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable

import networkx as nx

TERM_KINDS = ("entity", "group", "place", "time", "value")
KNOWLEDGE_GRADES = ("read", "said", "derived")


@dataclass(frozen=True)
class Violation:
    """Jedno porušení: která kontrola, který uzel, detail."""

    check: str
    node: str
    detail: str


def _out(g: nx.MultiDiGraph, n: str, etype: str) -> list[str]:
    return [v for _, v, d in g.out_edges(n, data=True) if d.get("type") == etype]


def _in(g: nx.MultiDiGraph, n: str, etype: str) -> list[str]:
    return [u for u, _, d in g.in_edges(n, data=True) if d.get("type") == etype]


def _has_in_prefix(g: nx.MultiDiGraph, n: str, prefix: str) -> bool:
    return any(str(d.get("type", "")).startswith(prefix) for _, _, d in g.in_edges(n, data=True))


def _reaches_document(g: nx.MultiDiGraph, sentence: str) -> bool:
    seen = set()
    q = deque([sentence])
    while q:
        n = q.popleft()
        if n in seen:
            continue
        seen.add(n)
        if g.nodes[n].get("kind") == "document":
            return True
        q.extend(_out(g, n, "part_of"))
    return False


def check_graph(g: nx.MultiDiGraph) -> list[Violation]:
    """Projdi celý graf a vrať porušení (prázdný seznam = čistý graf)."""
    out: list[Violation] = []
    for n, d in g.nodes(data=True):
        kind = d.get("kind")
        if kind == "statement":
            if d.get("life", "active") != "active":
                continue
            src = _out(g, n, "source")
            if not src:
                out.append(Violation("provenience", n, "výrok bez hrany source"))
            elif not any(_reaches_document(g, s) for s in src):
                out.append(Violation("provenience", n, "věta nevede na dokument (part_of)"))
            if d.get("grade") == "derived":
                prem = _out(g, n, "derived_from")
                rules = _out(g, n, "uses_rule")
                if not prem or not rules:
                    out.append(Violation("derivace", n, "odvozený výrok bez derived_from/uses_rule"))
                for p in prem:
                    pd = g.nodes.get(p, {})
                    if pd.get("kind") == "statement" and (pd.get("claim") != "SAFE" or pd.get("mood", "assert") != "assert"):
                        out.append(Violation("derivace", n, f"premisa {p} není SAFE tvrzení"))
            if d.get("claim") == "REJECTED" and not d.get("reason"):
                out.append(Violation("status", n, "REJECTED bez důvodu"))
        elif kind in TERM_KINDS:
            if not _in(g, n, "mention") and not _has_in_prefix(g, n, "role:") and not _out(g, n, "restricts") and not _in(g, n, "restricts"):
                out.append(Violation("osiřelost", n, f"{kind} bez zmínky i bez role"))
        elif kind == "sentence":
            if not _in(g, n, "source") and not _in(g, n, "residue_of") and not _out(g, n, "mention"):
                out.append(Violation("osiřelost", n, "věta bez výroku, zbytku i zmínky"))
        elif kind == "open":
            if not _out(g, n, "about"):
                out.append(Violation("open", n, "otevřená položka bez about"))
    return out


def hard_path(g: nx.MultiDiGraph, kernel: str, a: str, b: str) -> list[str] | None:
    """Cesta po tvrdých hranách daného jádra z `a` do `b` (BFS), nebo `None`.

    `member`: první hrana `member`, dál `subset`/`restricts`; `subset`:
    `subset`/`restricts`; `within`: `within` (+ `same_as` obousměrně);
    `same_as`: obousměrně. Triviální `a == b` je prázdná cesta.
    """
    if a == b:
        return [a]
    if a not in g or b not in g:
        return None

    def nexts(n: str, first: bool) -> Iterable[str]:
        for _, v, d in g.out_edges(n, data=True):
            t = d.get("type")
            if kernel == "member":
                if (first and t == "member") or (not first and t in ("subset", "restricts")):
                    yield v
            elif kernel == "subset":
                if t in ("subset", "restricts"):
                    yield v
            elif kernel == "within":
                if t in ("within", "same_as"):
                    yield v
            elif kernel == "same_as":
                if t == "same_as":
                    yield v
        if kernel in ("same_as", "within"):
            for u, _, d in g.in_edges(n, data=True):
                if d.get("type") == "same_as":
                    yield u

    prev: dict[str, str | None] = {a: None}
    q: deque[tuple[str, bool]] = deque([(a, True)])
    while q:
        n, first = q.popleft()
        for v in nexts(n, first):
            if v in prev:
                continue
            prev[v] = n
            if v == b:
                path = [b]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])  # type: ignore[arg-type]
                return list(reversed(path))
            q.append((v, False))
    return None


def _time_within(g: nx.MultiDiGraph, a: str, b: str) -> bool:
    """Bod/interval `a` leží v intervalu `b` (z atributů `t_start`/`t_end`)."""
    da, db = g.nodes.get(a, {}), g.nodes.get(b, {})
    sa, ea = da.get("t_start"), da.get("t_end") or da.get("t_start")
    sb, eb = db.get("t_start"), db.get("t_end") or db.get("t_start")
    if not sa or not sb:
        return False
    def norm(t: list[int], end: bool) -> tuple[int, int, int]:
        t = list(t) + ([12, 31] if end else [1, 1])[len(t) - 1:] if len(t) < 3 else list(t)
        return (int(t[0]), int(t[1]), int(t[2]))
    return norm(sb, False) <= norm(sa, False) and norm(ea, True) <= norm(eb, True)


def _disjoint(g: nx.MultiDiGraph, a: str, b: str) -> bool:
    for u, v, d in g.edges(data=True):
        if d.get("type") != "disjoint":
            continue
        if (hard_path(g, "subset", a, u) and hard_path(g, "subset", b, v)) or (hard_path(g, "subset", b, u) and hard_path(g, "subset", a, v)):
            return True
    return False


def check_answer(g: nx.MultiDiGraph, proof_statement_ids: list[str], hard_steps: list[tuple[str, str, str]]) -> list[Violation]:
    """Ověř, že odpověď je rekonstruovatelná z grafu (I‑12).

    Args:
        g: export paměti; proof_statement_ids: id výroků z důkazu (včetně
            výroků uzávěrů); hard_steps: tvrdé kroky `(jádro, a, b)`.
    Returns:
        Porušení: `status` (výrok není znalost), `provenience` (bez source),
        `rekonstrukce` (krok není cesta v grafu / čas nesedí / disjunkce chybí).
    """
    out: list[Violation] = []
    for sid in proof_statement_ids:
        d: dict[str, Any] = g.nodes.get(sid, {})
        if d.get("kind") != "statement":
            out.append(Violation("rekonstrukce", sid, "výrok důkazu není v grafu"))
            continue
        if d.get("claim") != "SAFE" or d.get("mood", "assert") != "assert" or d.get("grade") not in KNOWLEDGE_GRADES or d.get("life", "active") != "active":
            out.append(Violation("status", sid, f"výrok důkazu není znalost (claim={d.get('claim')}, mood={d.get('mood')}, grade={d.get('grade')})"))
        if not _out(g, sid, "source"):
            out.append(Violation("provenience", sid, "výrok důkazu bez source"))
    for kernel, a, b in hard_steps:
        ok = False
        if kernel in ("member", "subset", "within", "same_as"):
            ok = hard_path(g, kernel, a, b) is not None
        elif kernel == "time":
            ok = _time_within(g, a, b)
        elif kernel == "disjoint":
            ok = _disjoint(g, a, b)
        if not ok:
            out.append(Violation("rekonstrukce", a, f"krok {kernel}({a}, {b}) není v grafu"))
    return out
