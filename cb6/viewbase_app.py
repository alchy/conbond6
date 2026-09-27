"""Konverzace nad živým grafem ve viewBase2 (volitelný adaptér).

    pip install -e /Users/j/Projects/viewBase2/python     # viewbase (github.com/alchy/viewBase2)
    python -m cb6.viewbase_app [--pamet p.json] [--port 8080] [--user workbench]

Model viewBase2: `Project` (služba, port) → `Screen` (plocha) → okna:
`GraphWindow` (živý 3D graf, fyzika v prohlížeči, oblasti podle metadata
`skupina` = dokument), `TerminalWindow` (dialog), `LogWindow`, detailní okno
na klik.

Proč: paměť conbond6 JE graf (spec § 3, I‑11) a člověk má vidět, čím systém
myslí. Adaptér drží mimo jádro: po každém tahu se rozdíl paměti promítne
do plátna (`ensure_node`/`ensure_edge`), aktivace se ukáže jako
`highlight`, a konzole v prohlížeči (`TerminalWindow`) je tentýž dialog
jako `python -m cb6 chat`. Klik na uzel otevře detail s výroky.

Typy uzlů: entita, group (i zúžená), místo, čas, výrok. Tvrdé hrany jsou
role a jádrové relace; měkké (spoluvýskyt) se kreslí tence a jinou barvou,
aby bylo vidět, co nese pravdivost a co jen aktivaci (I‑8).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from cb6.dialog import Session
from cb6.memory import Memory
from cb6.oracle import live_or_recorded
from cb6.render import describe_node, render_statement

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "cache" / "parses.json"

#: Uživatel viewBase2 pro tenhle projekt. Je součástí konfigurace (v gitu),
#: tajemství NE: TOTP tajemství a QR pro něj vzniknou při první instanciaci
#: v `~/.viewbase/user-<jméno>/` (0600) — právě proto, aby se nedostaly do
#: repozitáře. Odemyká zabezpečená okna (`secured=True`), viz README viewBase2.
VIEWBASE_USER = "workbench"

TYPES = {
    "entity": dict(shape="sphere", color="#28d7fe", size=1.4),
    "group": dict(shape="box", color="#7bd389", size=1.2),
    "place": dict(shape="octahedron", color="#ffb347", size=1.3),
    "time": dict(shape="box", color="#c9c9c9", size=0.9),
    "value": dict(shape="box", color="#c9c9c9", size=0.8),
    "statement": dict(shape="sphere", color="#ff2a6d", size=0.7),
    "statement_said": dict(shape="sphere", color="#ff5fa2", size=0.8),
    "statement_hypothesis": dict(shape="sphere", color="#ffd166", size=0.6),
    "statement_rejected": dict(shape="sphere", color="#666666", size=0.5),
    "statement_pattern": dict(shape="sphere", color="#9b5de5", size=0.5),
    #: řádek lexikonu (znalostní vazba), materializovaný při použití — provenience v atributu `zdroj`
    "vazba": dict(shape="box", color="#4cc9f0", size=0.6),
}
#: Uzly, které v živém pohledu nezobrazujeme (jsou v grafu kvůli auditu a
#: introspekci — `!ukaž`, bench/graphcheck): věty, dokumenty, segmenty,
#: otevřené položky. Odvolané výroky také ne.
HIDDEN_KINDS = ("sentence", "document", "segment", "open")


def build(session: Session, *, title: str = "conbond6", port: int = 8080,
          user: str = VIEWBASE_USER) -> tuple[Any, Any]:
    """Postav projekt viewBase2: screen s grafovým oknem, konzolí (dialog) a log oknem.

    Args:
        session: sezení nad pamětí (graf se z ní promítá po každém tahu).
        title: titulek; port: port služby (Project ho potřebuje před vším).
        user: uživatel viewBase2 (odemyká zabezpečená okna; tajemství a QR
            vzniknou při prvním startu v ~/.viewbase/, do gitu nejdou).
    Returns:
        (project, screen) — volající zavolá `project.serve(screen, …)`.
    """
    import viewbase as vb  # type: ignore[import-not-found]

    project = vb.Project(port=port, user=user)
    screen = vb.Screen(title=title, theme="cyber")
    graph = vb.GraphWindow(screen=screen, title=f"{title} — graf paměti", dimensions=3, theme="cyber", highlight_neighbors=1)
    vb.LogWindow(screen=screen)
    for name, style in TYPES.items():
        graph.define_type(name, **style)
    graph.define_type("soft", color="#333333", size=0.1)
    graph.node_label("{name}")

    synced_nodes: set[str] = set()
    synced_edges: set[tuple[str, str, str]] = set()

    def sync() -> None:
        m = session.memory
        g = m.graph()
        with graph.batch():
            for nid, data in g.nodes(data=True):
                kind = data.get("kind", "group")
                if kind in HIDDEN_KINDS or (kind == "statement" and data.get("life") != "active"):
                    continue
                t = kind
                if kind == "statement" and data.get("grade") == "said":
                    t = "statement_said"
                if kind == "statement" and data.get("claim") == "HYPOTHESIS":
                    t = "statement_hypothesis"
                if kind == "statement" and data.get("claim") == "REJECTED":
                    t = "statement_rejected"
                if kind == "statement" and data.get("mood") in ("pattern", "reported"):
                    t = "statement_pattern"
                if t not in TYPES:
                    t = "group"
                label = data.get("label", nid)
                st = m.statements.get(nid) if kind == "statement" else None
                if st is not None:
                    label = m.render_short(st)
                    info = render_statement(m, st, with_source=True)
                    skupina = st.prov.doc or ""
                    status = f"{st.claim} · {st.grade} · {st.mood}"
                else:
                    node = m.nodes.get(nid)
                    info = " | ".join(render_statement(m, x) for x in m.statements_about(nid)[:6])
                    skupina = node.doc if node is not None and node.doc else ""
                    status = kind
                # `skupina` = dokument → knihovna z ní udělá oblast (shluk) v layoutu
                graph.ensure_node(str(nid), type=t, name=label, kind=kind, status=status, vyroky=info, skupina=skupina or "—")
                synced_nodes.add(str(nid))
            for a, b, data in g.edges(data=True):
                key = (str(a), str(b), str(data.get("type")))
                if key in synced_edges or a == b or str(a) not in synced_nodes or str(b) not in synced_nodes:
                    continue
                synced_edges.add(key)
                graph.ensure_edge(str(a), str(b), type=str(data.get("type")), soft=bool(data.get("soft")))
            for sid, st in m.statements.items():
                if st.status != "active" and graph.has_node(sid):
                    graph.remove_node(sid)
                    synced_nodes.discard(sid)
        # aktivace = kontext rozhovoru: rozsvítí se nejteplejší uzly a jejich okolí
        for n in m.most_active()[:3]:
            if graph.has_node(n.id):
                graph.highlight(n.id, 1)

    konzole = vb.TerminalWindow("dialog", title=f"{title} — dialog", prompt="» ", width=640, closable=False)

    def on_input(event: object) -> None:
        line = getattr(event, "line", "").strip()
        if not line:
            return
        graph.terminal_write("dialog", f"» {line}")
        try:
            answer = session.say(line)
            for out in answer.text.splitlines():
                graph.terminal_write("dialog", out)
        except Exception as exc:  # noqa: BLE001 — konzole nesmí spadnout
            graph.terminal_write("dialog", f"✗ chyba: {exc}")
        sync()

    graph.detail_window(rows=[("uzel", "name"), ("druh", "kind"), ("status", "status"), ("dokument", "skupina"), ("výroky", "vyroky")], width_chars=64)

    @graph.on_click
    def _clicked(event: object) -> None:
        nid = getattr(event, "node_id", None)
        m = session.memory
        if not nid:
            return
        graph.show_detail(nid)
        if nid in m.nodes:
            graph.terminal_write("dialog", f"[{nid}] {describe_node(m, nid)}")
            for st in m.statements_about(nid)[:5]:
                graph.terminal_write("dialog", "   " + render_statement(m, st, with_source=True))
        elif nid in m.statements:
            graph.terminal_write("dialog", f"[{nid}] {render_statement(m, m.statements[nid], with_source=True)}")
            graph.terminal_write("dialog", "   (celý záznam: !ukaž " + nid + ")")

    graph.open_terminal(konzole, on_input=on_input)
    graph.terminal_write("dialog", f"{title}: piš věty (zapíšu), otázky (odpovím), !nápověda pro příkazy, !ukaž s0042 pro výrok v grafu.")
    sync()
    return project, screen


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pamet", help="JSON paměti (načte se, na konci uloží)")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--user", default=VIEWBASE_USER,
                    help="uživatel viewBase2 (odemyká zabezpečená okna); "
                         "tajemství a QR vzniknou při prvním startu v ~/.viewbase/")
    args = ap.parse_args(argv)
    try:
        import viewbase as vb  # type: ignore[import-not-found]
    except ImportError:
        print("viewbase není nainstalované: pip install -e /Users/j/Projects/viewBase2/python",
              file=sys.stderr)
        return 2
    memory = Memory.load(Path(args.pamet)) if args.pamet and Path(args.pamet).exists() else Memory()
    session = Session(memory, live_or_recorded(CACHE))
    project, screen = build(session, port=args.port, user=args.user)
    try:
        project.serve(screen, open_browser=True)
    finally:
        if args.pamet:
            session.memory.save(Path(args.pamet))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
