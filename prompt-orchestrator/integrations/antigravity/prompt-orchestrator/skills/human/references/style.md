# Presets, rubric, output formats and examples

Delivery presets, strict-mode scoring, the exact output shapes and contract-compliant worked examples.

Contents: Presets; Scoring rubric; Output formats; Worked examples.

## Presets

A preset changes delivery inside a confirmed finding's sentence. It never adds facts, opinions, examples, anecdotes, certainty or personality the source lacks. When a proposed edit adds a comparison, judgment, promise or causal claim, reject it. When the case for the edit is uncertain, keep the source.

| Preset | Delivery | Best for |
|---|---|---|
| `crisp` (default) | Direct and economical in the source's register. Remove a formulaic opener when the sentence works without it; replace an inflated abstraction with the source's concrete fact; prefer a plain verb to a vague verb-noun phrase. Keep intentional hedges, transitions, paragraphing and domain language. Do not impose sentence-length targets, active voice or short paragraphs on already-natural prose. | Technical writing, documentation |
| `warm` | Conversational, not casual. Natural contractions, occasional "you" when the source addresses a reader, light transitions, a soft landing instead of an abrupt end. Use only supplied names, numbers, timing and actions; make an abstract purpose plain by saying what the named actor does. Avoid forced intimacy ("Hey friend!"), stacked exclamation marks, "super/awesome/amazing", "I hope this email finds you well". | Emails, blog posts |
| `expert` | Confident to the degree the source supports. Assertion, then evidence, then implication or caveat. Show knowledge through the source's specific contexts, numbers and named examples; never announce credentials ("In my extensive experience", "Trust me"). Keep every hedge the source needs. | Articles, analysis |
| `story` | Narrative order the source already has: scene, tension, resolution. Use the source's concrete details and quotes, cut "Let me tell you a story" and "And that's when I realized", and end on the image or moment instead of an explained moral. Never invent a scene, name, dialogue or number. | Case studies, personal posts |

Voice without invention: clean text can still read as anonymous (no stance, uniform rhythm, no specifics). Add first person, opinion, anecdote or sensory detail only when the author supplies them or a taught voice card records them. In impersonal copy (reference docs, third-party announcements) never fabricate an "I" or a lived experience: an invented anecdote is a louder tell than the slop it replaces. Dropping habitual hedges is fine; dropping load-bearing scope or certainty is not.

## Scoring rubric

Score 1 to 5 per criterion, 40 maximum. Strict mode fails below 32.

| Criterion | 5 means | Red flags |
|---|---|---|
| Directness | Opens with the point; every sentence advances it | "It's worth noting", "To be fair", habitual "I think / perhaps / kind of" |
| Natural rhythm | Sentence lengths vary naturally, mixed structures, no template | Uniform length, stacked fragments |
| Concrete verbs | Specific, visualizable verbs | leverage, utilize, facilitate, optimize, navigate, unpack, foster |
| Reader trust | Assumes competence, no over-explaining | "Think about it", "Let that sink in", "In other words", "As you know" |
| Human authenticity | No AI tells, and the voice matches the source or the taught card | Performative emphasis, binary contrasts, inflation, chatbot residue; also invented voice |
| Content density | Every word necessary | "At its core", "In today's [X]", "When it comes to", "Moving forward" |
| Fact preservation | Every number, name, date, URL, quote, scope and negation intact | Any loss or alteration |
| Template avoidance | Organic structure | "Not X. Y.", "X. That's it.", "Think about it:", a three-item list everywhere, every paragraph ending on a punch |

36 to 40: occasional minor tells. 32 to 35: passing. 28 to 31: AI patterns visible. Under 28: reads as generated.

## Output formats

Quick rewrite: return the cleaned text only.

Audit:

```markdown
## Issues found

- "[quoted span]": [category], [severity], [why it reads as machine-written]

## Assessment

- Clear problems: [...]
- Judgment calls or context-dependent: [...]
- Protected spans: "[span]": [reason it stays]
```

Strict or requested analysis:

```markdown
## Transformed text

[the rewrite]

## Validation

- Constraints: [X]/[Y] preserved
- AI patterns: [N] remaining (was [M])
- Structure: [pass/fail]
- Readability: grade [X], sentence variance [Y]
- Change: [X]% from original
- Score: [X]/40
```

## Worked examples

Each example follows the core contract: only confirmed spans change, and nothing new is added.

Throat-clearing, binary contrast and an emphasis crutch:

> Here's the thing: building products is hard. Not because the technology is complex. Because people are complex. Let that sink in.

> Building products is hard, and the reason is people, not technology.

Filler, inflation and jargon (the claim and its scope survive):

> In today's fast-paced business environment, it's becoming increasingly important for organizations to leverage their core competencies while navigating the complex landscape of digital transformation.

> Organizations increasingly need to use their core strengths during digital transformation.

Dramatic fragmentation:

> Speed. Quality. Cost. You can only pick two. That's it. That's the tradeoff.

> Speed, quality, cost: you can only pick two.

Meta-commentary and a colon reveal:

> Hint: the answer isn't what you think. Plot twist: it's actually quite simple. Let me explain. Think about it: when you remove complexity, things get easier.

> The answer is simple: when you remove complexity, things get easier.

Protected source, returned unchanged (register guard and literal jargon):

> Users must never store secrets in client-side code. The loan used 3:1 leverage, and the lease may be terminated only under Section 12(b).

No findings, returned byte-for-byte:

> We tested the API, fixed the retry path, and shipped on June 18. p99 latency fell to 180 ms.
