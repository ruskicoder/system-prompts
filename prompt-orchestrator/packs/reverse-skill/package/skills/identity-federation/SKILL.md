---
name: identity-federation
description: Use for authorized assessment of federated identity systems including SAML, OIDC, OAuth2 flows, SSO misconfiguration, and token confusion issues.
---

# Identity Federation (SAML / OIDC / OAuth)

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read precedent-pentest; put the SSO test accounts and the IdP/SP scope into scope
2. `NOW`: brute-force attempts that lock real user accounts are forbidden
3. `NEXT`: capture tools and documentation (metadata URLs)
4. `ACT`: protocol flow mapping → common misconfigurations → verification

## When to use

- SAML Response signature/assertion tampering surface (classic flaw patterns)
- OIDC implicit/authorization code + missing PKCE
- redirect_uri / state / nonce problems
- IdP and SP metadata, multi-tenant issuer confusion
- Complements the `api-security` JWT attacks (this skill focuses on federation and SSO flows)

## Workflow

```text
□ Draw it clearly: User → SP → IdP → Token → SP
□ Collect: /.well-known/openid-configuration, SAML metadata
□ Check: exact redirect_uri match, state binding, PKCE
□ Check: SAML signature coverage, algorithm downgrade
□ Session fixation and logout invalidation
```

## Toolchain

| Tool | Purpose |
|------|------|
| Burp + SAML Raider and similar | Assertion editing (authorized) |
| jwt_tool | JWT part |
| Browser DevTools | Redirect chain |
| IdP admin logs | Audit |

## References

- `references/sso-flow-checklist.md`
- `../api-security/` `../windows-ad/` (enterprise IdP)

## Routing context

**Upstream**: MASTER R37  
**Downstream**: pure API JWT → api-security; cloud IdP → cloud-k8s

## Task completion self-check

- [ ] Did I map the complete SSO flow?
- [ ] Does every Finding have reproduction and impact?
- [ ] Checklist?