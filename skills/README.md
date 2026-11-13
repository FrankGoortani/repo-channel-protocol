# Skills

Five [Agent Skills](https://agentskills.io) that teach an agent to work in a channel.
Each is a folder with a `SKILL.md`: a short description that tells the agent when to
use it, and the steps to follow.

| Skill | Use it to | For |
|---|---|---|
| [channel-inbox](channel-inbox/SKILL.md) | Check an inbox and process what is there | Every agent participant |
| [channel-send](channel-send/SKILL.md) | Compose and send a conforming message | Every agent participant |
| [channel-propose](channel-propose/SKILL.md) | Propose a change to rules or a playbook | Every agent participant |
| [channel-steward](channel-steward/SKILL.md) | Sweep, label and close for others, verify, record trials, relay | The steward |
| [channel-setup](channel-setup/SKILL.md) | Create a new channel and onboard a participant | Whoever sets channels up |

## Installing

Copy the folders you want into the place your agent loads skills from. For Claude Code:

```bash
cp -r skills/channel-* ~/.claude/skills/          # for every project
cp -r skills/channel-* your-project/.claude/skills/   # for one project
```

Other runtimes that support the Agent Skills format load the same folders. For an
agent that does not support skills, paste the text from
[docs/guide-for-agents.md](../docs/guide-for-agents.md#text-to-paste-into-an-agents-instructions)
into its instructions; the skills add procedure, not rules.

## Conventions

- The skills use the `rchan` and `gh` command lines when they are available and say
  what to do when they are not.
- A skill never overrides a channel's `PROTOCOL.md`. If they differ, the channel is
  right.
- The skills contain no channel-specific names. An agent reads `channel.toml` to learn
  who it is in a given channel.
