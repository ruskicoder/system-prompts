# Encryption/Decryption / Encoding/Decoding Tool Quick Reference

> Reverse engineering and CTFs often meet encrypted/encoded/hashed data. This document lists the most practical tools by scenario.

---

## Automatic identification + decryption (when you do not know which encryption was used)

| Tool | Stars | Purpose | Link |
|------|-------|------|------|
| **Ciphey** | 18k+ | AI automatic identification and decryption (supports 50+ encodings/ciphers/hashes) | https://github.com/Ciphey/Ciphey |
| **CyberChef** | 29k+ | Online/offline Swiss army knife for encoding and decoding (drag and drop) | https://github.com/gchq/CyberChef |
| **dcode.fr** |: | 900+ online cipher/encoding/math tools | https://www.dcode.fr/ |

### Using Ciphey

```bash
pip install ciphey
# Detect and decrypt automatically
ciphey -t "ciphertext"
# Read from a file
ciphey -f encrypted.txt
```

Ciphey supports: Base64/32/16, Caesar, Vigenere, XOR, AES (weak keys), Morse, Binary, Hex, URL encoding, HTML entities, hash identification and more.

### Using CyberChef

```text
Online version: https://gchq.github.io/CyberChef/
Offline version: download the HTML file from the GitHub Release and open it directly

Common recipes:
- From Base64 → decode Base64
- XOR → XOR decryption (keys can be brute-forced)
- AES Decrypt → AES decryption
- Magic → detect the encoding type automatically
```

---

## Hash identification and cracking

| Tool | Purpose | Link |
|------|------|------|
| **hashID** | Identify hash types (MD5/SHA/bcrypt and others) | https://github.com/psypanda/hashID |
| **hash-identifier** | Same as above, Python version | https://github.com/blackploit/hash-identifier |
| **haiti** | Modern hash identification tool (more accurate) | `gem install haiti` |
| **Hashcat** | GPU hash cracking | https://hashcat.net/ |
| **John the Ripper** | CPU hash cracking | https://www.openwall.com/john/ |
| **hashes.com** | Online hash lookup (rainbow tables) | https://hashes.com/ |

```bash
# Identify the hash type
hashid '5f4dcc3b5aa765d61d8327deb882cf99'
# Output: [+] MD5

# haiti (more accurate)
haiti '5f4dcc3b5aa765d61d8327deb882cf99'

# Hashcat cracking
hashcat -m 0 hash.txt rockyou.txt  # MD5
hashcat -m 1000 hash.txt rockyou.txt  # NTLM
```

---

## RSA attacks

| Tool | Purpose | Link |
|------|------|------|
| **RsaCtfTool** | Automatic RSA attacks (20+ attack methods) | https://github.com/Ganapati/RsaCtfTool |
| **SageMath** | Mathematical computation (large number factorization/elliptic curves) | https://www.sagemath.org/ |
| **factordb.com** | Online large number factorization lookup | http://factordb.com/ |
| **yafu** | Local large number factorization | https://github.com/bbuhrow/yafu |

```bash
# RsaCtfTool automatic attack
python RsaCtfTool.py --publickey pub.pem --private
python RsaCtfTool.py --publickey pub.pem --uncipherfile cipher.txt

# Supported attacks:
# Wiener, Boneh-Durfee, Fermat, Pollard p-1, Williams p+1
# Common modulus, Small q, Hastads, Noveltyprimes and others
```

---

## XOR analysis

| Tool | Purpose | Link |
|------|------|------|
| **xortool** | XOR key length guessing + known plaintext attack | https://github.com/hellman/xortool |
| **CyberChef XOR** | Visual XOR operations | Built into CyberChef |

```bash
# Guess the XOR key length
xortool encrypted_file
# Decrypt with the guessed key length
xortool -l 4 -c 00 encrypted_file

# Known plaintext attack (part of the plaintext is known)
xortool-xor -f encrypted -s "known_plaintext"
```

---

## Classical ciphers

| Cipher type | Tool | Notes |
|---------|------|------|
| Caesar | CyberChef / dcode.fr | Brute-force the 25 shifts |
| Vigenere | dcode.fr / Ciphey | The key length must be guessed |
| Substitution | quipqiup.com | Automatic solving by frequency analysis |
| Enigma | dcode.fr | Online simulator |
| Rail Fence | dcode.fr / CyberChef | Rail fence cipher |
| Playfair | dcode.fr | Needs the key |
| Morse | CyberChef | Dots and dashes to text |
| Bacon | dcode.fr | Binary steganography |
| ROT13/47 | CyberChef / `tr` | Simple substitution |

