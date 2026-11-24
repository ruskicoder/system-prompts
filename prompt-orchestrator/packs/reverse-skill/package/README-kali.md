# Kali Linux entry (short redirect)

> **[kali/README-kali.md](kali/README-kali.md) is authoritative for the details.**  
> This file is only the Kali shortcut at the repository root, so the main text under `kali/` is not maintained twice.

## AI: after reading

```text
1. Detect the package root (the directory that contains README.md / skills/)
2. Read kali/README-kali.md, then read kali/RULES-kali.md and follow it
3. bash kali/scripts/refresh-tool-index.sh
4. Task routing is shared with Windows: skills/MASTER-ROUTING.md, skills/ops/ (scope gate)
5. Report the configuration result to the user
```

## Humans: start in 30 seconds

```bash
cd /path/to/reverse-skill
bash kali/scripts/refresh-tool-index.sh
# Detailed bootstrap and MCP steps: see kali/README-kali.md
```

## Relationship to the main package

| Content | Location |
|------|------|
| Shared skills / routing / ops | `skills/`, `RULES.md` |
| Kali scripts and manifest | `kali/scripts/` |
| Full Kali documentation | **[kali/README-kali.md](kali/README-kali.md)** |

General AI guidance is still in [README_AI.md](README_AI.md) (when the Kali branch is chosen it points to the documents in this directory).
