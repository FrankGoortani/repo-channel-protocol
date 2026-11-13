# Prior art

Using a GitHub repository to coordinate AI agents is not a new idea, and this project
does not claim to have invented it. This page lists the related work found in a survey
in November 2026, says plainly what each does, and says what the Repo Channel Protocol
adds. The descriptions rest on each project's public documentation as read then. They
may be incomplete or out of date, and "it has no X" means "none was found". Corrections
are welcome: open an issue.

## Summary

No published specification was found that combines all of the following:

1. Typed messages as GitHub issues, with a fixed envelope and lifecycle.
2. Standing instructions as versioned files that bind an agent only when a named human
   has approved them in the file itself.
3. Trust tiers that bound what an agent is told, what it may do and how its output is
   treated.
4. One channel per agent, with a single bridge that relays between channels.
5. A ledger of observed capabilities, kept apart from what agents claim.
6. Defined behaviour when all parties share one GitHub account.
7. Fallbacks for participants that cannot perform basic operations.

Items 1 and, in part, 2 have clear precedents, listed next. No precedent was found for
3 to 7 in this setting.

## The closest work

### Issues as an agent mailbox

- **[agent-postbox](https://github.com/Aethelgard-Systems/agent-postbox)** (2026).
  A GitHub-based mailbox for agents, delivered as an MCP server and CLI. It has
  `to:<agent>` inbox labels, acknowledged handoffs, labels that only a human sets for
  approvals and decisions, and treats issue text as untrusted. It is the nearest
  neighbour. Differences: it is tooling, where RCP is a specification that needs no
  tooling; it requires a GitHub identity per agent; it has no instruction files with
  approval frontmatter, no trust tiers and no capability ledger.
- **Jon Udell, ["The agent coordination protocol hiding in plain sight: GitHub issues"](https://www.infoworld.com/article/4224587/the-agent-coordination-protocol-hiding-in-plain-sight-github-issues.html)**
  (InfoWorld, 2026), and his related project [bram](https://github.com/judell/bram). The
  same starting observation, including agents that share their owner's account and sign
  messages in the body. The article argues that no new protocol is needed. RCP agrees
  that no new *transport* is needed, and holds that once more than one agent and any
  private data are involved, the conventions need writing down: who approves, what is
  data, what silence means.
- **gptme's ["Bob and Alice"](http://timetobuildbob.com/blog/inter-agent-communication-breakthrough)**
  (2025). Two agents exchanging messages through issue comments in each other's
  repositories. Free-form, with separate accounts and no governance layer.
- **[ccpm](https://github.com/automazeio/ccpm)**. Uses GitHub issues as the project
  database for parallel coding agents. It coordinates work items for one team's agents
  in one codebase; it is not a messaging protocol between independent parties.

### Git-native agent protocols

- **[GNAP](https://github.com/farol-team/gnap)**, the Git-Native Agent Protocol.
  A draft that coordinates agents through JSON files in a repository: agents, tasks,
  runs and messages. Like RCP it needs no server and treats humans and agents alike as
  participants. Unlike RCP it uses files for everything, does not use issues, and does
  not define an approval gate on instructions or trust tiers.
- **[beads](https://github.com/gastownhall/beads)**. A git-backed issue tracker built
  for coding agents' own memory and task tracking. A different problem: one agent's
  working memory, where RCP is about communication between parties.
- **[mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail)**. Agent
  identities, inboxes and file leases for coding agents, backed by git and SQLite and
  served over MCP. It needs a server and targets agents working in one codebase.

### Agent automation on GitHub

- **[GitHub Agentic Workflows](https://github.com/github/gh-aw)**. Natural-language
  workflows that run agents in GitHub Actions, with issues as triggers and outputs.
  It runs agents; RCP defines what parties say to each other and who may approve what.
  The two could be combined.
- **IssueOps**. The established practice of using issues as an operations interface
  driven by Actions. RCP borrows the insight that an issue is a good state machine.

### Human-agent approval

- **[CHAP](https://github.com/BrightbeamAI/chap)**, the Collaborative Human Agent
  Protocol. A runtime for approvals, overrides, handoffs and evidence logs, compatible
  with MCP and A2A. It addresses the same concern as RCP's approval rules, as a service
  with a coordinator, where RCP uses files and issues.

## Wire protocols

These solve a different layer and are complements, not alternatives.

| Protocol | What it standardises | Relation to RCP |
|---|---|---|
| [A2A](https://github.com/a2aproject/A2A) | How one agent calls another over HTTP: discovery, tasks, streaming | Synchronous and endpoint-based. Says nothing about who approved an agent's standing instructions. Two agents that can speak A2A may still want a channel for the human-governed part. |
| [MCP](https://modelcontextprotocol.io) | How a model reaches tools and data | Many agents will reach a channel *through* an MCP server for GitHub. MCP is the access path; RCP is what is said. |
| ACP (IBM, BeeAI) | Agent-to-agent messaging over REST | Since merged into A2A. |
| FIPA-ACL, KQML | Message performatives based on speech-act theory | The ancestry of RCP's five message types. RCP keeps the idea of typed speech acts and drops the formal semantics. |

## Ideas borrowed from software practice

- **GitOps.** The repository is the source of truth, and changes to it are reviewed.
  RCP applies that to an agent's instructions.
- **`CODEOWNERS` and branch protection.** The enforcement mechanism for approval in
  distinct identity mode.
- **RFC and ADR processes.** The proposal process (branch, pull request, decision) is
  one of these in miniature.
- **Runbooks.** A playbook is a runbook whose reader is an agent, with an approval gate.
- **Append-only logs.** Ledgers follow the accounting rule: correct by adding, never by
  erasing.

## Security work this relies on

- Simon Willison, ["The lethal trifecta for AI agents"](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  (2025). The framing behind the trust tiers.
- Invariant Labs, ["GitHub MCP exploited"](https://invariantlabs.ai/blog/mcp-github-vulnerability)
  (2025). A demonstration that issue text can steer an agent into leaking private data,
  and the reason a channel in a public repository carries extra requirements.

## What RCP does not try to be

- An agent framework or runtime.
- A replacement for A2A or MCP.
- A task tracker for a coding team's agents.
- A product. It is a specification, a template and a small linter.
