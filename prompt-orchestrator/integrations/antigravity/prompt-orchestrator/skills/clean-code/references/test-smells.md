# Test Smells

Load this when writing or reviewing tests. Tiers run from tests that lie to tests that are only
untidy. Report the tier honestly: a style nit is not a false-confidence finding, and a test
that cannot fail is never a nit.

## Tier 1: false confidence (the test passes when the code is wrong)

| Smell | Signs | Fix |
|-------|-------|-----|
| No assertion | The test runs code and checks nothing (verifying a mock call does count as an assertion) | Assert the outcome the test is named for |
| Unawaited async assertion | An assertion on a promise, task or coroutine that is never awaited | Await or return it; confirm it can fail |
| Coverage touching | Every public method called in turn with no meaningful check | Replace with behaviour tests, or delete |
| Self-referential expectation | The expected value is computed from the actual value or by the same code under test | Use an independently known expected value |
| Swallowed exception | A catch block with no rethrow or assertion | Use the framework's expect-to-throw form |
| Assert only in a catch | The test passes when nothing is thrown, whatever the result | Assert the result on the success path too |
| Always-true assertion | `assert true`, `x == x`, or a condition that cannot fail | Remove it and assert something real |
| Commented-out assertion | The test still runs and still counts as coverage | Restore it or delete the test |
| Weak transformation oracle | A normalising or converting test feeds input already in the output form, so a no-op passes | Feed input that must change; derive the expected value independently |

## Tier 2: tests that cause pain

| Smell | Signs | Fix |
|-------|-------|-----|
| Flaky timing | Sleeps used to wait, wall-clock reads, unseeded randomness, hard-coded paths or hosts | Inject the clock and the random source; wait on a condition, not a duration |
| Order dependency | Shared mutable state between tests; a test that passes alone and fails in the suite, or the reverse | Reset state per test; remove globals |
| Over-mocking | More mock setup than test logic; mocks of types the test owns; exact call sequences asserted | Mock only real boundaries; assert outcomes |
| Implementation coupling | Private methods reached by reflection; internal state asserted; call counts on collaborators | Test through the public interface |
| Broad exception check | Expecting any exception, with no type or message check | Assert the specific type and the relevant message |
| Deep mock chains | A test mocks several levels of objects to reach the code | Often a Law of Demeter problem in the code under test; fix the code's reach first |

## Tier 3: maintainability

| Smell | Signs | Fix |
|-------|-------|-----|
| Vague name | `test1`, `testMethod`, a name that does not say the scenario and the expected result | Name the behaviour and the break it catches |
| Magic values | Unexplained numbers and strings in setup or assertions | Name them, or derive them visibly |
| Copy-paste tests | Three or more tests differing in one input | Parametrise; keep separate tests for distinct edge cases |
| Giant test | Many behaviours checked in one test | Split per behaviour |
| Useless assertion message | The message restates the assertion | Say what the failure means in the domain |
| Phases mixed | Arrange, act and assert interleaved | Separate the three phases |

## Tier 4: hygiene

| Smell | Signs | Fix |
|-------|-------|-----|
| Dead fixtures | Setup or teardown hooks that do nothing; helpers never called | Delete them |
| Leaked resources | Files, connections, servers or temp data never cleaned up | Use the language's scoped cleanup |

## Checks that a test is worth keeping
- It names the break it would catch.
- It exercises the real code path, faking only real boundaries.
- It fails when the code it covers is broken: change an operator or return a constant in the
  code under test, run it, and watch it go red. Restore the code after.
- It is deterministic: run it several times and in a different order.

## Test patterns worth using

| Pattern | Use |
|---------|-----|
| Test doubles by role | Dummy (filler), stub (canned answers), spy (records calls), mock (verifies expected calls), fake (working lightweight implementation such as an in-memory repository). Prefer fakes for owned boundaries and stubs for queries; reserve mocks for verifying commands sent to real external boundaries |
| Test data builder | Builds valid objects with defaults, overriding only what the test is about |
| Object mother | Named, ready-made fixtures for common scenarios; switch to builders when variants multiply |
| Arrange, act, assert | Three visible phases per test |
| Parametrised tests | One test body over a table of inputs and expected outputs |
| Characterization and approval tests | Pin current behaviour of legacy code before changing it (refactoring skill) |
| Property-based tests | Generate inputs and assert invariants (round trips, ordering, idempotency); good for parsers, serializers and pure logic |
| Contract tests | Check a provider against what its consumers rely on (consumer-driven where consumers are known) |
| Page object / screen object | UI tests talk to a model of the page, not to selectors scattered across tests |
| Test pyramid by cost | Many fast unit tests, fewer integration tests, few end-to-end tests; push each check to the cheapest level that can catch the bug |
