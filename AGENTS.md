# RK61 project instructions

- Read `README.md` first for the public overview. Before firmware/recovery work, read `docs/HANDOFF.md`: it is the detailed current handoff. Other stage notes are historical evidence.
- Work lives in `/home/xander/rk61-recovery/`, with firmware source in `smk/`.
- Preserve the stock dumps and `known-working/` baseline artifacts. Never overwrite a tested image with a new experiment.
- The current target is `royalkludge-rk61-rf-test_default_smk.hex` in `smk/build-rf-debug/`; it includes Bluetooth. The default/prototype target is the old wired-only build.
- The all-mode port is in `smk/src/keyboards/royalkludge-rk61/layouts/rf-test/` and reuses the driver in `layouts/led-test/`.
- The Git root is `/home/xander/rk61-recovery/`; `smk/` is vendored, normally tracked source, not a submodule/nested repo. Its original Git metadata is preserved locally under `.git/smk-upstream.git`. Do not assume upstream SMK HEAD contains this port.
- Keep firmware source, tests, docs and reviewed `known-working/` artifacts tracked. Do not add ignored toolchains, builds, secrets, stock dumps or stock-containing bundles. See `VERSION_CONTROL.md`.
- After a completed requested change, run the relevant validation. The user creates commits; do not make commits. Do not include unrelated edits, fabricate earlier history, or push without permission.
- Hardware-confirmed: USB, Fn layer, LED on/off/channel cycling, dongle output, Bluetooth via the documented pairing test. Do not extrapolate this into exhaustive battery/reconnection/all-slot validation.
- Keep ISP enabled. Never use preset-based/generated flash targets: this board is 258a:00e1, whereas the old RK61 flasher preset uses 00c7.
- Flashing is a separate user-run privileged operation; the harness blocks sudo. Do not bypass that boundary. Do not flash a full 65,536-byte stock dump as an application payload.
- Do not change the radio's firmware, erase bonds globally, or factory-reset pairing as a routine troubleshooting step. Bluetooth pairing is explicit and slot-specific.
- Run the actual SDCC build, interrupt checks, and `python3 test_bluetooth.py` after functional changes. Host tests do not prove electrical or over-air correctness. Editor-only `.clangd` flags are not the MCU compiler configuration.
- Document new hardware results and limits in README/the relevant stage notes. Keep new candidates distinct from the preserved baseline.
