"""Stock-derived battery decoding/filter checks; not sensor calibration."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOARD = ROOT / "smk/src/keyboards/royalkludge-rk61"
SOURCE = BOARD / "layouts/rf-test"

HARNESS = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "packet.h"
#include "battery.h"
#include "lighting.h"
static uint8_t response[4];
static void make(uint8_t a, uint8_t b) {
    response[0] = 0xbb;
    response[1] = (uint8_t)(0x55 - a - b);
    response[2] = a; response[3] = b;
}
static void observe(unsigned code, uint8_t now) {
    make((uint8_t)(code >> 1), (uint8_t)((code & 1) << 7));
    rk61_battery_observe(response, now);
}
static void expect(unsigned state) { assert(rk61_led_battery_state() == state); }
int main(void) {
    // Independent equivalent of stock's doubling and conditional OR, across
    // every payload combination. Route/link/LED bits must not change the code.
    for (unsigned a = 0; a < 256; ++a) {
        for (unsigned b = 0; b < 256; ++b) {
            make(a, b);
            unsigned expected = 2 * (a % 8) + (b >= 128);
            assert(rk61_packet_battery_code(response) == expected);
            for (unsigned byte = 0; byte < 4; ++byte) {
                response[byte] ^= 1;
                assert(rk61_packet_battery_code(response) == 255);
                response[byte] ^= 1;
            }
        }
    }
    static const uint8_t states[] = {0x81,0x81,0x81,2,2,3,3,4,4,5,5,5,5,5,5,5};
    for (unsigned code = 0; code < 16; ++code) {
        rk61_battery_init(0); expect(0);
        observe(code, 0); expect(states[code]); // every boundary, first valid
    }
    static const uint8_t logs[][4] = {
        {0xbb,0x30,0x25,0}, {0xbb,0x18,0x25,0x18}, {0xbb,0xf8,0x25,0x38}
    };
    for (unsigned i = 0; i < 3; ++i) {
        assert(rk61_packet_battery_code(logs[i]) == 10);
        rk61_battery_init(0); rk61_battery_observe(logs[i], 0); expect(5);
    }
    rk61_battery_init(0);
    make(0xff,0xff); response[0] = 0xff;
    rk61_battery_observe(response, 0); expect(0); // boot failure != empty/full
    observe(8, 0); expect(4);
    for (unsigned i = 0; i < 20; ++i) { observe(9, i); observe(8, i); expect(4); }
    observe(10, 20); observe(9, 21); expect(4);
    observe(10, 22); expect(5); // same BAND, three valid confirmations
    observe(7, 23); observe(8, 24); expect(5);
    make(4, 0); response[1] ^= 1;
    rk61_battery_observe(response, 25); expect(5); // resets confirmation sequence
    observe(7, 26); observe(8, 27); expect(5);
    observe(7, 28); expect(4);
    observe(2, 29); expect(0x81); // warning is immediate, not delayed by filter
    observe(3, 30); observe(3, 31); expect(0x81);
    observe(2, 32); expect(0x81); // no chatter on recovery
    observe(3, 33); observe(4, 34); observe(3, 35); expect(2);
    rk61_battery_expire(74); expect(2);
    rk61_battery_expire(75); expect(0); // last reading now 40 epochs old
    rk61_battery_expire(35); expect(0); // clock wrapping cannot resurrect data
    observe(0, 36); expect(0x81); // actual zero is low, never "unknown"
    rk61_battery_init(250); observe(10, 250);
    rk61_battery_expire(33); expect(5); // wrap-safe age 39
    rk61_battery_expire(34); expect(0);
    observe(6, 35); expect(3); // immediate recovery from unknown
    puts("PASS: exhaustive split-code/checksum decoding, stock vectors/bands, filtering/low/stale/wrap");
}
"""


class BatteryChecks(unittest.TestCase):
    def test_real_decoder_and_policy(self):
        with tempfile.TemporaryDirectory(prefix="rk61-battery-") as temp:
            source = Path(temp) / "test.c"
            output = Path(temp) / "test"
            source.write_text(HARNESS)
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                            "-I", str(SOURCE), "-I", str(BOARD), str(source),
                            str(SOURCE / "packet.c"), str(SOURCE / "battery.c"),
                            "-o", str(output)], check=True)
            subprocess.run([str(output)], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
