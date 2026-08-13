# Awesome System Prompts

> A curated collection of leaked AI system prompts from 73 platforms, an AI agent orchestrator framework, and a prompt management CLI — all in one monorepo.

## Sub-projects

| Directory | Purpose |
|-----------|---------|
| **[platform-prompts/](platform-prompts/)** | 73 platform leaked prompts + Docusaurus website for browsing all prompts (leaks + orchestrator) |
| **[prompt-orchestrator/](prompt-orchestrator/)** | Master AI agent orchestrator framework: AGENT.md, 14 skills, 9 workflows, install scripts for any platform |
| **[prompt-library/](prompt-library/)** | CLI tool for managing, organizing, and executing AI prompts (by Thibault You) |

## Quick Start

```bash
# Browse leaked prompts (Docusaurus site)
cd platform-prompts && pnpm install && pnpm dev

# Install orchestrator to all platforms (Linux / macOS)
cd prompt-orchestrator && bash install/install-all.sh

# Install orchestrator to all platforms (Windows PowerShell / CMD)
cd prompt-orchestrator && powershell .\install\install-all.ps1
# or execute directly in CMD:
install\install-all.bat

# Manage prompts via CLI
cd prompt-library && npm install && npm run build && npm install -g .
prompt-library-cli
```

## License

GPL v3
