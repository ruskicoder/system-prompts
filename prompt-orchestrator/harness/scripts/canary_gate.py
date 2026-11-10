#!/usr/bin/env python3
"""Canary hooks: a one-line drift signal on every reply, checked by script, never blocking.

`canary_gate.py start`                       SessionStart: restart the frame and letter cycle.
`canary_gate.py prompt [--provider codex]`   UserPromptSubmit: handle "canary off|on", draw a probe, inject it.
`canary_gate.py stop [--provider codex]`     Stop: check line 1 and scan the reply; report faults to the user.
`canary_gate.py subagent-start`              SubagentStart: give the subagent its own probe.
`canary_gate.py subagent-stop`               SubagentStop: check the subagent's report.
`canary_gate.py agent-done`                  PostToolUse on Agent: tell the lead which subagents missed.

A miss means the session has probably drifted from its rules; the advice is to rotate the session.
It is never proof that a rule was or was not followed.
"""
from __future__ import annotations

import json
import random
import re
import sys
import tomllib
from pathlib import Path

import harness_lib as h

FRAMES = "⡀⣀⣄⣤⣦⣶⣷⣿"
LETTERS = "abcdefghijklmnopqrstuvwxyz"
MODE_GLYPH = {"Surplus": "▇", "Normal": "▅", "Conserve": "▃", "Critical": "▁"}
CLOSE = {"(": ")", "[": "]", "{": "}", "<": ">"}
LINE_RE = re.compile(r"^([⡀⣀⣄⣤⣦⣶⣷⣿]) ([▇▅▃▁]) ([○░▒▓█]) ([(\[{<])([a-z])([)\]}>])$")
MARKER_RE = re.compile(r"^> canary marker (\d+): (.)$")
# (threshold percent, shade, advice to the model, note to the user)
LEVELS = (
    (75, "█", "Context is 75 percent or more: rotation is mandatory. Finish the current step cleanly, write a "
              "handoff, then rotate the session.", "rotation is mandatory now"),
    (70, "▓", "Context is 70 percent or more: rotate the session once the current task is done.",
     "rotate once the current task is done"),
    (65, "▒", "Context is 65 percent or more: suggest rotating to the user; continue while the task is unfinished.",
     "rotating is strongly suggested"),
    (60, "░", "Context is 60 percent or more: rotation is near.", "rotation is near"),
)
OPENERS = ("Let's", "In order to", "It's worth noting", "Needless to say", "At the end of the day",
           "It goes without saying", "Simply put")
OPENER_RE = re.compile(r"(?:^|[.!?]\s+|\n\s*(?:[-*]\s+|\d+\.\s+)?)(" + "|".join(re.escape(o) for o in OPENERS) + r")\b")
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x26FF), (0x231A, 0x231B), (0x23E9, 0x23FA), (0x2B50, 0x2B50),
                (0x2B55, 0x2B55), (0x2705, 0x2705), (0x2714, 0x2714), (0x2716, 0x2716), (0x2728, 0x2728),
                (0x2733, 0x2734), (0x274C, 0x274C), (0x274E, 0x274E), (0x2753, 0x2757), (0x2795, 0x2797),
                (0x27A1, 0x27A1), (0x27B0, 0x27B0), (0x27BF, 0x27BF), (0xFE0F, 0xFE0F))
CONTRACT = ("Asked", "Done", "State", "Next")
SWITCH_RE = re.compile(r"(?m)^\s*canary (off|on)\s*[.!]?\s*$")  # a line of its own, not a phrase in a sentence


# ---------------------------------------------------------------- configuration and state

def markers(path: Path | None = None) -> dict[int, dict]:
    path = path or h.HARNESS_HOME / "canary.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return {int(k): v for k, v in data.get("markers", {}).items() if v.get("shape") in CLOSE}


def state_key(sid: str) -> str:
    return f"canary-{sid or 'session'}"


def enabled(data: dict, state: dict) -> bool:
    if state.get("off"):
        return False
    config, _ = h.find_repo_config(data.get("cwd"))
    if config.get("canary") is False:
        return False
    return h.user_config().get("canary", True) is not False


def context_percent(sid: str):
    value = h.load_session(f"ctx-{sid or 'session'}").get("ctx")
    return int(value) if isinstance(value, (int, float)) else None  # the probe shows whole numbers


def level(ctx):
    if ctx is None:
        return None
    return next((lv for lv in LEVELS if ctx >= lv[0]), None)


def shade(ctx):
    lv = level(ctx)
    return lv[1] if lv else "○"


def current_mode(provider: str, data: dict) -> str:
    profile, _ = h.resolve_profile(provider, data.get("cwd"), h.load_session(data.get("session_id") or ""))
    return h.compute_mode(h.read_quota(provider), profile["modes"])["mode"]


# ---------------------------------------------------------------- reply checks

def first_line(text: str) -> str:
    return next((line.strip() for line in (text or "").splitlines() if line.strip()), "")


