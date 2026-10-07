# Teach and mimic workflows

Voice building from samples, the calibration game, voiced drafting, voice check and the refine loop.

## Teach workflow

Build a reusable voice from a writer's samples. You drive it end to end; the user supplies only approvals and answers, never a directory or a command. Store everything under `.human/voice/<name>/` in the working directory and keep that folder out of version control unless the user decides otherwise.

1. Gather samples. If the user offers none, harvest them from their chat transcripts and from folders they name as their own writing. Supported transcript sources are Claude Code (`~/.claude/projects/**/*.jsonl`) and Codex CLI or Desktop (`~/.codex/sessions/**/rollout-*.jsonl`), detected by content shape:

```bash
python3 <skill-dir>/scripts/human_tool.py harvest SOURCE [SOURCE...] -o candidates.json
python3 <skill-dir>/scripts/human_tool.py harvest-classify --candidates candidates.json --mode heuristic
```

   The adapters keep only explicitly user-authored turns. They drop assistant, developer, tool and reasoning turns, and injected content such as a pasted `AGENTS.md` or an environment banner (counted as `instruction-injection`). Every kept candidate runs through the scanners: a hard hit, or two or more scanner categories, marks it `suspect_ai`, ranked last. Show the ranked candidates with sources and flags. The user approves or rejects each one. Never auto-approve a `suspect_ai` candidate: human review is the defense against assistant text leaking into the voice. Heavy "um/uh" text is marked `dictated` and can still be kept. Harvesting stays local. Copy only approved samples into `.human/voice/<name>/samples/` as `.txt` or `.md` (convert other formats first).

2. Check the sample requirements: at least 5 documents and 2,000 to 3,000 words in the same genre as the target writing. Thinner or cross-genre samples set `low_confidence`. Tell the user the voice is provisional and ask for more same-genre samples before trusting a mimic. Do not teach on blog posts and then score legal memos.

3. Build the profile and card:

```bash
python3 <skill-dir>/scripts/human_tool.py profile samples/ -o profile.json
python3 <skill-dir>/scripts/human_tool.py card --profile profile.json --samples samples/ --out . --name NAME --provenance
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
4. Score the voice: `python3 <skill-dir>/scripts/human_tool.py voice-score --profile profile.json --impostors IMPOSTORS/ --seed 7 --samples samples/ draft.md`.

The rule: a mimic that scores well on voice but trips a removal gate is rejected. Voice never buys an exemption from the core contract. Meaning preservation against the original draft is its own hard gate and is never blended into the voice score.

Voice check ("does this sound like me?"): run `voice-score` only and change nothing. Report the composite (lower is closer to the writer), the GI rank, and the two or three metric deltas that explain the score in plain words ("your sentences run longer than usual; contractions match"). Check drafts often; commission rewrites rarely.

Scoring: composite = `0.5 * (1 - GI) + 0.5 * zsum`. GI (General Impostors) is the share of random feature-subset trials in which the draft beats every impostor at resembling the profile. `zsum` is the weighted per-feature distance normalized against the impostor pool and clipped to plus or minus 3. Both halves reward beating plausible other writers, which is what defeats a draft stuffed with the writer's markers. Drafts under 150 words are `low_confidence`. `--samples` adds a copy gate against verbatim lifting. The composite is a guide, not an oracle: treat per-draft deltas as the signal and under-claim.

Refine loop, only when single passes keep landing short:

```bash
python3 <skill-dir>/scripts/human_tool.py refine --samples samples/ --draft draft.md --out OUT --impostors IMPOSTORS/ --seed 1 --candidates-dir CANDS/
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
