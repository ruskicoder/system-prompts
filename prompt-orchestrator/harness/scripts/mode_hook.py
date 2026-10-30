#!/usr/bin/env python3
"""SessionStart and UserPromptSubmit hook: tells the lead its plan profile and power mode.

`mode_hook.py start [--provider claude|codex]` prints the mode tag at session start.
`mode_hook.py prompt` prints a tag only when the mode changed, when the user gave a Fable
command (with the quota line the lead must show), or when the user switched the session profile.
Plain stdout from these hooks reaches the model as context.
"""
from __future__ import annotations

import sys
import time

import harness_lib as h

STALE_PLAN_DAYS = 30


def plan_hint(profile: dict, source: str, quota: dict) -> str:
    cfg = h.user_config()
    set_at = cfg.get("plan_set_at")
    if source == "user" and set_at:
        try:
            age = (time.time() - time.mktime(time.strptime(str(set_at)[:10], "%Y-%m-%d"))) / 86400
        except ValueError:
            age = 0
        if age > STALE_PLAN_DAYS:
            return f"[harness: plan profile set {age:.0f} days ago; suggest /autosetup to re-check the plan.]"
    plan = (quota.get("plan") or "").lower()
    if plan and profile.get("detect") and plan not in [d.lower() for d in profile["detect"]]:
        return f"[harness: last usage read shows plan '{plan}' but profile is {profile['name']}; suggest /autosetup.]"
    return ""


def fable_line(profile: dict, mode: dict, quota: dict, prompt: str) -> str:
    fable = profile.get("fable", {})
    credits = fable.get("credits_phrase") and fable["credits_phrase"] in prompt.lower()
    if fable.get("included") or credits:
        target = "Fable" + (" on usage credits" if credits else "")
    else:
        model = profile.get("tiers", {}).get("frontier") or "the session model"
        target = f"{model} at xhigh (Fable not included in {profile.get('name')})"
    warn = mode["mode"] in ("Conserve", "Critical")
    fable_used = (quota.get("fable") or {}).get("used")
    if fable_used is not None and fable_used >= profile["modes"]["fable_warn"]:
        warn = True
    line = (f"[harness frontier: authorized by user command for this session. Target: {target}. "
            f"Mode {mode['mode']}, wk {h.fmt_pct(mode['weekly'])}, {h.fable_status(quota)}. "
            "Before spawning: write acceptance criteria, show the user this quota line, give the agent "
            "minimal context, run at xhigh to completion, end with a criteria check.")
    if warn:
        line += " WARNING: quota is tight; tell the user in one line, then spawn anyway."
    return line + "]"


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    provider = sys.argv[sys.argv.index("--provider") + 1] if "--provider" in sys.argv else "claude"
    data = h.read_stdin_json()
    sid = data.get("session_id") or ""
    session = h.load_session(sid)
    prompt = data.get("prompt") or data.get("user_input") or ""
    out = []

    if action == "prompt":
        match = h.PROFILE_OVERRIDE_RE.search(prompt)
        if match and h.load_profile(match.group(1).lower()):
            session["profile_override"] = match.group(1).lower()
            out.append(f"[harness: profile {session['profile_override']} for this session only]")
    if provider == "codex" and action == "start":
        try:
            import codex_bridge
            codex_bridge.refresh_quota(min_interval=300)
        except Exception as exc:  # noqa: BLE001
            print(f"{h.MARKER}: codex quota refresh failed: {exc}", file=sys.stderr)

    profile, source = h.resolve_profile(provider, data.get("cwd"), session)
    quota = h.read_quota(provider)
    mode = h.compute_mode(quota, profile["modes"])
    tag = h.mode_tag(profile, source, mode, quota)

    if action == "start" or mode["mode"] != session.get("last_mode") or out:
        out.insert(0, tag)
        if not session.get("plan_hint_shown"):
            hint = plan_hint(profile, source, quota)
            if hint:
                out.append(hint)
                session["plan_hint_shown"] = True
    if action == "prompt" and h.is_fable_command(prompt, tuple(h.user_config().get("fable_phrases", h.DEFAULT_FABLE_PHRASES))):
        session["fable_authorized_at"] = time.time()
        session["fable_credits"] = bool(profile.get("fable", {}).get("credits_phrase")
                                        and profile["fable"]["credits_phrase"] in prompt.lower())
        out.append(fable_line(profile, mode, quota, prompt))

    session["last_mode"] = mode["mode"]
    if sid:
        h.save_session(sid, session)
    if out:
        print("\n".join(out))
    return 0


if __name__ == "__main__":
    h.hook_safe(main)
