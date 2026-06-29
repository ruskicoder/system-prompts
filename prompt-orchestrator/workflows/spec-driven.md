# Workflow: Spec-Driven Development

## When to Use
| Criteria | Match |
|----------|-------|
| Intention | complex_feature, large_refactor, new_architecture |
| Complexity | multi-file, multi-session, cross-cutting, high risk |
| Power Mode | Deep or Critical |
| Clarity | requirements are vague or need stakeholder alignment |

## Required Skills
- file-operations
- code-execution
- code-quality-testing
- communication-tone
- project-scaffolding
- codebase-understanding (GitNexus)
- safety-profiles (appropriate level)
- memory-management

## Flow

### Phase 0: Thinking Stage (Pre-Action)
- [ ] Do I understand the feature vision? What problem are we solving?
- [ ] Have I researched existing functionality? (GitNexus query, context, impact)
- [ ] What's the scope boundary? What's explicitly IN and OUT?
- [ ] Is the user's intent clear enough to write requirements, or do I need more discussion?

### Phase 1: Requirements
Output: `.kiro/specs/{feature_name}/requirements.md`

1. Understand the feature from user's rough idea
2. Write user stories: "As a [role], I want [feature], so that [benefit]"
3. Write acceptance criteria in EARS format:
   - **WHEN** [event] **THEN** [system] **SHALL** [response]
   - **IF** [precondition] **THEN** [system] **SHALL** [response]
   - **WHILE** [state] **THEN** [system] **SHALL** [response]
4. Be specific, measurable, and testable
5. Include error handling and edge cases
6. Reference current codebase state via GitNexus:
   ```
   query({search_query: "existing related functionality"})
   impact({target: "area", direction: "upstream"})
   ```

**Gate**: User must approve requirements before proceeding to Design

### Phase 2: Design
Output: `.kiro/specs/{feature_name}/design.md`

1. **Overview**: high-level summary
2. **Architecture**: system architecture, data flow, patterns
3. **Components & Interfaces**: responsibilities, APIs, dependencies
4. **Data Models**: entities, relationships, validation
5. **Error Handling**: error types, propagation, logging
6. **Testing Strategy**: unit, integration, TDD opportunities
7. Include Mermaid diagrams for complex architectures
8. Research done in-context (no separate research files)
9. Reference impact analysis for proposed changes:
   ```
   impact({target: "existing_interfaces", direction: "upstream"})
   ```

**Gate**: User must approve design before proceeding to Tasks

### Phase 3: Tasks
Output: `.kiro/specs/{feature_name}/tasks.md`

1. Convert design into actionable checkbox list
2. Maximum two-level hierarchy (decimal: 1.1, 1.2)
3. Coding-only activities (no deployment, user testing, metrics)
4. Reference specific requirements for traceability
5. Incremental building — each task builds on previous
6. No orphaned code — everything must be wired together

**Gate**: User must approve tasks before proceeding to Execute

### Phase 4: Execute
- One task at a time
- Set task status to `in_progress` before starting
- Implement following the design
- Set task status to `completed` when done
- Stop after each task for user review
- Use GitNexus for verification:
  ```
  detect_changes()  # verify only expected files changed
  impact(...)       # check no unexpected breakage
  ```

### Phase 4b: Sanity Check (Per Task + Final)
**Per task:**
- [ ] Does the implementation match the design?
- [ ] Does it satisfy the acceptance criteria from requirements?
- [ ] Have I tested this specific change?
- [ ] `detect_changes()` — verify scope matches task

**Final:**
- [ ] All acceptance criteria from requirements are met
- [ ] Design compliance verified
- [ ] All execution flows affected by changes are tested
- [ ] No orphaned code or unused implementations *(Kiro)*
- [ ] No scope creep beyond the spec

### Phase 5: Verify
- Run tests for all affected execution flows
- Verify acceptance criteria from requirements
- Check design compliance

## Token Budget
- **Typical per phase**: 15K-40K tokens
- **Full feature**: 60K-200K+ tokens
- **Warning**: this is a high-consumption workflow. For each phase, check if you have enough remaining budget. If not, recommend session summarization between phases.

## GitNexus Integration — Throughout
- Requirements: query existing functionality
- Design: impact analysis on affected interfaces
- Tasks: context on dependencies
- Execute: detect_changes per task, impact verification

## Hallucination Watchpoints
- Skipping approval gates (must wait for explicit user approval)
- Implementation drift: code doesn't match design
- Scope creep: adding features not in requirements
- Orphaned tasks: creating code nothing uses
- Vague requirements: not specific enough to test
- Over-designing: architecture that exceeds what's needed
