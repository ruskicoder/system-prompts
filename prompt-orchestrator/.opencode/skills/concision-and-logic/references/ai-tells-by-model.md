# AI writing tells by model family

Research notes for `concision-and-logic`, `academic-writing` and `professional-writing`. Sources
were retrieved on 2026-11-07; each entry carries its own publication date. Model styles change
with every release, so treat a date older than six months as a lead to re-check.

## How to use this file

- A tell is a rate, not a proof. Graphite counts a phrase as a tell when a model uses it at least
  twice as often as human writers [G1]. One "crucial" in a report proves nothing; five tells in one
  paragraph make the paragraph read as generated.
- Fix the sentence, not the word. Wikipedia's editors warn that swapping surface words leaves the
  underlying shape and makes the text harder to review [W1]. Every fix below changes what the
  sentence claims or how it is built.
- The numbers in the Fix column are invented to show the shape of a good sentence. Take every
  figure in a real document from your own tests, logs or sources.
- Never use a detector score as evidence about a person. Detectors misclassified TOEFL essays by
  non-native writers as AI-written while classifying native writers' essays correctly [S3], and a
  test of detection tools found them neither accurate nor reliable [S4]. Vietnamese students
  writing in English are in the group the first study found to be over-flagged.

## Shared tells (all three families)

| Pattern | Example | Fix |
|---|---|---|
| Excess style vocabulary | "delves into", "showcasing", "underscores", "pivotal" | Use the plain verb, or the fact the word stands in for. Kobak et al. measured these words rising abruptly in PubMed abstracts after 2023 and estimated that at least 13.5 % of 2024 abstracts were processed with an LLM [S1]. |
| Present participle tails | "The gateway buffers packets, ensuring reliability." | State the effect as its own claim with its evidence: "The gateway buffers up to 200 packets. In test T4 no packet was lost during a 10 min outage." Reinhart et al. found instruction-tuned GPT-4o and Llama 3 overuse present participial clauses and nominalisations relative to human text [S2]. |
| Nominalisation stacks | "The implementation of the validation of the input" | Use the verb: "The app validates the input." [S2] |
| Copula avoidance | "The node serves as a relay." | "The node is a relay." Wikipedia lists "serves as", "stands as", "features", "boasts" in place of "is" or "has", observed in GPT and Gemini models [W1]. |
| Significance padding | "This stands as a testament to the system's robustness." | Delete, or give the measurement. [W1] |
| Rule of three | "fast, reliable and scalable" | Keep only the properties you measured. [W1] |
| Negative parallelism | "Not just a tracker, but a safety net." | State what it is: "The app alerts the base station when a hiker misses a check-in." [W1] |
| Vague attribution | "Experts argue that mesh networks are..." | Name and cite the source, or remove the claim. [W1] |
| Unasked conclusions and outlooks | "Despite these challenges, the future looks promising." | Cut. A report ends with results, limits and next steps that are already planned. [W1] |
| Uniform sentence length | Ten sentences of 15 to 20 words each | Let content set the length. A definition is short; a condition with two cases is long. Wikipedia notes a GPT-6 tendency toward shorter sentences in a narrow band and more periods and commas [W1]. |

## OpenAI GPT family (ChatGPT)

| Era and tell | Example | Fix |
|---|---|---|
| GPT-4 (2023 to mid-2024) vocabulary: "delve", "tapestry", "testament", "intricate", "meticulously", "interplay", "landscape", "bolstered", "garner", "Additionally" [W1] | "This report delves into the intricate landscape of mesh networking." | "This report describes how the TrekLink mesh relays messages." |
| GPT-4o (mid-2024 to mid-2025): "align with", "enhance", "fostering", "highlighting", "showcasing", "underscore", "vibrant" [W1] | "The feature enhances safety, fostering trust." | Name the change and its measured effect. |
| GPT-5 (mid-2025 to mid-2026): "emphasizing", "enhance", "highlighting", "showcasing", plus canned emphasis on coverage and notability [W1] | "The project has garnered attention from local trekking communities." | Cite the actual contact, or cut. |
| GPT-6 (mid-2026 on) vocabulary: "challenge", "clearer", "dependable", "echoed", "foster", "leverage", "matters", "multifaceted", "practical", "prioritize", "quietly", "steady", "universally" [W1] | "The design quietly prioritizes a dependable, practical experience." | "The app works offline. Check-ins queue on the phone until the mesh is reachable." |
| GPT-6 corrective framing. Graphite measured OpenAI's GPT-6 Astra using "does not establish" 275 times, "may provide" 18 times, "not necessarily" 17 times and "not simply" 10 times as often as Claude Opus 5.5 [G1]. Wikipedia dates "rather than", "should be treated as" and "does not by itself establish" to mid-2026, around the GPT-5.6 release [W1]. | "A passing demo does not by itself establish field readiness." | State the positive finding and its limit: "The demo covered 3 nodes over 400 m. Field range above 1 km is untested." |
| Two-clause verdicts (the shape the leader flagged in the register) | "Firmware enhancements made during the capstone are in scope and credited, and re-architecting the mesh stack is not." | Put scope in a list: "In scope: the firmware changes in Section 4.2. Out of scope: replacing the mesh protocol stack." |
| Hedge stacks | "This may potentially provide a basis for..." | One hedge, tied to the reason: "Results from 3 nodes may not hold for 20." [G1] |
| Formal clinical register. In a diabetes-text comparison, ChatGPT preferred "blood glucose levels" where Gemini wrote "blood sugar" [S5]. | "an increased risk of adverse outcomes" | Use the term your field and your reader use, and keep it fixed. |
| Em dash. Wikipedia files em-dash overuse as historical from September 2026, because recent models are tuned to avoid it; a July 2026 study it cites found ChatGPT using fewer em dashes than professional writers [W1]. | n/a | Its absence proves nothing. Look for the replacement tic: more periods and commas than human text [W1]. |

