#!/usr/bin/env python3
"""Harness control commands used by /autosetup, the installer and the user.

    harnessctl.py show [--provider claude|codex]
    harnessctl.py set-profile --provider claude --profile claude-max [--source user]
    harnessctl.py usage --provider claude --json '<desktop usage tool output>'
    harnessctl.py codex-discover        fill codex-plus from the live model list
    harnessctl.py profiles              list installed profiles

`set-profile` re-renders the installed Claude or Codex agents for the new profile, so agent
model fields always match the active plan.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import harness_lib as h
import render

PLAN_TO_PROFILE = {"claude": {"max": "claude-max", "pro": "claude-pro"},
                   "codex": {"plus": "codex-plus"}}
AGENT_DIRS = {"claude": Path.home() / ".claude", "codex": Path.home() / ".codex"}


def installed_agent_dir(provider: str) -> Path:
    return AGENT_DIRS[provider] / "agents"


def rerender(provider: str, profile_name: str) -> int:
    """Rewrite installed harness agents for a provider; leaves files without the marker alone."""
    target = installed_agent_dir(provider).parent
    if not (target / "agents").is_dir():
        return 0
    count = 0
    for agent in render.load_agents():
        rel, text = render.RENDERERS[provider](agent, h.load_profile(profile_name))
        path = target / rel
        if path.exists() and h.MARKER not in path.read_text(encoding="utf-8"):
            continue
        if path.exists():
            path.write_text(text, encoding="utf-8")
            count += 1
    return count


def cmd_show(args) -> int:
    profile, source = h.resolve_profile(args.provider)
    quota = h.read_quota(args.provider)
    mode = h.compute_mode(quota, profile["modes"])
    print(h.mode_tag(profile, source, mode, quota))
    print(f"profile: {profile.get('name')} ({source}); tiers: " +
          ", ".join(f"{k}={v or 'inherit'}" for k, v in profile.get("tiers", {}).items()))
    fable = profile.get("fable", {})
    print("frontier: " + ("Fable 5.1, user command only" if fable.get("included") else
                          f"{profile['tiers'].get('frontier') or 'session model'} at xhigh, user command only"
                          + (f"; Fable only with '{fable['credits_phrase']}'" if fable.get("credits_phrase") else "")))
    print(f"config: {h.user_config_path()}")
    return 0


def cmd_set_profile(args) -> int:
    if not h.load_profile(args.profile):
        print(f"unknown profile '{args.profile}'; installed: {', '.join(list_profiles())}", file=sys.stderr)
        return 2
    cfg = h.user_config()
    cfg.setdefault("profiles", {})[args.provider] = args.profile
    cfg["plan_source"] = args.source
    cfg["plan_set_at"] = dt.date.today().isoformat()
    path = h.write_user_config(cfg)
    changed = rerender(args.provider, args.profile) if args.provider in AGENT_DIRS else 0
    print(f"{args.provider} profile set to {args.profile} ({args.source}) in {path}; "
          f"{changed} installed agent file(s) re-rendered")
    return cmd_show(argparse.Namespace(provider=args.provider))


def parse_usage(raw: dict) -> tuple[str | None, dict, dict | None]:
    plan_obj = raw.get("plan", raw)
    plan = plan_obj.get("plan") if isinstance(plan_obj, dict) else None
    windows, fable = {}, None
    for win in (plan_obj.get("windows") if isinstance(plan_obj, dict) else None) or []:
        label = str(win.get("label", "")).lower()
        resets = win.get("resetsAt")
        try:
            resets_at = dt.datetime.fromisoformat(str(resets).replace("Z", "+00:00")).timestamp()
        except ValueError:
            resets_at = None
        entry = {"used": float(win.get("percentUsed", 0)), "resets_at": resets_at}
        if "fable" in label:
            fable = entry
        elif "5-hour" in label or "five" in label or "session" in label:
            windows["five_hour"] = entry
        elif "weekly" in label and ("all" in label or "fable" not in label) and "seven_day" not in windows:
            windows["seven_day"] = entry
    return plan, windows, fable


def cmd_usage(args) -> int:
    plan, windows, fable = parse_usage(json.loads(args.json))
    h.write_quota(args.provider, windows, "usage-tool", plan=(plan or "").lower() or None, fable=fable)
    suggested = PLAN_TO_PROFILE.get(args.provider, {}).get((plan or "").lower())
    print(json.dumps({"plan": plan, "suggested_profile": suggested, "windows": windows, "fable": fable}))
    return 0


def cmd_codex_discover(args) -> int:
    import codex_bridge
    models = codex_bridge.list_models()
    snapshot = codex_bridge.read_rate_limits()
    h.write_quota("codex", codex_bridge.windows_from(snapshot), "codex", plan=snapshot.get("planType"))
    configured = h.read_toml(Path.home() / ".codex" / "config.toml").get("model")
    names = [m.get("model") or m.get("id") for m in models]
    default = configured or next((m.get("model") for m in models if m.get("isDefault")), names[0] if names else "")
    path = h.profiles_dir() / "codex-plus.toml"
    profile = h.read_toml(path)
    profile["available"] = names
    tiers = profile.setdefault("tiers", {})
    for tier in ("frontier", "lead", "worker", "light"):
        if not tiers.get(tier) or tiers[tier] not in names:
            tiers[tier] = default
    profile["efforts"] = {m.get("model") or m.get("id"): [e.get("reasoningEffort", e) if isinstance(e, dict) else e
                                                         for e in m.get("supportedReasoningEfforts", [])]
                          for m in models}
    header = "".join(line + "\n" for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#"))
    path.write_text(header + h.dump_toml(profile), encoding="utf-8")
    print(json.dumps({"plan": snapshot.get("planType"), "configured": configured, "available": names,
                      "tiers": tiers}, indent=2))
    return 0


def list_profiles() -> list[str]:
    return sorted(p.stem for p in h.profiles_dir().glob("*.toml"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("show")
    p.add_argument("--provider", default="claude", choices=("claude", "codex"))
    p.set_defaults(func=cmd_show)
    p = sub.add_parser("set-profile")
    p.add_argument("--provider", default="claude", choices=("claude", "codex"))
    p.add_argument("--profile", required=True)
    p.add_argument("--source", default="user", choices=("user", "usage-tool", "codex", "installer"))
    p.set_defaults(func=cmd_set_profile)
    p = sub.add_parser("usage")
    p.add_argument("--provider", default="claude", choices=("claude", "codex"))
    p.add_argument("--json", required=True)
    p.set_defaults(func=cmd_usage)
    sub.add_parser("codex-discover").set_defaults(func=cmd_codex_discover)
    sub.add_parser("profiles").set_defaults(func=lambda a: print("\n".join(list_profiles())) or 0)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
