---
name: ot-ics
description: Use for authorized OT/ICS security assessment covering Purdue model zoning, PLC/SCADA exposure, industrial protocol discovery, and safe passive-first evaluation.
---

# OT / ICS Security

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md`; **mistakes in industrial control environments can cause physical harm**
2. `NOW`: the written authorization must state clearly: site, network segments, whether active scanning/register writes are allowed
3. `NOW`: case-init; **passive-first** by default; PLC write operations are forbidden before `ready_for_act`
4. `NEXT`: tool-index; most industrial control tools need manual installs and an isolated lab network
5. `ACT`: asset and zone identification → exposure surface → read-only verification

## When to use

- Industrial control/SCADA/DCS security assessment (authorized)
- Purdue model zones and cross-zone conduits
- Exposure of protocols such as Modbus/DNP3/S7/EtherNet/IP
- Engineering workstations, HMIs, historians, jump hosts
- IT/OT convergence boundary (firewall rules, data diodes)

## Safety iron rules (MUST)

```text
MUST NOT, unless explicitly allowed:
- Write coils/registers on a PLC
- Scan production OT across the whole network at high rate
- Interrupt paths related to the safety instrumented system (SIS)
Prefer: read-only identification, traffic mirroring, offline firmware/configuration analysis
```

## Workflow

### Phase 1: Zones and assets

```text
□ Purdue L0–L5 sketch: field devices → control → supervision → site DMZ → enterprise
□ Asset list: PLC/RTU/HMI/engineering workstation/historian/jump host
□ Protocol and port baseline (authorized segments only)
```

### Phase 2: Passive and read-only

```text
□ SPAN/mirror PCAP → protocol-reverse / Wireshark industrial dissectors
□ Offline audit of configuration and project files (TIA/RSLogix exports and similar)
□ Record default passwords and plaintext protocols (unauthenticated Modbus) as Findings without writing or changing values
```

### Phase 3: Limited active work (authorized only)

```text
□ Low-rate identification, maintenance window
□ Read-only function codes first
□ Evidence for every step; stop immediately and report on anomalies
```

### Phase 4: Firmware/patch surface

```text
□ Controller firmware version → CVE mapping (do not flash firmware blindly)
□ Combine with firmware-pentest for offline image analysis
```

## Toolchain

| Tool | Purpose | Note |
|------|------|------|
| Wireshark industrial dissectors | Passive parsing | Mirrored traffic |
| Nmap NSE (limited) | Identification | Rate and time window |
| Claroty/Nozomi and similar | Asset discovery | Commercial/on site |
| PLC vendor engineering software | Configuration audit | Offline first |
| binwalk / Ghidra | Firmware | Offline |

## References

- `references/ot-safe-assessment.md`
- `../firmware-pentest/` `../protocol-reverse/` `../network` via pentest-tools

## Routing context

**Upstream**: MASTER R28  
**Downstream**: deep firmware work `firmware-pentest`; protocols `protocol-reverse`; IT lateral movement `windows-ad`/`attack-chain`  
**Sibling**: do not hit OT with regular web scan default parameters

## Task completion self-check

- [ ] Was it passive/read-only by default with the authorization boundary recorded?
- [ ] Did I avoid write operations on control loops (unless explicitly allowed)?
- [ ] Do the Findings include a physical/process impact statement?
- [ ] Checklist / journal?