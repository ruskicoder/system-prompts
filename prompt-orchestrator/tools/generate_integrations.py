#!/usr/bin/env python3
"""
generate_integrations.py

Single build step that turns the canonical, hand-authored content in
`skills/*.md` and `workflows/*.md` into every file format needed for
Claude, Claude Code, Codex, Cursor, OpenCode, Gemini CLI / Antigravity,
Windsurf, and any other tool that follows the open Agent Skills standard
(https://agentskills.io) or reads an AGENTS.md file.

Why a generator instead of hand-maintained copies?
  - `skills/*.md` and `workflows/*.md` remain the single source of truth.
  - Every IDE/agent-specific file (SKILL.md folders, slash-command
    wrappers, TOML commands, etc.) is *derived* from that source, so
    there is never a risk of the copies drifting out of sync.
  - Re-running this script after editing a skill or workflow regenerates
    every integration in one step:

        python3 tools/generate_integrations.py

This script is intentionally dependency-light (stdlib + PyYAML, which is
already a dependency of skills/validate_skills.py) and safe to re-run
any number of times (it fully regenerates the derived directories below).

Derived, generated directories (do not hand-edit — edit skills/ or
workflows/ and re-run this script instead):
    .agents/skills/<id>/SKILL.md        universal Agent Skills standard
    .claude/skills/<id>/SKILL.md        Claude / Claude Code
    .opencode/skills/<id>/SKILL.md      OpenCode (native skill discovery)
    .opencode/commands/<id>.md          OpenCode  "/id"
    .cursor/commands/<id>.md            Cursor    "/id"
    .codex/prompts/<id>.md              Codex CLI "/prompts:id"
    .gemini/commands/<id>.toml          Gemini CLI + Antigravity "/id"
    .windsurf/workflows/<id>.md         Windsurf  "/id"
    AGENTS.md                           universal instructions fallback
    CLAUDE.md                           Claude Code project memory
    .cursor/rules/orchestrator.mdc      Cursor always-on rule
    .windsurf/rules/orchestrator.md     Windsurf always-on rule
    .claude-plugin/marketplace.json     Claude Code plugin marketplace
    .claude-plugin/plugin.json          Claude Code plugin manifest
    INTEGRATIONS.md                     human-readable compatibility map
    tools/registry.json                 machine-readable registry
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit(
        "PyYAML is required. Install it with:\n"
        "    pip install pyyaml --break-system-packages"
    )

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
WORKFLOWS_DIR = ROOT / "workflows"

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)

# Directories this script fully owns and regenerates on every run.
GENERATED_DIRS = [
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
    ROOT / ".opencode" / "skills",
    ROOT / ".opencode" / "commands",
    ROOT / ".cursor" / "commands",
    ROOT / ".codex" / "prompts",
    ROOT / ".gemini" / "commands",
    ROOT / ".windsurf" / "workflows",
]


def clean(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip()


def parse_entry(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    raw = raw.replace("\r\n", "\n")
    m = FRONTMATTER_RE.match(raw)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    fm_raw = m.group(1)
    data = yaml.safe_load(fm_raw) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")

    body = raw[m.end():].lstrip("\n")

    name = clean(data.get("name")) or path.stem
    description = clean(data.get("description"))
    argument_hint = clean(data.get("argument-hint")) or None
    license_ = clean(data.get("license")) or None

    if not name:
        raise ValueError(f"{path}: missing 'name' in frontmatter")
    if not description:
        raise ValueError(f"{path}: missing 'description' in frontmatter")
    if len(description) > 1024:
        raise ValueError(
            f"{path}: description is {len(description)} chars "
            "(Agent Skills spec caps this at 1024)"
        )
    if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
        raise ValueError(
            f"{path}: name '{name}' must be lowercase alphanumeric with "
            "hyphens only (Agent Skills spec)"
        )

    kind = "workflow" if path.parent.name == "workflows" else "skill"

    return {
        "id": name,
        "kind": kind,
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "description": description,
        "argument_hint": argument_hint,
        "license": license_,
        "body": body.rstrip() + "\n",
    }


def load_registry() -> list[dict]:
    entries = []
    seen = {}
    for directory in (SKILLS_DIR, WORKFLOWS_DIR):
        for path in sorted(directory.glob("*.md")):
            entry = parse_entry(path)
            if entry["id"] in seen:
                raise ValueError(
                    f"Duplicate skill/workflow name '{entry['id']}' in "
                    f"{path} and {seen[entry['id']]}"
                )
            seen[entry["id"]] = path
            entries.append(entry)
    return sorted(entries, key=lambda e: e["id"])


def yaml_frontmatter(fields: dict) -> str:
    """Render an ordered YAML frontmatter block, dropping empty values."""
    clean_fields = {k: v for k, v in fields.items() if v not in (None, "")}
    body = yaml.safe_dump(
        clean_fields, sort_keys=False, default_flow_style=False, allow_unicode=True
    ).strip()
    return f"---\n{body}\n---\n"


# ---------------------------------------------------------------------------
# 1. Agent Skills standard: .agents/skills, .claude/skills, .opencode/skills
# ---------------------------------------------------------------------------

def write_skill_md(entry: dict, base_dir: Path) -> None:
    skill_dir = base_dir / entry["id"]
    skill_dir.mkdir(parents=True, exist_ok=True)
    fm = yaml_frontmatter(
        {
            "name": entry["id"],
            "description": entry["description"],
            "argument-hint": entry["argument_hint"],
            "license": entry["license"],
        }
    )
    header = ""
    if entry["kind"] == "workflow":
        header = (
            f"<!-- Generated from {entry['source']} by "
            "tools/generate_integrations.py. Edit the source file, not "
            "this one. This is an execution WORKFLOW packaged as an "
            "Agent Skill so it is discoverable and directly invocable "
            "(\"/{}\") in every compatible tool. -->\n\n".format(entry["id"])
        )
    else:
        header = (
            f"<!-- Generated from {entry['source']} by "
            "tools/generate_integrations.py. Edit the source file, not "
            "this one. -->\n\n"
        )
    (skill_dir / "SKILL.md").write_text(fm + "\n" + header + entry["body"], encoding="utf-8")


# ---------------------------------------------------------------------------
# 2. Explicit slash-command wrappers per tool
# ---------------------------------------------------------------------------

def pointer_instructions(entry: dict) -> str:
    kind_label = "workflow" if entry["kind"] == "workflow" else "skill"
    return (
        f"This is the `{entry['id']}` {kind_label} from the prompt-orchestrator "
        f"framework (canonical source: `{entry['source']}`, also available at "
        f"`.agents/skills/{entry['id']}/SKILL.md`).\n\n"
        f"1. Load and follow the full instructions in that file exactly.\n"
        f"2. Treat everything after this line as the argument/context for "
        f"the {kind_label}, if anything was provided:\n\n"
    )


def write_opencode_command(entry: dict) -> None:
    fm = yaml_frontmatter(
        {
            "description": short_description(entry["description"]),
        }
    )
    body = pointer_instructions(entry) + "$ARGUMENTS\n"
    out = ROOT / ".opencode" / "commands" / f"{entry['id']}.md"
    out.write_text(fm + "\n" + body, encoding="utf-8")


def write_cursor_command(entry: dict) -> None:
    title = entry["id"].replace("-", " ").title()
    body = (
        f"# {title}\n\n"
        f"{pointer_instructions(entry)}"
        f"$ARGUMENTS\n"
    )
    out = ROOT / ".cursor" / "commands" / f"{entry['id']}.md"
    out.write_text(body, encoding="utf-8")


def write_codex_prompt(entry: dict) -> None:
    fm = yaml_frontmatter(
        {
            "description": short_description(entry["description"]),
            "argument-hint": entry["argument_hint"] or "[context]",
        }
    )
    body = pointer_instructions(entry) + "$ARGUMENTS\n"
    out = ROOT / ".codex" / "prompts" / f"{entry['id']}.md"
    out.write_text(fm + "\n" + body, encoding="utf-8")


def short_description(text: str, limit: int = 200) -> str:
    """Trim a description to ~limit chars without cutting mid-word."""
    if len(text) <= limit:
        return text
    cut = text[: limit + 1]
    space = cut.rfind(" ")
    if space == -1:
        space = limit
    return text[:space].rstrip(",.;: ") + "..."


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def write_gemini_command(entry: dict) -> None:
    description = toml_escape(short_description(entry["description"]))
    prompt_text = (
        f"This is the '{entry['id']}' "
        f"{'workflow' if entry['kind'] == 'workflow' else 'skill'} from the "
        f"prompt-orchestrator framework. Read and follow the instructions in "
        f"'.agents/skills/{entry['id']}/SKILL.md' (canonical source: "
        f"'{entry['source']}') exactly, then apply them to: {{{{args}}}}"
    )
    toml = (
        f'description = "{description}"\n'
        f'prompt = "{toml_escape(prompt_text)}"\n'
    )
    out = ROOT / ".gemini" / "commands" / f"{entry['id']}.toml"
    out.write_text(toml, encoding="utf-8")


def write_windsurf_workflow(entry: dict) -> None:
    fm = yaml_frontmatter({"description": short_description(entry["description"])})
    body = pointer_instructions(entry) + "// turbo\n{{ user input }}\n"
    out = ROOT / ".windsurf" / "workflows" / f"{entry['id']}.md"
    out.write_text(fm + "\n" + body, encoding="utf-8")


# ---------------------------------------------------------------------------
# 3. Root-level universal files
# ---------------------------------------------------------------------------

def write_agents_md() -> None:
    agent_md = (ROOT / "AGENT.md").read_text(encoding="utf-8")
    header = (
        "<!--\n"
        "  AGENTS.md is the emerging cross-vendor standard read natively by\n"
        "  Codex, Gemini CLI, Antigravity, Cursor (fallback), Windsurf,\n"
        "  OpenCode, Amp, Aider, and many other agents/IDEs.\n"
        "  This file is generated from AGENT.md by tools/generate_integrations.py.\n"
        "  Edit AGENT.md and re-run the generator; do not edit this file directly.\n"
        "-->\n\n"
    )
    (ROOT / "AGENTS.md").write_text(header + agent_md, encoding="utf-8")


def write_claude_md() -> None:
    content = (
        "# Prompt Orchestrator (Claude Code)\n\n"
        "This project ships the Central AI Agent Orchestrator. Claude Code "
        "loads the full orchestrator automatically via the import below.\n\n"
        "@AGENTS.md\n\n"
        "## Skills\n\n"
        "All framework capabilities are installed as native Claude Code "
        "Skills under `.claude/skills/`. Claude loads a skill automatically "
        "when a request matches its description, or you can invoke one "
        "directly by typing `/` followed by its name (for example "
        "`/agent-loop`, `/diagnostic-fix`, `/security-audit-codebase`).\n\n"
        "Run `/doctor` at any time to see which skills are loaded, or type "
        "`/` alone to browse the full list.\n"
    )
    (ROOT / "CLAUDE.md").write_text(content, encoding="utf-8")


def write_cursor_rule() -> None:
    out_dir = ROOT / ".cursor" / "rules"
    out_dir.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        "description: Central AI Agent Orchestrator - core operating principles, routing, and safety rules for this repo\n"
        "alwaysApply: true\n"
        "---\n\n"
        "# Prompt Orchestrator\n\n"
        "Load and follow `AGENTS.md` at the repository root as your primary "
        "operating specification for this project: identity & operating "
        "principles, the universal pre-action protocol, power modes, "
        "workflow routing, and the safety engine.\n\n"
        "Reusable capabilities are available as Cursor commands under "
        "`.cursor/commands/` — type `/` in chat to browse and run them "
        "(for example `/agent-loop`, `/plan-execute`, `/security-audit-codebase`). "
        "Each command points to the matching definition in `skills/` or "
        "`workflows/` (also mirrored at `.agents/skills/<name>/SKILL.md`).\n"
    )
    (out_dir / "orchestrator.mdc").write_text(content, encoding="utf-8")


def write_windsurf_rule() -> None:
    out_dir = ROOT / ".windsurf" / "rules"
    out_dir.mkdir(parents=True, exist_ok=True)
    content = (
        "---\n"
        "trigger: always_on\n"
        "description: Central AI Agent Orchestrator for this repo\n"
        "---\n\n"
        "Load and follow `AGENTS.md` at the repository root as your primary "
        "operating specification: identity & operating principles, the "
        "universal pre-action protocol, power modes, workflow routing, and "
        "the safety engine.\n\n"
        "Reusable capabilities are available as Windsurf workflows under "
        "`.windsurf/workflows/` — type `/` in Cascade to browse and run "
        "them (for example `/agent-loop`, `/plan-execute`).\n"
    )
    (out_dir / "orchestrator.md").write_text(content, encoding="utf-8")


def write_claude_plugin(entries: list[dict]) -> None:
    plugin_dir = ROOT / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)

    plugin_json = {
        "name": "prompt-orchestrator",
        "description": (
            "Central AI Agent Orchestrator: routing, safety, and 49 "
            "specialized skills/workflows distilled from 73 leaked "
            "platform prompts."
        ),
        "version": "1.0.0",
        # Points at the generated Agent-Skills-standard folders (each a
        # directory containing SKILL.md), not the flat skills/workflows/
        # source directories. Regenerated by tools/generate_integrations.py.
        "skills": ["./.claude/skills"],
    }
    (plugin_dir / "plugin.json").write_text(
        json.dumps(plugin_json, indent=2) + "\n", encoding="utf-8"
    )

    marketplace_json = {
        "name": "prompt-orchestrator",
        "owner": {"name": "prompt-orchestrator"},
        "plugins": [
            {
                "name": "prompt-orchestrator",
                "source": "./",
                "description": plugin_json["description"],
            }
        ],
    }
    (plugin_dir / "marketplace.json").write_text(
        json.dumps(marketplace_json, indent=2) + "\n", encoding="utf-8"
    )


def write_registry(entries: list[dict]) -> None:
    (ROOT / "tools" / "registry.json").write_text(
        json.dumps(
            [
                {
                    "id": e["id"],
                    "kind": e["kind"],
                    "source": e["source"],
                    "description": e["description"],
                    "argument_hint": e["argument_hint"],
                }
                for e in entries
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_integrations_doc(entries: list[dict]) -> None:
    skills = [e for e in entries if e["kind"] == "skill"]
    workflows = [e for e in entries if e["kind"] == "workflow"]

    lines = [
        "# Integrations",
        "",
        "This file is generated by `tools/generate_integrations.py`. It maps "
        "every skill/workflow to the exact file(s) each tool reads.",
        "",
        "## Compatibility matrix",
        "",
        "| Tool | Auto-discovery | Explicit `/name` |",
        "|---|---|---|",
        "| Claude / Claude Code | `.claude/skills/<name>/SKILL.md` (description match) | `.claude/skills/<name>/SKILL.md` (same file — Claude Code skills *are* slash commands) |",
        "| Codex CLI / IDE extension | `.agents/skills/<name>/SKILL.md` (Agent Skills standard) | `.codex/prompts/<name>.md` (`/prompts:<name>`) |",
        "| Cursor | `.cursor/rules/orchestrator.mdc` (always-on context) | `.cursor/commands/<name>.md` |",
        "| OpenCode | `.opencode/skills/<name>/SKILL.md`, `.claude/skills/…`, `.agents/skills/…` (native skill tool) | `.opencode/commands/<name>.md` |",
        "| Gemini CLI | `.agents/skills/<name>/SKILL.md` (Skills framework) | `.gemini/commands/<name>.toml` |",
        "| Antigravity | `.agents/skills/<name>/SKILL.md` (Skills framework, shares Gemini CLI's open-standard support) | `.gemini/commands/<name>.toml` |",
        "| Windsurf | `.windsurf/rules/orchestrator.md` (always-on context) | `.windsurf/workflows/<name>.md` |",
        "| Any other Agent-Skills-compliant tool | `.agents/skills/<name>/SKILL.md` | n/a (falls back to auto-discovery) |",
        "| Anything else | `AGENTS.md` at repo root (plain-text fallback read by nearly every coding agent) | n/a |",
        "",
        f"## Skills ({len(skills)})",
        "",
    ]
    for e in skills:
        hint = f" `{e['argument_hint']}`" if e["argument_hint"] else ""
        lines.append(f"- **`/{e['id']}`**{hint} — {e['description']}")
    lines += ["", f"## Workflows ({len(workflows)})", ""]
    for e in workflows:
        hint = f" `{e['argument_hint']}`" if e["argument_hint"] else ""
        lines.append(f"- **`/{e['id']}`**{hint} — {e['description']}")
    lines.append("")
    (ROOT / "INTEGRATIONS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for d in GENERATED_DIRS:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    entries = load_registry()
    print(f"Loaded {len(entries)} skills/workflows from skills/ and workflows/")

    for entry in entries:
        write_skill_md(entry, ROOT / ".agents" / "skills")
        write_skill_md(entry, ROOT / ".claude" / "skills")
        write_skill_md(entry, ROOT / ".opencode" / "skills")
        write_opencode_command(entry)
        write_cursor_command(entry)
        write_codex_prompt(entry)
        write_gemini_command(entry)
        write_windsurf_workflow(entry)

    write_agents_md()
    write_claude_md()
    write_cursor_rule()
    write_windsurf_rule()
    write_claude_plugin(entries)
    write_registry(entries)
    write_integrations_doc(entries)

    print("Generated:")
    for d in GENERATED_DIRS:
        count = sum(1 for _ in d.rglob("*") if _.is_file())
        print(f"  {d.relative_to(ROOT)}/  ({count} files)")
    print("  AGENTS.md, CLAUDE.md, .cursor/rules/orchestrator.mdc, "
          ".windsurf/rules/orchestrator.md, .claude-plugin/, "
          "INTEGRATIONS.md, tools/registry.json")


if __name__ == "__main__":
    main()
