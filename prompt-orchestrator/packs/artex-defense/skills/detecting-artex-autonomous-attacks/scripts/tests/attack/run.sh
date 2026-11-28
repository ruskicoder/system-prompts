#!/usr/bin/env bash
# Modified by prompt-orchestrator on 2026-11-27 (AGPL-3.0 section 5(a)): mounts references/ as the detections tree in the pack layout; changed again on 2026-11-28 to pin the default images by digest.
#
# Reproducible consistency test for the ARTEX ATT&CK coverage layer
# (../../attack/artex_navigator_layer.json). A coverage layer that drifts from the
# rules it claims to cover is worse than none, so this turns "these rules cover
# these ATT&CK techniques" from a claim into something a reviewer can re-run from
# source. It catches the realistic regression: a rule is added, removed, or
# retagged, but the Navigator layer is not updated to match.
#
# It proves (see check.py for the assertions) that the layer is a valid Navigator
# v4.x document and that its scored techniques and tactics are EXACTLY the attack.*
# tags on the Sigma rules — no rule technique missing from the layer, no layer
# technique absent from the rules — with every scored technique grounded in a rule
# file that exists.
#
# No host dependency beyond Docker: the check is pure Python standard library and
# runs in a container with the detections tree mounted read-only. Nothing is
# installed on the host and nothing is written to the repo.
#
# Usage:   detections/tests/attack/run.sh
# Env:     PYTHON_IMAGE  (default python:3.12-slim, pinned by digest below)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
DET_DIR="$REPO/references"
# prompt-orchestrator pack: the default image is pinned by digest. The digest was read on
# 2026-11-28 from Docker Hub for the tag python:3.12-slim. PYTHON_IMAGE still overrides it.
PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim@sha256:5b5fe805d367f8f5a359ded6ab2652b7f9a206453ee6ee789c0045ba6ec15016}"

docker run --rm \
  -v "$DET_DIR:/detections:ro" \
  -v "$HERE:/src:ro" \
  "$PYTHON_IMAGE" python3 /src/check.py
