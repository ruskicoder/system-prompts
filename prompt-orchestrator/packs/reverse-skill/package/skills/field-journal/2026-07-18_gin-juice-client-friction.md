# Modern Web Range Friction → Skill Hardening

> Date: 2026-07-18  
> Scenario: legitimate public ranges (PortSwigger-style scanner-eval / OWASP Juice Shop demo)  
> Redaction: no exploitation details for real business domains

## Conclusion (for the next agent)

**No breakthrough ≠ the package is ineffective.** You must deliver: a surface map, a sink list, the gate reasons, Evidence (observed|validated).  
Write failures into the timeline and feed them back into the playbook.

## Pitfalls

| Pitfall | Symptom | Fix/discipline |
|----|------|-----------|
| case-init authorization polluted | After `-AuthGranted` the status became an odd string | Allow only pending/granted/denied/unknown; decide AuthStatus with `PSBoundParameters` |
| lab_only not ready | ready_for_act false with network=lab_only | lab_only + granted + assets → ready |
| Windows curl `[]` | `bad range in position` | **Must** use `curl.exe --globoff` |
| append-evidence special characters | RawExcerpt with quotes/XML errors out | Block indentation + strip control characters |
| Public demo 503 | Juice Shop on Heroku down | Switch to local Docker or another legitimate target; do not grind on it |
| DOM XSS false positive | Reported validated just because an innerHTML sink exists | Exploitable only with a 200 non-numeric body; otherwise observed |
| agent-browser ref stale | click fails | Take a new snapshot after page changes |

## Reusable patterns

1. Surface → Sink → Chain (see `pentest-tools/references/client-side-lab-playbook.md`)  
2. Inventory-style `innerHTML = fetchBody`: prove the sink first, then look for a 200 non-numeric body  
3. Double proof with a static rg sink search + agent-browser eval  

## Toolchain

- case-init / case-guard / append-evidence / smoke  
- agent-browser (CDP)  
- curl --globoff  

## Environment

- Windows + PowerShell 5.1  
- The Docker Desktop daemon may not be ready  
