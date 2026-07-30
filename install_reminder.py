#!/usr/bin/env python3
"""
Install the handoff SessionStart auto-reminder hook into Claude Code settings.

Usage:
    python install_reminder.py

What it does:
    1. Copies handoff_reminder.py to the skills directory
    2. Adds a SessionStart hook to ~/.claude/settings.json (creates if needed)
    3. Preserves existing hooks — never overwrites

Safe to run multiple times — will skip if already configured.
"""

import json, os, shutil, sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"
SKILLS_DIR = CLAUDE_DIR / "skills" / "handoff"

REMINDER_SCRIPT = Path(__file__).parent / "handoff_reminder.py"
HOOK_KEY = "handoff-reminder"  # marker to detect already-installed


def find_python():
    """Find a working Python interpreter."""
    candidates = [
        shutil.which("python3"),
        shutil.which("python"),
        Path(sys.executable) if hasattr(sys, "executable") else None,
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(Path(c).resolve())
    print("❌ 找不到 Python。请手动配置。")
    sys.exit(1)


def install():
    print("=== Handoff Auto-Reminder 安装 ===\n")

    # 1. Copy hook script
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    dest = SKILLS_DIR / "handoff_reminder.py"
    shutil.copy(REMINDER_SCRIPT, dest)
    print(f"✅ Hook 脚本已安装: {dest}")

    # 2. Load or create settings
    if SETTINGS_FILE.exists():
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    else:
        settings = {}
    hooks = settings.setdefault("hooks", {})

    # 3. Check if already installed
    existing = hooks.get("SessionStart", [])
    for entry in existing:
        for h in entry.get("hooks", []):
            if h.get("args") and "handoff_reminder.py" in str(h.get("args")):
                print("✅ SessionStart hook 已存在，跳过。")
                return

    # 4. Find Python
    python = find_python()
    print(f"   Python: {python}")

    # 5. Add hook
    hook_entry = {
        "hooks": [
            {
                "type": "command",
                "command": python,
                "args": [str(dest.resolve())],
            }
        ]
    }
    existing.append(hook_entry)

    # 6. Write back
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("✅ SessionStart hook 已配置\n")
    print("重启 Claude Code 即可生效。每次新会话会自动提醒「要不要先读 HANDOFF？」")


if __name__ == "__main__":
    try:
        install()
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        sys.exit(1)
