#!/usr/bin/env python3
"""Shared cheap English-detection helpers for banned_phrase_scan.py,"""
from __future__ import annotations
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
