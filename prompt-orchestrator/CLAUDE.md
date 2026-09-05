# Prompt Orchestrator (Claude Code)

This project ships the Central AI Agent Orchestrator. Claude Code loads the full orchestrator automatically via the import below.

@AGENTS.md

## Skills

All framework capabilities are installed as native Claude Code Skills under `.claude/skills/`. Claude loads a skill automatically when a request matches its description, or you can invoke one directly by typing `/` followed by its name (for example `/agent-loop`, `/diagnostic-fix`, `/security-audit-codebase`).

Run `/doctor` at any time to see which skills are loaded, or type `/` alone to browse the full list.
