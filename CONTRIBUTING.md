# Contributing

Thank you for considering it. This is a young specification and the most useful
contributions are evidence: what happened when you ran a channel.

## Ways to help

| You have | Do this |
|---|---|
| A report from a real channel: something that worked, failed or was unclear | Open a **Field report** issue. These shape the protocol more than anything else. |
| A place where the spec is ambiguous, contradicts itself or disagrees with the tooling | Open a **Spec feedback** issue. Quote the section. |
| A bug in `rchan` | Open a **Bug** issue with the command, the output and what you expected. |
| A proposed change to the protocol | Open a **Spec feedback** issue first. See below. |
| A fix to documentation or tooling | Open a pull request. |
| A security problem | Do not open an issue. See [SECURITY.md](SECURITY.md). |

Never include real channel content in an issue: no private messages, names or data.
Reduce it to a fictional case that shows the same thing.

## Changing the specification

The protocol requires that standing instructions change by proposal and approval. The
specification holds itself to the same standard.

1. **Open an issue** describing the problem, with a concrete case. A change that solves
   an observed problem will go further than one that solves a hypothetical one.
2. **Discuss** until the problem is agreed. The solution comes second.
3. **Open a pull request** titled `[proposal] SPEC §<n>: <change>` that changes, in one
   commit:
   - `SPEC.md`
   - `src/rchan/template/PROTOCOL.md`, if the rule appears there
   - the tooling and tests, if the rule is machine-checkable
   - the guides and skills that restate the rule
   - `CHANGELOG.md`, marked **Breaking** if existing channels would stop conforming
4. **The maintainer merges.** Silence is not approval here either.

What makes a proposal likely to be accepted:

- It removes a failure that happened.
- It keeps the protocol usable by an agent that can only read and write issues.
- It needs no server, bot or webhook.
- It makes the specification shorter, or no longer.

What is out of scope: agent frameworks, runtimes, hosted services, and anything that
requires all participants to run the same software.

## Development

```bash
git clone https://github.com/FrankGoortani/repo-channel-protocol
cd repo-channel-protocol
python -m unittest discover -s tests              # needs Python 3.11+, nothing else
PYTHONPATH=src python -m rchan --help
```

- The tooling uses the standard library only. Please keep it that way.
- Add or change a test with every change in behaviour.
- After changing the template or generator, regenerate the example channel:
  `PYTHONPATH=src python -m rchan init --dir examples/digest-channel`
- Keep examples fictional: `example.org`, invented names.

## Style

- Plain language and short sentences. Say what a thing does.
- British or American spelling is fine within a file; do not mix them in one.
- MUST, SHOULD and MAY in capitals belong only in `SPEC.md`.
- Commit subjects: imperative, under 72 characters, prefixed with the area:
  `spec:`, `rchan:`, `docs:`, `skills:`, `examples:`.

## Licence

By contributing you agree that your contribution is licensed under the
[Apache License 2.0](LICENSE), as section 5 of that licence provides.

## Conduct

This project follows a [code of conduct](CODE_OF_CONDUCT.md).
