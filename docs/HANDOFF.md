# RK61 — developer handoff

> Public overview: [project README](../README.md).
> Detailed status, build provenance and recovery notes live here.

**Start here when resuming this project.** Working directory: `/home/xander/rk61-recovery/`.
Firmware checkout: `/home/xander/rk61-recovery/smk/`.

## Current source: fixed layer-key colours — unflashed

Physical **L1 / L2 / L3 / Fn** now keep **green / blue / magenta / yellow** in every
base/held layer. As requested, they follow main brightness and toggle (zero turns
them off); the battery bar is unchanged. Only row 4 / columns 2, 8, 10, 13 override
the background, using PWM00/01/02. Earlier diagnostic layouts have no overrides.
No keymap, radio/battery policy, GPIO drive, period or scheduling changes.

New local application: `candidate-layer-key-colours-v1.bin` (61,440 bytes), matching
`.hex`. BIN SHA-256:
`fa7a492563040d3bfbeb4f13930de01c3878a280ed7bf1af9c7aa1157fabcd60`.
HEX SHA-256:
`f02c2ebdab316a55a52709208c5b27e0f0865caf0e6006886add7294fb5a4f77`.
Highest linked address 0x5472, below 0xEC00. ISP enabled; sleep disabled.
SDCC builds and interrupt/overlay checks pass for all three RK61 targets; all
46 regressions pass, with expanded pixel/brightness/layer/battery checks.
Editor diagnostics are clean. This new candidate has not been flashed; hardware
appearance/mapping/current/temperature remain unvalidated. See the current
[KEYMAP checklist/command](../KEYMAP.md#current-source-fixed-layer-key-colours--unflashed).
The older battery-v1 candidate, preserved v5 and stock artifacts are unchanged.

## Battery-gauge candidate v1 — owner testing in progress

The owner reports leaving battery candidate v1 running on battery to test it;
no discharge/threshold results have been provided. Do not treat that as a
confirmed charge curve or exhaustive hardware pass.

**The battery-gauge change differs from owner-tested v5.** It adds a five-key battery bar on
physical Esc/1/2/3/4, dim white depleted segments, and blinking Esc using the stock
low-battery threshold. Battery sensing is decoded from the radio's split four-bit
value, not a new MCU ADC or NuPhy's decoder. Unknown/stale status is distinct.
Upper bands are provisional raw codes, **not calibrated percentages**. No charging
signal or battery shutdown policy is claimed. The owner recalls the original
firmware blinking Fn when low; that is not a hardware test of this candidate.

See **[BATTERY-TEST.md](../BATTERY-TEST.md)** for precise reverse-engineering evidence,
owner status vectors, timing/filtering, validation, limits and user-run flashing.
`candidate-battery-v1.bin/.hex` are new local ignored artifacts. BIN SHA-256:
`7f94cb071437dc8286412d02ab5c143ed4b51d3f8908f0bfca433fa1d9b474d6`.
Highest linked address 0x53AC; ISP enabled. All three SDCC RK61 builds and interrupt
checks pass; 46 regressions pass. The owner subsequently started testing v1;
the agent performed no flash. Tested v5 and older images are unchanged; use their
separate paths for recovery, not an experimental candidate.

## Current baseline

The owner has flashed and confirmed these features on the real keyboard:

- Wired USB typing.
- Fn layer, including WASD arrows.
- LEDs: dim white, green/red/blue channel selection, full on/off.
- Original 2.4-GHz USB dongle output.
- Bluetooth following the slot-selection/pairing test.

This is an experimental but functional custom **SMK** port. Do not interpret these confirmations as exhaustive testing of every key, LED, Bluetooth slot, operating system, battery-only startup, or reconnection scenario.

**Preserved all-mode baseline:** `known-working/baseline-all-modes.bin`, 61,440 bytes.
SHA-256: `3acda448a10008ebb9f2867fed494cef5d1bfae44689d5c42176a69164f63430`.

This is byte-identical to the owner-tested `rk61-bluetooth-test.bin`. The source/build at the original handoff matched that image; current source includes the unflashed battery candidate above, retaining the v5 keymap. Matching Intel HEX is `known-working/baseline-all-modes.hex`. A source/notes/recovery bundle is `known-working/baseline-all-modes-handoff.tar.gz`; its integrity manifest is `known-working/SHA256SUMS`.

**Do not overwrite these baseline or stock files with future experiments.** No new flash was performed during documentation/snapshotting.

## User-tested layout v3 — preserved

After flashing layout v3 and the suggested lighting/layer smoke test, the owner
reported **"okay seems to work well!"**. This is a positive general smoke-test
report, not exhaustive confirmation of every key, colour, Bluetooth slot,
battery/reconnection scenario, or electrical limits.

Preserved application: `known-working/layout-v3.bin`, matching `.hex`, source
snapshot `known-working/layout-v3-source.tar.gz`, and its own manifest
`known-working/layout-v3.SHA256SUMS`. Binary SHA-256:
`959fc33e791bbecdc194945d9d39d92d64611a653a9dc8142a04d547d5e74b32`.
Before preservation the source build was verified byte-identical to that payload.
The snapshot's notes predate this hardware report; this README is authoritative.
Do not overwrite this tested candidate or the original all-mode baseline.

## User-tested layout v4 — preserved

The owner flashed v4 and reported **"Alright it works perfectly!"** before
requesting the next brightness increase. This is a positive overall hardware
report, not a measured current/temperature rating or exhaustive slot/battery test.

Preserved: `known-working/layout-v4.bin`, matching `.hex`,
`known-working/layout-v4-source.tar.gz`, and `known-working/layout-v4.SHA256SUMS`.
Binary SHA-256:
`fd050affcc901283c5d641829887e747f031f30b56c05f54370ad800cd2cf772`.
The pre-change build was verified byte-identical to v4 before saving it. Snapshot
notes predate the hardware report; this README records the newer result.

## User-tested current layout — v5

After flashing v5, the owner reported **"alright it works!"**. This is a positive
overall smoke-test report, not a current/temperature rating or exhaustive test of
all slots, battery behavior or reconnection. V5 is now preserved as
`known-working/layout-v5.bin`, matching `.hex`, `layout-v5-source.tar.gz` and
`layout-v5.SHA256SUMS`. Its pre-preservation build matched the exact application
payload. Older baseline and layout-v1/v2/v3/v4 artifacts are unchanged.

**Git is now set up at this project root**, with `smk/` tracked as ordinary
source, alongside tests, docs and reviewed recovery artifacts. See
[VERSION_CONTROL.md](../VERSION_CONTROL.md) for commits, ignores and local-only files.
Earlier edits were not committed and cannot be reconstructed as Git history.

**The tested baseline and layout-v1/v2/v3/v4 artifacts are unchanged.** The current
source/build adapts the owner's saved `corne.vil`, with this physical bottom row:

`Left Ctrl | Left Alt | hold L1 | Space | hold L2 | Windows | hold L3 | Fn`

- **L1:** Q–P numbers, H/J/K/L arrows, Z–slash F1–F10.
- **L2:** Corne symbol positions, including Shift+key actions for `!`, braces, etc.
- **L3 (former Right Ctrl):** Q/W volume, H/J/K previous/next/play-pause,
  Y Print Screen, F/V host display brightness, Tab LED toggle, E colour cycle.
- User layers explicitly retain Backspace/Enter/Space/modifiers and layer controls;
  all other unassigned keys produce **no output**, not transparent fallback.
- Fn retains the service controls below. Priority: **Fn > L3 > L2 > L1**.
  L1+L2 does not automatically activate L3. Internal Fn index is now 4.
- **Layer lighting:** L1 green, L2 blue, L3 magenta, Fn yellow; release restores
  the remaining held layer or selected normal colour. Esc overrides that colour.
- **Fn+[ / Fn+]** cover **0..256 PWM counts in 16-count steps**, still booting
  the main lighting at 64. Zero turns off ordinary lighting; Esc stays at maximum.
  This doubles v4's ceiling; it is **not measured full capacity**. These are raw
  counts against a `0x0537` PWM period, not an 8-bit RGB 0–255 scale. Atomic byte
  levels 0..16 are converted to 16-bit duty counts inside the LED ISR.
  L3+Tab toggles zero/last nonzero brightness; Fn+] alone can leave zero.
