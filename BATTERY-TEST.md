# RK61 five-key battery gauge — candidate v1

**Current source, built/tested offline; not yet flashed or hardware-confirmed.**
The owner-tested v5 image and all older recovery artifacts remain unchanged.
The keymap, routing, pairing policy, GPIO drive and PWM period are unchanged.

## What the display means

Physical **Esc, 1, 2, 3, 4** form a left-to-right gauge, independent of ordinary
brightness, lighting toggle and held layers. Active segments use the selected
route colour: **teal Bluetooth, orange dongle, magenta USB**. This indicates
selected routing, not proof of a wireless connection.

| Decoded radio battery code | Display |
|---|---|
| 9..15 | Five route-coloured keys |
| 7..8 | Esc through 3 coloured; 4 dim neutral white |
| 5..6 | Esc through 2 coloured; 3/4 dim neutral white |
| 3..4 | Esc/1 coloured; 2/3/4 dim neutral white |
| 0..2 | Esc blinks in route colour; 1..4 dim neutral white |
| Unknown / stale | Esc steady in route colour; 1..4 pulse together in dim white |

**These are provisional raw-code bands, not calibrated percentages.** The decoder
and below-3 low warning come from stock firmware. The other band boundaries are
an explicit initial UI policy, not a recovered stock fuel-gauge curve. Neither
code 10 nor the field maximum 15 is established as full charge. Five coloured
keys therefore mean the upper display band, not a measured 81–100% remaining.
The originally proposed percentage intervals cannot honestly be claimed yet.
Blinking follows stock's low threshold rather than pretending it is exactly 10%.

Active segments use the existing 256-count status pulse, retaining colour ratios;
empty segments use 8 counts on each RGB channel (dim white/grey). The low blink's
off phase is truly off, not the main/layer colour. An actually discharged,
powered-off keyboard cannot illuminate a gauge.

A valid zero code is a low reading, not an error. Bad frames do not produce an
empty/full indication. USB selection does not force full or imply charging;
charging/full signals have not been decoded, so there is no charging animation.

## Recovered stock evidence

The owner recalls a low-battery Fn-key blink with **original RK firmware**, not
with custom SMK. The Bluetooth host exposes no battery percentage. These reports
do not validate our new display or a charge curve.

In the saved stock application:

- RX at **0x962D..0x96F3** validates the BB header and additive checksum.
- Wire byte 2 is stored at **XRAM 0x08B0**, wire byte 3 at **0x08AF**.
  These storage addresses are deliberately out of wire order.
- At **0x96BF..0x96D2**, stock builds XRAM **0x0920** as:
  `((wire_byte_2 & 7) << 1) | (wire_byte_3 >> 7)`.
