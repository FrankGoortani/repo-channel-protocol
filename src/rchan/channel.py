"""Check a channel repository against the protocol. See SPEC.md §8, §9, §13, §14."""
from __future__ import annotations

import csv
import io
import re
import subprocess
from pathlib import Path

from . import manifest as manifest_module
from . import render
from .manifest import Manifest, ManifestError
from .message import is_date as _is_date

FRONTMATTER_KEYS = ("id", "status", "version", "owner", "applies_to",
                    "approved_by", "approved_on", "supersedes")
STATUSES = ("draft", "active", "retired")
TRIAL_RESULTS = ("PASS", "PARTIAL", "FAIL", "CLAIMED")
_SUPERSEDES = re.compile(r"^[A-Za-z0-9_-]+@\d+$")


def parse_frontmatter(text: str) -> dict[str, str | list[str]] | None:
    """Read the restricted frontmatter of SPEC.md §8.3. None if the file has none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str | list[str]] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        line = re.sub(r"\s+#.*$", "", line).rstrip()
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"frontmatter line is not `key: value`: {line!r}")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            fields[key.strip()] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
        else:
            fields[key.strip()] = value.strip("\"'")
    raise ValueError("frontmatter is not closed with `---`")


def _as_list(value: str | list[str] | None) -> list[str]:
    if isinstance(value, list):
        return value
    return [value] if value else []


def check_instruction(text: str, m: Manifest) -> list[str]:
    """Problems with one instruction file's frontmatter."""
    try:
        fields = parse_frontmatter(text)
    except ValueError as error:
        return [str(error)]
    if fields is None:
        return ["missing frontmatter"]
    problems = [f"frontmatter is missing `{key}`" for key in FRONTMATTER_KEYS if key not in fields]
    problems += [f"`{key}` must be a single value, not a list"
                 for key in FRONTMATTER_KEYS
                 if key not in ("applies_to", "approved_by") and isinstance(fields.get(key), list)]
    if problems:
        return problems

    ids = {p.id for p in m.participants}
    approvers = {p.id for p in m.approvers}
    status = fields["status"]
    if status not in STATUSES:
        problems.append(f"`status` must be one of {', '.join(STATUSES)}")
    if not str(fields["version"]).isdigit() or int(str(fields["version"])) < 1:
        problems.append("`version` must be a positive integer")
    if fields["owner"] not in ids:
        problems.append(f"`owner` is not a participant: {fields['owner']!r}")
    applies = _as_list(fields["applies_to"])
    if not applies:
        problems.append("`applies_to` must name at least one participant")
    for pid in applies:
        if pid not in ids:
            problems.append(f"`applies_to` names someone who is not a participant: {pid!r}")
    supersedes = fields["supersedes"]
    if supersedes and not _SUPERSEDES.match(str(supersedes)):
        problems.append("`supersedes` must look like `ID@version`")

    approved_by = _as_list(fields["approved_by"])
    approved_on = fields["approved_on"]
    for pid in approved_by:
        if pid not in approvers:
            problems.append(f"`approved_by` names someone who is not an approver: {pid!r}")
    if status == "active":
        if not approved_by:
            problems.append("an active file needs `approved_by`")
        elif m.approval == "all" and set(approved_by) != approvers:
            problems.append("this channel requires every approver in `approved_by`")
        if not _is_date(approved_on):
            problems.append("an active file needs `approved_on` as YYYY-MM-DD")
    if status == "draft" and (approved_by or approved_on):
        problems.append("a draft must not carry `approved_by` or `approved_on`")
    return problems


