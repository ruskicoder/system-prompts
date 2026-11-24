# [seed] IoT Router Firmware Extraction + Root over the UART Serial Port

## Scenario classification
Firmware / IoT security

## Target overview
A low-to-mid-range home router: get the firmware bin from the vendor site, extract the squashfs with binwalk, then connect to the device UART over a serial port for a root shell, and analyze its web management interface and startup scripts.

## Complete execution chain

### Part 1: firmware analysis

1. Download the firmware file (vendor site / OpenWRT / dump the flash yourself)
2. Basic identification
   ```bash
   file firmware.bin
   binwalk firmware.bin                    # shows LZMA / SquashFS / U-Boot
   binwalk -E firmware.bin                 # entropy graph to judge whether it is encrypted
   ```
3. Extract
   ```bash
   binwalk -e firmware.bin
   cd _firmware.bin.extracted/squashfs-root
   ```
4. Key points of static analysis
   ```bash
   find . -name 'shadow' -exec cat {} \;          # default password hash
   find . -name '*.cgi' -o -name 'lighttpd*'      # web service
   find . -name 'rcS' -o -name 'init.d'           # startup scripts
   grep -r 'telnetd\|busybox' .                   # suspicious backdoors
   strings $(find . -name 'httpd') | grep -i 'admin\|debug\|backdoor'
   ```
5. Crack `/etc/shadow` offline once you have it:
   ```bash
   john --wordlist=rockyou.txt shadow
   ```

### Part 2: hardware UART

1. Open the case and look at the PCB → find an unused 4-pin / 6-pin header (usually unpopulated or with pins soldered)
2. Identify the pins with a multimeter
   - GND (connected to the ground copper)
   - VCC (3.3V, stable during boot)
   - TX (voltage jumps a lot during boot; outputs toward UART → PC)
   - RX (basically unchanged during boot)
3. Connect a USB-TTL adapter (CP2102 / FT232)
   - Router TX → USB-TTL RX
   - Router RX → USB-TTL TX
   - Router GND → USB-TTL GND
   - **Do not connect VCC** (the device is self-powered)
4. Open a serial listener on the host
   ```bash
   sudo screen /dev/ttyUSB0 115200
   # or: minicom / picocom
   ```
5. Power on → watch the U-Boot output → Linux boot → usually lands at a login prompt
6. Try default credentials / the cracked shadow password → get a root shell

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Empty directory after binwalk extraction | Some firmware uses non-standard formats (vendor private headers) | Slice manually with `dd` against the offsets, or use `unblob` instead of binwalk | 1h |
| binwalk -E shows entropy near 1 | Fully encrypted | Find the decryption key used during firmware upgrades (usually hard-coded in the OEM tool)| Hours |
| No characters on the UART | Wrong baud rate | Try 9600 / 38400 / 57600 / 115200 / 460800 / 921600 | 30min |
| Characters on the UART but garbled | TX/RX swapped / voltage level mismatch | 1) Swap TX RX  2) Confirm the USB-TTL is 3.3V, not 5V | 30min |
| Login prompt but no usable password | Not cracked + the vendor default password was changed | Interrupt at the U-Boot stage with a key press → `setenv bootargs ${bootargs} init=/bin/sh` → single-user mode | 1.5h |
| U-Boot does not respond to key interrupts | The vendor disabled the console / changed the prompt | Find `bootdelay` in the firmware; physically short the SPI flash to force a boot failure so U-Boot goes interactive | Hours |
| Root shell but telnetd does not work | No dropbear/telnetd in the image | Mount a USB drive and copy a busybox-static over | 1h |

## Toolchain findings

- **unblob** is stronger than binwalk (recognizes more formats automatically, does not get stuck on private headers)
- **firmware-mod-kit** is old but still usable for unpacking/packing
- **firmwalker** automatically scans the extracted squashfs for "sensitive leads" (credentials/private keys/URLs/binary backdoors)
- **EMBA** is a comprehensive firmware audit platform (an automated firmwalker + binary CVE scanning + emulated boot)
- **FirmAE** emulates IoT firmware boot with QEMU, allowing dynamic analysis of the web interface without real hardware
- **ChirpStack USB-TTL** / **Bus Pirate** / **Tigard** all work; a cheap CP2102 is enough too

## Key code/commands

One-stop firmware audit:

```bash
# 1. extract
unblob -k firmware.bin -o extracted/

# 2. run firmwalker
git clone https://github.com/craigz28/firmwalker
./firmwalker.sh extracted/squashfs-root

# 3. emulated boot (if supported)
docker run -it --rm -v $(pwd):/firmware firmae:latest \
  /work/run.sh -d 1 /firmware/firmware.bin

# 4. web up in emulation → scan directly with nuclei / nikto / curl
```

Try common UART baud rates automatically:

```bash
for baud in 9600 19200 38400 57600 115200 460800 921600; do
    echo "--- $baud ---"
    timeout 3 sudo cat /dev/ttyUSB0 < <(stty -F /dev/ttyUSB0 $baud cs8 -cstopb -parenb)
done
```

Classic U-Boot single-user bypass:

```text
# interrupt at the U-Boot stage with a key press (usually hold space or Ctrl+C)
=> setenv bootargs "console=ttyS0,115200 root=/dev/mtdblock2 rootfstype=squashfs init=/bin/sh"
=> saveenv
=> boot
# boots straight into sh, no password needed
```

## Improvement suggestions for this package

- `reverse-engineering/platforms.md` already has a firmware chapter; suggest splitting out `references/iot-firmware-cheatsheet.md`
- Add `reverse-engineering/references/uart-debug.md` covering UART/JTAG/SWD basics
- Add unblob / firmwalker to the bootstrap manifest

## Reusable patterns/script snippets

**Four stages of IoT security testing**:

```text
Stage 1: software
  · Download the vendor firmware + extract with binwalk/unblob
  · Run firmwalker
  · grep for default credentials / private keys / backdoor strings
  · Emulated boot with QEMU and run web vulnerability scans

Stage 2: hardware
  · Open the case and find UART/JTAG pads
  · Identify GND/VCC/TX/RX with a multimeter
  · Wire the USB-TTL, confirm 3.3V levels

Stage 3: debugging
  · Listen with screen/minicom
  · Interrupt at the U-Boot stage to go interactive
  · init=/bin/sh single-user mode to bypass the password

Stage 4: exploitation
  · With root → read /etc/shadow and crack offline
  · Look at the CGI binaries of the web management interface → find command injection / SSRF
  · Look at the UPnP / mDNS / Bluetooth broadcast logic
```

**Default credential quick reference** (common vendors):

```text
admin / admin
admin / password
root / root
root / 1234
support / support
ubnt / ubnt          # Ubiquiti
admin / 1234         # ZyXEL
```

## Evolution actions
- [ ] Split out iot-firmware-cheatsheet.md
- [ ] Create uart-debug.md
- [ ] Add unblob / firmwalker to the bootstrap-manifest

## Environment information
- Kali 2026.x (binwalk / unblob / squashfs-tools / firmwalker)
- USB-TTL adapter: CP2102 / FT232 (3.3V levels)
- Target: ARMv7 / MIPS router (OpenWRT-derived firmware is common)

## Redaction requirements
This entry is seed data, written from public IoT security testing methods, with no real vendor or model involved.