## Anthropic Claude family

| Tell | Example | Fix |
|---|---|---|
| Importance flags. Graphite measured Claude Opus 5.5 using "this matters" 116 times and "why _ matters" 92 times the human rate (2026-10-01) [G1]. | "This matters because hikers often lose signal." | Give the consequence as a fact: "In the 2025 survey, 11 of 30 hikers lost phone signal on the route." |
| "More than" and "rather than simply" contrasts: "is more than a _ it" 98 times, "rather than simply" 32 times the human rate [G1]. | "The gateway is more than a bridge: it is the system's memory." | "The gateway stores every packet for 7 days." |
| Forecast transitions: "looking ahead the" 40 times, "adds another layer" 27 times, "what comes next" 24 times [G1]. | "Looking ahead, the team plans..." | Start with the plan: "In Sprint 5 the team will..." |
| Evaluative adjectives: "dependable" 23 times, "steady" 11 times [G1]. | "a dependable alerting path" | Name the property measured: "alerts reached the base in under 5 s in 48 of 50 trials". |
| Em dash. Of contemporary models only Claude used em dashes more than professional writers in the July 2026 study cited by Wikipedia [W1]; Graphite measured Opus 5.5 at 0.015 em dashes per 1,000 words against 2.92 for Opus 5 [G1]. | `The node relays — and stores — every packet.` | Comma, colon or two sentences (prose-and-wording). |
| Antithesis and staged fragments. Community lists of Claude tells cite "This is not X, it's Y", "isn't just faster, it's cheaper", "Not a detail. A design decision.", colons and semicolons used as dramatic pauses where a person would write "and" or "but", and metaphors such as "load-bearing", "carry the argument", "full stop", "worth stating plainly" [C1][C2]. | "This is not a feature; it is a guarantee." | State the property and its evidence once. |
| Sycophantic openers in replies: "You're absolutely right!", "Great question" [C2][C3] | "You're absolutely right, the threshold is wrong." | "The threshold is 20 %, not 30 %. Fixed in Table 3." |
| Parenthetical and caveat density (observed in the TrekLink register, 2026-11-07): asides in parentheses, "note that", "sample values", notes about the document itself | "(see Section 3) (sample values; the organiser may change them)" | Move the value into a table with a "Default" column. Delete the note. |

Claude's writing tells are less studied in peer-reviewed work than GPT's. The Graphite figures
come from one company's study [G1]; the community lists are anecdotal [C1][C2][C3].

## Google Gemini family

