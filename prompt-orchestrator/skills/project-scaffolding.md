# Skill: Project Scaffolding

## Purpose
Create new projects, scaffolds, and codebases from scratch with efficient, minimal structure. _Source: Kiro (Category O)_

## Tools Required
- File operations (write, mkdir) _Source: Kiro (Category D)_
- Package managers (npm, pnpm, pip, cargo, etc.) _Source: Augment (Category E)_
- Terminal commands (init, install) _Source: Kiro (Category C)_

## Minimal Skeleton First (Kiro pattern)
- Start with the absolute minimum structure _Source: Lovable (Category E)_
- Present project structure overview before creating files _Source: Kiro (Category O)_
- Create skeleton implementations only _Source: Kiro (Category O)_
- Focus on essential functionality _Source: Cursor (Category E)_

```python
# WORKFLOW for scaffolding:
1. Provide concise project structure overview
2. Create minimal directory layout
3. Write skeleton implementations (stubs + signatures)
4. Fill in core functionality
5. Add dependency management
```
_Source: Kiro (Category O)_

## Single Artifact Pattern (Bolt pattern)
- For small-to-medium projects, create a single comprehensive response _Source: Bolt (Category Q)_
- Include all shell commands, file contents, and dependency info in one flow _Source: Bolt (Category Q)_
- Think holistically before writing any file _Source: Cursor (Category E)_

## Full-Stack App Defaults
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui _Source: Canva (Category E)_
- **Backend**: Node.js + Express / Python + FastAPI (match to user preference) _Source: Emergent (Category P)_
- **Database**: SQLite for prototyping, PostgreSQL for production _Source: Kiro (Category O)_
- **Icons**: lucide-react _Source: Bolt (Category Q)_
- **Charts**: recharts _Source: Bolt (Category Q)_

## File Organization
- Small, focused files (Lovable rule): aim for <50 lines per component _Source: Lovable (Category Q)_
- One component per file, one hook per file _Source: Same-Dev (Category E)_
- Group by feature, not by type _Source: Kiro (Category O)_
- Flat is better than nested — avoid unnecessary subfolders _Source: Kiro (Category O)_

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
_Source: Kiro (Category O)_

## Dependency Management
- Create `package.json` / `requirements.txt` / `Cargo.toml` with versioned deps _Source: Augment (Category E)_
- Use known-compatible versions _Source: Bolt (Category Q)_
- Prefer libraries that don't rely on native binaries (Bolt rule) _Source: Bolt (Category P)_
- For Node.js: Vite over custom web server _Source: Bolt (Category Q)_
- Include `.gitignore` _Source: Bolt (Category P)_

## What to Include in Every New Project
- [ ] Dependency manifest (package.json, etc.) _Source: Augment (Category E)_
- [ ] README with setup instructions _Source: Kiro (Category O)_
- [ ] `.gitignore` _Source: Bolt (Category P)_
- [ ] Entry point file _Source: Kiro (Category O)_
- [ ] Basic project structure _Source: Kiro (Category O)_
- [ ] Linter/formatter config if relevant _Source: Augment (Category E)_

## Incremental Building
- Don't create files that won't be used _Source: Lovable (Category E)_
- Each additional file must be referenced/imported by existing code _Source: Amp (Category E)_
- If feature scope is large, do it in phases:
  1. Core data model _Source: Kiro (Category O)_
  2. Business logic _Source: Kiro (Category O)_
  3. API/Interface layer _Source: Kiro (Category O)_
  4. UI (if applicable) _Source: Kiro (Category O)_

## No Dead Code
- Never leave placeholder implementations _Source: Lovable (Category E)_
- Don't include functions/classes that aren't called _Source: Same-Dev (Category E)_
- Remove commented-out code _Source: Same-Dev (Category E)_
- Don't over-abstract — wait for duplication to happen before extracting _Source: Amp (Category E)_
