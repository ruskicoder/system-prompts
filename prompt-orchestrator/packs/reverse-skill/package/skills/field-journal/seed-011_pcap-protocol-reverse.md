# [seed] Reverse Engineering a Custom Binary Protocol from a PCAP

## Scenario classification
Traffic capture analysis / protocol reverse engineering

## Target overview
An IoT device/desktop client uses a custom binary protocol over TCP (not HTTP). With a captured PCAP, recover the frame structure, field meanings and the encryption layer (if any), and write a local client/server reproduction.

## Complete execution chain

1. Open the PCAP in Wireshark and run the basic statistics first
   - `Statistics → Conversations` to see IP/port pairs
   - `Statistics → I/O Graphs` to see the data rhythm
2. Find the real application layer stream (strip standard layers such as TLS)
3. On a TCP stream → `Follow → TCP Stream` → switch to RAW mode → export
4. Binary-level observation: are the first few bytes of each frame a fixed magic / length field?
   ```bash
   xxd dump.bin | head -20
   ```
5. Look for patterns in hex mode: fixed header, length, TLV, CRC
6. Write a Python parser (struct + scapy) that decodes frame by frame
7. In parallel, cross-check the protocol fields from the decompiled binary (look at the structs around send/recv in IDA / Ghidra)
8. Verify: start your own client and send a frame → the server responds consistently

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Wireshark does not recognize the protocol and only shows "Data" | It is a private protocol with no dissector | Write a Wireshark Lua dissector or analyze offline directly in Python | 30min |
| No apparent pattern; every frame differs | There is a compression or encryption layer | Judge encryption with entropy analysis (`ent dump.bin`); look for nonce/IV fields | 1h |
| The length field does not add up | The length may be little-endian / big-endian / include or exclude itself | Take several frames of different lengths and solve the equations | 40min |
| TLS captured but cannot be decrypted | The client does not write SSLKEYLOGFILE | Hook at the client process layer (Frida capturing ssl_read/ssl_write) for plaintext | 1.5h |
| The data is correct but the server does not respond | The protocol carries an incrementing seq / nonce, and replays are rejected | Work out how seq is computed (usually the hash of the previous frame or an incrementing counter) | 50min |

## Toolchain findings

- A **Wireshark Lua Dissector** turns a private protocol into a Wireshark visualization in < 100 lines
- With **scapy**, a Python parser just defines a `Packet` subclass
- **Kaitai Struct** describes protocol structures in YAML and generates parsers in many languages (Python/Java/C++/JS), suited to long-term reuse
- **NetworkMiner** suits "after-the-fact forensics" better than Wireshark (reassembles files automatically, recognizes credentials)
- **ent / binwalk -E** for entropy; >7.5 is almost certainly encrypted

## Key code/commands

scapy custom protocol example (TLV):

```python
from scapy.all import *

class MyMsg(Packet):
    name = "MyProto"
    fields_desc = [
        StrFixedLenField("magic", b"\xab\xcd", 2),
        ByteField("version", 1),
        ByteField("type", 0),
        LenField("length", None, fmt="H"),     # H = uint16 BE
        XIntField("seq", 0),
        StrLenField("payload", "", length_from=lambda p: p.length - 8),
        XShortField("crc", 0),
    ]

# parse the PCAP
pkts = rdpcap('dump.pcap')
for p in pkts:
    if TCP in p and p[TCP].dport == 9527 and p.payload:
        msg = MyMsg(bytes(p[TCP].payload))
        msg.show()
```

Kaitai Struct YAML (first choice for long-term projects):

```yaml
# myproto.ksy
meta:
  id: myproto
  endian: be
seq:
  - id: magic
    contents: [0xab, 0xcd]
  - id: version
    type: u1
  - id: type
    type: u1
  - id: length
    type: u2
  - id: seq_no
    type: u4
  - id: payload
    size: length - 8
  - id: crc
    type: u2
```

Entropy analysis:

```bash
binwalk -E dump.bin             # entropy graph
ent dump.bin                    # numeric value
```

## Improvement suggestions for this package

- Add a "four-step custom protocol reverse engineering" chapter to `reverse-engineering/platforms.md`
- Add a `reverse-engineering/references/kaitai-cheatsheet.md` quick reference
- Add scapy (pip) and binwalk to the bootstrap manifest

## Reusable patterns/script snippets

**Four-step custom protocol reverse engineering**:

```text
1. Watch the rhythm (I/O graphs + Conversations to find session boundaries)
2. Find the frame boundaries (magic / length / terminator)
3. Split the fields (fixed header, length, payload, checksum)
4. Check for encryption (entropy + look for a nonce + cross-check the send function in the binary)
```

**A trick for finding the frame length**:

Export all PSH packets of the same stream → check the total length of each TCP segment, and whether a length field (try positions i, i+1, i+2) predicts the segment length.

## Evolution actions
- [ ] Add a protocol reverse engineering chapter to reverse-engineering/platforms.md
- [ ] Add scapy / binwalk to the bootstrap-manifest
- [ ] Add a Kaitai Struct quick reference

## Environment information
- Kali / Ubuntu, Wireshark 4.x, Python 3.10+, scapy 2.5
- Target protocol: custom TCP binary (with TLV / length prefix)
- Encryption layer: depends on the case (commonly AES-CTR / ChaCha20)

## Redaction requirements
This entry is seed data, written from public protocol reverse engineering methods, with no real product involved.