- **Fn+.** cycles nine normal colours; L3+E remains an alias. **Fn+Q/W/E are now
  Bluetooth slots 1/2/3**, replacing Fn+Q LED toggle, Fn+W Up and Fn+E colour.
  B/N/M remain slot aliases. Up is available on L1+K.
- **Esc selected-mode display:** teal Bluetooth, orange dongle, magenta wired.
  This indicates routing selection, **not** successful link/connection status.
  Esc **always uses the new 256-count maximum**, retaining its colour ratios,
  regardless of main brightness, held layers or the main-lighting toggle. Esc is
  therefore already at the higher level when lighting starts; it cannot be dimmed
  with Fn+[. Current/temperature validation is still required.
- **Physical routing (unchanged from v4):** stock-derived P5.6 high = wired;
  otherwise P5.5 high = Bluetooth, low = dongle. Intended behavior is power-on
  follows BT/dongle, power-off + cable uses wired. V4 has the owner's positive
  overall report; individual raw-pin measurements were not supplied.
  A stable physical change takes over from an explicit Fn selection. Unchanged
  inputs never restart pairing. Last BT slot is RAM-only, defaulting to slot 1
  after a power cycle; no radio bonds are erased. Lighting is also not saved.
- Held releases keep their original action. Synthetic modifiers are independent
  of physical modifiers and shared by overlapping shifted symbols. Duplicate
  basic usages remain held until their last physical source releases.
- Mode changes/pairing request media/system releases on the old route before
  switching. Radio retry/delivery limitations remain; no general reconnection
  solution or pairing-policy change is claimed.

See **[KEYMAP.md](../KEYMAP.md)** for keyboard-shaped maps, exact assignments, editing,
and the hardware checklist. Screen brightness/screenshot behavior depends on the
host. The Corne's bootloader, encoder controls, and unsupported RGB effects were
not copied. No battery warning was added. Mixed colours are uncalibrated PWM
recipes. GPIO drive, PWM period, column scheduling and scan blanking are unchanged;
only the allowed pulse range is expanded. Current/temperature and higher-duty
scan behavior have not been measured. **Esc starts at 256 even with main lighting
at zero**. Stop and power off if it heats, flickers or causes malfunction; lowering
main brightness cannot reduce Esc. Increase the main lighting one step at a time.

Packaged application: `candidate-layout-v5.bin` (61,440 bytes), with matching
`candidate-layout-v5.hex`. Binary SHA-256:
`e33b2766494d8114e26baaa5c7521875c5e56ee48239cf0b0c644be6802d51e5`.
Highest linked address: `0x5117`, below `0xEC00`; ISP remains enabled.
SDCC builds and interrupt checks pass for all-mode and earlier RK61 targets.
All **45** regression tests pass, including real matrix/report/layer-colour policy
execution and register-mocked LED tests, plus routing truth-table/bounce checks.
LED tests include the 240→256 boundary, saturation, restoring 256 after off, and
fixed-max Esc across all main brightness levels. The owner subsequently flashed
v5 and reported it working. This does not establish measured safe brightness or
current/temperature limits; those checks remain outstanding.

Earlier `candidate-layout-v1.bin/.hex` remain preserved; v1 had empty L1/L2 and
normal Right Ctrl. Its binary SHA-256 is
`e82f953d7d2dad6c2f4ac6e6685b35909896af831b68d6f20ed25c05118cc297`.
Layout v2 (`candidate-layout-v2.bin/.hex`) retains the three populated layers
without the new lighting controls/feedback; binary SHA-256:
`256f1c9b65883b5d520516dde19240f52a81a61d967359d527cf114958eaec17`.
Baseline, v3/v4 candidate binaries and both preserved v3/v4 image/HEX/source
manifests were re-verified unchanged.

## Hardware identity and original goal

| Item | Identification |
|---|---|
| Keyboard | Royal Kludge RK61, US layout |
| Main controller marking | BYK916; working SH68F90/SH68F90A-family 8051 support |
| PCB marking | `130-81892-10 US` |
| PCB date | `2022/08/16` |
| Keyboard USB VID:PID | `258a:00e1` |
| Stock USB strings | SINO WEALTH / Bluetooth Keyboard |
| Receiver VID:PID | `25a7:fa70` |
| Receiver strings | Compx / 2.4G Wireless Receiver; bcdDevice 3.91 |
| Radio chip marking | Not identified; protocol and GPIO interface recovered from firmware |

The original goals were LED control and programmable layers. Upstream QMK does not support this controller, and the experimental qmk-8051 fork explicitly excludes BYK916. We chose SMK instead of undertaking a QMK architecture/compiler port or replacing the controller. **This is not QMK, VIA, or Vial.**

The owner could not submit PCB photos. Work proceeded using the chip/PCB markings, USB descriptors, a stock dump, disassembly, and iterative hardware tests.

## Current controls

Current layout-v5 source controls (owner reports the build working; electrical limits are not measured). **Fn+Q/W/E now
select Bluetooth slots**, rather than the older lighting/W-arrow assignments.
Hold the physical Fn key for the following:

| Chord | Action |
|---|---|
| Fn+1 through Fn+= | F1 through F12 |
| Fn+A / S / D | Left / Down / Right (Up: L1+K) |
| Fn+Esc | Grave/backtick |
| Fn+Backspace | Delete |
| Fn+Q / W / E | Bluetooth slot 1 / 2 / 3 |
| Fn+[ / Fn+] | Main brightness down / up, including zero; ceiling 256 PWM counts |
| Fn+. | Cycle nine normal/base colours; visible after releasing Fn |
| Fn+R | 2.4-GHz dongle output |
| Fn+T | Wired USB output |
| Fn+B / N / M | Bluetooth slot 1 / 2 / 3 aliases |
| Fn+P | Start pairing for the selected Bluetooth slot |
| Fn+Y | Print radio status to the USB debug console |

Fn+P does nothing in USB or dongle mode. Pairing a Bluetooth slot may replace that slot's previous association; no global factory-reset/bond-erase command is implemented. Radio names are unchanged.

L3+Tab toggles ordinary lighting between zero and its last nonzero level; L3+E
cycles the normal colour. Esc stays at maximum (256 counts) even at zero.

As in v4, automatic routing follows the stock's two-input logic, not USB-cable
presence alone. `stock.asm` 0x7C43..0x7CE8 samples P5.5 twice: stable high selects
Bluetooth, stable low selects dongle when P5.6 is low; P5.6 high selects wired.
The implementation waits for **256 consecutive main-loop samples** of a new pin
pair (not a calibrated millisecond debounce). Physical movement restores automatic
routing; unchanged pins preserve explicit Fn choices and pairing. This software
policy is tested and the owner reported v4 working perfectly overall; individual
switch/pin measurements and exhaustive reconnection tests are not recorded. Use Fn+Y
raw P55/P56 readings to diagnose a mismatch. Fn+R/T remain manual recovery choices.

## How we got here

1. Identified the keyboard over USB; normal ID is 258a:00e1.
2. Investigated sinowisp. Its RK61 preset targets **00C7**, so we used explicit IDs, never that preset.
3. The owner ran the privileged full stock read. It produced 65,536 bytes; the keyboard reconnected.
4. Verified the dump was nonblank and its 4,096-byte bootloader MD5 matched a known RK61 bootloader: `3e0ebd0c440af5236d7ff8872343f85d`.
5. Preserved the ISP-view dump and generated the tool's ICP/JTAG-view conversion. Restoration through either path remains untested.
6. Disassembled the 8051 application and recovered a 14-column, 5-row matrix, the base key-action table, and Fn location. The owner confirmed the reconstructed layout matches the physical keyboard.
7. Added a board-specific SMK definition, wired USB output, and a momentary Fn layer. The owner confirmed typing and Fn arrows.
8. Recovered LED PWM setup/blanking and shared-column multiplexing. Added a separate low-duty diagnostic layout; the owner confirmed LEDs, green/red/blue/white cycling, and off.
9. Recovered the radio bus and packet format. Implemented stock-compatible transport, report encoding, and USB/dongle routing without resetting pairing. The owner confirmed both outputs.
10. Added three Bluetooth slots and explicit slot-specific pairing commands, reusing the same radio transport. The owner confirmed Bluetooth works.
11. Preserved the all-mode binary, matching source, tests, notes, provenance and checksums.

Original stage notes retain historical context; **this README is the current status**, not an old “not yet tested” statement in a stage description.

## Reverse-engineering findings

### Keys

Matrix columns, in scan order:

`P6.0 P6.1 P6.2 P6.3 P6.4 P6.5 P6.6 P6.7 P5.0 P5.1 P5.2 P5.7 P4.0 P4.2`.

Rows: `P7.1 P7.2 P7.3 P5.3 P5.4`. Select columns low; pressed inputs read low. Fn is column 13 / row 4.

Stock scan is at 0x947C, column dispatch at 0x9493, row sampling at 0x94F3. Key records start at 0xC600, four bytes each. Stock uses six original row-bit positions per column, but bit zero is discarded. Three ISO/JIS table entries are excluded from the US 61-key map.

See [matrix-table.md](../matrix-table.md), [matrix.json](../matrix.json), and [ANALYSIS.md](../ANALYSIS.md). Avoid conflating the stock generic 21-column event buffer with the actual 14 scanned columns.

### LEDs

- Stock PWM setup at 0x6E6F; period 0x0537.
- Per-channel off points: DUTY1 = DUTY2, staggered 0x26..0x37.
- Baseline/v3 maximum was 64 counts above the off point; v4 allowed 128. V5
  allows 0..256 in steps of 16, with main lighting still booting at 64 and Esc
  fixed at 256. No full-capacity/current rating has been established.
- One shared key/LED column is selected at a time. PWM is blanked and columns deselected before key sampling.
- Source GPIOs: P1.3..5, P2.0..5, P3.0..5.
- Used row channel groups: PWM23/24/25, PWM10/11/12, PWM13/14/15, PWM03/04/05, PWM00/01/02.
- PWM20..22 correspond to the extra original row and stay off.
- Measured-by-observation color order: group 0 green, 1 red, 2 blue; all three white.
- Layout v3 adds nine palette entries and held-layer overrides. Orange/violet
  use unequal channel pulses; actual mixed-colour appearance remains unverified.
- V4 adds an Esc-only override in column 0 / ANSI row 0, stock-derived PWM23/24/25.
  It is not a general per-key API. The owner gave a positive overall v4 report;
  detailed individual-pixel measurements were not supplied.
- No animation, host RGB-control protocol, saved lighting preferences, or battery warning yet.
- Drive settings follow stock; actual LED current has not been measured.

Important correction: stock vector **0x3B is USB**, not PWM. PWM0 is vector 0x43; its handler reaches the combined scan/LED logic. See [LED-TEST.md](../LED-TEST.md).

### Radio

| Signal | Pin |
|---|---|
| Wake/MOT candidate | P0.2 |
| Select | P7.5 |
| Clock | P4.7 |
| MCU → radio | P0.4 |
| Radio → MCU | P0.3 |
| ACK | P4.1 |

Stock-derived, MSB-first, separate TX/RX bit-bang transactions; clock idles high. Outputs are released after transfers. The bus differs from NuPhy Air60 despite sharing a protocol family; **do not copy NuPhy's pins/driver unchanged**.

TX: AA, length-minus-three, command, payload, checksum; complete frame sums to 0x55 modulo 256. Status: BB, checksum, two payload bytes; checksum + payload bytes sum to 0x55.

- Command 1: payload [pairing, link]; link 0 dongle, 1..3 Bluetooth.
- Command 2: 32-byte keyboard frame; modifiers at byte 3, five legacy key slots at 4..8, activity flag at 9, 20-byte NKRO bitmap at 10..29.
- Command 5: consumer/system usages.
- Command 6 [1,0]: USB mode.
- Command 0x0A [0,0]: query status.
- Command 0x0C [0,0]: wake nudge.

Pairing sends a single explicit pairing=1 command, not a follow-up non-pairing command that could cancel advertising. No radio firmware was replaced. Original dongle pairing continued working. See [WIRELESS-TEST.md](../WIRELESS-TEST.md), [BLUETOOTH-TEST.md](../BLUETOOTH-TEST.md), and `radio.asm`.

## Source map and Git state

SMK upstream: https://github.com/karstx/smk
Baseline commit: `69373bbb633bd1159f4541f486ff7506563a38ec`.

**This project now has one root Git repository**, including the full `smk/`
source and RK61 port, tests, docs and reviewed `known-working/` artifacts. The
initial checkpoint records the current working v5 state; earlier development was
not committed. `smk/` is not a gitlink/submodule. Original upstream Git metadata
is preserved locally in `.git/smk-upstream.git`, with provenance above.

Shared ignores exclude builds, toolchains, generated candidates, secrets and raw
stock dumps/disassemblies. The original all-mode handoff archive is local-only
because it embeds stock dumps; do not mistake its checksum entry for Git tracking.
Nothing was deleted or published. See [VERSION_CONTROL.md](../VERSION_CONTROL.md).
`known-working/baseline-tracked.patch` remains supplementary, not a complete port.

Within `smk/`:

- `src/keyboards/royalkludge-rk61/kbdef.h`: dimensions/custom keycodes.
- `user_init.c`, `user_matrix.c`, `user_sleep.c`: GPIO/scanning, no sleep support.
- `layouts/default/`: first wired-only map.
- `layouts/led-test/`: LED driver and earlier LED map.
- `layouts/rf-test/layout.c`: **current all-mode keymap**, in physical key order.
- `layouts/rf-test/keymap.h`: named base/L1/L2/L3/Fn layers and 61-key ANSI-to-matrix helper.
- `lighting.h`, `layouts/rf-test/lighting.c`: palette/bounds, all-mode held-layer
  colours and fixed physical bottom-row layer-key colour policy.
- `layouts/led-test/indicators.c`: shared blanked/multiplexed PWM driver, nine-colour palette and brightness controls.
- Board `kb.c`: no-layer/no-status override hooks for earlier wired/LED diagnostic layouts.
- `layouts/rf-test/battery.c/.h`: stock battery-code bands, filtering and stale expiry;
  atomic five-key display state. See the latest candidate note above.
- `src/smk/matrix.c`: held-action caching, layer priority, combined modifier/basic actions, and shared-usage release handling.
- `src/smk/report.c`, `report.h`: independent synthetic-modifier setter used by shifted symbols.
- `layouts/rf-test/kb.c`: stock-derived switch routing/debounce, RAM BT slot, atomic Esc colour, pairing guards and old-route media/system release requests.
- `layouts/rf-test/radio.c`: hardware bus, commands, bounded retries.
- `layouts/rf-test/packet.c`: portable packet encoding/checksum validation and
  stock split-field battery-code decoder.
- Board `meson.build`: keys-only, LED, and all-mode targets.
- `src/keyboards/meson.build`: registers the new board directory.
- `src/sino51lib/flash.c`, `src/smk/usb.c`: read-only pointer const-correctness fixes required by SDCC 4.6.0; remaining differences are formatting.
- `.clangd`: editor-only local include paths/SDCC keyword modelling, not firmware compiler flags.

## Build and verify the current firmware

Local tools: SDCC 4.6.0 (#16555), Meson 1.12.1, Python 3.11.15, sinowisp 2.1.0, disasm51 1.0.2. No system-wide tool installation was performed. SDCC was extracted from an Arch package into `toolchain/usr/`; Meson/disasm51 are in `venv/`. Paths are machine-local.

```sh
cd ~/rk61-recovery
export PATH="$PWD/venv/bin:$PWD/toolchain/usr/bin:$PWD/toolchain/bin:$PATH"

# For a fresh build directory:
meson setup smk/build-rf-debug smk --buildtype=debug -Disp=enabled -Dsleep=disabled

# For an existing build directory, normally just:
meson compile -C smk/build-rf-debug royalkludge-rk61-rf-test_default_smk.hex
python3 test_bluetooth.py
python3 test_keymap.py
python3 -m unittest test_leds.LedDriverChecks test_battery -v
```

If build definitions changed, use `meson setup --reconfigure smk/build-rf-debug smk` before compiling. The current all-mode target is still named **rf-test**, including Bluetooth.

`build-prototype.sh` and `build-rk61/` are the earlier keys-only release build, **not the current all-mode target**.

The 20 current Bluetooth-suite tests cover linked layers/lighting shortcuts, bounds, ISP jump, interrupt artifact, packet vectors/checksums, 100 deterministic bitmap cases, response validation, actual routing/pairing guards and radio command sequences. `test_keymap.py` executes the real keymap, matrix, reports and layer-colour policy in both 6KRO/NKRO modes, including overlapping holds/releases. `test_leds.LedDriverChecks` executes the real LED driver/policy with mock registers across nine base colours, zero..256 levels, held-layer overrides, fixed-maximum Esc at all levels, the 240/256 boundary, palette wrap, clamp/restore bounds, scan blanking and column sweep. These tests do not prove real GPIO timing, LED current/temperature/colour appearance, OS handling, or radio delivery. SDCC/interrupt checks remain authoritative; editor checks are supplemental.

To package a future candidate as a full-sized application payload, from this directory:

```sh
python3 - <<'PY'
from pathlib import Path
from test_prototype import load_hex
image = load_hex(Path("smk/build-rf-debug/royalkludge-rk61-rf-test_default_smk.hex"))
if not image or min(image) != 0 or max(image) >= 0xEC00:
    raise ValueError("Unexpected image bounds")
payload = bytearray(61440)
for address, value in image.items():
    payload[address] = value
with Path("candidate-all-modes.bin").open("xb") as output:
    output.write(payload)
PY
```

Use a new filename per experiment. Padding is zero-filled, matching sinowisp's normal application padding; this overwrites application-side settings/marker pages during flashing.

## Flash, baseline rollback and console

**Do not use generated Meson `*_flash` targets or sinowisp's RK61 preset.** The old preset targets PID 00C7; this device is 00E1, and the new rf-test board name is not a flasher preset.

Explicit, application-only baseline restore (only if USB ISP remains accessible):

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  ~/rk61-recovery/known-working/baseline-all-modes.bin
```

A future candidate uses the same command with its reviewed application file instead. Keep a cable and another usable keyboard available. The harness blocks sudo; the owner has been running these commands in their terminal. Do not work around that restriction.

USB debug console (cable connected), then press Fn+Y:

```sh
sudo ~/rk61-recovery/smk/tools/smk-console/target/release/smk-console 258a:00e1
```

The owner has successfully flashed each development stage. A rollback to stock or an external-programmer restore has **not** been tested. Preserving the bootloader does not guarantee recovery if the application cannot enumerate or enter ISP.

## Stock backups and memory boundaries

- `stock-full-isp.bin`: original 65,536-byte USB/ISP-view dump.
- `stock-app-isp.bin`: first 61,440 bytes, application-only stock restore candidate.
- `stock-full-icp.bin`: sinowisp conversion for potential external programming; **not a tested recovery procedure**.
- `stock.asm`, `radio.asm`, `sh68f90.mcu`: disassembly/evidence.
- `prepare_disassembly.py`, `extract_matrix.py`: repeatable analysis helpers.

Stock dump SHA-256: `8378056391aacc8705c45179525863485a730a214d220e4d43fdf98606815833`.

Code budget is below 0xEC00. SMK reserves 0xEC00..0xEDFF for settings and 0xEE00..0xEFFF for its marker sector. Application flash ends at 0xEFFF; bootloader is 0xF000..0xFFFF.

**Never flash the 65,536-byte full dump through an application-only write command.** ISP-view dumps also have reset-vector remapping; they are not raw physical-flash layouts. Even sinowisp “read” can set a firmware-enable byte. Main-controller backups do not capture the separate radio's bonds.

Flasher source: https://github.com/karstx/sinowisp, built at commit `9caf1c9e4f332388dc4748f3f449d604c66ca43e`; persistent executable is in `toolchain/bin/`. Its initial source checkout was in `/tmp/rk61-investigation.FqScX0/sinowisp`; do not depend on that temporary path surviving.

## Remaining work / sensible next priorities

1. **Power saving:** sleep, wake and battery-only behavior. Currently sleep is disabled; turn the keyboard off when unused.
2. Hardware/current/temperature validation of the 256-count ceiling and
   always-maximum Esc; prior success is not an electrical rating.
3. Persistent transport/profile/lighting preferences; verify physical power/selector behavior.
4. Reconnection supervision and reliable delivery/key-release behavior. Report retries currently stop after three attempts; a failed release can leave a remote key stuck.
5. Hardware-test/calibrate the new battery gauge; recover charging indication
   and low-voltage behavior. Raw bands are not yet charge percentages.
6. Longer testing across all Bluetooth slots, hosts, modifiers, multi-key rollover, USB plug/unplug, pairing/reconnection and LED/key-scan interference.
7. Optional richer layers/lighting effects later, only as needed.

The tested baseline has a base layer plus Fn. The layout-v5 candidate has three populated Corne-inspired held user layers plus separate Fn, layer-colour feedback and an Esc mode indicator, choosing the highest-numbered held overlay; explicit transparency falls back to base. Modified basic actions support shifted symbols, but this is not the full QMK layer stack/tap-hold/toggle feature set. Brightness and radio selection are not yet saved across power cycles. This is a debug build, not a finished low-power release.

Before future changes, read this handoff, preserve the tested baseline, edit the correct all-mode target, rebuild/run tests, package a distinct candidate, and hardware-test one change at a time.
