# RK61 BYK916 stock-firmware reconstruction

Board reported by owner: `130-81892-10 US`, `2022/08/16`.
Normal USB identity: `258a:00e1`.

## Input and recovery artifacts

- `stock-full-isp.bin`: original USB-view dump, 65,536 bytes.
- SHA-256: `8378056391aacc8705c45179525863485a730a214d220e4d43fdf98606815833`.
- Application region: `0x0000..0xEFFF`; bootloader: `0xF000..0xFFFF`.
- Bootloader MD5: `3e0ebd0c440af5236d7ff8872343f85d`, matching sinowisp's documented RK61 bootloader.
- `stock-full-icp.bin`: sinowisp ISP-to-JTAG conversion for potential external programming. NOT a tested recovery image.
- Neither USB restoration nor physical programming access has been tested.
- The raw full dump is NOT automatically an application-only USB flash payload.

## Matrix evidence

`stock.asm` is reachable-code disassembly with SH68F90 register symbols derived from SMK. Most data bytes remain data. The computed-jump table at `0x9493` has been added as explicit entry points.

- GPIO initialization at `0xA829` configures ports and pull-ups.
- Scan routine at `0x947C` deselects columns by setting P6=FF, P5|=87, P4|=05.
- Fourteen LJMP entries at `0x9493..0x94BC` dispatch to CLR-bit instructions.
- Ordered active-low column outputs: P6.0, P6.1, P6.2, P6.3, P6.4, P6.5, P6.6, P6.7, P5.0, P5.1, P5.2, P5.7, P4.0, P4.2.
- Row sampling at `0x94F3` combines `(P7 & 0x0F) | ((P5 << 1) & 0x30) | 0xC0`.
- Two samples are compared, then inverted; original bit 0 is masked off before storing into internal RAM `0x4E + column`.
- Usable row inputs in order: P7.1, P7.2, P7.3, P5.3, P5.4. Pressed level is low.
- Scanner advances through columns 0..13. The later event-processing loops support a larger generic 21-column, 6-bit buffer; that is not the physical matrix size.
- Event processing at `0x67B4` increments a key index across 6 original row bits per column.
- Key-action lookup at `0x0046` uses four-byte records at `0xC600 + key_index * 4`. For the usable rows, `key_index = column * 6 + row + 1`.
- Records in this base table are `[0, modifier_mask, keyboard_usage, 0]`.
- Fn check at `0x6670` reads internal RAM `0x5B` bit 5: column 13 / P4.2, row P5.4. Fn has no ordinary HID entry.

`matrix.json` and `matrix-table.md` contain the reconstructed base layer and pin assignments. Excluding empty cells and three ISO/JIS-only entries gives exactly 61 unique positions including Fn. Treat those three entries as likely unpopulated for this US PCB, not electrically verified absent switches.

## Scope and next step

This document records the original static reconstruction, before the first hardware tests. Subsequent stages were flashed and owner-confirmed: wired keys/Fn, LEDs, dongle output, and Bluetooth. See `README.md` for current status and the preserved all-mode baseline.

The recovered wiring supports this board-specific port, not an interchangeable NuPhy image. Battery power management, complete switch handling, persistence, and long-term reliability remain work in progress. Stock/external recovery remains untested.

## Reproduction

Run `python3 prepare_disassembly.py` (requires the local disasm51 virtual environment and SMK checkout), then `python3 extract_matrix.py`. The extractor rejects dumps with a different size or SHA-256 and validates the column-dispatch and row-sampling signatures before writing its reports.
