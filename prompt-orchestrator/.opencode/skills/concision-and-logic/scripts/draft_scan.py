#!/usr/bin/env python3
"""Flag shape-level AI tells and verbosity in an English draft.

Standard library only. Prints JSON. Exits 1 when it flags anything, 0 when clean.
Every finding is a candidate: confirm it in context before editing.

Usage:
    python3 draft_scan.py FILE [--genre academic|professional|any] [--max-findings N]
    python3 draft_scan.py - < draft.txt
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# Each rule: (category, compiled pattern, advice). Patterns run per sentence.
RULES: list[tuple[str, re.Pattern[str], str]] = []


def rule(category: str, pattern: str, advice: str) -> None:
    RULES.append((category, re.compile(pattern, re.IGNORECASE), advice))


# Universal claims: "every figure is a parameter", "any node can serve as".
rule("universal",
     r"\b(every|each|any|all)\s+(?:[\w-]+\s+){0,4}?(is|are|can|could|will|must|serves?|counts?|becomes?|acts?)\b",
     "Name the actual members or the condition, or cite the evidence that it holds for all.")
rule("universal",
     r"\b(always|never|universally|without exception|in all cases|no matter)\b",
     "Absolute claim: give the measured scope or drop the absolute.")

# Verdict and corrective framing (GPT-6 'does not establish', Claude 'rather than simply').
rule("verdict",
     r",\s*(and|but|while|whereas)\s+[^,;.]{1,90}?\b(is|are|was|were|does|do|did|can|will)\s+not\b[^,;.]{0,40}[.;]?\s*$",
     "Two-clause verdict. State each item on its own, or use an in-scope / out-of-scope list.")
rule("verdict",
     r"\b(does not|do not|cannot) (by itself |on its own |alone )?(establish|prove|guarantee|imply|mean)\b",
     "Corrective framing. Say what the evidence shows instead.")
rule("verdict",
     r"\b(rather than( simply| merely| just)?|not (simply|merely|just|only)|more than (a|an|just)|should be (treated|read|understood|seen) as|not necessarily)\b",
     "Contrast frame. State the positive claim directly.")

# Meta-commentary about the document or the reader.
rule("meta",
     r"\b(this means( that)?|note that|it is (worth|important to) not(e|ing)|importantly|notably|in other words|put simply|to be clear|for clarity|sample values?|as (mentioned|noted|stated|discussed) (above|earlier|before|previously)|this (section|document|report|table|figure|chapter) (describes|presents|outlines|explains|shows|covers|walks)|the following (section|table|list)|below (we|is|are)|here(?:'|’)s|let(?:'|’)s|we will now)\b",
     "Meta note about the text. Delete it, or move the fact into a table caption or heading.")
rule("importance",
     r"\b(this matters|why [\w\s]{1,30} matters|matters because|plays? an? (crucial|key|pivotal|vital|critical|significant) role|crucial(ly)?|pivotal|paramount|of (great|utmost) importance)\b",
     "Importance flag. Show the consequence (a number, a failure, a cost) instead of announcing it.")
rule("summary",
     r"^(in (summary|conclusion|short|essence)|overall|to (sum up|summari[sz]e|conclude)|taken together|all in all|ultimately|looking ahead)\b",
     "Recap or forecast sentence. Cut it unless the genre requires a conclusion.")

# Hedge stacks and empty modal verbs.
rule("hedge",
     r"\b(may|might|could|can) (potentially|possibly|perhaps|help( to)?|serve to|provide)\b|\bit is (possible|likely|plausible) that\b|\bto some (extent|degree)\b|\barguably\b",
     "Stacked or empty hedge. Keep one hedge tied to a stated limit, or state the result.")

# Copula avoidance and participle tails.
rule("copula",
     r"\b(serves?|stands?|acts?|functions?) as (a|an|the)\b",
     "Copula avoidance. Write 'is'.")
rule("participle-tail",
     r",\s+(highlighting|underscoring|showcasing|emphasi[sz]ing|ensuring|enabling|fostering|reflecting|demonstrating|paving|setting the stage|making it)\b",
     "Trailing -ing clause that asserts significance. Make it a separate, supported sentence or cut it.")

# Era vocabulary (see references/ai-tells-by-model.md for sources).
rule("ai-vocab",
     r"\b(delve|delves|delving|tapestry|testament|underscores?|showcas(e|es|ing)|intricate|meticulous(ly)?|interplay|landscape|realm|bolster(ed|s)?|garner(ed|s)?|vibrant|seamless(ly)?|robust|leverag(e|es|ed|ing)|multifaceted|dependable|steady|quietly|load-bearing|holistic|synerg(y|ies)|empower(s|ing)?|unlock(s|ing)?|navigat(e|ing) the)\b",
     "Model-era vocabulary. Use the plain word, or the specific fact the word stands in for.")

DASH = re.compile(r"\s—\s|—|\s–\s")
PAREN = re.compile(r"\(([^()]*)\)")
CITATION = re.compile(r"^\s*(\d{4}[a-z]?|[A-Z][\w-]+( et al\.?)?,? \d{4}|e\.g\.,?.*\d{4}|see [^)]*\d|\d+(\.\d+)*|[A-Z0-9]{2,8}s?|[ivx]+|[a-z])\s*$")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“(\[])")


def mask(text: str) -> str:
    """Blank out code fences, inline code and block quotes, keeping line numbers."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"```[\s\S]*?```", blank, text)
    text = re.sub(r"`[^`\n]+`", blank, text)
    return re.sub(r"(?m)^>.*$", blank, text)


