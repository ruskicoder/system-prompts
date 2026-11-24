# Code Audit Checklist (condensed)

- [ ] List of every external input entry
- [ ] Authentication/authentication middleware coverage
- [ ] Are multi-tenant IDs bound to the session
- [ ] Deserialization / pickle / YAML load
- [ ] SSRF egress and protocol restrictions
- [ ] Key and token storage
- [ ] File upload paths and types
- [ ] Dangerous exec/system/Runtime