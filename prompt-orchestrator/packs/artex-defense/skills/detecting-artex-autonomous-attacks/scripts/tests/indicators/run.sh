#!/usr/bin/env bash
# Modified by prompt-orchestrator on 2026-11-27 (AGPL-3.0 section 5(a)): mounts references/ as the detections tree and drops the mounts of the ARTEX source, CI and pre-commit files, which the pack does not ship; changed again on 2026-11-28 to pin the default images by digest.
#
# Source-of-truth consistency test for the ARTEX detection indicators
# (see check.py for the assertions). It proves the one thing the Sigma, Suricata,
# and ATT&CK tests do not: that each rule's pinned indicator is still the string
# ARTEX's own source actually emits. The realistic rot it catches is an upstream
# re-sync that bumps the prober User-Agent or rewrites the guard marker — every
# other test stays green while the deployed rule silently stops matching.
#
# No host dependency beyond Docker: the check is pure Python standard library and
# runs in a container with only the rule tree, the published indicator list, the
# source packages it pins, and the two configs that gate on them — the CI workflow
# and the pre-commit hook — mounted read-only (never work/ or anything else).
# Nothing is installed on the host and nothing is written to the repo.
#
# Usage:   detections/tests/indicators/run.sh
# Env:     PYTHON_IMAGE  (default python:3.12-slim, pinned by digest below)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
# prompt-orchestrator pack: the default image is pinned by digest. The digest was read on
# 2026-11-28 from Docker Hub for the tag python:3.12-slim. PYTHON_IMAGE still overrides it.
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016}"

docker run --rm \
  -e ARTEX_REPO_ROOT=/repo \
  -v "$REPO/references:/repo/detections:ro" \
  -v "$HERE:/src:ro" \
  "$PYTHON_IMAGE" python3 /src/check.py
