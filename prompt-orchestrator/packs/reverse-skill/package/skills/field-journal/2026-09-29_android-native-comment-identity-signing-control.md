# Anonymized Experience Record: Comment Targets and Re-Signed Launch Controls in an Old Android Client

Status: the fix task is complete; this records reusable methods and verification boundaries.

## Scenario

An old Android video client showed image-and-text posts with a comment count but no comment body, and some portrait videos closed the page when switching to full screen. The fix task ran on an authorized physical phone, and the original sample and earlier candidates were kept.

## Reusable findings

A visible comment count does not equal a valid comment target. When parsing an old-format card fails, the comment branch may carry an invalid business ID, while the same native post extension still holds a usable business identity. First confirm that the content identity matches, the business ID is positive and the type maps to existing client semantics, then reuse the native comment component; an explicit server comment URI keeps priority. Unknown, conflicting, cross-content or overflowing input must not be forcibly completed.

A web fallback introduces extra failures. A mobile web page may redirect, and HTTP 200 does not guarantee the expected declared metadata. Record the response status and limited structural information, but prefer the native business fields already received.

Startup failures after a business patch need a signing control that leaves the business code unchanged. A control that matches the original signing format helps narrow down container/initialization hypotheses; it cannot alone prove that a given native library is the primary cause. A process that stays alive briefly at the first prompt also does not count as a passing launch of the recommended home page.

## Verification and boundaries

The user accepted the two given samples of the final build on a real phone, and they link to the correct content and comment business targets. Parsing/type context regressions, original class retention, signing/alignment and the install hash are recorded separately. The fix acceptance covers only this build, this phone and the given samples; the original failure encoding and the first caller of the historical native error remain UNKNOWN.

This record contains no real domains, content IDs, accounts, phone serial numbers, local paths, signing keys, original APKs or original phone logs.
