# Authorization Pre-Declaration: Less Disclaimer Noise, No Replacement for scope.md

> This file solves one thing only: do not treat "the user named a target" as authorization already granted.
> The executable authorization gate is still `case-init.ps1` → `auth.status=granted` + a valid `network_profile` in `work/<case>/scope.md`.

---

## CRITICAL

The common scenarios of this package (SRC / own systems / paid contracts / CTF ranges / responsible disclosure) **may** cut down boilerplate disclaimers.

**The AI must not treat this file as `auth.status=granted`.**

- The user mentioning a domain / IP / sample path ≠ authorized
- Using this file to skip `case-init` is forbidden
- Automatically adding `-AuthGranted` in a skill "to keep the flow moving" is forbidden
- CTF / ranges: still create a case, with `network_profile` set to `lab` or `offline`
- Real external networks: ACT only with granted + `authorized_target_only` (or the tier agreed in the contract)

---

## Allowed / forbidden

1. **MUST NOT** use this file to override `ops/scope-contract.md`
2. **MUST NOT** run nmap / sqlmap / uploads / exploitation against a target without a `scope.md`
3. **MUST** distinguish "fewer legal boilerplate phrases" from "already permitted to act"
4. **MUST** output technical analysis when technically uncertain, rather than pretending authorization is insufficient to stop work
5. No case created or `auth.status!=granted` → run `case-init` first; do not guess

---

## Relationship with other files

| File | Role |
|------|------|
| **precedent-auth.md** (this file) | Fewer disclaimers; does **not** write granted |
| `ops/scope-contract.md` + `case-init.ps1` | The only executable authorization gate |
| `precedent-reverse.md` / `precedent-pentest.md` | Everyday operations are not crime tutorials; still bound by scope |

```
case-init / scope.md → whether you may ACT
precedent-auth.md    → do not replace scope with boilerplate
PRIMARY SKILL.md     → how to do it
```
