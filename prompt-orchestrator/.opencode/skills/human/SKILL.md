---
name: human
description: 'Find and repair AI writing patterns in English prose while preserving
  facts, meaning and voice: audit-only detection, a two-pass rewrite that edits only
  confirmed spans, reviewable co-writer suggestions, and teaching and mimicking a
  writer''s voice from their samples. Bundles standard-library scanners, a preservation
  validator and voice tools. Use to humanize, de-slop or unslop text, make a draft
  sound less robotic or less like ChatGPT, flag AI tells without changing anything,
  review a draft before publishing, or write in a specific person''s voice.'
argument-hint: '[rewrite | audit | cleanup | teach | mimic | voice-check] [text, file
  path or stdin]'
---

<!-- Generated from skills/human.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Human: find and repair AI writing patterns

Detect formulaic or unclear writing, repair only the defects you can confirm in context, and leave everything else byte-for-byte unchanged. Audit first. Rewrite only when the user asks for a rewrite. A clean scan does not prove a human wrote the text, and a familiar phrase does not prove a machine did.

## Non-negotiable rules

Read `references/contract.md` before any audit, rewrite, suggestion or voiced draft. It is the single behavior contract; nothing else in this skill overrides it. In short:

- A scanner match is a candidate, never a verdict. Confirm each defect in context; protect literal, domain-valid, quoted, attributed and genre-natural uses.
- Edit only sentences with confirmed findings, with the smallest repair. Copy every other sentence exactly. With no findings, return the source unchanged.
- Preserve facts, numbers, names, dates, quotes, code, units, scope, negations, hedges, attribution and register. Add no claims, opinions, anecdotes or certainty.
- Do not replace slop with staccato fragments or new filler.
- Run the validation gates after every rewrite or voiced draft. A voiced draft that trips a removal gate is rejected.

## Commands

A bare `/human <text>` runs `rewrite`. When the first word is not a command but the intent clearly maps to one, run that command.

| Command | Purpose | Read |
|---|---|---|
| `rewrite` | Default. Diagnose, repair confirmed findings, validate. | `references/workflows.md` |
| `audit` | Flag issues and change nothing. | `references/workflows.md` |
| `cleanup` | Span-level suggestions the user accepts or rejects. | `references/workflows.md` |
| `teach` | Build a voice profile and voice card from the writer's samples. | `references/voice.md` |
| `mimic` | Draft or rewrite in a taught voice under every removal gate. | `references/voice.md` |
| `voice-check` | Score whether a draft sounds like the taught writer. No rewrite. | `references/voice.md` |

| The user says | Run |
|---|---|
| "audit", "just flag it", "don't change anything", "review this before I publish" | `audit` |
| "suggest edits", "let me accept or reject each change" | `cleanup` |
| "harvest", "what writing of mine do you have?", "calibrate", "the A/B game", "quiz me on my voice" | `teach` |
| "write this like me", "match my voice", "mimic this author", "refine", "keep pushing until it sounds like me" | `mimic` |
| "does this sound like me?" | `voice-check` |
| "fix the structure", "it still reads like a template" | structure repair loop in `references/structure.md` |

## Arguments

| Argument | Meaning | Default |
|---|---|---|
| `--preset` | Delivery style: `crisp`, `warm`, `expert`, `story` (`references/style.md`) | `crisp` |
| `--strict` | Fail below 32/40 on the rubric; run preservation in `--strict` mode | off |
| `--report` | Same as `audit` | off |
| `--genre` | `prose`, `docs` (bold-label lists and heading previews allowed) or `social` (short-line cadence allowed) | `prose` |
| `--include-quoted` | Also scan quoted spans and blockquotes | off |
| Input | Text argument, file path or stdin | required |

Pass `--genre docs` or `--genre social` only when the input truly belongs to that genre. A false genre excuse does not clear a finding.

## Bundled tool

`scripts/human_tool.py` (next to this file) is standard-library Python 3. Run it from any directory:

```bash
python3 <skill-dir>/scripts/human_tool.py <command> [args]
```

Core commands: `scan` (phrases and patterns), `structure`, `silhouette`, `readability`, `constraints`, `preserve original.txt rewritten.txt`, `diff`. Every command prints JSON, and scanners exit 1 when they flag something. The full command list, including suggestion gates, harvest, voice profile, card, score, calibration, refine, stats and climb, is in `references/tools.md`.

## Reference files

Load only what the current task needs.

| File | Read when |
|---|---|
| `references/contract.md` | Always, before editing or auditing: findings, protections, rewrite rules, preservation rules, register guards, validation gates |
| `references/catalog.md` | Diagnosing: every pattern family with examples, repairs and protected literal uses; headings and slide titles |
| `references/structure.md` | Document shape: structure and silhouette metrics, macro tells, structure repair loop |
| `references/workflows.md` | Running `rewrite`, `audit` or `cleanup`, or splitting detection across agents |
| `references/voice.md` | Running `teach`, `mimic`, `voice-check`, the calibration game or the refine loop |
| `references/style.md` | Choosing a preset, scoring in strict mode, formatting output, worked examples |
| `references/tools.md` | Looking up any tool command and its arguments |

## Limits

- English only. Other languages get detection and a decline.
- The scanners propose candidates and context decides. A clean scan proves neither human authorship nor good writing, and the gates cannot guarantee that every defect is gone.
- In paired tests against the same model working without these rules, this approach found and repaired more issues but did not reach the precision and collateral-damage bar for whole documents. Prefer no-ops, keep edits span-minimal and always run the preservation gate.
- Voice scores are guides. Even strong authorship verification has a ceiling; under-claim.
- Harvested transcripts and voice folders are private: keep them local.
