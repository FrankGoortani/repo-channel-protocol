"""Command line for the Repo Channel Protocol reference tooling."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from . import __version__, channel, github, manifest, message, render


def _load(directory: str) -> manifest.Manifest:
    try:
        return manifest.load(directory)
    except manifest.ManifestError as error:
        for problem in error.problems:
            print(f"error: {problem}", file=sys.stderr)
        raise SystemExit(2) from error


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    path = root / manifest.FILENAME
    if not path.exists():
        root.mkdir(parents=True, exist_ok=True)
        path.write_text(render.STARTER_MANIFEST, encoding="utf-8")
        print(f"create   {path}")
        print("\nEdit channel.toml to describe your participants, then run `rchan init` again.")
        return 0
    m = _load(args.dir)
    for action, relative in render.write(root, m):
        print(f"{action:<8} {relative}")
    print("\nNext: `rchan lint`, commit and push, then `rchan labels` to create the labels on GitHub.")
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    errors, warnings = channel.lint(args.dir)
    if args.base:
        errors += channel.ledger_changes(args.dir, args.base)
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    if not errors:
        print("ok: channel conforms" + (f" ({len(warnings)} warning(s))" if warnings else ""))
    return 1 if errors else 0


def _read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as error:
        print(f"error: cannot read {path}: {error.strerror}", file=sys.stderr)
        raise SystemExit(2) from error


def cmd_check(args: argparse.Namespace) -> int:
    body = sys.stdin.read() if args.file == "-" else _read(args.file)
    m = None
    if (Path(args.dir) / manifest.FILENAME).exists():
        m = _load(args.dir)
    else:
        print(f"note: no {manifest.FILENAME} in {args.dir}; participant names were not checked")
    labels = message.split_list(args.labels) if args.labels is not None else None
    problems = message.check(body, title=args.title, labels=labels, manifest=m, kind=args.type)
    for problem in problems:
        print(f"error: {problem}")
    if not problems:
        print("ok: message conforms")
    return 1 if problems else 0


def cmd_inbox(args: argparse.Namespace) -> int:
    m = _load(args.dir)
    try:
        mine, unaddressed = github.inbox(m, args.who)
    except (ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    participant = m.get(args.who)
    assert participant is not None
    print(f"Inbox for {participant.name}: {len(mine)} open")
    for issue in mine:
        flags = " ".join(l for l in issue["labels"] if l.startswith(("state:", "prio:")))
        print(f"  #{issue['number']:<5} {issue['title']}  {flags}".rstrip())
    if unaddressed:
        print(f"\nUnaddressed (no `to:` label): {len(unaddressed)}")
        for issue in unaddressed:
            print(f"  #{issue['number']:<5} {issue['title']}")
            print(f"         labels from body: {', '.join(issue['suggested']) or 'none found'}")
    return 0


def _now(zone: str) -> str:
    try:
        return datetime.now(ZoneInfo(zone)).strftime("%Y-%m-%d %H:%M ") + zone
    except ZoneInfoNotFoundError:
        return datetime.now().astimezone().isoformat(timespec="minutes")


def cmd_send(args: argparse.Namespace) -> int:
    m = _load(args.dir)
    sections = {}
    for flag, items in (("--section", args.section), ("--section-file", args.section_file)):
        for item in items or []:
            heading, separator, value = item.partition("=")
            if not separator:
                print(f"error: {flag} takes HEADING=VALUE, got {item!r}", file=sys.stderr)
                return 2
            sections[heading.strip()] = _read(value) if flag == "--section-file" else value
    extra = [f"topic:{t}" for t in args.topic or []] + (["prio:high"] if args.high else [])
    try:
        title, body, labels = message.compose(
            m, kind=args.type, sender=args.sender, to=args.to, phrase=args.title,
            sent=_now(m.timezone), sections=sections, re_=args.re, needs=args.needs,
            due=args.due, basis=args.basis, extra_labels=extra)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(f"title:  {title}\nlabels: {', '.join(labels)}\n\n{body}", end="")
        return 0
    try:
        duplicate = None if args.force else github.find_duplicate(m, title)
        if duplicate:
            print(f"error: open issue #{duplicate} has the same title. Comment there, "
                  "or pass --force.", file=sys.stderr)
            return 1
        print(github.send(m, title, body, labels))
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


def cmd_labels(args: argparse.Namespace) -> int:
    m = _load(args.dir)
    try:
        names = github.sync_labels(m)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"ok: {len(names)} labels on {m.repository}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rchan", description="Reference tooling for the Repo Channel Protocol.")
    parser.add_argument("--version", action="version", version=f"rchan {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    def add(name: str, handler, help_: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=help_, description=help_)
        sub.add_argument("--dir", default=".", help="channel directory (default: .)")
        sub.set_defaults(handler=handler)
        return sub

    add("init", cmd_init, "Write a starter channel.toml, or generate the channel from it.")

    lint = add("lint", cmd_lint, "Check a channel repository against the protocol.")
    lint.add_argument("--base", metavar="REF",
                      help="also fail if ledger rows were edited or removed since this git ref")

    check = add("check", cmd_check, "Check one message body (a file, or - for stdin).")
    check.add_argument("file")
    check.add_argument("--title", help="the issue title")
    check.add_argument("--labels", help="the issue's labels, comma-separated")
    check.add_argument("--type", choices=list(message.TYPES), help="message type, if no title")

    inbox = add("inbox", cmd_inbox, "List a participant's open messages (needs gh).")
    inbox.add_argument("who", help="participant id or name")

    send = add("send", cmd_send, "Compose a conforming message and open it (needs gh).")
    send.add_argument("type", choices=list(message.TYPES))
    send.add_argument("--from", dest="sender", required=True, help="sender id or name")
    send.add_argument("--to", action="append", required=True, help="recipient; repeat for several")
    send.add_argument("--title", required=True, help="short phrase (the [type] prefix is added)")
    send.add_argument("--section", action="append", metavar="HEADING=TEXT",
                      help="a type-specific section, given inline. Repeat.")
    send.add_argument("--section-file", action="append", metavar="HEADING=PATH",
                      help="a type-specific section, read from a file. Repeat.")
    send.add_argument("--re", default="none", help="related issues, files or ids")
    send.add_argument("--needs", choices=list(message.NEEDS))
    send.add_argument("--due", default="none", help="YYYY-MM-DD")
    send.add_argument("--basis", help="instruction files acted under, e.g. playbooks/x.md@3")
    send.add_argument("--topic", action="append", help="adds a topic:<name> label; repeat")
    send.add_argument("--high", action="store_true", help="adds prio:high")
    send.add_argument("--dry-run", action="store_true", help="print the message, send nothing")
    send.add_argument("--force", action="store_true", help="send even if the title is a duplicate")

    add("labels", cmd_labels, "Create or update the protocol labels on GitHub (needs gh).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
