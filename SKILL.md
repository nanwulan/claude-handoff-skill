---
name: handoff
description: Use when the user says "/handoff", "写交接文档", "write handoff", "会话交接", "结束会话", "HANDOFF", or asks to write a summary for the next conversation before ending a session
---

# Handoff

## Overview

Generate `HANDOFF.ftmd` at project root — a structured document for a fresh AI session with zero prior context. Fully self-contained: no "as discussed", no implicit references.

## FTMD Format

FTMD stands for **Frictionless Transfer Markdown Document**. It is standard Markdown with a lightweight structural contract designed for AI-to-AI handoff.

| Property | Spec |
|----------|------|
| **Extension** | `.ftmd` |
| **Syntax** | Standard Markdown (CommonMark + GFM tables) |
| **Sections** | 8 required sections (see below), each a level-2 heading |
| **Encoding** | UTF-8, LF line endings |
| **Naming** | `HANDOFF-YYYY-MM-DD.ftmd` (project sessions) or `HANDOFF-<topic-slug>-YYYY-MM-DD.ftmd` (non-project) |
| **Frontmatter** | None — the filename IS the metadata |
| **Verification** | Every factual claim tagged `[V]` (verified) or `[?]` (recalled) |

The format is intentionally vanilla Markdown — no YAML frontmatter, no custom syntax. Any Markdown renderer can display it. The 8-section structure is the only contract; tools that consume `.ftmd` files only need to parse level-2 headings and table rows.

## Short-Session Gate

Before generating, check ALL of the following. If ALL are true, the session is too short — ask: **"这次会话较短，确定要写交接文档吗？"**

| Gate | Criteria |
|------|----------|
| **Topics** | Fewer than 3 distinct user-initiated topics |
| **Output** | No files were created or modified |
| **Decisions** | No architectural/technical decisions were made |
| **Duration** | The conversation was purely Q&A / information lookup |

Meeting just 1–2 of these is not enough to gate. All four must align. Don't generate a near-empty document — it wastes the reader's time and clutters the directory.

## Verification Protocol

**Nothing goes in the handoff from memory alone.** Before writing a single line:

1. **Reality check:** If git repo: `git status`, `git log --oneline -5`, `git diff --stat`. Use the diff output verbatim in the File Map and Completed sections — this is your primary evidence for `[V]` claims. If NOT a git repo: list recently modified files (`ls -lt` or equivalent), note any files changed during this session
2. **Re-read referenced files:** Every file the handoff will mention must be re-read during the handoff itself
3. **Re-run tests:** If the project has tests, run them now. "Tests pass" is only written from output produced during this handoff

**Tag every claim:**
| Tag | Meaning |
|-----|---------|
| `[V]` | Verified against the repo during this handoff — trustworthy |
| `[?]` | Recalled from memory, not re-checked — treat as a lead only |

The `[?]` tag should be rare. If most claims are `[?]`, the handoff is low-quality and the verification steps above weren't followed.

### When Verification Fails

If the reality check reveals problems (tests fail, git shows unexpected changes, a file to reference was deleted):
- **Don't abort.** Generate the handoff anyway — a partial snapshot is better than none.
- Tag affected claims as `[?]` and add a **"Verification Notes"** bonus section: what was checked, what failed, and what the expected vs. actual state was.
- If tests can't be run at all (no test suite, environment broken), note that explicitly rather than staying silent.

## claude-mem Integration

Handoff is a point-in-time snapshot. claude-mem is the accumulated knowledge base. They reinforce each other.

### On Write (generating handoff)

1. **Search memory:** Use `mcp__plugin_claude-mem_mcp-search__search` to find observations about the current project — query by project name, key concepts, or files touched
2. **Cross-reference:** For each observation: does it confirm a claim (cite it), contradict a claim (resolve before writing), or add missing context (include it)?
3. **Add "From Memory" bonus section:** List 3–5 most relevant past observations with one-line summaries and observation IDs — a bridge from the snapshot to the full knowledge base

