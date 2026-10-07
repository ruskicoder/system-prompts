---
name: file-operations
description: Read, write, search, and edit files across the workspace. Enforces the
  READ-BEFORE-WRITE rule, batch file reads, atomic SEARCH/REPLACE blocks, and file
  discovery via grep and glob rather than terminal commands.
argument-hint: <file path or search pattern>
---

<!-- Generated from skills/file-operations.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: File Operations

## Purpose
Read, write, search, and edit files in the filesystem with maximum efficiency and minimal token waste.

## Tools Required
- readFile / readMultipleFiles
- write / fsWrite
- append / fsAppend
- edit / strReplace / search_replace
- grep / grepSearch
- glob / fileSearch / glob_file_search
- delete / deleteFile
- list_dir / listDirectory

## General Principles
- Prefer batch reads (readMultipleFiles) over sequential single-file reads
- Read entire files when practical: partial reads force extra roundtrips
- Search first (grep/glob) before reading when you don't know exact file location
- Never print file contents to user: use edit/write tools instead
- Never generate binary, hashes, or non-textual content

## Reading Files

### Single File
- Use `readFile` with known absolute path
- For large files (>500 lines), read in chunks with offset/limit
- Prefer reading a large meaningful section over many small sequential reads

### Multiple Files
```python
# Preferred: batch related files in one call
readMultipleFiles(paths=[...])
```

### File Discovery
1. Use `glob` / `fileSearch` when you know part of the filename
2. Use `grep` / `grepSearch` when searching for content patterns
3. Use `listDirectory` for understanding structure
4. NEVER use shell `find`, `grep`, `cat` for file operations: use dedicated tools

## Writing Files

### Creating New Files
- Use `write` / `fsWrite` for new files or complete rewrites
- For files >50 lines, prefer write + follow-up appends
- Always create with complete, immediately runnable content
- Include all imports, dependencies, and types

### Appending to Existing Files
- Use `append` / `fsAppend` when adding to the end of a file
- File must already exist

### Editing Existing Files (SEARCH/REPLACE)
- Use `edit` / `strReplace` / `search_replace` for targeted edits
- CRITICAL: `oldString` / `SEARCH` block must match EXACTLY, character for character, including whitespace
- Include 2-5 lines of surrounding context to ensure uniqueness
- Break large edits into a series of smaller, targeted SEARCH/REPLACE blocks
- Each block should change a focused section: don't edit half a file at once

```python
# GOOD: precise with context
edit(
    filePath="src/app.py",
    oldString="def old_function():\n    return x + 1\n\ndef another():\n    pass",
    newString="def new_function():\n    return x * 2\n\ndef another():\n    pass"
)

# BAD: too little context (may match multiple places)
edit(
    filePath="src/app.py",
    oldString="return x + 1",
    newString="return x * 2"
)
```

### Partial Write for Large Files
- For large files where only small sections change, use `// keep existing code` markers
- The unchanged code stays as a comment placeholder
- Only applies when the tooling supports this pattern

## Deleting Files
- Use `deleteFile` / `delete` with explanation
- Handles non-existent files gracefully

## Searching

### Content Search (grep)
- Use `grep` / `grepSearch` for regex pattern matching across files
- Rust regex syntax. Escape special characters: `(`, `)`, `[`, `]`, `{`, `}`, `+`, `*`, `?`, `^`, `$`, `|`, `.`, `\`
- Include patterns to filter file types when possible
- Results capped at 50: refine query if results fill up

### File Search (glob)
- Use `glob` / `fileSearch` when you know part of the filename
- Glob patterns like `**/*.ts`, `src/**/*.py`

## Directory Listing
- Use `listDirectory` / `list_dir` with optional depth parameter
- Use for understanding project structure before diving in

## Batch Editing Rule
- When making multiple edits to the same file, combine ALL changes into a SINGLE edit call
- This minimizes roundtrips and token overhead
- Only split into multiple calls when edits are in completely unrelated sections

## Post-Edit Verification
- After editing, check for linter errors by running lint tools
- If errors introduced, fix them (max 3 fix cycles per file)
- Verify imports are complete and correct