---

## Encoding identification and conversion

| Encoding | Identification traits | Decoding |
|------|---------|---------|
| Base64 | Ends with `=` or `==`, character set A-Za-z0-9+/ | `base64 -d` / CyberChef |
| Base32 | Uppercase letters + 2-7, ends with `=` | CyberChef |
| Base58 | No 0/O/I/l, common in short identifier encodings | CyberChef |
| Hex | Only 0-9a-f, even length | `xxd -r -p` / CyberChef |
| URL encoding | `%XX` format | `urldecode` / CyberChef |
| HTML entities | `&#XX;` or `&amp;` format | CyberChef |
| Unicode escape | `\uXXXX` format | Python `decode('unicode_escape')` |
| JWT | `xxxxx.yyyyy.zzzzz` (three Base64URL parts) | jwt.io / CyberChef |
| Brainfuck | Only the eight characters `><+-.,[]` | Online interpreter |
| Ook! | Only `Ook.` `Ook!` `Ook?` | Online interpreter |

---

## Identifying crypto in reverse engineering

### Identify the algorithm by constants

| Constant/trait | Algorithm |
|-----------|------|
| `0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476` | MD5 |
| `0x6A09E667, 0xBB67AE85, 0x3C6EF372` | SHA-256 |
| `0x63, 0x7C, 0x77, 0x7B` (start of the S-Box) | AES |
| `0x243F6A88` (π in hexadecimal) | Blowfish |
| `0xB7E15163, 0x9E3779B9` | RC5/RC6/TEA |
| `0x61707865` ("expa") | ChaCha20/Salsa20 |
| `0xC6EF3720` | XTEA |

### Identify by behavior

| Behavioral trait | Possible algorithm |
|---------|-----------|
| 256-byte lookup table + swap operations | RC4 |
| 16-byte blocks + multiple permutation rounds | AES |
| Feistel structure (left-right swap) | DES/Blowfish/TEA |
| Large number multiplication/modular exponentiation | RSA |
| Elliptic curve point operations | ECDSA/ECDH |
| Fixed 64-round loop | TEA/XTEA |
| 32 rounds + delta constant | XTEA |

---

## Automated cryptanalysis

| Tool | Purpose | Link |
|------|------|------|
| **FeatherDuster** | Automated cryptanalysis framework | https://github.com/nccgroup/featherduster |
| **PkCrack** | ZIP known plaintext attack | https://www.unix-ag.uni-kl.de/~conrad/krypto/pkcrack.html |
| **bkcrack** | ZIP known plaintext attack (modern version) | https://github.com/kimci86/bkcrack |
| **z3** | SMT solver (constraint solving) | https://github.com/Z3Prover/z3 |
| **angr** | Symbolic execution (solve inputs automatically) | https://angr.io/ |

---

## Quick decision tree

```text
Given an unknown piece of data:

1. Look at the length and character set
   - Only hex characters → possibly hex encoding or a hash
   - Ends with = → Base64
   - Three dot-separated parts → JWT
   - 32/40/64 hex characters → hash (MD5/SHA1/SHA256)

2. Try Ciphey automatically
   ciphey -t "data"

3. If Ciphey fails → use the CyberChef Magic mode

4. If it is a hash → identify the type with hashID → crack with Hashcat/John

5. If it is RSA → automatic attack with RsaCtfTool

6. If it is XOR → analyze the key with xortool

7. If it is traditional ZIP encryption → prefer the `bkcrack` known plaintext attack; do not start with password brute force without evidence

8. If it is custom encryption → reverse the algorithm in IDA/Ghidra → write a decryption script by hand
```

---

## Online resources

| Resource | Link | Purpose |
|------|------|------|
| CyberChef | https://gchq.github.io/CyberChef/ | All-purpose encoding and decoding |
| dcode.fr | https://www.dcode.fr/ | 900+ cipher tools |
| quipqiup | https://quipqiup.com/ | Automatic substitution cipher solving |
| factordb | http://factordb.com/ | RSA large number factorization |
| jwt.io | https://jwt.io/ | JWT decoding/verification |
| hashes.com | https://hashes.com/ | Hash lookup |
| crackstation | https://crackstation.net/ | Online hash cracking |
