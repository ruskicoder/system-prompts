---
name: api-integration
description: Integrate with external APIs, REST, GraphQL, web services, SDKs, and
  third-party tools. Use when connecting external services, managing API keys securely,
  handling authentication (OAuth, JWT, API keys), implementing network retry logic,
  or configuring HTTP client libraries.
argument-hint: <API name, endpoint, or service>
---

<!-- Generated from skills/api-integration.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: API Integration & External Services

## Purpose
Integrate with external APIs, web services, libraries, and third-party tools.

## Tools Required
- HTTP/fetch tools
- Package management commands
- API key configuration tools

## General Principles
- Use best-suited external APIs and packages without asking permission; report each choice with the reason
- Match API/package versions to existing dependency management files
- Never hardcode API keys: use environment variables
- Point out when an external API requires a key

## API Selection
- Check if the project already uses a similar API/library: reuse it
- Choose versions compatible with existing dependency manifests
- Prefer well-established, maintained libraries
- For new projects: use latest stable version

```python
# API version selection priority:
1. Already present in dependency management file → use that version
2. Compatible with existing major version range → use latest in that range
3. No existing deps → use latest stable
```

## API Key & Secret Handling
- NEVER hardcode secrets in source code
- NEVER commit .env files with real secrets
- Use environment variables: `process.env.API_KEY`
- Point out required keys to user: "You'll need to set OPENAI_API_KEY in your .env"
- For local dev, suggest .env files (and ensure they're in .gitignore)

## REST API Integration
- Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Handle response status codes properly
- Implement error handling for network failures
- Add request/response logging for debugging
- Set reasonable timeouts (default: 30s)

## GraphQL API Integration
- Use query batching for multiple requests
- Handle partial error responses
- Implement pagination for list queries

## Authentication Patterns
- API Key (header-based): `Authorization: Bearer <key>`
- OAuth 2.0: redirect → code → token flow
- Basic Auth: `Authorization: Basic <base64>`
- JWT: decode for debugging, verify expiry

## Tool/CLI Integration
- For local tools: check if installed before using, provide install instructions if not
- For npm packages: check package.json before suggesting
- Prefer npx/pnpx for one-off tool runs

## Example Patterns

### Node.js/Express API call
```javascript
const response = await fetch("https://api.example.com/v1/data", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${process.env.API_KEY}`
  },
  body: JSON.stringify({ query: "data" })
});
if (!response.ok) {
  throw new Error(`API error: ${response.status} ${response.statusText}`);
}
const data = await response.json();
```

### Python API call
```python
import requests

response = requests.post(
    "https://api.example.com/v1/data",
    headers={"Authorization": f"Bearer {os.environ['API_KEY']}"},
    json={"query": "data"},
    timeout=30
)
response.raise_for_status()
data = response.json()
```

## Error Recovery
- Network errors: retry with exponential backoff (max 3 retries)
- Rate limiting: respect Retry-After headers
- Auth errors: check credentials, don't retry blindly
- Server errors (5xx): retry, may be transient
- Client errors (4xx): don't retry, fix the request

## Domain-Specific Knowledge
When integrating with specific platforms, learn their domain model:
- **Notion**: workspaces, pages, databases, properties, views, data sources
- **GitHub**: repos, issues, PRs, commits, actions, releases
- **Slack**: channels, messages, threads, users, workspace
- **Linear**: teams, issues, cycles, projects, workflows

Check the platform's documentation for exact API schemas.
