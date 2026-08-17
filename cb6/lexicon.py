"""Lexikon znalostních vazeb — vazby jako DATA, operátory v kódu, použití v grafu.

Proč (návrh `docs/superpowers/specs/2026-08-17-znalostni-vazby-design.md`):
do 17. 8. žily „vazby“ na čtyřech místech (`defaults.SYNONYMS`, `Memory.learned`,
`Memory.rules`, výroky `kind="rule"`) a jen poslední mělo provenienci v grafu.
Tenhle modul je *jedno* místo: každá vazba je jeden řádek
`{id, op, args, síla, autorita, zdroj, pozn}`; operátor je malá uzavřená
množina funkcí v kódu; použitý řádek se **líně materializuje do grafu** jako
uzel `kind="vazba"` (I‑11/I‑12 — odpověď je rekonstruovatelná z exportu).

Dnes v kódu: `třída` (ekvivalence — symetrická, tranzitivní), `implikace`
(jednosměrná: `p ⇒ q`; fakt `p` odpovídá na otázku `q`, ne naopak) a
`podřazení` (`x ⊆ y` nad lemmaty skupin: kdo je *drama*, je *dílo*; orientované,
tranzitivní — technicky implikace nad třídami, zvlášť jen kvůli čitelnosti
řádku a grafu). Ostatní operátory (`protiklad`, `inverze`, `skládání`,
`překryv`, `porovnání`) jsou vyjmenované, ale zatím bez kódu — řádek s nimi se
načte a hlídá, jen se neuplatní.

Síla: `same` (zaměnitelné ve verdiktu), `implies` (jednosměrné, ve verdiktu
jako odvození), `related` (jen pro recall / nápovědu — **nikdy ve verdiktu**).
Autorita: `seed` (soubory `cb6/lexikon/*.jsonl` v repu), `said` (`!uč` v
dialogu), `read` (věta typu „X je synonymum Y“ — zatím nečteme), `derived`.
Bez `zdroj` řádek neexistuje.
"""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Sequence

if TYPE_CHECKING:  # pragma: no cover — jen typy, žádný běhový import (memory importuje lexicon)
    from cb6.memory import Memory

#: Osm operátorů návrhu (§ 1.1). Kód dnes umí `třída`, `implikace`, `podřazení`; ostatní jsou rezervované.
OPS = ("třída", "implikace", "protiklad", "inverze", "skládání", "podřazení", "překryv", "porovnání")
STRENGTHS = ("same", "implies", "related")
AUTHORITIES = ("seed", "said", "read", "derived")

#: Adresář seed souborů (`*.jsonl`, jeden řádek = jedna vazba).
SEED_DIR = Path(__file__).parent / "lexikon"

#: Nejdelší řetěz vazeb, který shoda predikátů projde (kázat ⇒ hlásat ⇒ říci ~ říkat…).
MAX_CHAIN = 4

_SEED_ENABLED = True


def set_seed_enabled(enabled: bool) -> None:
    """Zapni/vypni seed vrstvu (ablace `bench run --bez-lexikonu`).

    Proč globálně: bench je jeden proces a ablace má ukázat, co seed vrstva
    přináší; řádky `said` v paměti zůstávají vždy.
    Vstup: `enabled`. Výstup: nic (mění stav modulu)."""
    global _SEED_ENABLED  # pylint: disable=global-statement
    _SEED_ENABLED = enabled


@dataclass(frozen=True)
class Link:
    """Jeden řádek lexikonu — vazba s operátorem, silou a proveniencí.

    Atributy anglicky jako zbytek jádra (`grade`, `claim`…); JSON klíče
    česky podle návrhu (`síla`, `autorita`, `zdroj`, `pozn`), protože soubory
    píše a čte člověk."""

    id: str
    op: str
    args: tuple[str, ...]
    strength: str
    authority: str
    source: str
    note: str = ""

    def to_json(self) -> dict[str, Any]:
        """Řádek do JSON (české klíče návrhu). Vstup: self. Výstup: dict."""
        return {"id": self.id, "op": self.op, "args": list(self.args), "síla": self.strength,
                "autorita": self.authority, "zdroj": self.source, "pozn": self.note}

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> "Link":
        """Řádek z JSON (české i anglické klíče — kvůli starším paměťovým souborům).
        Vstup: dict. Výstup: `Link` (bez validace — tu dělá `Lexicon`)."""
        return cls(
            id=str(d["id"]), op=str(d["op"]), args=tuple(str(a) for a in d.get("args", [])),
            strength=str(d.get("síla", d.get("strength", "same"))),
            authority=str(d.get("autorita", d.get("authority", "seed"))),
            source=str(d.get("zdroj", d.get("source", ""))),
            note=str(d.get("pozn", d.get("note", ""))),
        )

    def label(self) -> str:
        """Čitelný popisek pro graf a důkaz: `a ~ b` (same), `a ⇒ b` (implies), `a ≈ b` (related)."""
        sym = {"same": "~", "implies": "⇒", "related": "≈"}.get(self.strength, "?")
        if self.op == "podřazení" and self.strength == "implies":
            sym = "⊆"
        return f" {sym} ".join(self.args)

    def validate(self) -> None:
        """Hlídač formátu: známý operátor, síla, autorita, dva argumenty, zdroj.
        Proč přísně: řádek bez zdroje by v grafu neměl provenienci (I‑12);
        `třída`+`implies` nebo `implikace`+`same` je logický nesmysl.
        Vstup: self. Výstup: nic; `ValueError` při chybě."""
        if self.op not in OPS:
            raise ValueError(f"{self.id}: neznámý operátor {self.op!r}")
        if self.strength not in STRENGTHS:
            raise ValueError(f"{self.id}: neznámá síla {self.strength!r}")
        if self.authority not in AUTHORITIES:
            raise ValueError(f"{self.id}: neznámá autorita {self.authority!r}")
        if not self.source:
            raise ValueError(f"{self.id}: řádek bez zdroje")
        if self.op in ("třída", "implikace", "podřazení") and len(self.args) != 2:
            raise ValueError(f"{self.id}: {self.op} chce dva argumenty, má {len(self.args)}")
        if self.op == "třída" and self.strength == "implies":
            raise ValueError(f"{self.id}: třída nemůže mít sílu implies (použij implikace)")
        if self.op in ("implikace", "podřazení") and self.strength == "same":
            raise ValueError(f"{self.id}: {self.op} nemůže mít sílu same (použij třída)")


