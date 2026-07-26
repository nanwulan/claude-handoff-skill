---
name: handoff
description: Project State Management system. Use when the user says "/handoff", "写交接文档", "write handoff", "会话交接", "结束会话", "HANDOFF", or any subcommand (timeline/status/doctor)
---

# Handoff V2 — Project State Management

## Overview

Handoff is the **project memory layer** for Claude Code. It answers one question:

> "If I open this project in a fresh session, what do I need to know to start working immediately?"

It does this with two files:

| File | Role | Lifespan |
|------|------|----------|
| `PROJECT.ftmd` | Project long-term memory — accumulates decisions, failures, environment | **Persistent.** Lives as long as the project. |
| `HANDOFF-YYYY-MM-DD.ftmd` | Session snapshot — what happened THIS session, what's next | **Short-lived.** Read once then archived. |

Together they form a complete picture: PROJECT.ftmd tells you the project's history and identity; HANDOFF.ftmd tells you exactly where to pick up.

## FTMD Format

FTMD stands for **Frictionless Transfer Markdown Document**. Standard Markdown (CommonMark + GFM tables), UTF-8, LF line endings. No YAML frontmatter, no custom syntax — the filename IS the metadata.

Every factual claim tagged `[V]` (verified) or `[?]` (recalled from memory).

## PROJECT.ftmd — Long-Term Memory

This file lives at project root and is **never deleted**. Each `/handoff` updates it incrementally.

### Sections

| # | Section | Update Rule |
|---|---------|-------------|
| 1 | **Snapshot** | Overwritten each time — current stage, progress estimate, last-updated date |
| 2 | **Environment** | Overwritten each time — auto-captured from the system |
| 3 | **Decision Log** | **Appended** — each entry dated, newest first |
| 4 | **Failure Memory** | **Appended** — each entry dated, newest first |
| 5 | **Open Questions** | Replaced each time — currently unresolved questions |

### Format

```markdown
# Project: <project-name>

## Snapshot
- **Stage:** Feature Development | Bug Fixing | Refactoring | Prototyping | Maintenance
- **Progress:** rough percentage or "just started" / "nearing completion"
- **Focus:** one-line description of current work
- **Updated:** YYYY-MM-DD

## Environment
| Variable | Value |
|----------|-------|
| OS | Windows 11 |
| Shell | bash (Git Bash) |
| Node | v22.3.0 |
| Python | 3.12.4 |
| Git | 2.47.0 |
| Claude Code | (from `claude --version`) |
| Package Manager | npm 10.x |
| Workspace | E:\projects\foo |

## Decision Log
### 2026-07-26 — Use FTMD format over JSON/YAML
- **Context:** Needed a structured handoff format.
- **Decision:** Plain Markdown with 8-section convention.
- **Why:** No tooling dependency, Git-diffable, human-readable.
- **Rejected:** JSON (not readable), YAML (fragile indentation), SQLite (overkill).

## Failure Memory
### 2026-07-26 — Tried to install xyz package
- **Attempt:** `npm install xyz`
- **Result:** Build failed with native module error
- **Root cause:** Node version too new for xyz's node-gyp bindings
- **Lesson:** Pin xyz to v2.x or use Node 20 LTS

## Open Questions
- Q: Migrate to TypeScript? → waiting on team decision
- Q: Use Redis or Postgres for session store? → needs benchmark
```

### Update Rules

