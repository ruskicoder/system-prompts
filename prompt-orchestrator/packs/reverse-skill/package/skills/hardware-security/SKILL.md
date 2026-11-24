---
name: hardware-security
description: Use for authorized hardware and embedded interface security research including UART/JTAG discovery, debug pad triage, secure boot overview, and offline firmware extraction support.
---

# Hardware / Embedded Interface Security

## ACTION REQUIRED (execute right after reading)

1. `NOW`: confirm **physical access authorization** and device ownership
2. `NOW`: ESD/power safety; read-only probing by default
3. `NEXT`: combine with firmware-pentest for image analysis
4. `ACT`: enclosure and debug interface identification → consoles → extraction

## When to use

- UART / JTAG / SWD debug port discovery
- Boot logs, root shell, boot interruption
- Flash extraction together with teardown
- Feasibility assessment of secure boot/encrypted flash (non-destructive first)

## Workflow

```text
□ Disassemble the authorized device; photograph and label test points
□ Find GND/VCC/TX/RX with a multimeter; logic levels 1.8/3.3/5V
□ USB-TTL read-only logs; record the baud rate
□ JTAG: enumerate IDCODE; assess whether it is locked
□ Extract the image → hand over to firmware-pentest / ghidra
```

## Toolchain

| Tool | Purpose |
|------|------|
| USB-TTL / logic analyzer | UART |
| J-Link / CMSIS-DAP | Debugging |
| bus pirate / flipper (lab) | Multi-protocol |
| binwalk / flashrom | Extraction |

## References

- `references/debug-interface-triage.md`
- `../firmware-pentest/` `../ot-ics/`

## Routing context

**Upstream**: MASTER R34  
**MUST NOT**: disassemble or damage other people's devices without authorization

## Task completion self-check

- [ ] Did I record interface levels and the pinout?
- [ ] Is the image preserved with a hash?
- [ ] Checklist?