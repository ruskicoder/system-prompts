---
name: digital-forensics
description: Use for authorized digital forensics including memory dumps, disk timelines, PCAP investigation, artifact triage, and IR evidence preservation.
---

# Digital Forensics & IR Artifacts

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` or the organization's IR authorization statement
2. `NOW`: confirm that this is **forensics/attribution**, not an offensive scan
3. `NOW`: set up the case; prefer read-only evidence copies (write-protect the original media)
4. `NEXT`: tool-index; Volatility and similar are usually manual
5. `ACT`: preserve hashes → timeline → key artifacts

## When to use

- Memory dump analysis (Volatility 2/3)
- Disk/ E01 / dropped file timeline
- PCAP attribution and protocol reconstruction (can combine with `protocol-reverse/`)
- Host artifacts: Prefetch, Shimcache, Event Log, browser history
- Incident response IOC extraction (combine with `malware-analysis/` / `threat-hunting/`)

## Workflow

### 1. Preservation

```text
□ Compute SHA256; record the time zone and the collection commands
□ Work on a copy; keep the original read-only
□ Write chain of custody notes into the timeline
```

### 2. Memory

```bash
vol -f mem.dmp windows.info
vol -f mem.dmp windows.pslist
vol -f mem.dmp windows.netscan
vol -f mem.dmp windows.cmdline
```

### 3. Host artifacts

```text
□ Event logs: Security / PowerShell / Sysmon
□ Persistence: Run keys, services, scheduled tasks, WMI
□ Execution traces: Amcache, Prefetch, BAM
```

### 4. Network

```text
□ tshark session and DNS statistics
□ Export suspicious flows → protocol-reverse or malware C2 analysis
```

## Toolchain

| Tool | Purpose |
|------|------|
| Volatility 3 | Memory |
| Timeline Explorer / Plaso | Super timeline |
| tshark | PCAP |
| Eric Zimmerman tools | Windows artifacts |
| Autopsy / FTK Imager | Disk |

## References

- `references/forensics-triage.md`
- `../malware-analysis/` `../threat-hunting/` `../protocol-reverse/`

## Routing context

**Upstream**: MASTER R25  
**Downstream**: deep malicious sample analysis → malware-analysis; rules → threat-hunting

## Task completion self-check

- [ ] Did I preserve hashes and follow a copy policy?
- [ ] Can the timeline be rechecked?
- [ ] Are the IOCs redacted and graded?
- [ ] Checklist?