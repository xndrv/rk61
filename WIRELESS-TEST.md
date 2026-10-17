# RK61 2.4-GHz wireless test

## Current status

Keys, Fn arrows, and LED controls have been confirmed working. LED channel order is green, red, blue; all channels together appear white. The existing working image is preserved at `known-working/keys-and-leds.bin`.

The owner flashed this RF image and confirmed both wired and dongle output work. The exact working image is preserved at `known-working/keys-leds-dongle.bin`. Bluetooth is the next separate test; see `BLUETOOTH-TEST.md`.

Receiver observed: `25a7:fa70`, manufacturer `Compx`, product `2.4G Wireless Receiver`, bcdDevice 3.91. Its cached HID descriptors include ordinary keyboard reports and NKRO split across IDs 7, 8, 9 covering usages through 0x9F, consistent with the 20-byte RF bitmap.

## Stock-derived bus and packets

Transport: separate TX and RX bit-banged transfers, MSB first, clock idles high.

| Signal | Pin | Evidence |
|---|---|---|
| Wake/MOT candidate | P0.2 | Stock TX 0x8BF6 and RX 0x962D assert low before select |
| Select | P7.5 | Same TX/RX routines |
| Clock | P4.7 | TX byte 0xAD80 and RX byte 0xAA99 |
| MCU-to-radio data | P0.4 | TX byte 0xAD80 |
| Radio-to-MCU data | P0.3 | RX byte 0xAA99 |
| ACK | P4.1 | Stock TX snapshots then waits for a toggle |

Stock output pins are released to input after transactions. RF init preserves the matrix/LED pins and changes only the above signals plus stock P5.5/P5.6 input pull-ups.

TX frame format: AA, length-minus-three, command, payload, checksum; the entire frame sums to 0x55 modulo 256. RX status is BB, checksum, payload0, payload1; checksum plus both payload bytes sums to 0x55. These match SMK's existing BK3632 protocol, but the exact radio chip marking is not known and its NuPhy-specific GPIO transport cannot be copied unchanged.

Decoded mode dispatch table 0xA264 (in `radio.asm`):
- select existing dongle link: command 1, pairing=0, mode=0.
- USB mode: command 6, payload 1,0.
- wake nudge: command 0x0C, payload 0,0 (stock 0xAFB2).
- query status: command 0x0A, payload 0,0 (stock 0xB1FF).
- keyboard reports: 32 bytes, command 2, modifiers, five legacy key slots, activity flag at byte 9, twenty bitmap bytes at 10..29.
- extra reports: command 5, consumer/system usages.

The new build does NOT rename the radio, flash it, erase bonds, factory-reset it, or request pairing. The owner's successful dongle test confirms the existing link works without resetting or re-pairing.

## Test build

Target: `royalkludge-rk61-rf-test_default_smk.hex`, under `smk/build-rf-debug/`.

Separate board entry and `layouts/rf-test/` implementation; reuses the tested LED driver. USB debug console and ISP are enabled. The main-controller image is padded to 61,440 application bytes; the bootloader is not included.

Image: `rk61-wireless-test.bin`.
SHA-256: `966af5df4c0f9127c910ebed4b809911efb46ec738ec7ad15a08b3a7cccbc3f3`.

Controls:
- Fn+R: force dongle mode using the existing 2.4-GHz pairing.
- Fn+T: force wired mode.
- Fn+Y: log radio ACK, raw status response/checksum validity and P5.5/P5.6 readings.
- Fn+Q / Fn+E: keep the tested lighting controls.

At boot, the draft automatic route follows stock's apparent USB-detect input P5.6 (high wired, low radio). This interpretation is not yet hardware-confirmed. Manual Fn+R/T overrides it until the next power cycle. P5.5's Bluetooth-selection behavior is not implemented; this build only attempts 2.4 GHz.

## First hardware test

Keep the receiver and USB cable connected. If the keyboard has a hardware power or BT/2.4 switch, turn power on and select its original dongle position.

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true ~/rk61-recovery/rk61-wireless-test.bin
```

Allow a couple of seconds for startup. In a blank text editor, press Fn+R and try typing. The keyboard-side USB reports are no longer used in this mode, so successful typing is evidence of the receiver path. Fn+T returns to wired output. Test cable removal only after the connected-cable radio test works.

If RF does not work, keep the cable connected, start the console in another terminal, press Fn+Y, and capture the diagnostic line:

```sh
sudo ~/rk61-recovery/smk/tools/smk-console/target/release/smk-console 258a:00e1
```

Do not reset/re-pair the dongle yet; distinguish missing ACK, invalid RX, wrong mode/power pins, and missing link first.

## Validation and limits

- SDCC debug build and interrupt/overlay checks passed (14 vectors).
- 12 offline tests: linked keymap/layers/ISP/image bounds, diagnostic shortcuts, actual packet encoder compiled and executed on host, stock command vectors, release/modifier/NKRO/extra packet formats, 100 deterministic bitmap cases, invalid-response detection.
- LED driver host test was separately passed previously.
- Clang probes timed out; Python workspace probes misresolved existing sibling modules. The runnable tests and SDCC build are the actual evidence.
- Basic dongle output is hardware-confirmed. Timing margins, ACK/status interpretation, battery-only startup, reconnection, and sustained reliability remain untested.
- Report retries are bounded; failed transmissions can still lose a key release. This is an experimental first test, not finished wireless support.
- No battery power management/sleep is implemented; unplug/turn off when not testing.
- Default NKRO uses all 20 bitmap bytes; legacy non-NKRO RF output has five key slots, matching the stock frame layout.
- If USB ISP remains available, use the same explicit-ID write command with `known-working/keys-and-leds.bin` to roll back. USB/physical recovery is still not guaranteed after a failed image.