### On Read (resuming from handoff)

After reading the handoff, search memory for the project. Surface the most relevant observations. This bootstraps the new session with both the snapshot AND institutional knowledge.

## Required Sections

All eight sections are REQUIRED. Write each for a reader who knows nothing about this project or conversation.

| # | Section | Content |
|---|---------|---------|
| 1 | **Task** | What are we building? One paragraph of project-level context. |
| 2 | **Completed** | What is done and verified working. Each item tagged `[V]` or `[?]`. Be specific — file names, functions, features. |
| 3 | **Blocked** | What is stuck, split into two categories: **🔧 Technical** (symptom, root-cause hypothesis, file/line) and **👤 Needs decision** (question only the user can answer). Keep these clearly separated. |
| 4 | **Next Steps** | Ordered, actionable next actions. Each step names a specific file or endpoint. |
| 5 | **Pitfalls** | Things that went wrong and MUST NOT be repeated. Each pitfall has: what happened, why, correct approach. |
| 6 | **Decisions** | Key decisions made in this session and WHY. Include approaches that were considered and rejected. |
| 7 | **File Map** | Table: file path → what it does. Only files touched or relevant to current work. |
| 8 | **Startup Protocol** | Exact commands to get the project running, and ordered list of files to read first (ranked by importance). The new session follows this before doing anything else. |

Bonus sections (add if applicable): environment variables, API endpoints.

## Writing Standard

- **Zero-context:** Every sentence understandable without having been in this conversation.
- **Specific:** "Fix the 401 in `src/api/axios.ts:42`" not "Fix the auth bug".
- **Why included:** Every decision and pitfall states the reasoning.
- **Tables over prose:** Use structured formats; prose only for context that defies tabulation.
- **Length cap:** 200–400 lines. If content exceeds 400 lines, split into core (must-read, ≤400 lines) and an appendix file (`HANDOFF-YYYY-MM-DD-appendix.ftmd`). The core must be self-sufficient; the appendix is bonus detail.

## Save Location

