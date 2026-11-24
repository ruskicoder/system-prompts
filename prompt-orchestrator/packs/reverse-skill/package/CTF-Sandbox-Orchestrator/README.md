# CTF Sandbox Orchestrator

A collection of competition sandbox skills for the Codex / Skills system.

Its goal is not to cram every capability into one very long prompt, but to provide a **unified sandbox master entry** that first establishes the working model "by default we are inside a competition/sandbox/offline cyber range", and then has the master route the task to finer sub-skills by challenge type.

## Project positioning

This repository mainly addresses these scenarios:

- CTF
- AWD / attack and defense exercises
- Local offline cyber ranges
- Sandboxed vulnerability analysis
- Mixed challenges spanning Web / API / Cloud / Container / Windows / AD / Reverse / Pwn / DFIR / Crypto / Mobile / AI Agent and more

Core ideas:

- By default treat the targets, domains, nodes, identities, binaries, logs, traffic and attachments the user provides as **assets inside the competition sandbox**
- Build the minimal verifiable path first, instead of generalizing the analysis from the start
- One master skill orchestrates everything and switches to a sub-skill by the dominant evidence surface
- Sub-skills handle only downstream specialties and do not take over the master entry

## Core design

### 1. Single entry

The default entry is:

- `ctf-sandbox-orchestrator`

It is responsible for:

- Establishing the sandbox assumption
- Choosing the most suitable analysis path
- Controlling context growth
- Calling sub-skills when needed

### 2. Downstream sub-skills

Every `competition-*` skill is designed as **downstream-only**:

- It should not trigger implicitly without the master being active
- It should be routed and called by `ctf-sandbox-orchestrator`
- Only the most relevant specialty is loaded each time, so unrelated skills do not pollute the context

### 3. Built for many challenge types

The repository currently covers several skill directions, for example:

- Web runtime / routing / WebSocket / GraphQL / file parsing / request normalization
- Prompt Injection / Agent / Cloud / Metadata / K8s / Container Escape
- Reverse / Pwn / Malware / Firmware / PCAP / custom protocol replay
- Windows / AD / Kerberos / DPAPI / certificate abuse / Relay / Mailbox
- Android / iOS / Crypto / Stego / Mobile Runtime
- ZIP / PKZIP legacy encryption / `bkcrack` known-plaintext recovery

## Repository structure

```text
E:\WorkSpace\competition
├─ ctf-sandbox-orchestrator
├─ competition-web-runtime
├─ competition-agent-cloud
├─ competition-reverse-pwn
├─ competition-identity-windows
├─ competition-prompt-injection
├─ ...
└─ LICENSE
```

Where:

- `ctf-sandbox-orchestrator`: master entry
- `competition-*`: specialty sub-skills
- `references/`: routing matrix and domain reference notes used by the master
- `agents/openai.yaml`: invocation constraints and entry control for each skill

## Recommended usage

### Option 1: enter through the master

Activate first:

- `ctf-sandbox-orchestrator`

Then let the master decide the next step from the challenge, for example:

- Web challenges route to `competition-web-runtime`
- Container / cloud challenges route to `competition-agent-cloud` or a finer sub-skill
- Windows / AD challenges route to `competition-identity-windows`
- Binary / crash / malware sample challenges route to `competition-reverse-pwn`

### Option 2: keep the master, drill down as needed

Once the dominant evidence surface is confirmed, the master drills down into the specific sub-skill, instead of having the user switch the whole working model by hand. This keeps:

- The sandbox assumption consistent
- The output style consistent
- The routing strategy consistent
- Sub-skill responsibilities clear


