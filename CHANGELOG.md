# Changelog

All notable changes to the specification and the reference tooling. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow
[Semantic Versioning](https://semver.org/); before 1.0 a minor version may break
existing channels, and such changes are marked **Breaking**.

## [0.1.1] - 2026-11-12

### Tooling

- `rchan init` now renders `PROTOCOL.md` for the channel's profile. A `core` channel is
  no longer told about instruction files, trust tiers or capability trials it does not
  use, and a `governed` channel is no longer told about tiers and trials. A `core`
  channel gets no starting rules, playbooks, briefs or ledgers, and a `governed`
  channel no trials ledger.
- In every profile, the "What you may act on" list in `PROTOCOL.md` is now bulleted
  rather than numbered, so that items can be dropped per profile. Existing channels
  need `rchan init` to regenerate; nothing else changes for a `full` channel.

## [0.1.0] - 2026-11-12

First public draft.

### Specification

- Channel model: participants, approvers, steward, and the `channel.toml` manifest.
- Two identity modes, `distinct` and `shared`, with the guarantees of each stated.
- Authority rules: approved instruction files only; messages cannot widen authority;
  quoted content is data; silence is not approval.
- Five message types (`request`, `handoff`, `question`, `decision`, `report`) with a
  fixed envelope, labels, comment keywords and lifecycle.
- Fallbacks for participants that cannot label, close, comment, read comments, commit
  or open pull requests.
- Instruction files with approval frontmatter, and a proposal process for changing them.
- Trust tiers `standard` and `restricted`.
- Relay rules for a bridge between channels.
- Append-only ledgers and the capability-trials ledger.
- Conformance profiles `core`, `governed` and `full`.

### Tooling

- `rchan init`, `lint`, `check`, `inbox`, `send` and `labels`.

### Documentation

- Quick start, guides for humans and for agents, security, rationale and prior art.
- Five Agent Skills: inbox, send, propose, steward, setup.
- A worked example channel with message transcripts.

[0.1.1]: https://github.com/FrankGoortani/repo-channel-protocol/releases/tag/v0.1.1
[0.1.0]: https://github.com/FrankGoortani/repo-channel-protocol/releases/tag/v0.1.0
