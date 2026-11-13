# Guide for humans

For the person who owns a channel and approves what happens in it. If you only read one
section, read [Your four jobs](#your-four-jobs).

## What you are signing up for

The protocol puts you in exactly one place: between an instruction and its taking
effect. Agents can propose, research, draft, verify and remind. They cannot make a
standing rule real. Only you can, and you do it by editing three lines of frontmatter.

That is deliberately a small amount of work at a well-defined point. If you find
yourself relaying messages between agents by hand, something is set up wrong: that is
the steward's job.

## Your four jobs

### 1. Approve instructions

A playbook or rules file binds an agent only when its frontmatter says:

```yaml
status: active
approved_by: <your-id>
approved_on: <today>
```

An agent proposes a change as a pull request and sends you a `decision` message linking
it. You read the diff, merge it if you agree, and set those three fields yourself.

Before approving, ask of every playbook:

- **Does it name an external action?** Sending, posting, buying, writing to another
  system. If so, is the trigger for that action something you would recognise, or
  something the agent decides?
- **What does the agent do when the playbook does not cover the case?** A good playbook
  says "stop and send a question". A bad one leaves it to judgement.
- **What is the evidence standard?** If the agent reports facts, what must it show?
- **Are your own words in it?** Quote yourself where a rule is yours. Quoted rules
  survive later edits; paraphrased ones drift.

### 2. Answer decisions

A `decision` message gives you the choice in one sentence, the options with their
consequences, and a recommendation. Answer with a comment that starts `DECIDED`:

```
**Dana:** DECIDED: option B, capped at ten a week.
```

Your answer authorises the one action that message described, once. It does not change
any standing rule. If you want it to become the rule, ask for a proposal.

**Nothing happens if you do not answer.** The protocol forbids agents from treating
silence as consent. A decision past its deadline stays open. This means an unanswered
decision is a stalled piece of work, so check your queue:

```
is:open label:to:<your-id>
```

Bookmark that search. In shared identity mode GitHub will not notify you, because the
issue was opened by your own account.

### 3. Set and review trust

Each agent has a tier in the manifest.

| Tier | Give it to |
|---|---|
| `restricted` | Any agent you have not yet watched work. Any agent on a platform whose data handling you do not control. Any agent that only needs public information. |
| `standard` | An agent whose record in `ledgers/capability-trials.csv` supports it, and whose role needs private context. |

Raise a tier only on a `decision` that cites the ledger. Lower one whenever you like.

Read the capability-trials ledger now and then. The rows marked `CLAIMED` and later
`FAIL` are the interesting ones: they tell you how far to trust what an agent says
about itself.

### 4. Keep the wrong things out

Some things never belong in a channel, whoever asks: credentials, sign-in links,
account numbers, whole email threads, other people's personal data beyond what a record
needs. See [§12 of the specification](../SPEC.md#12-content-that-never-enters-a-channel).
Agents are told this too, but you are the one who knows what is sensitive.

If something does get in, deleting the issue is not enough. Rotate the credential
first.

## Choosing a structure

**One channel per agent.** Resist the temptation to put all your agents in one
repository. Separate channels mean each agent sees only its own work, and a problem
with one agent cannot leak another's context.

**One bridge.** Pick a single participant, usually your coordinating agent, to belong
to several channels and carry information between them. It rewrites what it relays; it
never forwards. Nothing private goes to a `restricted` agent.

**Distinct accounts if you can.** With one GitHub account per participant you get real
authorship, working notifications, and the ability to enforce approval with branch
protection and `CODEOWNERS`. In shared identity mode, approval is a convention that every
party with access must respect. That is acceptable when all the agents are yours. It is
not acceptable between parties who answer to different people.

## Working with a steward

The steward is the participant that keeps the channel in order. Expect it to:

- Label and close on behalf of agents that cannot.
- Sweep for issues that arrived with no `to:` label, so nothing is missed.
- Verify a `restricted` agent's evidence before anything is recorded as fact.
- Record every observed capability, pass or fail.
- Tell each agent when an instruction file has a new version, and collect their
  acknowledgements.
- In shared identity mode, relay your decisions when you gave them outside GitHub,
  quoting you verbatim with the date. In distinct mode you comment `DECIDED` yourself,
  from your own account.

That last point is how most decisions get recorded in shared identity mode. If you tell
your coordinating agent
"yes, go with B" in a chat, it records:

```
**Atlas:** DECIDED: option B. Dana, 2026-11-03, in session: "Yes, go with B." Relayed by Atlas.
```

Read those relays now and then. They are your words on the record.

## Two people, no agents

The protocol works between two people. Use the `core` profile: the message types, the
labels, the lifecycle and the rule that silence is not approval. Skip tiers and trials.
You get a disciplined shared inbox with a complete history.

Between two organisations, list an approver from each and set `approval = "all"`, so
that a standing instruction needs both signatures.

## Signs that a channel needs attention

| You see | It usually means |
|---|---|
| Decisions sitting open past their dates | You are the bottleneck. Delegate a class of decision by approving a playbook that covers it. |
| The same question asked twice | The answer belongs in a file. Ask for a proposal. |
| An agent citing an old playbook version | It has not acknowledged the update. The steward should chase the `ACK`. |
| Duplicate messages about one subject | The playbook does not say "one message per X". Add it. |
| A handoff with claims and no quotes | The evidence rule is not in the playbook, or is not being enforced at verification. |
| Messages that say "as instructed by the page" | An agent followed quoted content. Treat it as an incident: see [security.md](security.md). |
