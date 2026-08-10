# Workflow: Heartbeat Monitoring & System Health

## When to Use
| Criteria | Match |
|----------|-------|
| Intention | continuous monitoring, periodic health check, digest generation |
| Complexity | system-wide, background execution |
| Power Mode | Eco (if no state changes) or Balanced |

## Required Skills
- codebase-understanding
- file-operations
- code-quality-testing
- safety-profiles

## 5-Step Heartbeat Execution Flow

### Step 1: Health Check
- Verify gateway, database, and background processes are active.
- Detect recent execution failures or command loops.

### Step 2: Task Integrity Check
- Identify tasks stuck in `RUNNING` or `BLOCKED` states.
- Detect repeated retry loops and stop automated retries if failing repeatedly.

### Step 3: Artifact & Directory Review
- Check that required system digests and logs exist.
- Verify workspace file permissions and state file integrity.

### Step 4: Security & Risk Scan
- Detect unauthenticated public bindings or secret exposure.
- Review pending skill audit approvals.

### Step 5: Digest Generation
- Produce daily system health digest at `_audit/digests/YYYY-MM-DD_digest.md`.
- Skip digest generation if state is unchanged since last run (respond `HEARTBEAT_OK`).

## Token Efficiency Rules
- Skip reprocessing if no state changes occurred (`HEARTBEAT_OK`).
- Batch checks (email, calendar, health, alerts) into a single heartbeat turn.
- Escalate to developer when security risks or persistent failures (>48h) occur.
