"""Extract evidence from this RK61 dump; never opens or writes a USB device."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_SHA256 = "8378056391aacc8705c45179525863485a730a214d220e4d43fdf98606815833"
PORTS = {0x80: 0, 0x90: 1, 0x98: 2, 0xA0: 3, 0xB0: 4, 0x88: 5, 0xC0: 6, 0xF8: 7}
KEYS = {4 + i: chr(ord("A") + i) for i in range(26)}
KEYS.update({30 + i: str((i + 1) % 10) for i in range(10)})
KEYS.update({
    0x28: "Enter", 0x29: "Esc", 0x2A: "Backspace", 0x2B: "Tab",
    0x2C: "Space", 0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]",
    0x31: "Backslash", 0x32: "NonUSHash", 0x33: ";", 0x34: "Quote",
    0x36: ",", 0x37: ".", 0x38: "/", 0x39: "CapsLock",
    0x64: "NonUSBackslash", 0x65: "Menu", 0x87: "International1",
})
MODIFIERS = ["LCtrl", "LShift", "LAlt", "LGUI", "RCtrl", "RShift", "RAlt", "RGUI"]


def extract(blob: bytes) -> dict:
    """Addresses below are evidence-specific, not a generic firmware detector."""
    if len(blob) != 65536 or hashlib.sha256(blob).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Unexpected firmware: this extraction is specific to the saved dump")
    columns = []
    for col in range(14):
        entry = 0x9493 + 3 * col
        if blob[entry] != 0x02:
            raise ValueError("Expected LJMP in column dispatch table")
        target = int.from_bytes(blob[entry + 1:entry + 3], "big")
        if blob[target] != 0xC2:
            raise ValueError("Expected CLR bit at column target")
        bit = blob[target + 1]
        columns.append(f"P{PORTS[bit & 0xF8]}.{bit & 7}")
    expected_read = bytes.fromhex("e5 88 25 e0 54 30 ff e5 f8 54 0f 4f 44 c0")
    if blob[0x94F3:0x94F3 + len(expected_read)] != expected_read:
        raise ValueError("Unexpected row sampling instructions")
    # Original bit 0 is explicitly cleared after inversion; usable bits are 1..5.
    rows = ["P7.1", "P7.2", "P7.3", "P5.3", "P5.4"]
    matrix = []
    for row in range(5):
        cells = []
        for col in range(14):
            address = 0xC600 + (col * 6 + row + 1) * 4
            record = blob[address:address + 4]
            if record[0] or record[3]:
                raise ValueError("Unexpected action format")
            modifier, usage = record[1:3]
            label = KEYS.get(usage, f"HID_{usage:02X}" if usage else "Unused")
            if modifier:
                label = "+".join(name for i, name in enumerate(MODIFIERS) if modifier & (1 << i))
            if (col, row) == (13, 4):
                label = "Fn"
            cells.append({"key": label, "modifier": modifier, "usage": usage,
                          "record_address": f"0x{address:04X}"})
        matrix.append(cells)
    return {"sha256": EXPECTED_SHA256, "column_pins": columns, "row_pins": rows,
            "select_level": "low", "pressed_level": "low", "matrix": matrix,
            "status": "Static reconstruction, not electrically or physically tested",
            "fn_evidence": "0x6670 checks internal RAM 0x5B bit 5 (column 13, original row bit 5)",
            "ansi_inference": "NonUSHash, NonUSBackslash, International1 are likely unpopulated on this US PCB"}


def main() -> None:
    result = extract((ROOT / "stock-full-isp.bin").read_bytes())
    (ROOT / "matrix.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["| Row pin | " + " | ".join(result["column_pins"]) + " |",
             "|---|" + "---|" * 14]
    for pin, cells in zip(result["row_pins"], result["matrix"], strict=True):
        lines.append("| " + pin + " | " + " | ".join(cell["key"] for cell in cells) + " |")
    (ROOT / "matrix-table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
