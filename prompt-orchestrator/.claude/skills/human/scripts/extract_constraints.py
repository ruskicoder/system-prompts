#!/usr/bin/env python3
"""Extract must-preserve constraints from input text."""
from __future__ import annotations
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
