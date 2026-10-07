#!/usr/bin/env python3
"""Scan prose for discourse-level silhouette AI-writing patterns."""
from __future__ import annotations
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
