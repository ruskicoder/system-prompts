#!/usr/bin/env python3
"""Claude Code status line for the harness.

Reads the status JSON on stdin, caches `rate_limits` for the mode hook, and prints one line:
model, mode, 5-hour %, weekly %, context %. When the user config names `statusline_wrap`, that
command runs first with the same input and its output is kept in front of the harness segment.
"""
from __future__ import annotations

import subprocess
import sys

import harness_lib as h


def window(raw: dict | None) -> dict | None:
    if not raw or raw.get("used_percentage") is None:
        return None
    return {"used": float(raw["used_percentage"]), "resets_at": raw.get("resets_at")}


def cache_rate_limits(data: dict) -> dict:
    limits = data.get("rate_limits") or {}
    windows = {k: window(limits.get(k)) for k in ("five_hour", "seven_day")}
    windows = {k: v for k, v in windows.items() if v}
    if windows:
        return h.write_quota("claude", windows, "statusline")
    return h.read_quota("claude")


def wrapped(raw: str) -> str:
    command = h.user_config().get("statusline_wrap")
    if not command:
        return ""
    try:
        out = subprocess.run(command, shell=True, input=raw, capture_output=True, text=True, timeout=5)
        return out.stdout.strip().splitlines()[0] if out.stdout.strip() else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = __import__("json").loads(raw or "{}")
    except ValueError:
        data = {}
    quota = cache_rate_limits(data)
    session = h.load_session(data.get("session_id", ""))
    profile, _ = h.resolve_profile("claude", (data.get("workspace") or {}).get("current_dir"), session)
    mode = h.compute_mode(quota, profile["modes"])
    model = (data.get("model") or {}).get("display_name") or "?"
    ctx = (data.get("context_window") or {}).get("used_percentage")
    segment = (f"{model} | {profile.get('name', '?')} {mode['mode']} | 5h {h.fmt_pct(mode['five_hour'])}"
               f" | wk {h.fmt_pct(mode['weekly'])} | ctx {h.fmt_pct(ctx)}")
    prefix = wrapped(raw)
    print(f"{prefix} | {segment}" if prefix else segment)
    return 0


if __name__ == "__main__":
    h.hook_safe(main)
