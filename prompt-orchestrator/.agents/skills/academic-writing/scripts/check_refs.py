#!/usr/bin/env python3
"""Check every DOI and URL in a reference list, and report references that carry neither.

Standard library only. Needs network access to api.crossref.org and to each URL.
Prints JSON, one result per reference. Exits 1 when any reference is not `ok`.

Usage:
    python3 check_refs.py references.md [--min-title-ratio 0.6] [--timeout 15]

Which lines are references: if the file has a heading named References, Bibliography, Works
cited or Reference list, every non-empty line under it up to the next heading of the same or a
higher level; otherwise every non-empty line that is not a heading or a code fence. Write one
reference per line.

Per reference:
- Every DOI on the line is looked up on Crossref; its title, first author and year are compared
  with the line. A DOI keeps balanced brackets, so 10.1002/(SICI)1097-4571(199806)49:8 stays whole.
- Every URL on the line gets an HTTP status check. A doi.org link counts as its DOI. A URL that
  answers 403 or 404 is tried once more with a browser User-Agent before it fails, because some
  publishers refuse unknown clients.
- A reference with no DOI and no URL is `unchecked` with the reason "unchecked, no identifier":
  verify it by hand (ISBN in a library catalogue, standard by its number).

Statuses, worst first: fail (DOI not registered, URL unreachable), mismatch (DOI metadata does
not match the entry), unchecked (no identifier, or network error), ok. A URL that answers is not
proof that the page supports the claim: open every source yourself before citing it.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

DOI = re.compile(r"\b10\.\d{4,9}/[^\s\"']+", re.IGNORECASE)
URL = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
DOI_HOSTS = {"doi.org", "dx.doi.org", "www.doi.org"}
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
REF_HEADING = re.compile(r"^(?:\d+(?:\.\d+)*\.?\s+)?(references?|bibliography|works cited|reference list|sources)\b", re.IGNORECASE)
UA = "academic-writing-check-refs/1.1 (reference verification)"
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
PAIRS = {")": "(", "]": "[", ">": "<", "}": "{"}
RANK = {"fail": 3, "mismatch": 2, "unchecked": 1, "ok": 0}
NO_IDENTIFIER = "unchecked, no identifier"


def trim(token: str) -> str:
    """Strip trailing punctuation and closing brackets that have no opening partner in the token."""
    while token:
        last = token[-1]
        if last in ".,;:":
            token = token[:-1]
        elif last in PAIRS and token.count(last) > token.count(PAIRS[last]):
            token = token[:-1]
        else:
            break
    return token


def identifiers(line: str) -> tuple[list[str], list[str]]:
    """Return (dois, urls) found on the line, deduplicated, in order of appearance."""
    dois: list[str] = []
    urls: list[str] = []
    seen: set[str] = set()
    for m in URL.finditer(line):
        url = trim(m.group(0))
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc.lower() in DOI_HOSTS:
            doi = urllib.parse.unquote(parsed.path.lstrip("/"))
            if doi.lower().startswith("10.") and doi.lower() not in seen:
                seen.add(doi.lower())
                dois.append(doi)
            continue
        if url not in urls:
            urls.append(url)
    for m in DOI.finditer(line):
        doi = trim(m.group(0))
        if doi.lower() not in seen:
            seen.add(doi.lower())
            dois.append(doi)
    return dois, urls


def reference_lines(text: str) -> list[str]:
    lines = text.splitlines()
    section: list[str] = []
    level = None
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        h = HEADING.match(line.strip())
        if h:
            if level is not None and len(h.group(1)) <= level:
                break
            if level is None and REF_HEADING.match(h.group(2).strip()):
                level = len(h.group(1))
            continue
        if level is not None and line.strip():
            section.append(line)
    if level is not None:
        return section
    in_fence = False
    out = []
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.strip() and not HEADING.match(line.strip()):
            out.append(line)
    return out


def norm(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(text)))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text.lower())).strip()


def title_ratio(title: str, line: str) -> float:
    t, l = norm(title), norm(line)
    if t and t in l:
        return 1.0
    match = difflib.SequenceMatcher(None, t, l).find_longest_match(0, len(t), 0, len(l))
    return round(match.size / max(len(t), 1), 2)


def fetch_json(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def url_status(url: str, timeout: float, opener: Callable = urllib.request.urlopen) -> dict:
    """HEAD, then GET, then GET with a browser User-Agent when the server answers 403 or 404."""
    attempts = [("HEAD", UA), ("GET", UA), ("GET", BROWSER_UA)]
    last: int | str = "error"
    for method, agent in attempts:
        req = urllib.request.Request(url, method=method, headers={"User-Agent": agent})
        try:
            with opener(req, timeout=timeout) as resp:
                return {"http": resp.status, "browser_ua": agent == BROWSER_UA}
        except urllib.error.HTTPError as err:
            last = err.code
            if err.code not in (403, 404, 405):
                break
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            return {"http": f"error: {err}", "browser_ua": agent == BROWSER_UA}
    return {"http": last, "browser_ua": agent == BROWSER_UA}


def check_doi(doi: str, line: str, min_ratio: float, timeout: float, fetch: Callable = fetch_json) -> dict:
    result: dict = {"doi": doi}
    try:
        msg = fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""), timeout)["message"]
    except urllib.error.HTTPError as err:
        return {**result, "status": "fail", "reason": f"Crossref HTTP {err.code}: DOI not registered or mistyped"}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as err:
        return {**result, "status": "unchecked", "reason": f"network: {err}"}
    title = html.unescape((msg.get("title") or [""])[0])
    authors = [html.unescape(a.get("family", "")) for a in msg.get("author", [])]
    year = (msg.get("issued", {}).get("date-parts") or [[None]])[0][0]
    ratio = title_ratio(title, line)
    problems = []
    if ratio < min_ratio:
        problems.append(f"title mismatch ({ratio})")
    if authors and norm(authors[0]) and norm(authors[0]) not in norm(line):
        problems.append(f"first author '{authors[0]}' not in entry")
    if year and str(year) not in line:
        problems.append(f"year {year} not in entry")
    return {**result, "status": "mismatch" if problems else "ok", "problems": problems,
            "crossref": {"title": title, "first_author": authors[0] if authors else None, "year": year,
                         "container": html.unescape((msg.get("container-title") or [""])[0])}}


def check_url(url: str, timeout: float, status: Callable = url_status) -> dict:
    res = status(url, timeout)
    ok = isinstance(res["http"], int) and res["http"] < 400
    out = {"url": url, "status": "ok" if ok else "fail", "http": res["http"]}
    if res.get("browser_ua"):
        out["retried_with_browser_ua"] = True
    out["note"] = "URL reachable; open it and confirm it supports the claim" if ok else "unreachable"
    return out


def check_line(line: str, min_ratio: float, timeout: float,
               fetch: Callable = fetch_json, status: Callable = url_status) -> dict:
    dois, urls = identifiers(line)
    result: dict = {"line": line.strip()[:300]}
    if not dois and not urls:
        return {**result, "status": "unchecked", "reason": NO_IDENTIFIER, "checks": []}
    checks = [check_doi(d, line, min_ratio, timeout, fetch) for d in dois]
    checks += [check_url(u, timeout, status) for u in urls]
    worst = max((c["status"] for c in checks), key=RANK.__getitem__)
    return {**result, "status": worst, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path")
    parser.add_argument("--min-title-ratio", type=float, default=0.6)
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args(argv)
    text = Path(args.path).read_text(encoding="utf-8")
    results = [check_line(line, args.min_title_ratio, args.timeout) for line in reference_lines(text)]
    summary = {s: sum(1 for r in results if r["status"] == s) for s in ("ok", "mismatch", "fail", "unchecked")}
    summary["no_identifier"] = sum(1 for r in results if r.get("reason") == NO_IDENTIFIER)
    print(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False))
    return 0 if summary["ok"] == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
