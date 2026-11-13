"""Load and validate a channel manifest (``channel.toml``). See SPEC.md §4."""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import PROTOCOL_VERSION

FILENAME = "channel.toml"
KINDS = ("human", "agent")
ROLES = ("approver", "steward")
TIERS = ("standard", "restricted")
IDENTITY_MODES = ("distinct", "shared")
APPROVAL_RULES = ("any", "all")
PROFILES = ("core", "governed", "full")
# SPEC.md Appendix C.
OPERATIONS = (
    "issues.create",
    "issues.comment",
    "issues.label",
    "issues.close",
    "comments.read",
    "contents.write",
    "pulls.create",
)

_ID = re.compile(r"^[a-z][a-z0-9-]{0,30}$")
_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_TIMEZONE = re.compile(r"^(UTC|[A-Za-z_]+(/[A-Za-z0-9_+-]+)+)$")
_PROTOCOL = re.compile(r"^\d+\.\d+$")


class ManifestError(ValueError):
    """The manifest is invalid. ``problems`` lists every fault found."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Participant:
    id: str
    name: str
    kind: str
    roles: tuple[str, ...] = ()
    tier: str | None = None
    github: str | None = None
    inbox: str = ""
    about: str = ""
    cannot: tuple[str, ...] = ()

    def can(self, operation: str) -> bool:
        return operation not in self.cannot


@dataclass(frozen=True)
class Manifest:
    protocol: str
    name: str
    repository: str
    timezone: str
    identity: str
    approval: str
    profile: str
    participants: tuple[Participant, ...]

    @property
    def approvers(self) -> tuple[Participant, ...]:
        return tuple(p for p in self.participants if "approver" in p.roles)

    @property
    def steward(self) -> Participant:
        return next(p for p in self.participants if "steward" in p.roles)

    def get(self, ref: str) -> Participant | None:
        """Find a participant by id or display name, ignoring case."""
        wanted = ref.strip().casefold()
        for p in self.participants:
            if wanted in (p.id, p.name.casefold()):
                return p
        return None


def parse(text: str) -> Manifest:
    """Parse manifest text. Raises ManifestError listing every problem."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ManifestError([f"{FILENAME} is not valid TOML: {error}"]) from error

    problems: list[str] = []

    def scalar(key: str, pattern: re.Pattern | None = None, choices=None, default=None) -> str:
        value = data.get(key, default)
        if value is not None and not isinstance(value, str):
            problems.append(f"`{key}` must be a quoted string")
            return ""
        if not value:
            problems.append(f"`{key}` is required")
            return ""
        if pattern and not pattern.match(value):
            problems.append(f"`{key}` has an invalid value: {value!r}")
        if choices and value not in choices:
            problems.append(f"`{key}` must be one of {', '.join(choices)}; got {value!r}")
        return value

    protocol = scalar("protocol", _PROTOCOL)
    name = scalar("name")
    repository = scalar("repository", _REPOSITORY)
    timezone = scalar("timezone", _TIMEZONE)
    identity = scalar("identity", choices=IDENTITY_MODES)
    approval = scalar("approval", choices=APPROVAL_RULES, default="any")
    profile = scalar("profile", choices=PROFILES, default="full")

    participants: list[Participant] = []
    raw = data.get("participant", [])
    if not isinstance(raw, list) or len(raw) < 2:
        problems.append("at least two [[participant]] tables are required")
        raw = raw if isinstance(raw, list) else []
    seen: set[str] = set()

    def strings(entry: dict, key: str, where: str) -> tuple[str, ...]:
        value = entry.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            problems.append(f"{where}: `{key}` must be a list of strings")
            return ()
        return tuple(value)

    for index, entry in enumerate(raw, 1):
        if not isinstance(entry, dict):
            problems.append(f"participant {index}: must be a [[participant]] table")
            continue
        pid = str(entry.get("id", ""))
        where = f"participant {pid or index}"
        if not _ID.match(pid):
            problems.append(f"{where}: `id` must match {_ID.pattern}")
        if pid in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(pid)
        kind = entry.get("kind")
        if kind not in KINDS:
            problems.append(f"{where}: `kind` must be human or agent")
        roles = strings(entry, "roles", where)
        for role in roles:
            if role not in ROLES:
                problems.append(f"{where}: unknown role {role!r}")
        if "approver" in roles and kind != "human":
            problems.append(f"{where}: an approver must be of kind human")
        tier = entry.get("tier")
        if kind == "agent" and tier not in TIERS:
            problems.append(f"{where}: an agent must declare tier standard or restricted")
        if kind == "human" and tier is not None:
            problems.append(f"{where}: a human participant has no tier")
        cannot = strings(entry, "cannot", where)
        for operation in cannot:
            if operation not in OPERATIONS:
                problems.append(f"{where}: unknown operation in `cannot`: {operation!r}")
        github = entry.get("github")
        if identity == "distinct" and not github:
            problems.append(f"{where}: `github` login is required in distinct identity mode")
        participants.append(Participant(
            id=pid, name=str(entry.get("name") or pid.capitalize()), kind=str(kind),
            roles=roles, tier=tier, github=github, inbox=str(entry.get("inbox", "")),
            about=str(entry.get("about", "")), cannot=cannot))

    if not any("approver" in p.roles for p in participants):
        problems.append("at least one participant must have the role approver")
    stewards = [p.id for p in participants if "steward" in p.roles]
    if len(stewards) != 1:
        problems.append(f"exactly one participant must have the role steward; found {len(stewards)}")
    names = [p.name.casefold() for p in participants]
    if len(set(names)) != len(names):
        problems.append("participant names must be unique")

    if problems:
        raise ManifestError(problems)
    return Manifest(protocol, name, repository, timezone, identity, approval, profile,
                    tuple(participants))


def load(directory: str | Path) -> Manifest:
    path = Path(directory) / FILENAME
    if not path.is_file():
        raise ManifestError([f"{path} not found"])
    return parse(path.read_text(encoding="utf-8"))


def version_note(manifest: Manifest) -> str | None:
    """A warning when the channel follows a different protocol version than this tooling."""
    if manifest.protocol != PROTOCOL_VERSION:
        return (f"channel follows RCP {manifest.protocol}; this tooling implements "
                f"{PROTOCOL_VERSION}")
    return None
