#!/usr/bin/env python3
"""Detect and strip AI attribution lines from commit, tag, PR and release text.

Stdlib only. Commands:
    ai_trailer.py clean FILE     rewrite FILE in place (commit-msg hook)
    ai_trailer.py filter         read stdin, write the cleaned text to stdout (git filter-branch --msg-filter)
    ai_trailer.py check [FILE]   exit 1 and list the offending lines if FILE or stdin carries attribution

A human co-author is kept. A trailer line is treated as AI attribution when its email
belongs to an AI vendor, or when its name starts with an AI product name and the address is
a noreply or bot address (or absent).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AI_NAME = re.compile(
    r"^\s*(claude|anthropic|openai|chatgpt|gpt-?\d|codex|copilot|cursor|cursoragent|gemini|"
    r"aider|windsurf|codeium|cline|devin|jules|amazon\s+q|q\s+developer|tabnine)\b",
    re.IGNORECASE,
)
AI_DOMAIN = re.compile(
    r"@(?:[\w.-]+\.)?(anthropic\.com|openai\.com|cursor\.com|cursor\.sh|aider\.chat|"
    r"codeium\.com|windsurf\.com|cognition\.ai|devin\.ai|tabnine\.com)\b",
    re.IGNORECASE,
)
BOT_ADDRESS = re.compile(r"noreply|no-reply|\[bot\]|bot@", re.IGNORECASE)
PERSON_TRAILER = re.compile(r"^\s*([A-Za-z][A-Za-z-]*-by)\s*:\s*(.*)$", re.IGNORECASE)
# Product names that are unambiguous in a footer. Common words (cursor, devin, cline, ai) only
# count in their bracketed or "agent" form, so "created by cursor position" survives.
AI_NAMED = (
    r"\b(claude|anthropic|openai|chatgpt|codex|copilot|gemini|aider|windsurf|codeium|tabnine|"
    r"\[cursor\]|cursor\s+(agent|ai)\b|devin\s+ai\b|an?\s+ai\s+(assistant|agent|model|tool)\b)"
)
FOOTER = r"^\s*(\W\s*)?(generated|written|created|authored|made|co-authored)\s+(with|by|using|via)\b.{0,80}"
LINE_PATTERNS = [
    re.compile(FOOTER + AI_NAMED + r".{0,80}$", re.IGNORECASE),
    re.compile(r"^\s*[\w-]*-?session\s*:.*\b(claude\.ai|chatgpt\.com|cursor\.com)\b", re.IGNORECASE),
    re.compile(r"^\s*https?://(claude\.ai/code/session_|chatgpt\.com/codex/tasks/)\S*\s*$", re.IGNORECASE),
    re.compile(r"^\s*made-with\s*:\s*cursor\b", re.IGNORECASE),
    re.compile(r"^\s*ai-(assisted|generated|tool|model|agent)\s*:", re.IGNORECASE),
]


def is_ai_person(value: str) -> bool:
    """True when a `<Key>-by:` trailer value names an AI tool rather than a person."""
    if AI_DOMAIN.search(value):
        return True
    m = re.match(r"^\s*(.*?)\s*(<([^>]*)>)?\s*$", value)
    name, email = (m.group(1), m.group(3) or "") if m else (value, "")
    if not AI_NAME.match(name):
        return False
    return not email or bool(BOT_ADDRESS.search(email) or BOT_ADDRESS.search(name))


def is_ai_line(line: str) -> bool:
    m = PERSON_TRAILER.match(line)
    if m and is_ai_person(m.group(2)):
        return True
    return any(p.search(line) for p in LINE_PATTERNS)


def find(text: str) -> list[str]:
    return [line for line in text.splitlines() if is_ai_line(line)]


def clean(text: str) -> str:
    """Drop AI attribution lines; merge blank lines the removal left behind."""
    kept: list[str] = []
    removed_any = removed_since_text = False
    for line in text.splitlines():
        if is_ai_line(line):
            removed_any = removed_since_text = True
            continue
        if not line.strip() and kept and not kept[-1].strip() and removed_since_text:
            continue
        if line.strip():
            removed_since_text = False
        kept.append(line)
    if not removed_any:
        return text
    while kept and not kept[-1].strip():
        kept.pop()
    return "\n".join(kept) + "\n" if kept else ""


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "clean":
        path = Path(argv[1])
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        new = clean(text)
        if new != text:
            path.write_text(new, encoding="utf-8", errors="surrogateescape")
        return 0
    if argv and argv[0] == "filter":
        sys.stdout.write(clean(sys.stdin.read()))
        return 0
    if argv and argv[0] == "check":
        text = Path(argv[1]).read_text(encoding="utf-8") if len(argv) > 1 else sys.stdin.read()
        hits = find(text)
        for hit in hits:
            print(hit.strip())
        return 1 if hits else 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
