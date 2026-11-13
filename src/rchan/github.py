"""The commands that talk to GitHub, through the `gh` CLI.

Everything here goes through ``Runner`` so tests can substitute a fake.
"""
from __future__ import annotations

import json
import subprocess
from typing import Callable

from . import message, render
from .manifest import Manifest

# (argv, stdin) -> stdout. Raises RuntimeError on failure.
Runner = Callable[[list[str], str | None], str]


def gh(argv: list[str], stdin: str | None = None) -> str:
    try:
        done = subprocess.run(["gh", *argv], input=stdin, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise RuntimeError("the GitHub CLI `gh` is required: https://cli.github.com") from error
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip() or f"gh {' '.join(argv)} failed")
    return done.stdout


def sync_labels(m: Manifest, run: Runner = gh) -> list[str]:
    """Create or update every protocol label on the channel repository."""
    names = []
    for name, color, description in render.labels(m):
        run(["label", "create", name, "--repo", m.repository, "--color", color,
             "--description", description, "--force"], None)
        names.append(name)
    return names


def open_issues(m: Manifest, run: Runner = gh) -> list[dict]:
    out = run(["issue", "list", "--repo", m.repository, "--state", "open", "--limit", "500",
               "--json", "number,title,labels,updatedAt,body"], None)
    issues = json.loads(out)
    for issue in issues:
        issue["labels"] = [label["name"] for label in issue["labels"]]
    return issues


def inbox(m: Manifest, who: str, run: Runner = gh) -> tuple[list[dict], list[dict]]:
    """Return (inbox, unaddressed) for a participant.

    ``inbox`` is the open issues labelled ``to:{id}``, high priority first, then
    oldest first. ``unaddressed`` is filled only for the steward: open issues with
    no ``to:`` label at all, each with the labels its body says it should carry
    (SPEC.md §7.7).
    """
    participant = m.get(who)
    if participant is None:
        raise ValueError(f"not a channel participant: {who}")
    issues = open_issues(m, run)
    mine = [i for i in issues if f"to:{participant.id}" in i["labels"]]
    mine.sort(key=lambda i: ("prio:high" not in i["labels"], i["number"]))
    unaddressed = []
    if participant.id == m.steward.id:
        for issue in issues:
            if not any(label.startswith("to:") for label in issue["labels"]):
                issue["suggested"] = message.expected_labels(issue["body"], issue["title"], m)
                unaddressed.append(issue)
    return mine, unaddressed


def find_duplicate(m: Manifest, title: str, run: Runner = gh) -> int | None:
    """The number of an open issue with exactly this title, if there is one."""
    for issue in open_issues(m, run):
        if issue["title"].strip().casefold() == title.strip().casefold():
            return issue["number"]
    return None


def send(m: Manifest, title: str, body: str, labels: list[str], run: Runner = gh) -> str:
    """Open the issue and return its URL. Labels are applied only if the sender can."""
    argv = ["issue", "create", "--repo", m.repository, "--title", title, "--body-file", "-"]
    sender = m.get(message.parse_body(body).get("from", ""))
    if sender is None or sender.can("issues.label"):
        for label in labels:
            argv += ["--label", label]
    return run(argv, body).strip()
