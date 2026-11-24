#!/usr/bin/env python3
"""Download the optional reference library (1,432 brand SVGs, about 12 MB) into assets/library/svg/.

The prompt-orchestrator copy of this skill ships without these files. They are trademarks of their owners and are
for study only (see TRADEMARKS.md). The files come from the upstream repository at the vetted commit, and each one
is checked against assets/library/svg-manifest.sha256; a file that is not listed or does not match is not written.

    python3 scripts/fetch_library.py
"""
import hashlib
import os
import sys
import tarfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svglib  # noqa: E402

COMMIT = "e9eaddc07895575253d6663320354a708f53e955"
URL = f"https://codeload.github.com/kaankiziltug/logo-design-skill/tar.gz/{COMMIT}"
PREFIX = "skills/logo-design/assets/library/svg/"
MANIFEST = os.path.join(svglib.LIBRARY_DIR, "svg-manifest.sha256")


def load_manifest():
    want = {}
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            digest, name = line.split(None, 1)
            name = name.strip()
            if "/" in name or "\\" in name or not name.endswith(".svg"):
                raise ValueError(f"bad manifest entry: {name!r}")
            want[name] = digest
    return want


def main():
    want = load_manifest()
    os.makedirs(svglib.LIBRARY_SVG_DIR, exist_ok=True)
    written, mismatched = set(), []
    with urllib.request.urlopen(URL, timeout=60) as resp, tarfile.open(fileobj=resp, mode="r|gz") as tar:
        for member in tar:
            rel = member.name.split("/", 1)[-1]
            if not member.isfile() or not rel.startswith(PREFIX):
                continue
            name = rel[len(PREFIX):]
            if name not in want:
                continue
            data = tar.extractfile(member).read()
            if hashlib.sha256(data).hexdigest() != want[name]:
                mismatched.append(name)
                continue
            with open(os.path.join(svglib.LIBRARY_SVG_DIR, name), "wb") as fh:
                fh.write(data)
            written.add(name)
    missing = sorted(set(want) - written - set(mismatched))
    print(f"{len(written)} of {len(want)} SVGs written to {svglib.LIBRARY_SVG_DIR}")
    for name in mismatched:
        print(f"hash mismatch, skipped: {name}")
    for name in missing:
        print(f"not found upstream: {name}")
    return 1 if mismatched or missing else 0


if __name__ == "__main__":
    sys.exit(main())
