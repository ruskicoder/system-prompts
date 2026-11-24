# System Architecture Diagrams

## Full behavior chain flowchart

```mermaid
flowchart TD
    Start([The user raises a security or reverse engineering task]) --> Detect{Trigger keyword match?}
    Detect -->|Yes| ReadRouting[Read SKILL.md + routing.md]
    Detect -->|No| Normal([Normal conversation])
    
    ReadRouting --> RouteMatch{Routing matrix match?}
    RouteMatch -->|No hit| ProposeNew[Propose a new skill<br/>per CONTRIBUTING.md]
    RouteMatch -->|Hit| CheckJournal[Check field-journal<br/>for similar experience]
    
    CheckJournal --> CheckTools[Read tool-index.md<br/>confirm tool state]
    CheckTools --> ToolOK{Tools available?}
    
    ToolOK -->|Missing| Bootstrap[Call bootstrap-reverse.ps1<br/>automatic install]
    ToolOK -->|Available| Execute[Enter the skill workflow]
    
    Bootstrap --> BootOK{Install succeeded?}
    BootOK -->|Success| Execute
    BootOK -->|Failure| Guide[Print structured guidance<br/>wait for the user to handle it manually]
    Guide --> UserConfirm([The user confirms the install])
    UserConfirm --> Execute
    
    Execute --> TaskDone{Task complete?}
    TaskDone -->|No| Execute
    TaskDone -->|Yes| ReviewCase[Call case-review<br/>validate the evidence graph]
    ReviewCase --> GenReport[Call docs-generator<br/>generate report + diagrams]
    
    GenReport --> WriteJournal[Write back to field-journal<br/>record experience]
    WriteJournal --> UpdateIndex[Update index/routing/manifest]
    UpdateIndex --> Output([Output the final result])
```

## Skills module relationship diagram

```mermaid
flowchart LR
    subgraph Routing layer
        SKILL[SKILL.md<br/>main entry]
        Routing[routing.md<br/>routing matrix]
    end

    subgraph Reverse engineering
        APK[apk-reverse<br/>APK reverse engineering]
        IDA[ida-reverse<br/>IDA Pro]
        R2[radare2<br/>CLI analysis]
        RE[reverse-engineering<br/>general methodology]
        BinDiff[binary-diff<br/>symbol migration]
        PatchDiff[patch-diff-exploit<br/>N-day weaponization]
    end

    subgraph Exploitation
        Pwn[pwn-chain<br/>RE→exploit]
        Firmware[firmware-pentest<br/>full firmware chain]
    end

    subgraph Penetration testing
        Pentest[pentest-tools<br/>toolchain + loop framework]
        SrcHunter[src-hunter<br/>19 playbook]
        EDR[edr-bypass-re<br/>EDR bypass]
    end

    subgraph Web/Browser
        JS[js-reverse<br/>JS signature reverse engineering]
        Browser[browser-automation<br/>Playwright+OpenReverse]
    end

    subgraph Infrastructure
        Bootstrap[bootstrap-reverse.ps1<br/>on-demand bootstrap]
        Discovery[ToolDiscovery.ps1<br/>tool discovery]
        ToolIndex[tool-index<br/>state index]
    end

    subgraph Output layer
        Docs[docs-generator<br/>report generation]
        Diagram[diagram-generator<br/>diagram generation]
        Review[case-review<br/>Evidence graph audit]
        Journal[field-journal<br/>automatic evolution]
    end

    subgraph External
        CTF[CTF-Sandbox-Orchestrator<br/>40+ sub-skills]
    end

    SKILL --> Routing
    Routing --> APK & IDA & R2 & RE & BinDiff & PatchDiff
    Routing --> Pentest & JS & Browser & Pwn & Firmware & EDR
    Routing --> CTF

    Pentest --> SrcHunter
    APK -->|.so offload| IDA
    APK -->|.so offload| R2
    PatchDiff -->|write PoC| Pwn
    Firmware -->|crash found| Pwn
    Pwn -->|integrate| Pentest
    EDR -->|delivery phase| Pentest
    JS -->|browser operation| Browser
    
    Bootstrap --> Discovery --> ToolIndex
    
    APK & IDA & R2 & Pentest & JS -->|task complete| Review
    Review --> Docs
    Docs --> Diagram
    Docs --> Journal
```

## Bootstrap flow

```mermaid
flowchart TD
    Need[Missing tool detected] --> ReadManifest[Read bootstrap-manifest.json]
    ReadManifest --> Kind{Install type?}
    
    Kind -->|github-release-zip| GH[Download and extract ZIP<br/>from the GitHub release]
    Kind -->|pip-package| Pip[pip install]
    Kind -->|npm-mcp| NPM[Start with npx + register MCP]
    Kind -->|npm-global| Global[npm install -g<br/>+ postInstall]
    Kind -->|winget-package| Winget[winget install]
    Kind -->|local-http-mcp| HTTP[Register URL + start service]
    
    GH & Pip & NPM & Global & Winget & HTTP --> Verify{Available after verification?}
    Verify -->|Success| AddPath[Add to PATH<br/>refresh tool-index]
    Verify -->|Failure| Manual[Print manual install guidance]
    
    AddPath --> Continue([Continue the task])
    Manual --> Wait([Wait for user confirmation])
```

