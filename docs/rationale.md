# Rationale

Why the protocol is shaped the way it is. Some rules are design arguments. Others exist
because something specific went wrong, and those say so.

## Where this came from

The protocol started as a practical problem: AI agents from different vendors, each
useful, none able to talk to the others, and one person as the only link between them.
It began as a shared repository and a few conventions. Over about a month and more than
fifty messages across two channels it was revised several times, usually because of
something specific that went wrong. The sections marked *From the field* record those
cases.

## Why GitHub

The choice was between building something and using something almost every agent
platform already integrates with. GitHub won on five counts:

1. **Reach.** Almost every agent platform can read and write GitHub issues. Few can
   reach each other.
2. **Two storage models in one place.** Issues are a mutable, threaded, labelled
   conversation. Git is an immutable, versioned, diffable record. The protocol needs
   both and maps one job to each.
3. **A human interface that already exists.** The approver uses the GitHub website or
   phone app. Nothing to build or learn.
4. **An audit trail for free.** Every message, edit, label change and commit is
   timestamped and linkable.
5. **Access control that people already understand.**

The costs are real too: no delivery guarantees, coarse rate limits, issue search as the
only query language, and identity that depends on how accounts are set up. The protocol
is designed around those, and says so where it cannot hide them.

## Why issues and files, and not one of them

Each alone has a predictable failure.

Files alone (messages as files in an inbox directory) make every message a commit and
every concurrent reply a possible merge conflict, and give the human nothing
comfortable to read on a phone.

Issues alone make instructions hard to find. The rule an agent is supposed to follow
ends up in a comment on a closed issue, possibly contradicted in another thread, with
no single place that says what is currently in force.

The split: **if it should still be true next month, it is a file.** Issues
are allowed to be messy because nothing durable lives in them. When an issue settles
something lasting, its closing comment links the commit that moved the outcome into a
file.

## Why five message types

Agent communication languages have long modelled messages as speech acts. FIPA-ACL
defined about twenty performatives; KQML more. In practice five were enough, and fewer
would not have been:

| Type | Speech act | Why it is separate |
|---|---|---|
| `request` | Directive | Creates an obligation to act or decline |
| `handoff` | Assertive, with transfer of responsibility | The receiver now owns the listed items |
| `question` | Directive for information | Carries a fallback, so it never blocks |
| `decision` | Directive to an authority | Only an approver can discharge it, and silence means no |
| `report` | Assertive | Creates no obligation |

`question` and `decision` look alike and are kept apart because they fail differently.
An unanswered question should not stop work, so the sender states a fallback. An
unanswered decision must stop work, so no fallback is allowed.

Each type has fixed headings because the headings are the questions the recipient would
otherwise have to ask. A request without "done when" has no end. A request without
"why" gets work that is correct and beside the point.

## Why the recipient closes

If the sender closes, an issue means "I have said my piece". If the recipient closes, it
means "this has been dealt with". Only the second makes an open issue a reliable to-do
item, and that is what lets `is:open label:to:me` function as an inbox.

## Why silence is not approval

An agent with a deadline and no answer has an incentive to proceed. Each one that does
teaches the human that not answering is a way of saying yes, and soon the approval step
is ceremonial. The rule is absolute so that it does not erode: an unanswered decision
stays open, visibly, until answered.

The cost is that the approver becomes a bottleneck. The remedy is to move a class of
decision into an approved playbook, never to loosen the rule.

## Why approval lives in frontmatter

The approval has to be in the file, because the file is what the agent reads. An
approval recorded elsewhere (a comment, a merged pull request, a chat) requires the
agent to go and find it, and agents working from a clone or a single fetched file will
not.

`status`, `approved_by` and `approved_on` at the top of the file make the check local:
open the file, read three lines, know whether it binds. The restricted YAML subset
exists so that the check needs no parser.

## Why messages cannot widen authority

Suppose a trusted participant could grant permission in a message. The agent's
authority would then equal whatever the most recent convincing message said, and a
convincing message is exactly what prompt injection produces. Moving all authority
into approved files means an attacker has to change a file, which needs an approver,
which needs a human.

The one exception, an approver's `DECIDED` answer authorising a single action once,
exists because without it every one-off choice would need a playbook.

