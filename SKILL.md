---
name: handoff
description: Project State Management system. Use when the user says "/handoff", "handoff", "写交接文档", "write handoff", "会话交接", "结束会话", "HANDOFF", "交接", or any subcommand (timeline/status/doctor), or wants to save/resume project context across sessions
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
| OS | Linux x86_64 (or Windows 11, macOS 15, etc.) |
| Shell | bash 5.2 |
| Node | v22.3.0 |
| Python | 3.12.4 |
| Git | 2.47.0 |
| Claude Code | (from `claude --version`) |
| Package Manager | npm 10.x |
| Workspace | /home/user/projects/my-app (or C:\Users\...\my-app) |

## Decision Log
### 2026-07-26 — Use FTMD format over JSON/YAML
- **Context:** Needed a structured handoff format.
- **Decision:** Plain Markdown with 9-section convention.
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
1. **Snapshot:** Replace. Reflect current reality — verify against file state (and git status, if this is a git repo). Don't guess.
2. **Environment:** Replace. Re-run all capture commands fresh.
3. **Decision Log:** Append only if this session made new decisions. Don't duplicate. **Cap: 30 entries max.** If exceeded, delete the oldest (bottom of file) before appending.
4. **Failure Memory:** Append only if this session hit new pitfalls. Don't duplicate. **Cap: 30 entries max.** Same cleanup rule as Decision Log.
5. **Open Questions:** Replace. Remove resolved ones, add new ones.

**If PROJECT.ftmd doesn't exist:** create it with all sections populated.

## HANDOFF.ftmd — Session Snapshot

Generated fresh each `/handoff`. Nine required sections:

| # | Section | Content |
|---|---------|---------|
| 1 | **Task** | What are we building? One paragraph of project context. |
| 2 | **Completed** | What is done and verified. Each item tagged `[V]` or `[?]`. |
| 3 | **Git Snapshot** | Branch, last commit, changed files (from `git status` / `git diff --stat`). If not a git repo, write "N/A — not a git repo". |
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
| Python | `python3 --version` or `python --version` |
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
2. Run **Verification Protocol** (git status/diff if available, re-read files, run tests if available).
3. Collect **Environment** info via auto-capture commands.
4. **Optional — claude-mem:** If claude-mem tools are available (see "Optional: claude-mem Integration"), search for this project's observations and cross-reference with claims. Add "From Memory (claude-mem)" bonus section to the HANDOFF. If NOT available: skip silently.
5. Generate `HANDOFF-YYYY-MM-DD.ftmd` with all 9 sections.
6. Update `PROJECT.ftmd`: replace Snapshot + Environment, append Decision Log + Failure Memory, replace Open Questions.
7. Run **Cleanup Rules**.

### `/handoff timeline`

Read PROJECT.ftmd and display Decision Log + Failure Memory in chronological order (oldest first). No new file generated.

This shows **decision evolution** — when and why the team changed direction, abandoned approaches, or discovered pitfalls. It is NOT a development log: don't list file edits or timestamps. Only entries with strategic weight belong here.

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
| Git repo | `git status` works? (Skip if not a git repo — mark "N/A") |
| Environment | All fields captured? |
| Tests | Test suite exists? Last run passed? (Skip if none — mark "N/A") |
| claude-mem | If available: recent observations for this project? If not: mark "N/A (not installed)" |

Output as a checklist with ✅ / ⚠️ / ❌ markers. End with a one-line recommendation.

## Verification Protocol

**Nothing goes in the handoff from memory alone.** Before writing:

1. **Git reality check (if available):** Run `git status`, `git log --oneline -5`, `git diff --stat`. Use diff output verbatim in Git Snapshot and File Map. If this is not a git repo, skip git verification — mark Git Snapshot as "N/A (not a git repo)" and proceed.
2. **Re-read referenced files:** Every file the handoff mentions must be re-read during generation.
3. **Re-run tests (if available):** If the project has tests, run them. "Tests pass" is only written from output produced NOW. If no test suite exists, skip.

**Tag every claim:**
| Tag | Meaning |
|-----|---------|
| `[V]` | Verified against the project files during this handoff — trustworthy |
| `[?]` | Recalled from memory, not re-checked — treat as a lead only |

**Every `[V]` claim MUST include its evidence source.** Write it inline, not as a separate column. The evidence answers: "How would the next session verify this independently?"

