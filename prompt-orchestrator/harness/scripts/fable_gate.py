#!/usr/bin/env python3
"""PreToolUse hook on Agent/Task: the frontier tier runs only after the user's Fable command.

Denies a spawn of a critical agent, or any spawn on the Fable model, unless the current session
recorded a Fable command. Also denies Fable on a profile without included Fable unless the user
said the credits phrase. Allowed frontier spawns are counted for the weekly estimate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import harness_lib as h


def agent_file_model(name: str) -> str:
    path = Path.home() / ".claude" / "agents" / f"{name}.md"
    try:
        head = path.read_text(encoding="utf-8").split("---", 2)[1]
    except (OSError, IndexError):
        return ""
    match = re.search(r"^model:\s*(\S+)", head, re.M)
    return match.group(1) if match else ""


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


def main() -> int:
    data = h.read_stdin_json()
    if data.get("tool_name") not in ("Agent", "Task"):
        return 0
    tool_input = data.get("tool_input") or {}
    agent = str(tool_input.get("subagent_type") or "").split(":")[-1]
    model = str(tool_input.get("model") or "") or agent_file_model(agent)
    critical_agent = agent in h.CRITICAL_AGENTS
    fable_model = "fable" in model.lower()
    if not (critical_agent or fable_model):
        return 0
    session = h.load_session(data.get("session_id") or "")
    if not session.get("fable_authorized_at"):
        return deny("Frontier tier (critical agents, Fable) runs only on the user's explicit command "
                    "in this session, such as 'spin up Fable'. Suggest it to the user in one line and wait.")
    profile, _ = h.resolve_profile("claude", data.get("cwd"), session)
    if fable_model and not profile.get("fable", {}).get("included") and not session.get("fable_credits"):
        frontier = profile.get("tiers", {}).get("frontier") or "opus"
        return deny(f"Profile {profile.get('name')} has no included Fable. Re-spawn with model "
                    f"'{frontier}', or ask the user to say '{profile['fable'].get('credits_phrase', 'Fable with credits')}'.")
    h.record_fable_run()
    return 0


if __name__ == "__main__":
    h.hook_safe(main)
