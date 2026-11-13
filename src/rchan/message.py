"""Parse, check and compose RCP messages (issue bodies). See SPEC.md §7."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from .manifest import Manifest

ENVELOPE = ("From", "To", "Sent", "Re", "Needs", "Due")
OPTIONAL_ENVELOPE = ("Basis", "Labels")
NEEDS = ("action", "reply", "approval", "nothing")
KEYWORDS = ("ACK", "BLOCKED", "DONE", "DECLINED", "DECIDED", "FALLBACK", "WITHDRAWN")
STATE_LABELS = ("state:acked", "state:blocked", "state:waiting-approver")


@dataclass(frozen=True)
class MessageType:
    about: str
    needs: tuple[str, ...]
    required: tuple[tuple[str, str], ...]   # (heading, hint)
    optional: tuple[tuple[str, str], ...] = ()


_EVIDENCE = ("Evidence", "Quoted text, a message subject with its date, or links.")

TYPES: dict[str, MessageType] = {
    "request": MessageType(
        "Ask the recipient to do something", ("action",),
        (("Ask", "What to do, specifically."),
         ("Why", "The reason, so the recipient can judge edge cases."),
         ("Done when", "The observable result that closes this message.")),
        (_EVIDENCE,)),
    "handoff": MessageType(
        "Transfer state or results", ("nothing", "reply", "action"),
        (("What changed", "Decisions, replies received, records written."),
         ("Pending", "Open items, each with an identifier the recipient can look up.")),
        (_EVIDENCE,)),
    "question": MessageType(
        "You need information to proceed", ("reply",),
        (("Question", "One question."),
         ("Purpose", "What the answer will be used for."),
         ("Fallback", "What you will assume and do if no reply arrives by the due date."))),
    "decision": MessageType(
        "Only an approver can decide", ("approval",),
        (("Decision", "The choice, in one sentence."),
         ("Options", "Each option with its consequence."),
         ("Recommendation", "Which option and why.")),
        (_EVIDENCE,)),
    "report": MessageType(
        "For information; no action expected", ("nothing",),
        (("Report", "The facts, briefly."),),
        (_EVIDENCE,)),
}

_HEADING = re.compile(r"^###\s+(.+?)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
_TITLE = re.compile(r"^\[([a-z]+)\]\s+\S")
_SENT_LOCAL = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (UTC|[A-Za-z_]+(?:/[A-Za-z0-9_+-]+)+)$")
_COMMENT = re.compile(r"^\*\*(.+?):\*\*\s*(?:([A-Z]+)\b)?")
_EMPTY = ("", "_No response_")  # GitHub issue forms write the latter for a blank field.


def split_body(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split a body into (preamble, [(lower-cased heading, value), ...]) in document order.

    Headings inside fenced code blocks are content, not section breaks.
    """
    pairs: list[tuple[str, str]] = []
    preamble: list[str] = []
    current: str | None = None
    buffer: list[str] = []
    fenced = False

    def flush() -> None:
        if current is not None:
            value = "\n".join(buffer).strip()
            pairs.append((current, "" if value in _EMPTY else value))

    for line in text.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        heading = None if fenced else _HEADING.match(line)
        if heading:
            flush()
            current, buffer = heading.group(1).casefold(), []
        elif current is not None:
            buffer.append(line)
        else:
            preamble.append(line)
    flush()
    return "\n".join(preamble).strip(), pairs


def parse_body(text: str) -> dict[str, str]:
    """Sections keyed by lower-cased heading. If a heading repeats, the first one counts."""
    sections: dict[str, str] = {}
    for heading, value in split_body(text)[1]:
        sections.setdefault(heading, value)
    return sections


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def type_from_title(title: str) -> str | None:
    match = _TITLE.match(title or "")
    return match.group(1) if match and match.group(1) in TYPES else None


def _valid_sent(value: str) -> bool:
    local = _SENT_LOCAL.match(value)
    try:
        if local:
            datetime.strptime(local.group(1), "%Y-%m-%d %H:%M")
            return True
        return datetime.fromisoformat(value).tzinfo is not None
    except ValueError:
        return False


def _valid_due(value: str) -> bool:
    token = re.sub(r"\s*\(.*\)\s*$", "", value).strip()
    return token.casefold() == "none" or is_date(token)


