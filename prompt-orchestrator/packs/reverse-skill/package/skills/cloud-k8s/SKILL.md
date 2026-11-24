---
name: cloud-k8s
description: Use for authorized cloud, container, and Kubernetes security assessment including metadata SSRF, IAM misconfig, container escape paths, and cluster RBAC review.
---

# Cloud / Container / Kubernetes Security

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md`; **cloud/K8s testing requires written authorization**
2. `NOW`: case-init + scope; state the account boundary clearly and forbid destructive operations
3. `NOW`: confirm that the task concerns cloud metadata/containers/K8s/IAM, not a regular web scan (the latter goes to `pentest-tools/`)
4. `NEXT`: tool-index; kubectl/aws/gcloud and similar are mostly manual installs
5. `ACT`: start from "identity and exposure surface"; scanning the whole network by default is forbidden

## When to use

- Cloud metadata SSRF (169.254.169.254 / IMDS)
- Excessive IAM permissions, public storage buckets, wrong security groups
- Docker/containerd escape path assessment
- Kubernetes RBAC, Secrets, Admission, supply chain images
- Container image vulnerabilities (can link with `supply-chain-security/`)

## Workflow

### Phase 1: Identity and boundary

```text
□ Current identity: cloud AK/SK, K8s SA, node SSH?
□ Scope: single account / single cluster / single namespace
□ Network profile: authorized_target_only
```

### Phase 2: Cloud control plane

```bash
# Example (replace per vendor; MUST stay within the authorized account)
aws sts get-caller-identity
aws s3 ls
# Matching identity commands for Azure / GCP
```

```text
□ Public buckets / wrong ACLs
□ Metadata: IMDSv1 vs v2; SSRF chain
□ Assumable roles (PassRole) and lateral movement
```

### Phase 3: Containers

```text
□ privileged / hostPath / hostNetwork?
□ capabilities (SYS_ADMIN and similar)
□ Writable host paths → escape candidates
□ Image history and known CVEs → Trivy
```

### Phase 4: Kubernetes

```bash
kubectl auth can-i --list
kubectl get pods,secrets,svc -A
kubectl get clusterrolebindings
```

```text
□ SA token mounts and permissions
□ Missing protective admission webhooks
□ etcd / dashboard exposure
□ Whether network policies allow by default
```

## Toolchain

| Tool | Purpose | Bootstrap |
|------|------|------|
| kubectl | Cluster interaction | Manual |
| trivy | Images/IaC | bootstrap `trivy` if available |
| kube-bench / kubeaudit | CIS/configuration | Manual |
| pacu / scoutsuite | Cloud audit (authorized) | Manual |
| nuclei | Known cloud vulnerability templates | bootstrap nmap/nuclei ecosystem |

## References

- `references/k8s-cloud-checklist.md`
- CTF comparison: `../../CTF-Sandbox-Orchestrator/competition-agent-cloud/`
- `../supply-chain-security/` `../pentest-tools/`

## Routing context

**Upstream**: MASTER R23  
**Downstream**: node shell obtained → `attack-chain` / `windows-ad`; image vulnerabilities → supply-chain  
**MUST NOT**: scan other public cloud tenants without authorization

## Task completion self-check

- [ ] Did I stay within the authorized account/cluster?
- [ ] Do the findings include reproduction and impact?
- [ ] Did I avoid destructive operations?
- [ ] Report / journal?