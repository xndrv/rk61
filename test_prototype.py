"""Offline checks of the actual linked RK61 image; no USB access."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "smk/build-rk61"
STEM = "royalkludge-rk61_default_smk"


def load_hex(path: Path) -> dict[int, int]:
    memory: dict[int, int] = {}
    base = 0
    ended = False
    for line in path.read_text().splitlines():
        if not line.startswith(":") or ended:
            raise ValueError("Malformed Intel HEX")
        record = bytes.fromhex(line[1:])
        if len(record) < 5 or len(record) != record[0] + 5 or sum(record) & 255:
            raise ValueError("Invalid Intel HEX checksum/length")
        size, kind = record[0], record[3]
        addr = int.from_bytes(record[1:3], "big")
        payload = record[4:4 + size]
        if kind == 0:
            for i, value in enumerate(payload):
                target = base + addr + i
                if target in memory and memory[target] != value:
                    raise ValueError("Conflicting image records")
                memory[target] = value
        elif kind == 1:
            if size or addr:
                raise ValueError("Malformed EOF")
            ended = True
        elif kind in (2, 4):
            if size != 2 or addr:
                raise ValueError("Malformed extended address")
            base = int.from_bytes(payload, "big") << (4 if kind == 2 else 16)
        else:
            raise ValueError("Unexpected HEX record type")
    if not ended or not memory:
        raise ValueError("Incomplete image")
    return memory


class PrototypeChecks(unittest.TestCase):
    FN_LAYER = 1
    FN_KEYCODE = 1  # transparent Fn in the original layouts
    BASE_OVERRIDES = {}
    FN_ARROWS = {(1, 2): 0x52, (2, 1): 0x50, (2, 2): 0x51, (2, 3): 0x4F}

    @classmethod
    def setUpClass(cls):
        cls.image = load_hex(BUILD / f"{STEM}.hex")
        cls.mapping = json.loads((ROOT / "matrix.json").read_text())
        cls.linkmap = (BUILD / f"{STEM}.map").read_text()

    def symbol(self, name: str) -> int:
        match = re.search(r"^C:\s+([0-9A-F]+)\s+" + re.escape(name) + r"\s", self.linkmap, re.M)
        if match is None:
            raise ValueError(f"Missing linked symbol: {name}")
        return int(match[1], 16)

    def key(self, layer: int, row: int, col: int) -> int:
        addr = self.symbol("_keymaps") + ((layer * 5 + row) * 14 + col) * 2
        return self.image[addr] | (self.image[addr + 1] << 8)

    def test_image_bounds(self):
        self.assertEqual(min(self.image), 0)
        self.assertLess(max(self.image), 0xEC00)  # settings, marker, bootloader excluded

    def test_base_layer_matches_stock(self):
        count = 0
        for row, cells in enumerate(self.mapping["matrix"]):
            for col, cell in enumerate(cells):
                if cell["key"] == "Fn":
                    expected = 0x5220 + self.FN_LAYER
                elif cell["key"] in {"Unused", "NonUSHash", "NonUSBackslash", "International1"}:
                    expected = 0
                elif cell["modifier"]:
                    self.assertEqual(cell["modifier"].bit_count(), 1)
                    expected = 0xE0 + cell["modifier"].bit_length() - 1
                else:
                    expected = cell["usage"]
                expected = self.BASE_OVERRIDES.get((row, col), expected)
                self.assertEqual(self.key(0, row, col), expected, (row, col, cell["key"]))
                count += bool(expected)
        self.assertEqual(count, 61)

    def test_fn_bindings(self):
        for col in range(1, 13):
            self.assertEqual(self.key(self.FN_LAYER, 0, col), 0x39 + col)  # F1..F12
        for (row, col), usage in self.FN_ARROWS.items():
            self.assertEqual(self.key(self.FN_LAYER, row, col), usage)
        self.assertEqual(self.key(self.FN_LAYER, 0, 0), 0x35)  # grave
        self.assertEqual(self.key(self.FN_LAYER, 0, 13), 0x4C)  # delete
        self.assertEqual(self.key(self.FN_LAYER, 4, 13), self.FN_KEYCODE)

    def test_isp_jump_present(self):
        addr = self.symbol("_isp_jump")
        actual = bytes(self.image[addr + i] for i in range(10))
        self.assertEqual(actual, bytes.fromhex("c2 af 75 f0 a5 74 5a 02 ff 00"))

    def test_interrupt_check_passed(self):
        self.assertTrue((BUILD / "royalkludge-rk61_default_smk.interrupts-ok").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