def check_line(line: str, state: dict, marks: dict) -> tuple[list[str], dict]:
    """Return faults and the glyphs actually shown (used as the base for the next reply)."""
    m = LINE_RE.match(line)
    if not m:
        return ["line 1 is not a canary"], {}
    frame, bar, shade_shown, opening, letter, closing = m.groups()
    faults = []
    if CLOSE[opening] != closing:
        faults.append("bracket is not closed with its pair")
    if not state.get("reset") and state.get("frame") and state["frame"] in FRAMES:
        want = FRAMES[(FRAMES.index(state["frame"]) + 1) % len(FRAMES)]
        if frame != want:
            faults.append(f"frame skipped ({state['frame']} then {frame}, expected {want})")
    if not state.get("reset") and state.get("letter") and state["letter"] in LETTERS:
        want = LETTERS[(LETTERS.index(state["letter"]) + 1) % len(LETTERS)]
        if letter != want:
            faults.append(f"letter out of order ({state['letter']} then {letter}, expected {want})")
    if state.get("mode") and bar != MODE_GLYPH.get(state["mode"]):
        faults.append(f"mode bar {bar} does not match {state['mode']}")
    if state.get("ctx") is not None and shade_shown != shade(state["ctx"]):
        faults.append(f"context shade {shade_shown} does not match {state['ctx']:.0f} percent")
    probe = state.get("probe")
    if probe in marks and opening != marks[probe]["shape"]:
        faults.append(f"probe {probe} answered wrong: the rules near that marker may have dropped out")
    return faults, {"frame": frame, "letter": letter}


def strip_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(">"))


def has_emoji(text: str) -> bool:
    return any(lo <= ord(ch) <= hi for ch in text for lo, hi in EMOJI_RANGES)


def tools_used_this_turn(transcript_path) -> bool:
    """Best effort: did the assistant call a tool after the last user prompt?"""
    try:
        with open(transcript_path, "rb") as fh:  # the tail is enough; transcripts grow to many MB
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 512_000))
            lines = fh.read().decode("utf-8", errors="replace").splitlines()[1:]
    except (OSError, TypeError, ValueError):
        return False
    used = False
    for raw in lines:
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        message = entry.get("message") or {}
        content = message.get("content")
        if entry.get("type") == "user":
            is_prompt = isinstance(content, str) or (isinstance(content, list) and any(
                isinstance(c, dict) and c.get("type") == "text" for c in content))
            if is_prompt:
                used = False
        elif entry.get("type") == "assistant" and isinstance(content, list):
            if any(isinstance(c, dict) and c.get("type") == "tool_use" for c in content):
                used = True
    return used


def scan_reply(text: str, worked: bool) -> list[str]:
    prose = strip_code(text)
    faults = []
    if "—" in prose:
        faults.append("em dash in prose")
    if re.search(r"\s–\s", prose):
        faults.append("en dash used as a separator")
    opener = OPENER_RE.search(prose)
    if opener:
        faults.append(f"banned opener '{opener.group(1)}'")
    if has_emoji(text):
        faults.append("emoji in the reply")
    present = [p for p in CONTRACT if re.search(rf"(\*\*{p}\b|^{p}:)", text, re.M)]
    if present and len(present) < len(CONTRACT):
        faults.append("reply contract missing " + ", ".join(p for p in CONTRACT if p not in present))
    elif not present and worked:
        faults.append("reply contract (Asked, Done, State, Next) missing after work")
    return faults


# ---------------------------------------------------------------- marker placement (harnessctl uses this)

def place_markers(root: Path, marks: dict) -> list[str]:
    """Insert or update every marker line in the source files under root. Returns changed paths."""
    changed = []
    by_file: dict[str, list[tuple[int, dict]]] = {}
    for n, spec in sorted(marks.items()):
        by_file.setdefault(spec["file"], []).append((n, spec))
    for rel, items in by_file.items():
        path = root / rel
        lines, skip_blank = [], False
        for ln in path.read_text(encoding="utf-8").splitlines():
            if MARKER_RE.match(ln):  # drop the old marker and the blank line placed with it
                if lines and not lines[-1].strip() and spec_is_end(items, ln):
                    lines.pop()
                skip_blank = True
                continue
            if skip_blank and not ln.strip():
                skip_blank = False
                continue
            skip_blank = False
            lines.append(ln)
        for n, spec in items:
            marker = f"> canary marker {n}: {spec['shape']}"
            if spec["before"] == "END":
                lines += ["", marker]
                continue
            try:
                at = lines.index(spec["before"])
            except ValueError:
                raise SystemExit(f"canary marker {n}: heading not found in {rel}: {spec['before']}")
            lines[at:at] = [marker, ""]
        new = "\n".join(lines).rstrip("\n") + "\n"
        if new != path.read_text(encoding="utf-8"):
            path.write_text(new, encoding="utf-8")
            changed.append(rel)
    return changed


def spec_is_end(items, line: str) -> bool:
    m = MARKER_RE.match(line)
    return bool(m) and any(n == int(m.group(1)) and spec["before"] == "END" for n, spec in items)


