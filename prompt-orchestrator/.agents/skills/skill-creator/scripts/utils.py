"""Shared utilities for skill-creator scripts."""

from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Folded or literal block scalar (>, |, >-, |-, >+, |+), or a plain
            # or quoted scalar whose text continues on indented lines.
            is_block = value in (">", "|", ">-", "|-", ">+", "|+")
            parts = [] if is_block or not value else [value]
            i += 1
            while i < len(frontmatter_lines) and (
                frontmatter_lines[i].startswith((" ", "\t")) or not frontmatter_lines[i].strip()
            ):
                if frontmatter_lines[i].strip():
                    parts.append(frontmatter_lines[i].strip())
                i += 1
            description = " ".join(parts)
            if not is_block and len(description) >= 2 and description[0] == description[-1] and description[0] in "\"'":
                description = description[1:-1]
            continue
        i += 1

    return name, description, content


def set_skill_description(content: str, description: str) -> str:
    """Return SKILL.md text with the frontmatter description replaced by `description`."""
    lines = content.split("\n")
    end_idx = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    out = lines[:1]
    i = 1
    while i < end_idx:
        if lines[i].startswith("description:"):
            # A block scalar needs no quote escaping and parses back unchanged.
            out.append("description: |")
            out.extend("  " + part for part in description.split("\n"))
            i += 1
            while i < end_idx and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out + lines[end_idx:])
