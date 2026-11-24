# Protocol Reverse Engineering Quick Reference

> Applies to: the `protocol-reverse` skill · 2026-07-18

## Common layout patterns

| Pattern | Traits | Hint |
|------|------|------|
| Fixed header + body | Length in the first 2/4 bytes | Check whether it includes the header length |
| Magic number | Fixed `0xDEAD` and similar | Helps resynchronize the stream |
| TLV | Repeated type-length-value | The type enumeration is the message dictionary |
| Protobuf | Field number varint | `protoc --decode_raw` |
| Encrypted frames | High entropy, no plaintext URLs | Look near the nonce/IV first |

## Minimal Python skeleton

```python
import struct
def parse_frame(buf: bytes):
    magic, length, msg_type = struct.unpack_from(">IHI", buf, 0)
    body = buf[10:10+length]
    return {"magic": magic, "type": msg_type, "body": body}
```

## Extract TCP payloads from a PCAP

```bash
tshark -r cap.pcap -Y "tcp.port==4433" -T fields -e tcp.payload | head
```