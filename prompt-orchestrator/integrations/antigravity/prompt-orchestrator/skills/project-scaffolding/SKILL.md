---
name: project-scaffolding
description: Scaffold new applications, generate dependency manifests, and create
  initial directory structures. Use when initializing new codebases, setting up modern
  React/Vite/FastAPI stacks, or generating minimal project skeletons.
argument-hint: <stack or project description>
---

<!-- Generated from skills/project-scaffolding.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Project Scaffolding

## Purpose
Create new projects, scaffolds, and codebases from scratch with efficient, minimal structure.

## Tools Required
- File operations (write, mkdir)
- Package managers (npm, pnpm, pip, cargo, etc.)
- Terminal commands (init, install)

## Minimal Skeleton First
- Start with the absolute minimum structure
- Present project structure overview before creating files
- Create skeleton implementations only
- Focus on essential functionality

```python
# WORKFLOW for scaffolding:
1. Provide concise project structure overview
2. Create minimal directory layout
3. Write skeleton implementations (stubs + signatures)
4. Fill in core functionality
5. Add dependency management
```

## Single Artifact Pattern
- For small-to-medium projects, create a single comprehensive response
- Include all shell commands, file contents, and dependency info in one flow
- Think holistically before writing any file

## Full-Stack App Defaults
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express / Python + FastAPI (match to user preference)
- **Database**: SQLite for prototyping, PostgreSQL for production
- **Icons**: lucide-react
- **Charts**: recharts

## File Organization
- Small, focused files: aim for <50 lines per component
- One component per file, one hook per file
- Group by feature, not by type
- Flat is better than nested: avoid unnecessary subfolders

```python
# GOOD: feature-based structure
components/
  UserProfile.tsx
  UserList.tsx
hooks/
  useUsers.ts
utils/
  format.ts

# AVOID: over-nested
components/users/profile/UserProfile.tsx
components/users/list/UserList.tsx
```

## Dependency Management
- Create `package.json` / `requirements.txt` / `Cargo.toml` with versioned deps
- Use known-compatible versions
- Prefer libraries that don't rely on native binaries
- For Node.js: Vite over custom web server
- Include `.gitignore`

## What to Include in Every New Project
- [ ] Dependency manifest (package.json, etc.)
- [ ] README with setup instructions
- [ ] `.gitignore`
- [ ] Entry point file
- [ ] Basic project structure
- [ ] Linter/formatter config if relevant

## Incremental Building
- Don't create files that won't be used
- Each additional file must be referenced/imported by existing code
- If feature scope is large, do it in phases:
  1. Core data model
  2. Business logic
  3. API/Interface layer
  4. UI (if applicable)

## No Dead Code
- Never leave placeholder implementations
- Don't include functions/classes that aren't called
- Remove commented-out code
- Don't over-abstract: wait for duplication to happen before extracting
