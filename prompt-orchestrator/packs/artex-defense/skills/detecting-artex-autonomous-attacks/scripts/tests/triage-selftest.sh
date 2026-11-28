#!/usr/bin/env bash
# Modified by prompt-orchestrator on 2026-11-27 (AGPL-3.0 section 5(a)): mounts scripts/, where the pack keeps artex_host_triage.py; changed again on 2026-11-28 to pin the default images by digest.
#
# Non-suite gate: runs the host-triage tool's built-in --self-test in a container.
#
# The triage tool (detections/triage/artex_host_triage.py) is a responder helper,
# not a detection rule, so it is deliberately NOT one of the detections/tests/<x>/
# run.sh suites — that keeps the harness-sync registry exactly the eight rule
# suites (check-harness-sync.py counts only SUITES entries, `detections/tests/<x>/
# run.sh` CI steps, and directories carrying a run.sh; this file is none of them).
# It is a gate like check-harness-sync.sh: both run-all.sh and the detections CI
# workflow call it, so a broken triage check fails the same merge gate as the
# rule suites. A detection you cannot run is only a claim.
#
# The self-test builds its own synthetic host in a temporary directory, asserts
# every check fires on it and that a clean host produces zero findings, and exits
# non-zero on any failure. No host dependency beyond Docker: the tool is pure
# Python standard library and runs in a container with only detections/triage
# mounted read-only; nothing is installed on the host and nothing is written to
# the repo tree.
#
# Usage:   detections/tests/triage-selftest.sh
# Env:     PYTHON_IMAGE  (default python:3.12-slim, pinned by digest below)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
# prompt-orchestrator pack: the default image is pinned by digest. The digest was read on
# 2026-11-28 from Docker Hub for the tag python:3.12-slim. PYTHON_IMAGE still overrides it.
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016}"

docker run --rm \
  -v "$REPO/scripts:/triage:ro" \
  "$PYTHON_IMAGE" python3 /triage/artex_host_triage.py --self-test
