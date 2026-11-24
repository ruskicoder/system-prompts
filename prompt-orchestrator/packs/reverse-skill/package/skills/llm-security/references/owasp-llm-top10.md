# OWASP LLM & Agentic AI Top 10 (2025-2026)

## OWASP Top 10 for LLM Applications v2.0 (2025)

| # | Risk | Core problem | Test direction |
|---|------|---------|---------|
| LLM01 | Prompt Injection | Manipulate model behavior through crafted input | Direct injection, indirect injection, encoding bypass |
| LLM02 | Sensitive Information Disclosure | PII/API key/training data leaks | Prompt extraction, output analysis |
| LLM03 | Supply Chain | Poisoned models/libraries/datasets | Model provenance verification, dependency scanning |
| LLM04 | Data & Model Poisoning | Backdoors in training/fine-tuning data | Data provenance, behavior anomaly detection |
| LLM05 | Improper Output Handling | Output leads to XSS/SQLi/RCE | Downstream system injection testing |
| LLM06 | Excessive Agency | Too many tools/too much autonomy causes real harm | Permission audit, human-in-the-loop testing |
| LLM07 | System Prompt Leakage | Extract hidden instructions/keys/business logic | Cascaded extraction, canary token |
| LLM08 | Vector & Embedding Weaknesses | RAG pipeline attacks, embedding inversion | Retrieval poisoning, semantic similarity attacks |
| LLM09 | Misinformation | Hallucinations are a security risk in high-stakes scenarios | Factuality verification, confidence calibration |
| LLM10 | Unbounded Consumption | DoS/Denial-of-Wallet | Token consumption testing, rate limiting |

## OWASP Top 10 for Agentic Applications (ASI 2026)

| # | Risk | Core harm | Test direction |
|---|------|---------|---------|
| ASI01 | Agent Goal Hijack | Malicious input/tool output hijacks the goal | Instruction override, goal tampering |
| ASI02 | Tool Misuse & Exploitation | Unintended use of legitimate tools | Tool chain stitching, parameter injection |
| ASI03 | Identity & Privilege Abuse | Agent acts beyond its privileges | Credential theft, delegation chain testing |
| ASI04 | Agentic Supply Chain | Real-time risk from MCP descriptors/third-party tools | Dynamic supply chain scanning |
| ASI05 | Unexpected Code Execution | Prompt→tool→script RCE chain | Multi-layer code execution testing |
| ASI06 | Memory & Context Poisoning | Long-term memory/embedding poisoning | Memory persistence attacks |
| ASI07 | Insecure Inter-Agent Communication | Tampering with communication between agents | Man-in-the-middle, replay attacks |
| ASI08 | Cascading Failures | A single failure triggers system-wide collapse | Failure propagation testing |
| ASI09 | Human-Agent Trust Exploitation | Manipulate human operators into approving dangerous operations | Authority bias/urgency testing |
| ASI10 | Rogue Agents | Agent self-replication/persistent malicious behavior | Persistent backdoor detection |

## Actual data distribution

Share of problems found in real assessments:
- LLM01 Prompt Injection: ~45%
- LLM06 Sensitive Info Disclosure: ~20%
- LLM08 Excessive Agency: ~15%
- Remaining 7 items: ~20%

## Key defense principles

1. Separate planning and execution: the model that interprets intent ≠ the model that executes actions
2. Bind identity/purpose/scope/time limits: do not use broad ambient permissions
3. Log everything: tool calls/memory/communication as first-class security telemetry
4. Blast radius control: circuit breakers/rollback/emergency stop take priority over convenience
5. Treat all natural-language input (including retrieved content) as untrusted
6. Output is equally untrusted: sanitize before rendering/executing/querying
