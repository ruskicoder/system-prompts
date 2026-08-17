# Skill: Software Architecture Review (Review Software Architecture)

## Purpose
Review software architecture at the system level for coupling, cohesion, SOLID principles, API & data model design, scalability, operational reliability, and technical debt.

## Installation & Usage Options

### Via LobeHub Market CLI
```bash
# Register agent if needed
npx -y @lobehub/market-cli register --name "Antigravity" --source antigravity

# Install to custom skills directory
npx -y @lobehub/market-cli skills install pjt222-agent-almanac-review-software-architecture --dir skills

# Install for specific agent platform
npx -y @lobehub/market-cli skills install pjt222-agent-almanac-review-software-architecture --agent codex
```

### Native Orchestrator Loading
```markdown
# IDE Native syntax
#[[file:skills/review-software-architecture.md]]

# CLI reference
cat skills/review-software-architecture.md
```

## When to Use
- Evaluating a proposed architecture before implementation begins
- Assessing an existing system for scalability, maintainability, or security
- Reviewing Architecture Decision Records (ADRs) and design RFCs
- Performing a technical debt and code churn audit
- Evaluating readiness for significant scale-up or multi-tenant expansion
- Differentiating system-level architectural analysis from line-by-line PR reviews

## Inputs
- **Required**: System codebase or architecture documentation (diagrams, ADRs, README, contracts)
- **Required**: Context about system purpose, scale, and operating constraints
- **Optional**: Non-functional requirements (SLAs, latency, throughput, availability targets)
- **Optional**: Team size, skill composition, and deployment topology
- **Optional**: Known pain points or critical hotspots

## Tools & Prerequisites
- Codebase exploration tools (`grep_search`, `list_dir`, `view_file`)
- Dependency graph / circularity analyzers (e.g. `madge`, `pydeps`, `cargo-depgraph`)
- Git history churn analysis commands (`git log --format=format: --name-only | sort | uniq -c | sort -nr`)

## Step-by-Step Procedure

### Step 1: Map System Boundaries & Context
1. Map external dependencies, databases, caches, and communication protocols:
   ```markdown
   | Dependency | Type | Criticality | Operational Notes |
   |------------|------|-------------|-------------------|
   | PostgreSQL | RDBMS | Critical | Primary transactional state |
   | Redis | Cache / Queue | High | Session caching & rate limiting |
   | Kafka / RabbitMQ | Event Bus | Critical | Asynchronous event distribution |
   | Stripe / Auth0 | External API | High | Third-party vendor integration |
   ```
2. Identify architectural patterns in use (e.g., Clean/Hexagonal Architecture, Modular Monolith, Microservices, Event-Driven).

### Step 2: Structural Quality (Coupling & Cohesion)

#### Coupling Assessment
Evaluate inter-module dependencies and direction of flow:
- [ ] **Directionality**: Do dependencies flow inward toward domain models without circular references?
- [ ] **Contract Boundaries**: Do modules communicate through explicit interfaces/DTOs or directly touch internal tables/state?
- [ ] **Shared State**: Is mutable global state shared between separate components?
- [ ] **Database Coupling**: Do multiple services perform direct writes to the same database tables?

```bash
# Circular dependency detection (JavaScript / TypeScript)
npx madge --circular src/

# Python cross-package dependency check
grep -rn "^from app\." --include="*.py" | sort | uniq -c | sort -rn | head -20
```

#### Cohesion Assessment
Evaluate whether each component has a clear, focused responsibility:
- [ ] **Single Responsibility**: Does each module/class address only one domain concern?
- [ ] **File / Class Size**: Are there monolithic classes (>500 lines) accumulating multiple distinct workflows?
- [ ] **God Objects**: Is there a central orchestrator or manager that every other component depends upon?

| Coupling Level | Description | Status / Action |
|---|---|---|
| **Low (Optimal)** | Modules communicate via abstract contracts / interfaces | ✅ Target state |
| **Medium** | Modules share static data models / DTO libraries | ⚠️ Acceptable for shared types |
| **High (Concern)** | Modules directly query each other's internal persistence | ❌ Requires interface encapsulation |
| **Pathological** | Modules mutate each other's in-memory state or circular calls | 🚫 Critical refactoring needed |

### Step 3: SOLID & Design Principle Adherence
- **Single Responsibility (SRP)**: Each class/service has one reason to change.
- **Open/Closed (OCP)**: New features can be plugged in via extensions/strategies without altering base code.
- **Liskov Substitution (LSP)**: Derived implementations fulfill base contracts without breaking consumers.
- **Interface Segregation (ISP)**: Clients are not forced to depend on methods they do not use.
- **Dependency Inversion (DIP)**: High-level business logic depends on abstractions, not concrete database/network drivers.

### Step 4: API & Data Model Design Review
1. **Contract Consistency**: Predictable HTTP status codes, error payload schemas, and serialization formats.
2. **Idempotency & Safety**: Mutation operations implement idempotency keys or transactional boundaries.
3. **Pagination & Query Efficiency**: Large datasets enforce cursor or keyset pagination; prevent full table scans.
4. **Data Normalization vs Denormalization**: Ensure transactional models maintain referential integrity while read models are optimized for querying.

### Step 5: Scalability & Operational Reliability
1. **Stateless Compute**: Ensure backend application instances hold no in-memory state that blocks horizontal scaling.
2. **Resilience & Fault Isolation**: Circuit breakers, retry policies with exponential backoff, and dead-letter queues.
3. **Observability**: Structured JSON logging with trace IDs across service boundaries; health checks (`/healthz`, `/livez`).

### Step 6: Prioritized Architecture Decision & Debt Report
Synthesize findings into an actionable report:
1. **Executive Summary**: Architecture health assessment and top risks.
2. **Hotspots & Risk Matrix**: Impact (High/Medium/Low) vs Effort (High/Medium/Low).
3. **Refactoring & Migration Roadmap**: Phased remediation steps with rollback strategies.
