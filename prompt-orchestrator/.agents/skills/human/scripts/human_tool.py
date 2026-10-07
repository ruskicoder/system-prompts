#!/usr/bin/env python3
"""Command dispatcher for the `human` skill: python3 human_tool.py <command> [args].

Standard library only. Every command prints JSON; scanners exit 1 when they flag.
"""
import importlib, inspect, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

COMMANDS = {
    "scan": "banned_phrase_scan",
    "structure": "structure_scan",
    "silhouette": "silhouette_scan",
    "readability": "readability_metrics",
    "constraints": "extract_constraints",
    "preserve": "validate_preservation",
    "diff": "diff_check",
    "suggest": "suggest",
    "check-suggestions": "check_suggestions",
    "profile": "voice_profile",
    "card": "voice_card",
    "voice-score": "voice_score",
    "calibrate-pairs": "calibrate_pairs",
    "calibrate-score": "calibrate_score",
    "harvest": "harvest_samples",
    "harvest-classify": "harvest_classify",
    "refine": "run_mimic_refine",
    "stats": "mimic_stats",
    "climb": "run_structure_climb"
}


def main(argv):
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        print("commands: " + ", ".join(COMMANDS))
        return 0 if argv and argv[0] in {"-h", "--help"} else 2
    cmd, args = argv[0], argv[1:]
    mod = importlib.import_module(COMMANDS[cmd])
    sys.argv = [f"human_tool.py {cmd}"] + args
    fn = mod.main
    return fn(args) if inspect.signature(fn).parameters else fn()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]) or 0)
