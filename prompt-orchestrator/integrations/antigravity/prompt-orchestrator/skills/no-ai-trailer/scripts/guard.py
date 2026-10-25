#!/usr/bin/env python3
"""Claude Code PreToolUse guard: refuse a commit, tag, PR or release that carries AI attribution.

Reads the hook JSON on stdin. For Bash, it checks commands that write a commit, tag, note,
PR, issue or release (`git commit|tag|notes|merge|revert|cherry-pick`, `gh pr|issue|release|api`),
including files passed with -F/--file/--body-file/--notes-file. For MCP tools, it checks the
message, body, title and description fields. Exit 2 blocks the call and tells Claude why.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ai_trailer import find  # noqa: E402

WRITES_TEXT = re.compile(
    r"\bgit\b[^|;&]*\b(commit|tag|notes|merge|revert|cherry-pick)\b|\bgh\s+(pr|issue|release|api)\b"
)
FILE_FLAGS = {"-F", "--file", "--body-file", "--notes-file"}
TEXT_FIELDS = {"message", "body", "title", "description", "commit_message", "notes"}


def referenced_files(command: str) -> list[str]:
    try:
        words = shlex.split(command, posix=True)
    except ValueError:
        return []
    out = []
    for i, word in enumerate(words):
        if word in FILE_FLAGS and i + 1 < len(words):
            out.append(words[i + 1])
        elif "=" in word and word.split("=", 1)[0] in FILE_FLAGS:
            out.append(word.split("=", 1)[1])
    return [f for f in out if f != "-"]


def texts_for(payload: dict) -> list[str]:
    tool = payload.get("tool_name", "")
    data = payload.get("tool_input") or {}
    if tool == "Bash":
        command = str(data.get("command", ""))
        if not WRITES_TEXT.search(command):
            return []
        texts = [command, command.replace("\\n", "\n")]
        try:
            texts += shlex.split(command, posix=True)  # catches --trailer "Co-authored-by: ..."
        except ValueError:
            pass
        for name in referenced_files(command):
            path = Path(name).expanduser()
            if not path.is_absolute() and payload.get("cwd"):
                path = Path(payload["cwd"]) / path
            try:
                texts.append(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                pass
        return texts
    if tool.startswith("mcp__"):
        return [str(v) for k, v in data.items() if k in TEXT_FIELDS and isinstance(v, str)]
    return []


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    hits = [hit.strip() for text in texts_for(payload) for hit in find(text)]
    if not hits:
        return 0
    print(
        "no-ai-trailer: blocked. Remove the AI attribution line(s) and retry without them: "
        + "; ".join(dict.fromkeys(hits)),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
