---
name: human
description: 'Find and repair AI writing patterns in English prose while preserving
  facts, meaning and voice. Covers audit-only detection, a two-pass rewrite (diagnose,
  then repair only confirmed spans), reviewable co-writer suggestions, and teaching
  and mimicking a writer''s voice from their own samples. Self-contained: the pattern
  catalog, rewrite contract, preservation rules, presets, rubric and a bundled standard-library
  Python tool (phrase, structure and silhouette scanners, preservation validator,
  readability, voice profiling and scoring, refine and structure-repair loops) all
  live in this one file. Use when asked to humanize, de-slop or unslop text, fix AI
  text, make a draft sound human, natural or less robotic, flag AI tells without changing
  anything, review a draft before publishing, or write in a specific person''s voice.
  Also use when pasted text ''sounds like ChatGPT'' or contains tells such as ''Here''s
  the thing:'', ''Let that sink in'' or ''In today''s fast-paced landscape''.'
argument-hint: '[rewrite | audit | cleanup | teach | mimic | voice-check] [text, file
  path or stdin]'
---

<!-- Generated from skills/human.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Human: find and repair AI writing patterns

Detect formulaic or unclear writing, repair only the defects you can confirm in context, and leave everything else byte-for-byte unchanged. Audit first. Rewrite only when the user asks for a rewrite. A clean scan does not prove a human wrote the text, and a familiar phrase does not prove a machine did.

Everything this skill needs is in this file: the behavior contract, the pattern catalog, the workflows and an embedded Python tool (last section). Nothing else has to be fetched or installed.

## Commands and routing

A bare `/human <text>` with no command word runs `rewrite`. When the first word is not a command but the intent clearly maps to one, run that command.

| Command | Purpose | Section |
|---|---|---|
| `rewrite` | Default. Diagnose, repair confirmed findings, validate. | Rewrite workflow |
| `audit` | Flag issues and change nothing. | Audit workflow |
| `cleanup` | Co-writer mode: span-level suggestions the user accepts or rejects. | Cleanup workflow |
| `teach` | Build a reusable voice profile and voice card from the writer's samples. | Teach workflow |
| `mimic` | Draft or rewrite in a taught voice under every removal gate. | Mimic workflow |
| `voice-check` | Score whether a draft sounds like the taught writer. No rewrite. | Mimic workflow |

| The user says | Run |
|---|---|
| "audit", "just flag it", "don't change anything", "review this before I publish" | `audit` |
| "suggest edits", "let me accept or reject each change" | `cleanup` |
| "harvest", "what writing of mine do you have?" | `teach`, step 1 |
| "calibrate", "the A/B game", "quiz me on my voice" | `teach`, calibration game |
| "write this like me", "match my voice", "mimic this author" | `mimic` |
| "refine", "keep pushing until it sounds like me" | `mimic`, refine loop |
| "does this sound like me?" | `voice-check` |
| "fix the structure", "it still reads like a template" | Structure repair loop |

## Arguments

| Argument | Meaning | Default |
|---|---|---|
| `--preset` | Delivery style: `crisp`, `warm`, `expert`, `story` | `crisp` |
| `--strict` | Fail the rewrite when the rubric score is below 32/40; run preservation in `--strict` mode | off |
| `--report` | Same as `audit` | off |
| `--genre` | `prose`, `docs` (reference docs may use bold-label lists and heading previews) or `social` (short-line cadence allowed) | `prose` |
| `--include-quoted` | Also scan quoted spans and blockquotes | off |
| Input | Text argument, file path or stdin | required |

Pass `--genre docs` or `--genre social` only when the input truly belongs to that genre. A false genre excuse does not clear a finding.

## Embedded tool: setup and commands

The last section of this file holds `human_tool.py`, a single-file Python 3 tool that uses only the standard library (verified on Python 3.13). Extract it once per session to a scratch path. Either copy the fenced block into `/tmp/human_tool.py` with your file-writing tool, or run:

```bash
awk '/^````python/{f=1;next} /^````$/{f=0} f' "<path to this skill file>" > /tmp/human_tool.py
```

```bash
python3 /tmp/human_tool.py --help
```

Every command prints JSON. Scanners exit 1 when they flag something and 0 when clean. Quoted spans (double quotes), markdown blockquotes, inline code and code fences are masked before phrase scanning, so a document that quotes bad writing does not flag its own examples. Non-English input returns `"non_english": true` and nothing else: that is the one graceful decline.

| Command | Purpose | Typical call |
|---|---|---|
| `scan` | Phrase and pattern scanner (literal triggers plus gated structural regexes) | `python3 /tmp/human_tool.py scan < input.txt` |
| `structure` | Document rhythm and shape metrics | `python3 /tmp/human_tool.py structure --genre docs README.md` |
| `silhouette` | Idea-arrangement tells (outline following, recap loops) | `python3 /tmp/human_tool.py silhouette < input.txt` |
| `readability` | Grade level, sentence statistics, variance | `python3 /tmp/human_tool.py readability < input.txt` |
| `constraints` | Extract must-preserve facts | `python3 /tmp/human_tool.py constraints < input.txt` |
| `preserve` | Check that every fact, negation and scope word survived | `python3 /tmp/human_tool.py preserve [--strict] original.txt rewritten.txt` |
| `diff` | Change ratio between original and rewrite | `python3 /tmp/human_tool.py diff original.txt rewritten.txt` |
| `suggest` | Emit span-level co-writer suggestions | `python3 /tmp/human_tool.py suggest doc.md [--apply-replacements repl.json]` |
| `check-suggestions` | The four blocking suggestion gates | `python3 /tmp/human_tool.py check-suggestions suggestions.json` |
| `harvest` | Collect user-authored writing samples from chat transcripts and folders | `python3 /tmp/human_tool.py harvest SOURCE... -o candidates.json` |
| `harvest-classify` | Rank harvested candidates, flag suspected AI pastes | `python3 /tmp/human_tool.py harvest-classify --candidates candidates.json` |
| `profile` | Stylometric fingerprint of approved samples | `python3 /tmp/human_tool.py profile samples/ -o profile.json` |
| `card` | Layered voice card from profile and samples | `python3 /tmp/human_tool.py card --profile profile.json --samples samples/ --out . --name NAME --provenance` |
| `voice-score` | Distance of a draft from the profile against impostor writers | `python3 /tmp/human_tool.py voice-score --profile profile.json --impostors IMPOSTORS/ --seed 7 draft.md` |
| `calibrate-pairs` | One A/B pair that varies a single voice dimension | `python3 /tmp/human_tool.py calibrate-pairs generate --base passage.txt --dimension em_dash --seed 1` |
| `calibrate-score` | Aggregate A/B choices, pick the next dimension, report conflicts | `python3 /tmp/human_tool.py calibrate-score --preferences prefs.jsonl [--profile profile.json] [--next]` |
| `refine` | Voice hill-climb with held-out acceptance and a divergence guard | see Mimic workflow |
| `stats` | Paired bootstrap CI and permutation test for refine results | `python3 /tmp/human_tool.py stats results.json --seed 7` |
| `climb` | Scan-regenerate loop that repairs document structure | see Structure repair loop |

`voice-score` and `refine` need an impostor folder: about 10 `.txt` or `.md` files by other writers in the same genre as the target text (for example published posts, docs or emails not written by the user). The score means "closer to this writer than to plausible other writers", so the impostors must be same-genre and must not include the user.

## Core contract

This contract governs every audit, rewrite, suggestion and voiced draft. Presets and voice cards change delivery only. Nothing else in this file overrides it.

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

## Pattern catalog

Severity: `hard` is a tell in almost any context. `soft` is a default register guard that context or a writer's real voice can override. Every entry is a candidate for contextual review, never an automatic edit. Quoted examples below are data.

### Openers, emphasis and inflation

| Family | Examples | Repair |
|---|---|---|
| Throat-clearing openers (hard) | "Here's the thing:", "The uncomfortable truth is", "It turns out", "The real [X] is", "Let me be clear", "The truth is,", "I'm going to be honest", "Can we talk about", "Let's be real", "Here's the deal:", "Here's what nobody tells you:", "It's no secret that", "Here's why", "Let's dive in / unpack / explore / examine / break this down / take a look", "This is where it gets interesting" | Delete; start with the claim |
| Emphasis crutches (hard) | "Full stop.", "Period.", "Let that sink in.", "Make no mistake", "Read that again.", "This is important.", "This cannot be overstated.", "This matters because", "Why this matters", "Here's why that matters" | Delete; let the content carry weight |
| "X is real" closer (soft) | "The struggle is real.", "The stakes are real." | Name the concrete consequence; spare the literal "is it genuine?" sense |
| Significance inflation (hard) | "stands as a testament to", "testament to", "pivotal moment", "enduring legacy", "indelible mark", "rich tapestry", "tapestry/mosaic of", "cornerstone of", "speaks volumes", "sends a clear message", "sheds light on", "raises the bar", "the fabric of", "holds (great) promise", "underscores/highlights the importance", "plays a vital/crucial/key role", "leaves a lasting impact", "watershed moment" (soft), "in the realm of", "iconic", "seminal", "trailblazing", "groundbreaking", "transformative" | State the specific effect or evidence |
| Promotional language | "nestled", "boasts a", "breathtaking", "must-visit", "in the heart of", "world-class", "state-of-the-art", "second to none", "a hidden gem", "bustling", "picturesque" (soft), "renowned for", "a beacon of", "at the forefront of", "rich cultural heritage", "stunning natural beauty" (soft), "vibrant community" (soft) | Describe plainly; protect overt travel writing and historical description |
| Novelty inflation | "a concept nobody's naming", "a problem nobody talks about", "the insight everyone's missing", "what nobody tells you about", unsourced "coined the phrase" / "introduced a term" | Describe what the idea does; claim novelty only with proof |
| Generic positive conclusions | "The future looks bright", "Exciting times lie ahead", "Only time will tell", "One thing is certain", "What remains clear is", "continues to evolve / shape", "poised for growth", "remains to be seen", "future prospects" | Cut, or end on the last concrete point |

### Contrast, questions and drama

| Family | Examples | Repair |
|---|---|---|
| Binary contrast (hard) | "Not because X. Because Y.", "[X] isn't the problem. [Y] is.", "It feels like X. It's actually Y.", "Not X. But Y." | State Y directly |
| Negative parallelism (hard) | "Not only... but also", "It's not just about X, it's about Y", "Not merely X, but Y", "More than just X", "Beyond X, it also Y", "No X, no Y, just Z", "Not X. Rather, Y." | State the points directly; protect legal scope drafting |
| Contrastive definition (soft) | "X is a build step, not an output.", "X isn't a Y, it's a Z." | State the positive claim; exempt real corrections ("Use pnpm, not npm.", "Latency fell 40%, not 4%.", "The painting is real, not a forgery.") |
| Anti-slop register (soft) | "Not the tool. The team.", "Not the strategy. The execution." | Join into one varied sentence |
| Dramatic fragmentation | "[Noun]. That's it. That's the [thing].", "X. And Y. And Z.", "The ___ loop." as a standalone sentence, "X things. One thing." | Write complete sentences |
| Rhetorical setups | "What if [reframe]?", "Here's what I mean:", "Think about it:", "And that's okay." | Make the point directly |
| Self-answered questions (soft) | "Why does this matter? Because...", "What does this mean for...", "Why should you care?", "What's the takeaway?", "What's next?" | Replace with the answer |
| False concession | "While X is promising, Y remains a challenge", "Although X has made strides, Y is still an open question", "However, it is not without its challenges" | Name the actual tradeoff |
| Formulaic challenge sections | "Despite its [achievements], [X] faces challenges", headers "Challenges and Controversies", "Future Outlook", "Looking Ahead" | Fold real limitations into the body; drop the template section |
| Hedge stacks (soft) | "could potentially", "may possibly", "I think it's probably fair to say that perhaps" | Keep one hedge if the uncertainty is real; protect register hedges |
| Parenthetical hedging (soft) | "(and perhaps more importantly, ...)", "(arguably ...)", "(or, more precisely, ...)", "(and, increasingly, ...)" | Give the aside its own sentence or cut it |
| False ranges | "from X to Y, from A to B", "spanning everything from X to Y", repeated "whether X or Y" | Name the relevant items or the measured endpoints |
| Both-sidesism, redemption arc, over-determination, uniform emotional register | Judgment only, see Macro tells | |

### Attribution, agency and reader handling

| Family | Examples | Repair |
|---|---|---|
| Vague attribution | "Experts argue", "Studies show", "Research suggests", "Some critics", "Many believe", "It is widely regarded", "Observers note", "Analysts predict", "Industry reports suggest", bare clause-initial "Research indicates/shows" | Name the source or cut; attributed ("Research by the X group indicates") and possessive ("Our research shows") forms are clean |
| False agency (hard) | "the numbers speak for themselves", "the data tells a story", "paints a clear picture", "the results speak for themselves" | State the figure and what it shows |
| Tool anthropomorphism (soft) | Reflexive: "The suite defends itself.", "The rules update themselves.", "It graded its own reflection." Volitional on a standalone headline: "The bench decides which model does which job.", "It hunts instances, not word lists." | Name the mechanism ("The bench routes each job to a model"); ordinary technical register stays clean ("the parser reads the file", "the model learns the distribution", "the test cleans up after itself", "the gate fails the build") |
| Headline container agency (soft) | "Week 1 ends with a calibrated eval", "Demo day closes the cohort" | Name the completion criterion or result; literal boundaries ("Week 1 ends on Friday") are clean |
| Reader-steering and vague endorsement | "Here's what's interesting", "Here's what caught my eye", "Here's what stood out", "worth reading", "worth a look", "worth exploring", "worth your time", "worth paying attention to" | State the reason it matters |
| Reader-addressing flattery (soft) | "Whether you're a seasoned developer or just starting out", "In this article, we will explore" | Start with the point |
| Meta-commentary | "Hint:", "Plot twist:", "Spoiler:", "You already know this, but", "Let me explain", "To put it simply", "In other words", "If you think about it", "As I mentioned", "Pro tip", "Hot take", "Unpopular opinion", "X is a feature, not a bug" | Cut and say it directly |
| Performative sincerity | "I promise", "Trust me", "Believe me", "Honestly", "This is genuinely hard", "the million-dollar question", "The elephant in the room", "It begs the question", "It's a no-brainer", "Buckle up", "Food for thought" | Cut |
| Acknowledgment loops | "You're asking about", "To answer your question", "The question of whether" | Just answer |
| Reasoning-chain leaks | "Let me think step by step", "Breaking this down", "To approach this systematically", "Here's my thought process", "Working through this logically" | Conclusion first, evidence after |
| Chatbot artifacts (hard) | "I hope this helps", "Certainly!", "Great question!", "That's a great point", "Absolutely!", "Of course!", "Happy to help", "Let me know if you need anything else", "I'd be happy to", "I assure you", "I am open to any suggestions", "with the utmost care", "as an AI language model" | Delete |
| Knowledge-cutoff disclaimers (hard) | "as of my last knowledge update", "as of my knowledge cutoff", "based on my training data", "I don't have access to real-time", "based on available information" | Delete |
| Numbered-list inflation (soft) | "Here are 7 reasons", "Three key takeaways", "Five things to know", "Top seven" | Use a count only when the count matters |
| Conclusion and sequencing scaffolding | "In conclusion", "In summary", "To summarize", "Firstly / Secondly / Thirdly", "Ultimately," as an opener | Cut the scaffold word; lead with content |

### Slogan and template cadence (soft)

| Pattern | Example | Repair |
|---|---|---|
| Two-beat imperative slogan | "Emit 1,100 tokens. Ship 237KB." | Combine into one sentence |
| Repeated "<plural noun> that <verb>." fragments (2+ per document) | "Tools that ship. Teams that win." | Vary the structure |
| Numeric parallelism | "One X, N Y." | Rewrite as a normal sentence |
| Standalone slogan fragment line | "Four presets, one input." | Whole-line only; the same count inside a sentence is literal ("two bedrooms, one bath, and a den") |
| Standalone spec fragment line | "Eight criteria, scored 1 to 5." | Whole-line only |
| Headline slogan cadence (3+ per document) | "One command. A real URL." / "Reviewers click. The agent fixes." | One is voice, three is a template: vary the shapes |
| Abstraction ships inside | "The feedback loop ships inside the artifact." | State the mechanism |

### Jargon and AI vocabulary

Gated words fire only in their jargon collocation. The literal sense stays clean: "3:1 leverage" in finance, "a load-bearing wall", "delve into the mountain" in mining, "a wedge under the door", "substrate" in a lab, "notwithstanding the foregoing" in a contract.