- **0x7BE8..0x7C31** compares that value with 3 and toggles XRAM **0x091C**
  between 0 and 255 when below 3 (subject to stock's USB/mode gating).
  A value below 2 also sets bit 0x22.5. We do not port stock's sleep/shutdown
  policy or modify charging control pins.
- Lighting paths at **0x0FEC** and **0x422A** consume 0x091C as an LED override.
  The owner's exact Fn pixel identification remains a recollection, not an
  independently measured per-pixel mapping.
- Stock initializes 0x0920 to 9 on a mode change. That is an initial default,
  **not** a valid sensor sample or proof of a 0..10 percentage scale.

Owner-provided valid USB-connected status samples:

```text
bb 30 25 00
bb 18 25 18
bb f8 25 38
```

All decode to **code 10**, despite changing connection fields. ACK was 0 even
for these valid replies, so ACK transition failure alone cannot reject a
checksum-valid reading. No genuinely unplugged readings, full-charge reference,
discharge curve, cell voltage or current measurements were supplied.

Do not copy NuPhy's battery decoder: treating byte 3 bit 7 as an independent
low-power flag loses the low bit of this RK61's charge code. No radio firmware,
bond erase, new pairing command, ADC register or assumed voltage divider is used.

## Implementation and timing

- `layouts/rf-test/packet.c`: portable validated stock-code decoder.
- `layouts/rf-test/battery.c`: raw bands, three-sample confirmation of ordinary
  changes, immediate first reading/low warning, stale expiry. State published
  as one atomic byte; no radio work in the LED ISR.
- `layouts/rf-test/radio.c`: read-only command 0x0A polling in all routes,
  including wired, behind pending keyboard retries. Reuses the existing bounded
  bus transaction without a wake, route reassertion or pairing command.
  Only explicit Fn+Y/mode diagnostics print; periodic polling is silent.
- `layouts/led-test/indicators.c`: row 0 / columns 0..4 use PWM23/24/25.
  Other rows in those columns keep their layer colour. Earlier diagnostic
  layouts disable all status overrides and can still go completely dark.

One atomic scan epoch advances every **32 completed 14-column LED sweeps**,
even with ordinary brightness zero. Esc toggles once per epoch; radio polling
runs every 4 epochs; after 40 epochs without a valid reply the display becomes
unknown. This targets a gentle roughly once-per-second full blink cycle, polls
every few seconds and expires after tens of seconds. **These are scan-derived
intervals, not calibrated wall-clock milliseconds.** Real cadence must be checked
on hardware. Invalid frames reset confirmation progress; recovery from low needs
three consecutive valid same-band samples, preventing boundary chatter.

## Validation

SDCC builds and interrupt/overlay checks pass for all three RK61 targets, with
ISP enabled and sleep disabled. **46 regression tests pass** across these commands:

```sh
export PATH="$PWD/venv/bin:$PWD/toolchain/usr/bin:$PWD/toolchain/bin:$PATH"
meson compile -C smk/build-rf-debug \
  royalkludge-rk61-rf-test_default_smk.hex \
  royalkludge-rk61_led-test_smk.hex royalkludge-rk61_default_smk.hex
python3 test_bluetooth.py
python3 test_keymap.py
python3 -m unittest test_leds.LedDriverChecks test_battery -v
python3 -m unittest test_prototype test_leds.LedImageChecks test_wireless -v
```

Tests execute the real decoder for all 65,536 payload combinations plus corrupt
frames, the supplied vectors, every band, filtering/low/recovery/stale/clock wrap,
real bit-banged RX/polling with missing ACK, report priority, and the real PWM
driver for all gauge states/modes/layers/brightness levels. Host tests **do not**
prove battery calibration, radio delivery, GPIO timing, pixel/colour mapping,
real blink cadence, LED current or temperature.

## Candidate and user-run smoke test

- `candidate-battery-v1.bin`: 61,440-byte application payload.
- BIN SHA-256: `7f94cb071437dc8286412d02ab5c143ed4b51d3f8908f0bfca433fa1d9b474d6`.
- Matching `candidate-battery-v1.hex` SHA-256:
  `0ebc7effe03a00f9807650a108968d9d6452d99e88083f128fc944b6a28f677a`.
- Highest linked address **0x53AC**, below 0xEC00. ISP remains enabled.
- Generated root candidates are local/ignored, not preserved tested baselines.

Only if you choose to test, run this yourself with a cable and spare keyboard:

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  ~/rk61-recovery/candidate-battery-v1.bin
```

1. Check for heat or unintended flicker immediately. All five keys may now
   run at the fixed status maximum, even with main lighting at zero.
   Power off/unplug if there is heat, instability or malfunction.
2. Confirm physical Esc/1/2/3/4 only, left-to-right. With the previously supplied
   code 10, expect five coloured keys once a valid reply arrives.
3. Check layer colours elsewhere, ordinary brightness zero/restore, and typing.
   Then check wired/dongle/an already-paired BT slot. No routine re-pairing needed.
4. Fn+Y now prints `battery_code=N` (255 means invalid reply). Normal wireless
   use can establish whether this code decreases and whether all bands are useful.
   Do not deliberately deep-discharge the cell to calibrate an unverified gauge.
5. Confirm deliberate low blink and empty/unknown patterns when encountered.
   Those paths are host-tested only; no new low-battery hardware result is claimed.

Rollback, if USB ISP remains accessible, uses the same explicit-ID command with
`known-working/layout-v5.bin`. Rollback itself remains untested. Never use the
old RK61 preset, generated flash targets or a full stock dump as the payload.