def is_date(value: object) -> bool:
    """True for a real calendar date written exactly as YYYY-MM-DD."""
    text = str(value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return False
    try:
        date.fromisoformat(text)
        return True
    except ValueError:
        return False


def check(body: str, *, title: str | None = None, labels: list[str] | None = None,
          manifest: Manifest | None = None, kind: str | None = None) -> list[str]:
    """Return every way a message fails SPEC.md §7. An empty list means it conforms.

    The type is taken from ``kind``, else the title, else a ``type:`` label.
    Participant checks run only when a manifest is given; label checks only when
    labels are given.
    """
    problems: list[str] = []
    preamble, pairs = split_body(body)
    keys = [heading for heading, _ in pairs]
    sections = parse_body(body)
    labels = list(labels) if labels is not None else None

    if preamble:
        problems.append("the body must start with `### From`; text before the first heading "
                        "is not allowed")
    for heading in sorted({k for k in keys if keys.count(k) > 1}):
        problems.append(f"section `{heading}` appears more than once")

    titled = type_from_title(title or "")
    if title is not None and titled is None:
        problems.append("title must be `[type] short phrase` with a known type")
    if kind and titled and kind != titled:
        problems.append(f"the title says {titled} but the message was checked as a {kind}")
    kind = kind or titled
    type_labels = [l.split(":", 1)[1] for l in labels or () if l.startswith("type:")]
    if kind is None and len(type_labels) == 1:
        kind = type_labels[0]
    spec = TYPES.get(kind or "")
    if spec is None:
        problems.append("message type is unknown: give a `[type]` title or one `type:` label")

    # Envelope: every section present and non-empty; the six come first, in order;
    # Basis and Labels follow them, before the type-specific sections.
    envelope = [e.casefold() for e in ENVELOPE]
    optional = [o.casefold() for o in OPTIONAL_ENVELOPE]
    for heading in ENVELOPE:
        if not sections.get(heading.casefold()):
            problems.append(f"envelope section `{heading}` is missing or empty")
    unique = list(dict.fromkeys(keys))
    # The envelope sections present must be the first sections, in ENVELOPE order.
    envelope_present = [e for e in envelope if e in unique]
    if unique[:len(envelope_present)] != envelope_present:
        problems.append("envelope sections must come first and must appear in the order "
                        + ", ".join(ENVELOPE))
    # Of the remaining sections, Basis and Labels (in either order) must lead.
    after_envelope = [k for k in unique if k not in envelope]
    optional_present = [k for k in after_envelope if k in optional]
    if after_envelope[:len(optional_present)] != optional_present:
        problems.append("`Basis` and `Labels` must come straight after `Due`")

    sender = None
    recipients = []
    if manifest is not None:
        if sections.get("from"):
            sender = manifest.get(sections["from"])
            if sender is None:
                problems.append(f"`From` is not a channel participant: {sections['from']!r}")
        for ref in split_list(sections.get("to", "")):
            recipient = manifest.get(ref)
            if recipient is None:
                problems.append(f"`To` names someone who is not a participant: {ref!r}")
            else:
                recipients.append(recipient)

    if sections.get("sent") and not _valid_sent(sections["sent"]):
        problems.append("`Sent` must be `YYYY-MM-DD HH:MM Zone/Name` or an RFC 3339 timestamp")
    if sections.get("due") and not _valid_due(sections["due"]):
        problems.append("`Due` must be a YYYY-MM-DD date or `none`")

    needs_words = sections.get("needs", "").split()
    needs = needs_words[0].casefold() if needs_words else ""
    if needs and needs not in NEEDS:
        problems.append(f"`Needs` must be one of {', '.join(NEEDS)}")
    elif needs and spec and needs not in spec.needs:
        problems.append(f"`Needs: {needs}` is not allowed on a {kind}; use {' or '.join(spec.needs)}")

    if spec:
        for heading, _ in spec.required:
            if not sections.get(heading.casefold()):
                problems.append(f"a {kind} requires a non-empty `{heading}` section")
    if kind == "decision" and manifest is not None and recipients:
        if not any("approver" in r.roles for r in recipients):
            problems.append("a decision must be addressed to at least one approver")

    declared = split_list(sections.get("labels", ""))
    if sender is not None and not sender.can("issues.label") and not declared:
        problems.append(f"{sender.name} cannot apply labels, so the body needs a `Labels` section")

    if labels is not None:
        problems += _check_labels(labels, kind, sender, recipients, manifest)
    return problems


def _check_labels(labels, kind, sender, recipients, manifest) -> list[str]:
    problems = []
    senders = [l for l in labels if l.startswith("from:")]
    targets = [l for l in labels if l.startswith("to:")]
    types = [l for l in labels if l.startswith("type:")]
    if len(senders) != 1:
        problems.append(f"exactly one `from:` label is required; found {len(senders)}")
    if not targets:
        problems.append("at least one `to:` label is required")
    if len(types) != 1:
        problems.append(f"exactly one `type:` label is required; found {len(types)}")
    elif kind and types[0] != f"type:{kind}":
        problems.append(f"label {types[0]} disagrees with the message type {kind}")
    for label in labels:
        if label.startswith("state:") and label not in STATE_LABELS:
            problems.append(f"unknown state label: {label}")
        if label.startswith("prio:") and label != "prio:high":
            problems.append(f"unknown priority label: {label}")
    if manifest is not None:
        if sender and senders and senders[0] != f"from:{sender.id}":
            problems.append(f"label {senders[0]} disagrees with `From` ({sender.name})")
        if recipients and targets and set(targets) != {f"to:{r.id}" for r in recipients}:
            problems.append("`to:` labels disagree with the `To` section")
    return problems


def expected_labels(body: str, title: str, manifest: Manifest) -> list[str]:
    """The from/to/type labels a message should carry, derived from its body and title."""
    sections = parse_body(body)
    labels: list[str] = []
    sender = manifest.get(sections.get("from", ""))
    if sender:
        labels.append(f"from:{sender.id}")
    for ref in split_list(sections.get("to", "")):
        recipient = manifest.get(ref)
        if recipient:
            labels.append(f"to:{recipient.id}")
    kind = type_from_title(title)
    if kind:
        labels.append(f"type:{kind}")
    for label in split_list(sections.get("labels", "")):
        label = label.strip("`")
        if label.startswith(("prio:", "topic:")) and label not in labels:
            labels.append(label)
    return labels


def compose(manifest: Manifest, *, kind: str, sender: str, to: list[str], phrase: str,
            sent: str, sections: dict[str, str], re_: str = "none", needs: str | None = None,
            due: str = "none", basis: str | None = None,
            extra_labels: list[str] | None = None) -> tuple[str, str, list[str]]:
    """Build (title, body, labels) for a new message. Raises ValueError if it would not conform."""
    if kind not in TYPES:
        raise ValueError(f"unknown message type: {kind}")
    spec = TYPES[kind]
    author = manifest.get(sender)
    if author is None:
        raise ValueError(f"sender is not a channel participant: {sender}")
    recipients = [r for r in (manifest.get(ref) for ref in to) if r is not None]
    if not to or len(recipients) != len(to):
        raise ValueError(f"every recipient must be a channel participant: {', '.join(to)}")

    labels = [f"from:{author.id}", *(f"to:{r.id}" for r in recipients), f"type:{kind}",
              *(extra_labels or [])]
    envelope = {
        "From": author.name,
        "To": ", ".join(r.name for r in recipients),
        "Sent": sent,
        "Re": re_ or "none",
        "Needs": needs or spec.needs[0],
        "Due": due or "none",
    }
    if basis:
        envelope["Basis"] = basis
    if not author.can("issues.label"):
        envelope["Labels"] = ", ".join(labels)

    known = {h.casefold(): h for h, _ in spec.required + spec.optional}
    given = {k.casefold(): v for k, v in sections.items()}
    unknown = sorted(set(given) - set(known))
    if unknown:
        raise ValueError(f"a {kind} has no section named: {', '.join(unknown)}")
    parts = [f"### {h}\n{v}" for h, v in envelope.items()]
    parts += [f"### {h}\n{given[h.casefold()].strip()}"
              for h, _ in spec.required + spec.optional if given.get(h.casefold(), "").strip()]
    body = "\n\n".join(parts) + "\n"
    title = f"[{kind}] {phrase.strip()}"

    problems = check(body, title=title, labels=labels, manifest=manifest)
    if problems:
        raise ValueError("; ".join(problems))
    return title, body, labels


def comment_keyword(comment: str) -> tuple[str | None, str | None]:
    """Return (sender name, state keyword) from the first line of a comment."""
    match = _COMMENT.match(comment.lstrip())
    if not match:
        return None, None
    keyword = match.group(2) if match.group(2) in KEYWORDS else None
    return match.group(1).strip(), keyword
