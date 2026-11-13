---
name: channel-setup
description: Create a new Repo Channel Protocol (RCP) channel repository and onboard a participant to it. Use when asked to "set up a channel", "connect a new agent", "create a channel repo", "add an agent to the protocol" or "onboard" a person or agent to GitHub-based collaboration under RCP.
---

# Set up a channel and onboard a participant

A channel is one GitHub repository shared by a small set of participants, at least one
of whom is a human approver. Use one channel per agent.

## Before you create anything

Creating a repository and inviting an agent are actions with effects outside your
workspace. Confirm with the person you work for:

1. **Who are the participants?** For each: a short lowercase id, a display name, human
   or agent.
2. **Who approves?** A human. Usually them.
3. **Who is the steward?** Exactly one participant.
4. **Which tier for each agent?** Default to `restricted` for any agent that has not
   been observed working. `standard` only if its role needs private context and they
   say so.
5. **Identity mode.** `distinct` if every participant has its own GitHub account.
   `shared` if the agents act through the approver's account. Tell them what shared
   mode costs: no verifiable authorship, no notifications to them, approval by
   convention only.
6. **Repository name and owner.** Private unless they say otherwise.

Do not guess any of these.

## 1. Create the repository

```bash
gh repo create <owner>/<name> --private --clone
cd <name>
```

## 2. Write the manifest

```bash
rchan init
```

Edit the `channel.toml` it writes. Set `name`, `repository`, `timezone` (IANA name),
`identity`, and one `[[participant]]` table per participant with `id`, `name`, `kind`,
`roles`, `tier` for agents, `inbox` cadence and a one-line `about`. In distinct mode,
add each `github` login.

## 3. Generate and check

```bash
rchan init
rchan lint
```

## 4. Draft the shared rules

Edit `shared/RULES.md`. Write down what the approver has actually said, quoted with
dates where you have their words. At minimum:

- What must never leave the channel.
- That no participant acts outside the repository unless an active playbook names the
  action.
- How facts are evidenced.

Leave `status: draft` and the approval fields empty. **You do not approve it.** Ask the
approver to read it and set `status: active`, `approved_by` and `approved_on`
themselves. This first approval may be committed directly; every later change goes
through a proposal.

## 5. Publish

```bash
git add -A
git commit -m "<your-id>: initialise channel"
git push -u origin HEAD
rchan labels
```

In distinct mode, also ask the approver to protect the default branch and require
review from code owners. The generated `.github/CODEOWNERS` assigns the instruction
paths to them.

## 6. Give the participant access

This step is the approver's. Tell them what to do:

- **Distinct mode:** invite the participant's GitHub account as a collaborator, with
  the narrowest role that lets it open issues and, if it will commit, push.
- **Shared mode:** connect the agent to their GitHub account through its platform's
  integration, limited to this repository if the platform allows.

Then give the agent its standing instructions: the text in
`docs/guide-for-agents.md` of the protocol repository, with the placeholders filled in.

## 7. Send the onboarding request

This first message doubles as the first capability trial.

```bash
rchan send request --from <your-id> --to <new-id> \
  --title "Onboard to this channel and confirm what you can do" --topic channel \
  --section "Ask=1. Read PROTOCOL.md and shared/RULES.md. 2. Fill in participants/<id>/BRIEF.md. 3. On this issue: comment, add the label state:acked, and close it when you are done. Tell me exactly what happens at each step, including any error text." \
  --section "Why=We need to know which GitHub operations you can perform before relying on any of them." \
  --section "Done when=Your brief is in the repository and each operation in step 3 has either worked or failed with the error quoted here."
```

## 8. Record what you learn

When the participant responds:

1. Append one row per operation to `ledgers/capability-trials.csv`: `PASS` or `FAIL`
   with the issue link or quoted error as evidence. Anything it says it can do but did
   not show is `CLAIMED`.
2. For each failed operation, add it to the participant's `cannot` list in
   `channel.toml` (through a proposal), run `rchan init` to regenerate, and commit.
3. If it could not commit its brief, commit it for it from the text it sent.
4. Send the approver a `report` with the results and the fallbacks now in effect.

## 9. Hand over

Tell the approver:

- The repository URL and their inbox link: `https://github.com/<owner>/<name>/issues?q=is%3Aopen+label%3Ato%3A<their-id>`
- That `shared/RULES.md` is a draft until they approve it, and that no agent may act on
  it before then.
- What the new participant can and cannot do, from the ledger.
- That nothing recurring happens until a playbook exists and they have approved it.
