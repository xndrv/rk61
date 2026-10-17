"""Offline tests for the RF image and real packet encoder (not RF hardware)."""

import ctypes
import json
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_leds
import test_prototype

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "smk/src/keyboards/royalkludge-rk61/layouts/rf-test"
BUILD = ROOT / "smk/build-rf-debug"
STEM = "royalkludge-rk61-rf-test_default_smk"
Byte = ctypes.c_uint8
Packet = Byte * 32


class WirelessImageChecks(test_leds.LedImageChecks):
    # Current all-mode target: three Corne-inspired layers plus a separate Fn.
    FN_LAYER = 4
    FN_KEYCODE = 0x5224
    # Fn+W is now BT2; Up remains available on L1+K.
    FN_ARROWS = {(2, 1): 0x50, (2, 2): 0x51, (2, 3): 0x4F}
    LED_TOGGLE_LAYER = 3
    LED_TOGGLE_POSITION = (1, 0)
    LED_CYCLE_POSITION = (3, 9)
    BASE_OVERRIDES = {(4, 1): 0xE2, (4, 2): 0x5221, (4, 8): 0x5222, (4, 9): 0xE3, (4, 10): 0x5223}

    @classmethod
    def setUpClass(cls):
        cls.image = test_prototype.load_hex(BUILD / f"{STEM}.hex")
        cls.mapping = json.loads((ROOT / "matrix.json").read_text())
        cls.linkmap = (BUILD / f"{STEM}.map").read_text()

    def test_interrupt_check_passed(self):
        self.assertTrue((BUILD / "royalkludge-rk61-rf-test_default_smk.interrupts-ok").is_file())

    def test_route_shortcuts(self):
        toggle = self.led_toggle_keycode()
        self.assertEqual(self.key(self.FN_LAYER, 1, 4), toggle + 2)  # Fn+R
        self.assertEqual(self.key(self.FN_LAYER, 1, 5), toggle + 3)  # Fn+T
        self.assertEqual(self.key(self.FN_LAYER, 1, 6), toggle + 4)  # Fn+Y


class PacketChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="rk61-rf-packet-")
        library = Path(cls.temp.name) / "packet.so"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        str(SOURCE / "packet.c"), "-o", str(library)], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.rk61_packet_command.argtypes = [ctypes.POINTER(Byte), Byte, Byte, Byte]
        cls.lib.rk61_packet_command.restype = Byte
        cls.lib.rk61_packet_keyboard.argtypes = [ctypes.POINTER(Byte), Byte, ctypes.POINTER(Byte), ctypes.POINTER(Byte)]
        cls.lib.rk61_packet_keyboard.restype = None
        cls.lib.rk61_packet_extra.argtypes = [ctypes.POINTER(Byte), ctypes.c_uint16, ctypes.c_uint16]
        cls.lib.rk61_packet_extra.restype = None
        cls.lib.rk61_packet_status_valid.argtypes = [ctypes.POINTER(Byte)]
        cls.lib.rk61_packet_status_valid.restype = ctypes.c_bool

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_stock_command_vectors(self):
        for cmd, a, b, expected in [
            (1, 0, 0, "aa03010000a7"),  # existing dongle link; no pairing
            (6, 1, 0, "aa03060100a1"),  # USB mode
            (0x0A, 0, 0, "aa030a00009e"),
            (0x0C, 0, 0, "aa030c00009c"),
        ]:
            out = Packet()
            self.assertEqual(self.lib.rk61_packet_command(out, cmd, a, b), 6)
            self.assertEqual(bytes(out[:6]).hex(), expected)
            self.assertEqual(bytes(out[6:]), bytes(26))

    def test_release_packet(self):
        out = Packet()
        self.lib.rk61_packet_keyboard(out, 0, None, None)
        self.assertEqual(bytes(out[:4]), bytes.fromhex("aa1d0200"))
        self.assertEqual(out[9], 1)
        self.assertEqual(out[31], 0x8B)
        self.assertEqual(sum(out) & 255, 0x55)

    def test_nkro_and_modifier_packets(self):
        rng = random.Random(916)
        out = Packet()
        for _ in range(100):
            mods = rng.randrange(256)
            data = bytes(rng.randrange(256) for _ in range(20))
            out = Packet()
            self.lib.rk61_packet_keyboard(out, mods, None, (Byte * 20).from_buffer_copy(data))
            self.assertEqual(out[3], mods)
            self.assertEqual(bytes(out[4:9]), bytes(5))
            self.assertEqual(bytes(out[10:30]), data)
            self.assertEqual(out[9], 0)
            self.assertEqual(out[30], 0)
            self.assertEqual(sum(out) & 255, 0x55)
        self.lib.rk61_packet_keyboard(out, 2, None, None)
        self.assertEqual(out[9], 0)  # modifier-only press is NOT a release

    def test_legacy_and_extra_packets(self):
        out = Packet()
        self.lib.rk61_packet_keyboard(out, 1, (Byte * 5)(4, 5, 6, 7, 8), None)
        self.assertEqual(bytes(out[3:10]), bytes([1, 4, 5, 6, 7, 8, 0]))
        self.assertEqual(sum(out) & 255, 0x55)
        self.lib.rk61_packet_extra(out, 0x1234, 0x5678)
        self.assertEqual(bytes(out[:3]), bytes.fromhex("aa0b05"))
        self.assertEqual(bytes(out[9:13]), bytes.fromhex("34127856"))
        self.assertEqual(sum(out[:14]) & 255, 0x55)

    def test_response_validation(self):
        valid = bytes.fromhex("bbbd8018")
        self.assertTrue(self.lib.rk61_packet_status_valid((Byte * 4).from_buffer_copy(valid)))
        for i in range(4):
            corrupt = bytearray(valid)
            corrupt[i] ^= 1
            self.assertFalse(self.lib.rk61_packet_status_valid((Byte * 4).from_buffer_copy(corrupt)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
