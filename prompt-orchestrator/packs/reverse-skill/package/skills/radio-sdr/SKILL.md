---
name: radio-sdr
description: Use for authorized RF/SDR security research including signal identification, replay feasibility study in shielded labs, and wireless protocol analysis outside classic Wi-Fi.
---

# RF / SDR Security Research

## ACTION REQUIRED (execute right after reading)

1. `NOW`: **spectrum use and transmission are strictly regulated by law**; only authorized bands/shielded rooms/lab targets
2. `NOW`: scope states the devices, bands, and whether transmission is allowed (receive only by default)
3. `ACT`: receive-only identification → demodulation analysis → lab reproduction assessment

## When to use

- Non-Wi-Fi RF such as wireless remotes/sensors (authorized)
- Protocol research on ADS-B/remote controls and similar (legal reception)
- Division of work with wifi-wireless: this skill focuses on **general SDR RF**; Wi-Fi attack and defense goes to R29

## Workflow

```text
□ Confirm regulations and licenses
□ Receive only: identify the center frequency and modulation
□ GNU Radio / URH analysis
□ Replay only in a shielded room with written permission
□ Conclusions focus on: whether unauthorized control is possible / hardening advice
```

## Toolchain

| Tool | Purpose |
|------|------|
| RTL-SDR / HackRF (compliant) | Transmit/receive hardware |
| URH / GNU Radio | Analysis |
| Inspectrum | Signals |

## References

- `references/sdr-lab-rules.md`
- `../wifi-wireless/` `../ot-ics/` `../hardware-security/`

## Routing context

**Upstream**: MASTER R38  
**MUST NOT**: interfere with public communications, transmit without authorization

## Task completion self-check

- [ ] Was it receive-only by default with the regulatory boundary recorded?
- [ ] Checklist?