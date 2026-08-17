"""Zakotvení: čtení → uzly a výroky v paměti.

Proč zvláštní vrstva (spec § 3.2 conbond4, tady § 5–6): čtení jmenuje
věci slovy, paměť je drží jako uzly. Mezi tím stojí rozhodnutí o identitě
(„Jirásek“ = „Alois Jirásek“?), o zájmenech a nevysloveném podmětu
(aktivace = sliding window), o instanci z neurčité zmínky („Filip má
auto“ zakládá anonymní auto ∈ auto) a o přivlastnění („Filipovo auto“).
Každé takové rozhodnutí je **výchozí volba s autoritou** a zapíše se do
`Statement.defaults`; co se rozhodnout nedá, je otevřená položka.

Vstup: `Reading`, `Memory`, provenience, stupeň, téma dokumentu.
Výstup: `Grounded` — zapsané výroky (u otázky nezapsané, jen zakotvené).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cb6.discourse import Registry, ambiguous
from cb6.memory import Memory, Node, OpenItem, Provenance, Role, Statement
from cb6.read import Predication, Reading, TermSpec
from cb6.triage import Decision, Rule, Triaged, triage


@dataclass
class Grounded:
    statements: list[Statement] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    open: list[OpenItem] = field(default_factory=list)
    #: hlavní výrok (u otázky nezapsaný)
    main: Statement | None = None
    sentence: str = ""


class Grounder:
    """Jedno zakotvení jedné věty (drží paměť, provenienci a poznámky)."""

    def __init__(self, memory: Memory, prov: Provenance, grade: str, *, topic: str | None, write: bool,
                 triaged: Triaged | None = None, segment: str | None = None) -> None:
        self.m = memory
        self.prov = prov
        self.grade = grade
        self.topic = topic
        self.write = write
        #: rozhodnutí triáže (status/nálada predikací, pravidla); None = vše SAFE/assert
        self.triaged = triaged
        #: aktuální segment dokumentu (hrany `mention` a okno registru)
        self.segment = segment
        self.registry = Registry(memory)
        #: nejednoznačná koreference: (jméno role, kandidáti) — po zápisu jádra
        #: vzniknou HYPOTHESIS alternativy (I‑3, I‑8)
        self._ambiguous: list[tuple[str, list[str], str]] = []
        self.out = Grounded()
        self._defaults: list[str] = []
        self._pending_open: list[tuple[str, str, str, list[str]]] = []  # (kind, about, question, options)

    # ---- termy ---------------------------------------------------------------

    def resolve_term(self, t: TermSpec, *, role: str, subject_specific: bool, pred: str | None) -> str | None:
        """Term → id uzlu (nebo `None`, když se rozřešit nedá).

        Zaznamená výchozí volby do `self._defaults` a otevřené položky do
        `self._pending_open`; každý rozřešený term entity/místa je zmínka →
        hrana `mention` (registr referentů, I‑11).
        """
        nid = self._resolve_term_inner(t, role=role, subject_specific=subject_specific, pred=pred)
        if nid is not None and self.write and self.out.sentence:
            n = self.m.nodes.get(nid)
            if n is not None and n.kind in ("entity", "place"):
                self.m.note_mention(self.out.sentence, nid, role, " ".join(t.forms), self.segment or "")
        return nid

    def _resolve_term_inner(self, t: TermSpec, *, role: str, subject_specific: bool, pred: str | None) -> str | None:
        """Vlastní rozřešení termu (viz `resolve_term`)."""
        if t.kind == "wh":
            return None
        if t.kind == "entity":
            node, new = self.m.ensure_entity(t.name_lemmas or (t.lemma,), t.forms, gender=t.gender, number=t.number, doc=self.prov.doc, prefer=self.topic)
            if new:
                self.out.nodes.append(node)
                self.out.notes.append(f"{node.label()} → {node.id} (založen)")
            else:
                self.out.notes.append(f"{' '.join(t.forms)} → {node.id} ({node.label()}; týž uzel)")
                if " ".join(t.name_lemmas) != node.lemma:
                    self._defaults.append(f"identita: „{' '.join(t.name_lemmas)}“ = {node.label()} (částečné jméno)")
            return node.id
        if t.kind == "place":
            node = self.m.ensure_place(t.name_lemmas or (t.lemma,), t.forms)
            if node.gender is None:
                node.gender, node.number = t.gender, t.number
            return node.id
        if t.kind == "time":
            if t.time is None:
                return self.m.ensure_group(t.lemma).id
            return self.m.ensure_time(t.time).id
        if t.kind == "pron":
            return self._resolve_pron(t, role)
        if t.kind == "value":
            return self.m.ensure_group(t.lemma).id
        # group
        group = self.m.ensure_group(t.lemma, t.attrs)
        if t.possessor is not None:
            owned = self._resolve_possessed(t, group, role)
            if owned is not None:
                return owned
        if t.quant == "·" and t.quant_authority == "determiner":
            # „ten pes“ — určitý popis: naposled aktivní prvek té group, jinak nový
            for cand in self.m.most_active(kind="entity"):
                if self.m.member_star(cand.id, group.id) is not None:
                    self._defaults.append(f"{role}: „{t.lemma}“ = {cand.label()} (určitý popis z aktivace)")
                    return cand.id
        if (t.quant == "∃" and role == "co" and subject_specific and self.write
                and pred not in ("být",) and t.count is None):
            # neurčitá zmínka u konkrétního podmětu → nová instance („Filip má auto“ → a1 ∈ auto)
            inst = self.m.new_node("entity", t.lemma, names=[], attrs=t.attrs, doc=self.prov.doc, gender=t.gender, number=t.number)
            inst.base = group.id
            self.out.nodes.append(inst)
            self._defaults.append(f"{role}: nová instance {inst.id} ∈ {group.label()} (neurčitá zmínka)")
            self._member(inst.id, group.id)
            return inst.id
        return group.id

    def _member(self, elem: str, group: str) -> None:
        """Typovací výrok „instance ∈ skupina“ z neurčité zmínky („Filip má auto“ →
        a1 ∈ auto). Je `SAFE` (slouží uzávěrům), ale `kind="typing"` — není to
        znalost získaná z textu, bench ho nepočítá do yieldu ani do auditu."""
        st = Statement("", "být", "typing", kernel="member", grade=self.grade, prov=self.prov, sentence=self.out.sentence,  # type: ignore[arg-type]
                       roles=[Role("kdo", [elem], "·", "structural"), Role("co", [group], "∃", "structural")],
                       defaults=["instance: členství z neurčité zmínky"])
        self.m.attach(st)
        self.out.statements.append(st)

    def _resolve_pron(self, t: TermSpec, role: str) -> str | None:
        """Zájmeno / nevyslovený podmět → registr referentů (spec § 4).

        1. kandidáti = uzly se zmínkou v tomto/předchozím segmentu se shodou rodu
           a čísla (entity; když žádná, místa), řazení aktivace → role → čerstvost;
        2. téma dokumentu má přednost, dokud není jiný kandidát VÝRAZNĚ
           čerstvější (encyklopedický text: vedlejší osoby se zmíní jednou, téma
           se vrací) — beze změny proti conbond5;
        3. když nevítězí téma a první dva kandidáti jsou blízko (`ambiguous`),
           nevolí se: role zůstane bez termu, vzniknou HYPOTHESIS alternativy
           a otevřená položka (I‑3, I‑8);
        4. bez kandidáta → téma dokumentu; bez tématu → otevřená položka.
        """
        if t.lemma in ("se", "sebe", "si"):
            return None
        label = t.lemma if t.lemma != "∅" else "nevyslovený podmět"
        if t.person in ("1", "2"):
            self._pending_open.append(("reference", t.lemma, f"Na koho odkazuje „{label}“ v roli {role}?", []))
            return None
        cands = self.registry.candidates(gender=t.gender, number=t.number, segment=self.segment, kinds=("entity",))
        if not cands:
            cands = self.registry.candidates(gender=t.gender, number=t.number, segment=self.segment, kinds=("place",))
        if not cands:
            # registr prázdný (např. testy bez vět) → aktivace jako v conbond5
            fallback = self.m.most_active(kinds=("entity",), gender=t.gender, number=t.number) or self.m.most_active(kinds=("place",), gender=t.gender, number=t.number)
            if fallback:
                node = fallback[0]
                self._defaults.append(f"{role}: „{label}“ = {node.label()} (z aktivace)")
                return node.id
        if cands:
            node = cands[0].node
            topic = self.m.nodes.get(self.topic) if self.topic else None
            if topic is not None and any(c.node is topic for c in cands) and topic is not node:
                if self.m.activation(topic.id) * 3.0 >= self.m.activation(node.id):
                    node = topic
            if node is not topic and ambiguous(cands):
                ids = [c.node.id for c in cands[:3]]
                self._ambiguous.append((role, ids, label))
                self._pending_open.append(("reference", t.lemma, f"Na koho odkazuje „{label}“ v roli {role}? Kandidáti: " + ", ".join(self.m.nodes[i].label() for i in ids), [self.m.nodes[i].label() for i in ids]))
                self._defaults.append(f"{role}: „{label}“ nejednoznačné — kandidáti {', '.join(self.m.nodes[i].label() for i in ids)} (hypotézy)")
                return None
            self._defaults.append(f"{role}: „{label}“ = {node.label()} (koref: registr{', téma dokumentu' if node is topic else ''})")
            return node.id
        if self.topic and self.topic in self.m.nodes:
            node = self.m.nodes[self.topic]
            self._defaults.append(f"{role}: „{label}“ = {node.label()} (téma dokumentu)")
            return node.id
        self._pending_open.append(("reference", t.lemma, f"Na koho odkazuje „{label}“ v roli {role}?", []))
        return None

    def _resolve_possessed(self, t: TermSpec, group: Node, role: str) -> str | None:
        """„Filipovo auto“ / „jeho auto“ → auto, které Filip má (výrok `mít`),
        jinak nová instance s `mít`."""
        kind, word = t.possessor  # type: ignore[misc]
        owner: Node | None = None
        if kind == "adj":
            stem = word
            for suf in ("ův", "ova", "ovo", "in", "ina", "ino"):
                if word.endswith(suf):
                    stem = word[: -len(suf)]
                    break
            cands = [n for n in self.m.nodes.values() if n.kind == "entity" and any(w.lower().startswith(stem.lower()) for name in n.names for w in name.split()) and len(stem) >= 3]
            if len(cands) == 1:
                owner = cands[0]
            elif cands:
                owner = max(cands, key=lambda n: self.m.activation(n.id))
        else:
            cands = self.m.most_active(kinds=("entity",))
            owner = cands[0] if cands else (self.m.nodes.get(self.topic) if self.topic else None)
        if owner is None:
            self._pending_open.append(("reference", word, f"Čí je „{t.lemma}“ („{word}“)?", []))
            return None
        self._defaults.append(f"{role}: „{word} {t.lemma}“ → vlastník {owner.label()}")
        # existující vlastnictví?
        for st in self.m.statements_about(owner.id):
            if st.pred in ("mít", "vlastnit") and not st.neg:
                kdo, co = st.role("kdo"), st.role("co")
                if kdo and owner.id in kdo.terms and co:
                    for x in co.terms:
                        if self.m.member_star(x, group.id) is not None:
                            return x
        if not self.write:
            return None
        inst = self.m.new_node("entity", t.lemma, attrs=t.attrs, doc=self.prov.doc, gender=t.gender, number=t.number)
        inst.base = group.id
        self.out.nodes.append(inst)
        self._member(inst.id, group.id)
        # Přivlastnění není tvrzení o vlastnictví: „Jiráskova ulice“ ≠ „Jirásek má
        # ulici“, „jeho smrt“ ≠ „má smrt“. Nově odvozené `mít` je proto HYPOTHESIS
        # (I‑3: nikdy ve verdiktu); existující vlastnictví výše se použije jako SAFE.
        st = Statement("", "mít", "verb", grade=self.grade, prov=self.prov, sentence=self.out.sentence,  # type: ignore[arg-type]
                       roles=[Role("kdo", [owner.id], "·", "structural"), Role("co", [inst.id], "·", "structural")],
                       defaults=[f"vlastnictví z přivlastnění „{word}“"], claim="HYPOTHESIS",
                       reason="přivlastnění „" + word + "“ neurčuje vlastnictví (může jít o pojmenování, autorství, vztah)")
        self.m.attach(st)
        self.out.statements.append(st)
        return inst.id

    # ---- predikace -----------------------------------------------------------

    def ground_predication(self, p: Predication, *, parent: str | None = None, residue: list[tuple[str, str]] | None = None) -> Statement:
        """Zakotvi jednu predikaci jako výrok (a rekurzivně její vnořené).

        Args:
            p: predikace z čtení.
            parent: id výroku, do něhož je tato vnořena (vztažná věta, obsah
                promluvy…) — jde do `Statement.parent`, ne do `derived_from`
                (vnoření není odvození).
            residue: zbytek věty, který nese hlavní výrok.
        Returns:
            Zapsaný (nebo u otázky jen sestavený) výrok.
        """
        self._defaults = list(p.defaults)
        self._pending_open = []
        subj = p.role("kdo")
        subject_specific = bool(subj and subj.terms and subj.terms[0].kind in ("entity", "pron") and subj.terms[0].quant == "·")
        dec = self.triaged.decision(p) if self.triaged is not None else Decision()
        mood = p.mood if p.mood == "question" else dec.mood
        st = Statement("", p.pred, p.kind, neg=p.neg, modality=p.modality, kernel=p.kernel, grade=self.grade,  # type: ignore[arg-type]
                       prov=self.prov, sentence=self.out.sentence, tense=p.tense, mood=mood, parent=parent,  # type: ignore[arg-type]
                       residue=list(residue or []), claim=dec.claim, reason=dec.reason)
        self._defaults.extend(dec.defaults)
        nested_specs: list[tuple[Role, Predication]] = []
        for rf in p.roles:
            role = Role(rf.name, [], None, rf.authority, rf.surface, wh=rf.wh, wh_kind=rf.wh_kind)
            if rf.nested is not None:
                nested_specs.append((role, rf.nested))
            for t in rf.terms:
                nid = self.resolve_term(t, role=rf.name, subject_specific=subject_specific, pred=p.pred)
                if nid is None:
                    continue
                role.terms.append(nid)
                if t.count is not None:
                    role.counts[nid] = t.count
                if role.quant is None:
                    role.quant = t.quant
                if t.quant_authority.startswith("default") and t.quant_authority not in ("default:předmět",):
                    pass  # už je v p.defaults z čtení
            if rf.authority == "surface" and not rf.wh and p.kind not in ("nmod", "appos"):
                self._pending_open.append(("role_name", rf.surface, f"Co znamená role „{rf.name}“ ({rf.surface})? (kde, kdy, kudy, čím, …)", ["kde", "kdy", "kam", "odkud", "kudy", "čím", "s_kým", "komu"]))
            st.roles.append(role)
        # výčet členů skupiny („děti: Helena, Josef, Emílie“ → Helena ∈ dítě, …) není
        # totožnost (same_as by spojila všechny navzájem — otrava identity); převeď na member
        kdo_r, co_r = st.role("kdo"), st.role("co")
        if st.kernel == "same_as" and kdo_r and co_r and len(kdo_r.terms) == 1 and len(co_r.terms) > 1 \
                and self.m.nodes.get(kdo_r.terms[0], Node("", "")).kind == "group" \
                and all(self.m.nodes.get(t, Node("", "")).kind in ("entity", "place") for t in co_r.terms):
            group_id = kdo_r.terms[0]
            members = list(co_r.terms)
            kdo_r.terms, co_r.terms = members, [group_id]
            kdo_r.quant, co_r.quant = "·", "∃"
            st.kernel = "member"
            self._defaults.append(f"výčet: {self.m.nodes[group_id].label()}: {', '.join(self.m.nodes[t].label() for t in members)} → každý ∈ {self.m.nodes[group_id].label()} [výchozí]")
        st.defaults = list(dict.fromkeys(self._defaults))
        pending = list(self._pending_open)
        ambiguous_roles = list(self._ambiguous)
        self._ambiguous = []
        if self.write:
            self.m.attach(st)
            self.out.statements.append(st)
            for kind, about, question, options in pending:
                item = self.m.add_open(kind, about, question, st.id, options)
                self.out.open.append(item)
            # nejednoznačná koreference → alternativy jako HYPOTHESIS (I‑3, I‑8)
            for role_name, cand_ids, label in ambiguous_roles:
                for cid in cand_ids:
                    alt = Statement("", st.pred, st.kind, neg=st.neg, modality=st.modality, kernel=st.kernel,
                                    roles=[Role(r.name, list(r.terms) + ([cid] if r.name == role_name else []), r.quant, r.authority, r.surface, r.nested, dict(r.counts), r.wh, r.wh_kind) for r in st.roles],
                                    grade=st.grade, prov=st.prov, sentence=st.sentence, tense=st.tense, mood=st.mood,
                                    claim="HYPOTHESIS", alternatives=[st.id],
                                    reason=f"koreference: „{label}“ = {self.m.nodes[cid].label()}? (kandidáti {', '.join(self.m.nodes[i].label() for i in cand_ids)})",
                                    defaults=[f"{role_name}: „{label}“ = {self.m.nodes[cid].label()} (hypotéza koreference)"])
                    self.m.attach(alt)
                    self.out.statements.append(alt)
            if st.residue:
                item = self.m.add_open("residue", ", ".join(f"„{f}“" for f, _ in st.residue),
                                       "Do čtení se nedostalo: " + ", ".join(f"„{f}“ ({path})" for f, path in st.residue) + " — jakou roli to hraje?", st.id)
                self.out.open.append(item)
        for role, nested in nested_specs:
            child = self.ground_predication(nested, parent=st.id if self.write else None)
            role.nested = child.id or None
            if not self.write:
                role.nested = None
                self.out.statements.append(child)
        return st

    def ground_rule(self, rule: Rule, *, residue: list[tuple[str, str]] | None = None) -> Statement:
        """Podmínka z textu → výrok `kind="rule"` (SAFE jakožto pravidlo) s rolemi
        `pokud` (podmínka) a `pak` (důsledek), obě jako výroky `mood="pattern"`
        vnořené do pravidla. `only_if` prohodí strany; `iff` volající zavolá dvakrát.

        Args:
            rule: z triáže; residue: zbytek věty (nese ho pravidlo).
        Returns:
            Výrok pravidla (u `write=False` nezapsaný).
        """
        cond, cons = (rule.cond, rule.cons) if rule.kind != "only_if" else (rule.cons, rule.cond)
        st = Statement("", None, "rule", grade=self.grade, prov=self.prov, sentence=self.out.sentence,  # type: ignore[arg-type]
                       residue=list(residue or []), defaults=[f"pravidlo z podmínky „{rule.marker}“ ({rule.kind})"])
        if self.write:
            self.m.attach(st)
            self.out.statements.append(st)
        c1 = self.ground_predication(cond, parent=st.id or None)
        c2 = self.ground_predication(cons, parent=st.id or None)
        st.roles = [Role("pokud", [], None, "structural", nested=c1.id or None), Role("pak", [], None, "structural", nested=c2.id or None)]
        return st

    def ground(self, reading: Reading) -> Grounded:
        """Zakotvi celé čtení: hlavní predikace (nebo pravidla z podmínek), vnořené
        a vedlejší predikace, podle rozhodnutí triáže."""
        if self.write:
            sent = self.m.new_sentence(self.prov.doc, self.prov.sent_no, self.prov.text, segment=self.segment)
            self.out.sentence = sent.id
        rules = self.triaged.rules if self.triaged is not None else []
        if rules:
            first: Statement | None = None
            for rule in rules:
                r = self.ground_rule(rule, residue=reading.residue if first is None else None)
                first = first or r
                if rule.kind == "iff":
                    self.ground_rule(Rule("only_if", rule.cond, rule.cons, rule.marker))
            self.out.main = first
        else:
            self.out.main = self.ground_predication(reading.main, residue=reading.residue)
        for sec in reading.main.secondary:
            self.ground_predication(sec)
        if self.triaged is not None:
            for n in self.triaged.notes:
                self.out.notes.append(n)
        return self.out


def ground(reading: Reading, memory: Memory, prov: Provenance, grade: str = "read", *,
           topic: str | None = None, write: bool = True, segment: str | None = None) -> Grounded:
    """Zakotvi čtení do paměti — přes triáž (`triage()`), která rozhodne statusy.
    `write=False` jen rozřeší termy (otázka bázi nemění, I‑12) — vrací hlavní
    výrok bez id."""
    return ground_triaged(triage(reading), memory, prov, grade, topic=topic, write=write, segment=segment)


def ground_triaged(t: Triaged, memory: Memory, prov: Provenance, grade: str = "read", *,
                   topic: str | None = None, write: bool = True, segment: str | None = None) -> Grounded:
    """Zakotvi už roztříděné čtení (`Triaged`)."""
    return Grounder(memory, prov, grade, topic=topic, write=write, triaged=t, segment=segment).ground(t.reading)
