# Quick start

This sets up one channel between you, a coordinating agent and one other agent. It
takes about fifteen minutes. The [specification](../SPEC.md) is the reference; this
page is the shortest path through it.

## Before you start

- Python 3.11 or later.
- The [GitHub CLI](https://cli.github.com), signed in (`gh auth status`).
- Decide three things:
  1. **Who approves.** One human. That is probably you.
  2. **Who is the steward.** The participant that keeps the channel tidy: labels for
     agents that cannot label, closes for agents that cannot close, records what each
     agent turns out to be able to do. Choose the agent you trust most, or yourself.
  3. **Identity mode.** If each agent can have its own GitHub account, choose
     `distinct`. If the agents act through your account, choose `shared` and read
     [what that costs you](security.md#shared-identity-mode).

## 1. Install the tooling

```bash
pipx install git+https://github.com/FrankGoortani/repo-channel-protocol
rchan --version
```

`uv tool install git+https://github.com/FrankGoortani/repo-channel-protocol` works
too. The tooling uses only the Python standard library.

## 2. Create the repository

One repository per agent you work with. Keep it private.

```bash
gh repo create scout-channel --private --clone
cd scout-channel
```

## 3. Write the manifest

```bash
rchan init
```

This writes a starter `channel.toml`. Edit it:

```toml
protocol   = "0.1"
name       = "scout-channel"
repository = "your-account/scout-channel"
timezone   = "America/Toronto"
identity   = "shared"
approval   = "any"
profile    = "full"

[[participant]]
id    = "dana"
name  = "Dana"
kind  = "human"
roles = ["approver"]
inbox = "Daily, or when an agent flags an item"

[[participant]]
id    = "atlas"
name  = "Atlas"
kind  = "agent"
roles = ["steward"]
tier  = "standard"
inbox = "At the start of every working session"
about = "Coordinating agent in Dana's workspace"

[[participant]]
id    = "scout"
name  = "Scout"
kind  = "agent"
tier  = "restricted"
inbox = "09:00 and 17:00"
about = "Research agent. Public web only."
```

Start every new agent as `restricted`. You can raise the tier later, with evidence.

## 4. Generate the channel

```bash
rchan init
```

Now that the manifest exists, the same command generates everything else:

| File | Kind | What to do with it |
|---|---|---|
| `PROTOCOL.md` | Generated | Nothing. Every participant reads it. Never edit it by hand. |
| `.github/ISSUE_TEMPLATE/*.yml` | Generated | Nothing. One form per message type. |
| `.github/labels.tsv` | Generated | Nothing. Applied in step 6. |
| `shared/RULES.md` | Yours | Write the rules every participant must honour. Starts as a draft. |
| `participants/<id>/BRIEF.md` | Each participant's | Each agent fills in its own. |
| `ledgers/capability-trials.csv` | Shared | The steward appends to it. |
| `playbooks/` | Yours | One file per recurring workflow, when you have one. |

Run `rchan init` again whenever you change `channel.toml`. Generated files are
rewritten; yours are left alone.

## 5. Write and approve the rules

Open `shared/RULES.md`. Write the rules that apply to everything in this channel:
what must never leave it, what agents may never do, how sources are judged. Quote
yourself with a date where you can. A rule in your own words is harder to drift from.

When you are satisfied, approve it by editing the frontmatter:

```yaml
status: active
approved_by: dana
approved_on: 2026-11-12
```

This first version is the only one committed without a proposal. From here on,
every change follows [the proposal process](../SPEC.md#9-changing-instructions).

## 6. Check, publish, label

```bash
rchan lint
git add -A && git commit -m "dana: initialise channel" && git push -u origin HEAD
rchan labels
```

`rchan lint` checks the manifest, the frontmatter of every instruction file, the
ledgers, and that the generated files match the manifest.

## 7. Bring the agents in

For each agent:

1. Give it access to the repository. In `distinct` mode, invite its account as a
   collaborator. In `shared` mode, connect it to your account through whatever GitHub
   integration its platform offers.
2. Paste the text from [guide-for-agents.md](guide-for-agents.md#text-to-paste-into-an-agents-instructions)
   into its standing instructions.
3. Send the onboarding request:

```bash
rchan send request --from atlas --to scout \
  --title "Onboard to this channel and confirm what you can do" \
  --section "Ask=1. Read PROTOCOL.md and shared/RULES.md. 2. Fill in participants/scout/BRIEF.md. 3. On this issue: comment, add the label state:acked, and close it when done. Tell me exactly what happens at each step." \
  --section "Why=We need to know which GitHub operations you can perform before relying on any of them." \
  --section "Done when=Your brief is in the repository and each operation in step 3 has either worked or failed with the error text quoted here."
```

The onboarding request is also the first capability trial. Whatever the agent cannot
do, record it in `ledgers/capability-trials.csv` and add it to the agent's `cannot`
list in the manifest. The [fallbacks](../SPEC.md#78-participants-with-limited-capabilities)
then apply automatically.

## 8. Work

```bash
rchan inbox atlas        # what is waiting for Atlas, plus issues with no to: label if Atlas is the steward
rchan send --help        # compose any message type
rchan check body.md --title "[handoff] Sources, week of 2026-11-02"   # validate before sending by other means
```

When a workflow repeats, write it down as a playbook and approve it. That is the point
at which an agent may act on it without asking each time.

## Keeping a channel healthy

Add this to the channel repository as `.github/workflows/channel.yml` to check every
push:

```yaml
name: channel
on:
  push: { branches: [main] }
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install git+https://github.com/FrankGoortani/repo-channel-protocol
      - run: rchan lint --base "$BASE"
        env:
          BASE: ${{ github.event.pull_request.base.sha || github.event.before }}
```

`--base` makes the check fail if any existing ledger row was edited or removed since
that commit.

## Next

- [Guide for humans](guide-for-humans.md): what approving well looks like.
- [Guide for agents](guide-for-agents.md): the operating rules, in the order an agent needs them.
- [The worked example](../examples/digest-channel): a full channel with transcripts.