- ✅ Good: `Login redirect fixed [V] (AuthGuard.tsx:42, 7 tests pass in auth-guard.test.tsx)`
- ✅ Good: `Token expiry check added [V] (src/utils/token.ts:15, commit a1b2c3d)`
- ❌ Bad: `Login redirect fixed [V]` — no evidence, untrustworthy

If you can't name a file, test, or specific location that proves the claim, downgrade it to `[?]`.

If verification fails (tests fail, unexpected git state, file deleted), don't abort. Tag affected claims `[?]` and add a **"Verification Notes"** bonus section.

## Optional: claude-mem Integration

Handoff is fully self-contained — it works perfectly without any external tools.
claude-mem is an optional knowledge base that, IF available, enhances Handoff
with cross-project context.

### How to detect claude-mem

claude-mem is available when the session has tools matching `mcp__*mem-search*`.
If no such tools exist: skip ALL claude-mem steps silently. The handoff is complete
without them.

### When claude-mem IS available

**On Write:** During `/handoff` generation, search memory for this project's
observations. Add a "From Memory (claude-mem)" bonus section to HANDOFF.ftmd
with 3–5 most relevant past observations.

**On Read:** After reading HANDOFF in a new session, search memory for the project
to surface relevant institutional knowledge alongside the session snapshot.

**In Doctor:** Report whether recent observations exist for this project.

### Data Boundary

| Data type | Belongs to | Example |
|-----------|-----------|---------|
| User preferences, habits | claude-mem | "Prefers TypeScript" |
| Long-term tech stack choices | claude-mem | "This org uses React + Next.js" |
| Current task, immediate next step | handoff | "Refactoring login module, OAuth not done" |
| This session's decisions | handoff → PROJECT.ftmd | "Chose JWT over session tokens" |
| Pitfalls and lessons from this project | handoff → PROJECT.ftmd | "Don't use xyz v3 with Node 22" |

**Rule of thumb:** If it's true across projects or sessions → claude-mem. If it's
specific to what's happening right now in this project → handoff.

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

