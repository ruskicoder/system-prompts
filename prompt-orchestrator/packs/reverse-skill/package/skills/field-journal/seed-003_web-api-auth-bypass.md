# [seed] Web API Unauthorized Access + IDOR

## Scenario classification
Penetration testing

## Target overview
Black-box testing of a web application's REST API found unauthorized access and IDOR vulnerabilities.

## Complete execution chain

1. Information gathering: Nmap scan → port 443 runs Nginx + a back-end API
2. Directory discovery: FFUF brute force → found the `/api/v1/` path
3. API enumeration: visited `/api/v1/docs` → found exposed Swagger documentation
4. Authentication analysis: registered two test accounts A and B
5. IDOR test: used account A's token to access account B's resources → success (horizontal privilege escalation)
6. Unauthorized test: removed the Authorization header → some interfaces still returned data (unauthorized access)
7. Impact verification: confirmed that any user's personal information (name, email, phone number) can be read
8. Evidence collection: saved request/response screenshots and compiled a redacted report

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| FFUF blocked by the WAF | Request rate too high, triggering rate limiting | Lower the rate with `-rate 10`, add `-H "User-Agent: Mozilla/5.0..."` | 10min |
| Swagger docs 404 | The path is not the standard /swagger | Try `/api/v1/docs`, `/api-docs`, `/openapi.json` | 5min |
| Unsure whether the IDOR test succeeded | The returned data has no obvious user identifier | Compare the responses of the two accounts and find the user_id field difference | 15min |
| Report rejected by the SRC | Only screenshots were submitted, without complete reproduction steps | Added curl commands + complete requests/responses | 20min |

## Toolchain findings

- FFUF is faster than Gobuster but needs rate control to avoid bans
- Exposed Swagger/OpenAPI documentation is the fastest way to enumerate an API
- IDOR tests must use two of your own accounts against each other; do not touch other people's data
- SRC reports must have reproducible curl commands, not just screenshots

## Key code/commands

```bash
# directory discovery
ffuf -u https://target.example.com/api/v1/FUZZ -w /path/to/SecLists/Discovery/Web-Content/api/api-endpoints.txt -rate 10

# IDOR test
# use account A's token to access account B's resources
curl -H "Authorization: Bearer <token_A>" https://target.example.com/api/v1/users/USER_B_ID

# unauthorized test
curl https://target.example.com/api/v1/users/USER_B_ID
# if it returns 200 + data → unauthorized access
```

## Improvement suggestions for this package

- pentest-tools should add a dedicated "API penetration testing" checklist
- The src-hunter IDOR playbook works well but lacks guidance on "how to judge the impact scope of an IDOR"

## Reusable patterns/script snippets

**Three-step API unauthorized access test**:
```text
1. Normal request (with token) → record the normal response
2. Remove the token → check whether data is still returned (unauthorized)
3. Switch to another user's token → check whether access works (privilege escalation)
```

**Quick IDOR verification**:
```text
1. Register two accounts A and B
2. Get A's resource ID and B's resource ID
3. Request B's resource ID with A's token
4. If B's data comes back → IDOR confirmed
```

## Evolution actions
- [ ] No routing matrix update needed
- [ ] No bootstrap-manifest update needed
- [ ] No sub-skill documentation update needed

## Environment information
- OS: Windows (local machine) → target Linux server
- Tool versions: FFUF 2.x, curl, Burp Suite
- Target platform: Web API (REST, JSON)

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real target involved.

---
<!-- [Community contribution] Seed data, no PR needed -->