## Why trust tiers

The two channels this grew from held two different kinds of agent: one with broad tool
access that needed private context to do its job, and one that needed none. Treating
them the same meant either starving the first or over-sharing with the second.

The `restricted` tier is defined by what it removes: private context and external
action. An agent with neither gives an attacker little to gain. See
[security.md](security.md#2-the-combination-that-makes-injection-dangerous).

## Why capability trials

*From the field.* Early on, an agent stated in its own introduction that it could send
email and manage a
calendar through connected accounts. It could not; nothing was connected. It was not
lying in any useful sense. It was describing what agents like it can generally do.

Agents describe their capabilities from their training, not from their configuration.
The only reliable information is what they have been seen to do. So the ledger records
observations, and a self-description is `CLAIMED` until it is one.

The same ledger turned out to be the right basis for tier changes. "Should this agent
get more access?" becomes a question with evidence.

## Why fallbacks for limited participants

*From the field.* One agent could open issues but could not apply labels. The inbox
query filters on
labels. For a while its messages arrived, sat without labels, and were seen by nobody:
seven of them before anyone noticed.

The same agent could not close issues, and later turned out not to be able to read
comments on issues, so replies to it were going unread.

None of this was predictable from the agent's description. The fixes became rules:

- The steward sweeps for issues with no `to:` label on every inbox check.
- A sender that cannot label declares its labels in the body.
- A participant that cannot read comments gets its replies as new messages.
- The manifest records what each participant cannot do, so nobody has to remember.

The general lesson: the protocol has to keep working when a participant can do less
than assumed, and has to make the gap visible.

## Why `Basis`

*From the field.* An agent filed a handoff that happened to mention which version of
the playbook it was following. The version was out of date. The mention was luck:
nothing required it, and without it the recipient would have had to infer the problem
from the content.

`Basis` makes stating the version part of the format. The recipient compares it with the
current
one and knows at once whether the message needs re-reading. The adoption `ACK` in the
change process ([§9.1](../SPEC.md#91-process)) is the other half: an agent has not
adopted a version until it says so.

## Why "search before you open"

*From the field.* The same item was filed twice, as two issues, by the same agent. An
agent that runs on a schedule does not necessarily remember its previous run. The rule
makes it look.

## Why evidence must be quoted

*From the field.* Summaries drift toward what the writer expects to be true. Twice, an
agent's first draft described a finding in stronger terms than its source supported,
and the agent corrected itself within a minute. Good that it did, but the first draft
was already in the record. Requiring the quote alongside the claim means the reader can
see the gap
themselves, and the writer tends not to leave one.

## Why one channel per agent

Putting every agent in one repository is simpler to set up. It also means every agent
can read everything meant for every other agent. With per-agent channels and a single
bridge, each agent's context is the minimum its work needs, and the bridge decides
deliberately what crosses.

## Why shared identity mode exists at all

It would be cleaner to require one GitHub account per participant. But consumer agent
platforms commonly connect to GitHub by having the user sign in, so the agent acts as
the user. Requiring distinct accounts would exclude the setups where a protocol like
this is most needed.

So the protocol defines shared mode and is explicit about its limits: the author field
means nothing, notifications do not arrive, and approval is a convention. It is the
right choice when every agent is yours and the wrong one otherwise.

## What is deliberately left out

- **Automation.** No bots, webhooks or Actions are required. They can be added; the
  protocol must work without them.
- **A message schema in JSON.** The body is Markdown because the approver reads it on a
  phone. The headings give parsers enough structure.
- **Threading rules.** GitHub's own comment thread is the thread.
- **Priorities beyond one label.** A second priority level was never needed.
- **Encryption.** A channel is as confidential as the repository. Anything that needs
  more does not belong in it.

## Open questions

- Should approvals in distinct mode require signed commits?
- Should there be a defined way to archive a channel?
- Is there a useful third tier between `restricted` and `standard`, or does a playbook
  that names specific external actions already cover it?
- Can the same protocol run on other forges? The mapping to GitLab or Forgejo issues
  looks direct; nobody has tried it.

Comment on any of these in the [issue
tracker](https://github.com/FrankGoortani/repo-channel-protocol/issues).
