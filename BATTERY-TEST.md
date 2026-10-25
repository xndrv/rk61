# RK61 five-key battery gauge

## Power-state candidate v3 — owner reports working

V3 changes only the unavailable display: **Esc stays steady in its route colour;
keys 1–4 use normal keyboard lighting**, following the current base/held-layer
colour, ordinary brightness and lighting toggle. They no longer appear as battery
segments while physical power is OFF. Battery sensing/low-warning policy is the
same as v2 below. Available battery readings and unknown/stale patterns are
unchanged. V2's separate artifacts are preserved.

`candidate-battery-power-v3.bin/.hex`: 61,440-byte application BIN; highest linked
address 0x58F1, below 0xEC00. ISP enabled, sleep disabled.
BIN SHA-256: `ce721b9e734f562f1a307b14b1c39b25ae13e54d7396f7644facd089e1cf8e30`.
HEX SHA-256: `7995cf3b47821c0552ed8e1ace29fea2e9d1a26493898d963fef25668ceba1ae`.
All three SDCC target builds and interrupt checks pass; all 48 regressions pass.
The LED test checks unavailable keys against normal background pixels across
modes, brightness zero..256, held layers and both blink phases. The owner
subsequently reports **"Alright that works"** for the requested behavior. This is
a positive smoke-test report, not exhaustive calibration, electrical/pin or
all-mode validation. Pin interpretation/calibration limits from v2 still apply.

User-run flash command for v3:

```sh
sudo /home/xander/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  /home/xander/rk61-recovery/candidate-battery-power-v3.bin
```

With USB connected and power OFF, check keys 1–4 match the other ordinary keys
when changing base colour, holding each layer, dimming and toggling lighting.
Esc should keep its steady route colour even at zero ordinary brightness. With
power ON (including Fn+T wired output), the battery gauge should return after a
valid poll. The owner subsequently reported the requested behavior working.

## Power-state candidate v2 — unflashed

The owner reports a false Esc-only low-battery blink with the physical power
switch OFF and USB connected, while power ON restores correct-looking battery
readings even with the cable attached. This is a hardware symptom report, not
calibration or proof of the battery's electrical bypass arrangement.

The latest source uses the **existing debounced P5.6 power-off/wired input** to
mark battery sensing unavailable while it is high. It does not infer battery
availability from the selected output or USB enumeration. Thus power ON with
Fn+T selecting USB still accepts battery readings. The GPIO mapping remains the
port's existing stock-derived interpretation; confirm OFF/ON behavior on hardware.
There is no change to routing policy, radio firmware, pairing, GPIO drive,
charging controls, sleep, PWM levels, startup allowance or the decoder.

When unavailable, **Esc stays steadily route-coloured and keys 1–4 stay dark**.
Even checksum-valid low codes are ignored in this state; expiry cannot turn it
into an unknown/blinking display. Switching ON clears the old measurement and
partial filter history, then accepts the first fresh valid sample. Unknown/stale
and genuine low behavior remain unchanged when sensing is available. No battery
value is invented while sensing is unavailable. Fn+Y retains the raw battery
code and now adds `battery_display=40` for unavailable (`00` unknown, `81` low,
`02..05` ordinary bands).

New local application: `candidate-battery-power-v2.bin`, 61,440 bytes, matching
`candidate-battery-power-v2.hex`; highest linked address **0x590F**, below 0xEC00.
BIN SHA-256: `2159354b5339386e3e40038d36ab8c084ebfc724e979a8a6cedfc85ab622c932`.
HEX SHA-256: `6acf09cc8ae914ef505b31850ead381dc37e7f85a35ad6bf517827670a4d9e49`.
This includes responsive startup and fixed layer-key colours. Prior candidates
and the owner-tested v5 artifacts are preserved; v5 checksums still pass.

All three RK61 SDCC builds and interrupt/overlay checks pass, with ISP enabled
and sleep disabled. All **48** existing regression tests pass, with expanded
checks for ignoring every raw battery code while unavailable, expiry/wrap,
fresh-sample recovery, genuine low warnings, debounced physical input changes,
manual wired output while powered, and unavailable pixels across every main
brightness/mode/layer and both blink phases. Host checks do not establish the
physical pin's voltage/polarity, raw OFF/ON radio behavior or an accurate charge
curve. This candidate has not been flashed or hardware-tested by the agent.

