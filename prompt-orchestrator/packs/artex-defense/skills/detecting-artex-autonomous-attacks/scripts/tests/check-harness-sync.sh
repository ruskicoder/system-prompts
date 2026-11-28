#!/usr/bin/env bash
# Modified by prompt-orchestrator on 2026-11-27 (AGPL-3.0 section 5(a)): mounts this tests folder as the detections/tests tree and drops the CI workflow mount; changed again on 2026-11-28 to pin the default images by digest.
#
# Harness self-consistency check for the detection test suites (see
# check-harness-sync.py for the assertions). It proves the one thing the eight
# detection suites cannot: that run-all.sh, the CI workflow, and the suite
# directories on disk all name the same suites in the same order, so a suite
# wired into only one of the three cannot silently break the "run-all.sh runs the
# same suites as CI" promise while every per-suite test stays green.
#
# It is a gate, not a suite: run-all.sh runs it before the suite loop and it does
# not appear in the per-suite summary, and it is not itself a SUITES entry, a
# `.../run.sh` CI step, or a run.sh directory — so the eight detection suites stay
# eight and this check never counts itself.
#
# No host dependency beyond Docker: the check is pure Python standard library and
# runs in a container with only the detection tree and the CI workflow mounted
# read-only (never work/ or anything else). Nothing is installed on the host and
# nothing is written to the repo.
#
# Usage:   detections/tests/check-harness-sync.sh
# Env:     PYTHON_IMAGE  (default python:3.12-slim, pinned by digest below)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
# prompt-orchestrator pack: the default image is pinned by digest. The digest was read on
# 2026-11-28 from Docker Hub for the tag python:3.12-slim. PYTHON_IMAGE still overrides it.
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016}"

docker run --rm \
  -e ARTEX_REPO_ROOT=/repo \
  -v "$HERE:/repo/detections/tests:ro" \
  -v "$HERE:/src:ro" \
  "$PYTHON_IMAGE" python3 /src/check-harness-sync.py
