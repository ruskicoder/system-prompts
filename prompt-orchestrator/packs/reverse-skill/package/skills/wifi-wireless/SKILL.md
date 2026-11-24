---
name: wifi-wireless
description: Use for authorized wireless security assessment including Wi-Fi capture, WPA handshake analysis, rogue AP detection research, and lab-only deauth testing.
---

# Wi-Fi / Wireless Security

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read precedent-pentest; **wireless attacks carry high legal risk** and need written authorization and a physical scope
2. `NOW`: scope states the target SSID/BSSID/site; scanning neighboring networks is forbidden
3. `NEXT`: confirm that the adapter supports monitor mode
4. `ACT`: reconnaissance → collection → analysis (lab first)

## When to use

- Authorized Wi-Fi security assessment
- WPA/WPA2 handshake capture and offline assessment
- Rogue AP / phishing hotspot detection research
- Enterprise wireless isolation and portal security

## Workflow

```text
□ iwconfig / airmon-ng into monitor mode (legal environment)
□ airodump-ng locks onto the target BSSID channel
□ Handshake or PMKID capture (target only)
□ hashcat/aircrack offline assessment of the password policy
□ Report: encryption type, isolation, portal bypass, recommendations
```

## Toolchain

| Tool | Purpose |
|------|------|
| aircrack-ng suite | Capture/assessment |
| hcxdumptool / hcxtools | PMKID |
| hashcat | Password assessment |
| Wireshark | Management frame analysis |

## References

- `references/wireless-lab-rules.md`
- `../pentest-tools/` `../attack-chain/` (close-access section)

## Routing context

**Upstream**: MASTER R29  
**MUST NOT**: unauthorized deauth, operating on non-target client networks

## Task completion self-check

- [ ] Did I lock strictly onto the target BSSID?
- [ ] Did the report give hardening recommendations?
- [ ] Checklist?