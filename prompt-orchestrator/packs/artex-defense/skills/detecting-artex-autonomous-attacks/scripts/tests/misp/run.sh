#!/usr/bin/env bash
# Modified by prompt-orchestrator on 2026-11-27 (AGPL-3.0 section 5(a)): mounts references/ as the detections tree and drops the CI workflow mount; changed again on 2026-11-28 to pin the default images by digest.
#
# Reproducible consistency test for the MISP-format export of the ARTEX
# indicators (see check.py for the assertions). It proves two things no other
# detection test does: that detections/indicators/artex_indicators.misp.json is
# a MISP document pymisp actually parses (every attribute type/category is a real
# MISP type a server would accept), and that it stays row-for-row in sync with
# the source-of-truth CSV it is generated from — same values, the intended MISP
# type/category per indicator, and a to_ids/disable_correlation flag that mirrors
# the CSV's own honesty (rule-backed = actionable; host-forensic = triage hint).
#
# No host dependency beyond Docker: pymisp is pinned and installed inside the
# container, and the detection tree and CI workflow are mounted read-only.
# Nothing is installed on the host and nothing is written to the repo tree.
#
# Usage:   detections/tests/misp/run.sh
# Env:     PYTHON_IMAGE    (default python:3.12-slim, pinned by digest below)
#          PYMISP_VERSION  (default 2.5.34.4 — the pinned reference version)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
# prompt-orchestrator pack: the default image is pinned by digest. The digest was read on
# 2026-11-28 from Docker Hub for the tag python:3.12-slim. PYTHON_IMAGE still overrides it.
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016}"
PYMISP_VERSION="${PYMISP_VERSION:-2.5.34.4}"

docker run --rm \
  -e ARTEX_REPO_ROOT=/repo \
  -e PYMISP_VERSION="$PYMISP_VERSION" \
  -v "$REPO/references:/repo/detections:ro" \
  -v "$HERE:/src:ro" \
  "$PYTHON_IMAGE" sh -c 'pip install --quiet "pymisp==${PYMISP_VERSION}" && python3 /src/check.py'
