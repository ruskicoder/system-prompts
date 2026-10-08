---
name: memory-management
description: Persist and retrieve architectural context, user preferences, and project milestones across sessions. Use for crash-safe checkpointing, updating persistent memories, and managing context window retention.
argument-hint: "<memory action or context to save>"
---

# Skill: Memory & Context Management

## Purpose
Persist and retrieve important context across sessions, manage conversation state, and leverage memory systems efficiently.

## Tools Required
- Memory CRUD tools (create/update/delete memory)
- Todo list tools (todo_write)
- Persistent storage APIs (where available)
- Steering/configuration file tools

## General Principles
- Save context proactively: context windows are limited
- Save early, save often: don't wait until end of task
- Prefer updating existing memories over creating duplicates
- Tag memories for efficient retrieval
- Prioritize: user preferences > project decisions > technical context > conversation state

## Memory Creation

### What to Save
- User preferences (tone, formatting, tool usage preferences)
- Explicit user requests to remember something
- Important code snippets and project structure
- Technical stack decisions
- Major milestones and feature decisions
- Design patterns and architectural choices
- Current task state for multi-session work

### How to Save
```python
# Create new memory
create_memory(
    Action="create",
    Content="User prefers verbose explanations with code examples",
    Title="User communication preference",
    Tags=["user_preference", "communication"],
    UserTriggered=False  # set True only if user explicitly asked
)

# Update existing memory (find semantically similar first)
create_memory(
    Action="update",
    Id="existing_memory_id",
    Content="Updated preference content",
    Title="Updated title"
)

# Delete incorrect memory
create_memory(
    Action="delete",
    Id="incorrect_memory_id"
)
```

### When to NOT Save
- Trivial temporary state
- Information that will be irrelevant after current task
- Content the user explicitly doesn't want saved
- Sensitive/PII data

## Task Management (todo_write pattern)
- Use for multi-step tasks to track progress
- Create at start of complex task
- Mark items complete as soon as done (don't batch)
- Keep exactly ONE item `in_progress` at a time
- Update status in real-time
- Interrupt stash: on a deviation, record the current workflow, step and next action as a todo item, resolve the interrupt, then resume from it (communication-tone section 7)

```python
todo_write(
    todos=[
        {"content": "Implement user authentication", "status": "completed", "priority": "high"},
        {"content": "Add password validation", "status": "in_progress", "priority": "high"},
        {"content": "Write tests for auth flow", "status": "pending", "priority": "medium"}
    ]
)
```

## Session Continuation
- When ending a session, produce a structured summary
- Include: what was discussed, decisions made, current state, next steps
- The summary should be self-contained for next session to pick up

## Steering Files
- For persistent behavioral instructions, use steering files
- Steering files can be:
  - **Always included** (default): for universal instructions
  - **Conditional** (fileMatch): triggered when specific files are read
  - **Manual**: only when explicitly referenced
- Use file references `#[[file:path]]` to include specs into context

## Conversation History Awareness
- Be aware of context window limits
- If conversation is long, memory systems help preserve key facts
- Don't repeat information that was already established
- Refer back to earlier parts of conversation when relevant
- If context is lost (new session), ask for summary if one wasn't provided