**On every `/handoff`:**
1. **Snapshot:** Replace. Reflect current reality (don't guess — verify against git status and file state).
2. **Environment:** Replace. Re-run all capture commands fresh.
3. **Decision Log:** Append only if this session made new decisions. Don't duplicate entries already present.
4. **Failure Memory:** Append only if this session hit new pitfalls. Don't duplicate.
5. **Open Questions:** Replace. Remove resolved ones, add new ones.

**If PROJECT.ftmd doesn't exist:** create it with all sections populated.

## HANDOFF.ftmd — Session Snapshot

Generated fresh each `/handoff`. Eight required sections:

| # | Section | Content |
|---|---------|---------|
| 1 | **Task** | What are we building? One paragraph of project context. |
| 2 | **Completed** | What is done and verified. Each item tagged `[V]` or `[?]`. |
| 3 | **Git Snapshot** | Branch, last commit, changed files (from `git status` / `git diff --stat`). |
| 4 | **Blocked** | Two categories: **🔧 Technical** (symptom, hypothesis, file/line) and **👤 Needs decision** (question for user). |
| 5 | **Next Steps** | Ordered, actionable. Each names a specific file or endpoint. |
| 6 | **Pitfalls** | What went wrong this session. Symptom → root cause → correct approach. |
| 7 | **Decisions** | This session's decisions and WHY. Include rejected alternatives. |
| 8 | **File Map** | Table: file path → what it does. Only files touched this session. |
| 9 | **Startup Protocol** | Commands to run the project, ordered list of files to read first. |

If the session is the project's first, omit sections 6 and 7 (no history yet). Add bonus sections for env vars or API endpoints if applicable.

## Environment Auto-Capture

Run these commands during `/handoff` generation. No user input needed.

| What | Command |
|------|---------|
| OS | `uname -o` or `ver` |
| Shell | `echo $SHELL` or `$SHELL --version` |
| Node | `node --version` |
| Python | `python --version` |
| Git | `git --version` |
| Claude Code | `claude --version` |
| Package Manager | check for `package-lock.json` (npm), `yarn.lock`, `pnpm-lock.yaml` |
| Workspace | `pwd` |

Only run commands that exist. Skip any that fail — don't block the handoff.

## Commands

### `/handoff` (main)

Generate HANDOFF + update PROJECT + run cleanup. This is the primary command. No arguments needed.

**Step-by-step:**
1. Run **Short-Session Gate** check. If all 4 criteria met, ask user before proceeding.
2. Run **Verification Protocol** (git status, git diff, re-read files, run tests if available).
3. Collect **Environment** info via auto-capture commands.
4. Search **claude-mem** for relevant project observations.
5. Generate `HANDOFF-YYYY-MM-DD.ftmd` with all 9 sections.
6. Update `PROJECT.ftmd`: replace Snapshot + Environment, append Decision Log + Failure Memory, replace Open Questions.
7. Run **Cleanup Rules**.

### `/handoff timeline`

Read PROJECT.ftmd and display Decision Log + Failure Memory in chronological order (oldest first). No new file generated.

If PROJECT.ftmd doesn't exist: "📭 这个项目还没有长期记忆。下次 `/handoff` 时会自动创建。"

### `/handoff status`

Read PROJECT.ftmd Snapshot and output a one-line status:

> **项目:** handoff skill | **阶段:** Feature Development | **进度:** ~70% | **焦点:** V2 dual-file model | **更新:** 2026-07-26

If PROJECT.ftmd doesn't exist: "📭 还没有项目状态文件。输入 `/handoff` 来创建。"

### `/handoff doctor`

Check project health. Report what's present and what's missing:

| Check | Looks for |
|-------|-----------|
| PROJECT.ftmd | Exists? Has all 5 sections? |
| Latest HANDOFF | Exists? How old? |
| Git repo | `git status` works? Dirty working tree? |
| Environment | All fields captured? |
| Tests | Test suite exists? Last run passed? |
| claude-mem | Recent observations for this project? |

Output as a checklist with ✅ / ⚠️ / ❌ markers. End with a one-line recommendation.

## Verification Protocol

**Nothing goes in the handoff from memory alone.** Before writing:

1. **Git reality check:** `git status`, `git log --oneline -5`, `git diff --stat`. Use diff output verbatim in Git Snapshot and File Map.
2. **Re-read referenced files:** Every file the handoff mentions must be re-read during generation.
3. **Re-run tests:** If the project has tests, run them. "Tests pass" is only written from output produced NOW.

**Tag every claim:**
| Tag | Meaning |
|-----|---------|
| `[V]` | Verified against the repo during this handoff — trustworthy |
| `[?]` | Recalled from memory, not re-checked — treat as a lead only |

If verification fails (tests fail, unexpected git state, file deleted), don't abort. Tag affected claims `[?]` and add a **"Verification Notes"** bonus section.

## claude-mem Integration

Handoff = point-in-time snapshot. claude-mem = accumulated knowledge. They reinforce each other.

**On Write:** Search memory for project observations → cross-reference with claims → add "From Memory" bonus section with 3–5 most relevant past observations.

**On Read:** After reading handoff, search memory for the project → surface relevant observations → bootstrap the session with both snapshot AND institutional knowledge.

## Short-Session Gate

Before generating, check ALL four. If ALL true, ask: **"这次会话较短，确定要写交接文档吗？"**

| Gate | Criteria |
|------|----------|
| Topics | Fewer than 3 distinct user-initiated topics |
| Output | No files were created or modified |
| Decisions | No architectural/technical decisions were made |
| Duration | The conversation was purely Q&A / information lookup |

Meeting just 1–2 is not enough to gate. All four must align.

## Save Location

Determine in this order:
1. Git root (`git rev-parse --show-toplevel`)
2. Directory containing `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.
3. Current working directory — only if it looks like a project (has source/config files)
4. **Fallback:** `E:\projects\handoffs\`

**PROJECT.ftmd** → saved at the resolved project root (priority 1-3) or fallback directory (priority 4).

**HANDOFF-YYYY-MM-DD.ftmd** → same location as PROJECT.ftmd. If fallback directory, use topic slug: `HANDOFF-<topic-slug>-YYYY-MM-DD.ftmd`.

Never save to `/tmp/` or Desktop.

## Cleanup Rules

Apply on every `/handoff` invocation:

| Rule | Action |
|------|--------|
| **Read → done** | After reading a HANDOFF in a new session, rename to `.ftmd.done` |
| **Stale purge** | Delete `.done` files older than 7 days |
| **HANDOFF count cap** | Keep at most **3** active HANDOFF `.ftmd` files per project. Delete oldest beyond cap. (Down from 5 in V1 — PROJECT.ftmd now carries the history) |
| **PROJECT.ftmd** | **Never auto-deleted.** It is the project's long-term memory. |

## New Session Protocol

When a new session starts, read in this order:

1. **PROJECT.ftmd** first — understand the project's identity, history, environment
2. **Latest HANDOFF-*.ftmd** (without `.done`) — get the current task state and next steps

**Multiple HANDOFFs:** Read only the newest. Mark all older HANDOFF `.ftmd` files as `.done`.

**No files exist:** Reply: **"没有找到交接文档。这是一个全新的开始。"**

**Stale warning:** If the newest HANDOFF is older than 14 days: **"⚠️ 这份交接文档已过两周，信息可能已过时。是否仍然继续？"**

### Source-of-Truth Rank

1. **Running code** — what's on disk right now
2. **Test output** — what tests actually say
3. **Project docs** — README, spec, architecture docs
4. **PROJECT.ftmd** — the project memory file
5. **This HANDOFF** — the session snapshot
6. **Older handoffs** — archived `.done` files

If conflict found: state it explicitly ("PROJECT.ftmd says X, but code shows Y. Following the code.") and update PROJECT.ftmd accordingly.

## Degradation Detection

### Reactive: Context Rot

Watch for: contradicting earlier decisions, re-deriving settled conclusions, describing stale file contents, repeating failed approaches.

**First sign:** "💡 上下文可能正在退化。要不要 `/handoff` 保存进度？"
**Second sign:** "⚠️ 退化迹象增多，建议尽快 `/handoff`。"
**Never suggest more than twice per session.**

### Proactive: Milestone Check

At approximately every 10th exchange, evaluate: was meaningful work done since last handoff? If yes: **"📝 已经聊了约 10 轮了，要不要 `/handoff` 保存一下进度？"**

Don't suggest more than 3 proactive checks per session.

## Writing Standard

- **Zero-context:** Every sentence understandable without being in this conversation.
- **Specific:** "Fix the 401 in `src/api/axios.ts:42`" not "Fix the auth bug".
- **Why included:** Every decision and pitfall states the reasoning.
- **Tables over prose:** Use structured formats; prose only for context that defies tabulation.
- **Length cap:** 200–400 lines. If exceeded, split into core (≤400 lines) and appendix (`HANDOFF-YYYY-MM-DD-appendix.ftmd`).

## Quick Reference

| Trigger | Action |
|---------|--------|
| `/handoff` or `写交接文档` | Generate HANDOFF + update PROJECT + cleanup |
| `/handoff timeline` | Display Decision Log + Failure Memory from PROJECT.ftmd |
| `/handoff status` | One-line project status from PROJECT.ftmd |
| `/handoff doctor` | Health check: PROJECT, HANDOFF, Git, Env, Tests |
| `先读 HANDOFF` (new session) | Read PROJECT.ftmd → read latest HANDOFF → summarize |
| Context rot detected | Suggest `/handoff` (max 2x/session) |
| ~10th exchange milestone | Suggest `/handoff` (max 3x/session) |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing "as we discussed" or "continuing from" | Rewrite for zero-context reader |
| Saving to /tmp or Desktop | Always project root |
| Omitting rejected approaches in Decisions | Include what was NOT chosen and why |
| Vague pitfalls ("careful with auth") | Concrete symptom → root cause → correct approach |
| Skipping the File Map | New session needs to know which files to open |
| Writing "tests pass" from memory | Only from test output produced during THIS handoff |
| Claims without `[V]`/`[?]` tags | Every claim must be tagged |
| Skipping PROJECT.ftmd update | HANDOFF alone isn't enough — decisions and failures must go to PROJECT.ftmd |
| Duplicating Decision Log entries | Check PROJECT.ftmd before appending |
| Deleting PROJECT.ftmd | It is the project's long-term memory — never auto-delete |

## Post-Generation

After HANDOFF is written, PROJECT is updated, and cleanup is done:

**"✅ 交接文档已保存。建议开新会话继续——输入 `先读 HANDOFF` 即可无缝续接。"**

This closes the loop. Writing a handoff and then continuing in the same session defeats its purpose.
