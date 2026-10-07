#!/usr/bin/env python3
"""Validate that all must-preserve constraints survived transformation."""
from __future__ import annotations
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
