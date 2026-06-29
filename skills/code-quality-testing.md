# Skill: Code Quality & Testing

## Purpose
Write clean, correct, well-tested code through systematic quality practices. _Source: Cursor (Category A)_

## Tools Required
- Linter/analyzer tools
- Test framework commands
- Code execution tools

## General Principles
- Code must be immediately runnable — all imports, deps, endpoints included _Source: Qoder (Category E)_
- Write minimal code — only what's needed for the task, nothing extra _Source: Cursor (Category E)_
- Follow existing codebase conventions (style, patterns, libraries) _Source: Aider (Category E)_
- Prefer simple solutions — don't overengineer _Source: Cursor (Category E)_
- Verify before presenting — test your code _Source: Cursor (Category E)_

## Immediately Runnable Code

### Checklist Before Presenting
- [ ] All imports/requires are present _Source: Aider (Category Q)_
- [ ] All referenced variables/functions are defined
- [ ] Dependencies listed in package manifest
- [ ] No syntax errors (proper brackets, semicolons, indentation) _Source: Kiro (Category Q)_
- [ ] Type definitions match usage _Source: Amp (Category E)_
- [ ] API endpoints exist and match _Source: Cursor (Category E)_

### Web Apps
- Give beautiful, modern UI (Windsurf rule) _Source: Windsurf (Category E)_
- Use responsive design (Lovable rule) _Source: Lovable (Category E)_
- shadcn/ui + Tailwind default stack (Lovable rule) _Source: Lovable (Category E)_
- lucide-react for icons, recharts for charts _Source: Lovable (Category Q)_

## Testing Practices

### Unit Tests
- Test core logic and edge cases _Source: Cursor (Category E)_
- One test file per source module _Source: Cursor (Category E)_
- Test both success and failure paths _Source: Augment (Category E)_
- Mock external dependencies _Source: Cursor (Category E)_

### Integration Tests
- Test component interactions
- Test data flow through layers
- Test API endpoints end-to-end

### Running Tests
- After making changes, run relevant tests _Source: Cursor (Category E)_
- Don't commit if tests fail _Source: Cursor (Category E)_
- Fix test failures before marking task complete _Source: Cursor (Category E)_

## Debugging (Windsurf pattern)
- Address root cause, not symptoms _Source: Codex (Category E)_
- Add descriptive logging before trying fixes _Source: Windsurf (Category F)_
- Use test functions to isolate problem
- Only make changes when you're certain of the fix _Source: Windsurf (Category F)_
- If uncertain, gather more data first _Source: Windsurf (Category F)_

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
- For prototypes/rapid dev: let errors bubble up (Lovable pattern) — they'll surface for AI to fix _Source: Lovable (Category G)_
- For production: proper try/catch with meaningful error messages _Source: Amp (Category E)_
- Never expose stack traces to end users _Source: Amp (Category G)_
- Log errors for debugging without leaking sensitive data _Source: Warp (Category G)_

## Linter Integration (Cursor pattern)
- After editing a file, check linter results _Source: Cursor (Category E)_
- Fix introduced errors (max 3 cycles per file) _Source: Cursor (Category E)_
- Don't make uneducated guesses to fix lint errors _Source: Cursor (Category E)_
- If stuck after 3 cycles, present to user with what you know _Source: Cursor (Category E)_

## Code Review Before Presenting
- [ ] Does it match the requirement? _Source: Cursor (Category E)_
- [ ] Is it the minimal implementation? _Source: Cursor (Category E)_
- [ ] Are there edge cases not handled? _Source: Augment (Category E)_
- [ ] Does it follow codebase conventions? _Source: Aider (Category E)_
- [ ] Are there security concerns? _Source: Kiro (Category G)_
- [ ] Is it readable and maintainable? _Source: Factory (Category A)_

## Refactoring
- Small, focused commits _Source: Factory (Category E)_
- One concern per change _Source: Factory (Category E)_
- Don't mix refactoring with feature work _Source: Amp (Category E)_
- Preserve existing behavior during refactoring _Source: Orchids (Category E)_
- Add tests before refactoring if coverage is lacking _Source: Cursor (Category E)_
