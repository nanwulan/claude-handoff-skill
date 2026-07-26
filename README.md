# /handoff — Claude Code Project State Management

[![Version](https://img.shields.io/badge/version-v2.0.0-blue)](https://github.com/nanwulan/claude-handoff-skill/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> A Claude Code skill that maintains project state across sessions — so any fresh Claude session can pick up exactly where you left off, with full context.

## What It Does

Handoff maintains **two files** at project root:

| File | Role | Lifespan |
|------|------|----------|
| `PROJECT.ftmd` | Long-term memory — accumulated decisions, failures, environment | **Persistent.** Never auto-deleted. |
| `HANDOFF-YYYY-MM-DD.ftmd` | Session snapshot — what happened THIS session, what's next | **Short-lived.** Read once then archived. |

Together they form a complete project memory layer: `PROJECT.ftmd` tells you where you've been; `HANDOFF.ftmd` tells you where to go next.

📄 **[See an example](HANDOFF-example.ftmd)**

## V2: What's New

| Change | Detail |
|--------|--------|
| **Dual-file model** | `PROJECT.ftmd` accumulates decisions and lessons across sessions — they no longer get lost when handoffs are archived |
| **Environment auto-capture** | OS, Shell, Node, Python, Git, Claude Code version recorded automatically |
| **Git Snapshot section** | Branch, last commit, changed files — new session doesn't need to rescan the repo |
| **Subcommands** | `/handoff timeline` / `status` / `doctor` for quick project lookups |
| **HANDOFF 9 sections** | Added Git Snapshot as the 3rd required section |

## Commands

| Command | What it does |
|---------|-------------|
| `/handoff` | Generate HANDOFF + update PROJECT + cleanup |
| `/handoff timeline` | View Decision Log and Failure Memory in chronological order |
| `/handoff status` | One-line project status: stage, progress, current focus |
| `/handoff doctor` | Health check: PROJECT, HANDOFF, Git, Environment, Tests |

## The FTMD Format

FTMD (**Frictionless Transfer Markdown Document**) is vanilla Markdown with a structural contract. No YAML frontmatter, no custom syntax. The only contract is required level-2 heading sections.

### PROJECT.ftmd (5 sections)

| # | Section | Update Rule |
|---|---------|-------------|
| 1 | **Snapshot** | Replaced — current stage, progress, focus |
| 2 | **Environment** | Replaced — auto-captured system info |
| 3 | **Decision Log** | **Appended** — dated entries, newest first |
| 4 | **Failure Memory** | **Appended** — dated entries, newest first |
| 5 | **Open Questions** | Replaced — currently unresolved |

### HANDOFF.ftmd (9 sections)

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Task** | What are we building? |
| 2 | **Completed** | What's done, each claim verified `[V]` or recalled `[?]` |
| 3 | **Git Snapshot** | Branch, last commit, changed files |
| 4 | **Blocked** | 🔧 Technical blockers + 👤 Decisions needed |
| 5 | **Next Steps** | Ordered, actionable, file-specific |
| 6 | **Pitfalls** | What went wrong, why, correct approach |
| 7 | **Decisions** | What was chosen, why, what was rejected |
| 8 | **File Map** | Every relevant file and what it does |
| 9 | **Startup Protocol** | Commands to run + files to read first |

## Key Features (from V1, preserved)

- **Verification Protocol** — Nothing written from memory; every claim tagged `[V]` or `[?]`
- **Source-of-Truth Rank** — Running code > tests > docs > PROJECT.ftmd > HANDOFF
- **Degradation Detection** — Reactive context rot detection + proactive milestone nudges
- **claude-mem Integration** — Cross-references accumulated knowledge base on write and read
- **Auto-Cleanup** — Stale done files purged after 7 days; max 3 active HANDOFF files per project
- **Short-Session Gate** — Skips generation for trivial sessions

## Installation

```bash
# Unix/macOS
cp SKILL.md ~/.claude/skills/handoff/SKILL.md

# Windows
copy SKILL.md %USERPROFILE%\.claude\skills\handoff\SKILL.md
```

## Usage

```bash
/handoff           # Generate handoff + update project state
/handoff status    # Quick project status
/handoff timeline  # View development history
/handoff doctor    # Health check
```

**Resume from a handoff:** say "先读 HANDOFF" in a new session.

## Design Philosophy

Handoff is the **project memory layer** in a three-tier AI workflow:

```
Claude Code
    ↓
claude-mem (long-term, cross-project knowledge)
    ↓
handoff (project state, decisions, lessons)
    ↓
Git (code history)
    ↓
Workspace (files)
```

- **claude-mem** = what we've learned across *all* projects
- **handoff** = what we've decided and discovered in *this* project
- **Git** = what we've changed in *this* codebase

## License

MIT
