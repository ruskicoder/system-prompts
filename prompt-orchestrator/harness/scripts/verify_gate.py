#!/usr/bin/env python3
"""Stop and SubagentStop hook (Claude Code and Codex): accept work only when the repo check passes.

Runs the `verify` command from the nearest `.harness.toml` when files changed since the last
passing run. On failure it blocks the stop and returns the last 60 lines of output. After three
blocks in a row it lets the agent stop and tells it to report the failure. No `verify`, no block.
"""
from __future__ import annotations

import hashlib
import json
import subprocess

import harness_lib as h

MAX_LINES = 60
MAX_BLOCKS = 3


def tree_fingerprint(root) -> str | None:
    try:
        status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=root,
                                capture_output=True, text=True, timeout=30)
        if status.returncode != 0:
            return None
        diff = subprocess.run(["git", "diff", "HEAD", "--binary"], cwd=root, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    digest = hashlib.sha256(status.stdout.encode() + diff.stdout)
    for line in status.stdout.splitlines():
        if line.startswith("??"):
            try:
                digest.update((root / line[3:].strip('"')).read_bytes())
            except OSError:
                pass
    return digest.hexdigest()


def run_verify(command: str, root, timeout: int) -> tuple[bool, str]:
    try:
        proc = subprocess.run(command, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"verify command timed out after {timeout}s: {command}"
    output = (proc.stdout + "\n" + proc.stderr).strip().splitlines()
    return proc.returncode == 0, "\n".join(output[-MAX_LINES:])


def main() -> int:
    data = h.read_stdin_json()
    config, root = h.find_repo_config(data.get("cwd"))
    command = config.get("verify")
    if not command or root is None:
        return 0
    key = f"{data.get('session_id') or 'session'}-{data.get('agent_id') or 'main'}"
    state = h.load_session(key)
    fingerprint = tree_fingerprint(root)
    if fingerprint and fingerprint == state.get("verified"):
        return 0
    ok, output = run_verify(command, root, int(config.get("verify_timeout", 600)))
    if ok:
        state.update(verified=fingerprint, blocks=0)
        h.save_session(key, state)
        return 0
    blocks = int(state.get("blocks", 0))
    if blocks >= MAX_BLOCKS:
        state["blocks"] = 0
        h.save_session(key, state)
        print(json.dumps({"systemMessage": f"harness verify gate: `{command}` still fails after "
                          f"{MAX_BLOCKS} attempts; stop allowed. Report the failure to the user."}))
        return 0
    state["blocks"] = blocks + 1
    h.save_session(key, state)
    print(json.dumps({"decision": "block",
                      "reason": f"harness verify gate ({state['blocks']}/{MAX_BLOCKS}): `{command}` failed. "
                                f"Fix it before finishing. Last {MAX_LINES} lines:\n{output}"}))
    return 0


if __name__ == "__main__":
    h.hook_safe(main)
