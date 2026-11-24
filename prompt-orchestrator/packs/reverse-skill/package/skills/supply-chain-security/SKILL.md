---
name: supply-chain-security
description: Use for software supply-chain security assessment covering SBOM, SCA, CI/CD pipelines, container images, build integrity, dependency provenance, and vulnerability reachability.
---
# Supply Chain Security Testing

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

> SBOM / SCA / CI/CD pipelines / dependency provenance
> Regulation driven: US executive order SBOM, Chinese national standards, EU CRA

## When to use

- Software supply chain security assessment
- Open-source dependency vulnerability scanning and verification
- CI/CD pipeline security audit
- Container image security analysis
- Third-party component compliance review
- Build artifact provenance and integrity verification

## Six-layer supply chain governance framework

```text
Layer 1: source trust assessment → review of upstream repositories/maintainers/release history
Layer 2: build pipeline integration → CI/CD security gates, signature verification
Layer 3: artifact distribution integrity → signatures, checksums, attached SBOM
Layer 4: runtime protection → container scanning, admission control
Layer 5: continuous monitoring → real-time CVE tracking, vulnerability reachability analysis
Layer 6: incident response → supply chain attack response, rollback strategy
```

## Workflow

### 1. SBOM generation and audit

```text
Generate the SBOM:
□ CycloneDX format: cdxgen → bom.json
□ SPDX format: sbom-tool generate
□ Syft: syft <image|dir> -o spdx-json

Audit points:
□ Are there unknown/unauthorized dependencies
□ Are there deprecated/unmaintained packages
□ License conflict detection
□ Direct vs transitive dependency list
□ Release timeline and maintainer status of each component
```

### 2. Software composition analysis (SCA)

```bash
# OSV-Scanner (free, maintained by Google)
osv-scanner scan -r . --format json

# OWASP Dependency-Track (enterprise-grade continuous monitoring)
docker run -p 8080:8080 dependencytrack/apiserver
# → upload the SBOM → automatic matching against NVD/OSV/GitHub Advisory

# Snyk (commercial)
snyk test --all-projects
snyk monitor  # continuous monitoring

# Trivy (containers + dependencies + IaC)
trivy fs .          # filesystem scan
trivy image nginx   # container image
trivy config .      # IaC configuration
```

### 3. Vulnerability reachability verification

```text
SCA alert ≠ actual risk! For most SCA tools only ~15% of alerts are actually reachable.

Verification steps:
1. Get the CVE list with Dependency-Track or Trivy
2. Filter vulnerabilities with CVSS ≥ 7.0
3. Run reachability analysis on CVEs that have a PoC
   - Code Property Graph slicing: trace the path from user input to the vulnerable function
   - DEPTEX method: EPD (Execution Path Dominance) + LLM semantic verification
4. Verify the PoC in an isolated environment
5. Order fix priority for reachable vulnerabilities by actual impact
```

Tool references:
- CodeQL: GitHub code queries → data flow analysis
- Snyk Code: reachability marking
- DEPTEX: LLM-assisted context-aware risk assessment

### 4. CI/CD pipeline security

```text
Security checkpoints:
□ Code commit → pre-commit hook: gitleaks (secret scanning)
□ PR stage → SCA scan (Trivy/OSV-Scanner)
□ Build stage → artifact signing (cosign)
□ Push stage → attach SBOM (syft + attest)
□ Deploy stage → admission control (OPA/Kyverno + image scanning)
□ Runtime → continuous vulnerability monitoring (Dependency-Track)

Security of the pipeline itself:
□ Pipeline as Code audit (GitHub Actions / GitLab CI configuration injection)
□ Runner isolation (prevents malicious builds from breaking out of the container)
□ Secret management (Actions Secrets / Vault, hard-coding forbidden)
□ Third-party Action review (pin the commit SHA, not a tag)
```

### 5. Container image security

```bash
# Dockerfile audit
hadolint Dockerfile

# Image scanning (multiple layers: OS + application dependencies + configuration)
trivy image --severity HIGH,CRITICAL nginx:latest

# Minimal base image
# Prefer: distroless → alpine → slim → avoid latest
docker scout quickview nginx:latest

# Image signing
cosign sign --key cosign.key myimage:tag
cosign verify --key cosign.pub myimage:tag
```

### 6. Third-party dependency review

```text
New dependency checklist:
□ Maintenance status: commits in the last 6 months? Maintainer activity?
□ Security history: has malicious code ever been planted?
□ Dependency tree: how many transitive dependencies does it add?
□ License: compatible with the project license?
□ Alternatives: is there a safer alternative (Snyk Advisor / Socket.dev score)?

Risk assessment matrix:
  High maintenance × few dependencies × compatible license → low risk
  Low maintenance × many dependencies × license conflict → high risk
```

## Toolchain

| Tool | Purpose | Source |
|------|------|------|
| OWASP Dependency-Track | Enterprise-grade continuous SCA | `docker pull dependencytrack/apiserver` |
| OSV-Scanner | Free SCA (OSV.dev ecosystem) | `go install github.com/google/osv-scanner` |
| Trivy | Image + dependency + IaC scanning | `apt install trivy` |
| Syft | SBOM generation | `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh` |
| cdxgen | CycloneDX SBOM generation | `npm install -g @cyclonedx/cdxgen` |
| Cosign | Container signing | `go install github.com/sigstore/cosign/v2/cmd/cosign` |
| Gitleaks | Secret/credential scanning | `go install github.com/gitleaks/gitleaks/v8` |
| Snyk | Commercial SCA + reachability | `npm install -g snyk` |
| CodeQL | Code queries + data flow | Built into GitHub Actions |

## References

- `references/sbom-sca-methodology.md`: SBOM + SCA methodology
- `references/cicd-pipeline-security.md`: CI/CD pipeline security audit


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
