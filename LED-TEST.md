# RK61 LED diagnostic test

Status: hardware-tested by the owner. LEDs work but are deliberately dim; Fn+E cycles green, red, blue, white; Fn+Q turns them fully off. The tested image is also preserved at `known-working/keys-and-leds.bin`.

## Files

- Flash image: `~/rk61-recovery/rk61-led-test.bin`, 61,440-byte application-only image.
- SHA-256: `41db0463861e2d2b3372808f010f16c36efd9087ca07aa46ce90e495e4a08e27`.
- Preserved working rollback: `~/rk61-recovery/known-working/keys-only.bin`.
- Rollback SHA-256: `27b1d4b6b340607d78029932fe0c751cfaa5ef7d7874231e126a08b1d9010514`.
- Driver and diagnostic layout: `smk/src/keyboards/royalkludge-rk61/layouts/led-test/`.
- This variant is separate from the default keys-only layout.

## Expected behavior

After USB enumeration, display a dim all-channel pattern, ideally white. Fn+Q toggles LEDs. Fn+E cycles channel A, B, C, then all channels. The owner subsequently confirmed channel A=green, B=red, C=blue, then all=white. Other keys and the existing Fn arrows/F-row remain unchanged. No saved settings, wireless, or animations are added.

A test report should include: whether all keys light, the three Fn+E colors in order, whether Fn+Q fully blanks the lights, any flicker, and whether normal typing / Fn+WASD still works. Unexpectedly bright, hot, or malfunctioning behavior means unplug and investigate; do not leave it running unattended.

## Evidence and conservative test settings

- Stock GPIO setup: 0xA829; PWM-source outputs on P1.3..5, P2.0..5, P3.0..5.
- Stock PWM initialization: 0x6E6F; period 0x0537, per-channel staggered DUTY1 values 0x26..0x37.
- Stock blanking routine: 0x9885 sets DUTY2 equal to DUTY1.
- Stock loader: 0x5BFC maps successive original rows to PWM20/21/22, PWM23/24/25, PWM10/11/12, PWM13/14/15, PWM03/04/05, PWM00/01/02.
- Original row zero is unscanned/unpopulated on the ANSI matrix; PWM20..22 stay at their off values in this diagnostic.
- Test: add only 64 PWM counts to the stock off points, select just one shared column at a time, blank PWM and deselect columns before each matrix sweep.
- The source-pin drive setting follows the stock value 0 (SMK names it GPIO_DRIVE_25MA). This and the short pulse are not a measured current guarantee.
- Uses existing SMK timer slots, not a new PWM ISR. USB ISP support remains compiled in.

The period, off points and bank configuration are stock-derived. The owner confirmed working dim lighting, the color order, and complete off. Precise brightness/current characterization and exhaustive populated-row/per-key validation remain untested.

## Validation and rebuild

```sh
export PATH="$HOME/rk61-recovery/venv/bin:$HOME/rk61-recovery/toolchain/usr/bin:$HOME/rk61-recovery/toolchain/bin:$PATH"
meson compile -C "$HOME/rk61-recovery/smk/build-rk61" royalkludge-rk61_led-test_smk.hex
python3 "$HOME/rk61-recovery/test_leds.py"
```

Compilation and interrupt checks passed. Seven tests passed, covering the linked base keymap, original Fn bindings, LED shortcut entries, application bounds/HEX checks, ISP jump, interrupt-check artifact, and host execution of the real driver with mock registers. Host execution checks blanking, single-column selection, period/off values, short duty deltas, toggle press/release handling, and all four channel modes. It does not simulate the physical LED circuit or real-time 8051 timing.

Clang/LSP probes lacked SDCC board include paths or timed out; they are not independent clean-build confirmation.

## Flash and rollback

Use explicit VID/PID, not the generated preset-based Meson flash targets.

```sh
sudo ~/rk61-recovery/toolchain/bin/sinowisp write \
  --platform sh68f90 --vendor_id 0x258a --product_id 0x00e1 \
  --format bin --reboot true ~/rk61-recovery/rk61-led-test.bin
```

If USB ISP remains accessible, restore working keys-only SMK with the same command but use `~/rk61-recovery/known-working/keys-only.bin` as the input. That restore path has not itself been tested; an image that loses USB/ISP access can still require hardware recovery.
