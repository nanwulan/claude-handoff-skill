# /handoff — AI Session Continuity Skill

> A Claude Code skill for generating structured handoff documents that enable seamless session-to-session continuity with zero prior context.

## What It Does

`/handoff` generates a `HANDOFF.ftmd` file at project root — a fully self-contained document designed for a fresh AI session that knows nothing about your project or conversation. No "as we discussed", no implicit references.

It also defines the **New Session Protocol**: when a fresh session starts, it scans for the newest handoff, reads it, and bootstraps itself with full context.

📄 **[See an example](HANDOFF-example.ftmd)** — a complete handoff for a fictional login redirect fix.

## The FTMD Format

FTMD (**Frictionless Transfer Markdown Document**) is vanilla Markdown with a structural contract. No YAML frontmatter, no custom syntax — any Markdown renderer can display it. The only contract is 8 required level-2 heading sections.

| Property | Spec |
|----------|------|
| **Extension** | `.ftmd` |
| **Syntax** | CommonMark + GFM tables |
| **Sections** | 8 (Task, Completed, Blocked, Next Steps, Pitfalls, Decisions, File Map, Startup Protocol) |
| **Verification** | Every factual claim tagged `[V]` or `[?]` |

## The 8-Section Template

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Task** | What are we building? |
| 2 | **Completed** | What's done, each claim verified `[V]` or recalled `[?]` |
| 3 | **Blocked** | Technical blockers + decisions needed from the human |
| 4 | **Next Steps** | Ordered, actionable, file-specific |
| 5 | **Pitfalls** | What went wrong, why, and the correct approach |
| 6 | **Decisions** | What was chosen, why, and what was rejected |
| 7 | **File Map** | Every relevant file and what it does |
| 8 | **Startup Protocol** | Commands to run + files to read first |

## Key Features

- **Verification Protocol** — Nothing written from memory; every claim tagged `[V]` (verified) or `[?]` (recalled)
- **Source-of-Truth Rank** — Running code > tests > docs > handoff — handoff never overrides reality
- **Degradation Detection** — Reactive: self-monitors for context rot mid-session. Proactive: nudges at ~10 exchange milestones
- **claude-mem Integration** — Cross-references accumulated knowledge base for richer handoffs
- **Auto-Cleanup** — Stale done files purged after 7 days; active files capped per directory
- **Short-Session Gate** — Skips generation for trivial sessions (no files changed, no decisions made)

## Installation

Copy `SKILL.md` to your Claude Code skills directory:

```bash
# Unix/macOS
cp SKILL.md ~/.claude/skills/handoff/SKILL.md

# Windows
copy SKILL.md %USERPROFILE%\.claude\skills\handoff\SKILL.md
```

## Usage

### Generate a handoff
```
/handoff
```
Or say: "写交接文档", "write handoff", "会话交接", "结束会话"

### Resume from a handoff
```
先读 HANDOFF
```
The new session will find the newest `HANDOFF-*.ftmd`, read it, and summarize current status.

## Trigger Phrases

| Trigger | Action |
|---------|--------|
| `/handoff` / `写交接文档` | Generate timestamped handoff + run cleanup |
| `先读 HANDOFF` (new session) | Find newest `.ftmd`, read, summarize |
| Undone handoff exists at session start | Proactively mention it |
| Context rot detected mid-session | Suggest `/handoff` (max 2× per session) |

## File Naming

- **Project directories:** `HANDOFF-YYYY-MM-DD.ftmd`
- **Non-project sessions:** `HANDOFF-<topic-slug>-YYYY-MM-DD.ftmd`

## Design Philosophy

Handoff is a **point-in-time snapshot**. It works alongside claude-mem (accumulated knowledge base) rather than replacing it. The two systems reinforce each other:

- **Handoff** = what happened in *this* session
- **claude-mem** = what we've learned across *all* sessions

## License

MIT
