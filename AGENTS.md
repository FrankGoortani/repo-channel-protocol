# Instructions for agents working on this repository

This repository holds a specification, its documentation and a small reference tool.
These instructions are for coding agents changing the repository itself. To *use* the
protocol in a channel, read [docs/guide-for-agents.md](docs/guide-for-agents.md).

## Layout

| Path | Notes |
|---|---|
| `SPEC.md` | Normative. Every behavioural change starts here. |
| `src/rchan/` | Reference tooling. Python 3.11+, standard library only. No dependencies. |
| `src/rchan/template/PROTOCOL.md` | The per-channel rendering of the spec. Must agree with `SPEC.md`. |
| `tests/test_rchan.py` | `python -m unittest discover -s tests` |
| `examples/digest-channel/` | A generated channel plus transcripts. The tests lint it. |
| `docs/`, `skills/` | Informative. They restate the spec; they must not add rules. |

## Rules

1. **The spec is the source of truth.** If you change behaviour in `src/rchan`, the
   template, a guide or a skill, change `SPEC.md` in the same commit, and the other way
   round. A rule that appears in a guide but not in the spec is a bug.
2. **No dependencies.** The tooling must run on a bare Python install.
3. **Tests first for tooling changes.** Run the suite before and after.
4. **Regenerate the example** after any change to the template or generator:
   `PYTHONPATH=src python -m rchan init --dir examples/digest-channel`, then run the tests.
5. **Examples are fictional.** Use `example.org`, `example.net` and invented names. No
   real people, companies, products or data.
6. **Plain language.** Short sentences. No marketing. Say what a thing does.
7. **Normative keywords** (MUST, SHOULD, MAY) appear in capitals only in `SPEC.md`.
8. **Record user-visible changes** in `CHANGELOG.md`, and mark breaking ones.

## Checks before you finish

```bash
python -m unittest discover -s tests
PYTHONPATH=src python -m rchan lint --dir examples/digest-channel
```