def lint(directory: str | Path) -> tuple[list[str], list[str]]:
    """Check a channel directory. Returns (errors, warnings)."""
    root = Path(directory)
    try:
        m = manifest_module.load(root)
    except ManifestError as error:
        return error.problems, []
    errors: list[str] = []
    warnings: list[str] = []
    note = manifest_module.version_note(m)
    if note:
        warnings.append(note)

    for relative, content in render.generated(m).items():
        path = root / relative
        if not path.is_file():
            errors.append(f"{relative}: missing (run `rchan init`)")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"{relative}: out of date with channel.toml (run `rchan init`)")
    if m.identity == "shared" and (root / ".github/CODEOWNERS").exists():
        warnings.append(".github/CODEOWNERS has no effect in shared identity mode")

    if m.profile == "core":
        return errors, warnings

    if not (root / "shared/RULES.md").is_file():
        errors.append("shared/RULES.md: missing")
    seen_ids: dict[str, str] = {}
    for path in sorted([*root.glob("shared/*.md"), *root.glob("playbooks/*.md")]):
        relative = path.relative_to(root).as_posix()
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        for problem in check_instruction(text, m):
            errors.append(f"{relative}: {problem}")
        try:
            fields = parse_frontmatter(text) or {}
        except ValueError:
            fields = {}
        file_id = str(fields.get("id", ""))
        if file_id and file_id in seen_ids:
            errors.append(f"{relative}: id {file_id} is also used by {seen_ids[file_id]}")
        seen_ids.setdefault(file_id, relative)
        if fields.get("status") == "draft":
            warnings.append(f"{relative}: draft, not in force")
    for p in m.participants:
        if p.kind == "agent" and not (root / f"participants/{p.id}/BRIEF.md").is_file():
            errors.append(f"participants/{p.id}/BRIEF.md: missing")

    for path in sorted(root.glob("ledgers/*.csv")):
        relative = path.relative_to(root).as_posix()
        rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
        if not rows:
            errors.append(f"{relative}: a ledger needs a header row")
            continue
        for number, row in enumerate(rows[1:], 2):
            if row and len(row) != len(rows[0]):
                errors.append(f"{relative}:{number}: {len(row)} fields, header has {len(rows[0])}")

    if m.profile == "full":
        errors += _check_trials(root, m)
    return errors, warnings


def _check_trials(root: Path, m: Manifest) -> list[str]:
    path = root / "ledgers/capability-trials.csv"
    if not path.is_file():
        return ["ledgers/capability-trials.csv: missing"]
    text = path.read_text(encoding="utf-8")
    if not text.startswith(render.TRIALS_HEADER.strip()):
        return ["ledgers/capability-trials.csv: header must be " + render.TRIALS_HEADER.strip()]
    problems = []
    ids = {p.id for p in m.participants}
    for number, row in enumerate(csv.DictReader(io.StringIO(text)), 2):
        where = f"ledgers/capability-trials.csv:{number}"
        if not _is_date(row.get("date")):
            problems.append(f"{where}: `date` must be YYYY-MM-DD")
        if row.get("participant") not in ids:
            problems.append(f"{where}: `participant` is not in the manifest")
        if row.get("result") not in TRIAL_RESULTS:
            problems.append(f"{where}: `result` must be one of {', '.join(TRIAL_RESULTS)}")
        if not (row.get("evidence") or "").strip():
            problems.append(f"{where}: `evidence` is required")
        if row.get("result") != "CLAIMED" and row.get("observed_by") not in ids:
            problems.append(f"{where}: `observed_by` must be a participant")
    return problems


def ledger_changes(directory: str | Path, base: str) -> list[str]:
    """Ledger rows edited or removed since git ref ``base``. Ledgers are append-only (§8.5)."""
    root = Path(directory)

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)

    listing = git("ls-tree", "-r", "--name-only", base, "--", "ledgers")
    if listing.returncode != 0:
        return [f"cannot read git ref {base!r}: {listing.stderr.strip()}"]
    problems = []
    for relative in listing.stdout.split():
        if not relative.endswith(".csv"):
            continue
        before = git("show", f"{base}:{relative}").stdout
        path = root / relative
        if not path.is_file():
            problems.append(f"{relative}: ledger was removed")
            continue
        # Every earlier line must survive whole: the old text, ended with a newline,
        # must be a prefix of the new text.
        earlier = before if before.endswith("\n") or not before else before + "\n"
        now = path.read_text(encoding="utf-8")
        if now != before and not now.startswith(earlier):
            problems.append(f"{relative}: existing rows were edited or removed since {base}")
    return problems
