# RK61 Bluetooth test

## Status and rollback

Owner confirmed USB/dongle output with the preceding build, then flashed this image and confirmed Bluetooth works as well. This is now the functional all-mode baseline; see `README.md`. This does not establish exhaustive testing of every slot/host/reconnection scenario.

Preserved preceding dongle image: `known-working/keys-leds-dongle.bin` (SHA-256 `966af5df4c0f9127c910ebed4b809911efb46ec738ec7ad15a08b3a7cccbc3f3`), with the board source archived alongside it.

Owner-tested application image: `rk61-bluetooth-test.bin`, 61,440 bytes. An identical preserved baseline is `known-working/baseline-all-modes.bin`.
SHA-256: `3acda448a10008ebb9f2867fed494cef5d1bfae44689d5c42176a69164f63430`.

## Controls

- Fn+B: Bluetooth slot 1.
- Fn+N: Bluetooth slot 2.
- Fn+M: Bluetooth slot 3.
- Fn+P: initiate pairing for the currently selected Bluetooth slot.
- Fn+R: return to the existing 2.4-GHz dongle pairing.
- Fn+T: wired USB.
- Fn+Y: log radio status to the USB debug console.
- Fn+Q and Fn+E: unchanged LED controls.
- Existing Fn arrows/F-row remain unchanged.

Mode overrides last until power cycle. As before, automatic boot routing follows the apparent USB-detect input and otherwise defaults to dongle mode; selecting a Bluetooth profile is manual in this test. Physical BT/2.4 switch auto-selection, persistent profile preference, sleep, battery power management and reconnection supervision are not implemented.

## Implementation

Stock's command-1 dispatch at 0xA249/0xA264 uses payload [pairing, link], where link 0 is dongle and 1..3 are Bluetooth slots. Ordinary selection sends pairing=0, matching the previously working dongle sequence. Pairing sends one explicit pairing=1 command for the selected Bluetooth slot; it does not follow up with a non-pairing command that could cancel advertising.

The routing code releases the previous destination before switching, remembers the selected wireless link, and refuses pairing requests outside Bluetooth mode. The transport and keyboard/LED machinery are otherwise reused from the working build. No name-changing, radio-firmware writing, factory reset, or global bond-erase command is added.

Re-pairing a Bluetooth slot may replace its old association. The internal radio's bond handling is not under the main-controller firmware's direct control; do not assume a new pairing leaves that slot's old host connected.

## First test

Keep the USB cable connected for testing and recovery. Set any hardware power switch on. Start with slot 1; if it already has a working bond, Fn+B alone may reconnect it. Otherwise:

1. Open Bluetooth settings on the device you want to pair.
2. Press Fn+B, then Fn+P.
3. Look for the keyboard's existing RK61 Bluetooth name. This build does not rename it.
4. Complete OS pairing; enter any requested PIN on the RK61 and press Enter if prompted.
5. Test typing in a blank text editor. Fn+T returns to USB, Fn+R returns to the dongle.

Flash:

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true ~/rk61-recovery/rk61-bluetooth-test.bin
```

If it does not advertise, pair, or type, collect a status line by running the console below and pressing Fn+Y while the cable remains connected:

```sh
sudo ~/rk61-recovery/smk/tools/smk-console/target/release/smk-console 258a:00e1
```

Do not use a global factory reset as a troubleshooting step. If USB ISP remains available, the same explicit-ID write command with `known-working/keys-leds-dongle.bin` restores the preceding tested image. Recovery after loss of USB/ISP access remains unverified.

## Checks

- SDCC build and interrupt/overlay checks passed.
- 16 offline tests passed (`python3 ~/rk61-recovery/test_bluetooth.py`).
- Inherited image/packet tests verify the base layout, original controls, ISP jump, application bounds, checksums, modifiers, legacy/NKRO/extra reports and status validation.
- New tests verify Bluetooth key locations and all six stock select/pair vectors.
- Host harnesses execute the actual C routing and radio-selection code. They check old-destination release, all slots, press/release handling, manual override, USB/dongle pairing guards, and observed TX byte sequences (including invalid-link rejection before any transmission).
- Fresh SDCC build is authoritative for the 8051. An editor-only .clangd now supplies the missing include paths and models SDCC keywords for syntax analysis; it does not affect the firmware build. Latest active checks confirmed the four changed C/header paths clean; the Python probe timed out, while the runnable tests passed.
- These checks do not simulate the Bluetooth stack, physical radio timing, operating-system pairing, security/PIN exchange, or over-air behavior.
