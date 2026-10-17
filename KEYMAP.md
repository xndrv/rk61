# RK61 layer maps — layout v5

**Owner-tested v5: reported "alright it works!" after flashing.** This general
smoke-test result is not an electrical rating or exhaustive validation. These maps adapt
`corne.vil` by keeping its bindings on the same letter/punctuation keys. The
preserved all-mode baseline and layout-v1/v2/v3/v4 candidates are unchanged.
The owner reported v3 "seems to work well" and v4 "works perfectly" after flashing.
Their images, HEX files, source snapshots and manifests are preserved under
`known-working/layout-v3*`, `known-working/layout-v4*`, and now `known-working/layout-v5*`. These positive overall
reports do not establish measured current/temperature ratings or exhaustive testing.
See the [developer handoff](docs/HANDOFF.md) for recovery and flashing precautions.

## Layer keys

The bottom row, by physical position, is now:

```text
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

| Original position | New function |
|---|---|
| Left Ctrl | Left Ctrl |
| Windows | Left Alt |
| Left Alt | Hold Layer 1: numbers/navigation |
| Space | Space |
| Right Alt | Hold Layer 2: symbols |
| Menu / down-arrow legend | Windows (Left GUI) |
| Right Ctrl / right-arrow legend | Hold Layer 3: media/utilities |
| Fn | Hold the separate service layer |

Hold to activate, release to leave. Priority is **Fn > L3 > L2 > L1**.
Holding L1+L2 selects L2, **not** L3; L3 has its own dedicated key.
Releasing a higher layer restores any lower layer still held.

`--` means **disabled**, not transparent. User layers explicitly keep Backspace,
Enter, Space, both Shifts, Left Ctrl, Left Alt, Windows, and all four layer keys.
Tab remains Tab on L1/L2 but toggles lighting on L3. There is no Right Ctrl or
Right Alt modifier on the current base map.

## Base — normal typing

All non-bottom-row keys keep their existing US assignments.

```text
[Esc ][ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ][ 9 ][ 0 ][ - ][ = ][Backspace]
[ Tab ][ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ][ [ ][ ] ][    \    ]
[ Caps ][ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ][ ; ][ ' ][   Enter    ]
[ Shift  ][ Z ][ X ][ C ][ V ][ B ][ N ][ M ][ , ][ . ][ / ][ Right Shift  ]
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

## Layer 1 — numbers/navigation

```text
[ -- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][Backspace]
[ Tab ][ 1 ][ 2 ][ 3 ][ 4 ][ 5 ][ 6 ][ 7 ][ 8 ][ 9 ][ 0 ][-- ][-- ][    --   ]
[  --  ][-- ][-- ][-- ][-- ][-- ][Left][Down][Up][Right][-- ][-- ][   Enter    ]
[ Shift  ][F1 ][F2 ][F3 ][F4 ][F5 ][F6 ][F7 ][F8 ][F9 ][F10][ Right Shift   ]
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

- Q through P send 1 through 0.
- H/J/K/L send Left/Down/Up/Right.
- Z/X/C/V/B/N/M/comma/dot/slash send F1 through F10.
- Modifiers remain available for Ctrl+arrow and Shift+arrow selection.
- F11/F12 remain on Fn+- / Fn+=; Right Shift is not repurposed as F11.

## Layer 2 — symbols

Characters shown assume a **US host keyboard layout**; firmware sends HID keys
with Shift where needed, rather than literal text.

```text
[ -- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][Backspace]
[ Tab ][ ! ][ @ ][ # ][ $ ][ % ][ ^ ][ & ][ * ][ ( ][ ) ][-- ][-- ][    --   ]
[  --  ][-- ][-- ][-- ][-- ][-- ][ - ][ = ][ [ ][ ] ][ \ ][ ` ][   Enter    ]
[ Shift  ][-- ][-- ][-- ][-- ][-- ][ _ ][ + ][ { ][ } ][ | ][ Right Shift  ]
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

This follows your Corne's Q–P, H–quote, and N–slash positions. Right Shift stays
Shift; **Fn+Shift+Esc** provides tilde (`~`). Shifted symbols retain their own
synthetic Shift until released, without removing a separately held physical
Shift or the Shift needed by another held symbol.

## Layer 3 — media/utilities

```text
[ -- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][-- ][Backspace]
[ LED ][Vol-][Vol+][Colour][-- ][-- ][PrtSc][-- ][-- ][-- ][-- ][-- ][-- ][ -- ]
[  --  ][-- ][-- ][-- ][Bright+][-- ][Prev][Next][Play][-- ][-- ][-- ][ Enter ]
[ Shift  ][-- ][-- ][-- ][Bright-][-- ][-- ][-- ][-- ][-- ][-- ][Right Shift]
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

| Chord | Action |
|---|---|
| L3+Q / W | Volume down / up |
| L3+H / J / K | Previous track / next track / play-pause |
| L3+Y | Print Screen |
| L3+F / V | **Display** brightness up / down, where supported by the host |
| L3+Tab | Existing keyboard LEDs on/off |
| L3+E | Cycle the nine-colour normal/base palette (visible after releasing L3) |

Media, screenshot, and display-brightness positions match `corne.vil`. Print
Screen sends the ordinary keyboard usage; the OS decides how screenshots work.
Display brightness does not change keyboard LED brightness.

The Corne's RGB toggle is adapted to L3+Tab. Its hue/saturation/effect controls
are not copied; L3+E cycles the normal palette instead. Keyboard brightness now
has dedicated Fn+[ / Fn+] controls, separate from L3+F/V display brightness. The Corne's bootloader and encoder controls are
not copied. No new animation effects are introduced. V4 raises the permitted
PWM pulse ceiling experimentally, without changing GPIO drive settings.

## Fn — service shortcuts and Bluetooth slots

`.` means **explicitly use the base assignment**, unlike `--`.

```text
[Grave][F1 ][F2 ][F3 ][F4 ][F5 ][F6 ][F7 ][F8 ][F9 ][F10][F11][F12][ Delete ]
[  .  ][BT1][BT2][BT3][2.4][USB][Info][ . ][ . ][ . ][Pair][LED-][LED+][ . ]
[   .  ][Left][Down][Right][ . ][ . ][ . ][ . ][ . ][ . ][ . ][ . ][ Enter ]
[ Shift  ][ . ][ . ][ . ][ . ][BT1][BT2][BT3][ . ][Colour][ . ][Right Shift]
[Ctrl][Alt][ L1 ][                Space                 ][ L2 ][Win][ L3 ][Fn]
```

- 2.4 = original dongle; USB = wired output; Info = radio status on USB console.
- **Fn+Q/W/E** select Bluetooth slots **1/2/3**. B/N/M remain aliases.
- These replace the old Fn+Q LED toggle, Fn+W Up arrow, and Fn+E colour alias.
  Use **L1+K** for Up, **Fn+.** for colour, and dim to zero or L3+Tab for off.
- Pair = explicit pairing for the selected Bluetooth slot, ignored in USB/dongle mode.
- Fn's internal index is now **4**, keeping the actual user Layer 3 separate.
- Media/system releases are requested on the old route before changing transport
  or starting pairing. This is not a general reconnection/delivery guarantee;
  bounded radio retries and lost wireless releases remain a known limitation.
- Esc now indicates the selected route; no battery warning is added.

## Layer colours, brightness and Esc display

| State | Main keyboard colour, excluding Esc |
|---|---|
| Base | Selected normal colour; white at boot |
| Hold L1 | Green |
| Hold L2 | Blue |
| Hold L3 | Magenta |
| Hold Fn | Yellow |
| Brightness zero | Main lighting off, regardless of held layers |

Lighting follows **Fn > L3 > L2 > L1**. Release a layer to restore the remaining
held layer, or the selected base colour. Esc's connection colour overrides the
layer colour on **Esc only**.

| Esc colour | Selected output mode |
|---|---|
| Teal | Bluetooth, any of the three slots |
| Orange | Original 2.4-GHz dongle |
| Magenta | Wired USB |

This shows the **selected route, not confirmation of a connected host**.
**Esc always uses the 256-count maximum**, even when main brightness is zero,
when main lighting boots at 64, or while holding any layer. Colour ratios are
preserved: teal is green/half-blue; orange is red/quarter-green. The main
brightness buttons and L3+Tab cannot dim or turn off Esc. This higher Esc duty
requires fresh hardware/temperature checks; it starts as soon as lighting starts.

| Chord | Keyboard lighting control |
|---|---|
| Fn+[ | Dim one step, down to zero |
| Fn+] | Brighten one step, including from zero |
| Fn+. or L3+E | Cycle the normal/base colour |
| L3+Tab | Shortcut: zero / restore the last nonzero brightness |

Cycle: **white → green → red → blue → yellow → cyan → magenta → orange →
violet → white**. Teal is reserved for the mode indicator, not the base cycle.
Fn/L3 keep their layer colours while held; release to see the new base colour.

Main brightness covers **0..256 PWM counts in steps of 16** (17 levels), doubling
v4's 128-count ceiling. Main lighting boots at **64**, not at the new maximum;
Esc starts at its fixed maximum of 256. From 64, twelve Fn+] taps reach 256. Zero is the actual off state for main lighting; there is no
independent on/off flag to prevent the brightness-up key from restoring it.
Settings and last-nonzero brightness are RAM-only and reset on a full power cycle.

**256 is an experimental ceiling, not measured full capacity.** These are raw
counts against the `0x0537` (1335-count) PWM period, not 8-bit RGB values, so 255
is not a hardware ceiling. Doubling pulse width does not necessarily double
perceived brightness. GPIO drive, PWM period, scheduling and blanking are unchanged.

Brightness state is stored as atomic byte-sized levels 0..16 on the 8-bit MCU;
the driver converts to **16-bit** PWM pulses. Tests explicitly cover 240→256,
clamping and restoring 256 without wraparound. No electrical/current/temperature
certification is claimed. Check Esc immediately: it is already at 256 and cannot
be reduced by main-lighting controls. Raise main lighting one step at a time.
If there is heat, flicker or malfunction, unplug and power off; do not leave the
new higher duty running unattended. A visually dim result alone is not proof
that further increases are electrically safe.

The row/column targeting is stock-derived: Esc is column 0 / ANSI row 0, loaded
through PWM23/24/25. The implementation changes only that pixel and keeps the
other rows of column 0 at the normal layer colour. V4 received the owner's
positive overall report, but detailed per-pixel measurements were not recorded.

Implementation: shared `lighting.h` defines palette and bounds;
`layouts/rf-test/lighting.c` supplies layer colours; `layouts/rf-test/kb.c` publishes
an atomic selected-mode colour. The shared `layouts/led-test/indicators.c` handles
PWM, Esc targeting and brightness controls. Earlier diagnostic layouts have no
Esc/layer override and can still go completely dark. Battery indication is not added.

## Physical power and BT/dongle switches — hardware trial

Intended normal behavior matches the owner's description:

- **Power on:** follow the BT/dongle selector, even with a USB cable connected.
- **Power off + USB connected:** use wired output.
- No pairing is started merely by moving a switch or choosing a slot.

Stock `0x7C43..0x7CE8` samples P5.5 twice and checks P5.6. V5 keeps v4's
stock-derived truth table unchanged. The owner reports v4 working perfectly
overall; individual raw-pin measurements were not supplied:

| P5.6 | P5.5 | Automatic output |
|---|---|---|
| High | Either | Wired USB |
| Low | Low | Dongle |
| Low | High | Last selected Bluetooth slot; slot 1 after full power-up |

A new pin pair must appear in **256 consecutive main-loop samples** before a
change is accepted. This is a sample-count filter, not a measured millisecond
interval. A stable physical change cancels an explicit Fn output choice.
Unchanged pins preserve manual choices and do not restart pairing/advertising.

Fn+Q/W/E select a slot and immediately select Bluetooth. Fn+R/T force dongle/wired,
including as recovery choices if the physical interpretation is wrong. The last
BT slot is remembered only in RAM while the MCU remains powered; the radio's
stored associations are not erased. Fn+P is still the only explicit pairing action.

If the hardware does not match, keep the cable and another keyboard available,
use Fn+T for wired, and capture Fn+Y console lines for power on/off and both
BT/dongle positions. The raw `P55` / `P56` fields identify the actual input states.
Do not factory-reset/re-pair as a routine response to a selector problem.

## Editing a binding

Edit **`smk/src/keyboards/royalkludge-rk61/layouts/rf-test/layout.c`**.
Each `RK61_LAYOUT_ANSI(...)` block follows physical rows, left to right:
**14 / 14 / 13 / 12 / 8** keys. The helper hides the electrical holes.

| Entry | Meaning |
|---|---|
| `OFF` | Disabled key (`KC_NO`); default for unassigned user-layer keys |
| `KC_A`, `KC_LEFT`, etc. | Ordinary key or modifier |
| `LSFT(KC_1)` | Shift+1, producing `!` with a US host layout |
| `PASS` | Explicitly reuse the base assignment; not the user-layer default |
| `L1`, `L2`, `L3`, `FN` | Hold the corresponding layer |

Keep the four layer-control positions as shown: the action handler always
recognizes base-layer hold keys. A key already held during a layer change keeps
its original action until release. An `OFF` key pressed under a layer stays
silent even if the layer is released first; entering a layer does not cancel
already-held keys.

These are compile-time maps: edit, build/test, then flash a distinct candidate.
There is no live remapping app or support for Corne/QMK tap-hold/macros/combos.

## Validation and candidate

```sh
cd ~/rk61-recovery
export PATH="$PWD/venv/bin:$PWD/toolchain/usr/bin:$PWD/toolchain/bin:$PATH"
meson compile -C smk/build-rf-debug royalkludge-rk61-rf-test_default_smk.hex
python3 test_bluetooth.py
python3 test_keymap.py
python3 -m unittest test_leds.LedDriverChecks -v
```

Layout v5 passed the SDCC build and interrupt checker, 20 Bluetooth-suite checks,
and the host harness executing the real keymap, matrix handler, report encoder
and layer-colour policy in **both 6KRO and NKRO modes**. Tests cover disabled keys, layer priority,
shifted-symbol overlap, independently held modifiers, duplicate usages across
layers, media usage values/releases, Print Screen, and preserved Fn behavior.
The LED register-mock harness checks all nine base colours at zero..256 levels,
held-layer overrides, Esc-only teal/orange/magenta fixed at maximum (including
main zero and boot), unchanged other rows/columns, palette wrap, clamping/restore,
the 240/256 boundary, duty values below the PWM period, blanking and column sweep. Routing tests cover the stock-derived boot truth table, slot
memory, consecutive-sample debounce, switch/manual precedence, pairing guards
and selected-mode colour. These are not simulated physical switch measurements.
The broader regression run passed **45 tests**, including rebuilt earlier RK61
prototype and LED targets.

These checks do **not** prove GPIO timing, actual LED current/temperature/colour
appearance, real USB/radio delivery, OS support, or over-air Bluetooth behavior. Hardware validation remains outstanding.

**Tested candidate:** `candidate-layout-v5.bin`, 61,440 bytes, also preserved as
`known-working/layout-v5.bin`; matching
`candidate-layout-v5.hex`. Binary SHA-256:
`e33b2766494d8114e26baaa5c7521875c5e56ee48239cf0b0c644be6802d51e5`.
Highest linked address: `0x5117`, below the `0xEC00` settings boundary. ISP stays
enabled. Baseline, v3/v4 candidate binaries and both preserved v3/v4 image/HEX/source
manifests were verified unchanged. Never overwrite them with a new experiment.

To test, keep another usable keyboard and a USB cable available. Run this
**yourself in your terminal**, not through the agent:

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  ~/rk61-recovery/candidate-layout-v5.bin
```

Do not use generated flash targets, a preset, or a full stock dump. The README
has the explicit preserved-baseline restore command if USB ISP remains accessible.
No flash was performed by the agent.

To return to the user-tested v4 image, if USB ISP remains accessible, use
the same explicit-ID command with `~/rk61-recovery/known-working/layout-v4.bin`.
Actual rollback itself has not been tested; keep a spare keyboard available.

## V5 hardware checklist — overall success reported, detailed results not recorded

1. Confirm the bottom row, especially Right Ctrl now holding L3 rather than Ctrl.
2. Test L1 numbers/F-keys/HJKL arrows, including Ctrl+Shift+arrow selection.
3. Test L2 symbols, two symbols held together, and a separately held Shift.
   Release the layer before the symbol too; check for stuck keys/modifiers.
4. Test an unmapped key (e.g. L1+A) produces nothing, even when releasing L1 first.
5. Test all media keys, L3+Y, and display brightness on your OS. Brightness or
   screenshot behavior may differ by host; record observed results, not assumptions.
6. Test L3+Tab/E and all existing Fn controls. Check USB, the original dongle,
   and an already-paired Bluetooth host, especially media press/release on each.
   Layout testing alone should not require re-pairing.
7. Test overlapping layer holds restore both the correct bindings and colour:
   L1 green, L2 blue, L3 magenta, Fn yellow, then normal colour on release.
8. **Esc is already at the new maximum as soon as lighting starts.** Confirm its
   mode colour and watch for heat/flicker immediately. Dim main lighting four
   steps from 64 to zero: only Esc should remain, at unchanged full brightness.
   Fn+] restores main lighting; L3+Tab must not affect Esc.
9. Test Fn+Q/W/E slots and the physical power/BT/dongle switches, first with USB
   connected and then on battery if basic tests pass. Power-off+cable should be
   magenta/wired; power-on+BT teal; power-on+dongle orange. If not, capture Fn+Y
   P55/P56 readings for each position and report which output actually types.
10. Cycle colours with Fn+. and L3+E (Fn+E is now BT3). Test L3+Tab as zero/restore.
    Raise main brightness from **64 through 128 up to 256** in 16-count steps,
    checking typing, stability and temperature at each step. The last step is
    **240→256**, not a wrap to zero. Stop on flicker, heat or malfunction;
    do not leave an unverified higher setting running unattended.
11. Release media keys before switching hosts for normal use; separately verify
    mode-switch releases with another keyboard available to stop a stuck command.
