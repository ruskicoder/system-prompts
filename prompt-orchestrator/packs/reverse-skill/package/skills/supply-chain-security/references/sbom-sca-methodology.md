# SBOM + SCA Methodology

## SBOM standard comparison

| Standard | Format | Ecosystem | Recommended scenario |
|------|------|------|---------|
| SPDX | JSON/YAML/tag-value | Linux Foundation, Yocto | License compliance first |
| CycloneDX | JSON/XML | OWASP, Kubernetes | Security analysis first |
| SWID | XML | ISO standard | Enterprise asset management |

## SBOM generation toolchain

```bash
# cdxgen: generate a CycloneDX SBOM from source
cdxgen -o bom.json -t cyclonedx

# Syft: generate from containers/filesystems
syft nginx:latest -o spdx-json > sbom.spdx.json

# SBOM-Tool: Microsoft toolchain
sbom-tool generate -b ./build -bc ./src -pn MyApp -pv 1.0
```

## SCA tool comparison

| Tool | Free | Speed | Database | Reachability |
|------|:--:|------|--------|:--:|
| OSV-Scanner | Yes | Very fast | OSV.dev | No |
| Trivy | Yes | Fast | Multiple sources | No |
| Dependency-Track | Yes | Medium | NVD+OSV+GitHub | No: (needs a plugin) |
| Snyk | No | Medium | Proprietary | Yes |
| CodeQL | Yes | Slow | Code level | Yes |

## Vulnerability priority strategy

```
CVSS ≥ 9.0 + public PoC + reachable → P0 fix immediately
CVSS ≥ 7.0 + PoC + reachable → P1 fix this week
CVSS ≥ 7.0 + no PoC or unreachable → P2 fix next iteration
The rest → regular process
```

## Three-step manual verification

```bash
# 1. Confirm the version (do not blindly trust SBOM fields)
# Inside the container: dpkg -l | grep <package>
# Node: cat node_modules/<pkg>/package.json | jq .version
# Python: pip show <package>

# 2. Confirm the vulnerability
# Search the CVE: https://osv.dev / https://nvd.nist.gov
# Check the affected version range
# Find the GitHub Advisory / oss-security mailing list

# 3. Verify the impact
# Search for public PoCs: GitHub/Exploit-DB
# Analyze exploitation conditions: authentication/local access/specific configuration needed?
# Verify in an isolated environment: docker run --rm -it vulnerable-image bash
```

## Continuous monitoring

```yaml
# Daily SBOM update + scan
schedule:
  - cron: "0 6 * * *"  # every day at 6 am
    steps:
      - cdxgen -o bom.json
      - osv-scanner scan --sbom bom.json
      - trivy fs --exit-code 1 --severity CRITICAL .
```

Source: OWASP CycloneDX, SPDX, Google OSV, CISA SBOM Guidance
