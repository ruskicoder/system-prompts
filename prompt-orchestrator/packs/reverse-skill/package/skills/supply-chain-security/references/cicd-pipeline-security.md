# CI/CD Pipeline Security Audit

## Pipeline attack surface

```text
Threat model (STRIDE):
□ Spoofing: forged builds/signatures/provenance
□ Tampering: modified source code/build artifacts/dependencies
□ Repudiation: malicious operations without audit logs
□ Information disclosure: pipeline logs/build artifacts leak secrets
□ Denial of service: exhausted CI resources/broken builds
□ Elevation of privilege: runner escape/secret theft
```

## Audit checklist

### 1. Pipeline as Code configuration

```yaml
# GitHub Actions audit points
# ❌ Dangerous pattern
on:
  pull_request_target:  # PR trigger with access to secrets
    types: [opened]

# ❌ Script injection
- run: echo "${{ github.event.issue.title }}"  # user input → shell

# ❌ Unrestricted token permissions
permissions: write-all

# ✅ Safe pattern
on:
  pull_request:  # no access to secrets
    types: [opened]

# ✅ Pin to a SHA
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

# ✅ Least privilege
permissions:
  contents: read
```

### 2. Secret management

```bash
# Scan historical commits for secrets
gitleaks detect --source . --verbose
trufflehog git file://. --only-verified

# Check Actions Secrets usage
gh secret list
# Confirm: no hard-coded secrets, regular rotation, least privilege

# Runtime secret injection
# ✅ Use OIDC instead of long-lived secrets
# ✅ Secrets exposed only to specific steps when needed
```

### 3. Build integrity

```bash
# Build provenance
# Generate tamper-proof build records (SLSA L2+)
slsa-provenance generate --source . --output provenance.json

# Artifact signing
cosign sign-blob --key cosign.key artifact.tar.gz

# Verify
cosign verify-blob --key cosign.pub --signature artifact.tar.gz.sig artifact.tar.gz
```

### 4. Runner security

```text
□ Are GitHub-hosted runners used? (recommended, a fresh environment each time)
□ Self-hosted runner: does it run in an isolated VM/container?
□ Has it run fork PRs? (very high risk for self-hosted runners)
□ Does the runner have outbound network restrictions?
□ Could the build cache leak across builds?
```

### 5. Dependency fetch security

```text
□ npm: is package-lock.json committed? --force / --legacy-peer-deps are forbidden
□ pip: does requirements.txt pin versions? pip install <unverified source> is forbidden
□ Docker: is FROM pinned to a digest? The latest tag is forbidden
□ Go: is go.sum committed?
□ Private packages: does registry authentication use short-lived tokens?
```

## Automated check pipeline

```yaml
# .github/workflows/supply-chain.yml
name: Supply Chain Security
on: [push, pull_request]

jobs:
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: SBOM Generate
        run: |
          npm install -g @cyclonedx/cdxgen
          cdxgen -o sbom.json
      
      - name: OSV Scan
        run: |
          go install github.com/google/osv-scanner/cmd/osv-scanner@latest
          osv-scanner scan --sbom sbom.json --format sarif > osv-results.sarif
      
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: CRITICAL,HIGH
          exit-code: 1
      
      - name: Secret Scan
        run: |
          docker run --rm -v $PWD:/src ghcr.io/gitleaks/gitleaks:latest \
            detect --source /src --verbose
      
      - name: Dependency-Track Upload
        run: |
          curl -X POST https://dtrack.example.com/api/v1/bom \
            -H "X-Api-Key: ${{ secrets.DTRACK_API_KEY }}" \
            -F "autoCreate=true" -F "project=myapp" -F "bom=@sbom.json"
```

Source: SLSA Framework, OWASP CI/CD Top 10, GitHub Security Lab
