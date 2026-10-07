# Bundled tool commands

Every command of `scripts/human_tool.py`, its purpose and a typical call.

## Commands

Run every command as `python3 <skill-dir>/scripts/human_tool.py <command> [args]`. `<skill-dir>` is the folder that holds this skill's `SKILL.md`. The tool is standard-library Python 3 (verified on 3.13); `--help` lists the commands. Each module in `scripts/` also runs on its own (`python3 <skill-dir>/scripts/banned_phrase_scan.py < input.txt`).

Every command prints JSON. Scanners exit 1 when they flag something and 0 when clean. Quoted spans (double quotes), markdown blockquotes, inline code and code fences are masked before phrase scanning, so a document that quotes bad writing does not flag its own examples. Non-English input returns `"non_english": true` and nothing else: that is the one graceful decline.

| Command | Purpose | Typical call |
|---|---|---|
| `scan` | Phrase and pattern scanner (literal triggers plus gated structural regexes) | `python3 <skill-dir>/scripts/human_tool.py scan < input.txt` |
| `structure` | Document rhythm and shape metrics | `python3 <skill-dir>/scripts/human_tool.py structure --genre docs README.md` |
| `silhouette` | Idea-arrangement tells (outline following, recap loops) | `python3 <skill-dir>/scripts/human_tool.py silhouette < input.txt` |
| `readability` | Grade level, sentence statistics, variance | `python3 <skill-dir>/scripts/human_tool.py readability < input.txt` |
| `constraints` | Extract must-preserve facts | `python3 <skill-dir>/scripts/human_tool.py constraints < input.txt` |
| `preserve` | Check that every fact, negation and scope word survived | `python3 <skill-dir>/scripts/human_tool.py preserve [--strict] original.txt rewritten.txt` |
| `diff` | Change ratio between original and rewrite | `python3 <skill-dir>/scripts/human_tool.py diff original.txt rewritten.txt` |
| `suggest` | Emit span-level co-writer suggestions | `python3 <skill-dir>/scripts/human_tool.py suggest doc.md [--apply-replacements repl.json]` |
| `check-suggestions` | The four blocking suggestion gates | `python3 <skill-dir>/scripts/human_tool.py check-suggestions suggestions.json` |
| `harvest` | Collect user-authored writing samples from chat transcripts and folders | `python3 <skill-dir>/scripts/human_tool.py harvest SOURCE... -o candidates.json` |
| `harvest-classify` | Rank harvested candidates, flag suspected AI pastes | `python3 <skill-dir>/scripts/human_tool.py harvest-classify --candidates candidates.json` |
| `profile` | Stylometric fingerprint of approved samples | `python3 <skill-dir>/scripts/human_tool.py profile samples/ -o profile.json` |
| `card` | Layered voice card from profile and samples | `python3 <skill-dir>/scripts/human_tool.py card --profile profile.json --samples samples/ --out . --name NAME --provenance` |
| `voice-score` | Distance of a draft from the profile against impostor writers | `python3 <skill-dir>/scripts/human_tool.py voice-score --profile profile.json --impostors IMPOSTORS/ --seed 7 draft.md` |
| `calibrate-pairs` | One A/B pair that varies a single voice dimension | `python3 <skill-dir>/scripts/human_tool.py calibrate-pairs generate --base passage.txt --dimension em_dash --seed 1` |
| `calibrate-score` | Aggregate A/B choices, pick the next dimension, report conflicts | `python3 <skill-dir>/scripts/human_tool.py calibrate-score --preferences prefs.jsonl [--profile profile.json] [--next]` |
| `refine` | Voice hill-climb with held-out acceptance and a divergence guard | see Refine loop in `voice.md` |
| `stats` | Paired bootstrap CI and permutation test for refine results | `python3 <skill-dir>/scripts/human_tool.py stats results.json --seed 7` |
| `climb` | Scan-regenerate loop that repairs document structure | see Structure repair loop in `structure.md` |

`voice-score` and `refine` need an impostor folder: about 10 `.txt` or `.md` files by other writers in the same genre as the target text (for example published posts, docs or emails not written by the user). The score means "closer to this writer than to plausible other writers", so the impostors must be same-genre and must not include the user.
