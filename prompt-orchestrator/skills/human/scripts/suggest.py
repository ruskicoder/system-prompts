#!/usr/bin/env python3
"""Co-writer suggestion mode: emit LSP-style structured edit suggestions."""
from __future__ import annotations
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
