# RK61 responsive startup candidate v1

## Behavior and limits

The current all-mode source removes two blocking waits from startup:

- `rk61_radio_init()` configures the bus and records a deadline instead of
  waiting in `delay_ms()`. Lighting, layer controls and key processing can run
  during radio boot. USB typing can start as soon as the host configures USB.
- Only `royalkludge-rk61-rf-test` sets `USB_START_WITHOUT_ENUM_WAIT`; it skips the
  shared 500-ms no-host / up-to-4000-ms USB startup wait. Other targets retain it.
- A main-loop state machine preserves the radio boot allowance (1500 nominal
  timer ms), wake command, 20-ms gap, select command, and second 20-ms gap/repeat
  for non-pairing selection. Pairing sends exactly one pairing command. USB mode
  is also notified to the radio after its boot allowance, without delaying USB.
- The new SH68F90 clock counts programmed Timer2 intervals, excludes uncounted
  dispatch/ISR time, and works without USB or visible lighting. Deadlines use
  unsigned 16-bit subtraction across wrap. Actual allowances can be longer than
  the nominal values. No radio readiness bit or faster radio boot is claimed.
- No status poll, diagnostic query, report or release accesses the radio before
  its allowance expires. New selection requests replace staged old selections.
  Radio transactions themselves retain their existing bounded microsecond waits.
- Latest keyboard state is retained during startup, including releases. USB
  also retains separate consumer/system states until enumeration, and waits for
  endpoint availability to flush them. Radio reports wait until selection
  completes. Taps completed before readiness are coalesced away, not replayed.
- Mode colour still means selected route, not connection readiness. Bluetooth
  host reconnection and receiver availability remain outside this MCU's control.

This candidate includes the existing battery bar and fixed layer-key colours.
It preserves ISP and disabled sleep. No flash, power-on measurement or over-air
validation was performed by the agent. Early USB operation while enumeration
finishes, all wireless routes and electrical behavior still need hardware tests.
The tested v5 image and prior candidates remain at their separate paths.

## Validation

All three RK61 SDCC targets build with interrupt/overlay checks passing; all
48 regression checks pass across the six project suites. The
host suites cover linked image/keymap/ISP checks, real routing and pairing guards,
real radio wire sequences, no busy millisecond waits, silent radio boot, command
spacing, clock wrap, selection replacement, startup report coalescing, endpoint
backpressure, and cancellation on route changes. A register-mocked test executes
actual SH68F90 timer ISR accounting through wrap; linked startup assembly checks
that the all-mode main function skips USB waiting. Host checks do not establish
GPIO timing or successful wireless delivery.

Commands from the root, with the handoff's local tools on PATH:

```sh
meson compile -C smk/build-rf-debug royalkludge-rk61-rf-test_default_smk.hex \
  royalkludge-rk61_default_smk.hex royalkludge-rk61_led-test_smk.hex
python3 test_bluetooth.py
python3 -m unittest test_prototype test_leds test_wireless test_keymap test_battery -v
```

## Candidate and user-run hardware test

`candidate-startup-v1.bin` is a zero-padded 61,440-byte application; highest
linked address is 0x5862, below 0xEC00. Its matching HEX is
`candidate-startup-v1.hex`. These generated candidates are local and ignored.

- BIN SHA-256: `c7565c4ceb383a60c4a4f6d9434a8ebf5541268d70e940bcf866139e2d2f628b`
- HEX SHA-256: `1525cb397ae02d0c54a3a11516aa51e702647aeb82910481fa20880a3f7d8bde`

Flash only from the owner's terminal, using this board's explicit USB ID:

```sh
sudo /home/xander/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true \
  /home/xander/rk61-recovery/candidate-startup-v1.bin
```

1. Compare power-on to first lighting and first successful typing, separately,
   on wired USB, battery/dongle and an already bonded Bluetooth slot. Expect
   lighting and layer controls early; wireless still needs radio/host readiness.
2. Hold a basic key through startup, then release it. Also press and release a
   key entirely before readiness: it should not arrive later as a stuck press.
   Repeat with a modifier and media key. Check wired enumeration with these held.
3. Change Fn route or BT slot during the radio boot allowance. Verify only the
   final selected route starts. Confirm unchanged switches preserve the choice.
4. Test explicit Fn+P only on a deliberately chosen Bluetooth test slot; no
   global reset or dongle re-pairing is needed. Confirm one pairing request does
   not get cancelled by a later automatic non-pairing command.
5. Confirm layer lighting, fixed layer-key colours, battery gauge polling and
   Fn+Y diagnostics still work after startup. Repeat with main lighting at zero.

Record observations and elapsed times here/the handoff before calling this
candidate hardware-tested. The preserved `known-working/layout-v5.bin` remains
the owner-tested rollback application; use the handoff's explicit-ID procedure.
