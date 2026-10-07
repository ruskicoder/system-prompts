# Structure, silhouette and macro tells

Document-shape metrics, idea-arrangement tells, judgment-only macro tells and the structure repair loop.

## Structure, silhouette and macro tells

`structure` measures document shape. Concrete thresholds to self-check:

| Metric | Suspicious when |
|---|---|
| Average sentence length | under 8 or over 34 words |
| `sentence_burstiness` | sentence-length variance under 18 across 5 or more sentences (uniform rhythm) |
| `one_line_staccato` | 3 or more one-line paragraphs under 8 words (allowed under `--genre social`) |
| `connective_paragraph_openers` | 3 or more consecutive paragraphs opened by "However,", "Moreover,", "In addition," and similar |
| `opener_repetition` | 4 or more paragraphs with the same opener (blocking) |
| `participial_closer_share` | 35% or more sentences ending on an -ing clause |
| `signpost_density`, `triad_density`, `bold_colon_listicle_count` | high rates of signposts, three-item lists and bold-label bullets |
| `conclusion_coda`, `summary_sandwich` | a moralizing closer ("Ultimately, this reminds us that...") or an ending that only recaps the intro |

`silhouette` scores how ideas are arranged, one level above the surface: body paragraphs that open on a discourse cue instead of their own claim (`scaffold_opener_share`), opening vocabulary that vanishes mid-document and returns at the end (`callback_content`, the strongest single tell), cue-opener roles rotating like a template (`role_entropy_bits`), intro words reappearing as body-paragraph heads (`preview_fulfillment`) and headings that restate the intro's outline (`heading_preview`). The composite `silhouette_penalty` flags at 1.0 or more, scored against an embedded human reference. Cite the specific metric, not only the composite. Deleting cue words defeats silhouette but not surface repetition, so always read silhouette together with `structure`.

Macro tells that need judgment (no scanner enforces them):

| Tell | Watch for | Genre caveat |
|---|---|---|
| Both-sidesism | "on one hand / on the other hand" that refuses to conclude when the piece owes a conclusion | Journalism, judicial analysis and literature reviews may need real opposing views |
| Templated redemption arc | a too-clean fall, lesson, transformation, uplift sequence | Memoir, sermons and some case studies use arcs on purpose |
| Preview/recap symmetry | the ending adds nothing beyond the intro | Abstracts, executive summaries and TL;DRs restate legitimately |
| Over-determination | explicit theme-stating that tells the reader what to infer | Tutorials and accessibility-minded docs may need it |
| Uniform emotional register | every paragraph at the same polished confidence | Formal reports may keep texture low on purpose |

Macro structure is hard to fix by self-review alone. Use the structure repair loop when shape findings remain after a rewrite.

## Structure repair loop

When `structure` or `silhouette` findings remain after a rewrite, feed the exact findings back as targeted directives instead of asking a model to self-check document shape (single-pass self-review rarely fixes macro structure).

```bash
python3 <skill-dir>/scripts/human_tool.py climb --prompt-file task.txt --out OUT --generate-cmd "<your CLI>" --max-rounds 4 --genre prose
```

Each round scans the latest draft, turns findings into instructions that name the paragraph, opener or metric, and regenerates. A preservation guard aborts the round that drops a fact (exit 4). Exit 0 means converged, exit 3 means the round cap was reached while still dirty. Without a CLI generator, run the same loop by hand: scan, write directives that cite each finding, regenerate, re-scan, and stop when clean or after 4 rounds. Re-read negations, conditions, scope, certainty and party relationships after every round.
