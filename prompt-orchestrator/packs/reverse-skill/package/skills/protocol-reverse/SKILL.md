---
name: protocol-reverse
description: Use for authorized reverse engineering of custom binary protocols, Protobuf/gRPC, WebSocket frames, and PCAP-driven protocol recovery.
---

# Protocol Reverse Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm the authorization and routine operation boundaries
2. `NOW`: confirm whether the task is **protocol/traffic/serialization format** reverse engineering (not pure web parameter signing → switch to `js-reverse/`)
3. `NOW`: if there is network interaction with a target → complete scope with `../scripts/case-init.ps1`; ACT against the target is forbidden while `auth` is not granted
4. `NEXT`: read `../tool-index.md`; bootstrap missing tools (tshark/wireshark and similar may need manual installs)
5. `ACT`: enter Phase 1 of the workflow and produce a draft of the frame layout or message dictionary

## When to use

- Custom TCP/UDP binary protocols
- Protobuf / gRPC / FlatBuffers / MessagePack
- WebSocket / MQTT / private RPC
- Reconstruct fields and state machines from PCAP / PCAPNG
- Client-server checks, sequence numbers, encrypted frame headers

## Not for this skill

| Situation | Where to go |
|------|------|
| HTTP parameter signing / JS crypto only | `js-reverse/` |
| TLS certificate issues only | `pentest-tools/` or a browser proxy |
| Deep dive into a protocol stack inside firmware + emulation | `firmware-pentest/` first, then back to this skill |

## Workflow

### Phase 1: Collection and triage

```text
□ Get the samples: PCAP / proxy export / client logs / binary
□ Mark directions: C→S / S→C; handshake, heartbeat, reconnection?
□ Fixed header? Magic number? Length field? TLV? Fixed length?
□ Compressed (zlib/gzip/lz4) or encrypted (AES/ChaCha inside frames)?
□ tshark -r cap.pcap -T fields -e frame.number -e ip.src -e tcp.payload
```

### Phase 2: Frame layout reconstruction

```text
□ Align several messages of the same type and find constant bytes / incrementing sequence numbers
□ Length field: big endian/little endian, header included or not
□ Checks: CRC16/32, checksum, HMAC position
□ Draw the state machine: Connect → Auth → Ready → Request/Response → Close
□ Tools: draft Wireshark custom dissector / ImHex / 010 Editor template / Kaitai Struct
```

### Phase 3: Serialization and encryption

```text
□ Protobuf: recover the .proto (blackboxprotobuf / pbtk / protoc --decode_raw)
□ gRPC: HTTP/2 headers + protobuf body
□ Encryption: find the key derivation (client so/dll/JS) → combine with ida-reverse / js-reverse / apk-reverse
□ Replay: only within the authorized scope; harmless fields first, then sensitive operations
```

### Phase 4: Outputs

```text
MUST produce:
- Message type table (name / opcode / fields)
- At least 1 reproducible decode command or script
- Evidence: raw hex excerpt + decode result (redacted)
```

## Toolchain

| Tool | Required | Purpose | Bootstrap |
|------|------|------|------|
| tshark / Wireshark | Strongly recommended | PCAP parsing | Manual / winget |
| Python3 | Yes | Decode scripts | System |
| blackboxprotobuf | Optional | Unknown protobuf | pip |
| ImHex / 010 | Optional | Structure templates | Manual |
| IDA / r2 / Ghidra | As needed | Client serialization functions | See the matching skill |

## References

- `references/protocol-workflow.md`: frame layout and Protobuf quick reference
- Related: `../ida-reverse/` `../js-reverse/` `../firmware-pentest/` `../pentest-tools/`

## Routing context

**Upstream**: `MASTER-ROUTING` R21 · `routing.md`  
**Downstream**: client algorithm needed → `ida-reverse`/`js-reverse`; replay exploitation needed → `pentest-tools`/`api-security`  
**Sibling**: `malware-analysis` (C2 protocols), `digital-forensics` (traffic forensics)

## Task completion self-check

- [ ] Did I reconstruct the message layout or state machine (not just paste hex)?
- [ ] Is there a reproducible decode command?
- [ ] Did I respect scope / redaction?
- [ ] Did I write back to field-journal / the report Checklist?