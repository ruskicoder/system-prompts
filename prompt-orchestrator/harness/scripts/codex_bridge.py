#!/usr/bin/env python3
"""Talk to `codex app-server` (JSON-RPC over stdio) for plan quota and the model list.

    codex_bridge.py quota     refresh the Codex quota cache and print it
    codex_bridge.py models    print the visible models as JSON
    codex_bridge.py plan      print the plan type

Methods used: `initialize`, `account/rateLimits/read`, `model/list` (checked against the schema
from `codex app-server generate-json-schema`, codex-cli 0.156.1). Any failure raises; callers
keep their previous data.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time

import harness_lib as h

TIMEOUT = 10


class AppServer:
    def __init__(self):
        exe = shutil.which("codex")
        if not exe:
            raise RuntimeError("codex not found on PATH")
        self.proc = subprocess.Popen([exe, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self.next_id = 0
        self.call("initialize", {"clientInfo": {"name": h.MARKER, "version": "1.1.0"}})
        self.send({"method": "initialized"})

    def send(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def call(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        self.send({"id": self.next_id, "method": method, "params": params or {}})
        deadline = time.time() + TIMEOUT
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                break
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if message.get("id") == self.next_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message.get("result") or {}
        raise RuntimeError(f"{method}: no response within {TIMEOUT}s")

    def close(self) -> None:
        try:
            self.proc.stdin.close()
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except (OSError, subprocess.SubprocessError):
            self.proc.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def to_window(raw: dict | None) -> dict | None:
    if not raw or raw.get("usedPercent") is None:
        return None
    return {"used": float(raw["usedPercent"]), "resets_at": raw.get("resetsAt"),
            "minutes": raw.get("windowDurationMins")}


def windows_from(snapshot: dict) -> dict:
    """Map primary and secondary windows by duration: the 5-hour one and the weekly one."""
    out = {}
    for raw in (snapshot.get("primary"), snapshot.get("secondary")):
        window = to_window(raw)
        if not window:
            continue
        minutes = window.pop("minutes") or 0
        out["seven_day" if minutes and minutes > 24 * 60 else "five_hour"] = window
    return out


def read_rate_limits() -> dict:
    with AppServer() as server:
        result = server.call("account/rateLimits/read", {"excludeResetCreditDetails": True})
    return result.get("rateLimits") or {}


def refresh_quota(min_interval: int = 300) -> dict:
    cached = h.read_quota("codex")
    if cached and time.time() - float(cached.get("ts", 0)) < min_interval:
        return cached
    snapshot = read_rate_limits()
    return h.write_quota("codex", windows_from(snapshot), "codex", plan=snapshot.get("planType"))


def list_models() -> list[dict]:
    models, cursor = [], None
    with AppServer() as server:
        while True:
            result = server.call("model/list", {"cursor": cursor} if cursor else {})
            models += [m for m in result.get("data", []) if not m.get("hidden")]
            cursor = result.get("nextCursor")
            if not cursor:
                return models


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "quota"
    if action == "quota":
        print(json.dumps(refresh_quota(min_interval=0), indent=2))
    elif action == "models":
        print(json.dumps([{"model": m.get("model") or m.get("id"), "displayName": m.get("displayName"),
                           "isDefault": m.get("isDefault"),
                           "efforts": [e.get("reasoningEffort", e) if isinstance(e, dict) else e
                                       for e in m.get("supportedReasoningEfforts", [])]}
                          for m in list_models()], indent=2))
    elif action == "plan":
        print(read_rate_limits().get("planType") or "unknown")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