User-run flash command for this candidate:

```sh
sudo /home/xander/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  /home/xander/rk61-recovery/candidate-battery-power-v2.bin
```

Check with USB attached:

1. Power OFF: steady Esc, keys 1–4 dark, no false low blink even after waiting
   beyond the stale timeout. Fn+Y should show `battery_display=40`.
2. Power ON: the bar returns after a valid poll. Press Fn+T to select wired
   output and verify the bar continues updating. Fn+Y should show the raw code
   and a corresponding available display state. Check both BT/dongle selector
   positions without starting pairing.
3. Toggle OFF/ON again: old readings must not reappear before a new valid poll.
   Confirm typing, layer colours and startup behavior still work. An unknown
   display can briefly pulse keys 1–4 while awaiting a fresh powered reading.

Raw Fn+Y lines in both power states would still help confirm pin interpretation
and distinguish radio-returned low codes from stale data in the older firmware.
Do not deliberately discharge the cell to trigger a low warning. Rollback uses
`known-working/layout-v5.bin` with the handoff's explicit-ID procedure.

The original battery-v1 build remains below as historical build/test evidence.
Owner testing on battery was in progress without recorded discharge results.

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
| Unknown / stale while powered | Esc steady in route colour; 1..4 pulse together in dim white |
| Power OFF / unavailable (v3) | Esc steady in route colour; 1..4 follow ordinary base/layer lighting |

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

With sensing available, a valid zero code is a low reading, not an error. Bad frames do not produce an
empty/full indication. USB selection does not force full or imply charging;
charging/full signals have not been decoded, so there is no charging animation.

## Recovered stock evidence

### Wired false-low report — investigation open

The owner reports **Esc alone blinking with USB plugged in**, despite the battery
not being low. This identifies the low-state display path; missing/stale status
instead keeps Esc steady and pulses keys 1–4. It does not establish that the
battery is electrically bypassed or that its voltage is unavailable.

The owner subsequently confirms that **with the power switch ON, the battery
display reads correctly even while USB is connected**. This narrows the symptom
to the physical power state rather than USB connection alone. No raw OFF/ON
status frames or calibrated charge reference have been supplied yet.

Current `rk61_radio_battery_task()` runs in wired mode as well as wireless. A
checksum-valid code 0..2 immediately enables the low warning, regardless of
external power. A previous low reading can also remain displayed until valid
recovery samples arrive or the stale timeout expires. The earlier USB-connected
code-10 replies below show that plugging in USB does not universally prevent
reading this radio field; they do not prove fresh cell measurements in every
power-switch configuration.

Additional stock evidence at **0x7B86..0x7C31**: P4.4 high bypasses the battery-low
blink branch and writes the neutral LED override 0xAA; only P4.4 low reaches the
code-below-3 blink test, which is also gated by bit 0x20.4. The P4.4-high branch
also samples P7.7. Neither pin's electrical meaning/polarity has been measured
on this board. P4.4 is separate from the P5.6 route-selection input, so selecting
wired output alone is not proof of that stock power condition. No new GPIO
drive or guessed charging/battery-control operation has been introduced.

Next evidence needed: several Fn+Y lines while USB remains connected, first
with power OFF, then ON with Fn+T selecting wired output. Compare raw frames,
`valid`, `battery_code`, and P55/P56. This distinguishes valid low replies from
invalid replies leaving an earlier low state visible, and tests whether physical
power changes the returned battery code independently of selected output.
The power-state guard in v2 above addresses the display policy using the existing
P5.6 input; it does not claim to reproduce the unmeasured P4.4/P7.7 circuitry.

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
  In v1 other rows in those columns keep their layer colour. Newer source adds
  the fixed bottom-row layer-key colours (including L1 beneath battery key 2).
  Earlier diagnostic
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

For the original v1 build, SDCC builds and interrupt/overlay checks passed for
all three RK61 targets with ISP enabled and sleep disabled; **46 regression
tests passed** across these commands:

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