def read_markers_in(root: Path, marks: dict) -> list[str]:
    """Problems with the marker lines under root: missing, duplicated or not matching canary.toml."""
    problems = []
    for n, spec in sorted(marks.items()):
        try:
            found = [MARKER_RE.match(ln) for ln in (root / spec["file"]).read_text(encoding="utf-8").splitlines()]
        except OSError:
            problems.append(f"marker {n}: {spec['file']} not readable")
            continue
        hits = [m.group(2) for m in found if m and int(m.group(1)) == n]
        if len(hits) != 1:
            problems.append(f"marker {n}: found {len(hits)} times in {spec['file']}")
        elif hits[0] != spec["shape"]:
            problems.append(f"marker {n}: shape {hits[0]} in {spec['file']}, canary.toml says {spec['shape']}")
    return problems


# ---------------------------------------------------------------- hook entry points

def emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def on_start(data: dict, state: dict) -> None:
    state.update(reset=True, probe=None, ctx_told=0)


def on_prompt(data: dict, state: dict, provider: str) -> None:
    own = h.own_words(data.get("prompt") or data.get("user_input") or "").lower()
    if SWITCH_RE.search(own) and SWITCH_RE.search(own).group(1) == "off":
        state["off"] = True
        print("[canary: off for this session. Do not show the canary line.]")
        return
    if SWITCH_RE.search(own) and SWITCH_RE.search(own).group(1) == "on":
        state["off"] = False
        state["reset"] = True
    if not enabled(data, state):
        return
    marks = markers()
    if not marks:
        return
    sid = data.get("session_id") or ""
    probe = random.choice(sorted(marks))
    ctx = context_percent(sid)
    state.update(probe=probe, ctx=ctx, mode=current_mode(provider, data))
    line = f"[canary: probe {probe}, ctx {'?' if ctx is None else ctx}]"
    lv = level(ctx)
    if lv:
        line += " " + lv[2]
    print(line)


def on_stop(data: dict, state: dict) -> None:
    if not enabled(data, state) or not state.get("probe"):
        return
    text = data.get("last_assistant_message") or ""
    if data.get("stop_hook_active"):  # a continuation after another hook blocked: track, do not judge
        m = LINE_RE.match(first_line(text))
        if m:
            state.update(frame=m.group(1), letter=m.group(5), reset=False)
        return
    faults, shown = check_line(first_line(text), state, markers())
    if shown:
        state.update(shown, reset=False)
    if faults:
        state["misses"] = int(state.get("misses", 0)) + 1
    faults += scan_reply(text, tools_used_this_turn(data.get("transcript_path")))
    notes = []
    lv = level(state.get("ctx"))
    if lv and lv[0] > int(state.get("ctx_told", 0)):
        state["ctx_told"] = lv[0]
        notes.append(f"context {state['ctx']:.0f} percent: {lv[3]}")
    if faults:
        notes.insert(0, "; ".join(faults) + ". The session may have drifted from its rules; consider rotating it")
    if notes:
        emit({"systemMessage": "harness canary: " + ". ".join(notes) + "."})


def on_subagent_start(data: dict, state: dict) -> None:
    if not enabled(data, state):
        return
    marks = markers()
    if not marks:
        return
    probe = random.choice(sorted(marks))
    state.setdefault("sub", {})[data.get("agent_id") or "agent"] = probe
    emit({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext":
          f"[canary: subagent probe {probe}. Line 1 of your final report is the letter a inside the bracket "
          f"shape that the line 'canary marker {probe}' in your rules shows, alone on the line. No emoji.]"}})


def on_subagent_stop(data: dict, state: dict) -> None:
    if data.get("stop_hook_active") or not enabled(data, state):
        return
    probe = state.get("sub", {}).pop(data.get("agent_id") or "agent", None)
    marks = markers()
    if probe not in marks:
        return
    shape = marks[probe]["shape"]
    if first_line(data.get("last_assistant_message") or "") != f"{shape}a{CLOSE[shape]}":
        state.setdefault("dead", []).append(data.get("agent_type") or data.get("agent_id") or "subagent")


def on_agent_done(data: dict, state: dict) -> None:
    dead = state.pop("dead", [])
    if dead:
        emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
              f"harness canary: subagent {', '.join(dead)} answered without its canary probe, so its rules may "
              "not have loaded. Treat that report as unverified, end that subagent and rerun the task in a fresh one."}})


HANDLERS = {"start": on_start, "prompt": on_prompt, "stop": on_stop, "subagent-start": on_subagent_start,
            "subagent-stop": on_subagent_stop, "agent-done": on_agent_done}


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    provider = sys.argv[sys.argv.index("--provider") + 1] if "--provider" in sys.argv else "claude"
    if action not in HANDLERS:
        print(f"usage: canary_gate.py {{{'|'.join(HANDLERS)}}} [--provider claude|codex]", file=sys.stderr)
        return 0
    data = h.read_stdin_json()
    key = state_key(data.get("session_id") or "")
    state = h.load_session(key)
    if action == "prompt":
        on_prompt(data, state, provider)
    else:
        HANDLERS[action](data, state)
    h.save_session(key, state)
    return 0


if __name__ == "__main__":
    h.hook_safe(main)
