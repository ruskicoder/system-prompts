# Core contract, preservation and validation

Read before every audit, rewrite, suggestion or voiced draft. It overrides presets and voice cards.

## Core contract

This contract governs every audit, rewrite, suggestion and voiced draft. Presets and voice cards change delivery only. Nothing else in this skill overrides it.

### Goal

Repair concrete AI-writing or clarity defects. Leave everything else unchanged. Prefer a no-op to an uncertain edit.

### Findings

- Read every sentence, including headings and endings, before looking at scanner output. Phrase lists are incomplete: recognize paraphrased scaffolding by its function, not only by its wording.
- Quote the smallest defective span and name the contextual defect: formulaic framing, empty or inflated abstraction, unsupported rhetorical certainty, opaque or mixed metaphor, misleading heading, needless repetition, or a clear internal contradiction or ambiguity.
- Track every hard scanner match and every other candidate as `confirmed` or `protected`, with a reason. Repair every confirmed span.
- Confirm filler when deleting it loses no meaning. Replace inflated diction with its plain equivalent.
- Punctuation, vocabulary, cadence and structure alone prove neither a defect nor authorship.
- Do not fact-check, use today's date or outside knowledge to judge truth. Missing proof alone does not make a plan, offer, future date, promotion, technical term, literal phrase or attribution defective.
- Compare the source's own claims. Qualify a status that the source's observations contradict. Explicitly reject every initial, conditional or repeat action that exceeds a limit the source states; a hedge does not make it safe. Keep attributed claims intact and state conflicts separately. Make no edit when nearby prose already states the conflict and its uncertainty. Attribution does not protect a separate operative recommendation.

### Protections

A scanner match alone never authorizes an edit. Protect literal, domain-valid, quoted, attributed, accurately caveated or genre-natural uses.

- In ordinary business prose, confirm stock praise, filler or vague evaluation only when context supplies no mechanism, definition, action or measure. A noun referent alone is not enough: "a game-changer for the product" stays vague unless the text says what changes. "Actionable" is valid when the actions are defined. "Raises the bar" is valid when literal or measured.
- Soft cadence and document-shape scores never authorize an edit on their own.
- Inspect slogans and closing calls to action even when the tools are quiet. Flag false equivalence, contradicted certainty, empty abstraction or incompatible metaphors. Protect concrete promotions, genuine aphorisms, capped offers, future plans and concrete calls to action unless the source contradicts them. A stock journey or milestone sentence that adds no fact, action or claim is empty.
- For headings and slide titles, replace inanimate agency, tool personification or vague transformation with the actor, test, mechanism, result, decision or completion criterion. Renaming the same abstraction is not a repair.
- When macro cleanup is requested, remove connective scaffolding and a moralizing recap coda, including repeated facts. The coda's lesson is not protected.

### Rewrite rules

- Edit only sentences that contain a confirmed finding, using the smallest repair. Copy every other sentence byte-for-byte, in its original order and paragraph. With no findings, return the source exactly and skip validation.
- Preserve facts, quantities, dates, names, quotations, citations, code, units, scope, uncertainty, attribution, register and meaning.
- Add no claims, advice, personality, anecdote, certainty or conclusion.
- Delete empty framing. Do not substitute new filler, and do not produce staccato "anti-slop" prose (stacked short fragments are a tell of their own).
- Preserve force-bearing "never", "must" and "all" exactly in safety, security, legal and technical rules.
- Re-read the result for missed defects and introduced filler. Stop at matters of taste.
- For a list, return one validated replacement per item.

### Audit rules

Report findings and protections without rewriting. Report each requested load-bearing span separately. The exact no-op rule applies to rewrites, not to audits that must report protections.

### Decision rule

Return a finding only when the contextual defect is clearer than the case for preserving the text.

## Preservation rules

### Exact: never modify

| Type | Examples |
|---|---|
| Numbers and quantities | `$47.3M`, `23%`, `1,500 users`, `3 engineers` |
| Dates and times | `Q3 2024`, `March 15, 2024`, `2024-03-15`, `14:30 UTC` |
| Measurements and ranges | `5.2kg`, `100ms`, `2TB`, `$50-75K`, `3-5 years` |
| Proper nouns | companies, products, people, places, brand terms |
| Technical literals | API paths, identifiers, config values, version numbers, file paths, flags |
| Quoted material | direct quotes with their attribution, code snippets including whitespace |
| References | URLs, DOIs, ISBNs, citations such as `[1]` or `(Smith et al., 2024)`, `Section 12(b)` |

Magnitude and unit matter: `$47.3M` must not become `$47.3 billion`, and `150 km` must not become `150 miles`.

### Meaning: may rephrase, must not change

| Kind | Allowed | Not allowed |
|---|---|---|
| Causal | "A caused B" to "B resulted from A" | "A influenced B" (weaker) |
| Comparison | "3x faster" to "outperforms by 3x" | "faster" (lost quantifier) |
| Conditional | "If A, then B" to "B happens when A" | "A and B" (lost condition) |
| Negation | "does not support Y" to "lacks Y support" | "partially supports Y" (inverted) |
| Scope | "Most users (73%)" to "73% of users" | "Users prefer X" (lost scope) |

Special cases:

- Keep approximations approximate: "about 50%" may become "roughly 50%", never "50%". "Q2" is not "June". "under 500 ms" is not "500 ms".
- Keep both bounds of a range, every item of a list (order may change) and both the quote and the attribution of a quotation.
- Keep party relationships: "Apple sued Qualcomm" is not "Qualcomm sued Apple".

### Register guards

In legal, medical, security and scientific text, hedges, negations, absolutes and scope words carry the claim. Treat each as a hard preservation constraint and run `preserve --strict`. Examples: "arguably does not rise to gross negligence under Section 12(b)", "may cause drowsiness in some patients", "does not establish causation", "never store secrets in client-side code", "notwithstanding anything to the contrary", "at least", "no more than", "unless", "except", "only". Scan scope across the whole document, because scope can be set sentences before the one being edited.

## Validation

After every rewrite or voiced draft:

```bash
python3 <skill-dir>/scripts/human_tool.py preserve original.txt rewritten.txt
python3 <skill-dir>/scripts/human_tool.py scan < rewritten.txt
python3 <skill-dir>/scripts/human_tool.py structure < rewritten.txt
python3 <skill-dir>/scripts/human_tool.py silhouette < rewritten.txt
python3 <skill-dir>/scripts/human_tool.py readability < rewritten.txt
python3 <skill-dir>/scripts/human_tool.py diff original.txt rewritten.txt
```

Block on: preservation loss; any introduced hard or `anti_slop_register` hit; unjustified structural damage; corroborated or hard silhouette damage; staccato; and, in strict mode, a rubric score under 32/40. Use `preserve --strict` for legal, medical, security or scientific text. Pre-existing soft cadence and uncorroborated soft silhouette warnings are advisory. Then re-read negations, conditions, scope, certainty and party relationships yourself.
