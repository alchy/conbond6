"""QA v benchi: shoda odpovědi s očekáváním, rozklad chyb, kotva pro dosah.

Převzato z conbond5 `cb5/bench.py` (tam ověřené na 722 otázkách) a doplněno
o kotvu: dosah otázky = vzdálenost věty s odpovědí od poslední věty, kde je
téma jmenováno plným jménem (spec § 5.5). To je metr pro diskurzovou vrstvu.
"""

from __future__ import annotations

import re
import unicodedata

from cb6.memory import Memory
from cb6.render import describe_node


def norm(s: str) -> str:
    """NFC, malá písmena, sbalené mezery."""
    s = unicodedata.normalize("NFC", s).lower().strip()
    return re.sub(r"\s+", " ", s)


def years(s: str) -> set[str]:
    """Letopočty v řetězci (1000–2099)."""
    return set(re.findall(r"\b(1\d{3}|20\d{2})\b", s))


def tokens(s: str) -> list[str]:
    """Hrubá tokenizace pro porovnání odpovědi (bez interpunkce)."""
    return [t for t in re.split(r"[\s.,;:()–\-]+", norm(s)) if t]


def answer_matches(memory: Memory, expect: list[str], fillers: list[str], text: str) -> tuple[bool, bool]:
    """(sedí výplň, sedí aspoň text odpovědi).

    Výplň sedí, když očekávaný řetězec (nebo jeho letopočet, nebo všechny
    jeho tokeny s tolerancí koncovky) je mezi jmény/popiskou některé výplně.
    `text_hit` je horní mez: očekávaný řetězec je aspoň v renderu odpovědi.

    Args:
        memory: paměť po ingestu; expect: očekávané řetězce; fillers: id uzlů
            (nebo `count:N`) z verdiktu; text: vyrenderovaná odpověď.
    Returns:
        (hit, text_hit)
    """
    labels: list[str] = []
    for f in fillers:
        if f.startswith("count:"):
            labels.append(f.split(":", 1)[1])
            continue
        n = memory.nodes.get(f)
        if n is None:
            continue
        labels.append(describe_node(memory, f))
        labels.extend(n.names)
        if n.time is not None:
            labels.append(n.time.label)
        if n.kind == "entity" and n.base:
            labels.append(memory.nodes[n.base].lemma)
    norm_labels = [norm(x) for x in labels]
    hit = False
    for e in expect:
        en = norm(e)
        ey = years(en)
        for lab in norm_labels:
            if en == lab or en in lab or lab in en and len(lab) > 3:
                hit = True
            if ey and ey & years(lab):
                hit = True
            et = tokens(en)
            if et and all(any(t == w or (len(t) > 4 and (w.startswith(t[:-2]) or t.startswith(w[:-2]))) for w in tokens(lab)) for t in et):
                hit = True
    text_hit = any(norm(e) in norm(text) or (years(e) and years(e) & years(text)) for e in expect)
    return hit, text_hit


def classify_miss(verdict: object) -> str:
    """Proč otázka neprošla — hrubý rozklad podle verdiktu (stejné kategorie
    jako conbond5, aby se čísla dala srovnat)."""
    if verdict is None:
        return "nepřečteno"
    v = verdict
    if getattr(v, "fillers", None):
        return "špatná výplň"
    missing = list(getattr(v, "missing", []))
    if any("nevím nic" in x for x in missing):
        return "entita neznámá"
    if any("nemám žádný výrok" in x for x in missing):
        return "predikát chybí"
    if getattr(v, "near", None):
        return "role/logika (blízký výrok je)"
    return "bez výroku"


def anchor_words(question: str, topic: str) -> list[str]:
    """Kotva pro dosah: slova s velkým písmenem uvnitř otázky (jména), jinak
    téma dokumentu. Hrubé, ale deterministické; stačí na pásma dosahu."""
    ws = [w.strip("?,.!;:„“\"'()") for w in question.split()]
    caps = [w for i, w in enumerate(ws) if i > 0 and w[:1].isupper() and len(w) > 1]
    if caps:
        return caps
    return [w for w in topic.split() if w]


def find_answer_sentence(sentences: list[tuple[int, str]], expect: list[str]) -> int | None:
    """Číslo první věty (v našem číslování), která obsahuje očekávanou odpověď
    (řetězec nebo letopočet). `None`, když odpověď v textu není."""
    for no, text in sentences:
        nt = norm(text)
        for e in expect:
            if norm(e) in nt or (years(e) and years(e) & years(text)):
                return no
    return None


def last_anchor_sentence(sentences: list[tuple[int, str]], upto: int, anchor: list[str]) -> int | None:
    """Poslední věta ≤ `upto`, kde je kotva (všechna slova jména, s tolerancí
    koncovky — „Jiráska“ ~ „Jirásek“)."""
    stems = [norm(a)[:-1] if len(a) > 4 else norm(a) for a in anchor]
    if not stems:
        return None
    for no, text in reversed([s for s in sentences if s[0] <= upto]):
        nt = norm(text)
        if all(st in nt for st in stems):
            return no
    return None
