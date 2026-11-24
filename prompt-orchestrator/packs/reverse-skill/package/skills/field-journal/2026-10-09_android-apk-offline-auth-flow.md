# 2026-10-09 Offline Licensing Chain and Embedded Payload Analysis of an Android APK

## Scenario classification

Android APK / offline static analysis / Kotlin coroutines / Smali fallback / embedded native payload

## Reusable flow

1. Pin the SHA-256, ZIP CRCs, DEX, native libraries and key assets inventory of the original APK first.
2. Use JADX and Apktool together; Java handles high-level location, Smali confirms the facts of key methods.
3. Find the input entry from the login layout and Activity, then recover the licensing data flow along the coroutine classes, request builder classes and response models.
4. When JADX outputs `Method not decompiled` for a key coroutine method, go directly to the matching Smali method instead of guessing from incomplete Java.
5. Stream-decompress gzip or otherwise wrapped native assets and compute only the magic number, size, hash, entropy and characteristic strings, without executing the payload.
6. Pin the Manifest, Java, Smali, scripts and payloads as separate Evidence, then form the Findings and the callflow Path.

## Key Evidence patterns

- E-001: original sample hashes, ZIP integrity and content inventory.
- E-006: list of methods JADX did not fully recover, as the basis for switching to Smali.
- E-007: request type, attestation data, response fields and success result pinned from Smali.

## Core Finding

The licensing flow can be recovered as "UI input → coroutine login method → local attestation Map → encrypted transport request → token/expiry/concurrency limit → local session state". If key methods are not decompiled, Smali can provide sufficient call chain evidence, but the real back-end rules still need a separately authorized isolated dynamic analysis.

## Pitfalls and improvements

- When PowerShell reads Markdown, regex line endings must tolerate `\r\n`; otherwise pinned hashes may be misreported as mismatches.
- Do not mix the entropy of compressed files with that of decompressed payloads; the report should state what was measured.
- Do not run embedded scripts, ELFs, APKs or connect to their back end without approval; static conclusions should mark the dynamic verification gap explicitly.

## Privacy handling

This document records no real sample paths, package names, domains, certificate subjects, third-party app names, tokens or user data.
