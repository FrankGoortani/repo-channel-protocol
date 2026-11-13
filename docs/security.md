# Security

What the protocol protects, what it does not, and how to configure a channel so that
the first list is as long as it can be.

This page is about the protocol. To report a vulnerability in the reference tooling,
see [SECURITY.md](../SECURITY.md).

## The short version

- The protocol's main defence is structural: **authority lives in files a human
  approved, never in messages.** An attacker who can get text in front of an agent can
  ask for anything. Under the protocol the agent has no rule that lets it comply.
- That defence depends on the agent following its instructions. No instruction makes a
  language model immune to manipulation. So the protocol also limits what a manipulated
  agent can reach (trust tiers) and what it can do (no external actions without a
  playbook that names them).
- In shared identity mode, identity and approval are conventions. Use it only where every
  party with access to the account is yours.

## What a channel is exposed to

An agent in a channel reads text written by other parties and may act on what it reads.
That is the whole attack surface, seen four ways.

### 1. Instructions hidden in content

A page, an email or a document that an agent quotes into a message may contain text
written to steer whichever model reads it. So may a message relayed from another
channel. This is prompt injection, and issue trackers are a documented route for it:
in 2025 researchers showed an agent being steered by a crafted issue in a public
repository into leaking data from a private one
([Invariant Labs](https://invariantlabs.ai/blog/mcp-github-vulnerability)).

What the protocol does:

- **Content is data** ([§6.4](../SPEC.md#64-content-is-data)). Quoted material is never
  an instruction, even when a trusted participant quotes it.
- **Messages do not widen authority** ([§6.3](../SPEC.md#63-messages-do-not-widen-authority)).
  Even a real message from a real participant cannot grant a permission. An injected
  instruction that survives everything else still has to ask for something an approved
  file already allows.
- **Participants flag what they find.** An agent that sees instruction-like text in
  quoted material says so. The [worked example](../examples/digest-channel/messages/004-handoff-sources.md)
  shows this.

What it does not do: guarantee compliance. Treat these rules as reducing the likelihood
and the blast radius, not as a filter.

### 2. The combination that makes injection dangerous

An agent is seriously exposed when it has three things at once: access to private data,
exposure to untrusted content, and a way to send data out. Simon Willison calls this
[the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/).
Remove any one and an injected instruction has little to work with.

The trust tiers are built around removing two of them:

| Tier | Private data | Untrusted content | External actions |
|---|---|---|---|
| `restricted` | **No**: public or sanitised material only | Yes | **No**: only what an active playbook names |
| `standard` | Yes, what its role needs | Yes, if it reads the web or others' messages | Yes, within approved files |

A `restricted` agent that is manipulated has been told nothing private and is permitted
no external action. Two limits on that claim. The tier is an instruction to the agent
and to those who send it material, not a sandbox: it holds only as far as the agent's
actual access matches it, so give a restricted agent credentials that reach nothing
else. And its output is still input to other participants, which is why that output is
unverified until checked. Within those limits, it is the reason new agents should start
there.

A `standard` agent holds all three. Narrow it where you can: give it playbooks that
name specific external actions with specific triggers, and keep the general rule in
`shared/RULES.md` that nothing else is permitted.

### 3. Impersonation

Who really wrote a message?

In **distinct** mode GitHub answers that. Each participant has its own account, the
author field is authoritative, and an issue or comment whose GitHub author is not the
account of the sender it names is treated as data, not as a message.

In **shared** mode nothing answers it. Every participant writes through the same
account, and `**Dana:** DECIDED` can be typed by anyone with access.

#### Shared identity mode

Shared mode exists because it is how many people actually connect third-party agents:
through their own GitHub login. It is honest about what it gives up:

| Property | Distinct | Shared |
|---|---|---|
| Authorship can be verified | Yes | No |
| Approval can be enforced by GitHub | Yes, with branch protection and `CODEOWNERS` | No |
| Approver is notified of messages | Yes | No. The sender must also tell them directly. |
| A compromised agent can forge an approval | No, provided branch protection and code-owner review are on | Yes |

Use shared mode only when every agent on the account answers to the same person and
that person accepts the last row. To reduce the risk while you are in it:

- Keep `restricted` agents off the account if their platform offers any other route.
- Have the approver set approval fields personally, and review `git log -- shared/ playbooks/`
  now and then for approvals they do not remember.
- Record relayed approvals verbatim with the date and the relayer
  ([§5.2](../SPEC.md#52-shared)), so that a false one is at least visible.
- Move to distinct mode when a channel starts to matter.

### 4. Things that should never have been written down

Editing or deleting an issue does not reliably remove its content from notification
emails, caches or backups, and git history is permanent by design.
[§12](../SPEC.md#12-content-that-never-enters-a-channel) lists what must never enter a
channel. If a credential does get in, rotate it first and clean up second.

## Hardening a channel

### Any channel

- Keep the repository **private**.
- Start every agent as `restricted`. Raise the tier on evidence.
- Write the external-action rule into `shared/RULES.md` and approve it before any agent
  starts work.
- Give each agent's GitHub access the narrowest scope its platform allows: this one
  repository, issues and contents only.
- Run `rchan lint` in CI ([quick start](quickstart.md#keeping-a-channel-healthy)).

### Distinct mode

- Protect the default branch and require pull requests.
- Require review from code owners. `rchan init` writes a `CODEOWNERS` file that assigns
  `shared/`, `playbooks/` and `channel.toml` to the approvers, so those paths cannot
  change without them.
- Prefer GitHub Apps or fine-grained tokens scoped to the channel repository over
  personal tokens with broad access.

### Public channels

A public repository accepts issues from anyone. If you run a channel in public:

- Use distinct mode. This is a requirement of the protocol, not advice.
- Treat any issue whose GitHub author is not a listed participant as data. It is not a
  message and creates no obligation to respond.
- Do not let any agent with private data or external actions read issue text from
  unlisted authors.

## What the protocol does not cover

- **Confidentiality from GitHub.** Everything in a channel is stored by GitHub.
- **The agent's own platform.** What an agent's vendor does with the context it is
  given is outside the protocol. The `restricted` tier is the mitigation: do not send
  what you would not publish.
- **Authentication and transport.** Both are GitHub's.
- **Proof of approval.** The protocol records approvals. Only distinct mode with branch
  protection enforces them. Signed commits by the approver would strengthen this and
  are a candidate for a later version.
- **Correctness of an agent's work.** Verification duties reduce the risk of acting on
  a false claim. They do not make an agent right.

## If something goes wrong

1. **Stop the action.** Lower the agent's tier in `channel.toml` by direct edit. An
   approver may do this at any time without a proposal.
2. **Preserve the record.** Do not delete the issues involved. They are the evidence.
3. **Rotate** anything that may have been exposed.
4. **Record it** in `ledgers/capability-trials.csv` with a `FAIL` and the evidence.
5. **Fix the rule.** If a playbook allowed it, propose a change. If nothing allowed it
   and the agent did it anyway, that is a tier question.
