# /handoff — Project State Management for Claude Code

[![Version](https://img.shields.io/badge/version-v2.4.0-blue)](https://github.com/nanwulan/claude-handoff-skill/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Format](https://img.shields.io/badge/format-FTMD-orange)](#the-ftmd-format)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](#design-philosophy)
[![Claude Code](https://img.shields.io/badge/framework-Claude%20Code%202.1%2B-purple)](https://claude.ai/code)

> **Every Claude session starts with zero context. Handoff makes sure it ends with zero context loss.**
>
> A self-contained Claude Code skill that maintains a persistent project memory layer — accumulated decisions, environment state, failure lessons, and session snapshots — so any fresh session can pick up exactly where you left off, with the full depth of everything that came before.

---

## The Problem

You're deep into a project. Five sessions in, you've made dozens of micro-decisions, hit three gnarly bugs, and discovered that the dev server needs a specific Node version. Claude helped you through all of it — but Claude's memory resets every session.

**Without Handoff, every new session is ground zero.** You repeat yourself. Claude re-derives settled conclusions. Context that took 20 exchanges to build is gone. The project drifts.

**With Handoff, every session builds on the last.** Claude reads a structured snapshot of where things stand, verifies it against reality, and picks up the work — not from memory, but from documented truth.

## The Architecture

Handoff maintains a **dual-file memory layer** at your project root. The separation is deliberate:

```
                        ┌──────────────────────────┐
                        │     PROJECT.ftmd          │
                        │                           │
                        │  • Accumulates decisions   │
                  ┌─────▶  • Records failures        │──────┐
                  │     │  • Tracks environment      │      │
                  │     │  • Never deleted           │      │
                  │     └──────────────────────────┘      │
                  │                                        │
   ┌──────────────┴──────────────┐          ┌──────────────┴──────────────┐
   │       Session N             │          │       Session N+1           │
   │                             │          │                             │
   │  Reads PROJECT.ftmd         │          │  Reads PROJECT.ftmd         │
   │  Generates HANDOFF-*.ftmd   │──────────▶  Reads HANDOFF-*.ftmd       │
   │  Updates PROJECT.ftmd       │          │  Marks HANDOFF as .done     │
   │                             │          │  Continues the work         │
   └─────────────────────────────┘          └─────────────────────────────┘
```

| File | Role | Lifespan | Updated |
|------|------|----------|---------|
| `PROJECT.ftmd` | **Long-term memory** — decisions, failures, environment, open questions | **Permanent.** Accumulates across all sessions. | Every `/handoff` — Snapshot + Environment replaced; Decision Log + Failure Memory appended |
| `HANDOFF-YYYY-MM-DD.ftmd` | **Session snapshot** — completed work, git state, next steps, pitfalls, file map | **Disposable.** Read once then archived to `.ftmd.done` | Generated fresh each `/handoff` |

**The insight:** Decisions and lessons compound over time — they belong in persistent storage. Session snapshots are ephemeral — they serve one transfer then become history. Separating them is what makes the system work.

## Quick Start

```bash
# Install — one file, one directory
# Unix / macOS
mkdir -p ~/.claude/skills/handoff
cp SKILL.md ~/.claude/skills/handoff/SKILL.md

# Windows
mkdir %USERPROFILE%\.claude\skills\handoff
copy SKILL.md %USERPROFILE%\.claude\skills\handoff\SKILL.md
```

That's it. No dependencies, no config, no setup. Just copy the file.

```bash
# End of session → save
/handoff

# New session → resume
先读 HANDOFF
```

> ⚡ **「先读 HANDOFF」** is the canonical trigger phrase. Say exactly these four characters at the start of any new session, and Claude will read PROJECT.ftmd + the latest HANDOFF, verify git state, spot-check claims, and pick up where you left off — no re-explaining, no lost context.

### 🔔 Auto-Reminder — Don't Remember to Say It

Tired of forgetting to say "先读 HANDOFF"? Let Claude ask you instead:

```bash
python install_reminder.py
```

One command. Restart Claude Code. Every new session starts with a friendly reminder — no memorization required.

> 💡 If you installed via AI, your Claude will offer to set this up for you after the first `/handoff`.

📄 **[See a complete example](HANDOFF-example.ftmd)** — a realistic handoff showing all 9 sections in action.

## Commands

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/handoff` | Generate HANDOFF + update PROJECT + run cleanup | End of a productive session |
| `/handoff status` | One-line status: stage, progress, focus | Quick check — "where are we?" |
| `/handoff timeline` | Decision Log + Failure Memory, oldest first | Understand how the project evolved |
| `/handoff doctor` | Health check across 6 dimensions | Diagnose what's missing or stale |

### What `/handoff` Actually Does

1. **Short-Session Gate** — Skips generation if the session was trivial (no files changed, no decisions made, pure Q&A)
2. **Verification Protocol** — Runs `git status` and `git diff` (if available), re-reads referenced files, executes tests (if available)
3. **Environment Capture** — Records OS, shell, Node, Python, Git, and Claude Code versions
4. **Generates HANDOFF** — All 9 sections with evidence-tagged claims
5. **Updates PROJECT** — Replaces Snapshot + Environment; appends new decisions and failures
6. **Runs Cleanup** — Archives old `.done` files (7-day TTL), caps active HANDOFF files at 3

## Key Features

### 🔍 Verification Protocol — Nothing From Memory

Every claim in a handoff is tagged:

| Tag | Meaning |
|-----|---------|
| `[V]` | **Verified** — backed by a file, test output, or specific location produced THIS session |
| `[?]` | **Recalled** — from memory, not re-checked; treat as a lead, not a fact |

Every `[V]` claim includes its evidence inline: the file path, line number, test name, or specific location that proves it. The next session can independently verify. This is not convention — it's enforced by the generation protocol. **Claims without evidence are automatically downgraded to `[?]`.**

```
✅  Login redirect fixed [V] (AuthGuard.tsx:42, 7 tests pass in auth-guard.test.tsx)
⚠️  Token refresh might need retry logic [?] — not verified this session
```

### 🧠 Degradation Detection — The Skill Watches Its Own Context

Claude Code sessions have finite context windows. As the conversation grows long, the model starts to degrade — contradicting earlier decisions, re-deriving settled conclusions, forgetting what files contain.

Handoff detects this **in real time**:
- **Reactive:** Watches for contradictory statements, repeated failed approaches, stale file references
- **Proactive:** At ~10 exchange milestones, checks whether meaningful work was done and suggests a handoff
- **Polite:** Caps at 2 reactive + 3 proactive suggestions per session; respects consecutive declines

### 🔄 Source-of-Truth Hierarchy

When a handoff claim conflicts with reality, there's a clear resolution order:

```
1. Running code (what's on disk right now)
2. Test output (what tests actually say)
3. Project docs (README, spec, architecture)
4. PROJECT.ftmd (accumulated project memory)
5. HANDOFF.ftmd (current session snapshot)
6. Older handoffs (archived .done files)
```

Conflicts are surfaced explicitly: *"PROJECT.ftmd says X, but code shows Y. Following the code."* — and PROJECT.ftmd is updated accordingly.

### 🧹 Automatic Cleanup

| Rule | Action |
|------|--------|
| **Read → done** | HANDOFF files are renamed to `.ftmd.done` after being read in a new session |
| **Stale purge** | `.done` files older than 7 days are auto-deleted |
| **Cap enforcement** | Maximum 3 active HANDOFF files per project — oldest gets purged |
| **PROJECT.ftmd** | **Never auto-deleted.** It is the project's permanent memory. |

### 🚦 Short-Session Gate

Not every conversation needs a handoff. If ALL four criteria are met, Handoff asks before generating:

| Gate | Criteria |
|------|----------|
| Topics | < 3 distinct user-initiated topics |
| Output | No files created or modified |
| Decisions | No architectural/technical decisions made |
| Duration | Purely Q&A / information lookup |

This prevents noise — only meaningful work produces handoffs.

### Optional: claude-mem Integration

Handoff is **completely self-contained** — zero external dependencies. If you also use [claude-mem](https://github.com/nanwulan/claude-mem), Handoff detects it automatically and enriches its output with cross-project context. No config needed; it just works.

## The FTMD Format

**FTMD** — Frictionless Transfer Markdown Document — the **AI Agent Context Transfer Format**. A file format designed for one job: transferring project state between AI sessions with zero friction.

### Design Constraints

- **Human-readable** — plain Markdown, no tooling required to read or edit
- **Git-diffable** — structural consistency makes `git diff` meaningful
- **Zero-dependency** — no parser, no schema validator, no runtime
- **Self-describing** — the filename IS the metadata (no YAML frontmatter)

### PROJECT.ftmd — 5 Sections

| # | Section | Update Rule | Content |
|---|---------|-------------|---------|
| 1 | **Snapshot** | Replaced each time | Stage, progress %, focus, last-updated date |
| 2 | **Environment** | Replaced each time | OS, shell, language versions, workspace path |
| 3 | **Decision Log** | Appended (newest first) | Dated entries: context → decision → why → rejected alternatives |
| 4 | **Failure Memory** | Appended (newest first) | Dated entries: attempt → result → root cause → lesson |
| 5 | **Open Questions** | Replaced each time | Currently unresolved questions with context |

Sections 3–4 are capped at **30 entries each** — oldest is evicted when the cap is exceeded.

### HANDOFF.ftmd — 9 Sections

| # | Section | Answers |
|---|---------|---------|
| 1 | **Task** | What are we building? One paragraph of project context. |
| 2 | **Completed** | What is done and verified. Each item has evidence. |
| 3 | **Git Snapshot** | Branch, last commit, changed files (from live `git status` / `git diff --stat`). If not a git repo: "N/A — not a git repo". |
| 4 | **Blocked** | 🔧 Technical blockers (symptom, hypothesis, file/line) + 👤 Decisions needed. |
| 5 | **Next Steps** | Ordered, actionable. Each names a specific file or endpoint. |
| 6 | **Pitfalls** | What went wrong → why → correct approach. Concrete, not vague. |
| 7 | **Decisions** | This session's choices, their rationale, and what was rejected. |
| 8 | **File Map** | Table: every relevant file path → what it does. |
| 9 | **Startup Protocol** | Commands to run + ordered list of files to read first. |

## Design Philosophy

### 1. Zero-Context Target Audience

Every sentence in a handoff must be understandable by someone who was not in the conversation. No "as we discussed," no "continuing from yesterday." The reader has amnesia — write accordingly.

### 2. Evidence Over Memory

The verification protocol exists because AI memory is unreliable. Claims without evidence are not claims — they're hints. The `[V]`/`[?]` system makes this explicit.

### 3. Self-Contained by Default

Handoff works perfectly with nothing but a SKILL.md file. Every integration point with external tools is guarded: *"If available... else skip silently."* No one should install Handoff and hit a missing-dependency error.

### 4. Structured Over Prose

Tables, not walls of text. Sections, not essays. A new session needs to scan, not read. Prose is reserved for context that genuinely defies tabulation.

### 5. Decisions Carry Rationale

Every decision records not just what was chosen, but **what was rejected and why**. This prevents re-litigation — the next session sees the rejected alternatives and doesn't re-propose them.

### 6. Failures Are Assets

Failure Memory is not a bug tracker — it's an institutional knowledge base. Each entry captures the full chain: attempt → result → root cause → lesson. The goal is to prevent the next session (or the next developer) from hitting the same wall.

## Comparison

| | `/handoff` | Git commit messages | README notes | Copied chat logs |
|---|---|---|---|---|
| **Structured sections** | ✅ 9 required | ❌ Free-form | ❌ Ad-hoc | ❌ Raw text |
| **Evidence-tagged claims** | ✅ `[V]`/`[?]` | ❌ | ❌ | ❌ |
| **Environment capture** | ✅ Auto | ❌ | ❌ | ❌ |
| **Decision rationale** | ✅ With rejected alternatives | ⚠️ Sometimes | ❌ | ⚠️ Buried in conversation |
| **Failure lessons** | ✅ Root-cause chain | ❌ | ❌ | ❌ |
| **Auto-cleanup** | ✅ 7-day TTL + cap | ❌ | ❌ | ❌ |
| **AI-optimized** | ✅ Purpose-built | ❌ | ❌ | ⚠️ Verbose, redundant |
| **Git-diffable** | ✅ Structural consistency | ✅ | ❌ | ❌ |

## Compatibility

### Skill (Automated Features)

The full `/handoff` experience — generation, verification, degradation detection, cleanup — requires **Claude Code** as the framework. Copy `SKILL.md` to `~/.claude/skills/handoff/` and it works. The underlying AI model does not matter — tested and confirmed working on Claude, DeepSeek, and others.

| Framework | Works? |
|-----------|:------:|
| Claude Code | ✅ Full functionality |
| Codex | ❌ Different skill system |
| Cursor | ❌ Different skill system |
| Copilot | ❌ Different skill system |

### FTMD Files (Output)

The generated `PROJECT.ftmd` and `HANDOFF-*.ftmd` files are **plain Markdown**. Any AI tool — Claude, ChatGPT, Gemini, Copilot — can read them. Just say:

> "Read PROJECT.ftmd first, then HANDOFF-*.ftmd."

No lock-in. No special format. Write with Claude Code, read with anything.

## Real-World Workflow

```bash
# Session 1: End of productive work
$ /handoff
✅ 交接文档已保存。下次新会话时说「先读 HANDOFF」即可无缝续接。

# Session 2: Start fresh — zero context
$ 先读 HANDOFF
📋 Project: my-app | Stage: Feature Dev | Progress: ~30%
🔜 Next: Implement OAuth callback in src/auth/callback.ts
# → Claude immediately knows the project, picks up the work.

# Session 2 (later): Save progress
$ /handoff                    # Updates PROJECT, generates new HANDOFF, archives old one

# Any time: Quick checks
$ /handoff status             # One-line status
$ /handoff doctor             # Full health check
$ /handoff timeline           # See how decisions evolved
```

> 🔁 **The loop:** `/handoff` → 新会话 → `先读 HANDOFF` → 工作 → `/handoff` → 新会话 → `先读 HANDOFF` ... Each cycle accumulates project knowledge in PROJECT.ftmd while HANDOFF.ftmd carries the immediate baton.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the sync checklist and release process.

## License

MIT — use it, fork it, ship it. If you build something interesting on top of FTMD, open an issue — I'd love to see it.
