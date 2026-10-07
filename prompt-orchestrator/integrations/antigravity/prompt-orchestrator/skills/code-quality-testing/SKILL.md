---
name: code-quality-testing
description: Write clean, runnable, tested code and execute unit/integration test
  suites and linter passes. Trigger with "run tests", "fix test failure", "add unit
  tests", or when debugging root causes, verifying immediate code runnability, or
  enforcing coding standards.
argument-hint: <test command or test target>
---

<!-- Generated from skills/code-quality-testing.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Code Quality & Testing

## Purpose
Write clean, correct, well-tested code through systematic quality practices.

## Tools Required
- Linter/analyzer tools
- Test framework commands
- Code execution tools

## General Principles
- Code must be immediately runnable: all imports, deps, endpoints included
- Write minimal code: only what's needed for the task, nothing extra
- Follow existing codebase conventions (style, patterns, libraries)
- Prefer simple solutions: don't overengineer
- Verify before presenting: test your code

## Immediately Runnable Code

### Checklist Before Presenting
- [ ] All imports/requires are present
- [ ] All referenced variables/functions are defined
- [ ] Dependencies listed in package manifest
- [ ] No syntax errors (proper brackets, semicolons, indentation)
- [ ] Type definitions match usage
- [ ] API endpoints exist and match

### Web Apps
- Give beautiful, modern UI
- Use responsive design
- shadcn/ui + Tailwind default stack
- lucide-react for icons, recharts for charts

## Testing Practices

### Unit Tests
- Test core logic and edge cases
- One test file per source module
- Test both success and failure paths
- Mock external dependencies

### Integration Tests
- Test component interactions
- Test data flow through layers
- Test API endpoints end-to-end

### Running Tests
- After making changes, run relevant tests
- Don't commit if tests fail
- Fix test failures before marking task complete

## Debugging
- Address root cause, not symptoms
- Add descriptive logging before trying fixes
- Use test functions to isolate problem
- Only make changes when you're certain of the fix
- If uncertain, gather more data first

```python
# Debugging workflow
1. Observe symptom (error message, wrong output)
2. Gather data (logs, state, inputs)
3. Form hypothesis about root cause
4. Add targeted logging to confirm
5. Apply minimal fix
6. Verify fix resolves the symptom
```

## Error Handling Philosophy
- For prototypes/rapid dev: let errors bubble up; they'll surface for AI to fix
- For production: proper try/catch with meaningful error messages
- Never expose stack traces to end users
- Log errors for debugging without leaking sensitive data

## Linter Integration
- After editing a file, check linter results
- Fix introduced errors (max 3 cycles per file)
- Don't make uneducated guesses to fix lint errors
- If stuck after 3 cycles, present to user with what you know

## Code Review Before Presenting
- [ ] Does it match the requirement?
- [ ] Is it the minimal implementation?
- [ ] Are there edge cases not handled?
- [ ] Does it follow codebase conventions?
- [ ] Are there security concerns?
- [ ] Is it readable and maintainable?

## Refactoring
- Small, focused commits
- One concern per change
- Don't mix refactoring with feature work
- Preserve existing behavior during refactoring
- Add tests before refactoring if coverage is lacking