Determine in this order — try each, if it fails or doesn't exist, move to the next:
1. Git root (`git rev-parse --show-toplevel`) — if this is a git repo
2. Directory containing `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, or similar project marker
3. Current working directory — if it contains source files, config files, or looks like a project
4. **Fallback:** Current working directory — always available, always writable

**PROJECT.ftmd** → saved at the resolved project root (priority 1-3) or fallback directory (priority 4).

**HANDOFF-YYYY-MM-DD.ftmd** → same location as PROJECT.ftmd. If saved to fallback directory (priority 4), use topic slug: `HANDOFF-<topic-slug>-YYYY-MM-DD.ftmd` to avoid filename collisions.

Never save to `/tmp/` or Desktop.

## Cleanup Rules

Apply on every `/handoff` invocation:

| Rule | Action |
|------|--------|
| **Read → done** | After reading a HANDOFF in a new session, rename to `.ftmd.done` |
| **Stale purge** | Delete `.done` files older than 7 days |
| **HANDOFF count cap** | Keep at most **3** active HANDOFF `.ftmd` files per project. Delete oldest beyond cap. |
| **PROJECT.ftmd** | **Never auto-deleted.** It is the project's long-term memory. |

## New Session Protocol

Two triggers activate this protocol:

| Trigger | Source | Action |
|---------|--------|--------|
| **Auto-detect (unread)** | SessionStart hook detects `HANDOFF-*.ftmd` (not `.done`) | Model reads immediately — unread HANDOFF means the user wants to continue. No need to ask. |
| **Auto-detect (archived)** | SessionStart hook detects only `.ftmd.done` files | Model asks: "📝 上次的交接文档已归档。要不要看看最近的项目状态？" |
| **Manual** | User says "先读 HANDOFF" (canonical resume command) | Read immediately without asking |

### Step 0 — Auto-Read (Unread HANDOFF)

When the SessionStart hook detects an unread HANDOFF (`HANDOFF-*.ftmd`, not `.done`), the model **reads it immediately without asking**. The presence of an unread HANDOFF is itself the user's intent signal — they opened a new session to continue where they left off. Asking "要不要先读？" is unnecessary friction.

> 模型看到信号后直接执行 Step 1，无需等待用户确认。

When the hook detects only archived files (`.ftmd.done`), the model asks first — the user may not want to revisit old state.

**Rationale:** Unread HANDOFF = continuation intent. The user wrote it last session, didn't mark it done, and opened a new session. Every extra click between them and resuming work is friction with no benefit.

### Step 1 — Read

When triggered (auto-detect OR manual "先读 HANDOFF"), read in this order:

1. **PROJECT.ftmd** first — understand the project's identity, history, environment
2. **Latest HANDOFF-*.ftmd** (without `.done`) — get the current task state and next steps
3. **If claude-mem is available:** Search memory for this project — surface relevant observations alongside the handoff. **If not available:** Skip. Steps 1–2 provide sufficient context to start working.

**Multiple HANDOFFs:** Read only the newest. Mark all older HANDOFF `.ftmd` files as `.done`.

**No files exist:** Reply: **"没有找到交接文档。这是一个全新的开始。"**

**Stale warning:** If the newest HANDOFF is older than 14 days: **"⚠️ 这份交接文档已过两周，信息可能已过时。是否仍然继续？"**

### Recovery Protocol

After reading PROJECT.ftmd and HANDOFF, execute these steps before doing any work:

1. **Verify git state (if this is a git repo)** — `git status`, `git log --oneline -3`. Does the branch and last commit match the HANDOFF's Git Snapshot? If not, note the discrepancy. If not a git repo, skip this step.
2. **Spot-check [V] claims** — pick 1–2 `[V]` claims from the Completed section, re-read the referenced file or re-run the referenced test. If evidence doesn't hold, downgrade mentally to `[?]`.
3. **Confirm next step** — read the first item in Next Steps. State it to the user: "HANDOFF says the next step is X. Continue from here?"

If the HANDOFF is confirmed valid, **begin working from Next Steps**. Don't re-explore the project from scratch.

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

**Consecutive rejection:** If the user declines 2 consecutive reminders (any combination of reactive + proactive), stop all further reminders for this session. The user knows — respect their rhythm.

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
| `先读 HANDOFF` (new session, manual) | Read PROJECT.ftmd → read latest HANDOFF → summarize |
| Auto-detect unread (SessionStart hook) | Read immediately — unread HANDOFF = continuation intent |
| Auto-detect archived (SessionStart hook) | Ask user first → if confirmed, read archived state |
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
| Asking "要不要先读？" when unread HANDOFF exists | Unread HANDOFF = continuation intent. Auto-read immediately, don't ask. Only ask when all HANDOFFs are `.done`. |

## Post-Generation

After HANDOFF is written, PROJECT is updated, and cleanup is done:

> **✅ 交接文档已保存。下次新会话时自动加载继续工作，或说「先读 HANDOFF」手动触发。**

The exact phrase **"先读 HANDOFF"** is the manual trigger. But normally you won't need it — when you open a new session and an unread HANDOFF exists, the model auto-reads it immediately.

This closes the loop. Writing a handoff and then continuing in the same session defeats its purpose.

### Proactive reminder setup

After the closing message above, **always** check: does the user already have the SessionStart auto-reminder configured? If not, add one line:

> 💡 要不要我帮你配置自动提醒？以后每次新会话开头会自动加载未读的交接文档，无缝续接。跑一次 `python install_reminder.py` 就行。

If they say yes, run the script for them. If they decline, don't mention it again this session.

## Auto-Reminder (SessionStart Hook)

Want Claude Code to auto-load handoff documents at the start of every session?

### Quick install

```bash
python install_reminder.py
```

Does everything below in one command. Restart Claude Code to activate.

### Manual setup

Copy `handoff_reminder.py` to a permanent location:

```bash
cp handoff_reminder.py /path/to/your/hooks/
```

### 2. Configure settings.json

Add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": ["-u", "/absolute/path/to/handoff_reminder.py"]
          }
        ]
      }
    ]
  }
}
```

On Windows, use the absolute Python interpreter path:

```json
"command": "C:\\Users\\<user>\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
"args": ["-u", "C:\\Users\\<user>\\path\\to\\handoff_reminder.py"]
```

### How it works

The hook runs at SessionStart, detects HANDOFF files, and injects a signal into the model's context via `additionalContext` (stdout JSON). The model then auto-reads unread handoffs or asks about archived ones.

- If an unread `HANDOFF-*.ftmd` exists → model sees signal → auto-reads immediately without asking
- If only archived `.done` files exist → model sees hint about past handoffs → asks user if they want to review
- If no handoff files at all → silent (no interruption)

**Design note:** The hook does NOT output to stderr. Claude Code hook protocol (exit 0) does not display stderr to the terminal — only `additionalContext` reaches the model. The model is responsible for relaying the prompt to the user.