@dataclass(frozen=True)
class LexMatch:
    """Výsledek shody predikátů: použité řádky (řetěz od faktu k dotazu), popis
    kroku pro důkaz a příznak `derived` (řetěz obsahuje implikaci → odvození)."""

    links: tuple[Link, ...]
    step: str
    derived: bool


@lru_cache(maxsize=4)
def load_seed(directory: Path = SEED_DIR) -> tuple[Link, ...]:
    """Načti seed řádky ze všech `*.jsonl` v adresáři (kešované — soubory se
    za běhu nemění). Prázdné řádky a `#` komentáře se přeskočí; chybějící
    `zdroj` se doplní jako `soubor#řádek`.
    Vstup: adresář. Výstup: n‑tice `Link` (validované, id unikátní)."""
    out: list[Link] = []
    seen: set[str] = set()
    for path in sorted(Path(directory).glob("*.jsonl")):
        rel = f"cb6/lexikon/{path.name}"
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            d = json.loads(s)
            d.setdefault("zdroj", f"{rel}#{no}")
            d.setdefault("autorita", "seed")
            link = Link.from_json(d)
            link.validate()
            if link.id in seen:
                raise ValueError(f"{rel}#{no}: duplicitní id {link.id}")
            seen.add(link.id)
            out.append(link)
    return tuple(out)