Determine where to save in this order:
1. Git root (`git rev-parse --show-toplevel`) if in a repo
2. Directory containing `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.
3. The current working directory — but ONLY if it looks like a project (has source files, config files)
4. **Fallback:** `E:\projects\handoffs\` — for non-project sessions (config work, skill development, general discussions)

Save as:
- **Project directories (priority 1-3):** `<directory>/HANDOFF-YYYY-MM-DD.ftmd` (e.g. `HANDOFF-2026-07-26.ftmd`)
- **Fallback directory (priority 4):** `<directory>/HANDOFF-<topic-slug>-YYYY-MM-DD.ftmd` (e.g. `HANDOFF-handoff-skill-2026-07-26.ftmd`) — the topic slug (3-5 words, kebab-case) prevents unrelated handoffs from getting mixed up in the shared directory

If same day + same topic already exists, append counter: `HANDOFF-handoff-skill-2026-07-26-2.ftmd`.

Never save to `/tmp/` or Desktop.

## Cleanup Rules

Apply these on every `/handoff` invocation:

| Rule | Action |
|------|--------|
| **Read + done** | After reading a handoff in a new session, rename it to `HANDOFF-YYYY-MM-DD.ftmd.done` |
| **Stale purge** | Delete all `.done` files older than 7 days |
| **Count cap** | Project directories: keep at most 5 active `.ftmd` files. Fallback directory (`E:\projects\handoffs\`): keep at most 20 `.ftmd` files. Delete oldest beyond the cap. `.done` files are excluded from the count (handled by stale purge). |

The goal: no stale documents mislead a new session, no runaway disk usage.

## New Session Protocol

When a new session starts, scan for the newest `HANDOFF-*.ftmd` (without `.done`) in the project root. If found, read it before anything else.

**Multiple handoffs:** If more than one `.ftmd` file exists, read ONLY the newest. Mark all older `.ftmd` files as `.done` immediately — they are superseded snapshots. Never read multiple handoffs: the newest one already covers the most recent state.

After reading, summarize: what the project is, current status, next action.

**When no handoff exists:** If the user says "先读 HANDOFF" but no `.ftmd` file is found, reply: **"没有找到交接文档。这是一个全新的开始。"** Then proceed normally — the session is starting fresh and doesn't need bootstrapping.

### Source-of-Truth Rank

When the handoff disagrees with reality, reality always wins. Precedence:

1. **Running code** — what's on disk right now
2. **Test output** — what tests actually say
3. **Project docs** — README, spec, architecture docs
4. **This HANDOFF** — the handoff document
5. **Older handoffs** — archived `.done` files

If a conflict is found, state it explicitly: "HANDOFF says X, but the code now shows Y. Following the code." Never let a stale document override live code.

### [V] Spot-Check

Before trusting `[V]` claims, spot-check 1–2 of them against the current repo: re-read the referenced file and confirm it still exists and matches. If a `[V]` claim has gone stale (file deleted, content changed), downgrade it mentally to `[?]` and flag it to the user. This catches drift that happened between handoff and now.

### Stale Warning

If the handoff file is older than 14 days, add: **"⚠️ 这份交接文档已过两周，信息可能已过时。是否仍然继续？"**

Ask: "Continue from here?" After the user confirms they're continuing, rename it to `.done`.

The user may also say "先读 HANDOFF" to trigger this explicitly.

## Degradation Detection

### Reactive: Watch for Context Rot

Watch for these signs of context rot mid-session:

- Contradicting a decision made earlier in the same session
- Re-deriving something that was already settled
- Describing a file's content that no longer matches reality
- Repeating a failed approach without realizing it was already tried

When any of these are detected, suggest in one sentence: **"💡 这次会话内容较多，上下文可能正在退化。要不要 `/handoff` 写一份交接文档，然后开新会话继续？"** Wait for confirmation — never run automatically.

If the user declines, keep working but stay alert. If a second degradation sign appears later in the same session, suggest again with more urgency: **"⚠️ 上下文退化迹象增多，建议尽快 `/handoff`。"** Don't suggest more than twice per session — after that, trust the user's judgment.

### Proactive: Milestone Check

Even without degradation signs, proactively evaluate at approximately every 10th user exchange. Ask yourself: "Has meaningful work been done since the last handoff (or session start)?" If yes — files were created/changed, decisions were made, bugs were fixed — suggest: **"📝 已经聊了约 10 轮了，要不要 `/handoff` 保存一下进度？"**

This is a gentle nudge, not a demand. If the user says no, reset the counter and check again in another ~10 exchanges. Don't suggest more than 3 proactive checks per session.

## Quick Reference

| Trigger | Action |
|---------|--------|
| `/handoff` or `写交接文档` | Generate timestamped handoff + run cleanup |
| `先读 HANDOFF` (new session) | Find newest `.ftmd`, read, summarize |
| Undone handoff exists at session start | Auto-read newest, summarize status |
| Context rot detected mid-session | Suggest `/handoff` (max 2x per session) |
| Cleanup auto-runs | On every `/handoff` invocation |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing "as we discussed" or "continuing from" | Rewrite as if the reader has never met you |
| Saving to /tmp or Desktop | Always project root |
| Omitting rejected approaches | Decision log must include what was NOT chosen and why |
| Vague pitfalls ("careful with auth") | Each pitfall: concrete symptom → root cause → correct approach |
| Skipping the file map | A new session needs to know which files to open first |
| Writing "tests pass" from memory | Only write test results from output produced during this handoff |
| Claims without `[V]`/`[?]` tags | Every claim must be tagged; `[?]` should be rare |

## Post-Generation

After the HANDOFF file is written, saved, and cleanup is done, end with: **"✅ 交接文档已保存。建议开新会话继续——输入 `先读 HANDOFF` 即可无缝续接。"**

This closes the loop. Writing a handoff and then continuing in the same session defeats its purpose — the handoff goes stale the moment you keep chatting.
