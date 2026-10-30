"""Shared runtime for the prompt-orchestrator harness hooks (standard library only, Python 3.11+).

Holds config and profile loading, the quota cache, pace and mode computation, and per-session
state. Every hook imports this module from the same directory, so the installed layout is
`<harness home>/scripts/*.py` next to `<harness home>/profiles/*.toml` and `critical.toml`.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

if sys.version_info < (3, 11):  # tomllib arrived in 3.11
    raise SystemExit("prompt-orchestrator harness needs Python 3.11 or later")
import tomllib

HARNESS_HOME = Path(__file__).resolve().parent.parent
MARKER = "prompt-orchestrator-harness"
WINDOWS = {"five_hour": 5 * 3600, "seven_day": 7 * 24 * 3600}
MODES = ("Surplus", "Normal", "Conserve", "Critical")
FALLBACK_PROFILE = {"claude": "claude-pro", "codex": "codex-plus"}
CRITICAL_AGENTS = ("critical-architect", "critical-reviewer")
DEFAULT_FABLE_PHRASES = ("spin up fable", "use fable", "run fable", "fable with credits",
                         "critical-architect", "critical-reviewer")
NEGATION_RE = re.compile(r"\b(?:don't|do not|dont|never|no|without|not)\b(?:\W+\w+){0,2}\W*$")
PROFILE_OVERRIDE_RE = re.compile(r"harness profile:\s*([a-z0-9][a-z0-9-]*)", re.I)
DEFAULT_MODES = {"surplus_pace": -15, "conserve_pace": 10, "conserve_five_hour": 75,
                 "critical": 90, "fable_warn": 80, "stale_minutes": 15}
DEFAULT_FANOUT = {"surplus": 6, "normal": 4, "conserve": 2, "critical": 0}


# ---------------------------------------------------------------- paths

def _base(env_var: str, win_var: str, fallback: str) -> Path:
    root = os.environ.get("PO_HARNESS_HOME")
    if root:
        return Path(root) / {"XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
                             "XDG_STATE_HOME": "state"}[env_var]
    if os.name == "nt":
        return Path(os.environ.get(win_var) or Path.home() / "AppData" / "Local") / "prompt-orchestrator" / (
            "" if win_var == "APPDATA" else env_var.split("_")[1].lower())
    return Path(os.environ.get(env_var) or Path.home() / fallback) / "prompt-orchestrator"


def config_dir() -> Path:
    return _base("XDG_CONFIG_HOME", "APPDATA", ".config")


def cache_dir() -> Path:
    return _base("XDG_CACHE_HOME", "LOCALAPPDATA", ".cache")


def state_dir() -> Path:
    return _base("XDG_STATE_HOME", "LOCALAPPDATA", ".local/state")


def user_config_path() -> Path:
    return config_dir() / "harness.toml"


# ---------------------------------------------------------------- small IO helpers

def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def read_stdin_json() -> dict:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(toml_value(v) for v in value) + "]"
    return json.dumps(str(value))


def toml_key(key) -> str:
    return key if re.fullmatch(r"[A-Za-z0-9_-]+", str(key)) else json.dumps(str(key))


def dump_toml(data: dict) -> str:
    """Write the flat-plus-one-level-tables TOML the harness config uses."""
    lines = [f"{toml_key(k)} = {toml_value(v)}" for k, v in data.items() if not isinstance(v, dict)]
    for key, table in data.items():
        if isinstance(table, dict):
            lines += ["", f"[{toml_key(key)}]"] + [f"{toml_key(k)} = {toml_value(v)}" for k, v in table.items()]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- config and profiles

def user_config() -> dict:
    return read_toml(user_config_path())


def write_user_config(data: dict) -> Path:
    path = user_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# prompt-orchestrator harness user config (written by /autosetup or the installer)\n"
                    + dump_toml(data), encoding="utf-8")
    return path


def find_repo_config(cwd: str | os.PathLike | None) -> tuple[dict, Path | None]:
    """Nearest `.harness.toml` from cwd upward."""
    here = Path(cwd or os.getcwd()).resolve()
    for folder in (here, *here.parents):
        candidate = folder / ".harness.toml"
        if candidate.is_file():
            return read_toml(candidate), folder
    return {}, None


def profiles_dir() -> Path:
    return HARNESS_HOME / "profiles"


def load_profile(name: str) -> dict:
    data = read_toml(profiles_dir() / f"{name}.toml")
    if not data:
        return {}
    data.setdefault("name", name)
    data["modes"] = {**DEFAULT_MODES, **data.get("modes", {})}
    data["fanout"] = {**DEFAULT_FANOUT, **data.get("fanout", {})}
    data.setdefault("fable", {"included": False})
    data.setdefault("tiers", {})
    return data


def resolve_profile(provider: str, cwd=None, session: dict | None = None) -> tuple[dict, str]:
    """Return (profile, source). Order: session override, repo, user config, fallback."""
    session = session or {}
    candidates = [(session.get("profile_override"), "session")]
    repo, _ = find_repo_config(cwd)
    candidates.append((repo.get("profile"), "repo"))
    candidates.append((user_config().get("profiles", {}).get(provider), "user"))
    for name, source in candidates:
        if name:
            profile = load_profile(name)
            if profile:
                return profile, source
    return load_profile(FALLBACK_PROFILE.get(provider, "claude-pro")), "fallback"


def critical_list(cwd=None) -> dict:
    base = read_toml(HARNESS_HOME / "critical.toml")
    repo, _ = find_repo_config(cwd)
    extra = repo.get("critical", {})
    return {"paths": list(base.get("paths", [])) + list(extra.get("paths", [])),
            "keywords": list(base.get("keywords", [])) + list(extra.get("keywords", []))}


# ---------------------------------------------------------------- quota cache and modes

def quota_path(provider: str) -> Path:
    return cache_dir() / f"quota-{provider}.json"


def write_quota(provider: str, windows: dict, source: str, plan: str | None = None,
                fable: dict | None = None, now: float | None = None) -> dict:
    data = {"ts": now or time.time(), "source": source, **windows}
    if plan:
        data["plan"] = plan
    if fable:
        data["fable"] = fable
    previous = read_json(quota_path(provider), {}) or {}
    # The status line never sees the Fable window; keep the last one /autosetup recorded.
    if not fable and previous.get("fable"):
        data["fable"] = previous["fable"]
    if not plan and previous.get("plan"):
        data["plan"] = previous["plan"]
    write_json(quota_path(provider), data)
    return data


def read_quota(provider: str) -> dict:
    return read_json(quota_path(provider), {}) or {}


def is_stale(quota: dict, stale_minutes: float, now: float | None = None) -> bool:
    now = now or time.time()
    return not quota or now - float(quota.get("ts", 0)) > stale_minutes * 60


def pace(window: dict | None, seconds: int, now: float | None = None) -> float | None:
    """Percent used minus percent of the window elapsed, in points."""
    if not window or window.get("used") is None or not window.get("resets_at"):
        return None
    now = now or time.time()
    remaining = float(window["resets_at"]) - now
    elapsed = min(max(1 - remaining / seconds, 0.0), 1.0)
    return float(window["used"]) - 100 * elapsed


def compute_mode(quota: dict, modes: dict, now: float | None = None) -> dict:
    """Mode plus the numbers behind it. Missing or stale data gives Normal, flagged stale."""
    now = now or time.time()
    result = {"mode": "Normal", "stale": is_stale(quota, modes["stale_minutes"], now),
              "five_hour": None, "weekly": None, "weekly_pace": None}
    if result["stale"]:
        return result
    five, week = quota.get("five_hour") or {}, quota.get("seven_day") or {}
    result["five_hour"] = five.get("used")
    result["weekly"] = week.get("used")
    result["weekly_pace"] = pace(week, WINDOWS["seven_day"], now)
    used = [v for v in (result["five_hour"], result["weekly"]) if v is not None]
    if any(v >= modes["critical"] for v in used):
        result["mode"] = "Critical"
    elif ((result["weekly_pace"] is not None and result["weekly_pace"] > modes["conserve_pace"])
          or (result["five_hour"] is not None and result["five_hour"] >= modes["conserve_five_hour"])):
        result["mode"] = "Conserve"
    elif result["weekly_pace"] is not None and result["weekly_pace"] <= modes["surplus_pace"]:
        result["mode"] = "Surplus"
    return result


# ---------------------------------------------------------------- Fable (frontier) tracking

def fable_runs_path() -> Path:
    return state_dir() / "fable_runs.json"


def record_fable_run(now: float | None = None) -> None:
    runs = read_json(fable_runs_path(), []) or []
    runs.append(now or time.time())
    write_json(fable_runs_path(), runs[-500:])


def fable_runs_since(start: float) -> int:
    return sum(1 for t in (read_json(fable_runs_path(), []) or []) if t >= start)


def fable_status(quota: dict, now: float | None = None) -> str:
    """The Fable window when /autosetup recorded one, else weekly % plus local frontier runs."""
    now = now or time.time()
    fable = quota.get("fable") or {}
    if fable.get("used") is not None:
        return f"fable window {fable['used']:.0f}%"
    week = quota.get("seven_day") or {}
    start = float(week["resets_at"]) - WINDOWS["seven_day"] if week.get("resets_at") else now - WINDOWS["seven_day"]
    return f"fable window unknown, {fable_runs_since(start)} frontier run(s) this week"


def is_fable_command(text: str, phrases=DEFAULT_FABLE_PHRASES) -> bool:
    low = (text or "").lower()
    for phrase in phrases:
        start = low.find(phrase)
        while start != -1:
            if not NEGATION_RE.search(low[max(0, start - 40):start]):
                return True
            start = low.find(phrase, start + 1)
    return False


# ---------------------------------------------------------------- session state

def session_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "unknown")
    return state_dir() / "sessions" / f"{safe}.json"


def load_session(session_id: str) -> dict:
    return read_json(session_path(session_id), {}) or {}


def save_session(session_id: str, data: dict) -> None:
    write_json(session_path(session_id), data)
    _prune_sessions()


def _prune_sessions(max_age_days: int = 7) -> None:
    folder = state_dir() / "sessions"
    cutoff = time.time() - max_age_days * 86400
    try:
        for path in folder.glob("*.json"):
            if path.stat().st_mtime < cutoff:
                path.unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- tag

def fmt_pct(value) -> str:
    return "?" if value is None else f"{value:.0f}%"


def mode_tag(profile: dict, source: str, mode: dict, quota: dict) -> str:
    parts = [f"harness: {profile.get('name', '?')}" + ("" if source in ("user", "repo") else f" ({source})"),
             mode["mode"]]
    if mode["stale"]:
        parts.append("quota data stale or missing")
    else:
        pace_txt = "" if mode["weekly_pace"] is None else f" (pace {mode['weekly_pace']:+.0f})"
        parts += [f"5h {fmt_pct(mode['five_hour'])}", f"wk {fmt_pct(mode['weekly'])}{pace_txt}"]
    parts.append(f"fanout max {profile['fanout'].get(mode['mode'].lower(), 4)}")
    parts.append("frontier: user command only")
    tag = "[" + " | ".join(parts) + "]"
    if source == "fallback":
        tag += "\n[harness: no plan profile set. Ask the user to run /autosetup or say 'harness profile: <name>'.]"
    return tag


def hook_safe(main) -> None:
    """Run a hook entry point; any internal error exits 0 so a broken harness never blocks work."""
    try:
        code = main()
    except SystemExit as exc:
        raise exc
    except Exception as exc:  # noqa: BLE001
        print(f"{MARKER}: {type(exc).__name__}: {exc}", file=sys.stderr)
        code = 0
    sys.exit(code or 0)
