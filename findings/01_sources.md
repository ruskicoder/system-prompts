# Sources Log — Anti-Hallucination & Grounded AI Architecture

## Primary & Technical Sources

### 1. Google Cloud Vertex AI & Google Research Grounding Guidance (2025/2026)
- **URL**: https://cloud.google.com/vertex-ai/docs/generative-ai/grounding/overview
- **Authority**: Google Cloud AI & Research Team
- **Key Principles**:
  - Grounding anchors LLM responses in verifiable external knowledge sources (search APIs, enterprise context).
  - Mandatory citation format mapping output claims directly to source attribution tags.
  - Strict fallback to "insufficient source data" refusal when retrieved context lacks necessary facts.
- **Date**: 2025/2026

### 2. OpenAI Retrieval Augmented Generation & Grounding Prompt Engineering (2025/2026)
- **URL**: https://platform.openai.com/docs/guides/prompt-engineering
- **Authority**: OpenAI Applied AI Research
- **Key Principles**:
  - "Rule of Refusal": Explicit instruction forcing model to state ignorance when sources are insufficient.
  - "Citation Contract": Mandates explicit source notation for all factual assertions.
  - Grounding pipeline: Search & retrieve first -> verify evidence -> synthesize output with citations.
- **Date**: 2025/2026

### 3. OWASP Top 10 for LLM Applications — LLM09: Overreliance & Hallucination Prevention
- **URL**: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- **Authority**: OWASP International Security Standard Body
- **Key Principles**:
  - Overreliance on model hallucination leads to systemic operational failures.
  - Mandatory verification layer: All technical claims and code recommendations must be backed by primary evidence (log files, direct code reads, or web search retrieval).
- **Date**: 2025/2026

### 4. Self-Corrective Retrieval & Multi-Agent Debate Patterns (Self-RAG / CoVe)
- **URL**: https://arxiv.org/abs/2310.11511 (Self-RAG: Learning to Retrieve, Generate, and Critique)
- **Authority**: AI Research Community (ArXiv / Meta AI / UW)
- **Key Principles**:
  - Two-pass verification: Search/retrieve -> generate claim -> self-critique claim against evidence.
  - Prohibits false certainty; mandates explicit confidence ratings based on evidence coverage.
- **Date**: 2024/2025
