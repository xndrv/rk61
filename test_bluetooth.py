"""Image, command sequence and routing tests; no Bluetooth hardware simulation."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import test_wireless as wireless

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "smk/src/keyboards/royalkludge-rk61/layouts/rf-test"


class BluetoothImageChecks(wireless.WirelessImageChecks):
    def test_bluetooth_shortcuts(self):
        toggle = self.led_toggle_keycode()
        for slot in range(3):
            self.assertEqual(self.key(self.FN_LAYER, 1, 1 + slot), toggle + 5 + slot)  # Q/W/E
            self.assertEqual(self.key(self.FN_LAYER, 3, 5 + slot), toggle + 5 + slot)  # B/N/M aliases
        self.assertEqual(self.key(self.FN_LAYER, 1, 10), toggle + 8)

    def test_keyboard_lighting_shortcuts(self):
        toggle = self.led_toggle_keycode()
        self.assertEqual(self.key(self.FN_LAYER, 1, 11), toggle + 9)  # Fn+[
        self.assertEqual(self.key(self.FN_LAYER, 1, 12), toggle + 10)  # Fn+]
        self.assertEqual(self.key(self.FN_LAYER, 3, 9), toggle + 1)  # Fn+.
        self.assertEqual(self.key(3, 1, 3), toggle + 1)  # L3+E alias; Fn+E is BT3

    def assert_user_layer(self, layer, assignments):
        # Check every cell, including all disabled keys and electrical holes.
        expected = {(0, 13): 0x2A, (1, 0): 0x2B, (2, 13): 0x28,
                    (3, 0): 0xE1, (3, 13): 0xE5, (4, 0): 0xE0,
                    (4, 1): 0xE2, (4, 2): 0x5221, (4, 5): 0x2C,
                    (4, 8): 0x5222, (4, 9): 0xE3, (4, 10): 0x5223, (4, 13): 0x5224}
        expected.update(assignments)
        for row in range(5):
            for col in range(14):
                self.assertEqual(self.key(layer, row, col), expected.get((row, col), 0),
                                 (layer, row, col))

    def test_number_navigation_layer(self):
        assignments = {(1, col): 0x1D + col for col in range(1, 11)}  # 1..0
        assignments.update({(3, col): 0x39 + col for col in range(1, 11)})  # F1..10
        assignments.update({(2, 6): 0x50, (2, 7): 0x51, (2, 8): 0x52, (2, 9): 0x4F})
        self.assert_user_layer(1, assignments)

    def test_symbol_layer(self):
        assignments = {(1, col): 0x200 | (0x1D + col) for col in range(1, 11)}
        for col, usage in enumerate([0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x35], 6):
            assignments[(2, col)] = usage
            if col < 11:
                assignments[(3, col)] = 0x200 | usage
        self.assert_user_layer(2, assignments)

    def test_media_screenshot_layer(self):
        toggle = self.led_toggle_keycode()
        self.assert_user_layer(3, {(1, 0): toggle, (1, 1): 0xAA, (1, 2): 0xA9,
                                   (1, 3): toggle + 1, (1, 6): 0x46,
                                   (2, 4): 0xBD, (3, 4): 0xBE,
                                   (2, 6): 0xAC, (2, 7): 0xAB, (2, 8): 0xAE})


class BluetoothPacketChecks(wireless.PacketChecks):
    def test_stock_bluetooth_vectors(self):
        for slot in range(1, 4):
            for pairing in (0, 1):
                out = wireless.Packet()
                self.lib.rk61_packet_command(out, 1, pairing, slot)
                self.assertEqual(bytes(out[:6]), bytes([0xAA, 3, 1, pairing, slot, 0xA7 - pairing - slot]))


MOCK_HEADER = r'''
#pragma once
#include <stdbool.h>
#include <stdint.h>
#define __xdata
#define __critical
#define MATRIX_ROWS 5
#define MATRIX_COLS 14
#define REPORT_ID_NKRO 6
#define REPORT_ID_CONSUMER 2
#define REPORT_ID_SYSTEM 1
#define NKRO_REPORT_BITS 20
extern uint8_t P4_7, P7_5, P0_2, P0_4, P0_3, P4_1, P0CR, P4CR, P7CR, P5CR, P5PCR, P5_5, P5_6;
enum { RK61_LED_TOGGLE = 0x7e00, RK61_LED_CHANNEL, RK61_RF_24G, RK61_USB_MODE, RK61_RF_STATUS,
       RK61_BT1, RK61_BT2, RK61_BT3, RK61_BT_PAIR };
typedef union { uint8_t raw[8]; struct {uint8_t mods, reserved, keys[6];}; } report_keyboard_t;
typedef struct { uint8_t report_id, mods, bits[20]; } report_nkro_t;
typedef struct { uint8_t report_id; uint16_t usage; } report_extra_t;
void delay_us(uint16_t us);
void delay_ms(uint16_t ms);
void watchdog_kick(void);
void usb_send_report(report_keyboard_t *report);
void usb_send_nkro(report_nkro_t *report);
void usb_send_extra(report_extra_t *report);
void host_consumer_send(uint16_t usage);
void host_system_send(uint16_t usage);
'''
REGISTERS = "uint8_t P4_7, P7_5, P0_2, P0_4, P0_3, P4_1, P0CR, P4CR, P7CR, P5CR, P5PCR, P5_5, P5_6;\n"
ROUTING_HARNESS = r'''
#include <assert.h>
#include "mock.h"
#include "radio.h"
REGISTERS
static int last_link = -1, paired, selections, releases, usb_reports, radio_reports;
void rk61_radio_init(void) {}
void rk61_radio_select(bool wireless) { assert(!wireless); last_link = -1; ++selections; }
void rk61_radio_select_link(uint8_t link, bool pairing) {
    assert(link <= 3 && (!pairing || link));
    last_link = link; paired = pairing; ++selections;
}
void rk61_radio_release(void) { ++releases; }
void rk61_radio_status(void) {}
void rk61_radio_task(void) {}
void rk61_radio_keyboard(report_keyboard_t *r) { (void)r; ++radio_reports; }
void rk61_radio_nkro(report_nkro_t *r) { (void)r; ++radio_reports; }
void rk61_radio_extra(report_extra_t *r) { (void)r; ++radio_reports; }
void usb_send_report(report_keyboard_t *r) { (void)r; ++usb_reports; }
void usb_send_nkro(report_nkro_t *r) { (void)r; ++usb_reports; }
void usb_send_extra(report_extra_t *r) { (void)r; ++usb_reports; }
#include "KB_PATH"
static int consumer_releases, system_releases, released_route = -1;
void host_consumer_send(uint16_t usage) {
    assert(usage == 0);
    ++consumer_releases;
    released_route = radio_mode;
}
void host_system_send(uint16_t usage) { assert(usage == 0); ++system_releases; }
static void poll(unsigned samples) { while (samples--) kb_update_switches(); }
static void move_switches(uint8_t bits) {
    P5_5 = bits & 1;
    P5_6 = (bits >> 1) & 1;
    poll(256);
}
int main(void) {
    P5_6 = 1;
    kb_init();
    assert(!radio_mode && selections == 0);
    assert(rk61_led_connection_colour() == RK61_COLOUR_MAGENTA);
    assert(!kb_process_record(RK61_BT_PAIR, true)); // no pairing in USB mode
    assert(selections == 0);
    for (int slot = 1; slot <= 3; ++slot) {
        int before = selections;
        assert(!kb_process_record(RK61_BT1 + slot - 1, false));
        assert(selections == before); // release must not select or pair
        int extra_before = consumer_releases;
        bool old_route = radio_mode;
        kb_process_record(RK61_BT1 + slot - 1, true);
        assert(consumer_releases == extra_before + 1 && system_releases == consumer_releases);
        assert(released_route == old_route); // release before routing changes
        assert(radio_mode && radio_link == slot && last_link == slot && !paired);
        kb_process_record(RK61_BT_PAIR, false);
        assert(!paired);
        extra_before = consumer_releases;
        kb_process_record(RK61_BT_PAIR, true);
        assert(last_link == slot && paired);
        assert(consumer_releases == extra_before + 1 && released_route == 1);
        assert(rk61_led_connection_colour() == RK61_COLOUR_TEAL);
        before = selections;
        poll(300); // unchanged physical switches must not cancel advertising
        assert(selections == before && paired);
    }
    kb_process_record(RK61_RF_24G, true);
    assert(radio_mode && radio_link == 0 && last_link == 0 && !paired);
    assert(rk61_led_connection_colour() == RK61_COLOUR_ORANGE);
    int before = selections;
    kb_process_record(RK61_BT_PAIR, true);
    assert(selections == before); // cannot disturb the working dongle bond
    report_nkro_t report = {0};
    kb_send_nkro(&report);
    assert(radio_reports == 1);
    kb_process_record(RK61_USB_MODE, true);
    assert(!radio_mode && last_link == -1);
    assert(released_route == 1 && system_releases == consumer_releases);
    before = usb_reports;
    kb_send_nkro(&report);
    assert(usb_reports == before + 1);
    assert(releases >= 3);
    assert(kb_process_record(RK61_LED_TOGGLE, true)); // preserve LED handler
    assert(kb_process_record(4, true)); // preserve ordinary key processing
    before = selections;
    poll(300); // unchanged switches preserve explicit wired selection
    assert(!radio_mode && selections == before);
    assert(rk61_led_connection_colour() == RK61_COLOUR_MAGENTA);

    // A stable physical change takes over; BT slot 3 was remembered above.
    move_switches(0);
    assert(radio_mode && radio_link == 0 && !paired);
    assert(rk61_led_connection_colour() == RK61_COLOUR_ORANGE);
    move_switches(1);
    assert(radio_mode && radio_link == 3 && !paired);
    kb_process_record(RK61_BT2, true);
    move_switches(0); assert(radio_link == 0);
    move_switches(1); assert(radio_link == 2); // RAM-only last Bluetooth slot
    assert(rk61_led_connection_colour() == RK61_COLOUR_TEAL);
    move_switches(3); assert(!radio_mode); // power-off/wired input wins
    move_switches(2); assert(!radio_mode); // selector doesn't override wired input
    assert(rk61_led_connection_colour() == RK61_COLOUR_MAGENTA);

    // Reject alternating samples and short bounces: require 256 consecutive
    // samples of one new pair, not a mixture of different switch positions.
    before = selections;
    P5_6 = 0; poll(100);
    P5_5 = 1; poll(200);
    P5_6 = 1; poll(100);
    P5_5 = 0; poll(300); // return to accepted state; resets debounce
    assert(!radio_mode && selections == before);
    P5_6 = 0; P5_5 = 1;
    poll(255); assert(!radio_mode && selections == before);
    poll(1); assert(radio_mode && radio_link == 2 && !paired);
    before = selections; poll(500); assert(selections == before);

    // Boot truth table: stock-derived pin polarity, not simulated hardware.
    for (unsigned bits = 0; bits < 4; ++bits) {
        P5_5 = bits & 1; P5_6 = (bits >> 1) & 1;
        kb_init();
        if (bits & 2) {
            assert(!radio_mode && rk61_led_connection_colour() == RK61_COLOUR_MAGENTA);
        } else {
            assert(radio_mode && radio_link == ((bits & 1) ? 1 : 0));
            assert(rk61_led_connection_colour() == ((bits & 1) ? RK61_COLOUR_TEAL : RK61_COLOUR_ORANGE));
            assert(!paired);
        }
    }
}
'''
SEQUENCE_HARNESS = r'''
#include <assert.h>
#include "mock.h"
REGISTERS
static uint8_t bytes[256], accumulator, bits;
static unsigned count;
void delay_us(uint16_t us) {
    // Observe the real TX bit loop after each rising clock edge.
    if (us == 2 && P4_7 && (P0CR & 0x10)) {
        accumulator = (uint8_t)((accumulator << 1) | !!P0_4);
        if (++bits == 8) { assert(count < sizeof(bytes)); bytes[count++] = accumulator; bits = 0; }
    }
}
void delay_ms(uint16_t ms) { (void)ms; }
void watchdog_kick(void) {}
#include "RADIO_PATH"
static void check_frame(unsigned offset, uint8_t command_id, uint8_t a, uint8_t b) {
    assert(bytes[offset] == 0xaa && bytes[offset + 1] == 3);
    assert(bytes[offset + 2] == command_id && bytes[offset + 3] == a && bytes[offset + 4] == b);
    unsigned sum = 0;
    for (unsigned i = 0; i < 6; ++i) sum += bytes[offset + i];
    assert((sum & 255) == 0x55);
}
int main(void) {
    rk61_radio_select_link(4, false);
    rk61_radio_select_link(0, true);
    assert(count == 0); // guards run before any radio transmission
    for (unsigned link = 0; link <= 3; ++link) {
        count = bits = 0;
        rk61_radio_select_link(link, false);
        assert(count == 24);
        check_frame(0, 0x0c, 0, 0);
        check_frame(6, 1, 0, link);
        check_frame(12, 1, 0, link);
        check_frame(18, 0x0a, 0, 0);
        if (link) {
            count = bits = 0;
            rk61_radio_select_link(link, true);
            assert(count == 18); // no second command cancelling/restarting advertising
            check_frame(0, 0x0c, 0, 0);
            check_frame(6, 1, 1, link);
            check_frame(12, 0x0a, 0, 0);
        }
    }
    count = bits = 0;
    rk61_radio_select(false);
    assert(count == 12);
    check_frame(0, 6, 1, 0);
    check_frame(6, 0x0a, 0, 0);
}
'''


class BluetoothHostChecks(unittest.TestCase):
    def run_harness(self, source: str, extra_sources: list[str]):
        source = source.replace("REGISTERS", REGISTERS).replace("KB_PATH", str(SOURCE / "kb.c")).replace("RADIO_PATH", str(SOURCE / "radio.c"))
        with tempfile.TemporaryDirectory(prefix="rk61-bt-host-") as temp:
            directory = Path(temp)
            (directory / "mock.h").write_text(MOCK_HEADER)
            for name in ["kbdef.h", "report.h", "usb.h", "host.h", "delay.h", "watchdog.h"]:
                (directory / name).write_text('#include "mock.h"\n')
            (directory / "debug.h").write_text('#define dprintf(...) ((void)0)\n')
            (directory / "test.c").write_text(source)
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-value",
                            "-I", temp, "-I", str(SOURCE), "-I", str(SOURCE.parent.parent), str(directory / "test.c"),
                            *extra_sources, "-o", str(directory / "test")], check=True)
            subprocess.run([str(directory / "test")], check=True)

    def test_real_routing_and_pairing_guards(self):
        self.run_harness(ROUTING_HARNESS, [])

    def test_real_radio_command_sequences(self):
        self.run_harness(SEQUENCE_HARNESS, [str(SOURCE / "packet.c")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
