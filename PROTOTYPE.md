# RK61 SMK prototype — historical keys-only stage

This file describes the first wired-only variant. Later stages added tested LEDs, dongle output and Bluetooth; `README.md` is the current all-mode handoff.

## What is implemented

A local board definition in `smk/src/keyboards/royalkludge-rk61/`:

- Stock-derived 14-column / 5-row matrix pins, idle high, active low.
- 61-key ANSI base map, including Fn.
- Hold Fn: number row 1..= becomes F1..F12, WASD becomes arrows, Esc becomes grave, Backspace becomes Delete.
- Transparent fall-through elsewhere; layer bindings are draft defaults, editable in `layouts/default/layout.c`.
- Wired USB reports only.
- ISP HID support enabled and its linked jump sequence checked offline.
- NKRO enabled through upstream defaults.
- Sleep disabled. Unported LED/radio/control GPIO pins left as inputs without pull-ups.
- RGB, radio, battery/charging controls and switch-state handling are NOT implemented.
- Owner flashed the keys-only image and confirmed typing plus Fn+WASD arrows work.

## Build and validation

Run `bash ~/rk61-recovery/build-prototype.sh`.

The compiler and Meson are locally installed/extracted under `toolchain/` and `venv/`; no system-wide package installation was performed.

Upstream baseline commit: `69373bbb633bd1159f4541f486ff7506563a38ec`.
Compiler: SDCC 4.6.0. Two upstream source files needed const-correctness adjustments for this compiler: `src/sino51lib/flash.c`, `src/smk/usb.c`.

Output: `smk/build-rk61/royalkludge-rk61_default_smk.hex`.

- Compiler/linker succeeded.
- Upstream interrupt checker passed: 14 claimed vectors, no reported overlay collisions.
- Five offline image tests passed: HEX validity/application bounds, base-layer agreement, Fn mappings, ISP jump sequence, interrupt-check artifact.
- Active LSP checks timed out; they are not evidence of a clean result. Actual SDCC compilation is the relevant platform build check.
- Owner confirmed the keys-only image enumerates and works. No simulator test was performed; long-term stability and restoration remain untested. The later LED-test variant was also owner-tested; see `LED-TEST.md`.

## Before any first flash

Do NOT use upstream's generated `royalkludge-rk61_default_flash` target. It uses sinowisp's preset for PID 00C7, whereas this board and prototype use PID 00E1. First-flash and restore commands must be explicitly reviewed for the correct identity and image section.

The full stock dump is an ISP-view backup, not an application-only USB payload. A correctly derived application image is needed for USB restoration; the converted full image is for a potential external programmer. Recovery has not been tested.

The first prototype deliberately lacks lighting. Leaving unknown outputs high-impedance is conservative, not proof that all LEDs/radio/power circuitry will be in the desired state. Do not infer that the stock bootloader can recover a prototype that never enumerates or cannot process ISP commands.

## Lighting feasibility assessment

The stock firmware directly configures the SH68F90 PWM register banks in routine 0x6E6F. Correction to the earlier interrupt attribution: vector 0x3B / handler 0xAC7F is USB, not PWM. PWM0 is vector 0x43 / handler 0xAC3C, which calls scan routine 0x947C; that routine also calls the LED duty-register loader at 0x5BFC (or 0x5ECD for a different buffer).

A separate diagnostic LED driver has now been built from stock PWM setup and off-point evidence. See `LED-TEST.md` for hardware-test instructions, checks, limitations, and rollback. The owner confirmed dim lighting, green/red/blue/white cycling and full off. Precise brightness/electrical characterization and exhaustive per-key mapping still need work before richer effects.