def sentences(text: str):
    """Yield (line_number, sentence) for prose lines; table rows count as one sentence each."""
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or set(stripped) <= set("|-: "):
            continue
        if stripped.startswith("|"):
            for cell in stripped.strip("|").split("|"):
                if cell.strip():
                    yield lineno, cell.strip()
            continue
        stripped = re.sub(r"^(#+|[-*+]|\d+[.)])\s+", "", stripped)
        for sent in SENT_SPLIT.split(stripped):
            if sent.strip():
                yield lineno, sent.strip()


def scan(text: str, genre: str = "any") -> dict:
    text = mask(text)
    findings = []
    lengths = []
    paren_asides = 0
    words_total = 0
    for lineno, sent in sentences(text):
        words = re.findall(r"[A-Za-z0-9][\w'’-]*", sent)
        words_total += len(words)
        if len(words) >= 3:
            lengths.append(len(words))
        for category, pattern, advice in RULES:
            if category == "summary":
                m = pattern.search(sent.lstrip("*_ "))
            else:
                m = pattern.search(sent)
            if m:
                findings.append({"line": lineno, "category": category, "match": m.group(0).strip(),
                                 "sentence": sent[:240], "advice": advice})
        if DASH.search(sent):
            findings.append({"line": lineno, "category": "dash", "match": "em or en dash",
                             "sentence": sent[:240],
                             "advice": "Use a comma, a colon or two sentences (prose-and-wording)."})
        for inner in PAREN.findall(sent):
            if CITATION.match(inner):
                continue
            paren_asides += 1
            if len(inner.split()) >= 4:
                findings.append({"line": lineno, "category": "parenthesis", "match": f"({inner[:60]})",
                                 "sentence": sent[:240],
                                 "advice": "Parenthetical aside. Make it its own sentence, a table column, or cut it."})
        if genre == "professional" and len(words) > 30:
            findings.append({"line": lineno, "category": "long-sentence", "match": f"{len(words)} words",
                             "sentence": sent[:240], "advice": "Split: one fact or one request per sentence."})
        elif len(words) > 40:
            findings.append({"line": lineno, "category": "long-sentence", "match": f"{len(words)} words",
                             "sentence": sent[:240], "advice": "Split at the main verb boundary."})

    metrics = {
        "words": words_total,
        "sentences": len(lengths),
        "mean_sentence_words": round(statistics.mean(lengths), 1) if lengths else 0,
        "stdev_sentence_words": round(statistics.pstdev(lengths), 1) if len(lengths) > 1 else 0,
        "parenthetical_asides": paren_asides,
        "asides_per_100_words": round(100 * paren_asides / words_total, 2) if words_total else 0,
    }
    notes = []
    if metrics["asides_per_100_words"] > 1.0:
        notes.append("Parenthesis density above 1 per 100 words: rewrite most asides as plain sentences.")
    if len(lengths) >= 8 and metrics["stdev_sentence_words"] < 4:
        notes.append("Sentence lengths are uniform: a template rhythm. Vary by content, not by rule.")
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["category"]] = counts.get(f["category"], 0) + 1
    return {"metrics": metrics, "counts": counts, "notes": notes, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", help="file to scan, or - for stdin")
    parser.add_argument("--genre", choices=["academic", "professional", "any"], default="any")
    parser.add_argument("--max-findings", type=int, default=200)
    args = parser.parse_args(argv)
    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    result = scan(text, args.genre)
    result["findings"] = result["findings"][: args.max_findings]
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["findings"] or result["notes"] else 0


if __name__ == "__main__":
    sys.exit(main())
