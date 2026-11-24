# Release Checklist

> Check each item before every release. Source of truth for the version: the VERSION file must match the latest released version in CHANGELOG.md (the CI version-check job verifies this automatically and fails on a mismatch).

## Release steps

1. [ ] Confirm that the [Unreleased] section of CHANGELOG.md is complete (Keep a Changelog groups: Added / Fixed / Security / Removed)
2. [ ] Change `## [Unreleased]` to `## [x.y.z] — YYYY-MM-DD`, and update the compare link from ...HEAD to the new tag
3. [ ] Update the VERSION file to x.y.z in the same change
4. [ ] For milestone versions (such as v1.0.0 / v1.1.0), also update docs/RELEASE_NOTES_v<x.y.z>.md
5. [ ] Tag: git tag v<x.y.z> + git push --tags
6. [ ] After pushing, confirm that CI is all green (routing 221 benchmark + coherence + pin gate + version-check)

## Metadata sync (items to handle during a release)

- Bootstrap capability added or removed: sync the capability lists in RULES.md / skills/SKILL.md (skills/scripts/bootstrap-manifest.json is the single source of truth, currently 26 entries; Kali-only capabilities are in kali/scripts/bootstrap-manifest.json)
- New field-journal entry: update the three places in skills/field-journal/_index.md (scenario categories / frequent patterns / entity inverted index) and the statistics
- Routing rule change: change only skills/config/routing.json (generator scripts maintain the docs, or the docs at least stay consistent)

> Note: journal entries no longer keep a hand-maintained cumulative <!-- [evolution stats] --> comment at the bottom (removed on 2026-08-10 because the numbers could not be maintained reliably); _index.md is authoritative for project counts.
