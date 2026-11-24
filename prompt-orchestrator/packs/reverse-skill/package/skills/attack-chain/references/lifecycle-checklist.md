# Pentest/Attack Chain Lifecycle Checklist

> Integrates community pentest skill packages (such as the six phases of Orizon claude-code-pentest) with this package's `attack-chain` + `ops`.  
> Inspiration: public Claude pentest lifecycle skills (retrieved 2026-07); **commands and authorization follow this package's scope**.  
> Date: 2026-07-17

## Before use

- [ ] `case-init` complete, `auth.status=granted`
- [ ] `network_profile` ≠ unrestricted misused against production
- [ ] `lead` has assigned specialist_roles (`ops/role-map.md`)

## Phase gates

| Phase | Role | Skill in this package | Completion standard |
|------|------|------------|----------|
| 0 Scope | lead | ops/scope-contract | ready_for_act |
| 1 Recon | cie | pentest-tools | Asset list + timeline |
| 2 Enum/Vuln | cpe | pentest-tools / api-security | Draft candidate F-* |
| 3 Validate | cpe | pentest-tools | E-* + validated Finding |
| 4 Post-ex (if authorized) | cpe/lead | Second half of attack-chain | Stays within out_of_scope limits |
| 5 RE support | cre | ida/apk/js/… | Only when a client/binary needs it |
| 6 Report | doc | docs-generator | Evidence→Finding→Path |
| 7 Journal | lead | field-journal | Redacted |

## Differences from "fully automatic takeover from one domain" skills (distinctive features)

| Common in external automation packages | reverse-skill |
|------------------|---------------|
| Scans the domain wildly by default | Requires a scope asset list |
| Writes the report straight from weak evidence | Mandatory E/F/P chain |
| Single session without roles | role-map handoff |
| No tool index | tool-index + bootstrap |

## At least one timeline entry per phase

See `ops/timeline-workitem.md` for the format.
