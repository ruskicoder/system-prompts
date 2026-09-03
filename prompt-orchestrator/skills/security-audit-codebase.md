---
name: security-audit-codebase
description: Perform systematic codebase security audits covering regex secret scanning, dependency vulnerability audits (npm audit, pip-audit, cargo audit), injection vulnerability detection, and OWASP Top 10 mitigation.
argument-hint: "<target directory or focus area>"
---

# Skill: Codebase Security Audit (Security Audit Codebase)

## Purpose
Perform a systematic security audit of a codebase checking for exposed secrets, vulnerable dependencies, injection vulnerabilities, insecure configurations, and OWASP Top 10 issues.

## Installation & Usage Options

### Via LobeHub Market CLI
```bash
# Register agent if needed
npx -y @lobehub/market-cli register --name "Antigravity" --source antigravity

# Install to custom skills directory
npx -y @lobehub/market-cli skills install pjt222-agent-almanac-security-audit-codebase --dir skills

# Install globally
npx -y @lobehub/market-cli skills install pjt222-agent-almanac-security-audit-codebase --global
```

### Native Orchestrator Loading
```markdown
# IDE Native syntax
#[[file:skills/security-audit-codebase.md]]

# CLI reference
cat skills/security-audit-codebase.md
```

## When to Use
- Before publishing, deploying, or releasing a project
- Periodic security review of existing repositories
- After adding authentication, authorization, or third-party API integrations
- Before open-sourcing a previously private repository
- Preparing for security compliance audits (SOC 2, ISO 27001, OWASP ASVS)
- Validating dependencies after CVE disclosures

## Inputs
- **Required**: Codebase repository to audit
- **Optional**: Specific focus area (`secrets`, `dependencies`, `injection`, `auth`, `crypto`, `configuration`)
- **Optional**: Compliance framework (`OWASP Top 10`, `SOC 2`, `ISO 27001`)
- **Optional**: Previous audit findings for regression comparison

## Tools & Prerequisites
- Secret scanners (`gitleaks`, `trufflehog`, or regex search via `grep_search`)
- SAST / Linter tools (`semgrep`, `bandit`, `eslint-plugin-security`)
- Dependency audit package managers (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`)
- Git history inspection tools (`git log`, `git ls-files`)

## Step-by-Step Procedure

### Step 1: Scan for Exposed Secrets & Keys
Search the codebase for tokens, private keys, passwords, and connection strings:

```bash
# API keys and provider tokens
grep -rn "sk-\|ghp_\|gho_\|github_pat_\|hf_\|AKIA\|AIza" --include="*.{md,js,ts,py,json,yml,yaml,env}" .

# Generic credential assignments
grep -rn "password\s*=\s*['\"][^'\"]\+['\"]" --include="*.{js,ts,py,json}" .
grep -rn "api[_-]key\s*[=:]\s*['\"][^'\"]\+['\"]" --include="*.{js,ts,py,json}" .
grep -rn "secret\s*[=:]\s*['\"][^'\"]\+['\"]" --include="*.{js,ts,py,json}" .

# Database connection strings with credentials
grep -rn "postgres://\|postgresql://\|mysql://\|mongodb://\|redis://" .

# Private keys and certificates
grep -rn "BEGIN.*PRIVATE KEY" .
```

**Expected:** No active credentials in code — only environment variable references (`process.env.API_KEY`, `os.environ.get(...)`) or documented placeholder tokens (`YOUR_API_KEY_HERE`).
**On Failure:** Immediately revoke/rotate the compromised secret, untrack the file, and sanitize git history using `git-filter-repo`.

### Step 2: Verify `.gitignore` & Version Control Hygiene
Ensure sensitive local files and credentials cannot be committed:

```bash
# Verify sensitive files are ignored
git check-ignore .env .env.local *.pem *.key credentials.json

# Check for accidentally tracked secret files
git ls-files | grep -i "\.env\|\.pem\|\.key\|credentials\.json\|secrets\."
```

**Remediation:** If sensitive files are tracked, run `git rm --cached <file>`, ensure it is listed in `.gitignore`, and commit the exclusion.

### Step 3: Dependency Vulnerability Audit
Scan third-party libraries for known CVEs:

```bash
# Node.js / TypeScript
npm audit --audit-level=moderate
npx audit-ci --moderate

# Python
pip-audit
safety check

# Rust
cargo audit

# Go
govulncheck ./...
```

**Remediation:** Apply automated patches via `npm audit fix` / `pip install --upgrade <pkg>` or pin patched dependency versions in package manifests.

### Step 4: Check for Injection Vulnerabilities
1. **SQL Injection**: Ensure all queries use parameterized inputs or ORM prepared statements:
   ```bash
   # Look for string interpolation in database queries
   grep -rn "SELECT.*FROM.*+\|SELECT.*FROM.*%s\|f\"SELECT.*FROM" --include="*.{js,ts,py}" .
   ```
2. **Command Injection**: Check for unsanitized shell invocations (`exec`, `eval`, `child_process.exec`, `subprocess.Popen(..., shell=True)`).
3. **Cross-Site Scripting (XSS)**: Check for raw HTML injection (`dangerouslySetInnerHTML`, `innerHTML`, `v-html`).
4. **Path Traversal**: Validate file path operations against directory boundaries (`..`, `path.resolve` checks).

### Step 5: Authentication & Access Control
- [ ] **BOLA / IDOR**: Are user IDs checked against the authenticated session on every resource access?
- [ ] **JWT Verification**: Is signature validation enforced? Are algorithms locked (`HS256`/`RS256`, refusing `none`)?
- [ ] **Password Storage**: Are passwords hashed using modern, salted key-derivation functions (`Argon2id`, `bcrypt`, `scrypt`)?
- [ ] **Session Security**: Do session cookies enforce `HttpOnly`, `Secure`, and `SameSite=Strict` / `Lax`?

### Step 6: Security Configuration & Cryptography
- [ ] **CORS Policy**: Avoid `Access-Control-Allow-Origin: *` in conjunction with `Allow-Credentials: true`.
- [ ] **Security Headers**: Ensure `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, and `Strict-Transport-Security` are configured.
- [ ] **Strong Cryptography**: Refuse deprecated hash/cipher algorithms (`MD5`, `SHA1`, `DES`, `RC4`).

### Step 7: Security Audit Report & Remediation Plan
Group findings by severity and provide precise remediation steps:

| Severity | Definition | Action Required |
|----------|------------|-----------------|
| 🔴 **Critical** | Remote code execution, unauthenticated data breach, exposed active secret | Immediate hotfix & key rotation |
| 🟠 **High** | SQL injection with auth required, BOLA/IDOR, high CVE in dependency | Fix prior to next release |
| 🟡 **Medium** | Missing CSRF protection, loose CORS headers, medium CVE | Remediate in current sprint |
| 🟢 **Low** | Missing security headers, verbose error messages, informational | Track in maintenance backlog |
