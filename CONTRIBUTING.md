# Contributing

This is a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) — a structured Markdown prompt that implements project state management. Improvements are welcome.

## Files

| File | Role |
|------|------|
| `SKILL.md` | The skill itself — all instructions for Claude Code |
| `README.md` | Human-facing documentation |
| `HANDOFF-example.ftmd` | Example of the 9-section handoff format |
| `PROJECT.ftmd` | The skill's own long-term memory — our dogfood |
| `CONTRIBUTING.md` | This file |

## How to Contribute

1. **Fork** this repo
2. **Edit `SKILL.md`** — this is where the skill logic lives
3. **Test** by copying to your `~/.claude/skills/handoff/SKILL.md` and running `/handoff` in Claude Code
4. **Run the sync checklist** (see below) before committing
5. **Open a PR** with a clear description of what you changed and why

## 7+1 Sync Checklist

**Mandatory after every SKILL.md change.** The skill lives in three places; they must stay in lockstep.

| # | Location | Action |
|---|----------|--------|
| 1 | `.claude/skills/handoff/SKILL.md` | Edit the primary file |
| 2 | `Desktop/handoff/SKILL.md` | `cp` sync, `diff` confirm |
| 3 | `README.md` | Version badge, architecture diagram, key features, compatibility |
| 4 | `HANDOFF-example.ftmd` | Does it match current section structure? |
| 5 | `CONTRIBUTING.md` | File list, design principles still accurate? |
| 6 | GitHub Releases | Tag + release notes if version bumped |
| 7 | GitHub repo description | `gh repo edit --description` if positioning changed |
| **+1** | **Grep old version numbers** | `grep -rn "v[0-9]" *.md` across entire repo — badge URLs are the #1 miss |

## Convention

- **Auto-resume is the default.** When an unread HANDOFF exists at session start, Claude loads it immediately — no trigger phrase needed. Want to manually resume? Say **「先读 HANDOFF」**. Every `/handoff` post-generation message reinforces this: "下次新会话时自动加载继续工作，或说「先读 HANDOFF」手动触发。"
- The dual-file model (`PROJECT.ftmd` persistent / `HANDOFF-*.ftmd` disposable) is the architectural invariant. Don't propose merging them.

## What Makes a Good Contribution

- **TDD mindset** — identify a failure case before adding a fix
- **Zero-context readable** — the skill must work for a fresh AI session
- **Tables over prose** — structured formats wherever possible
- **No vague rules** — every instruction must be concrete and testable
- **Respect the dual-file model** — PROJECT.ftmd accumulates, HANDOFF.ftmd snapshots
- **Self-contained by default** — integrations are guarded ("if available, else skip")

## Design Principles

1. **Zero-context target audience** — every sentence understandable without being in the conversation
2. **Evidence over memory** — `[V]` claims must include their proof source
3. **Self-contained** — zero hard dependencies; optional integrations are guarded
4. **Structured over prose** — tables for scanability, prose only when necessary
5. **Decisions carry rationale** — rejected alternatives are as important as the choice
6. **Failures are assets** — each pitfall records the full chain: attempt → result → root cause → lesson

These principles are also documented in `PROJECT.ftmd` (Decision Log) — our own handoff system dogfoods itself.
