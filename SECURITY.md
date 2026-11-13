# Security policy

## Reporting a vulnerability

Please report privately through GitHub:
**[Report a vulnerability](https://github.com/FrankGoortani/repo-channel-protocol/security/advisories/new)**.
Do not open a public issue.

Include what you found, how to reproduce it, and what an attacker could do with it.
You will get an acknowledgement within seven days.

## What counts

- **In the tooling (`rchan`):** anything that lets crafted input (a manifest, a message
  body, a ledger, an issue fetched from GitHub) execute code, write outside the channel
  directory, or cause a non-conforming channel or message to be reported as conforming.
- **In the specification:** a flaw in the protocol's rules that lets a participant gain
  authority the rules are meant to deny it, beyond the limits already documented in
  [docs/security.md](docs/security.md).

## What does not

- The documented limits of shared identity mode (sender names are claims, not proof).
- A language model failing to follow the protocol. The protocol reduces that risk and
  says it does not remove it.
- Vulnerabilities in GitHub or in an agent platform. Report those to their owners.

## Supported versions

The latest release. The protocol is pre-1.0; fixes are not backported.