class Lexicon:
    """Operátory nad množinou řádků: `třída` = union‑find (reprezentant),
    `implikace` = orientované hrany; shoda predikátů = cesta od faktu k dotazu
    přes hrany `same` (oběma směry) a `implies` (po směru), nejvýš `MAX_CHAIN`.

    Postaví se za mikrosekundy (řádků jsou stovky), proto vzniká na každý
    `Evaluator` znovu — sdílený stav mezi pamětmi by byl chyba (dvě paměti se
    nesmějí ovlivnit; řádky `said` patří jedné paměti)."""

    def __init__(self, rows: Iterable[Link]) -> None:
        self.rows: dict[str, Link] = {}
        #: predikát → [(soused, řádek, směr_ok)] — `same` oběma směry, `implies` jen a→b
        self._adj: dict[str, list[tuple[str, Link]]] = {}
        #: pro `related`: sousedé přes jakoukoli sílu, neorientovaně
        self._loose: dict[str, set[str]] = {}
        self._parent: dict[str, str] = {}
        self._memo: dict[tuple[str, str], LexMatch | None] = {}
        for link in rows:
            link.validate()
            if link.id in self.rows:
                raise ValueError(f"duplicitní id {link.id}")
            self.rows[link.id] = link
            if link.op not in ("třída", "implikace", "podřazení"):
                continue  # rezervované operátory: řádek držíme, kód zatím nemá
            a, b = link.args
            self._loose.setdefault(a, set()).add(b)
            self._loose.setdefault(b, set()).add(a)
            if link.strength == "related":
                continue
            if link.op == "třída":
                self._adj.setdefault(a, []).append((b, link))
                self._adj.setdefault(b, []).append((a, link))
                self._union(a, b)
            else:
                self._adj.setdefault(a, []).append((b, link))
                self._adj.setdefault(b, [])
        for lst in self._adj.values():
            lst.sort(key=lambda x: (x[1].id, x[0]))  # determinismus cest

    # ---- stavba -----------------------------------------------------------------

    @classmethod
    def for_memory(cls, memory: "Memory") -> "Lexicon":
        """Lexikon pro danou paměť: seed (pokud není ablace) + řádky, které paměť
        drží (`said` z dialogu, dřív materializované). Vstup: paměť. Výstup: `Lexicon`."""
        rows: dict[str, Link] = {}
        if _SEED_ENABLED:
            for link in load_seed():
                rows[link.id] = link
        for link in memory.links.values():
            rows[link.id] = link  # paměť má přednost (týž id = tentýž řádek)
        return cls(rows.values())

    def _find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def _union(self, a: str, b: str) -> None:
        ra, rb = self._find(a), self._find(b)
        if ra != rb:
            self._parent[max(ra, rb)] = min(ra, rb)

    # ---- operátory --------------------------------------------------------------

    def rep(self, pred: str) -> str:
        """Reprezentant třídy `same` (nebo predikát sám). Vstup: predikát. Výstup: reprezentant."""
        return self._find(pred) if pred in self._parent else pred

    def match(self, pattern: str, fact: str) -> LexMatch | None:
        """Sedí predikát faktu `fact` na predikát dotazu/vzoru `pattern`?

        Proč směr: `bydlet ⇒ žít` znamená, že výrok „bydlí v Praze“ odpovídá
        na „Kde žije?“, ale „žil v Praze“ neodpovídá na „Kde bydlí?“. Cesta
        vede od faktu k dotazu po `same` (oběma směry) a `implies` (po směru).
        Vstup: `pattern` (dotaz/podmínka), `fact` (výrok). Výstup: `LexMatch`
        (u shody bez řádků prázdný řetěz) nebo `None`."""
        if pattern == fact:
            return LexMatch((), "", False)
        if fact not in self._adj or pattern not in self._adj:
            return None
        key = (pattern, fact)
        if key in self._memo:
            return self._memo[key]
        result: LexMatch | None = None
        prev: dict[str, tuple[str, Link] | None] = {fact: None}
        queue: deque[tuple[str, int]] = deque([(fact, 0)])
        while queue:
            node, depth = queue.popleft()
            if node == pattern:
                chain: list[Link] = []
                cur = node
                while prev[cur] is not None:
                    p, link = prev[cur]  # type: ignore[misc]
                    chain.append(link)
                    cur = p
                chain.reverse()
                derived = any(l.strength == "implies" for l in chain)
                ids = ", ".join(l.id for l in chain)
                if all(l.op == "podřazení" for l in chain):
                    head, sym = "podřazení", "⊆"
                else:
                    head = "implikace" if derived else "synonymum"
                    sym = "⇒" if derived else "~"
                result = LexMatch(tuple(chain), f"{head}: {fact} {sym} {pattern} [{ids}]", derived)
                break
            if depth >= MAX_CHAIN:
                continue
            for nxt, link in self._adj.get(node, ()):
                if nxt not in prev:
                    prev[nxt] = (node, link)
                    queue.append((nxt, depth + 1))
        self._memo[key] = result
        return result

    def related(self, a: str, b: str) -> bool:
        """Jsou predikáty jakkoli spojené (same/implies/related, bez ohledu na
        směr, do `MAX_CHAIN` kroků)? Jen pro recall/nápovědu — nikdy pro verdikt.
        Vstup: dva predikáty. Výstup: bool."""
        if a == b:
            return True
        if a not in self._loose or b not in self._loose:
            return False
        seen = {a}
        frontier = {a}
        for _ in range(MAX_CHAIN):
            nxt: set[str] = set()
            for x in frontier:
                for y in self._loose.get(x, ()):
                    if y == b:
                        return True
                    if y not in seen:
                        seen.add(y)
                        nxt.add(y)
            frontier = nxt
            if not frontier:
                break
        return False


_TEACH = re.compile(r"^(\S+)\s*(=>|=|~|<)\s*(\S+)$")


def parse_teach(arg: str) -> tuple[str, tuple[str, str], str] | None:
    """Zápis dialogu: `!uč a = b` (třída/same), `!uč a => b` (implikace/implies),
    `!uč a ~ b` (třída/related), `!uč a < b` (podřazení: a ⊆ b, implies).
    Vstup: text za příkazem. Výstup: `(op, args, síla)` nebo `None`."""
    mt = _TEACH.match(arg.strip())
    if not mt:
        return None
    a, sym, b = mt.groups()
    if sym == "=>":
        return "implikace", (a, b), "implies"
    if sym == "<":
        return "podřazení", (a, b), "implies"
    if sym == "=":
        return "třída", (a, b), "same"
    return "třída", (a, b), "related"


def links_for_graph(links: Sequence[Link]) -> list[tuple[str, dict[str, Any]]]:
    """Uzly `kind="vazba"` pro export grafu (atributy = řádek + popisek).
    Vstup: řádky. Výstup: seznam `(id, atributy)` pro `add_node`."""
    out: list[tuple[str, dict[str, Any]]] = []
    for l in links:
        out.append((l.id, {"kind": "vazba", "label": l.label(), "op": l.op, "args": list(l.args),
                           "síla": l.strength, "autorita": l.authority, "zdroj": l.source, "pozn": l.note,
                           "activation": 0.0}))
    return out
