"""Diskurz: registr referentů jako čtecí pohled nad grafem (spec conbond6 § 4).

Zásada z inventury conbond0–4: **aktivace řadí, identita žije v registru.**
Registr ale není tabulka vedle grafu (I‑11) — je to jen pohled nad hranami
`mention` (věta → uzel; role, tvar, segment), které zapisuje zakotvení, a nad
atributy uzlů (rod, číslo). Rozhodnutí koreference se pak dá z grafu
dohledat: hrana `mention` z věty se zájmenem na zvolený uzel + výchozí volba
„koref: registr“ na výroku; alternativy jsou `HYPOTHESIS` výroky
s `alternative_of` (I‑3, I‑8).

Kandidáti pro zájmeno / nevyslovený podmět: uzly se zmínkou v tomto nebo
předchozím segmentu (bez segmentů: celý dokument), se shodou rodu a čísla;
řazení: aktivace ↓ → poslední role (podmět > předmět > ostatní) → čerstvost
(číslo věty ↓) → id.
"""

from __future__ import annotations

from dataclasses import dataclass

from cb6.memory import Memory, Node

ROLE_RANK = {"kdo": 0, "co": 1}


@dataclass
class Candidate:
    """Kandidát koreference s pořadím a zdůvodněním (jde do `defaults`)."""

    node: Node
    activation: float
    last_role: str
    last_sentence: int
    segment: str

    def key(self) -> tuple[float, int, int, str]:
        """Řadicí klíč: aktivace ↓, role (podmět první), čerstvost ↓, id."""
        return (-self.activation, ROLE_RANK.get(self.last_role, 2), -self.last_sentence, self.node.id)


class Registry:
    """Čtecí pohled nad zmínkami v paměti (`Memory.mentions`)."""

    def __init__(self, memory: Memory) -> None:
        self.m = memory

    def _sentence_no(self, sentence_id: str) -> int:
        n = self.m.nodes.get(sentence_id)
        if n is None:
            return -1
        try:
            return int(n.lemma.rsplit("#", 1)[-1])
        except ValueError:
            return -1

    def previous_segment(self, segment: str) -> str | None:
        """Předchozí segment téhož dokumentu (podle pořadí vzniku), nebo None."""
        seg = self.m.nodes.get(segment)
        if seg is None:
            return None
        segs = [n for n in self.m.nodes.values() if n.kind == "segment" and n.doc == seg.doc]
        segs.sort(key=lambda n: n.id)
        for i, n in enumerate(segs):
            if n.id == segment and i > 0:
                return segs[i - 1].id
        return None

    def candidates(self, *, gender: str | None, number: str | None, segment: str | None,
                   kinds: tuple[str, ...] = ("entity",)) -> list[Candidate]:
        """Kandidáti pro zájmeno / nevyslovený podmět.

        Args:
            gender, number: rysy zájmena (None = neomezuje); segment: aktuální
            segment (None = celý dokument); kinds: druhy uzlů (entity, place).
        Returns:
            Kandidáti seřazení od nejlepšího (viz docstring modulu).
        """
        allowed_segments: set[str] | None = None
        if segment:
            allowed_segments = {segment}
            prev = self.previous_segment(segment)
            if prev:
                allowed_segments.add(prev)
        last: dict[str, tuple[str, int, str]] = {}  # node -> (role, sentence_no, segment)
        for sent, node, role, _form, seg in self.m.mentions:
            n = self.m.nodes.get(node)
            if n is None or n.kind not in kinds:
                continue
            if allowed_segments is not None and seg and seg not in allowed_segments:
                continue
            no = self._sentence_no(sent)
            cur = last.get(node)
            if cur is None or no >= cur[1]:
                # při stejné větě vyhrává lepší role
                if cur is not None and no == cur[1] and ROLE_RANK.get(cur[0], 2) <= ROLE_RANK.get(role, 2):
                    continue
                last[node] = (role, no, seg)
        out: list[Candidate] = []
        for node_id, (role, no, seg) in last.items():
            n = self.m.nodes[node_id]
            if gender and n.gender and gender not in n.gender.split(","):
                continue
            if number and n.number and number != n.number:
                continue
            out.append(Candidate(n, self.m.activation(node_id), role, no, seg))
        out.sort(key=Candidate.key)
        return out

    def last_mention(self, node_id: str) -> tuple[str, str, str] | None:
        """(věta, role, tvar) poslední zmínky uzlu, nebo None."""
        best_no = -2
        best: tuple[str, str, str] | None = None
        for sent, node, role, form, _seg in self.m.mentions:
            if node != node_id:
                continue
            no = self._sentence_no(sent)
            if no >= best_no:
                best_no = no
                best = (sent, role, form)
        return best


def ambiguous(cands: list[Candidate], *, ratio: float = 0.6) -> bool:
    """Jsou první dva kandidáti tak blízko, že by volba byla hádání (I‑8)?
    Ano, když druhý má aspoň `ratio`× aktivaci prvního (a stejnou nebo lepší roli)."""
    if len(cands) < 2:
        return False
    a, b = cands[0], cands[1]
    if a.activation <= 0:
        return True
    return b.activation >= ratio * a.activation
