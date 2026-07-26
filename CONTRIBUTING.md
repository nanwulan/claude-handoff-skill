# Contributing

This is a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) — a structured Markdown prompt that implements project state management. Improvements are welcome.

## Files

| File | Role |
|------|------|
| `SKILL.md` | The skill itself — all instructions for Claude Code |
| `README.md` | Human-facing documentation |
| `HANDOFF-example.ftmd` | Example of the 9-section handoff format |

## How to contribute

1. **Fork** this repo
2. **Edit `SKILL.md`** — this is where the skill logic lives
3. **Test** by copying to your `~/.claude/skills/handoff/SKILL.md` and running `/handoff` in Claude Code
4. **Open a PR** with a clear description of what you changed and why

## What makes a good contribution

- **TDD mindset** — identify a failure case before adding a fix
- **Zero-context readable** — the skill must work for a fresh AI session
- **Tables over prose** — structured formats wherever possible
- **No vague rules** — every instruction must be concrete and testable
- **Respect the dual-file model** — PROJECT.ftmd accumulates, HANDOFF.ftmd snapshots

## Design principles

This skill follows the [superpowers:writing-skills](https://github.com/anthropics/skills) methodology — no fix without a failing test first. Don't add features that haven't proven themselves in real sessions.
