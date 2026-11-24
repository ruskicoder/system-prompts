# CTF Resource Essentials Quick Reference

> Selected from [awesome-ctf-resources](https://github.com/devploit/awesome-ctf-resources) and [awesome-ctf](https://github.com/apsdehal/awesome-ctf)
> Grouped by CTF challenge type, keeping only the most practical tools and resources.

---

## General frameworks

| Tool | Purpose | Link |
|------|------|------|
| Pwntools | Exploit development framework (Python) | https://github.com/Gallopsled/pwntools |
| ctf-tools | One-command install of a CTF tool set | https://github.com/zardus/ctf-tools |
| Ciphey | AI automatic decryption | https://github.com/ciphey/ciphey |
| CyberChef | Online encoding/decoding/encryption/decryption | https://gchq.github.io/CyberChef/ |

---

## Web

### Tools
| Tool | Purpose |
|------|------|
| Burp Suite | HTTP interception/replay/scanning |
| SQLMap | SQL injection |
| XSStrike | XSS detection |
| dirsearch | Directory discovery |
| JWT_Tool | JWT attacks |
| SSRFmap | SSRF exploitation |

### Common topics
- SQL injection (union query/blind/time-based blind/stacked)
- XSS (reflected/stored/DOM)
- SSRF (internal network probing/cloud metadata)
- File upload (bypass extension/MIME/content checks)
- Deserialization (PHP/Java/Python pickle)
- Template injection (SSTI)
- JWT forgery/key confusion

### Payload references
- https://github.com/swisskyrepo/PayloadsAllTheThings
- https://book.hacktricks.wiki/

---

## Reverse

### Tools
| Tool | Purpose |
|------|------|
| IDA Pro / Ghidra | Decompilation |
| radare2 / r2 | CLI analysis |
| angr | Symbolic execution |
| Frida | Dynamic hooking |
| GDB + pwndbg | Debugging |
| uncompyle6 | Python decompilation |
| jadx | Android decompilation |
| dnSpy | .NET decompilation |

### Common topics
- Algorithm reconstruction (encryption/encoding/custom)
- Anti-debugging/anti-VM bypass
- Packers/obfuscation (UPX/VMProtect/OLLVM)
- Symbolic execution to solve constraints
- Dynamic hooks to bypass checks
- Go/Rust reverse engineering (symbol recovery)

---

## Pwn

### Tools
| Tool | Purpose |
|------|------|
| Pwntools | Exploit writing |
| GDB + pwndbg/GEF | Debugging |
| ROPgadget | ROP chain construction |
| one_gadget | libc one-shot |
| checksec | Protection detection |
| LibcSearcher | libc version identification |

### Common topics
- Stack overflow (ret2text/ret2libc/ret2shellcode/ROP)
- Heap exploitation (UAF/double free/tcache/fastbin)
- Format strings (arbitrary read/write)
- Integer overflow
- Kernel pwn (privilege escalation/race conditions)
- Sandbox escape (seccomp bypass)

### Common payload patterns
```python
# ret2libc template
from pwn import *
elf = ELF('./vuln')
libc = ELF('./libc.so.6')
p = process('./vuln')
# leak libc base → calculate system/binsh → overwrite ret
```

---

## Crypto

### Tools
| Tool | Purpose |
|------|------|
| SageMath | Mathematical computation |
| RsaCtfTool | Automatic RSA attacks | 
| hashcat/john | Hash cracking |
| CyberChef | Encoding/decoding |
| z3 (SMT solver) | Constraint solving |

### Common topics
- RSA (small public exponent/common modulus/Wiener/Coppersmith)
- AES (ECB/CBC padding oracle/bit flipping)
- Classical ciphers (Caesar/Vigenere/transposition)
- Hash length extension attacks
- Elliptic curves (ECDSA nonce reuse)
- Lattice cryptography (LLL/CVP)

---

## Forensics

### Tools
| Tool | Purpose |
|------|------|
| Volatility | Memory forensics |
| Autopsy/Sleuth Kit | Disk forensics |
| Wireshark | Traffic analysis |
| binwalk | Firmware/file extraction |
| foremost | File recovery |
| exiftool | Metadata extraction |

### Common topics
- Memory dump analysis (processes/passwords/malicious code)
- PCAP traffic analysis (HTTP/DNS/TCP reassembly)
- Filesystem analysis (deleted file recovery/hidden partitions)
- Log analysis (web logs/system logs)
- Disk image analysis

---

## Misc/Stego

### Tools
| Tool | Purpose |
|------|------|
| StegSolve | Image steganography analysis |
| zsteg | PNG/BMP steganography |
| steghide | JPEG steganography |
| Audacity | Audio analysis |
| strings/xxd | Basic analysis |
| file/binwalk | File type identification |

### Common topics
- LSB steganography (least significant bit of images)
- File header repair/concatenation
- QR codes/barcodes
- Audio spectrogram steganography
- ZIP fake encryption/known plaintext attacks
- Encoding identification (Base64/Hex/Morse/Braille)

---

## Online platforms

| Platform | Characteristics | Link |
|------|------|------|
| CTFTime | Event calendar + writeups | https://ctftime.org/ |
| HackTheBox | Hands-on target machines | https://www.hackthebox.com/ |
| TryHackMe | Guided learning | https://tryhackme.com/ |
| PicoCTF | Beginner friendly | https://picoctf.org/ |
| pwnable.kr | Pwn focused | http://pwnable.kr/ |
| cryptopals | Crypto focused | https://cryptopals.com/ |
| OverTheWire | War series challenges | https://overthewire.org/ |
| Root-Me | General challenges | https://www.root-me.org/ |

---

## Writeup resources

| Resource | Link |
|------|------|
| CTFTime Writeups | https://ctftime.org/writeups |
| 0xdf hacks stuff | https://0xdf.gitlab.io/ |
| LiveOverflow (YouTube) | https://www.youtube.com/c/LiveOverflow |
| John Hammond (YouTube) | https://www.youtube.com/c/JohnHammond010 |
| IppSec (HTB walkthrough) | https://www.youtube.com/c/ippsec |
