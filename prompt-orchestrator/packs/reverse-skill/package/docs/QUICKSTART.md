# reverse-skill Quick Start and Community Questions

## Project positioning

`reverse-skill` is a collection of reverse engineering and security research skills, rules and tool documents that AI clients can read. It is not a single executable application. Before using it, confirm that you have explicit authorization for the analysis target, or that you are using a legitimate CTF, teaching or test environment.

## Basic usage

First download the project:

    git clone https://github.com/zhaoxuya520/reverse-skill.git
    cd reverse-skill

Then give the project directory to your AI client as a workspace or document source. The core files are:

- `RULES.md`: general rules and safety boundaries.
- `skills/MASTER-ROUTING.md`: skill routing and task dispatch.
- `skills/*/SKILL.md`: skill descriptions for each specialty.
- `docs/platforms/`: tool install instructions for each operating system.

The project stays client-neutral, so the official documentation of each client is authoritative for how OpenCode, Codex, Cursor, Claude Code and other clients actually load it; do not assume that one client's plugin or sync format works in other clients.

The most reliable general method is to open the complete repository root as the workspace instead of copying only the `skills/` subdirectory into the client. Confirm that the client can read `AGENTS.md` / `RULES.md` at the root, then run the platform-native `master-route`; if the client does not load project rules automatically, reference `RULES.md` and the target `SKILL.md` explicitly in the conversation.

## OpenCode, Codex and sync problems

If the client shows `Not Synchronizable` or cannot sync, first check that the workspace points at the complete repository root, that file permissions allow reading, and that the client supports the directory format. The most reliable alternative is to open the repository directly in a local workspace and reference the needed rule or skill files explicitly in the conversation. If the problem still reproduces, include the client version, operating system, full error message and minimal reproduction steps in your report.

## The AI refuses an analysis request

An AI's safety policy does not necessarily allow every operation just because the prompt says "I am authorized". Handle only legitimately authorized targets and avoid asking for unauthorized intrusion, credential theft, persistence or destructive operations; you can limit the request to code understanding, sample analysis, vulnerability fixing, CTF or defensive verification. For a specific APK, website or account, prepare a verifiable authorization scope and test environment first.

## Python tools and uv

Standalone command-line tools can use:

    uv tool install PACKAGE_NAME

Project dependencies use an isolated environment:

    uv venv
    uv pip install -r requirements.txt

Do not mechanically replace every `pip` string with `uv pip`; `python -m pip`, the `pipx` bootstrap and existing virtual environments each serve different purposes. If `uv` is not installed, use the operating system package manager or an explicitly created virtual environment, and do not install security tools directly into the system-wide Python.

For fuller install and archive security guidance, see [Installation and Download Security Guidance](UV-AND-DOWNLOAD-SECURITY.md).

## ZIP antivirus alerts and download security

Reverse engineering tools may contain binaries, debuggers, packers or test data that easily trigger antivirus heuristics. An antivirus warning neither proves a file safe nor proves it malicious. Do not disable antivirus software or skip warnings blindly.

Before opening an archive, download it from the expected HTTPS repository or release page, check the checksum or release digest (if provided), inspect the archive content, and scan it with up-to-date security software. Do not run unknown binaries, scripts or installers in it just because the download succeeded.

## Accounts, contributions and vague reports

Follow the terms of service of the AI client, GitHub, tool vendors and the target environment. The repository itself cannot guarantee that third-party platforms will not restrict accounts, and it cannot decide account policies for those platforms. To contribute radare2 or other skills, read `skills/CONTRIBUTING.md` first and submit a small, verifiable pull request.

Only issues with the full error message, environment information and reproduction steps are suitable for further fixing. For reports that only say "virus", "gaha" or "test", add the file name, download URL, scanning product, version and reproduction method.

## External models and APIs

This repository does not bundle, proxy or resell the Grok/xAI API, and it does not collect or distribute Grok API keys. Users configure models and API endpoints themselves in their chosen AI client or provider; when using a third-party relay service, check the provider, data handling terms and key risks yourself.
