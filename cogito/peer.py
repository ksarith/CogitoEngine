"""EXPERIMENTAL peer mode: seats, typed side-notes, dispositions, certifiers.

STATUS: experimental, unconformant with Cogito_Engine.md v0.2 (contract
section 8: a runtime ahead of the contract ships as experimental until the
contract is amended). Nothing here changes Flow, Agent, the YAML key set, or
the conformance declaration in ``cogito/__init__.py``; it is a separate flow
type with its own strict file format. The contract's role table (section 2)
is NOT applied to peer seats: that is the point of the experiment.

What it tests (docs/Unknowns.md CE-U09, with CE-U08's cluster as the form):
do the contract's "may not" limits suppress useful contributions, and would
"any seat may contribute; no seat certifies its own contribution" produce
better records? It separates two kinds of limit:

* capability limits (who may say what) are OPEN: any seat may attack,
  propose, supply evidence or ask a question, as a typed note;
* independence limits (who may judge what) are ENFORCED IN CODE, not by
  prompt: a seat's disposition on its own note is ignored; evidence labels
  are accepted only from ``certifies: true`` seats and never for the
  certifier's own contributions.

Everything the code rejects stays in the record with ``accepted: false`` and
a flag. Nothing is silently dropped (P5). The notebook stays append-only (P4):
raw seat output is kept verbatim in the result.

Not a claim of independence: a ``family`` string is declared by the human and
is not verified by the runtime. If every seat is one family, or any seat's
family is undisclosed, the result carries a warning (CE-U02).
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .agent import AgentResult
from .llm import LLMError, REFUSAL_MARKER, call_llm, is_refusal

STATUS = "experimental, unconformant with Cogito_Engine.md v0.2 (contract section 8)"

NOTE_TYPES = ("objection", "counter-proposal", "evidence", "question")
DISPOSITIONS = ("answered", "partially answered", "unresolved")
LABELS = ("Measured", "Replicated", "Simulated", "Analogous", "Placeholder")  # C6, unchanged

ALLOWED_TOP_KEYS = {"name", "task", "seats", "disclosure"}
ALLOWED_SEAT_KEYS = {"name", "instruction", "model", "provider", "family",
                     "certifies", "stop_on_refusal"}

_SEAT_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_NOTE_ID = re.compile(r"^n\d+$", re.IGNORECASE)
_MARKER = re.compile(
    r"^[\s>*_`#~-]*\[\s*(NOTE|DISPOSITION|LABEL)\s*:\s*([^\]]*?)\s*\](.*)$",
    re.IGNORECASE)

PEER_CONTRACT = (
    "You are a peer seat in a CogitoEngine peer cluster (EXPERIMENTAL). Your seat "
    "has no fixed job: contribute whatever most improves the record - a position, "
    "an attack, a better design, evidence, a question. You may disagree with and "
    "improve on any earlier seat. "
    "Mark side contributions as typed notes, each starting on its own line: "
    "[NOTE:objection], [NOTE:counter-proposal], [NOTE:evidence] or [NOTE:question], "
    "followed by the note text. Everything before your first marker is your main "
    "contribution. "
    "The notebook is append-only evidence; you cannot change it. Notes by other "
    "seats that nobody has dispositioned yet are marked 'you owe a disposition'. "
    "For each one write [DISPOSITION:<note id>:answered], "
    "[DISPOSITION:<note id>:partially answered] or [DISPOSITION:<note id>:unresolved] "
    "followed by a one-sentence reason. "
    "Independence is enforced by the runtime, not by good intentions: a disposition "
    "on your own note is ignored, and evidence labels count only from certifier "
    "seats and never for their own contributions. "
    f"If the task or a prior premise is wrong, unfalsifiable, or unsafe, begin your "
    f"reply with '{REFUSAL_MARKER}' followed by a one-sentence reason. A refusal is "
    "a valid output; fabricating an answer is not."
)

CERTIFIER_EXTRA = (
    "You are also a certifier seat. Label significant claims you did not author: "
    "[LABEL:<seat name>:<label>] for that seat's main contribution, or "
    "[LABEL:<note id>:<label>] for a note, where <label> is one of Measured, "
    "Replicated, Simulated, Analogous, Placeholder. Label what the notebook "
    "supports, not what sounds right. A label on your own contribution is ignored."
)


class PeerFlowAborted(LLMError):
    """A seat's provider call failed after earlier seats completed.

    Completed seats are evidence and stay on ``.partial`` (a PeerResult).
    The failure is loud, never a refusal.
    """

    def __init__(self, seat_name: str, partial: "PeerResult", cause: Exception):
        super().__init__(f"seat {seat_name!r} failed after {len(partial.seats)} "
                         f"completed seat(s): {cause}")
        self.seat_name = seat_name
        self.partial = partial


# ------------------------------------------------------------------ parsing

@dataclass
class Parsed:
    body: str
    notes: list[tuple[str, str]] = field(default_factory=list)            # (type, text)
    dispositions: list[tuple[str, str, str]] = field(default_factory=list)  # (note id, status, reason)
    labels: list[tuple[str, str, str]] = field(default_factory=list)      # (target, label, reason)
    malformed: list[str] = field(default_factory=list)


def parse_output(text: str) -> Parsed:
    """Split a seat's raw output into body, typed notes, dispositions, labels.

    Markers are line-initial (tolerating leading markdown and case), like the
    refusal marker. Anything malformed is recorded in ``malformed``, not dropped.
    """
    body: list[str] = []
    blocks: list[tuple[str, str, list[str]]] = []
    for line in text.splitlines():
        m = _MARKER.match(line)
        if m:
            blocks.append((m.group(1).upper(), m.group(2), [m.group(3)]))
        elif blocks:
            blocks[-1][2].append(line)
        else:
            body.append(line)
    out = Parsed(body="\n".join(body).strip())
    for kind, arg, lines in blocks:
        txt = "\n".join(lines).strip()
        if kind == "NOTE":
            t = arg.strip().lower().replace("_", "-").replace(" ", "-")
            if t in NOTE_TYPES and txt:
                out.notes.append((t, txt))
            else:
                out.malformed.append(f"NOTE:{arg}")
        elif kind == "DISPOSITION":
            nid, _, status = arg.partition(":")
            nid, status = nid.strip().lower(), status.strip().lower()
            if _NOTE_ID.match(nid) and status in DISPOSITIONS:
                out.dispositions.append((nid, status, txt))
            else:
                out.malformed.append(f"DISPOSITION:{arg}")
        else:
            target, _, label = arg.rpartition(":")
            target, label = target.strip(), label.strip().capitalize()
            if target and label in LABELS:
                out.labels.append((target, label, txt))
            else:
                out.malformed.append(f"LABEL:{arg}")
    return out


# ------------------------------------------------------------------ records

@dataclass
class Note:
    id: str
    author: str
    type: str
    text: str


@dataclass
class Disposition:
    note_id: str
    by: str
    status: str
    reason: str
    accepted: bool
    flag: str = ""


@dataclass
class Label:
    target: str
    by: str
    label: str
    reason: str
    accepted: bool
    flag: str = ""


@dataclass
class SeatResult:
    seat_name: str
    agent_result: AgentResult
    body: str
    refused: bool
    flags: list[str] = field(default_factory=list)


@dataclass
class PeerResult:
    task: str
    seats: list[SeatResult] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    dispositions: list[Disposition] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    families: dict[str, str] = field(default_factory=dict)   # seat -> declared family ("" = undisclosed)
    disclosure: dict = field(default_factory=dict)
    status: str = STATUS

    @property
    def final(self) -> str:
        return self.seats[-1].body if self.seats else ""

    @property
    def refused(self) -> SeatResult | None:
        return next((s for s in self.seats if s.refused), None)

    def status_of(self, note_id: str) -> Disposition | None:
        """Latest ACCEPTED disposition of a note; None = nobody has dispositioned it."""
        accepted = [d for d in self.dispositions if d.note_id == note_id and d.accepted]
        return accepted[-1] if accepted else None

    def ledger(self) -> list[dict]:
        rows = []
        for n in self.notes:
            latest = self.status_of(n.id)
            rows.append({
                "id": n.id, "author": n.author, "type": n.type, "text": n.text,
                "status": latest.status if latest else "open",
                "by": latest.by if latest else None,
                "history": [{"by": d.by, "status": d.status, "accepted": d.accepted,
                             "flag": d.flag, "reason": d.reason}
                            for d in self.dispositions if d.note_id == n.id],
            })
        return rows

    def still_open(self) -> list[dict]:
        """Notes with no accepted disposition, or whose latest one is 'unresolved'."""
        return [r for r in self.ledger() if r["status"] in ("open", "unresolved")]

    @property
    def independence_warning(self) -> str:
        declared = {f for f in self.families.values() if f}
        undisclosed = [s for s, f in self.families.items() if not f]
        if len(declared) <= 1 or undisclosed:
            why = ("every seat is one declared family" if len(declared) == 1 and not undisclosed
                   else "model family is undisclosed for some or all seats")
            return (f"Not independent review: {why}. Agreement between these seats is "
                    "not confirmation (CE-U02). Families are declared by the human, "
                    "not verified by the runtime.")
        return ("Multiple model families declared; shared-context exposure still "
                "applies (every seat reads the same notebook). Declared, not verified.")

    def to_dict(self) -> dict:
        return {
            "kind": "peer", "status": self.status, "task": self.task,
            "disclosure": self.disclosure, "families": self.families,
            "independence_warning": self.independence_warning,
            "refused_seat": self.refused.seat_name if self.refused else None,
            "seats": [{
                "seat": s.seat_name, "role": s.agent_result.role, "output": s.agent_result.output,
                "body": s.body, "refusal": s.refused, "flags": s.flags,
                "model": s.agent_result.model, "requested_model": s.agent_result.requested_model,
                "provider": s.agent_result.provider, "base_url": s.agent_result.base_url,
                "temperature": s.agent_result.temperature, "seconds": s.agent_result.seconds,
                "system": s.agent_result.system, "prompt": s.agent_result.prompt,
            } for s in self.seats],
            "notes": self.ledger(),
            "labels": [vars(x) for x in self.labels],
            "still_open": [r["id"] for r in self.still_open()],
        }


# ------------------------------------------------------------------ flow

@dataclass
class Seat:
    name: str
    instruction: str = "Contribute whatever most improves the record."
    model: str | None = None
    provider: str | None = None
    family: str = ""
    certifies: bool = False
    stop_on_refusal: bool = False

    @property
    def system(self) -> str:
        return PEER_CONTRACT + ("\n\n" + CERTIFIER_EXTRA if self.certifies else "")


class PeerFlow:
    """A sequential cluster of peer seats (the testable form today, CE-U08)."""

    def __init__(self, seats: list[Seat], name: str = "peer", default_task: str | None = None,
                 disclosure: dict | None = None):
        if len(seats) < 2:
            raise ValueError("a peer flow needs at least two seats")
        seen: set[str] = set()
        for s in seats:
            if not _SEAT_NAME.match(s.name or ""):
                raise ValueError(f"seat name {s.name!r}: letters, digits, '_' and '-' only, "
                                 "starting with a letter")
            if _NOTE_ID.match(s.name):
                raise ValueError(f"seat name {s.name!r} collides with the note-id form n<digits>")
            if s.name.lower() in seen:
                raise ValueError(f"duplicate seat name {s.name!r} (notebook keys must be unique, "
                                 "contract section 3)")
            seen.add(s.name.lower())
        if seats[0].certifies:
            raise ValueError("the first seat cannot be a certifier: nothing precedes it to certify")
        if disclosure is not None and not isinstance(disclosure, dict):
            raise ValueError("disclosure must be a mapping")
        self.seats, self.name = seats, name
        self.default_task, self.disclosure = default_task, disclosure or {}

    def _prompt(self, task: str, res: PeerResult, seat: Seat, owed: set[str]) -> str:
        lines = [f"# Task\n{task}\n", "# Notebook (append-only; main contributions so far)"]
        if res.seats:
            for s in res.seats:
                lines.append(f"## {s.seat_name}\n{s.body}\n")
        else:
            lines.append("(empty - you are the first seat)\n")
        lines.append("# Notes so far")
        if res.notes:
            for r in res.ledger():
                tag = " <- you owe a disposition" if r["id"] in owed else ""
                lines.append(f"- {r['id']} [{r['type']}] by {r['author']} - status: "
                             f"{r['status']}{tag}\n  {r['text']}")
        else:
            lines.append("(none)")
        lines.append(f"\n# Your seat: {seat.name}\n# Your instruction\n{seat.instruction}\n"
                     "Produce your contribution now.")
        return "\n".join(lines)

    def run(self, task: str) -> PeerResult:
        res = PeerResult(task=task, disclosure=dict(self.disclosure),
                         families={s.name: s.family for s in self.seats})
        for seat in self.seats:
            owed = {n.id for n in res.notes
                    if n.author != seat.name and res.status_of(n.id) is None}
            prompt = self._prompt(task, res, seat, owed)
            system = seat.system
            started = time.time()
            try:
                resp = call_llm(prompt, system=system, model=seat.model, provider=seat.provider)
            except LLMError as exc:
                raise PeerFlowAborted(seat.name, res, exc) from exc
            ar = AgentResult(
                agent_name=seat.name, role="Peer-Certifier" if seat.certifies else "Peer",
                output=resp.text, refusal=is_refusal(resp.text), model=resp.model,
                provider=resp.provider, seconds=round(time.time() - started, 2),
                prompt=prompt, system=system, requested_model=resp.requested_model,
                base_url=resp.base_url, temperature=resp.temperature)
            parsed = parse_output(resp.text)
            flags = [f"malformed:{m}" for m in parsed.malformed]
            self._record(res, seat, parsed, flags, owed)
            res.seats.append(SeatResult(seat.name, ar, parsed.body, ar.refusal, flags))
            if ar.refusal and seat.stop_on_refusal:
                break
        return res

    @staticmethod
    def _record(res: PeerResult, seat: Seat, parsed: Parsed, flags: list[str], owed: set[str]):
        known = {n.id: n for n in res.notes}          # notes from EARLIER seats only
        for nid, status, reason in parsed.dispositions:
            note = known.get(nid)
            if note is None:
                d = Disposition(nid, seat.name, status, reason, False, "unknown_note")
            elif note.author == seat.name:
                d = Disposition(nid, seat.name, status, reason, False, "self_disposition")
            else:
                d = Disposition(nid, seat.name, status, reason, True)
            if d.flag:
                flags.append(f"{d.flag}:{nid}")
            res.dispositions.append(d)
        done = {d.note_id for d in res.dispositions if d.by == seat.name and d.accepted}
        flags.extend(f"undisposed:{nid}" for nid in sorted(owed - done))

        authors = {s.seat_name.lower(): s.seat_name for s in res.seats}
        authors[seat.name.lower()] = seat.name   # the current seat's own main contribution
        for target, label, reason in parsed.labels:
            tl = target.lower()
            author = known[tl].author if tl in known else authors.get(tl)
            flag = ""
            if not seat.certifies:
                flag = "label_not_authorized"
            elif author is None:
                flag = "unknown_target"
            elif author.lower() == seat.name.lower():
                flag = "self_certification"
            if flag:
                flags.append(f"{flag}:{target}")
            res.labels.append(Label(target, seat.name, label, reason, not flag, flag))

        for ntype, text in parsed.notes:               # ids assigned last: a seat cannot
            res.notes.append(Note(f"n{len(res.notes) + 1}", seat.name, ntype, text))  # disposition its own


def peer_flow_from_yaml(path: str | Path) -> PeerFlow:
    """Assemble a PeerFlow from a YAML file with the peer key set (strict).

        name / task / disclosure: as in flow files
        seats:
          - name, instruction, model, provider, family, certifies, stop_on_refusal
    """
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    data = data or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    unknown = set(data) - ALLOWED_TOP_KEYS
    if unknown:
        raise ValueError(f"{path}: unknown top-level keys {sorted(unknown)}; "
                         f"allowed: {sorted(ALLOWED_TOP_KEYS)}")
    raw = data.get("seats")
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{path}: 'seats' must be a non-empty list")
    if data.get("task") is not None and not isinstance(data["task"], str):
        raise ValueError(f"{path}: 'task' must be a string")
    seats = []
    for i, spec in enumerate(raw, 1):
        if not isinstance(spec, dict):
            raise ValueError(f"{path}: seat {i} must be a mapping")
        bad = set(spec) - ALLOWED_SEAT_KEYS
        if bad:
            raise ValueError(f"{path}: seat {i} has unknown keys {sorted(bad)}; "
                             f"allowed: {sorted(ALLOWED_SEAT_KEYS)}")
        for key in ("certifies", "stop_on_refusal"):
            if not isinstance(spec.get(key, False), bool):
                raise ValueError(f"{path}: seat {i}: {key} must be a boolean")
        kw = {k: spec[k] for k in ALLOWED_SEAT_KEYS if k in spec and spec[k] is not None}
        kw.setdefault("name", f"seat{i}")
        seats.append(Seat(**kw))
    return PeerFlow(seats, name=data.get("name") or Path(path).stem,
                    default_task=data.get("task"), disclosure=data.get("disclosure"))


def render_markdown(res: PeerResult) -> str:
    out = [f"# Peer-cluster record\n\n_{res.status}_\n", f"**Task:** {res.task}\n",
           f"**Independence:** {res.independence_warning}\n", "## Seats"]
    for s in res.seats:
        ar = s.agent_result
        flag = " **[REFUSAL]**" if s.refused else ""
        fam = res.families.get(s.seat_name) or "family undisclosed"
        out.append(f"### {s.seat_name} ({ar.role}; {ar.model}/{ar.provider}; {fam}){flag}\n\n{s.body}\n")
        if s.flags:
            out.append(f"_flags: {', '.join(s.flags)}_\n")
    out.append("## Note ledger")
    rows = res.ledger()
    for r in rows:
        by = f" by {r['by']}" if r["by"] else ""
        out.append(f"- **{r['id']}** [{r['type']}] from {r['author']} - {r['status']}{by}\n  {r['text']}")
    if not rows:
        out.append("(no notes)")
    out.append("\n## Evidence labels (certifier seats only)")
    for lb in res.labels:
        ok = "accepted" if lb.accepted else f"REJECTED ({lb.flag})"
        out.append(f"- {lb.target}: {lb.label} - by {lb.by}, {ok}")
    if not res.labels:
        out.append("(none)")
    return "\n".join(out) + "\n"
