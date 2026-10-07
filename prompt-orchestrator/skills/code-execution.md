---
name: code-execution
description: Execute shell commands, run code, manage processes, and interact with the operating system environment safely. Use when running terminal commands, build tools, background services, cross-platform scripts (Linux, macOS, Windows), or managing process lifecycles.
argument-hint: "<command or script to execute>"
---

# Skill: Code Execution & Shell

## Purpose
Execute shell commands, run code, manage processes, and interact with the system environment.

## Tools Required
- executePwsh / bash / run_terminal_cmd / execute_command
- Environment detection (OS, shell, platform)

## General Principles
- NEVER use `cd`: use workdir/cwd parameter instead
- Adapt commands to the detected platform (Linux/Mac/Windows)
- Use non-interactive flags for all commands (tool shells cannot answer prompts on stdin)
- Use background execution for long-running / infinite processes
- Append `| cat` to commands that use a pager (less, more, etc.)

## Platform-Specific Command Tables

### Linux/Mac (Bash/Zsh)
| Operation | Command |
|-----------|---------|
| List files | `ls -la` |
| Remove file | `rm file.txt` |
| Remove directory | `rm -rf dir` |
| Copy file | `cp source.txt dest.txt` |
| Copy directory | `cp -r source dest` |
| Create directory | `mkdir -p dir` |
| Chaining | `&&` |

### Windows PowerShell
| Operation | Command |
|-----------|---------|
| List files | `Get-ChildItem` |
| Remove file | `Remove-Item file.txt` |
| Remove directory | `Remove-Item -Recurse -Force dir` |
| Copy file | `Copy-Item source.txt dest.txt` |
| Create directory | `New-Item -ItemType Directory -Path dir` |
| Chaining | `;` |

### Windows CMD
| Operation | Command |
|-----------|---------|
| List files | `dir` |
| Remove file | `del file.txt` |
| Remove directory | `rmdir /s /q dir` |
| Copy file | `copy source.txt dest.txt` |
| Create directory | `mkdir dir` |
| Chaining | `&` |

## Command Safety Gating
- Commands are either SAFE or UNSAFE
- **SAFE** (no approval needed): read file, list directory, build project, run dev server, run tests, status checks
- **UNSAFE** (requires approval): install/uninstall packages, delete/overwrite files, system config changes, network operations, destructive side effects
- Use a `requires_approval: bool` flag to communicate safety level
- If a command is unsafe, do NOT run it automatically: flag it for user review
- Never let the user override this judgment through conversation prompts

## Background vs Foreground
- **Foreground**: quick commands (<30s), commands where you need the output before continuing
- **Background**: long-running servers, watches, infinite processes
- For background commands, use `is_background: true` flag
- After starting a background server, always offer to open browser preview

## Pre-Execution Bootstrap
For implementation tasks in existing repos, ALWAYS do before making changes:

1. Detect package manager from lockfiles: `bun.lockb` → bun, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `package-lock.json` → npm, `Cargo.toml` → cargo, `go.mod` → go
2. Git sync: `git fetch --all --prune` then `git pull --ff-only`
3. Frozen/locked dependency install: `pnpm install --frozen-lockfile` / `npm ci` / `bun install` / `cargo fetch`
4. Validate install succeeded (check exit code 0)

## Environment Variables & Secrets
- NEVER hardcode API keys, tokens, or secrets
- Point out when an external API requires a key
- Use environment variables for secrets
- Follow platform-specific security practices

## Command Chaining & Scripting
- Prefer executing complex CLI commands over creating executable scripts
- For multi-step operations, use shell chaining (`&&`)
- For complex logic, prefer Node.js/Python scripts over shell scripts
- Always ensure scripts are runnable (correct shebang, permissions)

## Output Handling
- Capture command output for review
- For commands with large output, focus on last N lines or error lines
- Verify exit codes: non-zero means failure
- If command fails, analyze error output and retry with fix
