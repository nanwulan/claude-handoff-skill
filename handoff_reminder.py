import json, os, glob

# Find latest handoff file
claude_dir = os.path.expanduser("~/.claude")
handoff_pattern = os.path.join(claude_dir, "HANDOFF-*.ftmd")
handoffs = glob.glob(handoff_pattern)
done_pattern = os.path.join(claude_dir, "HANDOFF-*.ftmd.done")
dones = glob.glob(done_pattern)

if handoffs:
    latest = max(handoffs, key=os.path.getmtime)
    name = os.path.basename(latest)
    msg = f"📝 检测到交接文档 {name}。要不要先读 HANDOFF？"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg
        }
    }))
elif dones:
    # Has archived handoffs but no active ones
    msg = "📝 上次的交接文档已归档。要不要看看最近的项目状态？说「先读 HANDOFF」即可。"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg
        }
    }))
# else: no handoffs at all → silent
