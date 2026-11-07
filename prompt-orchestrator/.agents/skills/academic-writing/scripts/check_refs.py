#!/usr/bin/env python3
"""Check that every DOI and URL in a reference list resolves, and that DOI metadata matches the entry.

Standard library only. Needs network access to api.crossref.org and to each URL.
Prints JSON, one result per reference line. Exits 1 when any reference fails or mismatches.

Usage:
    python3 check_refs.py references.md [--min-title-ratio 0.6] [--timeout 15]

A reference line is any line that contains a DOI (10.xxxx/...) or an http(s) URL.
For a DOI the script fetches Crossref metadata and compares the title with the line text.
For a URL without a DOI it checks the HTTP status only: it cannot confirm the page says what
the reference claims. Open every source yourself before citing it.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>)\]]+)", re.IGNORECASE)
URL = re.compile(r"https?://[^\s<>)\]]+")
UA = "academic-writing-check-refs/1.0 (reference verification; mailto:none)"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def fetch_json(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def url_status(url: str, timeout: float) -> int | str:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status
        except urllib.error.HTTPError as err:
            if method == "GET" or err.code not in (403, 405):
                return err.code
        except (urllib.error.URLError, TimeoutError) as err:
            return f"error: {err}"
    return "error"


def title_ratio(title: str, line: str) -> float:
    t, l = norm(title), norm(line)
    if t and t in l:
        return 1.0
    match = difflib.SequenceMatcher(None, t, l).find_longest_match(0, len(t), 0, len(l))
    return round(match.size / max(len(t), 1), 2)


def check_line(line: str, min_ratio: float, timeout: float) -> dict | None:
    doi_m = DOI.search(line)
    if doi_m:
        doi = doi_m.group(1).rstrip(".,;")
        result = {"doi": doi, "line": line.strip()[:300]}
        try:
            msg = fetch_json("https://api.crossref.org/works/" + urllib.parse.quote(doi), timeout)["message"]
        except urllib.error.HTTPError as err:
            result.update(status="fail", reason=f"Crossref HTTP {err.code}: DOI not registered or mistyped")
            return result
        except (urllib.error.URLError, TimeoutError, ValueError) as err:
            result.update(status="unchecked", reason=f"network: {err}")
            return result
        title = (msg.get("title") or [""])[0]
        authors = [a.get("family", "") for a in msg.get("author", [])]
        year = (msg.get("issued", {}).get("date-parts") or [[None]])[0][0]
        ratio = title_ratio(title, line)
        problems = []
        if ratio < min_ratio:
            problems.append(f"title mismatch ({ratio})")
        if authors and norm(authors[0]) and norm(authors[0]) not in norm(line):
            problems.append(f"first author '{authors[0]}' not in entry")
        if year and str(year) not in line:
            problems.append(f"year {year} not in entry")
        result.update(status="mismatch" if problems else "ok", problems=problems,
                      crossref={"title": title, "first_author": authors[0] if authors else None,
                                "year": year, "container": (msg.get("container-title") or [""])[0]})
        return result
    url_m = URL.search(line)
    if url_m:
        url = url_m.group(0).rstrip(".,;")
        status = url_status(url, timeout)
        ok = isinstance(status, int) and status < 400
        return {"url": url, "line": line.strip()[:300], "status": "ok" if ok else "fail", "http": status,
                "note": "URL reachable; open it and confirm it supports the claim" if ok else "unreachable"}
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path")
    parser.add_argument("--min-title-ratio", type=float, default=0.6)
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args(argv)
    results = []
    for line in Path(args.path).read_text(encoding="utf-8").splitlines():
        res = check_line(line, args.min_title_ratio, args.timeout)
        if res:
            results.append(res)
    summary = {s: sum(1 for r in results if r["status"] == s) for s in ("ok", "mismatch", "fail", "unchecked")}
    print(json.dumps({"summary": summary, "results": results}, indent=2, ensure_ascii=False))
    return 0 if summary["mismatch"] == summary["fail"] == summary["unchecked"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