| Tell | Example | Fix |
|---|---|---|
| Verbosity: the leader's main complaint ("they tend to yap"). 16x Engineer found Gemini 2.5 Pro gave long explanations by default; "Minimize prose" did not shorten it and "Be concise." did [C4]. A 320-sample stylometric comparison rated Gemini 3 Pro high on formality and low on conciseness [C5]. YapBench measured an order-of-magnitude spread in excess length across 76 assistants, with "vacuum-filling" on ambiguous prompts [S6]. | A 600-word answer to a question with a one-line answer | Answer first, in one or two sentences. Keep only what supports or limits the answer. Run the length budget in `concision-and-logic`. |
| Structure in place of argument: headers, bullets and bolded key terms where prose with connectives is needed [C5][C6]. | Five bullets, each a noun phrase, with no "because", "so" or "unless" between them | Rebuild the reasoning as sentences joined by the real relation (cause, condition, contrast, sequence). |
| Unrequested options: "Option 1, Option 2, Option 3" [C5]; Gemini used "option" about 13 times as often as ChatGPT and Claude in workplace writing in one 300,000-word test [C6]. | Three draft subject lines when one was asked for | Give one answer. Offer alternatives only when the reader must choose. |
| Meta-commentary: describing what it is about to do instead of doing it [C5]. | "Here is a breakdown of the key considerations:" | Delete the line. Start with the first consideration. |
| Formal tone with extreme adjectives; "it's not X, it's Y" used most of the three families in the same test [C6]. | "a truly transformative, game-changing approach" | Cut the adjective; give the comparison with numbers. |
| Weak logic hidden by fluent structure: claims in parallel bullets that do not follow from each other, a conclusion that restates the premises, a list whose items mix levels (a goal, a tool and a risk in one list). No study isolates this for Gemini; it is the leader's observation and is checked by `concision-and-logic` for any model. | "Benefits: offline support. Firebase. Safety." | One level per list. Each claim gets a "because" you can point to. |
| Copula avoidance, shared with GPT [W1] | "The dashboard serves as the hub." | "The dashboard is the organiser's main screen." |

Sources on Gemini are blog tests and vendor analyses, several from companies that sell
humanizer or detector tools [C4][C5][C6]. Treat their figures as indicative.

## Sources

Peer-reviewed and preprint studies:

- [S1] D. Kobak, R. González-Márquez, E.-Á. Horvát and J. Lause, "Delving into LLM-assisted writing in biomedical publications through excess vocabulary," *Science Advances*, vol. 11, no. 27, eadt3813, Jul. 2025. doi:10.1126/sciadv.adt3813
- [S2] A. Reinhart et al., "Do LLMs write like humans? Variation in grammatical and rhetorical styles," *PNAS*, vol. 122, no. 8, e2422455122, Feb. 2025. doi:10.1073/pnas.2422455122
- [S3] W. Liang, M. Yuksekgonul, Y. Mao, E. Wu and J. Zou, "GPT detectors are biased against non-native English writers," *Patterns*, vol. 4, no. 7, 100779, Jul. 2023. doi:10.1016/j.patter.2023.100779
- [S4] D. Weber-Wulff et al., "Testing of detection tools for AI-generated text," *International Journal for Educational Integrity*, vol. 19, art. 26, Dec. 2023. doi:10.1007/s40979-023-00146-z
- [S5] K. Rudnicka, "ChatGPT and Gemini AIs have uniquely different writing styles," *Scientific American*, 9 Jul. 2025. https://www.scientificamerican.com/article/chatgpt-and-gemini-ai-have-uniquely-different-writing-styles/ (magazine article)
- [S6] V. Borisov, M. Gröger, M. Mikhael and R. H. Schreiber, "Do chatbot LLMs talk too much? The YapBench benchmark," arXiv:2601.00624, Jan. 2026. https://arxiv.org/abs/2601.00624

Style guides and community references:

- [W1] Wikipedia, "Wikipedia:Signs of AI writing," WikiProject AI Cleanup, revision 1384165696, retrieved 2026-11-07. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (descriptive advice page, not policy)
- [G1] Graphite, "AI Tells: Opus 5.5 Update," 1 Oct. 2026. https://graphite.io/five-percent/research/ai-tells-opus-5-5-update (9,974 aligned topics, human articles predating ChatGPT)
- [C1] explainx.ai, "Claude Opus 5 Claudisms: why it says 'load-bearing'," 11 Aug. 2026. https://explainx.ai/blog/claude-opus-5-load-bearing-claudisms-writing-tells-2026
- [C2] Hacker News, "How to stop Claude from saying load-bearing," 2026. https://news.ycombinator.com/item?id=48905248
- [C3] Hacker News, "Claude says 'You're absolutely right!' about everything," 2025. https://news.ycombinator.com/item?id=44885398
- [C4] 16x Engineer, "Why Gemini 2.5 Pro won't stop talking (and how to fix it)," 2025. https://eval.16x.engineer/blog/gemini-2-5-pro-verbose-output-control
- [C5] My Writing Twin, "Gemini 3 Pro writing style analysis." https://www.mywritingtwin.com/profile/gemini-3-pro
- [C6] Wondering About AI, "I prompted ChatGPT, Claude, and Gemini to generate over 300,000 words." https://wonderingaboutai.substack.com/p/i-prompted-chatgpt-claude-and-gemini
- G. D. Gopen and J. A. Swan, "The science of scientific writing," *American Scientist*, vol. 78, no. 6, pp. 550-558, 1990. https://www.americanscientist.org/blog/the-long-view/the-science-of-scientific-writing (reader-expectation principles used in the logic check)
