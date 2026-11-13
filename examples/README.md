# Examples

## [digest-channel](digest-channel)

A complete, fictional channel. Dana writes a weekly newsletter about database releases.
Two agents help: **Scout**, a research agent on the `restricted` tier that can read the
public web and nothing else, and **Atlas**, a coordinating agent in Dana's workspace
that verifies what Scout finds and acts as steward. Both agents post through Dana's
GitHub account, so the channel uses shared identity.

The directory is what `rchan init` generates from [channel.toml](digest-channel/channel.toml),
plus the files a real channel would add: approved rules, one approved playbook, two
ledgers.

GitHub issues do not live in a directory, so the conversations are written out as
transcripts in [messages/](digest-channel/messages). Each file has the issue's title,
labels and final state, then the body, then the comments.

| Transcript | Shows |
|---|---|
| [001-request-onboard](digest-channel/messages/001-request-onboard.md) | Onboarding as a capability trial. Scout turns out not to be able to label, close or commit, and the fallbacks take over. |
| [002-handoff-brief](digest-channel/messages/002-handoff-brief.md) | The fallback for an agent that cannot commit: the file travels in a handoff and the steward commits it unchanged. A self-described capability is recorded as `CLAIMED`. |
| [003-decision-activate-playbook](digest-channel/messages/003-decision-activate-playbook.md) | A proposal and its decision. The approver answers outside GitHub and the steward relays her words verbatim. |
| [004-handoff-sources](digest-channel/messages/004-handoff-sources.md) | A handoff from a restricted agent with `Basis` and `Labels` sections, verification by the steward, and an instruction embedded in a quoted page that both agents treat as data. |
| [005-question-prereleases](digest-channel/messages/005-question-prereleases.md) | A question that goes unanswered, the sender proceeding on its stated fallback, and the gap being routed to the approver as a rule change. |
| [006-report-limit](digest-channel/messages/006-report-limit.md) | An agent reporting a limit with the exact error text, not guessing at what it could not read. |

The file numbers match the issue numbers the transcripts refer to.

Things to look at:

- [shared/RULES.md](digest-channel/shared/RULES.md) and
  [playbooks/weekly-digest.md](digest-channel/playbooks/weekly-digest.md): approval
  frontmatter, and rules that quote the approver.
- [ledgers/capability-trials.csv](digest-channel/ledgers/capability-trials.csv):
  `PASS`, `FAIL`, `PARTIAL` and `CLAIMED` rows with evidence.
- [ledgers/sources.csv](digest-channel/ledgers/sources.csv): verified and rejected
  entries from a restricted agent.
- [PROTOCOL.md](digest-channel/PROTOCOL.md): the protocol as rendered for this channel.

Check it yourself:

```bash
rchan lint --dir examples/digest-channel
```
