# Legacy Code: Seams, Sprout, Wrap, Strangle

Load this when code has no tests, cannot be tested as it stands, or is too large to restructure
in place. "Legacy" here means code without a safety net, whatever its age.

## The change algorithm
1. Find the change points: where the new behaviour or the fix has to go.
2. Find test points: where the effect of the code can be observed.
3. Break the dependencies that stop those points from running in a test, with the smallest
   edits possible.
4. Write characterization tests at the test points.
5. Make the change under the two-hats rule, then refactor.

## Characterization tests
- Record current behaviour, not intended behaviour. A surprising output is pinned as is and
  noted; it gets fixed later in its own step.
- Cover the inputs the change touches: typical values, boundaries, the empty case, the error
  path. Generate inputs when the space is large and the code is pure.
- Golden master: for large or textual outputs (reports, rendered pages, CLI output, generated
  files), store the full output and compare it. Normalize timestamps, ids, ordering and paths
  first, or the master fails on noise and stops being trusted.
- Keep the net fast (seconds, not minutes) so it runs after every step.
- When behaviour later changes on purpose, update the master in that same change and say why.

## Seams
A seam is a place where behaviour can change without editing the code at that place. Make one
with the smallest edit:
- **Parameter seam**: pass the dependency in (clock, client, repository) with the old one as the
  default.
- **Object seam**: extract an interface or a small wrapper around a hard dependency and inject it.
- **Function seam**: route a static or global call through a function the test can replace.
- **Link or module seam**: substitute a module at import or build time when the language allows.
Avoid broad mocking frameworks over pure logic; test pure logic directly.

## Scratch refactoring
When code is too tangled to understand, refactor it freely on a throwaway branch to learn how it
works, then discard that branch and start again with tests. The scratch work is for
understanding only and never ships.

## Sprout and wrap
For new behaviour in untested code when pinning costs more than the time available:
- **Sprout function or class**: write the new behaviour as a new, test-first unit and call it
  from one line in the old code.
- **Wrap function or class**: rename the old entry point, create a new one with the old name
  that adds the new behaviour before or after calling it.
Both leave the old code's shape alone. Record the debt so the refactoring is scheduled.

## Strangler fig
For a subsystem too large or risky to restructure in place:
1. Put a routing seam in front of the capability (a facade, a router, a feature flag).
2. Build the new implementation for one capability behind it.
3. Prove equivalence: run old and new on the same inputs (parallel run or differential test) and
   compare outputs; investigate every difference before routing traffic.
4. Route that capability to the new path; watch errors and outputs.
5. Repeat per capability. Delete the old path once it carries no traffic.
Name the deletion date and the routing check when the migration starts.

## Migration checklist
- [ ] Change points and test points named
- [ ] Seams created with minimal edits, each covered by a test
- [ ] Characterization tests pinned and normalized; fast enough to run every step
- [ ] Equivalence shown by parallel run or differential test before any routing switch
- [ ] Old path removed on schedule; no permanent double maintenance