## Pentest loop

```mermaid
flowchart TD
    Init[Initialize: set the target, scope and tools] --> Loop

    subgraph Loop[Core loop]
        Align[1. Realign the goal] --> Review[2. Review known findings]
        Review --> Decide[3. Decide the next action]
        Decide --> Risk{4. Risk gate}
        Risk -->|Low/medium/high| Exec[5. Execute the action]
        Risk -->|Critical| Ask[Request user approval]
        Ask -->|Approved| Exec
        Exec --> Record[6. Record the result]
        Record --> Check{7. Self-check}
        Check -->|Continue| Align
        Check -->|Complete| Done
    end

    Done[8. Completion check] --> Report([Generate the final report])
```

## Automatic evolution mechanism

```mermaid
flowchart LR
    Task([Task complete]) --> WriteLog[Write to field-journal<br/>pitfalls + solutions + code]
    WriteLog --> UpdateIdx[Update _index.md<br/>by scenario]
    UpdateIdx --> CheckUpdate{System update needed?}
    
    CheckUpdate -->|Route missing| FixRoute[Update routing.md]
    CheckUpdate -->|Tool change| FixTool[Refresh tool-index]
    CheckUpdate -->|New tool| FixManifest[Update bootstrap-manifest]
    CheckUpdate -->|No update needed| Done([Done])
    
    FixRoute & FixTool & FixManifest --> Done

    NewTask([Next task of the same kind]) --> ReadIdx[Read _index.md]
    ReadIdx --> Reuse[Reuse existing experience<br/>avoid repeating mistakes]
```

## Multi-platform support architecture

```mermaid
flowchart TD
    subgraph Shared["Shared layer (platform-neutral)"]
        Skills[skills/<br/>SKILL.md + routing.md + references]
        CTF[CTF-Sandbox-Orchestrator/<br/>40+ sub-skills]
        Journal[field-journal/<br/>recorded experience]
        Docs[docs-generator + diagram-generator]
    end

    subgraph Windows["Windows platform layer"]
        WinScripts[skills/scripts/*.ps1<br/>PowerShell scripts]
        WinManifest[bootstrap-manifest.json<br/>winget + GitHub ZIP]
        WinRules[RULES.md<br/>Windows rules]
    end

    subgraph Kali["Kali Linux platform layer"]
        KaliScripts[kali/scripts/*.sh<br/>Bash scripts]
        KaliManifest[kali/scripts/bootstrap-manifest.json<br/>apt + pip + GitHub tar]
        KaliRules[kali/RULES-kali.md<br/>Kali rules]
    end

    Skills --> WinScripts & KaliScripts
    CTF --> WinScripts & KaliScripts
    Journal --> WinScripts & KaliScripts

    WinScripts --> WinManifest
    KaliScripts --> KaliManifest

    WinRules --> Skills
    KaliRules --> Skills
```

### Platform selection logic

| Environment | Rules file | Scripts | Package management |
|------|--------------|-----------|--------|
| Windows | `RULES.md` | `skills/scripts/*.ps1` | winget / GitHub Release ZIP |
| Kali Linux | `kali/RULES-kali.md` | `kali/scripts/*.sh` | apt / pip / npm / GitHub tar.gz |

### Kali edition traits

- **Many tools preinstalled**: nmap, sqlmap, hashcat, hydra, metasploit, radare2, binwalk, burpsuite and others need no bootstrap
- **Unified apt management**: no winget, no manual ZIP extraction
- **Native bash**: simpler scripts with no PowerShell dependency
- **Path conventions**: `/usr/bin/`, `/opt/`, `~/tools/`, no drive letter or space problems

## File read sequence diagram

```mermaid
sequenceDiagram
    participant U as User
    participant AI as AI client
    participant R as RULES.md / RULES-kali.md
    participant SK as SKILL.md
    participant RT as routing.md
    participant TI as tool-index.md
    participant FJ as field-journal
    participant SUB as Sub-skill
    participant BS as bootstrap
    participant DOC as docs-generator

    U->>AI: Raises a security task
    AI->>R: Read the routing rules
    AI->>SK: Read the main entry
    AI->>RT: Route match
    AI->>FJ: Look up similar experience
    AI->>TI: Confirm tool state
    alt Tool missing
        AI->>BS: Automatic install (.ps1 or .sh)
        BS-->>AI: Result
    end
    AI->>SUB: Enter the workflow
    AI-->>U: Task result
    AI->>DOC: Generate the report
    AI->>FJ: Write back experience
    AI-->>U: Done
```
