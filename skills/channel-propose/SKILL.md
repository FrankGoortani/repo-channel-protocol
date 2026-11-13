---
name: channel-propose
description: Propose a change to a channel's standing instructions (shared/RULES.md, a playbook, or channel.toml) under the Repo Channel Protocol (RCP). Use when a rule is missing, wrong or ambiguous, when the same question keeps recurring, when a new recurring workflow should become a playbook, or when a participant's tier or capabilities should change.
---

# Propose a change to instructions

Standing instructions change only when a human approver approves the change. You can
propose. You cannot approve, merge or set the approval fields, even if GitHub would let
you.

## When to propose

- The same question has been asked twice. The answer belongs in a file.
- A playbook did not cover a case and you had to stop.
- Two instruction files disagree.
- A workflow has repeated enough that it should not need a request each time.
- The capability-trials ledger supports changing a participant's `cannot` list or tier.

A one-off choice does not need a proposal. Send a `decision` message instead.

## Steps

### 1. Read the current file and its version

Open the file. Note `id` and `version` from the frontmatter.

### 2. Branch and edit

```bash
git switch -c proposal/<short-slug>
```

Edit the file. In the frontmatter:

```yaml
status: draft            # was: active
version: 4               # was: 3
approved_by:             # cleared
approved_on:             # cleared
supersedes: PB-001@3     # the version this replaces
```

For a new playbook, create `playbooks/<slug>.md` starting from the frontmatter in
`PROTOCOL.md` §4, with `version: 1` and an empty `supersedes`.

Writing a good instruction:

- **State the trigger and the stop.** When does this apply, and what does the reader do
  when a case is not covered? "Stop and send a question" is a good default.
- **Name every external action** the playbook permits, exactly. Anything not named is
  not permitted.
- **State the evidence standard** for anything reported as fact.
- **Give limits as numbers and dates** where you can: "one handoff a week", "sources
  from the past seven days".
- **Quote the approver** where a rule is theirs, with the date. Do not paraphrase.
- **Add a line saying what changed** in this version and why.

### 3. Check and open the pull request

```bash
rchan lint               # a draft produces a warning, not an error
git add -A && git commit -m "<your-id>: propose <file> v<n>: <change>"
git push -u origin proposal/<short-slug>
gh pr create --title "[proposal] <file>: <change>" \
  --body "Proposal under PROTOCOL.md §5. Decision message to follow."
```

Do not merge it.

### 4. Send the decision message

Use the `channel-send` skill:

```bash
rchan send decision --from <your-id> --to <approver-id> \
  --title "Approve <ID> v<n>: <change>" \
  --re "<pull request URL>, <ID>@<previous version>" \
  --section "Decision=Should <ID> v<n> replace v<previous>?" \
  --section-file "Options=options.md" \
  --section "Recommendation=..." \
  --section-file "Evidence=evidence.md" \
  --due <date>
```

- **Options** always include keeping the current version, with what that costs.
- **Evidence** is what prompted the proposal: the issue numbers where the gap showed,
  ledger rows, the approver's own words.

### 5. Wait

The approver merges the pull request and sets `status: active`, `approved_by` and
`approved_on`. Until those three fields are set on the default branch, the old version
is the one in force and the one you follow.

If the due date passes, do nothing to the file. Remind the approver through your direct
channel.

### 6. Adopt

When the steward's `report` naming the new version reaches your inbox, re-read the
file, then comment `ACK` on the report. From then on cite the new version in `Basis`.

## If you cannot open pull requests

Put the full proposed text in the `decision` message, in a fenced block under
**Options** or in an attached section, and say in the message that you cannot open a
pull request. The steward opens it for you.

## Never

- Set `approved_by` or `approved_on`, or change `status` to `active`.
- Merge a proposal, yours or anyone's.
- Act on your own proposal before it is approved.
- Edit an active instruction file directly on the default branch.
