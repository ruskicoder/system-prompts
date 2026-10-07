---
name: turnaround-builder
description: End-to-end prototyping and greenfield application turnaround builder. Generates complete project skeletons, manifests, UI components, backend routes, and verified builds in a single comprehensive pass.
argument-hint: "<application concept or prototype description>"
---

# Workflow: Turnaround Builder

## When to Use
| Criteria | Match |
|----------|-------|
| Intention | new_app, prototype, proof_of_concept |
| Complexity | from scratch, single-turn generation |
| Power Mode | Balanced or Deep |
| Clarity | requirements may be high-level ("make me a todo app") |

## Required Skills
- project-scaffolding
- file-operations
- code-execution
- code-quality-testing
- communication-tone
- build-discipline
- safety-profiles (default)

## Flow

### Step 0: Thinking Stage (Pre-Action)
- [ ] What technology stack best fits this project? Use defaults unless specified
- [ ] What's the CORE functionality? Don't over-engineer: minimum viable
- [ ] What files are truly needed? No unnecessary abstractions
- [ ] Think HOLISTICALLY and COMPREHENSIVELY BEFORE creating an artifact
- [ ] Consider ALL relevant files, dependencies, and potential impacts

### Step 1: Think Holistically
Before writing ANY file, plan the entire project:
- What technology stack?
- What are the core features?
- What's the data model?
- What's the UI structure?
- What files are needed?

### Step 2: Present Overview
Give the user a quick architecture summary:
- Stack choice (React/Vite/Tailwind/shadcn)
- Component tree
- Data flow
- 3-5 sentence overview

### Step 3: Build Everything
Generate all files in one comprehensive pass:
1. Create dependency manifest
2. Configure build tooling
3. Create all source files
4. Ensure all imports are valid
5. Verify everything compiles/builds

### Step 4: Verify
- Run build to check for errors
- Fix any compilation issues
- If web app: start dev server and offer browser preview

### Step 4b: Sanity Check
- [ ] Does the project BUILD without errors? Run the build command
- [ ] Are all imports valid and files exist? ("All imports MUST exist")
- [ ] Is the app functional at the basic level?
- [ ] Have I only implemented what was asked? No over-engineering?
- [ ] Is the UI responsive and modern?
- [ ] Does it have proper error handling for the core flow?

### Step 5: Summary
- Single, non-technical sentence explaining what was built
- 2-3 bullet points on key features implemented
- Instructions to run the project

## Style Guidelines
- **UI**: beautiful, modern, responsive
- **Components**: shadcn/ui by default, lucide-react for icons
- **Styling**: Tailwind CSS exclusively
- **Code**: minimal, clean, production-quality
- **Error handling**: let errors bubble up; they'll be caught in dev
- **DO NOT overengineer**: minimum viable implementation

## What NOT to Do
- State the default stack and packages in one plan and get one confirmation; do not ask about each choice separately
- Don't create placeholder files or stubs
- Don't leave TODO comments
- Don't implement features user didn't ask for

## What to Include
- Working, immediately runnable code
- All necessary imports and dependencies
- Proper styling (not default HTML)
- Responsive design
- Interactive functionality

## Token Budget
- **Typical**: 10K-30K tokens
- **Max recommended**: 50K tokens
- Larger projects should be split into phases

## GitNexus Integration
- Minimal: new code has no graph yet
- If integrating into existing repo: `impact` on affected interfaces

## Hallucination Watchpoints
- Incomplete implementations (missing files, missing imports)
- Components that look good but don't work
- Using libraries not in the dependency manifest
- Not checking if the code actually builds
- Over-engineering the prototype
