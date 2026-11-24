# Cloud / K8s Checklist (condensed)

## IMDS
- [ ] Can SSRF reach 169.254.169.254
- [ ] Is IMDSv2 enforced
- [ ] Permission surface of the returned IAM role

## K8s high risk
- [ ] Too many cluster-admin bindings
- [ ] Secrets in plaintext environment variables
- [ ] privileged + hostPID/hostPath combination
- [ ] Anonymous auth / insecure apiserver port

## Containers
- [ ] Running as root
- [ ] Kernel modules loadable / docker.sock mounted