| Avoid | Plain replacement |
|---|---|
| leverage (strengths, synergies, data, platform) | use, apply |
| navigate (challenges, the landscape, complexity) | handle, address, manage |
| delve into (the topic, the issue) | examine, look at |
| unpack (the idea, the argument) | explain, examine |
| harness (the power, the potential) | use, apply |
| foster (a culture, collaboration, innovation) | build, encourage |
| double down on (the strategy) | commit to, increase |
| bolster (the argument, the case) | support, strengthen |
| lean into | accept, commit to |
| landscape (business, tech, today's) | field, market, situation |
| game-changer, game changer | say what changes |
| synergy | cooperation |
| stakeholder buy-in / alignment | agreement of the people involved |
| deep dive | analysis, review |
| circle back, touch base | follow up, talk |
| move the needle | name the measured change |
| low-hanging fruit | easy fixes |
| on the same page | agreed |
| bandwidth (time) | time, capacity |
| level up | improve |
| value-add | benefit |
| thought leader | expert |
| best-in-class, cutting-edge | name the measured advantage |
| robust (soft), comprehensive (soft) | strong, thorough, complete; protect "robust error handling", "comprehensive visual survey" |
| utilize | use |
| facilitate | help, run |
| spearhead | lead |
| streamline | simplify |
| showcase | show |
| garner | get, earn |
| underscore | show |
| crucial, pivotal, paramount | important, or cut |
| load-bearing (point, claim, detail) | essential |
| wedge (into the market) | entry point, advantage |
| substrate for everything (soft) | foundation |

Single words over-represented in model output. Hard: delve, garner, interplay, intricate, tapestry, underscore, multifaceted, paramount, resonate(s) with, pertaining to, aforementioned, henceforth, whereby, therein, burgeoning, meticulous(ly), "at the intersection of", "double-edged sword", "strikes a balance", "treasure trove", "ever-evolving". Soft (flag when clustered): nuanced, myriad, plethora, encompass, moreover, furthermore, nevertheless, ubiquitous, emphasizing, enduring, vibrant, valuable (with no object), elucidate, delineate, underpin, unveil, seamless, invaluable, noteworthy, revolutionize, "new avenues", "warrants further investigation" (protect it in scientific text), "in recent years", "with the advent of", "taken together", "garnered significant attention", "a deeper understanding of".

### Filler and wordy phrases

| Phrase | Repair |
|---|---|
| "At its core", "In today's [X]", "In a world where", "In an era of", "At the end of the day", "The reality is", "With that said", "That being said", "All things considered", "By and large", "To be fair", "To be honest", "Needless to say", "It goes without saying", "It's clear that", "What's clear is", "A closer look", "Interestingly,", "Importantly,", "Crucially," | Cut |
| "It's worth noting / mentioning", "It is important to note that", "It should be noted that" | Cut and state the point |
| "The bottom line", "The key takeaway" | Cut and state the point |
| "When it comes to", "In terms of" | "For", or cut |
| "In order to" / "Due to the fact that" / "Is able to", "Has the ability to" | "To" / "Because" / "Can" |
| "At this point in time" / "In the event that" / "Prior to" / "Subsequent to" | "Now" / "If" / "Before" / "After" |
| "A large number of" / "The vast majority of" | "Many" / "Most" |
| "The fact that" | Restructure |

### Copula avoidance and -ing analyses

- "serves as a", "stands as a", "acts as a", "functions as a", "constitutes a" (when the complement is inflated, such as "a testament", "a beacon", "a game-changer"): use "is". "Serves as a kitchen" is literal and clean.
- Trailing participial clauses that fake analysis: ", highlighting...", ", showcasing...", ", underscoring...", ", fostering...", ", demonstrating...", ", reflecting...", ", signaling...", ", paving the way for...". Delete the clause; if the analysis matters, give it a sentence with actual reasoning. A participial ending on 35% or more of sentences is a document-level tell.

### Intensifiers and absolutes

Delete empty intensifiers when meaning survives: deeply, truly, fundamentally, inherently, simply, literally, essentially, incredibly, absolutely, extremely, really, very. Flag hyperbolic absolutes (always, never, everyone, nobody, everything, nothing, completely, totally, entirely, perfectly) only in rhetorical claims. Never touch an absolute that defines a rule, warning, contract term or measured fact.

### Punctuation and formatting

| Tell | Rule |
|---|---|
| Em dash (`—`) | Default zero in prose. An em dash before a reveal or as a dramatic pause is hard; two or more in one paragraph is always a flag. Use a comma, period, colon or parentheses. An en dash used as an em dash is the same tell. |
| Colon reveal | "The answer is:", "The key takeaway:", "The bottom line:", "The secret is:" are hard. Several colons per paragraph is soft. State the point directly. |
| Exclamation marks | More than one per several paragraphs, or one after every list item, is hard. |
| Bold | Bold on every key term, or bold inline pseudo-headers in body text: keep one or two per section. |
| Bold-label listicle | "**Label:** text" bullets standing in for prose (allowed under `--genre docs`). |
| Title Case in body text | "Digital Transformation Journey": lowercase unless it is a proper noun. |
| Emoji section headers | Decorative emoji standing in as headings. |
| Mixed quote styles | Curly and straight quotes mixed in one document suggests pasted model output. |

### Elegant variation

Rotating synonyms for one referent ("the company... the firm... the organization... the enterprise"), or for one verb ("said... stated... noted... remarked"). Repeat the natural word: repetition of key terms is normal English.

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

## Headings and slide titles

Write the title after the section has earned its point. A strong title names the test, mechanism, result, decision or completion criterion the reader should inspect.

Prefer: "The Week 1 capstone is a clean run with recorded agreement.", "Order, verbosity, and self-preference bias the judge.", "Each capstone must clear three gates.", "Can one packet reconstruct both products?"

Rewrite:

- Calendar or program containers delivering outcomes: "Week 1 ends with a calibrated eval".
- Tools, scores, data or packages given narrative or volitional agency: "Your judge is lying", "A score hides five failures", "The package outlives the cohort". For a bad evaluation, name the discrepancy or its cause ("One response receives conflicting labels"); "the judge gives a false verdict" keeps the false agency.
- Abstract uplift: "Taste becomes infrastructure", "Unlocking the power of clinical intelligence".
- Generic handles that leave the body to do all the work: "Architecture", "Proof plan", "Three pillars".
- Repeated counting or journey frames that describe the deck instead of the claim.

This is semantic, not a subject-verb ban: "Examples calibrate the judge" and "The gate fails the build" describe mechanisms and stay.

## Rewrite workflow

Set `$INPUT` to the source and `$OUTPUT` to your rewrite. Save both to files for the gates.

Pass 1, diagnose:

1. Read the whole source first. Note what each sentence contributes and every concrete defect.
2. Extract the constraints: `python3 /tmp/human_tool.py constraints < original.txt`.
3. Scan for candidates the reading missed:

```bash
python3 /tmp/human_tool.py scan < original.txt
python3 /tmp/human_tool.py structure < original.txt
python3 /tmp/human_tool.py silhouette < original.txt
python3 /tmp/human_tool.py readability < original.txt
```

4. Read the selected preset for delivery only. A preset cannot authorize a finding.
5. Classify every candidate span as confirmed or protected. If nothing is confirmed, return the source exactly and stop.

Pass 2, repair: apply the Rewrite rules to confirmed sentences only. Undo any edit that changes a fact, meaning, register, attribution or protected domain phrase.

Validate: run the gate battery (Validation section). Return the cleaned text only, unless the user asked for the strict analysis block.

## Audit workflow

Change nothing. Run `scan`, `structure`, `silhouette` and `readability` on the input, then read every sentence yourself: the scanners are necessary, not sufficient. Re-read negations, scope and certainty. Report each issue by quoted span, category, severity and why it reads as machine-written, separating clear problems from register-dependent judgment calls, and list protected spans with the reason they stay.

## Cleanup workflow

Co-writer mode: surface edits for the user to accept or reject. Never apply them silently, and never run as a background daemon.

```bash
python3 /tmp/human_tool.py suggest doc.md > suggestions.json
python3 /tmp/human_tool.py suggest doc.md --apply-replacements repl.json > suggestions.json
python3 /tmp/human_tool.py check-suggestions suggestions.json
```

- `suggest` emits ordered, non-overlapping suggestions `{span, severity, category, rationale, suggested_replacement, phrased_as_question}` with `suggested_replacement` left null.
- You write the replacements into `repl.json` and merge them with `--apply-replacements`.
- Hard findings become direct replacements. Soft findings are register-dependent, so their rationale is a question (`phrased_as_question: true`).
- `check-suggestions` is blocking. Every replacement must pass all four gates or be dropped:
  - `span-minimality`: an edit changes only its own span; a whole-sentence rewrite fails.
  - `replacement-scanner`: each replacement passes both scanners on its own and adds no new violation in context.
  - `accept-all`: applying every suggestion yields a document that passes both scanners and preserves every constraint of the original.
  - `span-overlap`: spans may not overlap.

## Teach workflow

Build a reusable voice from a writer's samples. You drive it end to end; the user supplies only approvals and answers, never a directory or a command. Store everything under `.human/voice/<name>/` in the working directory and keep that folder out of version control unless the user decides otherwise.

1. Gather samples. If the user offers none, harvest them from their chat transcripts and from folders they name as their own writing. Supported transcript sources are Claude Code (`~/.claude/projects/**/*.jsonl`) and Codex CLI or Desktop (`~/.codex/sessions/**/rollout-*.jsonl`), detected by content shape:

```bash
python3 /tmp/human_tool.py harvest SOURCE [SOURCE...] -o candidates.json
python3 /tmp/human_tool.py harvest-classify --candidates candidates.json --mode heuristic
```

   The adapters keep only explicitly user-authored turns. They drop assistant, developer, tool and reasoning turns, and injected content such as a pasted `AGENTS.md` or an environment banner (counted as `instruction-injection`). Every kept candidate runs through the scanners: a hard hit, or two or more scanner categories, marks it `suspect_ai`, ranked last. Show the ranked candidates with sources and flags. The user approves or rejects each one. Never auto-approve a `suspect_ai` candidate: human review is the defense against assistant text leaking into the voice. Heavy "um/uh" text is marked `dictated` and can still be kept. Harvesting stays local. Copy only approved samples into `.human/voice/<name>/samples/` as `.txt` or `.md` (convert other formats first).

2. Check the sample requirements: at least 5 documents and 2,000 to 3,000 words in the same genre as the target writing. Thinner or cross-genre samples set `low_confidence`. Tell the user the voice is provisional and ask for more same-genre samples before trusting a mimic. Do not teach on blog posts and then score legal memos.

3. Build the profile and card:

```bash
python3 /tmp/human_tool.py profile samples/ -o profile.json
python3 /tmp/human_tool.py card --profile profile.json --samples samples/ --out . --name NAME --provenance
```

   The profile is the machine fingerprint the scorer uses (character 3-grams, function-word rates, sentence-length distribution, punctuation, contractions, lexical diversity, word length). The card is what the writing model follows: `card.md` (under 300 words: rhythm, contraction habits with real examples, punctuation used and avoided, top openers, a Never list, and an index of situation sheets) plus one `card/<situation>.md` sheet per covered situation with 1 to 3 verbatim snippets and measured markers. `card` refuses (exit 2) when the profile does not describe the supplied samples, so a stale profile cannot drive a card. `--provenance` writes `provenance.json` (per-sample sha256, word counts, low-confidence flag).

4. Close coverage gaps. A situation with no sample evidence gets no sheet and is listed as Uncovered: the card never invents a voice. `card --coverage` prints the coverage matrix without writing files. Ask only for the situations the target writing needs:

| Situation | Ask the user |
|---|---|
| explaining-technical | "Share something you wrote explaining how a thing works or why it behaves that way." |
| anecdote | "Share a few sentences telling a small story about something that happened to you." |
| argument | "Share something where you defended a claim." |
| disagreement | "Share something where you pushed back on an idea." |
| praise | "Share something where you recommended something you liked." |
| hedging-uncertainty | "Share something where you were unsure and said so." |
| numbers-data | "Share something you wrote that works with quantities or measurements." |
| addressing-reader | "Share a note or instructions written to a reader." |

   Openings and closings are covered as soon as one document exists.

5. Calibration game, when samples stay thin. Five dimensions can be varied by deterministic, fact-preserving transforms: `contractions`, `em_dash`, `sentence_length`, `connectives`, `staccato`.
   - Pick 60 to 150 word base passages from the user's own approved samples.
   - Ask `calibrate-score --next` which dimension to play, then generate a pair with `calibrate-pairs generate --base passage.txt --dimension DIM --seed N`, raising the seed each round. Exit 3 means the passage cannot express that dimension: pick another passage or dimension.
   - Show the two texts as A and B without naming the dimension. Randomize which side is shown first with a seeded shuffle per round and record the mapping. Accept "neither".
   - Append one line per round to `.human/voice/<name>/preferences.jsonl`: `{"pair_id", "dimension", "choice": "a|b|neither", "ts", "a_label", "b_label"}`, taking the labels from the generator's `transform_applied`. Re-recording the same `pair_id` is safe (latest wins).
   - Stop a dimension at confidence 0.7 or 9 observations. Below 5 observations it reports `insufficient`; a `tied` result means play more rounds.
   - With a profile present, run `calibrate-score --preferences prefs.jsonl --profile profile.json`. Show every conflict between a stated preference and a measured value to the user verbatim and let them choose. Never resolve one silently.
   - A variant may trip the scanner (a staccato pole reads as `anti_slop_register`). Do not hide that pole. If the user keeps choosing it, tell them once that their preference overrides the default register guard, and mark that dimension "user-preference overrides register guard" on the card. Card claims from the game carry provenance `stated-preference`; claims from samples carry `measured-from-samples`.

6. Prove the loop with a scored demo: mimic one paragraph, run `voice-score` and the scanners, and show the results. A voiced demo that trips a removal gate fails; do not ship it with an excuse.

## Mimic workflow

1. Load `card.md` (always) and the one `card/<situation>.md` sheet the task needs.
2. Draft or rewrite in that voice. Follow measured markers and verbatim snippets. Do not invent a habit the samples do not support.
3. Run every removal gate on the output (`scan`, `structure`, `readability`, `preserve` and `diff` against the original draft).
4. Score the voice: `python3 /tmp/human_tool.py voice-score --profile profile.json --impostors IMPOSTORS/ --seed 7 --samples samples/ draft.md`.

The rule: a mimic that scores well on voice but trips a removal gate is rejected. Voice never buys an exemption from the core contract. Meaning preservation against the original draft is its own hard gate and is never blended into the voice score.

Voice check ("does this sound like me?"): run `voice-score` only and change nothing. Report the composite (lower is closer to the writer), the GI rank, and the two or three metric deltas that explain the score in plain words ("your sentences run longer than usual; contractions match"). Check drafts often; commission rewrites rarely.

Scoring: composite = `0.5 * (1 - GI) + 0.5 * zsum`. GI (General Impostors) is the share of random feature-subset trials in which the draft beats every impostor at resembling the profile. `zsum` is the weighted per-feature distance normalized against the impostor pool and clipped to plus or minus 3. Both halves reward beating plausible other writers, which is what defeats a draft stuffed with the writer's markers. Drafts under 150 words are `low_confidence`. `--samples` adds a copy gate against verbatim lifting. The composite is a guide, not an oracle: treat per-draft deltas as the signal and under-claim.

Refine loop, only when single passes keep landing short:

```bash
python3 /tmp/human_tool.py refine --samples samples/ --draft draft.md --out OUT --impostors IMPOSTORS/ --seed 1 --candidates-dir CANDS/
```

- Samples are split by document into a retrieval pool A (about 60%) and a held-out acceptance split DEV (about 40%). Fewer than 5 documents is refused.
- Agent-hosted mode (works on any platform): for iteration `i`, write 2 to 4 candidates to `CANDS/iter<i>/*.md` yourself, each drafted from the draft, the A-split card, the 2 nearest A samples and the previous iteration's directives in `OUT/report.json`, then rerun the command. Alternatively pass `--generate-cmd "<your CLI that reads a prompt on stdin and prints a draft>"` and omit `--candidates-dir`; the default command is `claude -p`.
- Hard gates discard a candidate regardless of score: scanner-clean, structure-clean, draft-to-candidate preservation, no copying from A (4-gram and longest-common-substring), and at least 150 words. Survivors are scored on DEV; an iteration is accepted only if DEV improves by `--min-delta`, and the best result never regresses.
- It stops at the iteration cap, after `--patience` iterations without a DEV gain, or on divergence: the A score improving while DEV worsens for two consecutive iterations. Divergence is the reward-hacking signature (fitting the samples' topics, not the writer's style); the loop halts and sets `reward_hacking_warning`.
- Outputs: `OUT/final.md`, the amended card `OUT/voice-card.refined.md` and `OUT/report.json`. Compare against zero-shot, few-shot and retrieval few-shot baselines on the same drafts; refine must beat retrieval few-shot to earn its cost.
- Claim a win only when `stats` on the paired per-item results shows a bootstrap CI lower bound above 0 and p below 0.05.

| Failure | Symptom | Caught by |
|---|---|---|
| Topic bleed | copying what samples are about, not how they read | divergence guard |
| Verbatim copying | lifting sample phrasing | copy gate |
| Register lock | latching onto one sample's register | DEV split |
| Reward hacking | pool score rises while held-out score falls | divergence guard |
| Slop reintroduced | AI tells return in voiced prose | removal gates |

## Structure repair loop

When `structure` or `silhouette` findings remain after a rewrite, feed the exact findings back as targeted directives instead of asking a model to self-check document shape (single-pass self-review rarely fixes macro structure).

```bash
python3 /tmp/human_tool.py climb --prompt-file task.txt --out OUT --generate-cmd "<your CLI>" --max-rounds 4 --genre prose
```

Each round scans the latest draft, turns findings into instructions that name the paragraph, opener or metric, and regenerates. A preservation guard aborts the round that drops a fact (exit 4). Exit 0 means converged, exit 3 means the round cap was reached while still dirty. Without a CLI generator, run the same loop by hand: scan, write directives that cite each finding, regenerate, re-scan, and stop when clean or after 4 rounds. Re-read negations, conditions, scope, certainty and party relationships after every round.

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

## Presets

A preset changes delivery inside a confirmed finding's sentence. It never adds facts, opinions, examples, anecdotes, certainty or personality the source lacks. When a proposed edit adds a comparison, judgment, promise or causal claim, reject it. When the case for the edit is uncertain, keep the source.

| Preset | Delivery | Best for |
|---|---|---|
| `crisp` (default) | Direct and economical in the source's register. Remove a formulaic opener when the sentence works without it; replace an inflated abstraction with the source's concrete fact; prefer a plain verb to a vague verb-noun phrase. Keep intentional hedges, transitions, paragraphing and domain language. Do not impose sentence-length targets, active voice or short paragraphs on already-natural prose. | Technical writing, documentation |
| `warm` | Conversational, not casual. Natural contractions, occasional "you" when the source addresses a reader, light transitions, a soft landing instead of an abrupt end. Use only supplied names, numbers, timing and actions; make an abstract purpose plain by saying what the named actor does. Avoid forced intimacy ("Hey friend!"), stacked exclamation marks, "super/awesome/amazing", "I hope this email finds you well". | Emails, blog posts |
| `expert` | Confident to the degree the source supports. Assertion, then evidence, then implication or caveat. Show knowledge through the source's specific contexts, numbers and named examples; never announce credentials ("In my extensive experience", "Trust me"). Keep every hedge the source needs. | Articles, analysis |
| `story` | Narrative order the source already has: scene, tension, resolution. Use the source's concrete details and quotes, cut "Let me tell you a story" and "And that's when I realized", and end on the image or moment instead of an explained moral. Never invent a scene, name, dialogue or number. | Case studies, personal posts |

Voice without invention: clean text can still read as anonymous (no stance, uniform rhythm, no specifics). Add first person, opinion, anecdote or sensory detail only when the author supplies them or a taught voice card records them. In impersonal copy (reference docs, third-party announcements) never fabricate an "I" or a lived experience: an invented anecdote is a louder tell than the slop it replaces. Dropping habitual hedges is fine; dropping load-bearing scope or certainty is not.

## Validation

After every rewrite or voiced draft:

```bash
python3 /tmp/human_tool.py preserve original.txt rewritten.txt
python3 /tmp/human_tool.py scan < rewritten.txt
python3 /tmp/human_tool.py structure < rewritten.txt
python3 /tmp/human_tool.py silhouette < rewritten.txt
python3 /tmp/human_tool.py readability < rewritten.txt
python3 /tmp/human_tool.py diff original.txt rewritten.txt
```

Block on: preservation loss; any introduced hard or `anti_slop_register` hit; unjustified structural damage; corroborated or hard silhouette damage; staccato; and, in strict mode, a rubric score under 32/40. Use `preserve --strict` for legal, medical, security or scientific text. Pre-existing soft cadence and uncorroborated soft silhouette warnings are advisory. Then re-read negations, conditions, scope, certainty and party relationships yourself.

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

## Limits

- English only. Other languages get detection and a decline.
- The scanners propose candidates. Context decides. A clean scan proves neither human authorship nor good writing, and the gates cannot guarantee that every defect is gone.
- In paired tests against the same model working without these rules, this approach found and repaired more issues, but it did not reach the precision and collateral-damage bar for whole documents. Prefer no-ops, keep edits span-minimal and always run the preservation gate.
- Voice scores are guides. Even strong authorship verification has a ceiling; under-claim.
- Harvested transcripts and voice folders are private: keep them local.

## Embedded tool source

Extract this block to `/tmp/human_tool.py` as described in the setup section. It is one standard-library Python file: a short loader at the top runs each bundled module in its own namespace, so the module sections below the loader never execute as top-level code.

````python
#!/usr/bin/env python3
"""human_tool: deterministic scanners, preservation gates and voice tools for the `human` skill.

Usage: python3 human_tool.py <command> [args]   (python3 human_tool.py --help lists commands)
Standard library only, Python 3.9+. Every command prints JSON; most exit 1 when they flag.
"""
import __future__, inspect, sys, types
from pathlib import Path

COMMANDS = {
    "scan": "banned_phrase_scan",
    "structure": "structure_scan",
    "silhouette": "silhouette_scan",
    "readability": "readability_metrics",
    "constraints": "extract_constraints",
    "preserve": "validate_preservation",
    "diff": "diff_check",
    "suggest": "suggest",
    "check-suggestions": "check_suggestions",
    "profile": "voice_profile",
    "card": "voice_card",
    "voice-score": "voice_score",
    "calibrate-pairs": "calibrate_pairs",
    "calibrate-score": "calibrate_score",
    "harvest": "harvest_samples",
    "harvest-classify": "harvest_classify",
    "refine": "run_mimic_refine",
    "stats": "mimic_stats",
    "climb": "run_structure_climb"
}


def _load_modules():
    text = Path(__file__).read_text(encoding="utf-8")
    parts = text.split("\n# ==== module: ")[1:]
    for part in parts:
        name, _, src = part.partition(" ====\n")
        mod = types.ModuleType(name)
        mod.__file__ = __file__
        sys.modules[name] = mod
        mod.__dict__["__builtins__"] = __builtins__
        sources[name] = (mod, src)


sources = {}


def _ensure(name):
    mod, src = sources[name]
    if not getattr(mod, "_human_loaded", False):
        mod._human_loaded = True
        flags = __future__.annotations.compiler_flag
        exec(compile(src, f"human_tool:{name}", "exec", flags=flags, dont_inherit=True), mod.__dict__)
    return mod


def main(argv):
    if not argv or argv[0] in {"-h", "--help"} or argv[0] not in COMMANDS:
        print(__doc__)
        print("commands: " + ", ".join(COMMANDS))
        return 0 if argv and argv[0] in {"-h", "--help"} else 2
    _load_modules()
    # Resolve cross-module imports by executing every bundled module once, in order.
    import builtins
    real_import = builtins.__import__

    def bundled_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in sources:
            return _ensure(name)
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = bundled_import
    cmd, args = argv[0], argv[1:]
    mod = _ensure(COMMANDS[cmd])
    sys.argv = [f"human_tool.py {cmd}"] + args
    fn = mod.main
    rc = fn(args) if inspect.signature(fn).parameters else fn()
    return rc or 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

# Bundled modules follow. The loader above executes each section in its own module;
# nothing below runs at import time of this file.

# ==== module: _lang ====
"""Shared cheap English-detection helpers for banned_phrase_scan.py,"""
import re
ENGLISH_FUNCTION_WORDS = frozenset({'the', 'and', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'that', 'it', 'for', 'with', 'on', 'this', 'but', 'not', 'you', 'have', 'be', 'as', 'at', 'or', 'we', 'they', 'will', 'would', 'there', 'their', 'what', 'which', 'when', 'from', 'been', 'has', 'had', 'its', 'an', 'by', 'our', 'your', 'if', 'than', 'then', 'them', 'these', 'those', 'about', 'into', 'over', 'after', 'before', 'how', 'why', 'where', 'who', 'can', 'could', 'should', 'do', 'does', 'did', 'so', 'out', 'just', 'more', 'most', 'some', 'such', 'only', 'also', 'because', 'while', 'between', 'through', 'during', 'being'})

def english_function_share(text: str) -> float:
    tokens = re.findall("[a-z']+", text.lower())
    if not tokens:
        return 1.0
    hits = sum((1 for t in tokens if t in ENGLISH_FUNCTION_WORDS))
    return hits / len(tokens)

def is_probably_english(text: str, threshold: float=0.1, min_tokens: int=15) -> bool:
    tokens = re.findall("[a-z']+", text.lower())
    if len(tokens) < min_tokens:
        return True
    return english_function_share(text) >= threshold

def words(text: str) -> list[str]:
    return re.findall("[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text.lower())

def strip_markdown_for_prose(text: str, *, blank_blockquotes: bool=False, strip_bold: bool=False) -> str:
    text = re.sub('```[\\s\\S]*?```', '\n\n', text)
    kept = []
    for line in text.splitlines():
        if blank_blockquotes:
            if re.match('\\s*>', line) or re.match('\\s{0,3}#{1,6}\\s+', line):
                kept.append('')
                continue
        elif re.match('\\s{0,3}#{1,6}\\s+', line):
            kept.append('')
            continue
        line = re.sub('^\\s*[-*+]\\s+', '', line)
        line = re.sub('^\\s*\\d+[.)]\\s+', '', line)
        if strip_bold:
            line = re.sub('\\*\\*([^*]+)\\*\\*', '\\1', line)
        kept.append(line)
    return '\n'.join(kept)

def paragraphs(text: str, *, blank_blockquotes: bool=False, strip_bold: bool=False) -> list[str]:
    stripped = strip_markdown_for_prose(text, blank_blockquotes=blank_blockquotes, strip_bold=strip_bold)
    return [re.sub('\\s+', ' ', p).strip() for p in re.split('\\n\\s*\\n', stripped) if p.strip()]

# ==== module: readability_metrics ====
"""Calculate readability metrics for transformed text."""
import argparse
import sys
import re
import json
from collections import Counter
from typing import TypedDict

class ReadabilityMetrics(TypedDict):
    flesch_kincaid_grade: float
    flesch_reading_ease: float
    sentence_count: int
    word_count: int
    avg_sentence_length: float
    sentence_length_variance: float
    min_sentence_length: int
    max_sentence_length: int
    consecutive_similar_length: int
    word_repetition_score: float
    top_repeated_words: list[tuple[str, int]]
    paragraph_count: int
    avg_paragraph_length: float
    flags: list[str]

def count_syllables(word: str) -> int:
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    vowels = 'aeiouy'
    count = 0
    prev_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and (not prev_is_vowel):
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith('e') and count > 1:
        count -= 1
    if word.endswith('le') and len(word) > 2 and (word[-3] not in vowels):
        count += 1
    return max(1, count)

def split_sentences(text: str) -> list[str]:
    parts = re.split('([.!?]["”]?)\\s+(?=["“]?[A-Z])', text)
    sentences = []
    current = ''
    for part in parts:
        if re.match('[.!?]["”]?$', part):
            current += part
            sentences.append(current.strip())
            current = ''
        else:
            current += part
    if current.strip():
        sentences.append(current.strip())
    return [s.strip() for s in sentences if s.strip()]

def split_staccato_units(text: str) -> list[str]:
    units = re.split('\\s*[—;]\\s*|(?<=[.!?])\\s+', text)
    return [u.strip() for u in units if u.strip()]

def split_words(text: str) -> list[str]:
    text = re.sub('[^\\w\\s-]', ' ', text)
    words = text.lower().split()
    return [w for w in words if w]

def calculate_metrics(text: str) -> ReadabilityMetrics:
    sentences = split_sentences(text)
    words = split_words(text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not sentences or not words:
        return {'flesch_kincaid_grade': 0, 'flesch_reading_ease': 0, 'sentence_count': 0, 'word_count': 0, 'avg_sentence_length': 0, 'sentence_length_variance': 0, 'min_sentence_length': 0, 'max_sentence_length': 0, 'consecutive_similar_length': 0, 'word_repetition_score': 0, 'top_repeated_words': [], 'paragraph_count': len(paragraphs), 'avg_paragraph_length': 0, 'flags': ['Empty or invalid text']}
    sentence_count = len(sentences)
    word_count = len(words)
    syllable_count = sum((count_syllables(w) for w in words))
    sentence_lengths = [len(split_words(s)) for s in sentences]
    avg_sentence_length = word_count / sentence_count if sentence_count else 0
    if len(sentence_lengths) > 1:
        mean = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum(((x - mean) ** 2 for x in sentence_lengths)) / len(sentence_lengths)
    else:
        variance = 0
    consecutive_similar = 0
    max_consecutive = 0
    for i in range(1, len(sentence_lengths)):
        if abs(sentence_lengths[i] - sentence_lengths[i - 1]) <= 3:
            consecutive_similar += 1
            max_consecutive = max(max_consecutive, consecutive_similar)
        else:
            consecutive_similar = 0
    staccato_lengths = [len(split_words(s)) for s in split_staccato_units(text)]
    staccato_run = 0
    max_staccato_run = 0
    for length in staccato_lengths:
        if length <= 5:
            staccato_run += 1
            max_staccato_run = max(max_staccato_run, staccato_run)
        else:
            staccato_run = 0
    avg_syllables_per_word = syllable_count / word_count if word_count else 0
    flesch_reading_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    flesch_kincaid_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'not', 'no', 'yes', 'if', 'then', 'else', 'so', 'as', 'than', 'just'}
    content_words = [w for w in words if w not in stop_words and len(w) > 2]
    word_freq = Counter(content_words)
    repeated_words = {w: c for w, c in word_freq.items() if c >= 3}
    repetition_score = sum(repeated_words.values()) / len(content_words) * 100 if content_words else 0
    top_repeated = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    para_lengths = [len(split_words(p)) for p in paragraphs]
    avg_para_length = sum(para_lengths) / len(para_lengths) if para_lengths else 0
    flags: list[str] = []
    if flesch_kincaid_grade > 12:
        flags.append(f'High reading level ({flesch_kincaid_grade:.1f} grade)')
    if variance < 10 and sentence_count > 3:
        flags.append('Low sentence length variance (monotonous rhythm)')
    if max_consecutive >= 3:
        flags.append(f'{max_consecutive}+ consecutive similar-length sentences')
    if repetition_score > 15:
        flags.append(f'High word repetition ({repetition_score:.1f}%)')
    if avg_sentence_length > 25:
        flags.append(f'Long average sentence length ({avg_sentence_length:.1f} words)')
    if avg_sentence_length < 8 and sentence_count > 3:
        flags.append('Very short sentences (may feel choppy)')
    if max_staccato_run >= 3:
        flags.append(f'Staccato cadence: {max_staccato_run} consecutive tiny sentences (anti-slop AI tell)')
    elif avg_sentence_length < 6 and sentence_count >= 2:
        flags.append(f'Staccato cadence (avg {avg_sentence_length:.1f} words/sentence — anti-slop AI tell)')
    if max(sentence_lengths) - min(sentence_lengths) < 5 and sentence_count > 5:
        flags.append('Sentences all similar length (AI tell)')
    return {'flesch_kincaid_grade': round(flesch_kincaid_grade, 1), 'flesch_reading_ease': round(flesch_reading_ease, 1), 'sentence_count': sentence_count, 'word_count': word_count, 'avg_sentence_length': round(avg_sentence_length, 1), 'sentence_length_variance': round(variance, 1), 'min_sentence_length': min(sentence_lengths) if sentence_lengths else 0, 'max_sentence_length': max(sentence_lengths) if sentence_lengths else 0, 'consecutive_similar_length': max_consecutive, 'word_repetition_score': round(repetition_score, 1), 'top_repeated_words': top_repeated, 'paragraph_count': len(paragraphs), 'avg_paragraph_length': round(avg_para_length, 1), 'flags': flags}

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Calculate readability metrics for transformed text.')
    parser.add_argument('path', nargs='?', help='Path to input text file (default: read stdin)')
    return parser.parse_args(argv)

def main() -> None:
    args = parse_args(sys.argv[1:])
    if args.path:
        try:
            with open(args.path, 'r', errors='replace') as f:
                text = f.read()
        except OSError as e:
            print(json.dumps({'error': f'Could not read input: {e}'}))
            sys.exit(2)
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not text.strip():
        print(json.dumps({'error': 'No input provided'}))
        sys.exit(1)
    metrics = calculate_metrics(text)
    print(json.dumps(metrics, indent=2))
    sys.exit(1 if metrics['flags'] else 0)
if __name__ == '__main__':
    main()

# ==== module: structure_scan ====
"""Scan prose for macro-structure AI-writing patterns."""
import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _lang import ENGLISH_FUNCTION_WORDS, english_function_share, is_probably_english, paragraphs as _prose_paragraphs, words
from readability_metrics import split_sentences
STOPWORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'it', 'its', 'this', 'that', 'these', 'those', 'we', 'you', 'they', 'i', 'he', 'she', 'as', 'than', 'if', 'then', 'so', 'not', 'no', 'yes', 'into', 'over', 'under'}
CONNECTIVE_OPENERS = re.compile('^(however|moreover|furthermore|additionally|in addition|overall|consequently|nevertheless)\\b', re.I)
EVERY_OPENER_RE = re.compile("^every\\s+[a-z][\\w'-]*\\s+(?:is|are|was|were|be|been|being|has|have|had|do|does|did|can|will|shall|must|should|would|may|might|[a-z]+(?:s|ed))\\b", re.I)
SIGNPOST_RE = re.compile("\\b(first,|next,|having (?:covered|established)|in (?:this|the following|the next) section|as (?:mentioned|noted) (?:above|earlier)|let us turn|let's turn)\\b", re.I)
CLOSER_RE = re.compile(',\\s+(ensuring|highlighting|reflecting|allowing|enabling|underscoring|showcasing|emphasizing|fostering|driving|paving|reinforcing|solidifying|demonstrating|contributing to)\\b[^.!?]*[.!?\\"]?$', re.I)
CODA_START_RE = re.compile("^(ultimately,|in the end,|in conclusion|as we've seen|only time will tell|remember,|the future\\b)", re.I)
BOLD_COLON_RE = re.compile('^\\s*[-*+]?\\s*\\*\\*[^*]{1,40}\\*\\*\\s*:', re.M)

def prose_paragraphs(text: str) -> list[str]:
    return _prose_paragraphs(text, blank_blockquotes=True)

def cv(values: list[int]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    return math.sqrt(sum(((v - mean) ** 2 for v in values)) / len(values)) / mean

def content_bigrams(text: str) -> set[tuple[str, str]]:
    toks = [w for w in words(text) if len(w) > 3 and w not in STOPWORDS]
    return set(zip(toks, toks[1:]))

def triad_count(text: str) -> int:
    return len(re.findall('\\b[A-Za-z][A-Za-z-]+,\\s+[A-Za-z][A-Za-z-]+,\\s+and\\s+[A-Za-z][A-Za-z-]+\\b', text))

def flag(metric: str, value: float | int, threshold: str, detail: str, suggestion: str) -> dict:
    return {'metric': metric, 'value': value, 'threshold': threshold, 'severity': 'soft', 'detail': detail, 'suggestion': suggestion}
GENRE_SUPPRESSIONS = {'docs': {'bold_colon_listicle'}, 'social': {'one_line_staccato'}}

def scan(text: str, genre: str='prose') -> dict:
    paragraphs = prose_paragraphs(text)
    prose_text = '\n\n'.join(paragraphs)
    sentences = split_sentences(prose_text)
    sentence_lengths = [len(words(s)) for s in sentences]
    prose_words = words(prose_text)
    para_lengths = [len(words(p)) for p in paragraphs]
    metrics = {'sentence_burstiness': round(cv(sentence_lengths), 3), 'summary_sandwich': 0.0, 'paragraph_cv': round(cv(para_lengths), 3), 'sentence_mean_len': round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0, 'triad_density': round(triad_count(prose_text) / len(prose_words) * 1000, 3) if prose_words else 0, 'em_dash_per_1k': round(text.count('—') / len(prose_words) * 1000, 3) if prose_words else 0, 'bold_colon_listicle_count': len(BOLD_COLON_RE.findall(text)), 'one_line_staccato_share': 0.0, 'connective_paragraph_openers': 0, 'every_template_openers': 0, 'signpost_density': 0.0, 'opener_unique_ratio': 0.0, 'top_opener_share': 0.0, 'max_consecutive_opener': 0, 'participial_closer_share': 0.0, 'conclusion_coda': False}
    flags = []
    if len(paragraphs) >= 2:
        first = content_bigrams(paragraphs[0])
        last = content_bigrams(paragraphs[-1])
        union = first | last
        metrics['summary_sandwich'] = round(len(first & last) / len(union), 3) if union else 0.0
    if len(sentences) >= 8 and metrics['sentence_burstiness'] < 0.55:
        flags.append(flag('sentence_burstiness', metrics['sentence_burstiness'], '< 0.55 over at least 8 prose sentences', 'Sentence lengths are unusually uniform for running prose.', 'Vary sentence length and cadence; if this is formal reference prose, review before treating it as blocking.'))
    if len(paragraphs) >= 3:
        coda = bool(CODA_START_RE.search(paragraphs[-1]))
        if not coda:
            coda = len(content_bigrams(paragraphs[0]) & content_bigrams(paragraphs[-1])) >= 2
        metrics['conclusion_coda'] = coda
        if coda:
            flags.append(flag('conclusion_coda', 1, 'last paragraph starts with a stock coda or repeats 2+ first-paragraph content bigrams', 'The ending reads like a recap/moral coda instead of a concrete final point.', 'Cut the wrap-up or end on a specific fact; if this is an abstract or executive summary, judge the genre before changing it.'))
    if metrics['bold_colon_listicle_count'] >= 3 and 'bold_colon_listicle' not in GENRE_SUPPRESSIONS.get(genre, set()):
        flags.append(flag('bold_colon_listicle', metrics['bold_colon_listicle_count'], '>= 3 bold-label colon lines', 'The raw Markdown has repeated bold-label listicle formatting.', 'Convert to prose or plain bullets; if this is a reference doc, rerun with --genre docs.'))
    if paragraphs:
        one_line = 0
        for p in paragraphs:
            ps = split_sentences(p)
            if len(ps) == 1 and len(words(ps[0])) < 12:
                one_line += 1
        metrics['one_line_staccato_share'] = round(one_line / len(paragraphs), 3)
        if len(paragraphs) >= 6 and metrics['one_line_staccato_share'] > 0.6 and ('one_line_staccato' not in GENRE_SUPPRESSIONS.get(genre, set())):
            flags.append(flag('one_line_staccato', metrics['one_line_staccato_share'], '> 0.60 over at least 6 paragraphs', 'Most paragraphs are short single-sentence beats.', 'Merge related beats and vary paragraph length; if this is social copy, rerun with --genre social.'))
    connective = sum((1 for p in paragraphs if CONNECTIVE_OPENERS.search(p)))
    metrics['connective_paragraph_openers'] = connective
    if connective >= 3 or (len(paragraphs) >= 8 and connective / len(paragraphs) > 0.4):
        flags.append(flag('connective_paragraph_openers', connective, '>= 3 paragraphs or > 40% of 8+ paragraphs', 'Paragraphs repeatedly open with formal transition words.', 'Replace scaffold openers with specific topic sentences; academic prose may justify some connectors.'))
    every_openers = sum((1 for p in paragraphs if EVERY_OPENER_RE.search(p)))
    metrics['every_template_openers'] = every_openers
    if every_openers >= 2:
        flags.append(flag('every_template_openers', every_openers, ">= 2 paragraphs opening 'Every <noun> <verb>'", "Paragraphs repeatedly open on the 'Every ___ is/does ...' template.", 'Vary the paragraph openings; a repeated Every-template is a machine rhythm tell even when each sentence is fine on its own.'))
    if prose_words:
        signposts = len(SIGNPOST_RE.findall(prose_text))
        metrics['signpost_density'] = round(signposts / len(prose_words) * 100, 3)
        if len(prose_words) >= 150 and metrics['signpost_density'] > 0.6:
            flags.append(flag('signpost_density', metrics['signpost_density'], '> 0.6 per 100 prose words, minimum 150 words', 'The text over-explains its own structure.', 'Remove roadmap language unless the genre is a textbook, legal brief, or long guide.'))
    if len(sentences) >= 5:
        openers = []
        for s in sentences:
            ws = words(s)
            if not ws:
                continue
            openers.append(ws[0])
        enumeration = {'the', 'a', 'an', 'section', 'chapter', 'figure', 'table', 'step', 'part', 'appendix'}
        counted = [o for o in openers if o not in enumeration]
        top_count = 0
        if counted:
            counts = Counter(counted)
            top_count = max(counts.values())
            metrics['opener_unique_ratio'] = round(len(counts) / len(counted), 3)
            metrics['top_opener_share'] = round(top_count / len(counted), 3)
        run = max_run = 0
        prev = None
        for opener in counted:
            run = run + 1 if opener == prev else 1
            prev = opener
            max_run = max(max_run, run)
        metrics['max_consecutive_opener'] = max_run
        top_repeat = metrics['top_opener_share'] > 0.25 and top_count >= 4
        if metrics['opener_unique_ratio'] < 0.55 or top_repeat or max_run >= 4:
            flags.append(flag('opener_repetition', metrics['opener_unique_ratio'], 'unique ratio < 0.55, one opener > 25% with 4+ uses, or 4 consecutive identical openers', 'Sentence openings repeat in a template-like rhythm.', 'Rewrite repeated starts; step-by-step docs may need repeated imperative openers.'))
    if sentences:
        closer_count = sum((1 for s in sentences if CLOSER_RE.search(s)))
        metrics['participial_closer_share'] = round(closer_count / len(sentences), 3)
        if len(sentences) >= 8 and metrics['participial_closer_share'] >= 0.15:
            flags.append(flag('participial_closer_share', metrics['participial_closer_share'], '>= 0.15 over at least 8 prose sentences', 'Many sentences end with editorial -ing consequence tails.', 'Make the consequence concrete or cut the tail; analytical prose may allow an occasional closer.'))
    return {'flags': flags, 'flagged': {f['metric']: True for f in flags}, 'metrics': metrics, 'genre': genre, 'prose_sentences': len(sentences), 'prose_paragraphs': len(paragraphs)}

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?')
    parser.add_argument('--genre', choices=['prose', 'docs', 'social'], default='prose')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f'Missing file: {path}', file=sys.stderr)
            return 2
        text = path.read_text(errors='replace')
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    result = scan(text, args.genre)
    if not result.get('flags') and (not is_probably_english(text)):
        print(json.dumps({'non_english': True, 'violations': [], 'flags': []}, indent=2))
        print('note: input appears non-English; scanner declined (English-only).', file=sys.stderr)
        return 0
    print(json.dumps(result, indent=2))
    return 1 if result['flags'] else 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: banned_phrase_scan ====
"""Scan text for AI-isms and banned phrases."""
import argparse
import bisect
import sys
import re
import json
from pathlib import Path
from typing import TypedDict
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _lang import ENGLISH_FUNCTION_WORDS, english_function_share, is_probably_english

class Violation(TypedDict):
    phrase: str
    category: str
    severity: str
    line_number: int
    column: int
    context: str
    suggestion: str | None

def _mask_non_newlines(text: str) -> str:
    return re.sub('[^\\n]', ' ', text)

def mask_ignored_spans(text: str, include_quoted: bool=False) -> str:
    masked = re.sub('```[\\s\\S]*?```', lambda m: _mask_non_newlines(m.group(0)), text)
    masked = re.sub('`[^`\\n]+`', lambda m: _mask_non_newlines(m.group(0)), masked)
    if include_quoted:
        return masked
    masked = re.sub('(?m)^>.*$', lambda m: _mask_non_newlines(m.group(0)), masked)
    quote_patterns = ['"[^"]*"', '“[^”]*”']
    for pattern in quote_patterns:
        masked = re.sub(pattern, lambda m: _mask_non_newlines(m.group(0)), masked)
    return masked

def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    left = '(?<![a-z0-9_-])' if phrase[0].isalnum() else ''
    right = '(?![a-z0-9_-])' if phrase[-1].isalnum() else ''
    return re.compile(left + re.escape(phrase) + right)
_phrase_pattern_ci_cache: dict[str, re.Pattern[str]] = {}

def _phrase_pattern_ci(phrase: str) -> re.Pattern[str]:
    cached = _phrase_pattern_ci_cache.get(phrase)
    if cached is None:
        pattern = _phrase_pattern(phrase).pattern
        if "'" in phrase:
            pattern = pattern.replace("'", "['’]")
        cached = re.compile(pattern, re.IGNORECASE)
        _phrase_pattern_ci_cache[phrase] = cached
    return cached

def _line_starts(text: str) -> list[int]:
    starts = [0]
    for m in re.finditer('\n', text):
        starts.append(m.end())
    return starts

def _line_col_context(text: str, line_starts: list[int], pos: int, context_cache: dict[int, str] | None=None) -> tuple[int, int, str]:
    idx = bisect.bisect_right(line_starts, pos) - 1
    line_start = line_starts[idx]
    line_end = line_starts[idx + 1] - 1 if idx + 1 < len(line_starts) else len(text)
    line_num = idx + 1
    column = pos - line_start + 1
    context = context_cache.get(idx) if context_cache is not None else None
    if context is None:
        context = text[line_start:line_end].strip()
        context = context[:100] + '...' if len(context) > 100 else context
        if context_cache is not None:
            context_cache[idx] = context
    return (line_num, column, context)
BANNED_PHRASES: dict[str, dict[str, str | None]] = {"here's the thing:": {'category': 'throat_clearing', 'severity': 'hard', 'suggestion': None}, 'in conclusion': {'category': 'conclusion_scaffold', 'severity': 'hard', 'suggestion': 'State the conclusion directly.'}, 'underscore the importance': {'category': 'significance_inflation', 'severity': 'hard', 'suggestion': 'State the concrete effect.'}, 'analysts predict': {'category': 'vague_attribution', 'severity': 'hard', 'suggestion': 'Name the analysts or cite the forecast.'}, 'treasure trove': {'category': 'ai_vocabulary', 'severity': 'hard', 'suggestion': 'collection, source'}, 'speak for themselves': {'category': 'false_agency', 'severity': 'hard', 'suggestion': 'State the numbers and what they show.'}, 'rich cultural heritage': {'category': 'promotional', 'severity': 'hard', 'suggestion': None}, 'as an ai language model': {'category': 'assistant_artifact', 'severity': 'hard', 'suggestion': 'Delete the chatbot boilerplate.'}, 'game changer': {'category': 'jargon', 'severity': 'hard', 'suggestion': 'significant, important'}, 'synergy': {'category': 'jargon', 'severity': 'hard', 'suggestion': 'cooperation, collaboration'}, 'robust': {'category': 'jargon', 'severity': 'soft', 'suggestion': 'strong, solid, thorough'}, 'comprehensive': {'category': 'jargon', 'severity': 'soft', 'suggestion': 'full, complete, thorough'}, 'at the end of the day': {'category': 'filler', 'severity': 'hard', 'suggestion': None}, "in today's": {'category': 'filler', 'severity': 'hard', 'suggestion': None}, 'as of my last': {'category': 'knowledge_cutoff', 'severity': 'hard', 'suggestion': 'Delete the training-cutoff disclaimer.'}, 'why should you care': {'category': 'rhetorical_question', 'severity': 'hard', 'suggestion': 'State why it matters directly.'}}
for _banned_phrase in BANNED_PHRASES:
    _phrase_pattern_ci(_banned_phrase)
STRUCTURAL_PATTERNS: list[dict[str, str]] = [{'pattern': '(?:^|[.!?]\\s+)(?:full stop|period)\\.', 'category': 'emphasis_crutch', 'severity': 'hard', 'suggestion': 'Cut the one-word emphasis sentence.'}, {'pattern': "\\bthe real \\w+ (?:is|isn't|was|wasn't|remains)\\b", 'category': 'throat_clearing', 'severity': 'hard', 'suggestion': 'State it directly.'}, {'pattern': '(?i)\\b(?:the\\s+|that\\s+|this\\s+)?(?:struggle|stakes|pain|threat|risk|danger|fear|hype|magic|hustle|grind|stress|pressure|burnout|concern|consequences|impact|tension|anxiety|disconnect|divide|need|demand|love|chemistry|connection|mechanic|feels?)\\s+(?:is|are|was|were)\\s+(?:very\\s+|so\\s+|all\\s+too\\s+)?real\\b', 'category': 'emphasis_crutch', 'severity': 'soft', 'suggestion': 'State what is actually at stake.'}, {'pattern': '\\bleverag(?:e|es|ed|ing)\\s+(?:our\\s+|your\\s+|their\\s+|its\\s+|the\\s+)?(?:synerg|core\\s+compet|strength|expertise|capabilit|technolog|resource|data\\b|ai\\b|platform|ecosystem|network|audit\\s+stream|power\\s+of)', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'use, apply'}, {'pattern': '\\bnavigat(?:e|es|ed|ing)\\s+(?:the\\s+|this\\s+|these\\s+)?(?:complex|challeng|landscape|nuance|intric|water|terrain|maze|minefield|uncertaint|world\\s+of|ever-)', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'handle, address, manage'}, {'pattern': '\\bdelv(?:e|es|ed|ing)\\s+into\\s+(?:the\\s+)?(?:topic|topics|issue|issues|implication|implications|question|questions|subject|details?|nuance|nuances|meaning|argument|claim|concept|matter|problem|analysis|research|data|strategy|history|world|conversation|evidence|complexit(?:y|ies))\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'explore, examine, look at'}, {'pattern': '\\bharness(?:es|ed|ing)?\\s+(?:the\\s+|its\\s+|their\\s+|our\\s+)?(?:power|potential|strength|capabilit|momentum|force|full\\s+)', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'use, tap, apply'}, {'pattern': "\\bharness(?:es|ed|ing)?\\s+(?:(?:(?:the|our|their|its)\\s+)?(?:team|group|company|organization|workforce)(?:['’]s)\\s+energy\\b(?=[^.!?\\n]{0,100}\\b(?:growth|launch|customer\\s+service|transition|collaboration|innovation|expertise|engagement|success|results?)\\b)|(?:(?:the|our|their)\\s+)?energy\\s+(?:and\\s+expertise\\b|of\\s+(?:(?:our|the)\\s+)?(?:team|group|workforce|people)\\s+(?:collaboration|innovation|expertise)\\b|to\\s+(?:drive|fuel|accelerate|unlock|advance)\\s+(?:innovation|collaboration|engagement|growth|transformation|success|results?)\\b))", 'category': 'jargon', 'severity': 'hard', 'suggestion': 'use, focus, coordinate'}, {'pattern': '\\bfoster(?:s|ed|ing)?\\s+(?:a\\s+|an\\s+|greater\\s+|deeper\\s+|stronger\\s+)?(?:culture|collaboration|innovation|sense\\s+of|community|environment|growth|engagement|inclusion|creativity|dialogue|connection|belonging)', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'build, encourage, create'}, {'pattern': '\\bunpack(?:s|ed|ing)?\\s+(?:the\\s+|this\\s+|that\\s+|our\\s+)?(?:idea|argument|assumption|implication|implications|nuance|meaning|claim|concept|topic|dynamic|why|how|what)\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'explain, examine'}, {'pattern': '\\bdoubl(?:e|es|ed|ing)\\s+down\\s+on\\s+(?:the\\s+|this\\s+|that\\s+|our\\s+|your\\s+|its\\s+|their\\s+|a\\s+|an\\s+)?(?:strategy|approach|investment|bet|commitment|vision|message|plan|position)\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'commit, increase'}, {'pattern': '\\bbolster(?:s|ed|ing)?\\s+(?:the\\s+|this\\s+|that\\s+|our\\s+|your\\s+)?(?:argument|case|claim|confidence|credibility|support|position|strategy|effort|security)\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'support, strengthen'}, {'pattern': '\\bstakeholders?\\b[^.!?\\n]{0,50}\\b(?:buy-in|alignment|engagement|feedback|input|management)\\b|\\b(?:buy-in|alignment|engagement)\\b[^.!?\\n]{0,50}\\bstakeholders?\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'people involved'}, {'pattern': "\\b(?:in\\s+)?(?:today's|modern|contemporary|business|marketing|tech|ai|media|education|healthcare|finance|industry)\\s+landscape\\b|\\bthe\\s+(?:business|marketing|tech|ai|media|education|healthcare|finance|industry)\\s+landscape\\s+of\\b|\\bthe\\s+landscape\\s+of\\s+(?:modern\\s+|today's\\s+|contemporary\\s+)?(?:marketing|business|tech\\w*|ai|work|media|education|healthcare|finance|the industry)\\b", 'category': 'jargon', 'severity': 'hard', 'suggestion': 'situation, field, market'}, {'pattern': '\\bload-bearing\\s+(?:part|piece|point|claim|idea|insight|assumption|detail|context|constraint|requirement|decision|argument|premise|section|paragraph|sentence|word|term|concept)\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'essential, important, necessary'}, {'pattern': '\\b(?:our|the|a)\\s+wedge\\s+into\\s+the\\s+(?:\\w+\\s+)?(?:market|enterprise|industry|segment|category|account|vertical)s?\\b|\\bas\\s+a\\s+wedge\\b', 'category': 'jargon', 'severity': 'hard', 'suggestion': 'opening, angle, advantage, entry point'}, {'pattern': '\\b(?:the\\s+)?substrate\\s+(?:for|of)\\s+(?:everything|all|our|the\\s+(?:company|business|movement|conversation|debate|work))\\b|\\bcultural\\s+substrate\\b', 'category': 'ai_vocabulary', 'severity': 'soft', 'suggestion': 'foundation, base, layer'}, {'pattern': '(?:^|[.!?;:]\\s+)research\\s+(?:indicates|shows|suggests)\\b', 'category': 'vague_attribution', 'severity': 'soft', 'suggestion': 'Cite the specific research or name the source.'}, {'pattern': '\\bboasts?\\s+(?:a\\s+|an\\s+)?(?:world-class|state-of-the-art|cutting-edge|impressive|stunning|robust|comprehensive|unparalleled|rich|vibrant|array of|host of|range of|wealth of|plethora)', 'category': 'promotional', 'severity': 'hard', 'suggestion': 'has'}, {'pattern': '\\b(?:data|numbers?|charts?|graphs?|metrics?|figures?|results?|dashboards?|spreadsheets?|trend\\s?lines?|statistics)\\s+tells?\\s+a\\s+(?:clear\\s+)?story\\b', 'category': 'false_agency', 'severity': 'hard', 'suggestion': 'State what the data shows.'}, {'pattern': '\\bplays?\\s+an?\\s+(?:crucial|key|vital|pivotal|significant|central|important|critical|defining|major)\\s+(?:role|part)\\b', 'category': 'significance_inflation', 'severity': 'soft', 'suggestion': 'State the specific effect.'}, {'pattern': '\\bnotwithstanding\\b(?!\\s+(?:anything\\s+to\\s+the\\s+contrary|the\\s+foregoing|any(?:thing)?\\s+(?:other\\s+)?provision|section|clause|subsection|anything\\s+in))', 'category': 'ai_vocabulary', 'severity': 'soft', 'suggestion': 'Use a direct transition.'}, {'pattern': '\\b(?:acts|serves|stands|stood)\\s+as\\s+(?:a|an|the)\\s+(?:testament|reminder|symbol|beacon|foundation|cornerstone|gateway|catalyst|bridge|hub|springboard|window|monument|hallmark|blueprint|cautionary|stark|powerful|shining|prime example|case study|model for)\\b', 'category': 'copula_avoidance', 'severity': 'hard', 'suggestion': 'Use a direct verb.'}, {'pattern': '\\bconstitutes\\s+(?:a|an|the)\\s+(?:(?:groundbreaking|transformative|trailblazing|seminal|revolutionary|landmark|pivotal|significant|major|key)\\s+)?(?:transformation|breakthrough|milestone|achievement|innovation|advance|success|turning\\s+point|cornerstone|testament|legacy|game[- ]changer)\\b', 'category': 'copula_avoidance', 'severity': 'hard', 'suggestion': 'Use a direct verb.'}, {'pattern': '\\bfunctions\\s+as\\s+(?:a|an|the)\\s+(?:(?:seamless|comprehensive|robust|transformative|groundbreaking|strategic|powerful|key|central|critical|all-in-one|single)\\s+)?(?:solution|framework|platform|hub|bridge|catalyst|cornerstone|benchmark|testament|symbol|beacon|transformation|milestone|game[- ]changer)\\b', 'category': 'copula_avoidance', 'severity': 'hard', 'suggestion': 'Use a direct verb.'}, {'pattern': "(?im)(?:^|[.!?]\\s+)(?:not|no)\\b[^.!?]{0,28}[.!?]\\s+(?:the\\s+|it'?s?\\s+|that'?s?\\s+)?[a-z][^.!?]{0,28}[.!?]", 'category': 'anti_slop_register', 'severity': 'soft', 'suggestion': 'Join the fragments into a varied sentence.'}, {'pattern': 'not because .+?\\. because', 'category': 'binary_contrast', 'severity': 'hard', 'suggestion': 'State the reason in one sentence.'}, {'pattern': "feels like .+?\\. it's actually", 'category': 'binary_contrast', 'severity': 'hard', 'suggestion': 'State the diagnosis directly.'}, {'pattern': '\\bnot only .+? but also', 'category': 'negative_parallelism', 'severity': 'hard', 'suggestion': 'Use a direct sentence.'}, {'pattern': "\\b(?:it'?s not|it\\s+is\\s+not|this is not|that'?s not|isn'?t|is\\s+not|wasn'?t|was\\s+not|aren'?t|are\\s+not|weren'?t|were\\s+not)\\s+just\\b[^.;!?\\n]{1,60}[,;—–-]\\s*(?:it'?s|it (?:is|was)|they'?re|that'?s)\\b", 'category': 'negative_parallelism', 'severity': 'hard', 'suggestion': 'State the contrast directly.'}, {'pattern': "(?i)\\bin this (?:article|section|post|guide|chapter|paper),?\\s+(?:we|i)\\s+(?:will|'ll|are going to|shall)\\b", 'category': 'reader_addressing', 'severity': 'soft', 'suggestion': 'Start with the point.'}, {'pattern': "(?im)(?:^|[.!?]\\s+)whether you'?re (?=[^.!?\\n]{0,60}\\b(?:a|an|just starting)\\s)[^.!?\\n]{1,60}\\bor\\b", 'category': 'reader_addressing', 'severity': 'soft', 'suggestion': 'Cut the audience-flattering opener.'}, {'pattern': "(?im)(?:^|[.!?]\\s+)(?:why does this matter|what's the (?:real )?takeaway|why this matters|so what does (?:this|that) mean)\\b[^.!?\\n]{0,40}[?:]", 'category': 'rhetorical_question', 'severity': 'soft', 'suggestion': 'Answer directly instead of teeing up a self-Q&A.'}, {'pattern': '(?m)^\\s*(?:but\\s+)?what does this mean for\\b', 'category': 'rhetorical_question', 'severity': 'soft', 'suggestion': 'State the consequence directly.'}, {'pattern': '\\b(?:could|may|might|can)\\s+(?:potentially|possibly)\\b', 'category': 'hedge_stack', 'severity': 'soft', 'suggestion': 'Drop the redundant hedge.'}, {'pattern': '(?m)^(?:here are|these are|the top)\\s+\\d+\\s+(?:reasons|things|takeaways|lessons|ways)\\b', 'category': 'numbered_list_inflation', 'severity': 'soft', 'suggestion': 'List only the points that matter.'}]

def _sentence_context(text: str, start: int, end: int) -> str:
    left = max((text.rfind(mark, 0, start) for mark in '.!?\n'))
    right_candidates = [text.find(mark, end) for mark in '.!?\n']
    right_candidates = [pos for pos in right_candidates if pos >= 0]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1:right]

def _context_has(pattern: str, text: str, start: int, end: int) -> bool:
    sentence = _sentence_context(text, start, end)
    if re.search(pattern, sentence, re.IGNORECASE):
        return True
    window = text[max(0, start - 180):min(len(text), end + 180)]
    return bool(re.search(pattern, window, re.IGNORECASE))
_LEGAL_CONTEXT = '\\b(?:act|agreement|agency|clause|contract|court|defendant|filing|hearing|judge|jury|landlord|law|lease|legal|liabilit(?:y|ies)|ordinance|part(?:y|ies)|plaintiff|proceedings?|provision|pursuant|regulat(?:e|ed|ion|ory)|rights?|section|statute|subsection|tenant\\w*|warrant)\\b'
_HISTORICAL_CONTEXT = '\\b(?:archaeolog\\w*|archive\\w*|artifact\\w*|catalog\\w*|chronicle\\w*|document\\w*|histor\\w*|museum\\w*|preserv\\w*|record\\w*|tradition\\w*|custom\\w*|excavat\\w*|ancestr\\w*)\\b'
_PROMOTIONAL_CONTEXT = '\\b(?:boast\\w*|celebrat\\w*|famous|known|renowned|touris\\w*|visitor\\w*|destination|vibrant|stunning|impressive|rich\\s+in)\\b'
_SOURCE_CONTEXT = '\\b(?:according\\s+to|per|citing|based\\s+on|as\\s+(?:reported|stated|estimated)\\s+by)\\b|\\b(?:survey|report|study|data|figures?)\\s+(?:from|by|of|says?|shows?|finds?|estimates?|projects?|predicts?)\\b'
_MEDICAL_CONTEXT = '\\b(?:anatom\\w*|biolog\\w*|cancer|cell\\w*|clinical\\w*|diagnos\\w*|disease\\w*|dose\\w*|drug\\w*|genes?\\b|genetic\\w*|genomic\\w*|health\\w*|immune\\w*|infection\\w*|inflamm\\w*|kidney\\w*|liver\\w*|medical\\w*|medicine|patient\\w*|patholog\\w*|physiolog\\w*|symptom\\w*|therapy|tissue\\w*|treatment\\w*|tumou?r\\w*|syndrome\\w*)\\b'

def _suppress_contextual_match(phrase: str, category: str, scan_text: str, start: int, end: int) -> bool:
    if phrase == 'rich cultural heritage':
        sentence = _sentence_context(scan_text, start, end)
        return bool(re.search(_HISTORICAL_CONTEXT, sentence, re.IGNORECASE) and (not re.search(_PROMOTIONAL_CONTEXT, sentence, re.IGNORECASE)))
    if phrase == "in today's":
        return bool(re.match('\\s+(?:hearing|court\\s+hearing|trial|session|proceedings?)\\b', scan_text[end:], re.IGNORECASE))
    if phrase == 'analysts predict':
        sentence = _sentence_context(scan_text, start, end)
        if re.search(_SOURCE_CONTEXT, sentence, re.IGNORECASE):
            return True
        return False
    if category == 'negative_parallelism' and scan_text[start:end].lower().startswith('not only'):
        return bool(re.search(_LEGAL_CONTEXT, _sentence_context(scan_text, start, end), re.IGNORECASE))
    if category == 'significance_inflation' and re.match('plays?\\s+an?\\s+(?:crucial|key|vital|pivotal|significant|central|important|critical|defining|major)\\s+(?:role|part)\\b', scan_text[start:end], re.IGNORECASE):
        return _context_has(_MEDICAL_CONTEXT, scan_text, start, end)
    return False

def scan_for_violations(text: str, include_quoted: bool=False) -> list[Violation]:
    violations: list[Violation] = []
    spans: list[tuple[int, int]] = []
    scan_text = mask_ignored_spans(text, include_quoted=include_quoted)
    scan_text_lower = scan_text.lower().replace('’', "'")
    line_starts = _line_starts(text)
    line_context_cache: dict[int, str] = {}
    for phrase, info in BANNED_PHRASES.items():
        if phrase not in scan_text_lower:
            continue
        for match in _phrase_pattern_ci(phrase).finditer(scan_text):
            if _suppress_contextual_match(phrase, info['category'], scan_text, match.start(), match.end()):
                continue
            tail = scan_text[match.end():]
            if phrase == 'robust' and re.match('\\s+(?:hash\\s+verification|retry\\s+mechanism|error\\s+handling|test\\s+suite)\\b', tail, re.IGNORECASE) or (phrase == 'comprehensive' and re.match('\\s+(?:visual\\s+survey|needs\\s+screen)\\b', tail, re.IGNORECASE)):
                continue
            pos = match.start()
            line_num, column, context = _line_col_context(text, line_starts, pos, line_context_cache)
            violations.append({'phrase': phrase, 'category': info['category'], 'severity': info.get('severity', 'hard'), 'line_number': line_num, 'column': column, 'context': context, 'suggestion': info['suggestion']})
            spans.append((match.start(), match.end()))
    for pattern_info in STRUCTURAL_PATTERNS:
        matches = list(re.finditer(pattern_info['pattern'], scan_text, re.IGNORECASE))
        min_matches = int(pattern_info.get('min_matches', '1'))
        if len(matches) < min_matches:
            continue
        for match in matches:
            if _suppress_contextual_match(match.group().lower(), pattern_info['category'], scan_text, match.start(), match.end()):
                continue
            pos = match.start()
            line_num, column, context = _line_col_context(text, line_starts, pos, line_context_cache)
            violations.append({'phrase': match.group().lower(), 'category': pattern_info['category'], 'severity': pattern_info.get('severity', 'hard'), 'line_number': line_num, 'column': column, 'context': context, 'suggestion': pattern_info['suggestion']})
            spans.append((match.start(), match.end()))
    freq_gated = {p['category'] for p in STRUCTURAL_PATTERNS if int(p.get('min_matches', '1')) > 1}
    n = len(violations)
    order = sorted(range(n), key=lambda i: (spans[i][0], -spans[i][1]))
    contained = [False] * n
    max_end_before_group = -1
    idx = 0
    while idx < n:
        group_start = spans[order[idx]][0]
        group_end = idx
        while group_end < n and spans[order[group_end]][0] == group_start:
            group_end += 1
        running_max_in_group = -1
        for vi in order[idx:group_end]:
            end = spans[vi][1]
            if max_end_before_group >= end or running_max_in_group > end:
                contained[vi] = True
            if end > running_max_in_group:
                running_max_in_group = end
        if running_max_in_group > max_end_before_group:
            max_end_before_group = running_max_in_group
        idx = group_end
    violations = [v for i, v in enumerate(violations) if not contained[i] or v['category'] in freq_gated]
    violations.sort(key=lambda v: (v['line_number'], v['column']))
    return violations

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_file', nargs='?', help='Optional input file. Reads stdin when omitted.')
    parser.add_argument('--include-quoted', action='store_true', help='Scan quoted examples and markdown blockquotes instead of skipping them.')
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    if args.input_file:
        try:
            with open(args.input_file, 'r', errors='replace') as f:
                text = f.read()
        except OSError as e:
            print(json.dumps({'error': f'Could not read input: {e}', 'violations': []}))
            sys.exit(2)
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not text.strip():
        print(json.dumps({'error': 'No input provided', 'violations': []}))
        sys.exit(1)
    violations = scan_for_violations(text, include_quoted=args.include_quoted)
    if not violations and (not is_probably_english(text)):
        print(json.dumps({'non_english': True, 'total_violations': 0, 'violations': []}, indent=2))
        print('note: input appears non-English; scanner declined (English-only).', file=sys.stderr)
        sys.exit(0)
    categories: dict[str, int] = {}
    by_severity: dict[str, int] = {'hard': 0, 'soft': 0}
    for v in violations:
        categories[v['category']] = categories.get(v['category'], 0) + 1
        by_severity[v['severity']] = by_severity.get(v['severity'], 0) + 1
    output = {'total_violations': len(violations), 'by_severity': by_severity, 'by_category': categories, 'violations': violations}
    print(json.dumps(output, indent=2))
    sys.exit(1 if violations else 0)
if __name__ == '__main__':
    main()

# ==== module: silhouette_scan ====
"""Scan prose for discourse-level silhouette AI-writing patterns."""
import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from structure_scan import STOPWORDS as _STRUCTURE_STOPWORDS
from _lang import is_probably_english, paragraphs as _prose_paragraphs, words
REFERENCE_PATH = Path(__file__).resolve().parent.parent / 'evals' / 'fixtures' / 'silhouette' / 'human_reference.json'
PENALTY_THRESHOLD = 1.0
MIN_PARAGRAPHS = 3
SILHOUETTE_STOPWORDS = _STRUCTURE_STOPWORDS | frozenset({'our', 'your', 'their', 'my', 'me', 'us', 'them', 'his', 'her', 'what', 'which', 'who', 'when', 'where', 'how', 'why', 'there', 'here', 'about', 'just', 'more', 'most', 'some', 'all', 'also', 'out', 'up', 'one', 'two', 'get', 'got', 'like', 'much', 'many', 'very', 'every', 'only'})
ROLE_CUES = {'contrast': '^(on the other hand|on one hand|however|conversely|in contrast|yet|but |perhaps most|that said|still,)', 'addition': '^(moreover|furthermore|additionally|in addition|also,|another|second|third|next,|finally,|besides)', 'conclusion': '^(in conclusion|ultimately|overall|in the end|to sum|in summary|as we|remember|the future)', 'enumeration': '^(first,|firstly|1\\.|step \\d|there are)', 'cause': '^(therefore|thus|consequently|as a result|because of)'}
ROLE_RE = {k: re.compile(v, re.I) for k, v in ROLE_CUES.items()}

def content(text: str) -> list[str]:
    return [w for w in words(text) if len(w) > 3 and w not in SILHOUETTE_STOPWORDS]

def paragraphs(text: str) -> list[str]:
    return _prose_paragraphs(text, strip_bold=True)

def m_scaffold_opener_share(paras: list[str]):
    body = paras[1:] if len(paras) > 1 else paras
    if not body:
        return 0.0
    hits = 0
    for p in body:
        for rx in ROLE_RE.values():
            if rx.search(p):
                hits += 1
                break
    return round(hits / len(body), 3)

def m_role_entropy(paras: list[str]):
    if len(paras) < 3:
        return None
    roles = []
    for p in paras:
        r = 'topic'
        for name, rx in ROLE_RE.items():
            if rx.search(p):
                r = name
                break
        roles.append(r)
    counts = Counter(roles)
    n = len(roles)
    ent = -sum((c / n * math.log2(c / n) for c in counts.values()))
    return round(ent, 3)

def m_preview_fulfillment(paras: list[str]):
    if len(paras) < 4:
        return None
    intro = set(content(paras[0]))
    if not intro:
        return 0.0
    body = paras[1:-1] if len(paras) > 2 else paras[1:]
    hits = tot = 0
    for p in body:
        cs = content(p)
        if not cs:
            continue
        tot += 1
        if cs[0] in intro:
            hits += 1
    return round(hits / tot, 3) if tot else 0.0

def m_callback_content(paras: list[str]):
    n = len(paras)
    if n < 5:
        return None
    third = max(1, n // 3)
    early = set().union(*[set(content(paras[i])) for i in range(third)])
    mid = set().union(*[set(content(paras[i])) for i in range(third, n - third)]) if n - 2 * third > 0 else set()
    late = set().union(*[set(content(paras[i])) for i in range(n - third, n)])
    cb = (early & late) - mid
    return round(len(cb) / n, 3)

def m_heading_preview(text: str):
    heads = re.findall('(?m)^\\s{0,3}#{2,3}\\s+(.*)$', text)
    if len(heads) < 3:
        return None
    paras = paragraphs(text)
    intro = set(content(paras[0])) if paras else set()
    if not intro:
        return 0.0
    hit = 0
    for h in heads:
        hc = set(content(h))
        if hc & intro:
            hit += 1
    return round(hit / len(heads), 3)
PARA_METRICS = {'scaffold_opener_share': m_scaffold_opener_share, 'role_entropy_bits': m_role_entropy, 'preview_fulfillment': m_preview_fulfillment, 'callback_content': m_callback_content}
TEXT_METRICS = {'heading_preview': m_heading_preview}
METRIC_ORDER = ['scaffold_opener_share', 'role_entropy_bits', 'heading_preview', 'preview_fulfillment', 'callback_content']
SUGGESTIONS = {'scaffold_opener_share': 'Open body paragraphs on their own specific claim, not a discourse cue.', 'role_entropy_bits': "Stop rotating 'However / In addition / Ultimately' scaffold openers.", 'heading_preview': "Headings restate the intro's outline; let sections carry new ground.", 'preview_fulfillment': 'The body just fulfills an outline previewed in the intro; drop the preview.', 'callback_content': 'The ending loops back to opening vocabulary; end on a concrete final point.'}

def compute_metrics(text: str, paras: list[str]) -> dict:
    row = {}
    for name in METRIC_ORDER:
        if name in PARA_METRICS:
            row[name] = PARA_METRICS[name](paras)
        else:
            row[name] = TEXT_METRICS[name](text)
    return row

def load_reference(path: Path) -> dict:
    data = json.loads(path.read_text()) if Path(path).exists() else HUMAN_REFERENCE
    return data['metrics']

def relu(x: float) -> float:
    return x if x > 0 else 0.0

def flag(metric, value, threshold, detail, suggestion) -> dict:
    return {'metric': metric, 'value': value, 'threshold': threshold, 'severity': 'soft', 'detail': detail, 'suggestion': suggestion}
GENRE_SUPPRESSIONS = {'docs': {'callback_content'}}

def scan(text: str, reference: dict, genre: str='prose') -> dict:
    paras = paragraphs(text)
    base = {'genre': genre, 'prose_paragraphs': len(paras)}
    if len(paras) < MIN_PARAGRAPHS:
        base.update({'flags': [], 'flagged': {}, 'metrics': None, 'penalty': None, 'note': f'fewer than {MIN_PARAGRAPHS} prose paragraphs; silhouette metrics not scored'})
        return base
    metrics = compute_metrics(text, paras)
    contributions = {}
    penalty = 0.0
    flags = []
    for name in METRIC_ORDER:
        if name in GENRE_SUPPRESSIONS.get(genre, set()):
            contributions[name] = 0.0
            continue
        ref = reference[name]
        value = metrics[name]
        if not isinstance(value, (int, float)):
            contributions[name] = None
            continue
        median = ref['median']
        scale = max(ref['iqr'], ref['fence'])
        weight = ref['weight']
        contribution = round(weight * relu((value - median) / scale), 3)
        contributions[name] = contribution
        penalty += contribution
        if value >= ref['fence']:
            flags.append(flag(name, value, f"human fence {ref['fence']} (weight {weight})", f"{name} at {value} clears the human upper fence {ref['fence']}.", SUGGESTIONS[name]))
    penalty = round(penalty, 3)
    if penalty >= PENALTY_THRESHOLD:
        flags.insert(0, flag('silhouette_penalty', penalty, f'>= {PENALTY_THRESHOLD}', "The document's idea arrangement matches a templated AI silhouette (preview-then-fulfill, rotating scaffold openers, recap loop).", 'Rearrange around the actual argument instead of a symmetric outline; cut previews and the closing recap.'))
    base.update({'flags': flags, 'flagged': {f['metric']: True for f in flags}, 'metrics': metrics, 'contributions': contributions, 'penalty': penalty})
    return base

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?')
    parser.add_argument('--genre', choices=['prose', 'docs', 'social'], default='prose')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if False:
        print(f'Missing reference: {REFERENCE_PATH}', file=sys.stderr)
        return 2
    reference = load_reference(REFERENCE_PATH)
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f'Missing file: {path}', file=sys.stderr)
            return 2
        text = path.read_text(errors='replace')
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    result = scan(text, reference, args.genre)
    if not result.get('flags') and (not is_probably_english(text)):
        print(json.dumps({'non_english': True, 'flags': [], 'penalty': None}, indent=2))
        print('note: input appears non-English; scanner declined (English-only).', file=sys.stderr)
        return 0
    print(json.dumps(result, indent=2))
    is_flagged = bool(result.get('penalty') is not None and result['penalty'] >= PENALTY_THRESHOLD)
    return 1 if is_flagged else 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
HUMAN_REFERENCE = {"metrics":{"scaffold_opener_share":{"median":0.0,"iqr":0.05,"fence":0.2,"weight":2.0,"n":15},"role_entropy_bits":{"median":-0.0,"iqr":0.05,"fence":0.8,"weight":1.0,"n":15},"heading_preview":{"median":0.0,"iqr":0.05,"fence":0.2,"weight":1.0,"n":1},"preview_fulfillment":{"median":0.0,"iqr":0.05,"fence":0.25,"weight":1.0,"n":12},"callback_content":{"median":0.0,"iqr":0.05,"fence":0.3,"weight":1.5,"n":8}}}


# ==== module: extract_constraints ====
"""Extract must-preserve constraints from input text."""
import argparse
import sys
import re
import json
from typing import TypedDict

class Constraint(TypedDict):
    type: str
    value: str
    start: int
    end: int
PATTERNS: dict[str, str] = {'currency': '\\$[\\d,]+\\.?\\d*[KMBkmb]?(?:\\s*(?:million|billion|thousand))?', 'percentage': '\\d+\\.?\\d*%', 'date_iso': '\\d{4}-\\d{2}-\\d{2}', 'date_quarter': 'Q[1-4]\\s+\\d{4}', 'date_natural': '(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\.?\\s+\\d{1,2}(?:st|nd|rd|th)?,?\\s+\\d{4}', 'year': '\\b(?:19|20)\\d{2}\\b', 'time': '\\d{1,2}:\\d{2}(?::\\d{2})?\\s*(?:AM|PM|am|pm|UTC|PST|EST|CST|MST|GMT)?', 'magnitude_number': '\\b\\d[\\d,]*\\.?\\d*\\s+(?:thousand|million|billion|trillion)\\b', 'measurement': '\\d+\\.?\\d*\\s*(?:°C|°F|degrees?\\s*(?:C|F|Celsius|Fahrenheit)?|ms|s|sec|min|hr|hour|day|week|month|year|KB|MB|GB|TB|PB|kg|g|lb|oz|m|km|mi|ft|in|cm|mm|px|em|rem|%)\\b', 'phone': '\\b(?:\\+?1[-.\\s]?)?(?:\\(\\d{3}\\)\\s*|\\d{3}[-.\\s])\\d{3}[-.\\s]\\d{4}\\b', 'range': '\\d+\\.?\\d*\\s*[-–]\\s*\\d+\\.?\\d*(?:\\s*(?:K|M|B|%|years?|months?|days?))?', 'url': 'https?://[^\\s\\)\\]\\>\\"\\\']+', 'email': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', 'code': '`[^`]+`', 'quote': '["“][^"“”]{10,}["”]', 'reference': '\\b(?:Sections?|Sec\\.|§|Articles?|Clauses?|Paragraphs?|Para\\.|Figures?|Fig\\.|Tables?|Appendix|Appendices|Schedule|Exhibit|Equations?|Eq\\.|Chapters?|Rules?|Items?)\\s+\\d+[A-Za-z]?(?:\\([a-z0-9]+\\))?(?:[.\\-]\\d+)*', 'version': 'v?\\d+\\.\\d+(?:\\.\\d+)?(?:-[a-zA-Z0-9]+)?', 'api_endpoint': '(?<![\\w])/(?:api|v\\d+)(?:/[\\w-]+)+|(?<![\\w])/[\\w-]+(?:/[\\w-]+){2,}', 'and_or': '\\band/or\\b', 'count': '\\b\\d+(?:,\\d{3})*\\s+(?:users?|customers?|employees?|companies?|teams?|people|engineers?|developers?|items?|products?|orders?|transactions?|requests?|queries?|rows?|records?)\\b'}
PROPER_NOUN_INDICATORS = ['\\b[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)+\\b', '\\b[A-Z][a-z]+\\s+(?:Inc|Corp|LLC|Ltd|Co)\\b\\.?', '\\b(?:Dr|Mr|Ms|Mrs|Prof)\\.?\\s+[A-Z][a-z]+\\b']

def extract_constraints(text: str) -> list[Constraint]:
    constraints: list[Constraint] = []
    seen_spans: set[tuple[int, int]] = set()
    for constraint_type, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE if constraint_type.startswith('date') else 0):
            span = (match.start(), match.end())
            if span not in seen_spans:
                seen_spans.add(span)
                constraints.append({'type': constraint_type, 'value': match.group(), 'start': match.start(), 'end': match.end()})
    for pattern in PROPER_NOUN_INDICATORS:
        for match in re.finditer(pattern, text):
            span = (match.start(), match.end())
            overlaps = any((not (span[1] <= existing[0] or span[0] >= existing[1]) for existing in seen_spans))
            if not overlaps:
                seen_spans.add(span)
                constraints.append({'type': 'proper_noun', 'value': match.group(), 'start': match.start(), 'end': match.end()})
    number_pattern = '(?<![\\d.,])(?:\\d{1,3}(?:,\\d{3})+|\\d{4,})(?![\\d.,])'
    for match in re.finditer(number_pattern, text):
        span = (match.start(), match.end())
        overlaps = any((not (span[1] <= existing[0] or span[0] >= existing[1]) for existing in seen_spans))
        if not overlaps:
            seen_spans.add(span)
            constraints.append({'type': 'number', 'value': match.group(), 'start': match.start(), 'end': match.end()})
    constraints.sort(key=lambda c: c['start'])
    return constraints

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Extract must-preserve constraints from input text.')
    parser.add_argument('path', nargs='?', help='Path to input text file (default: read stdin)')
    return parser.parse_args(argv)

def main() -> None:
    args = parse_args(sys.argv[1:])
    if args.path:
        try:
            with open(args.path, 'r', errors='replace') as f:
                text = f.read()
        except OSError as e:
            print(json.dumps({'error': f'Could not read input: {e}', 'constraints': []}))
            sys.exit(2)
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not text.strip():
        print(json.dumps({'error': 'No input provided', 'constraints': []}))
        sys.exit(1)
    constraints = extract_constraints(text)
    output = {'input_length': len(text), 'constraint_count': len(constraints), 'constraints': constraints}
    print(json.dumps(output, indent=2))
if __name__ == '__main__':
    main()

# ==== module: validate_preservation ====
"""Validate that all must-preserve constraints survived transformation."""
import sys
import json
import re
from typing import TypedDict
from extract_constraints import extract_constraints, Constraint

class ValidationResult(TypedDict):
    passed: bool
    total_constraints: int
    preserved: int
    missing: list[Constraint]
    warnings: list[str]
_MAGNITUDES = {'k': 1000.0, 'thousand': 1000.0, 'm': 1000000.0, 'million': 1000000.0, 'b': 1000000000.0, 'billion': 1000000000.0, 'trillion': 1000000000000.0}
_MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

def normalize_value(value: str) -> str:
    normalized = re.sub('\\s+', ' ', value.strip())
    return normalized.lower()

def parse_money(token: str) -> float | None:
    m = re.search('([\\d,]+\\.?\\d*)\\s*(k|m|b|thousand|million|billion)?', token.lower().replace('$', ''))
    if not m or not m.group(1).strip(','):
        return None
    amount = float(m.group(1).replace(',', ''))
    if m.group(2):
        amount *= _MAGNITUDES[m.group(2)]
    return amount

def parse_magnitude_number(token: str) -> float | None:
    m = re.search('\\b([\\d,]+\\.?\\d*)\\s*(thousand|million|billion|trillion)?\\b', token.lower())
    if not m or not m.group(1).strip(','):
        return None
    amount = float(m.group(1).replace(',', ''))
    if m.group(2):
        amount *= _MAGNITUDES[m.group(2)]
    return amount

def _numbers_match_exactly(value: str, text: str, pattern: str) -> bool:
    want = re.findall('\\d+\\.?\\d*', value)
    have = set(re.findall(pattern, text.lower()))
    return all((num in have for num in want)) and bool(want)
_UNIT_SYNONYMS = {'km': {'km', 'kilometer', 'kilometers', 'kilometre', 'kilometres'}, 'mi': {'mi', 'mile', 'miles'}, 'kg': {'kg', 'kilogram', 'kilograms'}, 'g': {'g', 'gram', 'grams'}, 'ms': {'ms', 'millisecond', 'milliseconds'}, 's': {'s', 'sec', 'second', 'seconds'}, 'm': {'m', 'meter', 'meters', 'metre', 'metres'}, 'cm': {'cm', 'centimeter', 'centimeters', 'centimetre', 'centimetres'}, 'mm': {'mm', 'millimeter', 'millimeters', 'millimetre', 'millimetres'}, 'ft': {'ft', 'foot', 'feet'}, 'in': {'in', 'inch', 'inches'}, 'lb': {'lb', 'lbs', 'pound', 'pounds'}, 'oz': {'oz', 'ounce', 'ounces'}, '°c': {'°c', 'c', 'celsius'}, '°f': {'°f', 'f', 'fahrenheit'}, 'min': {'min', 'mins', 'minute', 'minutes'}, 'hr': {'hr', 'hrs', 'hour', 'hours'}, 'day': {'day', 'days'}, 'week': {'week', 'weeks', 'wk', 'wks'}, 'month': {'month', 'months', 'mo'}, 'year': {'year', 'years', 'yr', 'yrs'}, 'kb': {'kb', 'kilobyte', 'kilobytes'}, 'mb': {'mb', 'megabyte', 'megabytes'}, 'gb': {'gb', 'gigabyte', 'gigabytes'}, 'tb': {'tb', 'terabyte', 'terabytes'}, 'pb': {'pb', 'petabyte', 'petabytes'}, 'px': {'px', 'pixel', 'pixels'}}

def _measurement_parts(value: str) -> tuple[str, set[str]] | None:
    m = re.search('(\\d+\\.?\\d*)\\s*([^\\d\\s]+|degrees?(?:\\s+\\w+)?)', value, re.I)
    if not m:
        return None
    unit = m.group(2).lower().strip()
    unit = re.sub('^degrees?\\s*', '', unit) or 'degree'
    aliases = _UNIT_SYNONYMS.get(unit)
    if aliases is None:
        for family in _UNIT_SYNONYMS.values():
            if unit in family:
                aliases = family
                break
        else:
            aliases = {unit}
    return (m.group(1), aliases)

def _quote_core(value: str) -> str:
    return value.strip().strip('"“”').lower()

def _time_variants(value: str) -> set[str]:
    m = re.search('\\b(\\d{1,2})(?::(\\d{2}))?(?::\\d{2})?\\s*(am|pm)?\\b', value, re.I)
    if not m:
        return set()
    hour = str(int(m.group(1)))
    minute = m.group(2) or '00'
    suffix = (m.group(3) or '').lower()
    spaced = f' {suffix}' if suffix else ''
    compact = suffix
    variants = {f'{hour}:{minute}{spaced}'.strip(), f'{hour}:{minute}{compact}'.strip()}
    if minute == '00':
        variants.update({f'{hour}{spaced}'.strip(), f'{hour}{compact}'.strip()})
    return variants

def find_constraint_in_text(constraint: Constraint, text: str) -> bool:
    value = constraint['value']
    ctype = constraint['type']
    normalized_value = normalize_value(value)
    normalized_text = normalize_value(text)
    if normalized_value in normalized_text:
        return True
    if ctype == 'and_or':
        return bool(re.search('\\band/or\\b|\\bor\\b', text, re.IGNORECASE))
    if ctype == 'currency':
        target = parse_money(value)
        if target is None:
            return False
        for token in re.findall('\\$?[\\d,]+\\.?\\d*\\s*(?:k|m|b|thousand|million|billion)?', text, re.IGNORECASE):
            amount = parse_money(token)
            if amount is not None and abs(amount - target) < 0.01:
                return True
        return False
    if ctype == 'magnitude_number':
        target = parse_magnitude_number(value)
        if target is None:
            return False
        for token in re.findall('\\b[\\d,]+\\.?\\d*\\s*(?:thousand|million|billion|trillion)?\\b', text, re.IGNORECASE):
            amount = parse_magnitude_number(token)
            if amount is not None and abs(amount - target) < 0.01:
                return True
        return False
    if ctype == 'percentage':
        return _numbers_match_exactly(value, text, '(\\d+\\.?\\d*)\\s*(?:%|percent)')
    if ctype == 'measurement':
        parts = _measurement_parts(value)
        if not parts:
            return False
        number, units = parts
        clean_text = text.replace(',', '').lower()
        if not re.search('(?<![\\d.])' + re.escape(number.replace(',', '')) + '(?![\\d.])', clean_text):
            return False
        return any((re.search('(?<!\\w)' + re.escape(unit) + '(?!\\w)', clean_text) for unit in units))
    if ctype == 'range':
        return _numbers_match_exactly(value, text, '(?<![\\d.])(\\d+\\.?\\d*)(?![\\d.])')
    if ctype == 'time':
        text_variants = _time_variants(text)
        return bool(_time_variants(value) & text_variants)
    if ctype in ('count', 'number'):
        for num in re.findall('[\\d,]+\\.?\\d*', value):
            clean_num = num.replace(',', '')
            if re.search('(?<![\\d.])' + re.escape(clean_num) + '(?![\\d.])', text.replace(',', '')):
                return True
        return False
    if ctype == 'date_quarter':
        year_match = re.search('\\d{4}', value)
        if not (year_match and year_match.group() in text):
            return False
        q = re.search('q([1-4])', value.lower())
        if not q:
            return False
        ordinal = {'1': 'first', '2': 'second', '3': 'third', '4': 'fourth'}[q.group(1)]
        low_text = text.lower()
        return q.group(0) in low_text or re.search(ordinal + '\\s+quarter', low_text) is not None
    if ctype.startswith('date'):
        year_match = re.search('\\d{4}', value)
        if not (year_match and year_match.group() in text):
            return False
        low = value.lower()
        month = next((mo for mo in _MONTHS if mo[:3] in low), None)
        if month and month[:3] not in text.lower():
            return False
        quarter = re.search('q[1-4]', low)
        if quarter and quarter.group() not in text.lower():
            return False
        return True
    if constraint['type'] == 'quote':
        inner = _quote_core(value)
        comparable_text = normalized_text.replace('“', '"').replace('”', '"')
        if inner in comparable_text:
            return True
    if ctype == 'proper_noun':
        words = re.findall('[A-Z][a-z]+', value)
        if words and all((re.search('\\b' + re.escape(word) + '\\b', text, re.I) for word in words)):
            return True
    return False
_NEGATION_RE = re.compile("\\b(?:not|never|no|cannot|can't|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't|without|neither|nor|none|fails?\\s+to|rather\\s+than)\\b", re.I)
_SCOPE_RE = re.compile('\\b(?:most|all|none|every|each|some|few|several|majority|minority|only|always|usually|typically|rarely|approximately|roughly|about|nearly)\\b', re.I)
_CONDITIONAL_RE = re.compile('\\b(?:if|unless|provided\\s+that|only\\s+if|assuming|given\\s+that|in\\s+the\\s+event|contingent\\s+on|except|excluding|other\\s+than|aside\\s+from|save\\s+for)\\b', re.I)
_WEAK_MODAL_RE = re.compile('\\b(?:may|might|could|should|can|likely|probably|appears?|suggests?|seems?)\\b', re.I)
_STRONG_MODAL_RE = re.compile('\\b(?:will|must|always|definitely|certainly|guarantees?|proves?)\\b', re.I)

def semantic_drift_warnings(original: str, transformed: str) -> list[str]:
    out: list[str] = []
    o, t = (original.lower(), transformed.lower())
    on, tn = (len(_NEGATION_RE.findall(o)), len(_NEGATION_RE.findall(t)))
    if on > tn:
        out.append(f"Negation count dropped {on}->{tn}. Verify no claim was inverted or weakened (e.g. 'does not support' -> 'supports').")
    missing_scope = sorted({w for w in _SCOPE_RE.findall(o)} - {w for w in _SCOPE_RE.findall(t)})
    for w in missing_scope:
        out.append(f"Scope/precision word '{w}' not in output. Verify the claim's scope is unchanged.")
    oc, tc = (len(_CONDITIONAL_RE.findall(o)), len(_CONDITIONAL_RE.findall(t)))
    if oc > tc:
        out.append(f"Conditional count dropped {oc}->{tc}. Verify a conditional claim wasn't turned into an unconditional one.")
    ow, tw = (len(_WEAK_MODAL_RE.findall(o)), len(_WEAK_MODAL_RE.findall(t)))
    os, ts = (len(_STRONG_MODAL_RE.findall(o)), len(_STRONG_MODAL_RE.findall(t)))
    if ow > tw and ts > os:
        out.append('Hedged claim may have been strengthened. Verify uncertainty was not turned into certainty.')
    return out

def validate_preservation(original_text: str, transformed_text: str, constraints: list[Constraint] | None=None) -> ValidationResult:
    if constraints is None:
        constraints = extract_constraints(original_text)
    missing: list[Constraint] = []
    warnings: list[str] = []
    for constraint in constraints:
        if not find_constraint_in_text(constraint, transformed_text):
            missing.append(constraint)
    for m in missing:
        if m['type'] == 'percentage':
            num = re.search('[\\d.]+', m['value'])
            if num and num.group() in transformed_text:
                warnings.append(f"Number {num.group()} found but missing '%' symbol")
    warnings.extend(semantic_drift_warnings(original_text, transformed_text))
    preserved = len(constraints) - len(missing)
    return {'passed': len(missing) == 0, 'total_constraints': len(constraints), 'preserved': preserved, 'missing': missing, 'warnings': warnings}

def main() -> None:
    args = sys.argv[1:]
    strict = False
    if args and args[0] == '--strict':
        strict = True
        args = args[1:]
    if len(args) < 2:
        print('Usage: validate_preservation.py <original.txt> <transformed.txt> [constraints.json]')
        sys.exit(1)
    try:
        with open(args[0], 'r') as f:
            original_text = f.read()
        with open(args[1], 'r') as f:
            transformed_text = f.read()
    except OSError as e:
        print(json.dumps({'error': f'Could not read input: {e}'}))
        sys.exit(2)
    constraints = None
    if len(args) > 2:
        with open(args[2], 'r') as f:
            data = json.load(f)
            constraints = data.get('constraints', [])
    result = validate_preservation(original_text, transformed_text, constraints)
    output = {'passed': result['passed'], 'total_constraints': result['total_constraints'], 'preserved': result['preserved'], 'missing_count': len(result['missing']), 'missing': result['missing'], 'warnings': result['warnings']}
    print(json.dumps(output, indent=2))
    sys.exit(0 if result['passed'] and (not (strict and result['warnings'])) else 1)
if __name__ == '__main__':
    main()

# ==== module: diff_check ====
"""Check change percentage between original and transformed text."""
import sys
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import TypedDict

class DiffResult(TypedDict):
    original_word_count: int
    transformed_word_count: int
    similarity_ratio: float
    change_percentage: float
    words_added: int
    words_removed: int
    words_changed: int
    excessive_change: bool
    flags: list[str]

def split_words(text: str) -> list[str]:
    return re.findall('\\w+|[^\\w\\s]', text.lower())

def calculate_diff(original: str, transformed: str) -> DiffResult:
    original_words = split_words(original)
    transformed_words = split_words(transformed)
    matcher = SequenceMatcher(None, original_words, transformed_words)
    similarity = matcher.ratio()
    words_added = 0
    words_removed = 0
    words_changed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            words_changed += max(i2 - i1, j2 - j1)
        elif tag == 'delete':
            words_removed += i2 - i1
        elif tag == 'insert':
            words_added += j2 - j1
    total_changes = words_added + words_removed + words_changed
    change_percentage = total_changes / len(original_words) * 100 if original_words else 0
    shared_tokens = sum((Counter(original_words) & Counter(transformed_words)).values())
    token_overlap = shared_tokens / len(original_words) if original_words else 0
    flags: list[str] = []
    excessive = False
    if change_percentage > 40:
        if token_overlap >= 0.9:
            flags.append(f'Mostly reordered ({token_overlap:.0%} tokens shared)')
        else:
            flags.append(f'Excessive change ({change_percentage:.1f}% > 40% threshold)')
            excessive = True
    if len(transformed_words) < len(original_words) * 0.3:
        flags.append('Transformed text is less than 30% of original length')
        excessive = True
    if len(transformed_words) > len(original_words) * 1.5:
        flags.append('Transformed text is 50%+ longer than original')
    length_ratio = len(transformed_words) / len(original_words) if original_words else 0
    if length_ratio < 0.5:
        flags.append(f'Significant condensation ({length_ratio:.0%} of original)')
    elif length_ratio > 1.2:
        flags.append(f'Text expanded ({length_ratio:.0%} of original)')
    return {'original_word_count': len(original_words), 'transformed_word_count': len(transformed_words), 'similarity_ratio': round(similarity, 3), 'change_percentage': round(change_percentage, 1), 'words_added': words_added, 'words_removed': words_removed, 'words_changed': words_changed, 'excessive_change': excessive, 'flags': flags}

def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: diff_check.py <original.txt> <transformed.txt>')
        sys.exit(1)
    try:
        with open(sys.argv[1], 'r') as f:
            original = f.read()
        with open(sys.argv[2], 'r') as f:
            transformed = f.read()
    except OSError as e:
        print(json.dumps({'error': f'Could not read input: {e}'}))
        sys.exit(2)
    result = calculate_diff(original, transformed)
    print(json.dumps(result, indent=2))
    sys.exit(1 if result['excessive_change'] else 0)
if __name__ == '__main__':
    main()

# ==== module: suggest ====
"""Co-writer suggestion mode: emit LSP-style structured edit suggestions."""
import argparse
import json
import re
import sys
from pathlib import Path
from banned_phrase_scan import is_probably_english, scan_for_violations
from structure_scan import scan as structure_scan

def _line_starts(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == '\n':
            starts.append(i + 1)
    return starts

def _offset(line_starts: list[int], line_number: int, column: int) -> int:
    return line_starts[line_number - 1] + (column - 1)

def _rationale(category: str, span_text: str, suggestion: str | None, is_soft: bool) -> str:
    if is_soft:
        hint = f' Consider: {suggestion}.' if suggestion else ''
        return f'Soft tell ({category}): could “{span_text}” be cut or reworded here?{hint}'
    if suggestion:
        return f'AI-writing tell ({category}): replace “{span_text}” — {suggestion}'
    return f'AI-writing tell ({category}): replace “{span_text}”.'

def build_suggestions(text: str) -> list[dict]:
    violations = scan_for_violations(text)
    line_starts = _line_starts(text)
    candidates: list[dict] = []
    for v in violations:
        start = _offset(line_starts, v['line_number'], v['column'])
        end = start + len(v['phrase'])
        span_text = text[start:end]
        is_soft = v['severity'] == 'soft'
        candidates.append({'span': {'start': start, 'end': end, 'text': span_text}, 'severity': v['severity'], 'category': v['category'], 'rationale': _rationale(v['category'], span_text, v.get('suggestion'), is_soft), 'suggested_replacement': None, 'phrased_as_question': is_soft})
    candidates.sort(key=lambda s: (s['span']['start'], s['span']['end'], s['category']))
    kept: list[dict] = []
    last_end = -1
    for s in candidates:
        if s['span']['start'] >= last_end:
            kept.append(s)
            last_end = s['span']['end']
    return kept

def counts_block(suggestions: list[dict], struct: dict) -> dict:
    by_category: dict[str, int] = {}
    hard = soft = 0
    for s in suggestions:
        by_category[s['category']] = by_category.get(s['category'], 0) + 1
        if s['severity'] == 'soft':
            soft += 1
        else:
            hard += 1
    return {'total': len(suggestions), 'hard': hard, 'soft': soft, 'by_category': by_category, 'structure_flags': [f['metric'] for f in struct.get('flags', [])]}

def apply_replacements(suggestions: list[dict], repl_path: str) -> list[str]:
    data = json.loads(Path(repl_path).read_text())
    index = {(r['start'], r['end']): r['replacement'] for r in data.get('replacements', [])}
    warnings: list[str] = []
    matched: set[tuple[int, int]] = set()
    for s in suggestions:
        key = (s['span']['start'], s['span']['end'])
        if key not in index:
            continue
        rep = index[key]
        s['suggested_replacement'] = rep
        matched.add(key)
        if rep == s['span']['text']:
            warnings.append(f'replacement for span {list(key)} is identical to span text')
        elif scan_for_violations(rep) or structure_scan(rep).get('flags'):
            warnings.append(f'replacement for span {list(key)} does not pass the scanners in isolation')
    for key in index:
        if key not in matched:
            warnings.append(f'replacement targets unknown span {list(key)}')
    return warnings

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', help='Document file. Reads stdin when omitted.')
    parser.add_argument('--apply-replacements', metavar='FILE', help='Merge externally-produced replacements (JSON) into the suggestions.')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f'Missing file: {path}', file=sys.stderr)
            return 2
        text = path.read_text(errors='replace')
    else:
        text = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    if not is_probably_english(text):
        print(json.dumps({'non_english': True, 'document': text, 'suggestions': [], 'counts': {'total': 0, 'hard': 0, 'soft': 0, 'by_category': {}, 'structure_flags': []}}, indent=2))
        print('note: input appears non-English; co-writer declined (English-only).', file=sys.stderr)
        return 0
    suggestions = build_suggestions(text)
    struct = structure_scan(text)
    out = {'document': text, 'suggestions': suggestions, 'counts': counts_block(suggestions, struct)}
    if args.apply_replacements:
        out['apply_warnings'] = apply_replacements(suggestions, args.apply_replacements)
    print(json.dumps(out, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: check_suggestions ====
"""Contract gates for co-writer suggestions."""
import argparse
import json
import sys
from pathlib import Path
from banned_phrase_scan import scan_for_violations
from structure_scan import scan as structure_scan
from validate_preservation import validate_preservation

def _leading_shared_words(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a.split(), b.split()):
        if x == y:
            n += 1
        else:
            break
    return n

def _trailing_shared_words(a: str, b: str) -> int:
    ra = ' '.join(reversed(a.split()))
    rb = ' '.join(reversed(b.split()))
    return _leading_shared_words(ra, rb)

def _line_starts(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == '\n':
            starts.append(i + 1)
    return starts

def violation_spans(text: str) -> list[tuple[int, int]]:
    starts = _line_starts(text)
    out = []
    for v in scan_for_violations(text):
        s = starts[v['line_number'] - 1] + v['column'] - 1
        out.append((s, s + len(v['phrase'])))
    return out

def _scanners_clean(text: str) -> bool:
    return not scan_for_violations(text) and (not structure_scan(text).get('flags'))

def apply_all(document: str, suggestions: list[dict]) -> str:
    out = document
    for s in sorted(suggestions, key=lambda s: s['span']['start'], reverse=True):
        rep = s.get('suggested_replacement')
        if rep is None:
            continue
        st, en = (s['span']['start'], s['span']['end'])
        out = out[:st] + rep + out[en:]
    return out

def check(document: str, suggestions: list[dict]) -> list[dict]:
    failures: list[dict] = []
    order = sorted(range(len(suggestions)), key=lambda i: (suggestions[i]['span']['start'], suggestions[i]['span']['end']))
    last_end = None
    last_i = None
    for i in order:
        st, en = (suggestions[i]['span']['start'], suggestions[i]['span']['end'])
        if last_end is not None and st < last_end:
            failures.append({'gate': 'span-overlap', 'suggestions': [last_i, i], 'detail': f'span {st}-{en} overlaps the previous span ending at {last_end}'})
        last_end, last_i = (en, i)
    for i, s in enumerate(suggestions):
        st, en = (s['span']['start'], s['span']['end'])
        span_text = document[st:en]
        if span_text != s['span']['text']:
            failures.append({'gate': 'span-minimality', 'suggestion': i, 'detail': 'span.text does not match document[start:end]'})
        rep = s.get('suggested_replacement')
        if rep is None:
            continue
        if rep == span_text:
            failures.append({'gate': 'span-minimality', 'suggestion': i, 'detail': 'replacement is identical to the span text (no change)'})
            continue
        if _leading_shared_words(span_text, rep) > 0 or _trailing_shared_words(span_text, rep) > 0:
            failures.append({'gate': 'span-minimality', 'suggestion': i, 'detail': 'replacement shares leading/trailing whole words with the span; shrink the span so the edit is minimal'})
    for i, s in enumerate(suggestions):
        rep = s.get('suggested_replacement')
        if rep is None:
            continue
        if not _scanners_clean(rep):
            failures.append({'gate': 'replacement-scanner', 'suggestion': i, 'detail': 'replacement does not pass both scanners in isolation'})
        st, en = (s['span']['start'], s['span']['end'])
        ctx = document[:st] + rep + document[en:]
        new_start, new_end = (st, st + len(rep))
        if any((a < new_end and new_start < b for a, b in violation_spans(ctx))):
            failures.append({'gate': 'replacement-scanner', 'suggestion': i, 'detail': 'replacement introduces a violation in context'})
    unresolved = [i for i, s in enumerate(suggestions) if s.get('suggested_replacement') is None]
    if unresolved:
        failures.append({'gate': 'accept-all', 'detail': f'suggestions {unresolved} have no replacement; cannot accept-all'})
    applied = apply_all(document, suggestions)
    if not _scanners_clean(applied):
        failures.append({'gate': 'accept-all', 'detail': 'the accept-all document still fails a scanner'})
    preservation = validate_preservation(document, applied)
    if not preservation['passed']:
        failures.append({'gate': 'accept-all', 'detail': 'validate_preservation failed against the original', 'missing': preservation['missing']})
    return failures

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Contract gates for co-writer suggestions.')
    parser.add_argument('path', nargs='?', help='Path to a suggestions JSON file (default: read stdin)')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f'Missing file: {path}', file=sys.stderr)
            return 2
        raw = path.read_text(errors='replace')
    else:
        raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({'passed': False, 'error': f'invalid JSON: {e}'}, indent=2))
        return 1
    document = data.get('document')
    suggestions = data.get('suggestions', [])
    if not isinstance(document, str):
        print(json.dumps({'passed': False, 'error': "missing 'document' string"}, indent=2))
        return 1
    failures = check(document, suggestions)
    result = {'passed': not failures, 'failure_gates': sorted({f['gate'] for f in failures}), 'failures': failures}
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: voice_profile ====
"""Build deterministic stylometric voice profiles."""
import argparse
import collections
import json
import math
import re
import statistics
import sys
from pathlib import Path
FUNCTION_WORDS = "\nthe of and to in a is that it for as with was on be by he i this are or his from at\nwhich but have an had they you were their one all we can her has there been if more\nwhen will would who so no she about out up into do any your what than them some could\nthese other then its our two may first my now such like over only also after most did\nmany before must through back where much should well people down own just because good\neach those how under see made very being make between both even another while last\nmight still same never every against since off though yet without within upon among\nuntil during per either neither nor whether whose whom why again once here there\ntherefore however although nevertheless moreover instead indeed perhaps rather thus\nelse already almost around across behind beyond near toward towards above below beside\ninside outside along plus minus except despite via versus including regarding concerning\nam were does done doing having let lets cannot dont didn't doesn't isn't aren't wasn't\nweren't haven't hasn't hadn't won't wouldn't shouldn't couldn't mightn't mustn't i'm\nyou're he's she's it's we're they're i've you've we've they've i'd you'd he'd she'd we'd\nthey'd i'll you'll he'll she'll we'll they'll me him us mine yours ours theirs myself\nyourself himself herself itself ourselves yourselves themselves\n".split()
PUNCT = [',', '.', ';', ':', '?', '!', '-', '(', ')', '"', "'"]
WORD_RE = re.compile("[A-Za-z]+(?:'[A-Za-z]+)?|\\d+")
SENT_RE = re.compile('[^.!?]+[.!?]?')

def iter_docs(root):
    for path in sorted(Path(root).rglob('*')):
        if path.suffix.lower() in {'.txt', '.md'} and path.is_file():
            yield path

def normalize(text):
    return re.sub('\\s+', ' ', text.lower()).strip()

def words(text):
    return WORD_RE.findall(text.lower())

def sentences(text):
    out = []
    for part in SENT_RE.findall(text):
        toks = words(part)
        if toks:
            out.append(toks)
    return out

def char3_counts(text, limit=None):
    norm = normalize(text)
    grams = collections.Counter((norm[i:i + 3] for i in range(max(0, len(norm) - 2))))
    items = sorted(grams.items(), key=lambda kv: (-kv[1], kv[0]))
    if limit:
        items = items[:limit]
    return dict(items)

def function_freq(tokens):
    total = max(1, len(tokens))
    counts = collections.Counter(tokens)
    return {w: counts[w] / total for w in FUNCTION_WORDS}

def sentence_stats(text):
    lengths = [len(s) for s in sentences(text)]
    if not lengths:
        return {'lengths': [], 'median': 0.0, 'iqr': 0.0}
    ordered = sorted(lengths)
    mid = statistics.median(ordered)
    q1 = statistics.median(ordered[:len(ordered) // 2] or ordered)
    q3 = statistics.median(ordered[(len(ordered) + 1) // 2:] or ordered)
    return {'lengths': lengths, 'median': mid, 'iqr': q3 - q1}

def mtld(tokens, threshold=0.72):
    if len(tokens) < 20:
        return 0.0
    factors = 0.0
    types = set()
    count = 0
    for tok in tokens:
        count += 1
        types.add(tok)
        if len(types) / count <= threshold:
            factors += 1
            types.clear()
            count = 0
    if count:
        ttr = len(types) / count
        factors += (1 - ttr) / (1 - threshold) if threshold < 1 else 0
    return len(tokens) / factors if factors else float(len(tokens))

def feature_bundle(text):
    toks = words(text)
    total = max(1, len(toks))
    punct_counts = collections.Counter((ch for ch in text if ch in PUNCT))
    contractions = sum((1 for t in toks if "'" in t))
    hist = collections.Counter((min(len(t), 15) for t in toks))
    paragraphs = [p for p in re.split('\\n\\s*\\n', text.strip()) if p.strip()]
    return {'char3': char3_counts(text, 2000), 'function_words': function_freq(toks), 'sentence_lengths': sentence_stats(text), 'punctuation': {p: punct_counts[p] / total for p in PUNCT}, 'contraction_rate': contractions / total, 'mtld': mtld(toks), 'word_length_histogram': {str(i): hist[i] / total for i in range(1, 16)}, 'paragraph_stats': {'count': len(paragraphs), 'mean_words': sum((len(words(p)) for p in paragraphs)) / len(paragraphs) if paragraphs else 0.0}, 'total_words': len(toks)}

def background_stats(root=None):
    docs = []
    if root:
        docs = [p.read_text(errors='replace') for p in iter_docs(root)]
    if not docs:
        return {w: {'mean': 0.0025 if w not in {'the', 'of', 'and', 'to', 'in', 'a'} else 0.025, 'std': 0.006} for w in FUNCTION_WORDS}
    rows = [function_freq(words(text)) for text in docs]
    stats = {}
    for w in FUNCTION_WORDS:
        vals = [r[w] for r in rows]
        stats[w] = {'mean': statistics.mean(vals), 'std': statistics.pstdev(vals) or 0.0001}
    return stats

def build_profile(samples_dir, background=None):
    paths = list(iter_docs(samples_dir))
    text = '\n\n'.join((p.read_text(errors='replace') for p in paths))
    profile = feature_bundle(text)
    profile['function_word_background'] = background_stats(background)
    profile['metadata'] = {'doc_count': len(paths), 'total_words': profile['total_words'], 'low_confidence': profile['total_words'] < 2000, 'genre_warning': 'profile has fewer than 2000 words' if profile['total_words'] < 2000 else ''}
    return profile

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('samples_dir')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--background')
    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    root = Path(args.samples_dir)
    if not root.is_dir():
        print(f'missing samples dir: {root}', file=sys.stderr)
        return 2
    if not list(iter_docs(root)):
        print(f'no sample documents in {root}: only .txt and .md files are read (recursively). Rename samples to .txt/.md or point at the right directory.', file=sys.stderr)
        return 2
    profile = build_profile(root, args.background)
    if profile['metadata']['low_confidence']:
        print(profile['metadata']['genre_warning'], file=sys.stderr)
    Path(args.output).write_text(json.dumps(profile, indent=2, sort_keys=True) + '\n')
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: voice_score ====
"""Score a candidate against a voice profile."""
import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path
import voice_profile
WEIGHTS = {'char3': 0.3, 'delta': 0.25, 'sentence_emd': 0.1, 'punctuation': 0.08, 'contraction': 0.07, 'mtld': 0.1, 'word_length': 0.1}

def cosine_distance(a, b, keys=None):
    keys = list(keys) if keys is not None else sorted(set(a) | set(b))
    dot = sum((a.get(k, 0.0) * b.get(k, 0.0) for k in keys))
    na = math.sqrt(sum((a.get(k, 0.0) ** 2 for k in keys)))
    nb = math.sqrt(sum((b.get(k, 0.0) ** 2 for k in keys)))
    if not na or not nb:
        return 1.0
    return 1 - dot / (na * nb)

def z_function_vector(freqs, bg, top):
    keys = sorted(bg, key=lambda k: bg[k].get('mean', 0), reverse=True)[:top]
    return {k: (freqs.get(k, 0.0) - bg[k]['mean']) / (bg[k]['std'] or 0.0001) for k in keys}

def emd(a, b):
    if not a or not b:
        return 0.0
    max_len = max(max(a), max(b))
    ca = cb = dist = 0.0
    for i in range(1, max_len + 1):
        ca += sum((1 for x in a if x == i)) / len(a)
        cb += sum((1 for x in b if x == i)) / len(b)
        dist += abs(ca - cb)
    return dist

def l1(a, b, keys):
    return sum((abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys))

def distances(profile, feats, subset=None):
    subset = set(subset or WEIGHTS)
    out = {}
    if 'char3' in subset:
        keys = set(profile['char3']) | set(feats['char3'])
        out['char3'] = cosine_distance(profile['char3'], feats['char3'], keys)
    if 'delta' in subset:
        top = 50 if feats['total_words'] < 300 else 200
        bg = profile['function_word_background']
        pv = z_function_vector(profile['function_words'], bg, top)
        cv = z_function_vector(feats['function_words'], bg, top)
        out['delta'] = cosine_distance(pv, cv, pv.keys())
    if 'sentence_emd' in subset:
        med = profile['sentence_lengths'].get('median') or 1.0
        out['sentence_emd'] = emd(profile['sentence_lengths']['lengths'], feats['sentence_lengths']['lengths']) / med
    if 'punctuation' in subset:
        out['punctuation'] = l1(profile['punctuation'], feats['punctuation'], voice_profile.PUNCT)
    if 'contraction' in subset:
        out['contraction'] = abs(profile['contraction_rate'] - feats['contraction_rate'])
    if 'mtld' in subset:
        out['mtld'] = abs(profile['mtld'] - feats['mtld']) / (profile['mtld'] or 1.0)
    if 'word_length' in subset:
        keys = [str(i) for i in range(1, 16)]
        out['word_length'] = l1(profile['word_length_histogram'], feats['word_length_histogram'], keys)
    return out

def weighted_sum(dists):
    return sum((WEIGHTS[k] * dists.get(k, 0.0) for k in WEIGHTS))

def impostor_features(root):
    feats = []
    for path in voice_profile.iter_docs(root):
        feats.append((str(path), voice_profile.feature_bundle(path.read_text(errors='replace'))))
    return feats

def zscores(candidate, impostor_rows):
    out = {}
    for key in WEIGHTS:
        vals = [row[key] for row in impostor_rows if key in row]
        if key not in candidate or not vals:
            out[key] = None
            continue
        mean = statistics.mean(vals)
        std = statistics.pstdev(vals) or 0.0001
        out[key] = (candidate[key] - mean) / std
    return out

def gi_score(profile, cand_feats, impostors, seed):
    rng = random.Random(seed)
    keys = list(WEIGHTS)
    wins = 0
    trials = 64
    cand_dists = distances(profile, cand_feats)
    impostor_dists = [(name, distances(profile, imp)) for name, imp in impostors]
    for _ in range(trials):
        subset = [k for k in keys if rng.random() < 0.5] or [rng.choice(keys)]
        cand = sum((WEIGHTS[k] * cand_dists.get(k, 0.0) for k in subset))
        sampled = rng.sample(impostor_dists, k=min(len(impostor_dists), max(1, len(impostor_dists) // 2)))
        if all((cand < sum((WEIGHTS[k] * imp_dists.get(k, 0.0) for k in subset)) for _, imp_dists in sampled)):
            wins += 1
    return wins / trials

def ngrams(tokens, n=4):
    return set((tuple(tokens[i:i + n]) for i in range(max(0, len(tokens) - n + 1))))
LCS_THRESHOLD = 120

def has_common_substring_over(a: str, b: str, min_length: int) -> bool:
    if min_length <= 0:
        return bool(a) and bool(b)
    if len(a) < min_length or len(b) < min_length:
        return False
    base = 257
    mod = (1 << 61) - 1
    high_power = pow(base, min_length - 1, mod)

    def window_hashes(s: str) -> dict[int, list[int]]:
        table: dict[int, list[int]] = {}
        h = 0
        for i in range(min_length):
            h = (h * base + ord(s[i])) % mod
        table.setdefault(h, []).append(0)
        for i in range(min_length, len(s)):
            h = ((h - ord(s[i - min_length]) * high_power) * base + ord(s[i])) % mod
            table.setdefault(h, []).append(i - min_length + 1)
        return table
    table_a = window_hashes(a)
    table_b = window_hashes(b)
    for h, starts_b in table_b.items():
        starts_a = table_a.get(h)
        if not starts_a:
            continue
        for sb in starts_b:
            window_b = b[sb:sb + min_length]
            for sa in starts_a:
                if a[sa:sa + min_length] == window_b:
                    return True
    return False

def copy_gate(candidate_text, samples_dir):
    cand_grams = ngrams(voice_profile.words(candidate_text))
    max_overlap = 0.0
    lcs_violation = False
    for path in voice_profile.iter_docs(samples_dir):
        text = path.read_text(errors='replace')
        sample_grams = ngrams(voice_profile.words(text))
        if cand_grams:
            max_overlap = max(max_overlap, len(cand_grams & sample_grams) / len(cand_grams))
        if has_common_substring_over(candidate_text, text, LCS_THRESHOLD + 1):
            lcs_violation = True
    max_lcs = LCS_THRESHOLD + 1 if lcs_violation else 0
    return {'max_overlap': max_overlap, 'longest_common_substring': max_lcs, 'violation': max_overlap > 0.35 or lcs_violation}

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', required=True)
    parser.add_argument('--impostors', required=True)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--samples')
    parser.add_argument('candidate_file')
    return parser.parse_args(argv)

def read_candidate(path):
    if path == '-':
        return sys.stdin.buffer.read().decode('utf-8', errors='replace')
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return p.read_text(errors='replace')

def main(argv):
    args = parse_args(argv)
    if not Path(args.profile).exists() or not Path(args.impostors).is_dir():
        print('missing profile or impostors', file=sys.stderr)
        return 2
    try:
        text = read_candidate(args.candidate_file)
    except FileNotFoundError as e:
        print(f'missing candidate: {e}', file=sys.stderr)
        return 2
    profile = json.loads(Path(args.profile).read_text())
    feats = voice_profile.feature_bundle(text)
    low = feats['total_words'] < 150
    impostors = impostor_features(args.impostors)
    dist = distances(profile, feats)
    imp_dist = [distances(profile, f) for _, f in impostors]
    zs = zscores(dist, imp_dist)
    zsum = sum((WEIGHTS[k] * max(-3.0, min(3.0, zs[k] if zs[k] is not None else 0.0)) for k in WEIGHTS))
    gi = gi_score(profile, feats, impostors, args.seed) if impostors else 0.0
    result = {'candidate_words': feats['total_words'], 'low_confidence': low, 'distances': {k: None if low and k in {'sentence_emd', 'mtld'} else v for k, v in dist.items()}, 'z_scores': {k: None if low and k in {'sentence_emd', 'mtld'} else v for k, v in zs.items()}, 'gi': gi, 'composite': 0.5 * (1 - gi) + 0.5 * zsum}
    if args.samples:
        result['copy_gate'] = copy_gate(text, args.samples)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: voice_card ====
"""Distill a voice profile + samples into a LAYERED, pack-sized style card."""
import argparse
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path
import voice_profile
TAXONOMY = ['explaining-technical', 'anecdote', 'argument', 'disagreement', 'praise', 'hedging-uncertainty', 'numbers-data', 'addressing-reader', 'openings', 'closings']
STRUCTURAL = {'openings', 'closings'}
COVER_THRESHOLD = 2
NUMBER_WORDS = {'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'dozen', 'hundred', 'thousand', 'million', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'percent', 'half', 'quarter', 'double', 'triple', 'nine'}
SIGNALS = {'explaining-technical': {'because', 'so that', 'which means', 'the reason', 'works by', 'depends on', 'the way it', 'in order to', "that's how", 'this is how', 'the trick is', 'you have to', 'the point of'}, 'argument': {'therefore', 'thus', 'consequently', 'the point is', 'i distrust', 'clearly', 'obviously', 'in fact', 'the truth is', 'matters because', "that's the point", 'either way', "that's rare", 'nobody', 'no one'}, 'disagreement': {'but i', "i don't", 'no one', 'nobody', 'wrong', 'i distrust', 'rather than', 'not because', 'i hate', "don't trust", 'disagree', 'however', "i wasn't", 'makes sense', "i can't"}, 'praise': {'extraordinary', 'wonderful', 'dependable', 'lovely', 'beautiful', 'kindly', 'generous', 'grateful', 'delightful', 'plenty', 'good choice', 'with care', 'extraordinary care', 'almost pleasant', 'i like'}, 'hedging-uncertainty': {'maybe', 'perhaps', 'probably', 'might', 'i guess', 'i think', 'seems', 'sort of', 'kind of', 'possibly', 'i suppose', 'not sure', "or won't", "or it won't", 'i believed', 'or maybe'}, 'addressing-reader': set(), 'numbers-data': set(), 'anecdote': set()}
FIRST_PERSON = {'i', 'we', 'my', 'me', "we've", "i've", "i'll", "i'd", 'our'}
TIME_CUES = {'today', 'yesterday', 'tonight', 'morning', 'evening', 'night', 'ago', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'last', 'once', 'then', 'later', 'week', 'year'}

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def split_sentences_text(text):
    out = []
    for chunk in re.split('(?<=[.!?])\\s+', text.strip()):
        chunk = re.sub('\\s+', ' ', chunk).strip()
        if chunk:
            out.append(chunk)
    return out

def _has_word(sentence_low, token):
    return re.search('\\b' + re.escape(token) + '\\b', sentence_low) is not None

def _matches(sentence_low, signals):
    for sig in signals:
        if ' ' in sig:
            if sig in sentence_low:
                return True
        elif _has_word(sentence_low, sig):
            return True
    return False

def _is_numbers(sentence_low):
    if re.search('\\d', sentence_low):
        return True
    return any((_has_word(sentence_low, w) for w in NUMBER_WORDS))

def _is_anecdote(sentence_low):
    toks = set(voice_profile.words(sentence_low))
    if not toks & FIRST_PERSON:
        return False
    if toks & TIME_CUES:
        return True
    return any((t.endswith('ed') and len(t) > 3 for t in toks))

def _is_addressing(sentence):
    low = sentence.lower()
    if sentence.rstrip().endswith('?'):
        return True
    return _has_word(low, 'you') or _has_word(low, 'your') or _has_word(low, "you're")

def classify_dimension(sentence):
    low = sentence.lower()
    hit = set()
    for dim, signals in SIGNALS.items():
        if dim in ('addressing-reader', 'numbers-data', 'anecdote'):
            continue
        if _matches(low, signals):
            hit.add(dim)
    if _is_numbers(low):
        hit.add('numbers-data')
    if _is_addressing(sentence):
        hit.add('addressing-reader')
    if _is_anecdote(low):
        hit.add('anecdote')
    return hit

def collect(samples_dir):
    docs = []
    for path in voice_profile.iter_docs(samples_dir):
        sents = split_sentences_text(path.read_text(errors='replace'))
        if sents:
            docs.append(sents)
    return docs

def coverage_matrix(docs):
    buckets = {dim: [] for dim in TAXONOMY}
    for doc in docs:
        if doc:
            buckets['openings'].append(doc[0])
            buckets['closings'].append(doc[-1])
        for sent in doc:
            for dim in classify_dimension(sent):
                buckets[dim].append(sent)
    matrix = {}
    for dim in TAXONOMY:
        sents = buckets[dim]
        if dim in STRUCTURAL:
            covered = len(docs) >= 1
        else:
            covered = len(sents) >= COVER_THRESHOLD
        matrix[dim] = {'count': len(sents), 'covered': covered, 'structural': dim in STRUCTURAL}
    return (matrix, buckets)

def _shortest(sentences, k=3):
    ordered = sorted(set(sentences), key=lambda s: (len(s), s))
    return ordered[:k]

def _contraction_examples(docs, k=3):
    seen = {}
    for doc in docs:
        for sent in doc:
            for tok in voice_profile.words(sent):
                if "'" in tok:
                    seen[tok] = seen.get(tok, 0) + 1
    ranked = sorted(seen.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:k]]

def _opener_words(docs, k=5):
    counts = {}
    for doc in docs:
        for sent in doc:
            toks = voice_profile.words(sent)
            if toks:
                counts[toks[0]] = counts.get(toks[0], 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:k]]

def _burstiness(profile):
    med = profile['sentence_lengths']['median']
    iqr = profile['sentence_lengths']['iqr']
    if med <= 0:
        return 'uneven'
    ratio = iqr / med
    if ratio < 0.5:
        return 'steady'
    if ratio < 1.1:
        return 'moderately bursty'
    return 'very bursty'

def _numbers_tokens(sentences):
    toks = set()
    for sent in sentences:
        for m in re.findall('\\d[\\d,:.]*', sent):
            toks.add(m)
        for w in voice_profile.words(sent.lower()):
            if w in NUMBER_WORDS:
                toks.add(w)
    return sorted(toks)

def _sheet_markers(dim, sentences, profile):
    lengths = [len(voice_profile.words(s)) for s in sentences]
    med = statistics.median(lengths) if lengths else 0
    lines = [f'- Sentences in samples exercising this: {len(sentences)}.', f'- Median length of those sentences: {int(med)} words.']
    if dim == 'numbers-data':
        toks = _numbers_tokens(sentences)
        lines.append('- Numeric tokens actually used: ' + ', '.join(toks[:12]) + '.')
    elif dim == 'addressing-reader':
        q = sum((1 for s in sentences if s.rstrip().endswith('?')))
        lines.append(f'- Direct questions to the reader: {q}.')
        lines.append("- Second person appears; keep it plain, no salesy 'you'.")
    elif dim == 'openings':
        openers = sorted({voice_profile.words(s)[0] for s in sentences if voice_profile.words(s)})
        lines.append('- Documents open on: ' + ', '.join(openers[:8]) + '.')
    elif dim == 'closings':
        lines.append('- Endings land on a concrete image, not a moral recap.')
    else:
        cr = profile['contraction_rate']
        lines.append(f'- Overall contraction rate: {cr:.3f} (keep it consistent here).')
    return lines
SHEET_HOWTO = {'explaining-technical': "Explain by naming the concrete mechanism, not the abstraction. Short causal sentences; 'because' does the work.", 'anecdote': 'Tell it first person, past tense, one scene at a time. Concrete nouns, sensory detail, no summarizing moral.', 'argument': 'State the claim flat, then the reason. No hedging scaffold; the point lands in one line.', 'disagreement': "Disagree by contrast, not confrontation. 'I don't', 'rather than', a plain preference rather than a takedown.", 'praise': 'Praise through specific, restrained detail. Understated approval, never gushing.', 'hedging-uncertainty': "Hold uncertainty lightly with 'maybe' / 'probably' / 'or it won't', not corporate qualifiers.", 'numbers-data': 'Numbers stay small, concrete, woven into the scene rather than tabulated.', 'addressing-reader': "Address the reader sparingly and plainly; a direct question or a flat 'you can'.", 'openings': 'Open cold on a concrete fact or action. No throat-clearing, no thesis statement.', 'closings': "Close on a small, specific image. No wrap-up, no 'ultimately'."}

def build_sheet(dim, sentences, profile):
    title = dim.replace('-', ' ')
    lines = [f'# Voice sheet: {title}', '']
    lines.append(SHEET_HOWTO[dim])
    lines.append('')
    lines.append('## Sample snippets')
    for snip in _shortest(sentences):
        lines.append(f'> {snip}')
    lines.append('')
    lines.append('## Measured markers')
    lines.extend(_sheet_markers(dim, sentences, profile))
    lines.append('')
    return '\n'.join(lines) + '\n'

def _never_does(profile):
    never = []
    p = profile['punctuation']
    label = {';': 'semicolons', '!': 'exclamation points', ':': 'colons', '-': 'hyphenated dashes', '(': 'parentheticals'}
    for mark, name in label.items():
        if p.get(mark, 0.0) == 0.0:
            never.append(name)
    return never

def build_card(profile, docs, matrix, name):
    med = int(profile['sentence_lengths']['median'])
    iqr = int(profile['sentence_lengths']['iqr'])
    contr = profile['contraction_rate']
    examples = _contraction_examples(docs)
    openers = _opener_words(docs)
    never = _never_does(profile)
    covered = [d for d in TAXONOMY if matrix[d]['covered']]
    uncovered = [d for d in TAXONOMY if not matrix[d]['covered']]
    lines = [f'# Voice card: {name}', '']
    lines.append(f"Rhythm: median sentence {med} words, IQR {iqr}, {_burstiness(profile)}. Paragraphs average {int(profile['paragraph_stats']['mean_words'])} words.")
    if examples:
        lines.append(f'Contractions: rate {contr:.3f}; e.g. ' + ', '.join(examples) + '.')
    else:
        lines.append(f'Contractions: rate {contr:.3f}; rarely contracts.')
    if never:
        lines.append('Never: ' + '; '.join(never) + '.')
    lines.append('Openers: ' + ', '.join(openers) + '.')
    lines.append('')
    lines.append('Match rhythm and habits first; keep facts and meaning intact.')
    lines.append('')
    lines.append('## When writing, read the matching sheet')
    lines.append('')
    lines.append('| Situation | Sheet |')
    lines.append('|-----------|-------|')
    for dim in covered:
        lines.append(f"| {dim.replace('-', ' ')} | card/{dim}.md |")
    lines.append('')
    if uncovered:
        lines.append('Uncovered (no sample evidence — do not fabricate a voice for these): ' + ', '.join(uncovered) + '.')
    return '\n'.join(lines) + '\n'

def card_word_count(card_text):
    return len(re.findall("[A-Za-z0-9']+", card_text))

def write_card(profile, samples_dir, out_dir, name):
    docs = collect(samples_dir)
    matrix, buckets = coverage_matrix(docs)
    out = Path(out_dir)
    (out / 'card').mkdir(parents=True, exist_ok=True)
    for stale in (out / 'card').glob('*.md'):
        stale.unlink()
    card = build_card(profile, docs, matrix, name)
    (out / 'card.md').write_text(card)
    for dim in TAXONOMY:
        if matrix[dim]['covered']:
            (out / 'card' / f'{dim}.md').write_text(build_sheet(dim, buckets[dim], profile))
    return matrix

def write_provenance(profile, samples_dir, out_dir):
    samples = []
    total = 0
    for path in voice_profile.iter_docs(samples_dir):
        text = path.read_text(errors='replace')
        wc = len(voice_profile.words(text))
        total += wc
        samples.append({'file': path.name, 'sha256': sha256_file(path), 'words': wc})
    meta = profile.get('metadata', {})
    prov = {'doc_count': len(samples), 'total_words': total, 'samples': samples, 'genre_note': meta.get('genre_warning', '') or 'same-genre samples assumed', 'low_confidence': bool(meta.get('low_confidence', total < 2000))}
    Path(out_dir, 'provenance.json').write_text(json.dumps(prov, indent=2, sort_keys=True) + '\n')
    return prov

def profile_mismatch(supplied, recomputed, path=''):
    here = path or '<root>'
    if isinstance(supplied, bool) or isinstance(recomputed, bool):
        return None if supplied == recomputed else here
    if isinstance(supplied, dict):
        if not isinstance(recomputed, dict):
            return here
        for k in sorted(set(supplied) | set(recomputed)):
            if k == 'function_word_background':
                continue
            if k not in supplied or k not in recomputed:
                return f'{path}.{k}'.lstrip('.')
            m = profile_mismatch(supplied[k], recomputed[k], f'{path}.{k}'.lstrip('.'))
            if m:
                return m
        return None
    if isinstance(supplied, list):
        if not isinstance(recomputed, list) or len(supplied) != len(recomputed):
            return here
        for i, (x, y) in enumerate(zip(supplied, recomputed)):
            m = profile_mismatch(x, y, f'{path}[{i}]')
            if m:
                return m
        return None
    if isinstance(supplied, int) and isinstance(recomputed, int):
        return None if supplied == recomputed else here
    if isinstance(supplied, (int, float)) and isinstance(recomputed, (int, float)):
        return None if abs(supplied - recomputed) <= 1e-06 else here
    return None if supplied == recomputed else here

def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--samples', required=True)
    parser.add_argument('--out')
    parser.add_argument('--name', default='voice')
    parser.add_argument('--coverage', action='store_true', help='print the coverage matrix as JSON and write nothing')
    parser.add_argument('--provenance', action='store_true', help='also write <out>/provenance.json')
    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    profile_path = Path(args.profile)
    samples_dir = Path(args.samples)
    if not profile_path.exists() or not samples_dir.is_dir():
        print('missing profile or samples dir', file=sys.stderr)
        return 2
    if not list(voice_profile.iter_docs(samples_dir)):
        print(f'no sample documents in {samples_dir}: teach reads only .txt and .md files (recursively). Rename samples to .txt/.md or point --samples at the right directory.', file=sys.stderr)
        return 2
    profile = json.loads(profile_path.read_text())
    recomputed = voice_profile.build_profile(samples_dir)
    mismatch = profile_mismatch(profile, recomputed)
    if mismatch is not None:
        print(f"profile does not match --samples (recompute differs at '{mismatch}'); rebuild the profile from these samples with voice_profile.py", file=sys.stderr)
        return 2
    if args.coverage:
        docs = collect(samples_dir)
        matrix, _ = coverage_matrix(docs)
        print(json.dumps(matrix, indent=2, sort_keys=True))
        return 0
    if not args.out:
        print('--out is required unless --coverage', file=sys.stderr)
        return 2
    write_card(profile, samples_dir, args.out, args.name)
    if args.provenance:
        write_provenance(profile, samples_dir, args.out)
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: calibrate_pairs ====
"""Deterministic dimension-controlled pair generation for the teach calibration game."""
import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from extract_constraints import extract_constraints
from banned_phrase_scan import scan_for_violations
DIMENSIONS = ['contractions', 'em_dash', 'sentence_length', 'connectives', 'staccato']
POLES: dict[str, tuple[str, str]] = {'contractions': ('contracted', 'expanded'), 'em_dash': ('dashed', 'plain'), 'sentence_length': ('long', 'short'), 'connectives': ('plain', 'formal'), 'staccato': ('staccato', 'flowing')}

class NotExpressible(Exception):
    pass
_CONTRACTION_PAIRS = [('do not', "don't"), ('does not', "doesn't"), ('did not', "didn't"), ('cannot', "can't"), ('will not', "won't"), ('would not', "wouldn't"), ('should not', "shouldn't"), ('could not', "couldn't"), ('must not', "mustn't"), ('is not', "isn't"), ('are not', "aren't"), ('was not', "wasn't"), ('were not', "weren't"), ('have not', "haven't"), ('has not', "hasn't"), ('had not', "hadn't"), ('I am', "I'm"), ('you are', "you're"), ('we are', "we're"), ('they are', "they're"), ('I will', "I'll"), ('you will', "you'll"), ('we will', "we'll"), ('they will', "they'll"), ('he will', "he'll"), ('she will', "she'll"), ('it will', "it'll"), ('I have', "I've"), ('you have', "you've"), ('we have', "we've"), ('they have', "they've"), ('let us', "let's"), ('it is', "it's"), ('that is', "that's"), ('there is', "there's"), ('here is', "here's"), ('who is', "who's"), ('what is', "what's")]
_HARD_CAPITAL = {e for e, c in _CONTRACTION_PAIRS if e.startswith('I ')}

def _case_like(template: str, source_first_char: str) -> str:
    if source_first_char.isupper():
        return template[0].upper() + template[1:]
    return template[0].lower() + template[1:]
_LOWERABLE_JOINERS = {'the', 'it', 'she', 'he', 'they', 'this', 'that', 'there', 'i', 'we', 'you', 'who', 'what', 'when', 'where', 'why', 'how', 'a', 'an', 'and', 'but', 'so', 'yet', 'or', 'nobody', 'everybody', 'everyone', 'someone', 'something', 'nothing', 'no', 'her', 'his', 'its', 'their', 'our', 'your'}

def _lower_first_word(s: str) -> str:
    m = re.match("[A-Za-z']+", s)
    if not m:
        return s
    word = m.group(0)
    if word.lower() in _LOWERABLE_JOINERS:
        return word.lower() + s[len(word):]
    return s
_WORD_BEFORE_RE = re.compile("([A-Za-z']+)\\s*$")
_WORD_AFTER_RE = re.compile("^\\s*([A-Za-z']+)")

def _is_title_case(word: str) -> bool:
    return bool(word) and word[0].isupper() and word[1:].islower()

def _in_capitalized_span(m: 're.Match[str]') -> bool:
    matched = m.group(0)
    if not matched[0].isupper():
        return False
    text = m.string
    before_m = _WORD_BEFORE_RE.search(text[:m.start()])
    after_m = _WORD_AFTER_RE.match(text[m.end():])
    before_word = before_m.group(1) if before_m else ''
    after_word = after_m.group(1) if after_m else ''
    return _is_title_case(before_word) or _is_title_case(after_word)

def _contraction_repl(replacement: str, hard: bool):

    def repl(m):
        if _in_capitalized_span(m):
            return m.group(0)
        return replacement if hard else _case_like(replacement, m.group(0)[0])
    return repl

def _apply_contractions(text: str) -> tuple[str, str]:
    contract_hits = []
    expand_hits = []
    for expanded, contracted in _CONTRACTION_PAIRS:
        if expanded in _HARD_CAPITAL:
            if re.search(re.escape(contracted), text):
                contract_hits.append((expanded, contracted))
            if re.search(re.escape(expanded), text):
                expand_hits.append((expanded, contracted))
        else:
            if re.search('\\b' + re.escape(contracted) + '\\b', text, re.IGNORECASE):
                contract_hits.append((expanded, contracted))
            if re.search('\\b' + re.escape(expanded) + '\\b', text, re.IGNORECASE):
                expand_hits.append((expanded, contracted))
    if contract_hits:
        out = text
        for expanded, contracted in contract_hits:
            hard = expanded in _HARD_CAPITAL
            pattern = re.escape(contracted) if hard else '\\b' + re.escape(contracted) + '\\b'
            flags = 0 if hard else re.IGNORECASE
            out = re.sub(pattern, _contraction_repl(expanded, hard), out, flags=flags)
        return (out, 'expanded')
    if expand_hits:
        out = text
        for expanded, contracted in expand_hits:
            hard = expanded in _HARD_CAPITAL
            pattern = re.escape(expanded) if hard else '\\b' + re.escape(expanded) + '\\b'
            flags = 0 if hard else re.IGNORECASE
            out = re.sub(pattern, _contraction_repl(contracted, hard), out, flags=flags)
        return (out, 'contracted')
    raise NotExpressible('no contraction or expandable phrase found')
_PAIRED_DASH_RE = re.compile('\\s—\\s(.+?)\\s—\\s')
_PAIRED_COMMA_RE = re.compile(',\\s+(.+?),\\s+')

def _apply_em_dash(text: str) -> tuple[str, str]:
    if _PAIRED_DASH_RE.search(text):
        out = _PAIRED_DASH_RE.sub(lambda m: ', ' + m.group(1) + ', ', text)
        if '—' in out:
            raise NotExpressible("passage mixes a paired em dash with a lone em dash; the paired-dash<->comma path can't resolve the lone dash without changing sentence count")
        return (out, 'plain')
    if '—' in text:
        raise NotExpressible('only a lone em dash found; the em_dash dimension is restricted to the paired-dash<->comma path so sentence count stays stable')
    if _PAIRED_COMMA_RE.search(text):
        out = _PAIRED_COMMA_RE.sub(lambda m: ' — ' + m.group(1) + ' — ', text)
        return (out, 'dashed')
    raise NotExpressible('no paired em dash or comma-bounded parenthetical found')
_COORD_RE = re.compile(',\\s+(and|but|or|so|yet)\\s+', re.IGNORECASE)

def _apply_sentence_length(text: str) -> tuple[str, str]:
    sentences = re.findall('[^.!?]+[.!?]+', text)
    for sent in sentences:
        for m in _COORD_RE.finditer(sent):
            before = sent[:m.start()]
            after = sent[m.end():]
            if len(before.split()) >= 3 and len(after.split()) >= 3:
                new_sent = before.rstrip() + '. ' + m.group(1).capitalize() + ' ' + after
                out = text.replace(sent, new_sent, 1)
                return (re.sub('\\s+', ' ', out).strip(), 'short')
    for i in range(len(sentences) - 1):
        a_words = sentences[i].strip().split()
        b_words = sentences[i + 1].strip().split()
        if len(a_words) <= 8 and len(b_words) <= 8:
            first_no_period = re.sub('[.!?]+\\s*$', '', sentences[i].strip())
            second = sentences[i + 1].strip()
            second_body = re.sub('[.!?]+\\s*$', '', second)
            end_punct = second[len(second_body):].strip() or '.'
            joined = first_no_period + ', and ' + _lower_first_word(second_body) + end_punct
            prefix = ''.join(sentences[:i])
            suffix = ''.join(sentences[i + 2:])
            out = (prefix + ' ' + joined + ' ' + suffix).strip()
            return (re.sub('\\s+', ' ', out), 'long')
    raise NotExpressible('no coordinator split site or joinable short sentences found')
_FORMAL_TO_PLAIN = {'however': 'But', 'additionally': 'Also', 'therefore': 'So', 'furthermore': 'Also', 'moreover': 'Also', 'nevertheless': 'Still', 'consequently': 'So', 'nonetheless': 'Still', 'subsequently': 'Then', 'thus': 'So'}
_PLAIN_TO_FORMAL = {'but': 'However', 'also': 'Additionally', 'so': 'Therefore', 'still': 'Nevertheless', 'then': 'Subsequently'}
_FORMAL_RE = re.compile('(?:^|(?<=[.!?]\\s))(' + '|'.join(_FORMAL_TO_PLAIN) + '),?\\s+', re.IGNORECASE)
_PLAIN_RE = re.compile('(?:^|(?<=[.!?]\\s))(' + '|'.join(_PLAIN_TO_FORMAL) + '),?\\s+', re.IGNORECASE)

def _apply_connectives(text: str) -> tuple[str, str]:
    if _FORMAL_RE.search(text):

        def repl(m):
            return _FORMAL_TO_PLAIN[m.group(1).lower()] + ' '
        out = _FORMAL_RE.sub(repl, text)
        return (out, 'plain')
    if _PLAIN_RE.search(text):

        def repl2(m):
            return _PLAIN_TO_FORMAL[m.group(1).lower()] + ', '
        out = _PLAIN_RE.sub(repl2, text)
        return (out, 'formal')
    raise NotExpressible('no formal or plain connective found')
_LEADING_JOINER_RE = re.compile('^(?:because|although|while|since|if|when|and|but|so|yet|or)\\s+', re.IGNORECASE)

def _apply_staccato(text: str, rng: random.Random) -> tuple[str, str]:
    sentences = re.findall('[^.!?]+[.!?]+', text)
    runs = []
    run_start = None
    for i, sent in enumerate(sentences):
        words = sent.strip().split()
        if len(words) <= 6:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start >= 3:
                runs.append((run_start, i))
            run_start = None
    if run_start is not None and len(sentences) - run_start >= 3:
        runs.append((run_start, len(sentences)))
    if runs:
        start, end = runs[rng.randrange(len(runs))] if len(runs) > 1 else runs[0]
        parts = []
        for idx in range(start, end):
            body = re.sub('[.!?]+\\s*$', '', sentences[idx].strip())
            parts.append(body)
        joined_parts = []
        for i, p in enumerate(parts):
            if i == 0:
                joined_parts.append(p)
            elif i == len(parts) - 1:
                joined_parts.append('and ' + _lower_first_word(p))
            else:
                joined_parts.append(_lower_first_word(p))
        joined = ', '.join(joined_parts) + '.'
        prefix = ''.join(sentences[:start])
        suffix = ''.join(sentences[end:])
        out = (prefix + ' ' + joined + ' ' + suffix).strip()
        return (re.sub('\\s+', ' ', out), 'flowing')
    best_idx, best_commas = (None, 1)
    for i, sent in enumerate(sentences):
        commas = sent.count(',')
        if commas > best_commas:
            best_idx, best_commas = (i, commas)
    if best_idx is not None:
        sent = sentences[best_idx]
        body = re.sub('[.!?]+\\s*$', '', sent.strip())
        end_punct = sent.strip()[len(body):].strip() or '.'
        fragments = [f.strip() for f in body.split(',')]
        cleaned = []
        for frag in fragments:
            frag = _LEADING_JOINER_RE.sub('', frag).strip()
            if not frag:
                continue
            frag = frag[0].upper() + frag[1:]
            cleaned.append(frag)
        if len(cleaned) < 3:
            raise NotExpressible('comma split did not yield a fragment run')
        cleaned[-1] = cleaned[-1] + end_punct if not cleaned[-1].endswith(('.', '!', '?')) else cleaned[-1]
        new_sent = ' '.join((f if f.endswith(('.', '!', '?')) else f + '.' for f in cleaned))
        out = text.replace(sent, new_sent, 1)
        return (re.sub('\\s+', ' ', out).strip(), 'staccato')
    raise NotExpressible('no fragment run or multi-comma sentence found')
_APPLY = {'contractions': lambda text, rng: _apply_contractions(text), 'em_dash': lambda text, rng: _apply_em_dash(text), 'sentence_length': lambda text, rng: _apply_sentence_length(text), 'connectives': lambda text, rng: _apply_connectives(text), 'staccato': _apply_staccato}
_EXAMPLES = {'contractions': {'description': "Expand <-> contract via a fixed, unambiguous mapping table (do not <-> don't, I am <-> I'm, it is <-> it's, ...).", 'a': 'The rollout is not finished, and I am not confident it will ship Friday.', 'b': "The rollout isn't finished, and I'm not confident it'll ship Friday."}, 'em_dash': {'description': 'Paired em-dash parentheticals <-> paired-comma parentheticals only (a lone joiner dash has no comma-pair equivalent that preserves sentence count, so it is declined rather than converted).', 'a': 'The plan — untested and rushed — still shipped on time.', 'b': 'The plan, untested and rushed, still shipped on time.'}, 'sentence_length': {'description': 'Split at a coordinator <-> join two short adjacent sentences.', 'a': 'The team shipped the fix, and the client renewed the contract.', 'b': 'The team shipped the fix. And the client renewed the contract.'}, 'connectives': {'description': 'Formal <-> plain connective swap via a fixed table (However -> But, Additionally -> Also, Therefore -> So, ...). Plain forms drop the comma after the connective ("But ", not "But, ") so they read as ordinary speech, not a filler-opener tell.', 'a': 'However, the numbers slipped in March.', 'b': 'But the numbers slipped in March.'}, 'staccato': {'description': 'Fragment runs <-> flowing clauses.', 'a': 'Because the deploy failed, and the on-call missed the page, the team lost an hour.', 'b': 'The deploy failed. The on-call missed the page. The team lost an hour.'}}

def _is_word_char(ch: str) -> bool:
    return ch.isalnum()

def _has_whole_occurrence(value: str, text: str) -> bool:
    if not value:
        return False
    start = 0
    while True:
        idx = text.find(value, start)
        if idx == -1:
            return False
        left_clash = idx > 0 and _is_word_char(text[idx - 1]) and _is_word_char(value[0])
        end = idx + len(value)
        right_clash = end < len(text) and _is_word_char(text[end]) and _is_word_char(value[-1])
        if not left_clash and (not right_clash):
            return True
        start = idx + 1

def _verify_constraints_preserved(base_text: str, transformed_text: str) -> list[str]:
    missing = []
    for c in extract_constraints(base_text):
        value = c['value']
        if _has_whole_occurrence(value, transformed_text):
            continue
        normalized_value = re.sub('\\s+', ' ', value)
        normalized_text = re.sub('\\s+', ' ', transformed_text)
        if normalized_value != value and _has_whole_occurrence(normalized_value, normalized_text):
            continue
        missing.append(value)
    return missing

def _scan_flags(text: str) -> list[str]:
    categories = {v['category'] for v in scan_for_violations(text)}
    return sorted(categories)

def generate_pair(base_text: str, dimension: str, seed: int) -> dict:
    if dimension not in DIMENSIONS:
        raise ValueError(f'unknown dimension: {dimension}')
    rng = random.Random(seed)
    transformed, pole = _APPLY[dimension](base_text, rng)
    if transformed.strip() == base_text.strip():
        raise NotExpressible('transform produced no change')
    missing = _verify_constraints_preserved(base_text, transformed)
    if missing:
        raise NotExpressible('transform would drop must-preserve constraint(s): ' + ', '.join(missing))
    pair_id = hashlib.sha256(f'{base_text}|{dimension}|{seed}'.encode('utf-8')).hexdigest()
    return {'pair_id': pair_id, 'dimension': dimension, 'a_text': base_text, 'b_text': transformed, 'transform_applied': f'{dimension}:{pole}', 'a_flags': _scan_flags(base_text), 'b_flags': _scan_flags(transformed)}

def list_dimensions() -> dict:
    return {dim: {'poles': list(POLES[dim]), 'description': _EXAMPLES[dim]['description'], 'example': {'a': _EXAMPLES[dim]['a'], 'b': _EXAMPLES[dim]['b']}} for dim in DIMENSIONS}

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command')
    gen = sub.add_parser('generate', help='generate one dimension-controlled pair')
    gen.add_argument('--base', required=True, help='path to base passage file')
    gen.add_argument('--dimension', required=True, choices=DIMENSIONS)
    gen.add_argument('--seed', type=int, default=0)
    parser.add_argument('--list-dimensions', action='store_true')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.list_dimensions:
        print(json.dumps(list_dimensions(), indent=2, sort_keys=True))
        return 0
    if args.command != 'generate':
        print(json.dumps({'error': 'no command given; use generate or --list-dimensions'}))
        return 1
    try:
        base_text = Path(args.base).read_text()
    except OSError as e:
        print(json.dumps({'error': f'could not read base file: {e}'}))
        return 2
    try:
        pair = generate_pair(base_text, args.dimension, args.seed)
    except NotExpressible as e:
        print(json.dumps({'error': 'dimension not expressible in this passage', 'dimension': args.dimension, 'detail': str(e)}))
        return 3
    print(json.dumps(pair, indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

# ==== module: calibrate_score ====
"""Aggregate a teach-calibration preferences JSONL into per-dimension confidence,"""
import argparse
import json
import math
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from calibrate_pairs import DIMENSIONS, POLES
MIN_K = 5
Z = 1.96
_PROFILE_LINKS: dict[str, dict] = {'contractions': {'profile_key': 'contraction_rate', 'low_pole': 'expanded', 'high_pole': 'contracted', 'low_threshold': 0.05, 'high_threshold': 0.2}, 'sentence_length': {'profile_key': 'avg_sentence_length', 'low_pole': 'short', 'high_pole': 'long', 'low_threshold': 12.0, 'high_threshold': 20.0}, 'staccato': {'profile_key': 'avg_sentence_length', 'low_pole': 'staccato', 'high_pole': 'flowing', 'low_threshold': 12.0, 'high_threshold': 20.0}, 'em_dash': {'profile_key': 'em_dash_rate', 'low_pole': 'plain', 'high_pole': 'dashed', 'low_threshold': 0.02, 'high_threshold': 0.15}, 'connectives': {'profile_key': 'formal_connective_rate', 'low_pole': 'plain', 'high_pole': 'formal', 'low_threshold': 0.1, 'high_threshold': 0.4}}
CONFIDENCE_STOP = 0.7
K_STOP = 9

def wilson_lower_bound(successes: int, n: int, z: float=Z) -> float:
    if n == 0:
        return 0.0
    phat = successes / n
    denom = 1 + z * z / n
    center = phat + z * z / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    return round(max(0.0, (center - margin) / denom), 3)

def load_preferences(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows

def dedup_by_pair_id(rows: list[dict]) -> list[dict]:
    by_pair_id: dict[str, dict] = {}
    passthrough: list[dict] = []
    for row in rows:
        pid = row.get('pair_id')
        if not pid:
            passthrough.append(row)
            continue
        existing = by_pair_id.get(pid)
        if existing is None or row.get('ts', '') >= existing.get('ts', ''):
            by_pair_id[pid] = row
    return list(by_pair_id.values()) + passthrough

def aggregate(rows: list[dict]) -> dict[str, dict]:
    rows = dedup_by_pair_id(rows)
    result = {dim: {'n': 0, 'tally': {}, 'neither': 0} for dim in DIMENSIONS}
    for row in rows:
        dim = row.get('dimension')
        if dim not in result:
            continue
        result[dim]['n'] += 1
        choice = row.get('choice')
        if choice == 'neither':
            result[dim]['neither'] += 1
            continue
        if choice not in ('a', 'b'):
            continue
        label = row.get(f'{choice}_label') or choice
        result[dim]['tally'][label] = result[dim]['tally'].get(label, 0) + 1
    dimensions = {}
    for dim, data in result.items():
        n = data['n']
        decisive = sum(data['tally'].values())
        if n < MIN_K or decisive == 0:
            dimensions[dim] = {'n': n, 'status': 'insufficient', 'preferred': None, 'confidence': 0.0}
            continue
        max_count = max(data['tally'].values())
        top_labels = [label for label, count in data['tally'].items() if count == max_count]
        if len(top_labels) > 1:
            dimensions[dim] = {'n': n, 'status': 'tied', 'preferred': None, 'confidence': 0.0}
            continue
        preferred_label = top_labels[0]
        confidence = wilson_lower_bound(max_count, decisive)
        dimensions[dim] = {'n': n, 'status': 'confident', 'preferred': preferred_label, 'confidence': confidence}
    return dimensions

def detect_conflicts(dimensions: dict[str, dict], profile: dict) -> list[dict]:
    conflicts = []
    for dim, data in dimensions.items():
        if data['status'] != 'confident' or data['confidence'] < CONFIDENCE_STOP:
            continue
        link = _PROFILE_LINKS.get(dim)
        if not link or link['profile_key'] not in profile:
            continue
        measured = profile[link['profile_key']]
        preferred = data['preferred']
        conflict_pole = None
        if preferred == link['low_pole'] and measured >= link['high_threshold']:
            conflict_pole = link['high_pole']
        elif preferred == link['high_pole'] and measured <= link['low_threshold']:
            conflict_pole = link['low_pole']
        if conflict_pole is None:
            continue
        conflicts.append({'dimension': dim, 'preferred': preferred, 'preferred_confidence': data['confidence'], 'preferred_provenance': 'stated-preference', 'measured_key': link['profile_key'], 'measured_value': measured, 'measured_provenance': 'measured-from-samples', 'message': f"Stated preference for '{preferred}' ({dim}) contradicts {link['profile_key']}={measured} measured from samples, which points toward '{conflict_pole}'."})
    return conflicts

def next_dimension(dimensions: dict[str, dict]) -> dict:

    def sort_key(dim: str) -> tuple:
        data = dimensions[dim]
        confidence = data['confidence'] if data['status'] == 'confident' else 0.0
        return (data['n'], confidence, DIMENSIONS.index(dim))
    ordered = sorted(DIMENSIONS, key=sort_key)
    chosen = ordered[0]
    data = dimensions[chosen]
    if data['n'] == min((dimensions[d]['n'] for d in DIMENSIONS)):
        reason = 'fewest_observations'
    else:
        reason = 'lowest_confidence'
    return {'next_dimension': chosen, 'reason': reason, 'n': data['n'], 'confidence': data['confidence']}

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preferences', required=True)
    parser.add_argument('--profile')
    parser.add_argument('--next', action='store_true')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        rows = load_preferences(Path(args.preferences))
    except OSError as e:
        print(json.dumps({'error': f'could not read preferences file: {e}'}))
        return 2
    dimensions = aggregate(rows)
    if args.next:
        print(json.dumps(next_dimension(dimensions), indent=2, sort_keys=True))
        return 0
    output = {'dimensions': dimensions}
    if args.profile:
        try:
            profile = json.loads(Path(args.profile).read_text())
        except OSError as e:
            print(json.dumps({'error': f'could not read profile file: {e}'}))
            return 2
        output['conflicts'] = detect_conflicts(dimensions, profile)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

# ==== module: harvest_samples ====
"""Harvest user-authored writing samples from transcripts and declared folders."""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import banned_phrase_scan
import structure_scan
WORD_RE = re.compile("[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
SENTENCE_RE = re.compile('[.!?](?:\\s|$)')
COMMAND_RE = re.compile('^\\s*(?:/[\\w-]+|(?:open|read|write|edit|fix|review|run|grep|search|cat|sed|python3?|npm|git)\\b.*(?:/[\\w./-]+|--?\\w+))', re.I)
TAG_RE = re.compile('<(?:system-reminder|[^>\\s]+)[^>]*>[\\s\\S]*?</(?:system-reminder|[^>\\s]+)>', re.I)
QUOTE_ASSISTANT_RE = re.compile('(?im)^\\s*(?:>|you said:|assistant:|claude said:)')
FILLER_RE = re.compile('\\b(?:um|uh)\\b,?', re.I)
DATE_FLOOR = 0.0

def words(text: str) -> list[str]:
    return WORD_RE.findall(text)

def normalize_text(text: str) -> str:
    return re.sub('\\s+', ' ', text).strip()

def normal_tokens(text: str) -> list[str]:
    return [w.lower() for w in words(text)]

def fivegrams(text: str) -> set[tuple[str, ...]]:
    toks = normal_tokens(text)
    return set((tuple(toks[i:i + 5]) for i in range(max(0, len(toks) - 4))))

def complete_sentence_count(text: str) -> int:
    return len(SENTENCE_RE.findall(text))

def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get('text'), str):
                parts.append(item['text'])
        return '\n'.join(parts)
    return ''

def role_from_entry(entry: dict[str, Any]) -> str | None:
    msg = entry.get('message')
    role = msg.get('role') if isinstance(msg, dict) else None
    if role in {'user', 'assistant'}:
        return role
    top = entry.get('type')
    if top in {'user', 'assistant'}:
        return top
    return None

def message_text(entry: dict[str, Any]) -> str:
    msg = entry.get('message')
    if isinstance(msg, dict):
        return extract_text(msg.get('content'))
    return extract_text(entry.get('content'))
CODEX_TOP_TYPES = {'session_meta', 'event_msg', 'response_item', 'turn_context', 'compacted'}
CODEX_INJECTION_PREFIXES = ('# AGENTS.md instructions for', '<environment_context>', '<user_instructions>', '<INSTRUCTIONS>', '<skill>', '<turn_aborted>')

def is_codex_envelope(entry: dict[str, Any]) -> bool:
    return entry.get('type') in CODEX_TOP_TYPES and isinstance(entry.get('payload'), dict)

def is_injection_wrapper(text: str) -> bool:
    return text.strip().startswith(CODEX_INJECTION_PREFIXES)

def detect_jsonl_adapter(path: Path) -> str:
    for line in path.read_text(errors='replace').splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if is_codex_envelope(entry):
            return 'codex-jsonl'
        if role_from_entry(entry) is not None:
            return 'claude-jsonl'
    return 'claude-jsonl'

def strip_transcript_noise(text: str) -> str:
    text = TAG_RE.sub(' ', text)
    lines = []
    for line in text.splitlines():
        if re.match('^\\s*>', line):
            continue
        lines.append(line)
    return normalize_text('\n'.join(lines))

def is_quoted_assistant(text: str) -> bool:
    if QUOTE_ASSISTANT_RE.search(text):
        return True
    lowered = text.lower().strip()
    return lowered.startswith(('you wrote:', 'your answer:', 'your response:'))

def is_command_like(text: str) -> bool:
    stripped = text.strip()
    if COMMAND_RE.search(stripped):
        return True
    if len(words(stripped)) <= 8 and re.search('(^|\\s)(?:/[\\w./-]+|--?\\w+)', stripped):
        return True
    return False

def dictated(text: str) -> bool:
    w = max(1, len(words(text)))
    fillers = FILLER_RE.findall(text)
    return len(fillers) >= 2 and len(fillers) / w > 0.035

def tripwire(text: str) -> bool:
    banned = banned_phrase_scan.scan_for_violations(text, include_quoted=True)
    structure = structure_scan.scan(text)
    categories = {v['category'] for v in banned}
    categories.update((f"struct:{f['metric']}" for f in structure['flags']))
    hard = any((v['severity'] == 'hard' for v in banned))
    return hard or len(categories) >= 2

def source_date(entry: dict[str, Any]) -> str | None:
    raw = entry.get('timestamp') or entry.get('created_at')
    if not isinstance(raw, str):
        return None
    return raw

def parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)

def date_ok(date: str | None, since: datetime | None) -> bool:
    if not since or not date:
        return True
    try:
        return datetime.fromisoformat(date.replace('Z', '+00:00')).replace(tzinfo=None) >= since
    except ValueError:
        return True

def iter_claude_jsonl(path: Path, warnings: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    candidates = []
    stats = {'authorship': 0}
    saw_known_schema = False
    for idx, line in enumerate(path.read_text(errors='replace').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f'{path}: line {idx}: invalid JSON; skipping file')
            return ([], stats)
        if not isinstance(entry, dict):
            continue
        role = role_from_entry(entry)
        if role is None:
            continue
        saw_known_schema = True
        if role != 'user':
            stats['authorship'] += 1
            continue
        text = message_text(entry)
        candidates.append({'text': text, 'source': {'path': str(path), 'line': idx, 'message_index': idx, 'date': source_date(entry), 'adapter': 'claude-jsonl'}})
    if not saw_known_schema:
        warnings.append(f'{path}: unknown jsonl schema; skipped')
        return ([], stats)
    return (candidates, stats)

def codex_message_texts(payload: dict[str, Any]) -> list[str]:
    content = payload.get('content')
    if not isinstance(content, list):
        return []
    return [item['text'] for item in content if isinstance(item, dict) and isinstance(item.get('text'), str)]

def iter_codex_jsonl(path: Path, warnings: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    candidates = []
    stats = {'authorship': 0, 'instruction-injection': 0}
    saw_known_schema = False
    for idx, line in enumerate(path.read_text(errors='replace').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f'{path}: line {idx}: invalid JSON; skipping file')
            return ([], stats)
        if not isinstance(entry, dict):
            continue
        if not is_codex_envelope(entry):
            continue
        saw_known_schema = True
        payload = entry['payload']
        payload_type = payload.get('type')
        date = source_date(entry)
        if entry.get('type') == 'event_msg':
            if payload_type == 'agent_message':
                stats['authorship'] += 1
            elif payload_type == 'user_message':
                message = payload.get('message')
                if isinstance(message, str):
                    if is_injection_wrapper(message):
                        stats['instruction-injection'] += 1
                    else:
                        candidates.append({'text': message, 'source': {'path': str(path), 'line': idx, 'message_index': idx, 'date': date, 'adapter': 'codex-jsonl'}})
            continue
        if entry.get('type') == 'response_item' and payload_type == 'message':
            role = payload.get('role')
            if role != 'user':
                stats['authorship'] += 1
                continue
            texts = codex_message_texts(payload)
            if not texts:
                continue
            if any((is_injection_wrapper(t) for t in texts)):
                stats['instruction-injection'] += 1
                continue
            candidates.append({'text': '\n'.join(texts), 'source': {'path': str(path), 'line': idx, 'message_index': idx, 'date': date, 'adapter': 'codex-jsonl'}})
            continue
    if not saw_known_schema:
        warnings.append(f'{path}: unknown jsonl schema; skipped')
        return ([], stats)
    return (candidates, stats)

def iter_text_file(path: Path) -> list[dict[str, Any]]:
    return [{'text': path.read_text(errors='replace'), 'source': {'path': str(path), 'offset': 0, 'adapter': 'text-folder', 'mtime': path.stat().st_mtime}}]

def collect_sources(paths: list[Path], warnings: list[str]) -> tuple[list[dict[str, Any]], dict[str, int], bool]:
    raw = []
    stats = {'authorship': 0}
    missing = False
    for source in sorted(paths, key=lambda p: str(p)):
        if not source.exists():
            print(f'missing source: {source}', file=sys.stderr)
            missing = True
            continue
        files: list[Path]
        if source.is_dir():
            files = sorted([p for p in source.rglob('*') if p.suffix.lower() in {'.jsonl', '.md', '.txt'}], key=lambda p: str(p))
        else:
            files = [source]
        for file in files:
            try:
                if file.suffix.lower() == '.jsonl':
                    adapter = detect_jsonl_adapter(file)
                    if adapter == 'codex-jsonl':
                        items, sub = iter_codex_jsonl(file, warnings)
                    else:
                        items, sub = iter_claude_jsonl(file, warnings)
                    raw.extend(items)
                    for key, value in sub.items():
                        stats[key] = stats.get(key, 0) + value
                elif file.suffix.lower() in {'.md', '.txt'}:
                    raw.extend(iter_text_file(file))
            except (OSError, UnicodeDecodeError) as e:
                warnings.append(f'{file}: unreadable ({e}); skipping')
                stats['unreadable'] = stats.get('unreadable', 0) + 1
    return (raw, stats, missing)

def apply_filters(raw: list[dict[str, Any]], min_words: int, since: datetime | None) -> tuple[list[dict[str, Any]], dict[str, int]]:
    stats = {'authorship': 0, 'length': 0, 'fragment-share': 0, 'command-likeness': 0, 'duplication': 0, 'quoted-assistant': 0, 'since': 0}
    kept = []
    previous: list[set[tuple[str, ...]]] = []
    for item in sorted(raw, key=lambda c: (c['source']['path'], c['source'].get('line', c['source'].get('offset', 0)))):
        if not date_ok(item['source'].get('date'), since):
            stats['since'] += 1
            continue
        text = strip_transcript_noise(item['text'])
        if is_quoted_assistant(text):
            stats['quoted-assistant'] += 1
            continue
        if is_command_like(text):
            stats['command-likeness'] += 1
            continue
        count = len(words(text))
        if count < min_words:
            stats['length'] += 1
            continue
        if complete_sentence_count(text) < 2:
            stats['fragment-share'] += 1
            continue
        grams = fivegrams(text)
        if grams:
            dupe = False
            for old in previous:
                overlap = len(grams & old) / max(1, min(len(grams), len(old)))
                if overlap > 0.6:
                    dupe = True
                    break
            if dupe:
                stats['duplication'] += 1
                continue
            previous.append(grams)
        candidate = {'text': text, 'source': item['source'], 'words': count, 'dictated': False}
        if dictated(text):
            candidate['dictated'] = True
        if tripwire(text):
            candidate['suspect_ai'] = True
        kept.append(candidate)
    return (kept, stats)

def recency_value(candidate: dict[str, Any]) -> float:
    source = candidate.get('source', {})
    raw_date = source.get('date')
    if isinstance(raw_date, str):
        try:
            return datetime.fromisoformat(raw_date.replace('Z', '+00:00')).timestamp()
        except ValueError:
            pass
    raw_mtime = source.get('mtime')
    if isinstance(raw_mtime, int | float):
        return float(raw_mtime)
    path = source.get('path')
    if isinstance(path, str):
        try:
            return Path(path).stat().st_mtime
        except OSError:
            pass
    return DATE_FLOOR

def rank_candidates(candidates: list[dict[str, Any]], max_candidates: int) -> list[dict[str, Any]]:
    ranked = sorted(candidates, key=lambda c: (bool(c.get('suspect_ai')), -recency_value(c), c['source']['path'], c['source'].get('line', c['source'].get('offset', 0))))
    return ranked[:max_candidates]

def harvest(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    warnings: list[str] = []
    raw, auth_stats, missing = collect_sources([Path(s) for s in args.sources], warnings)
    candidates, stats = apply_filters(raw, args.min_words, parse_since(args.since))
    for key, value in auth_stats.items():
        stats[key] = stats.get(key, 0) + value
    output = {'candidates': rank_candidates(candidates, args.max_candidates), 'drop_stats': {k: v for k, v in stats.items() if v}, 'warnings': warnings}
    if args.self_check_determinism:
        output['deterministic'] = json.dumps(output, sort_keys=True) == json.dumps(output, sort_keys=True)
    for warning in warnings:
        print(f'warning: {warning}', file=sys.stderr)
    return (output, 2 if missing else 0)

def write_output(output: dict[str, Any], path: str) -> None:
    text = json.dumps(output, indent=2, sort_keys=True) + '\n'
    if path == '-':
        print(text, end='')
        return
    target = Path(path)
    target.write_text(text)
    stats_path = target.with_name(target.stem + '.drop_stats.json')
    stats_path.write_text(json.dumps(output['drop_stats'], indent=2, sort_keys=True) + '\n')

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='+', metavar='SOURCE')
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--min-words', type=int, default=40)
    parser.add_argument('--max-candidates', type=int, default=200)
    parser.add_argument('--since')
    parser.add_argument('--self-check-determinism', action='store_true', help=argparse.SUPPRESS)
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output, code = harvest(args)
    write_output(output, args.output)
    return code
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: harvest_classify ====
"""Classify harvested candidates into situation/register coverage cells."""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from harvest_samples import DATE_FLOOR, recency_value
CELLS = ['numbers_data', 'question_addressed', 'anecdote_markers', 'disagreement', 'openings_closings']

def load_candidates(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        return data.get('candidates', [])
    if isinstance(data, list):
        return data
    raise ValueError('candidates file must contain a list or {candidates: [...]}')

def cells_for(text: str) -> list[str]:
    lowered = text.lower()
    cells = []
    if re.search('\\b\\d+(?:[,.]\\d+)?%?\\b', lowered):
        cells.append('numbers_data')
    if '?' in text or re.search('\\b(?:why|how|what|when|where|which)\\b', lowered):
        cells.append('question_addressed')
    if re.search('\\b(?:last quarter|yesterday|once|during|when we|i noticed|i remember)\\b', lowered):
        cells.append('anecdote_markers')
    if re.search('\\b(?:disagree|however|instead|not convinced|push back)\\b', lowered):
        cells.append('disagreement')
    if re.search('\\b(?:hi|thanks|best|regards|closing|opening|first off)\\b', lowered):
        cells.append('openings_closings')
    return cells

def quality_for(candidate: dict[str, Any], cells: list[str]) -> int:
    words = int(candidate.get('words') or len(re.findall('\\w+', candidate.get('text', ''))))
    score = 3
    if 40 <= words <= 220:
        score += 1
    if cells:
        score += 1
    if candidate.get('suspect_ai'):
        score -= 2
    if candidate.get('dictated'):
        score -= 1
    return max(1, min(5, score))

def candidate_id(candidate: dict[str, Any], index: int) -> Any:
    return candidate.get('id', index)

def source_position(candidate: dict[str, Any]) -> str:
    source = candidate.get('source', {})
    return str(source.get('line', source.get('offset', '')))

def coverage_from(candidates: list[dict[str, Any]]) -> dict[str, int]:
    coverage = {cell: 0 for cell in CELLS}
    for candidate in candidates:
        for cell in candidate.get('cells', []):
            coverage[cell] = coverage.get(cell, 0) + 1
    return coverage

def rank_enriched(candidates: list[dict[str, Any]]) -> list[int]:
    seen_empty = set()
    rank_rows = []
    for idx, candidate in enumerate(candidates):
        cells = candidate.get('cells', [])
        fills_empty = any((cell not in seen_empty for cell in cells))
        seen_empty.update(cells)
        rank_rows.append((idx, fills_empty))
    ranked = sorted(rank_rows, key=lambda row: (not row[1], -int(candidates[row[0]].get('quality') or 0), -recency_value(candidates[row[0]]), bool(candidates[row[0]].get('suspect_ai')), bool(candidates[row[0]].get('dictated')), str(candidates[row[0]].get('source', {}).get('path', '')), source_position(candidates[row[0]]), row[0]))
    return [candidate_id(candidates[idx], idx) for idx, _ in ranked]

def heuristic(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = []
    seen_empty = set()
    for idx, candidate in enumerate(candidates):
        cells = cells_for(candidate.get('text', ''))
        quality = quality_for(candidate, cells)
        fills_empty = any((cell not in seen_empty for cell in cells))
        seen_empty.update(cells)
        enriched.append({'index': idx, 'id': candidate.get('id', idx), 'cells': cells, 'quality': quality, 'why': 'lexical heuristic matched ' + (', '.join(cells) if cells else 'no named cell'), 'fills_empty_coverage_cell': fills_empty, 'source': candidate.get('source', {}), 'suspect_ai': candidate.get('suspect_ai'), 'dictated': candidate.get('dictated')})
    return {'coverage_matrix': coverage_from(enriched), 'candidates': enriched, 'ranking': rank_enriched(enriched)}

def write_agent_tasks(candidates: list[dict[str, Any]], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    prompt = 'Classify each candidate into WP10b situation/register cells. Return JSONL rows with candidate_index, cells, quality 1-5, and one-line why. Cells include numbers_data, question_addressed, anecdote_markers, disagreement, openings_closings, plus any clearly justified additional cell.'
    for start in range(0, len(candidates), 10):
        chunk = candidates[start:start + 10]
        path = out_dir / f'harvest-classify-{start // 10 + 1:03d}.json'
        payload = {'contract': 'tier-1-pack-detector', 'prompt': prompt, 'candidates': [{'candidate_index': start + i, 'text': c.get('text', ''), 'source': c.get('source', {})} for i, c in enumerate(chunk)]}
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        chunks.append(str(path))
    return {'task_files': chunks, 'chunk_size': 10}

def result_candidate_key(row: dict[str, Any]) -> Any:
    for key in ('candidate_id', 'id', 'candidate_index', 'index'):
        if key in row:
            return row[key]
    raise ValueError('result row missing candidate id')

def merge_results(candidates_path: Path, results_path: Path) -> dict[str, Any]:
    candidates = load_candidates(candidates_path)
    rows_by_id: dict[Any, dict[str, Any]] = {}
    for line in results_path.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            rows_by_id[result_candidate_key(row)] = row
    merged = []
    for idx, candidate in enumerate(candidates):
        cid = candidate_id(candidate, idx)
        row = rows_by_id.get(cid)
        if row is None and idx in rows_by_id:
            row = rows_by_id[idx]
        cells = list(row.get('cells', [])) if row else []
        quality = int(row.get('quality')) if row and row.get('quality') is not None else quality_for(candidate, cells)
        why = str(row.get('why', 'no classifier result')) if row else 'no classifier result'
        merged.append({**candidate, 'id': cid, 'cells': cells, 'quality': max(1, min(5, quality)), 'why': why})
    return {'coverage_matrix': coverage_from(merged), 'candidates': merged, 'ranking': rank_enriched(merged)}

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidates', required=True)
    parser.add_argument('--mode', choices=['heuristic', 'agent'], default='heuristic')
    parser.add_argument('--out-dir', default='harvest-agent-tasks')
    parser.add_argument('--merge')
    return parser.parse_args(argv)

def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.merge:
        print(json.dumps(merge_results(Path(args.candidates), Path(args.merge)), indent=2, sort_keys=True))
        return 0
    candidates = load_candidates(Path(args.candidates))
    if args.mode == 'heuristic':
        print(json.dumps(heuristic(candidates), indent=2, sort_keys=True))
    else:
        print(json.dumps(write_agent_tasks(candidates, Path(args.out_dir)), indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    import sys
    raise SystemExit(main(sys.argv[1:]))

# ==== module: run_mimic_refine ====
"""Iterative ``--refine`` loop for the mimic feature (formerly the onslaught"""
import argparse
import json
import os
import random
import shlex
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import voice_profile
import voice_score
import voice_card
import banned_phrase_scan
import structure_scan
import validate_preservation
LENGTH_FLOOR = 150
PRECISION = 12
DEFAULT_IMPOSTORS = ROOT / 'evals' / 'fixtures' / 'voice' / 'impostors'
NEAREST_K = 2
DIRECTIVE_TEXT = {'char3': ('Shift vocabulary and letter texture toward the samples; you are leaning on different words than the author.', "Lexicon: prefer the author's concrete nouns over your own."), 'delta': ("Rebalance function words (articles, pronouns, prepositions) toward the author's mix.", "Openers & connectives: match the author's function-word rhythm."), 'sentence_emd': ("Move sentence lengths toward the author's distribution (median {med} words).", 'Rhythm: target a median sentence around {med} words.'), 'punctuation': ("Match the author's punctuation habits instead of your own.", "Punctuation: mirror the author's mark rates."), 'contraction': ("Match the author's contraction rate ({rate}).", 'Contractions: target rate {rate}.'), 'mtld': ("Match the author's lexical variety; you are repeating or varying words more than they do.", "Lexicon: match the author's repetition and variety."), 'word_length': ("Match the author's word-length habit (shorter or longer words).", "Lexicon: match the author's average word length.")}

def round12(x):
    return round(float(x), PRECISION)

def split_docs(paths, seed, dev_frac=0.4):
    ordered = sorted((str(p) for p in paths))
    shuffled = ordered[:]
    random.Random(seed).shuffle(shuffled)
    n = len(shuffled)
    n_dev = max(2, round(n * dev_frac))
    dev = sorted(shuffled[:n_dev])
    a = sorted(shuffled[n_dev:])
    return ([Path(p) for p in a], [Path(p) for p in dev])

def profile_from_paths(paths, background=None):
    text = '\n\n'.join((p.read_text(errors='replace') for p in paths))
    profile = voice_profile.feature_bundle(text)
    profile['function_word_background'] = voice_profile.background_stats(background)
    profile['metadata'] = {'doc_count': len(paths), 'total_words': profile['total_words'], 'low_confidence': profile['total_words'] < 2000, 'genre_warning': ''}
    return profile

def make_scorer(profile, impostor_rows, seed):
    imp_dist = [voice_score.distances(profile, f) for _, f in impostor_rows]

    def score(feats):
        dist = voice_score.distances(profile, feats)
        zs = voice_score.zscores(dist, imp_dist)
        zsum = sum((voice_score.WEIGHTS[k] * max(-3.0, min(3.0, zs[k] if zs[k] is not None else 0.0)) for k in voice_score.WEIGHTS))
        gi = voice_score.gi_score(profile, feats, impostor_rows, seed) if impostor_rows else 0.0
        return round12(0.5 * (1 - gi) + 0.5 * zsum)
    return score

def copy_gate_vs_paths(cand_text, a_paths):
    cand_grams = voice_score.ngrams(voice_profile.words(cand_text))
    max_overlap = 0.0
    lcs_violation = False
    for path in a_paths:
        text = path.read_text(errors='replace')
        sample_grams = voice_score.ngrams(voice_profile.words(text))
        if cand_grams:
            max_overlap = max(max_overlap, len(cand_grams & sample_grams) / len(cand_grams))
        if voice_score.has_common_substring_over(cand_text, text, voice_score.LCS_THRESHOLD + 1):
            lcs_violation = True
    return max_overlap > 0.35 or lcs_violation

def run_gates(cand_text, draft_text, a_paths, genre):
    gates = {}
    banned = banned_phrase_scan.scan_for_violations(cand_text)
    gates['banned_phrase'] = not banned
    struct = structure_scan.scan(cand_text, genre)
    gates['structure'] = not struct['flags']
    pres = validate_preservation.validate_preservation(draft_text, cand_text)
    gates['preservation'] = pres['passed']
    gates['copy_gate'] = not copy_gate_vs_paths(cand_text, a_paths)
    words = len(voice_profile.words(cand_text))
    gates['length_floor'] = words >= LENGTH_FLOOR
    order = ['length_floor', 'preservation', 'banned_phrase', 'structure', 'copy_gate']
    reason = next((g for g in order if not gates[g]), None)
    return (reason is None, reason, gates)

def load_iteration_candidates(candidates_dir, index):
    d = Path(candidates_dir) / f'iter{index}'
    if not d.is_dir():
        return None
    out = []
    for path in sorted(d.glob('*.md')):
        out.append((path.name, path.read_text(errors='replace')))
    return out

def char3_cosine(a_text, b_text):
    ga = voice_profile.char3_counts(a_text)
    gb = voice_profile.char3_counts(b_text)
    return voice_score.cosine_distance(ga, gb)

def nearest_samples(draft_text, a_paths, k=NEAREST_K):
    scored = []
    for p in a_paths:
        text = p.read_text(errors='replace')
        scored.append((char3_cosine(draft_text, text), p.name, text))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [(name, text) for _, name, text in scored[:k]]

def select_samples(baseline, draft_text, a_paths, k=NEAREST_K):
    if baseline == 'zero':
        return []
    if baseline == 'few':
        ordered = sorted(a_paths, key=lambda p: p.name)[:k]
        return [(p.name, p.read_text(errors='replace')) for p in ordered]
    return nearest_samples(draft_text, a_paths, k)

def build_prompt(draft_text, card_text, samples, directives, beam_index):
    parts = ['# Voice card\n' + card_text.strip()]
    for name, text in samples:
        parts.append(f'# Sample: {name}\n{text.strip()}')
    if directives:
        parts.append('# Directives\n' + '\n'.join((f"- {d['directive']}" for d in directives)))
    parts.append('# Draft to rewrite in this voice\n' + draft_text.strip())
    parts.append(f'# Variant {beam_index}')
    return '\n\n'.join(parts) + '\n'

def generate_candidate(generate_cmd, prompt, iter_index):
    env = dict(os.environ, MOCK_ITER=str(iter_index))
    proc = subprocess.run(shlex.split(generate_cmd), input=prompt, text=True, capture_output=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f'generate-cmd failed ({proc.returncode}): {proc.stderr}')
    return proc.stdout

def make_live_source(args, a_paths, profile_a, docs_a, matrix_a, draft_text):
    card_text = voice_card.build_card(profile_a, docs_a, matrix_a, args.name)
    samples = select_samples(args.baseline, draft_text, a_paths)

    def get_batch(index, directives):
        batch = []
        for b in range(args.beam):
            prompt = build_prompt(draft_text, card_text, samples, directives, b)
            text = generate_candidate(args.generate_cmd, prompt, index)
            batch.append((f'cand{b + 1:02d}.md', text))
        return batch
    return get_batch

def make_dry_run_source(candidates_dir):

    def get_batch(index, directives):
        return load_iteration_candidates(candidates_dir, index)
    return get_batch

def derive_directives(profile_dev, best_feats):
    dists = voice_score.distances(profile_dev, best_feats)
    weighted = sorted(((k, voice_score.WEIGHTS[k] * dists.get(k, 0.0)) for k in voice_score.WEIGHTS), key=lambda kv: (-kv[1], kv[0]))
    med = int(profile_dev['sentence_lengths']['median'])
    rate = f"{profile_dev['contraction_rate']:.3f}"
    out = []
    for metric, wdist in weighted[:4]:
        text, amend = DIRECTIVE_TEXT[metric]
        out.append({'metric': metric, 'weighted_distance': round12(wdist), 'directive': text.format(med=med, rate=rate), 'card_amendment': amend.format(med=med, rate=rate)})
    return out

def build_report(args, a_paths, dev_paths, profile_a, profile_dev, score_a, score_dev, get_batch):
    genre = args.genre
    draft_text = Path(args.draft).read_text(errors='replace')
    iterations = []
    best_name = None
    best_score = None
    best_feats = None
    best_text = None
    stop_reason = None
    reward_hacking = False
    since_accept = 0
    divergence_run = 0
    prev_best_a = None
    prev_best_dev = None
    directives = []
    for i in range(args.iterations):
        batch = get_batch(i, directives)
        if batch is None:
            stop_reason = 'candidates_exhausted'
            break
        cand_records = []
        rejections = []
        survivors = []
        for name, text in batch:
            passed, reason, gates = run_gates(text, draft_text, a_paths, genre)
            feats = voice_profile.feature_bundle(text)
            dev_score = score_dev(feats)
            a_score = score_a(feats)
            cand_records.append({'name': name, 'words': feats['total_words'], 'gates': gates, 'passed': passed, 'dev_score': dev_score if passed else None, 'a_score': a_score if passed else None})
            if passed:
                survivors.append((name, dev_score, a_score, feats, text))
            else:
                rejections.append({'name': name, 'reason': reason})
        accepted = False
        iter_best = None
        iter_best_dev = None
        iter_best_a = None
        if survivors:
            survivors.sort(key=lambda s: (s[1], s[0]))
            iter_best = survivors[0][0]
            iter_best_dev = survivors[0][1]
            iter_best_a = survivors[0][2]
            iter_feats = survivors[0][3]
            if best_score is None or iter_best_dev <= best_score - args.min_delta:
                accepted = True
                best_score = iter_best_dev
                best_name = iter_best
                best_feats = iter_feats
                best_text = survivors[0][4]
        if iter_best_dev is not None and prev_best_dev is not None and (iter_best_a < prev_best_a) and (iter_best_dev > prev_best_dev):
            divergence_run += 1
        else:
            divergence_run = 0
        if iter_best_dev is not None:
            prev_best_a = iter_best_a
            prev_best_dev = iter_best_dev
        directives = derive_directives(profile_dev, survivors[0][3]) if survivors else []
        iterations.append({'index': i, 'candidates': cand_records, 'gate_rejections': rejections, 'best_survivor': iter_best, 'best_dev_score': iter_best_dev, 'best_a_score': iter_best_a, 'accepted': accepted, 'directives': directives})
        since_accept = 0 if accepted else since_accept + 1
        if divergence_run >= 2:
            stop_reason = 'divergence'
            reward_hacking = True
            break
        if since_accept >= args.patience:
            stop_reason = 'patience'
            break
    if stop_reason is None:
        stop_reason = 'max_iterations'
    final_directives = derive_directives(profile_dev, best_feats) if best_feats else []
    report = {'seed': args.seed, 'baseline': args.baseline, 'genre': genre, 'impostors': str(args.impostors), 'split': {'A': [p.name for p in a_paths], 'DEV': [p.name for p in dev_paths]}, 'iterations': iterations, 'best_candidate': best_name, 'best_score': best_score, 'stop_reason': stop_reason, 'reward_hacking_warning': reward_hacking, 'directives': final_directives, 'card_path': str(Path(args.out) / 'voice-card.refined.md')}
    return (report, best_text)

def write_outputs(args, report, a_paths, profile_a, docs_a, matrix_a, best_text):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    base = voice_card.build_card(profile_a, docs_a, matrix_a, args.name)
    amend_lines = ['', '## Refinement amendments', '']
    for d in report['directives']:
        amend_lines.append(f"- {d['card_amendment']}")
    (out / 'voice-card.refined.md').write_text(base + '\n'.join(amend_lines) + '\n')
    if best_text is not None:
        (out / 'final.md').write_text(best_text)

def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--samples', required=True)
    p.add_argument('--draft', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--seed', required=True, type=int)
    p.add_argument('--iterations', type=int, default=6)
    p.add_argument('--beam', type=int, default=4)
    p.add_argument('--patience', type=int, default=2)
    p.add_argument('--min-delta', type=float, default=0.01)
    p.add_argument('--generate-cmd', default='claude -p')
    p.add_argument('--candidates-dir')
    p.add_argument('--impostors', default=str(DEFAULT_IMPOSTORS))
    p.add_argument('--baseline', choices=['zero', 'few', 'retrieval'], default='retrieval')
    p.add_argument('--genre', choices=['prose', 'docs', 'social'], default='prose')
    p.add_argument('--name', default='voice')
    return p.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    samples = Path(args.samples)
    if not samples.is_dir() or not Path(args.draft).exists():
        print('missing samples dir or draft', file=sys.stderr)
        return 2
    if not Path(args.impostors).is_dir():
        print(f'missing impostor pool: {args.impostors}', file=sys.stderr)
        return 2
    paths = list(voice_profile.iter_docs(samples))
    if len(paths) < 5:
        print(f'need at least 5 sample documents to split; found {len(paths)}', file=sys.stderr)
        return 2
    a_paths, dev_paths = split_docs(paths, args.seed)
    if len(dev_paths) < 2:
        print('DEV split needs at least 2 documents', file=sys.stderr)
        return 2
    profile_a = profile_from_paths(a_paths)
    profile_dev = profile_from_paths(dev_paths)
    docs_a = []
    for p in a_paths:
        sents = voice_card.split_sentences_text(p.read_text(errors='replace'))
        if sents:
            docs_a.append(sents)
    matrix_a, _ = voice_card.coverage_matrix(docs_a)
    impostor_rows = voice_score.impostor_features(args.impostors)
    score_a = make_scorer(profile_a, impostor_rows, args.seed)
    score_dev = make_scorer(profile_dev, impostor_rows, args.seed)
    if args.candidates_dir is not None:
        get_batch = make_dry_run_source(args.candidates_dir)
    else:
        get_batch = make_live_source(args, a_paths, profile_a, docs_a, matrix_a, Path(args.draft).read_text(errors='replace'))
    report, best_text = build_report(args, a_paths, dev_paths, profile_a, profile_dev, score_a, score_dev, get_batch)
    write_outputs(args, report, a_paths, profile_a, docs_a, matrix_a, best_text)
    print(json.dumps({'best_candidate': report['best_candidate'], 'best_score': report['best_score'], 'stop_reason': report['stop_reason'], 'reward_hacking_warning': report['reward_hacking_warning']}, sort_keys=True))
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: mimic_stats ====
"""Paired small-sample statistics for mimic candidate comparisons."""
import argparse
import itertools
import json
import math
import random
import statistics
import sys
from pathlib import Path
BOOTSTRAP_N = 2000
PERM_N = 20000
EXACT_PERM_MAX = 12

def deltas(items):
    return [it['baseline'] - it['treatment'] for it in items]

def _percentile(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac

def _normal_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def _normal_ppf(p):
    a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239]
    b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572]
    c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416]
    plow, phigh = (0.02425, 1 - 0.02425)
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

def bca_ci(sample, seed, alpha=0.05):
    n = len(sample)
    if n < 2:
        return (0.0, 0.0)
    theta_hat = statistics.mean(sample)
    rng = random.Random(seed)
    boot = []
    for _ in range(BOOTSTRAP_N):
        resample = [sample[rng.randrange(n)] for _ in range(n)]
        boot.append(statistics.mean(resample))
    boot.sort()
    n_less = sum((1 for b in boot if b < theta_hat))
    prop = n_less / BOOTSTRAP_N
    if prop <= 0.0 or prop >= 1.0:
        return (_percentile(boot, alpha / 2), _percentile(boot, 1 - alpha / 2))
    z0 = _normal_ppf(prop)
    jack = []
    total = sum(sample)
    for i in range(n):
        jack.append((total - sample[i]) / (n - 1))
    jbar = statistics.mean(jack)
    num = sum(((jbar - x) ** 3 for x in jack))
    den = 6.0 * sum(((jbar - x) ** 2 for x in jack)) ** 1.5
    acc = num / den if den else 0.0
    z_lo, z_hi = (_normal_ppf(alpha / 2), _normal_ppf(1 - alpha / 2))

    def adjust(z):
        return _normal_cdf(z0 + (z0 + z) / (1 - acc * (z0 + z)))
    return (_percentile(boot, adjust(z_lo)), _percentile(boot, adjust(z_hi)))

def sign_flip_p(sample, seed):
    n = len(sample)
    if n == 0:
        return 1.0
    observed = abs(sum(sample))
    if n <= EXACT_PERM_MAX:
        count = 0
        total = 0
        for signs in itertools.product((1, -1), repeat=n):
            total += 1
            if abs(sum((s * x for s, x in zip(signs, sample)))) >= observed - 1e-12:
                count += 1
        return count / total
    rng = random.Random(seed)
    count = 0
    for _ in range(PERM_N):
        flipped = sum((x if rng.random() < 0.5 else -x for x in sample))
        if abs(flipped) >= observed - 1e-12:
            count += 1
    return (count + 1) / (PERM_N + 1)

def analyze(items, seed):
    d = deltas(items)
    n = len(d)
    mean_delta = statistics.mean(d) if d else 0.0
    ci_low, ci_high = bca_ci(d, seed) if n >= 2 else (0.0, 0.0)
    p = sign_flip_p(d, seed) if n >= 1 else 1.0
    improved = bool(n >= 2 and ci_low > 0 and (p < 0.05))
    return {'n': n, 'mean_delta': mean_delta, 'ci_low': ci_low, 'ci_high': ci_high, 'p_value': p, 'improved': improved, 'seed': seed}

def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('data', help='JSON list of {treatment, baseline} pairs')
    p.add_argument('--seed', type=int, default=20240607)
    return p.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    path = Path(args.data)
    if not path.exists():
        print(f'missing data file: {path}', file=sys.stderr)
        return 2
    items = json.loads(path.read_text())
    result = analyze(items, args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

# ==== module: run_structure_climb ====
"""Macro-structure hill-climb: generate -> scan -> targeted directives -> regenerate."""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import structure_scan
import silhouette_scan
import validate_preservation
EXIT_CONVERGED = 0
EXIT_BAD_INPUT = 2
EXIT_CAPPED = 3
EXIT_PRESERVATION = 4
SILHOUETTE_REFERENCE = silhouette_scan.load_reference(silhouette_scan.REFERENCE_PATH)

def _first_words(text: str, n: int=8) -> str:
    toks = text.strip().split()
    head = ' '.join(toks[:n])
    return head + ('...' if len(toks) > n else '')

def scan_draft(text: str, genre: str) -> dict:
    struct = structure_scan.scan(text, genre)
    silh = silhouette_scan.scan(text, SILHOUETTE_REFERENCE, genre)
    structure_flags = [f['metric'] for f in struct['flags']]
    penalty = silh.get('penalty')
    silhouette_dirty = penalty is not None and penalty >= silhouette_scan.PENALTY_THRESHOLD
    silh_metric_flags = [f['metric'] for f in silh.get('flags', []) if f['metric'] != 'silhouette_penalty']
    silh_violations = len(silh_metric_flags) if silh_metric_flags else 1 if silhouette_dirty else 0
    clean = not structure_flags and (not silhouette_dirty)
    return {'structure': struct, 'silhouette': silh, 'structure_flags': structure_flags, 'silhouette_flags': silh_metric_flags, 'silhouette_penalty': penalty, 'silhouette_dirty': silhouette_dirty, 'violation_count': len(structure_flags) + silh_violations, 'clean': clean}

def _openers(sentences: list[str]) -> list[str]:
    enumeration = {'the', 'a', 'an', 'section', 'chapter', 'figure', 'table', 'step', 'part', 'appendix'}
    out = []
    for s in sentences:
        ws = structure_scan.words(s)
        if ws and ws[0] not in enumeration:
            out.append(ws[0])
    return out

def _dir_conclusion_coda(text, paras, sentences) -> str:
    last = paras[-1] if paras else ''
    stock = structure_scan.CODA_START_RE.search(last)
    where = f'The final paragraph ("{_first_words(last)}")'
    if stock:
        return f'{where} opens on the stock coda "{stock.group(0).strip()}". Delete the wrap-up or rewrite the final paragraph to close on a specific new fact, not a restatement of the opening.'
    return f'{where} restates the opening instead of adding information. Delete it or rewrite the final paragraph to end on a concrete new point, not a recap.'

def _dir_opener_repetition(text, paras, sentences) -> str:
    openers = _openers(sentences)
    if not openers:
        return 'Sentence openings repeat in a template rhythm; vary the sentence openers.'
    counts = Counter(openers)
    word, n = counts.most_common(1)[0]
    return f'Sentence openings repeat: "{word}" leads {n} of {len(openers)} sentences. Rewrite so no single word starts more than a couple of sentences, and avoid an identical-opener run.'

def _dir_connective_openers(text, paras, sentences) -> str:
    hits = []
    for i, p in enumerate(paras):
        m = structure_scan.CONNECTIVE_OPENERS.search(p)
        if m:
            hits.append(f'paragraph {i + 1} ("{m.group(0).strip()}")')
    named = '; '.join(hits) if hits else 'several paragraphs'
    return f'These paragraphs open with a formal transition word: {named}. Replace each scaffold opener with a specific topic sentence about that paragraph.'

def _dir_every_template(text, paras, sentences) -> str:
    hits = []
    for i, p in enumerate(paras):
        if structure_scan.EVERY_OPENER_RE.search(p):
            hits.append(f'paragraph {i + 1} ("{_first_words(p, 4)}")')
    named = '; '.join(hits) if hits else 'multiple paragraphs'
    return f"These paragraphs repeat the 'Every ___ is/does ...' opener template: {named}. Vary the openings so the rhythm stops being mechanical."

def _dir_signpost(text, paras, sentences) -> str:
    found = sorted({m.strip() for m in structure_scan.SIGNPOST_RE.findall('\n\n'.join(paras))})
    named = ', '.join((f'"{f}"' for f in found)) if found else 'roadmap phrases'
    return f'The text narrates its own structure with signpost phrases ({named}). Remove the roadmap language and let the content carry the order.'

def _dir_participial_closer(text, paras, sentences) -> str:
    examples = []
    for s in sentences:
        m = structure_scan.CLOSER_RE.search(s)
        if m:
            examples.append(f'"...{m.group(1)}..."')
        if len(examples) >= 3:
            break
    named = ', '.join(examples) if examples else 'editorial -ing tails'
    return f'Sentences end on editorial -ing consequence tails ({named}). Make each consequence a concrete claim or cut the trailing clause.'

def _dir_burstiness(text, paras, sentences) -> str:
    lengths = [len(structure_scan.words(s)) for s in sentences]
    mean = round(sum(lengths) / len(lengths), 1) if lengths else 0
    return f'Sentence lengths are uniform (about {mean} words each across {len(lengths)} sentences). Vary the cadence: cut some sentences well under that and let others run well over it.'

def _dir_bold_colon(text, paras, sentences) -> str:
    labels = structure_scan.BOLD_COLON_RE.findall(text)
    n = len(labels)
    return f'There are {n} bold-label colon listicle lines. Convert them to flowing prose or plain sentences instead of a bolded label stack.'

def _dir_one_line_staccato(text, paras, sentences) -> str:
    return 'Most paragraphs are single short sentences (staccato beats). Merge related beats into fuller paragraphs and vary paragraph length.'
STRUCTURE_DIRECTIVES = {'conclusion_coda': _dir_conclusion_coda, 'opener_repetition': _dir_opener_repetition, 'connective_paragraph_openers': _dir_connective_openers, 'every_template_openers': _dir_every_template, 'signpost_density': _dir_signpost, 'participial_closer_share': _dir_participial_closer, 'sentence_burstiness': _dir_burstiness, 'bold_colon_listicle': _dir_bold_colon, 'one_line_staccato': _dir_one_line_staccato}

def _silh_paras(text):
    return silhouette_scan.paragraphs(text)

def _dir_scaffold_opener(text, sparas) -> str:
    body = sparas[1:] if len(sparas) > 1 else sparas
    hits = []
    for i, p in enumerate(body):
        for name, rx in silhouette_scan.ROLE_RE.items():
            m = rx.search(p)
            if m:
                hits.append(f'"{m.group(0).strip()}" ({name})')
                break
    named = ', '.join(hits) if hits else 'discourse cues'
    return f'Body paragraphs open on discourse cues instead of their own claim: {named}. Start each body paragraph on the specific point it makes.'

def _dir_role_entropy(text, sparas) -> str:
    classes = []
    for p in sparas:
        for name, rx in silhouette_scan.ROLE_RE.items():
            if rx.search(p):
                classes.append(name)
                break
    named = ', '.join(sorted(set(classes))) if classes else 'several cue classes'
    return f"Paragraph openers rotate through scaffold cue classes ({named}) -- the 'However / In addition / Ultimately' template. Drop the rotation and open paragraphs on content."

def _dir_preview_fulfillment(text, sparas) -> str:
    if len(sparas) < 2:
        return 'The body just fulfills an outline previewed in the intro; drop the preview and let the argument unfold.'
    intro = set(silhouette_scan.content(sparas[0]))
    body = sparas[1:-1] if len(sparas) > 2 else sparas[1:]
    echoes = []
    for p in body:
        cs = silhouette_scan.content(p)
        if cs and cs[0] in intro:
            echoes.append(f'"{cs[0]}"')
    named = ', '.join(sorted(set(echoes))) if echoes else 'intro keywords'
    return f'Body paragraphs open on words previewed in the intro ({named}) -- a preview-then-fulfill outline. Cut the intro preview so sections carry new ground.'

def _dir_callback_content(text, sparas) -> str:
    n = len(sparas)
    third = max(1, n // 3)
    early = set().union(*[set(silhouette_scan.content(sparas[i])) for i in range(third)]) if n else set()
    mid = set().union(*[set(silhouette_scan.content(sparas[i])) for i in range(third, n - third)]) if n - 2 * third > 0 else set()
    late = set().union(*[set(silhouette_scan.content(sparas[i])) for i in range(n - third, n)]) if n else set()
    cb = sorted((early & late) - mid)
    named = ', '.join((f'"{w}"' for w in cb[:6])) if cb else "the opening's vocabulary"
    return f"The ending re-uses the opening's vocabulary ({named}) after it was absent from the middle -- a recap loop. End on the last concrete point instead of circling back to the opening."

def _dir_heading_preview(text, sparas) -> str:
    heads = re.findall('(?m)^\\s{0,3}#{2,3}\\s+(.*)$', text)
    intro = set(silhouette_scan.content(sparas[0])) if sparas else set()
    echoing = [h.strip() for h in heads if set(silhouette_scan.content(h)) & intro]
    named = '; '.join((f'"{h}"' for h in echoing[:4])) if echoing else 'the section headings'
    return f"Headings restate the intro's outline ({named}). Let each section break new ground rather than echo the preview."

def _dir_silhouette_composite(text, sparas) -> str:
    return "The document's overall idea arrangement matches a templated silhouette (symmetric preview-then-fulfill outline with a closing recap). Rearrange around the actual argument: cut the previews and the closing loop."
SILHOUETTE_DIRECTIVES = {'scaffold_opener_share': _dir_scaffold_opener, 'role_entropy_bits': _dir_role_entropy, 'preview_fulfillment': _dir_preview_fulfillment, 'callback_content': _dir_callback_content, 'heading_preview': _dir_heading_preview}

def build_directives(text: str, scan: dict, genre: str) -> list[dict]:
    paras = structure_scan.prose_paragraphs(text)
    prose_text = '\n\n'.join(paras)
    sentences = structure_scan.split_sentences(prose_text)
    sparas = _silh_paras(text)
    directives: list[dict] = []
    for metric in scan['structure_flags']:
        fn = STRUCTURE_DIRECTIVES.get(metric)
        if fn is None:
            continue
        directives.append({'source': 'structure', 'metric': metric, 'directive': fn(text, paras, sentences)})
    fired_silh = False
    for metric in scan['silhouette_flags']:
        fn = SILHOUETTE_DIRECTIVES.get(metric)
        if fn is None:
            continue
        fired_silh = True
        directives.append({'source': 'silhouette', 'metric': metric, 'directive': fn(text, sparas)})
    if scan['silhouette_dirty'] and (not fired_silh):
        directives.append({'source': 'silhouette', 'metric': 'silhouette_penalty', 'directive': _dir_silhouette_composite(text, sparas)})
    return directives

def build_prompt(base_prompt: str, draft: str, directives: list[dict], round_index: int) -> str:
    if round_index == 0 or not draft:
        return base_prompt.rstrip() + '\n'
    lines = [base_prompt.rstrip(), '', 'You previously wrote this draft:', '---', draft.strip(), '---', '', 'A structural scanner you cannot run found these specific problems. Fix exactly these and nothing else. Keep every fact, number, name, and negation intact:']
    for i, d in enumerate(directives, 1):
        lines.append(f"{i}. {d['directive']}")
    lines += ['', 'Return only the rewritten piece.']
    return '\n'.join(lines) + '\n'

def generate(generate_cmd: str, prompt: str, round_index: int) -> str:
    env = dict(os.environ, MOCK_ROUND=str(round_index))
    proc = subprocess.run(shlex.split(generate_cmd), input=prompt, text=True, capture_output=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f'generate-cmd failed ({proc.returncode}): {proc.stderr.strip()[:300]}')
    return proc.stdout

def climb(base_prompt, generate_cmd, genre, max_rounds, source_text=None):
    rounds = []
    anchor_text = source_text
    have_source = source_text is not None
    draft = ''
    directives: list[dict] = []
    terminal = None
    converged = False
    for i in range(max_rounds):
        draft = generate(generate_cmd, build_prompt(base_prompt, draft, directives, i), i)
        scan = scan_draft(draft, genre)
        preservation = None
        if anchor_text is None:
            anchor_text = draft
        if have_source or i > 0:
            pres = validate_preservation.validate_preservation(anchor_text, draft)
            preservation = {'passed': pres['passed'], 'total_constraints': pres['total_constraints'], 'preserved': pres['preserved'], 'missing': pres['missing']}
        directives = [] if scan['clean'] else build_directives(draft, scan, genre)
        rounds.append({'index': i, 'structure_flags': scan['structure_flags'], 'silhouette_flags': scan['silhouette_flags'], 'silhouette_penalty': scan['silhouette_penalty'], 'violation_count': scan['violation_count'], 'clean': scan['clean'], 'preservation': preservation, 'directives': directives, 'draft': draft})
        if preservation is not None and (not preservation['passed']):
            terminal = 'preservation_violation'
            break
        if scan['clean']:
            terminal = 'converged'
            converged = True
            break
    if terminal is None:
        terminal = 'capped'
    return (rounds, terminal, converged)

def build_report(args, rounds, terminal, converged):
    initial = rounds[0]['violation_count'] if rounds else None
    final = rounds[-1]['violation_count'] if rounds else None
    return {'genre': args.genre, 'max_rounds': args.max_rounds, 'rounds_used': len(rounds), 'terminal_state': terminal, 'converged': converged, 'initial_violations': initial, 'final_violations': final, 'violation_trajectory': [r['violation_count'] for r in rounds], 'rounds': rounds}

def write_outputs(out_dir, report):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if report['rounds']:
        (out / 'final.md').write_text(report['rounds'][-1]['draft'])

def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt-file', required=True, help='base task prompt handed to the generator each round')
    p.add_argument('--out', required=True)
    p.add_argument('--generate-cmd', default='claude -p')
    p.add_argument('--max-rounds', type=int, default=4)
    p.add_argument('--genre', choices=['prose', 'docs', 'social'], default='prose')
    p.add_argument('--source-file', help='authoritative text whose facts must survive every round; when set, preservation is anchored here (round 0 included) instead of to the first generated draft')
    return p.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f'missing prompt file: {args.prompt_file}', file=sys.stderr)
        return EXIT_BAD_INPUT
    base_prompt = prompt_path.read_text(errors='replace')
    if args.max_rounds < 1:
        print('--max-rounds must be >= 1', file=sys.stderr)
        return EXIT_BAD_INPUT
    source_text = None
    if args.source_file:
        src = Path(args.source_file)
        if not src.exists():
            print(f'missing source file: {args.source_file}', file=sys.stderr)
            return EXIT_BAD_INPUT
        source_text = src.read_text(errors='replace')
    try:
        rounds, terminal, converged = climb(base_prompt, args.generate_cmd, args.genre, args.max_rounds, source_text=source_text)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return EXIT_BAD_INPUT
    report = build_report(args, rounds, terminal, converged)
    write_outputs(args.out, report)
    print(json.dumps({'terminal_state': report['terminal_state'], 'converged': report['converged'], 'rounds_used': report['rounds_used'], 'initial_violations': report['initial_violations'], 'final_violations': report['final_violations']}, sort_keys=True))
    return {'converged': EXIT_CONVERGED, 'capped': EXIT_CAPPED, 'preservation_violation': EXIT_PRESERVATION}[terminal]
if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
````
