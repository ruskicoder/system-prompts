# Rewrite, audit and cleanup workflows

Step-by-step flows for the three editing commands, plus the multi-agent split.

## Rewrite workflow

Set `$INPUT` to the source and `$OUTPUT` to your rewrite. Save both to files for the gates.

Pass 1, diagnose:

1. Read the whole source first. Note what each sentence contributes and every concrete defect.
2. Extract the constraints: `python3 <skill-dir>/scripts/human_tool.py constraints < original.txt`.
3. Scan for candidates the reading missed:

```bash
python3 <skill-dir>/scripts/human_tool.py scan < original.txt
python3 <skill-dir>/scripts/human_tool.py structure < original.txt
python3 <skill-dir>/scripts/human_tool.py silhouette < original.txt
python3 <skill-dir>/scripts/human_tool.py readability < original.txt
```

4. Read the selected preset for delivery only. A preset cannot authorize a finding.
5. Classify every candidate span as confirmed or protected. If nothing is confirmed, return the source exactly and stop.

Pass 2, repair: apply the Rewrite rules in `contract.md` to confirmed sentences only. Undo any edit that changes a fact, meaning, register, attribution or protected domain phrase.

Validate: run the gate battery (Validation in `contract.md`). Return the cleaned text only, unless the user asked for the strict analysis block in `style.md`.

## Audit workflow

Change nothing. Run `scan`, `structure`, `silhouette` and `readability` on the input, then read every sentence yourself: the scanners are necessary, not sufficient. Re-read negations, scope and certainty. Report each issue by quoted span, category, severity and why it reads as machine-written, separating clear problems from register-dependent judgment calls, and list protected spans with the reason they stay.

## Cleanup workflow

Co-writer mode: surface edits for the user to accept or reject. Never apply them silently, and never run as a background daemon.

```bash
python3 <skill-dir>/scripts/human_tool.py suggest doc.md > suggestions.json
python3 <skill-dir>/scripts/human_tool.py suggest doc.md --apply-replacements repl.json > suggestions.json
python3 <skill-dir>/scripts/human_tool.py check-suggestions suggestions.json
```

- `suggest` emits ordered, non-overlapping suggestions `{span, severity, category, rationale, suggested_replacement, phrased_as_question}` with `suggested_replacement` left null.
- You write the replacements into `repl.json` and merge them with `--apply-replacements`.
- Hard findings become direct replacements. Soft findings are register-dependent, so their rationale is a question (`phrased_as_question: true`).
- `check-suggestions` is blocking. Every replacement must pass all four gates or be dropped:
  - `span-minimality`: an edit changes only its own span; a whole-sentence rewrite fails.
  - `replacement-scanner`: each replacement passes both scanners on its own and adds no new violation in context.
  - `accept-all`: applying every suggestion yields a document that passes both scanners and preserves every constraint of the original.
  - `span-overlap`: spans may not overlap.

## Multi-agent split

For orchestrated runs, give each detector agent one pack and have it return JSON findings only (`{"span", "rule", "pack", "severity", "note"}`):

| Pack | Owns | Notes |
|---|---|---|
| phrases-core | throat-clearing, emphasis, significance, jargon, vague attribution, false agency, filler, chatbot artifacts, conclusions, rhetorical setups, list inflation | Leave literal, legal, medical, code and domain uses unreported |
| structure | the structure and silhouette metrics, macro tells | Quote the smallest span; use paragraph ranges for whole-document patterns |
| voice | anti-slop register, binary contrast, contrastive definitions, fragments, slogan cadence, tool agency, em dash, exclamation and bold overuse, warmth stripped into telegraphese | Mark hard when the cadence is itself a formula |
| register-guards | hedges, negations, absolutes, scope words that must survive | Every finding is a preservation constraint; run on the whole text |
| facts | numbers, dates, names, URLs, quotes, identifiers, approximations, party relationships | Hard for exact facts, negations, scope and quantities |

Measured tiering: span-scoped replacement is safe on the cheapest capable model because the gates carry the safety. Full rewrites of register-sensitive text erode hedges, absolutes and legal negations on cheap models, so give them to the strongest model and re-scan. Structure is always machine-detected and machine-gated.
