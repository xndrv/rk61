"""Execute the real keymap, matrix actions and report encoder with host sinks.

No GPIO, USB electrical behavior, or over-air Bluetooth is simulated.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SMK = ROOT / "smk/src/smk"
LAYOUT = ROOT / "smk/src/keyboards/royalkludge-rk61/layouts/rf-test"

MOCK = r'''
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "report.h"
#define __xdata
#define MATRIX_ROWS 5
#define MATRIX_COLS 14
enum { RK61_LED_TOGGLE = SAFE_RANGE, RK61_LED_CHANNEL, RK61_RF_24G,
       RK61_USB_MODE, RK61_RF_STATUS, RK61_BT1, RK61_BT2, RK61_BT3, RK61_BT_PAIR,
       RK61_LED_BRIGHTNESS_DOWN, RK61_LED_BRIGHTNESS_UP };
extern const uint16_t keymaps[][MATRIX_ROWS][MATRIX_COLS];
bool host_nkro_active(void);
void host_keyboard_send(report_keyboard_t *report);
void host_nkro_send(report_nkro_t *report);
void host_system_send(uint16_t usage);
void host_consumer_send(uint16_t usage);
bool kb_process_record(uint16_t keycode, bool pressed);
bool layout_process_record(uint16_t keycode, bool pressed);
void indicators_pwm_disable(void);
void indicators_pwm_enable(void);
void user_matrix_sinks_off(void);
void user_matrix_scan_pre(void);
void user_matrix_cols_deselect_all(void);
void user_matrix_col_select(uint8_t col);
void user_matrix_col_deselect(uint8_t col);
uint8_t user_matrix_read_rows(void);
void user_matrix_scan_post(void);
void delay_us(uint16_t us);
void sleep_note_activity(void);
'''

HARNESS = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "mock.h"
#include "LAYOUT_PATH"
#include "report.c"
#include "matrix.c"
#include "POLICY_PATH"

static bool use_nkro;
static uint8_t sent_mods;
static uint16_t consumer;
static unsigned reports, consumer_reports, custom_presses;
bool host_nkro_active(void) { return use_nkro; }
void host_keyboard_send(report_keyboard_t *r) { assert(!use_nkro); sent_mods = r->mods; ++reports; }
void host_nkro_send(report_nkro_t *r) { assert(use_nkro); sent_mods = r->mods; ++reports; }
void host_system_send(uint16_t u) { (void)u; assert(false); }
void host_consumer_send(uint16_t u) { consumer = u; ++consumer_reports; }
bool kb_process_record(uint16_t k, bool pressed) {
    if (k >= SAFE_RANGE) { custom_presses += pressed; return false; }
    return true;
}
bool layout_process_record(uint16_t k, bool pressed) { (void)k; (void)pressed; return true; }
void indicators_pwm_disable(void) {}
void indicators_pwm_enable(void) {}
void user_matrix_sinks_off(void) {}
void user_matrix_scan_pre(void) {}
void user_matrix_cols_deselect_all(void) {}
void user_matrix_col_select(uint8_t c) { (void)c; }
void user_matrix_col_deselect(uint8_t c) { (void)c; }
uint8_t user_matrix_read_rows(void) { return 0xff; }
void user_matrix_scan_post(void) {}
void delay_us(uint16_t us) { (void)us; }
void sleep_note_activity(void) {}

#define HAS_KEY(k) is_key_pressed(&keyboard_report, (k))
static void edge(uint8_t row, uint8_t col, bool down) {
    if (down) matrix[col] |= (uint8_t)(1u << row);
    else matrix[col] &= (uint8_t)~(1u << row);
    matrix_updated = true;
    assert(matrix_task());
    static const uint8_t colours[] = {RK61_COLOUR_NORMAL, RK61_COLOUR_GREEN,
        RK61_COLOUR_BLUE, RK61_COLOUR_MAGENTA, RK61_COLOUR_YELLOW};
    assert(get_action_layer() < sizeof(colours));
    assert(rk61_led_override_colour() == colours[get_action_layer()]);
}
static uint8_t layer_col(unsigned layer) { return layer == 1 ? 2 : layer == 2 ? 8 : 10; }
static void reset(void) {
    matrix_init();
    memset(&keyboard_report, 0, sizeof(keyboard_report));
    memset(&last_report, 0, sizeof(last_report));
    memset(&nkro_report, 0, sizeof(nkro_report));
    memset(&last_nkro_report, 0, sizeof(last_nkro_report));
    clear_mods();
    sent_mods = consumer = reports = consumer_reports = custom_presses = 0;
}
static void base_remap(void) {
    reset();
    edge(4, 1, true); assert(sent_mods == MOD_BIT(KC_LALT));
    edge(4, 1, false); assert(!sent_mods);
    edge(4, 9, true); assert(sent_mods == MOD_BIT(KC_LGUI));
    edge(4, 9, false); assert(!sent_mods);
    edge(4, 10, true); assert(action_layer == RK61_LAYER_3 && !sent_mods);
    edge(4, 10, false); assert(!action_layer);
}
static void disabled_keys(void) {
    for (unsigned layer = 1; layer <= 3; ++layer) {
        reset();
        edge(4, layer_col(layer), true);
        assert(action_layer == layer);
        for (uint8_t r = 0; r < 5; ++r) {
            for (uint8_t c = 0; c < 14; ++c) {
                if (keymaps[layer][r][c] != KC_NO) continue;
                edge(r, c, true);
                edge(r, c, false);
            }
        }
        assert(!reports && !consumer_reports && !custom_presses);
        edge(4, layer_col(layer), false);
        assert(!action_layer);
    }
}
static void navigation(void) {
    static const uint8_t arrows[] = { KC_LEFT, KC_DOWN, KC_UP, KC_RGHT };
    reset();
    edge(4, 2, true);
    for (unsigned i = 0; i < 10; ++i) {
        uint8_t digit = i == 9 ? KC_0 : KC_1 + i;
        edge(1, 1 + i, true); assert(HAS_KEY(digit)); edge(1, 1 + i, false); assert(!HAS_KEY(digit));
        edge(3, 1 + i, true); assert(HAS_KEY(KC_F1 + i)); edge(3, 1 + i, false);
    }
    edge(4, 0, true); // Control+Shift+arrow remains usable for selection.
    edge(3, 0, true);
    for (unsigned i = 0; i < 4; ++i) {
        edge(2, 6 + i, true);
        assert(HAS_KEY(arrows[i]) && sent_mods == (MOD_BIT(KC_LCTL) | MOD_BIT(KC_LSFT)));
        edge(2, 6 + i, false);
    }
    edge(3, 0, false); edge(4, 0, false); edge(4, 2, false);
    assert(!sent_mods);
}
static void symbols(void) {
    static const uint8_t plain[] = { KC_MINS, KC_EQL, KC_LBRC, KC_RBRC, KC_BSLS, KC_GRV };
    reset();
    edge(4, 8, true);
    for (unsigned i = 0; i < 10; ++i) {
        uint8_t digit = i == 9 ? KC_0 : KC_1 + i;
        edge(1, 1 + i, true);
        assert(HAS_KEY(digit) && sent_mods == MOD_BIT(KC_LSFT));
        edge(1, 1 + i, false);
        assert(!HAS_KEY(digit) && !sent_mods);
    }
    for (unsigned i = 0; i < 6; ++i) {
        edge(2, 6 + i, true); assert(HAS_KEY(plain[i]) && !sent_mods); edge(2, 6 + i, false);
        if (i < 5) {
            edge(3, 6 + i, true); assert(HAS_KEY(plain[i]) && sent_mods == MOD_BIT(KC_LSFT));
            edge(3, 6 + i, false); assert(!sent_mods);
        }
    }
    edge(4, 8, false);
}
static void overlapping_symbols(void) {
    reset();
    edge(4, 8, true);
    edge(1, 1, true); // !
    edge(1, 2, true); // @
    edge(1, 1, false);
    assert(!HAS_KEY(KC_1) && HAS_KEY(KC_2) && sent_mods == MOD_BIT(KC_LSFT));
    edge(3, 0, true); // physical left Shift, separate from the synthetic one
    edge(3, 13, true); // physical right Shift too
    edge(4, 8, false);
    edge(1, 2, false); // release @ after leaving layer
    assert(!HAS_KEY(KC_2) && sent_mods == (MOD_BIT(KC_LSFT) | MOD_BIT(KC_RSFT)));
    edge(3, 0, false); assert(sent_mods == MOD_BIT(KC_RSFT));
    edge(3, 13, false); assert(!sent_mods && !get_weak_mods());

    reset();
    edge(4, 8, true); edge(1, 1, true); edge(3, 0, true);
    edge(3, 0, false); // releasing physical Shift must not remove the symbol's Shift
    assert(sent_mods == MOD_BIT(KC_LSFT));
    edge(1, 1, false); edge(4, 8, false); assert(!sent_mods);
}
static void shared_usage(void) {
    for (unsigned release_symbol_first = 0; release_symbol_first < 2; ++release_symbol_first) {
        reset();
        edge(0, 1, true); // base 1
        edge(4, 8, true); edge(1, 1, true); // ! uses the same keyboard usage
        assert(HAS_KEY(KC_1) && sent_mods == MOD_BIT(KC_LSFT));
        edge(release_symbol_first ? 1 : 0, 1, false);
        assert(HAS_KEY(KC_1));
        assert(sent_mods == (release_symbol_first ? 0 : MOD_BIT(KC_LSFT)));
        edge(release_symbol_first ? 0 : 1, 1, false);
        edge(4, 8, false);
        assert(!HAS_KEY(KC_1) && !sent_mods);
    }
}
static void essential_keys(void) {
    static const uint8_t rows[] = {0, 2, 4, 3, 3, 4, 4, 4};
    static const uint8_t cols[] = {13, 13, 5, 0, 13, 0, 1, 9};
    for (unsigned layer = 1; layer <= 3; ++layer) {
        for (unsigned i = 0; i < sizeof(rows); ++i) {
            reset();
            edge(4, layer_col(layer), true);
            edge(rows[i], cols[i], true);
            assert(reports == 1); // explicitly mapped keys, not fallthrough
            edge(rows[i], cols[i], false);
            assert(reports == 2 && !sent_mods);
            edge(4, layer_col(layer), false);
        }
    }
}
static void releases_across_layers(void) {
    reset();
    edge(2, 1, true); edge(4, 1, true);
    edge(4, 2, true);
    assert(HAS_KEY(KC_A) && sent_mods == MOD_BIT(KC_LALT));
    edge(2, 1, false); edge(4, 1, false);
    assert(!HAS_KEY(KC_A) && !sent_mods);
    edge(4, 2, false);
    reset();
    edge(4, 8, true); edge(2, 1, true); // A is OFF
    edge(4, 8, false); edge(2, 1, false);
    assert(!reports && !HAS_KEY(KC_A));
}
static void overlapping_layers(void) {
    for (unsigned a = 1; a <= 3; ++a) {
        for (unsigned b = 1; b <= 3; ++b) {
            if (a == b) continue;
            reset();
            edge(4, layer_col(a), true); edge(4, layer_col(b), true);
            assert(action_layer == (a > b ? a : b));
            edge(4, layer_col(a), false); assert(action_layer == b);
            edge(4, layer_col(b), false); assert(!action_layer);
        }
    }
    reset();
    edge(4, 2, true); edge(4, 8, true);
    assert(action_layer == RK61_LAYER_2); // no automatic tri-layer
    edge(4, 10, true); edge(4, 13, true);
    assert(action_layer == RK61_FN);
    edge(4, 13, false); assert(action_layer == RK61_LAYER_3);
    edge(4, 10, false); assert(action_layer == RK61_LAYER_2);
    edge(4, 8, false); assert(action_layer == RK61_LAYER_1);
    edge(4, 2, false); assert(!action_layer);
}
static void media_and_screenshot(void) {
    static const uint8_t rows[] = {1, 1, 2, 2, 2, 2, 3};
    static const uint8_t cols[] = {1, 2, 6, 7, 8, 4, 4};
    static const uint16_t usages[] = {0xea, 0xe9, 0xb6, 0xb5, 0xcd, 0x6f, 0x70};
    for (unsigned i = 0; i < sizeof(rows); ++i) {
        reset();
        edge(4, 10, true); edge(rows[i], cols[i], true);
        assert(consumer_reports == 1 && consumer == usages[i] && !reports);
        edge(4, 10, false); // release must still stop the media usage
        edge(rows[i], cols[i], false);
        assert(consumer_reports == 2 && !consumer && !reports);
    }
    reset();
    edge(4, 10, true); edge(1, 6, true);
    assert(HAS_KEY(KC_PSCR) && !consumer_reports);
    edge(4, 10, false); assert(HAS_KEY(KC_PSCR));
    edge(1, 6, false); assert(!HAS_KEY(KC_PSCR));
    edge(4, 10, true); edge(1, 0, true); edge(1, 0, false);
    edge(1, 3, true); edge(1, 3, false); edge(4, 10, false);
    assert(custom_presses == 2); // existing lighting handlers receive Tab/E
}
static void fn_still_works(void) {
    reset();
    edge(4, 13, true); edge(2, 1, true); assert(HAS_KEY(KC_LEFT));
    edge(4, 13, false); assert(HAS_KEY(KC_LEFT));
    edge(2, 1, false); assert(!HAS_KEY(KC_LEFT) && !HAS_KEY(KC_A));
    edge(4, 13, true); edge(1, 1, true); edge(4, 13, false); edge(1, 1, false);
    assert(custom_presses == 1 && !HAS_KEY(KC_Q));
    edge(4, 13, true); edge(3, 0, true); edge(0, 0, true);
    assert(HAS_KEY(KC_GRV) && sent_mods == MOD_BIT(KC_LSFT)); // tilde
    edge(0, 0, false); edge(3, 0, false); edge(4, 13, false);
}
int main(void) {
    for (unsigned protocol = 0; protocol < 2; ++protocol) {
        use_nkro = protocol != 0;
        base_remap(); disabled_keys(); navigation(); symbols(); overlapping_symbols();
        shared_usage(); essential_keys(); releases_across_layers(); overlapping_layers();
        media_and_screenshot(); fn_still_works();
    }
    puts("PASS: three layers, symbols/modifier overlap, media usages, screenshot, Fn; 6KRO + NKRO");
}
'''


class KeymapHostChecks(unittest.TestCase):
    def test_real_keymap_matrix_and_reports(self):
        with tempfile.TemporaryDirectory(prefix="rk61-keymap-") as temp:
            directory = Path(temp)
            (directory / "mock.h").write_text(MOCK)
            # GCC C lacks SDCC's fixed-underlying-enum syntax. Preserve all values.
            keycodes = (SMK / "keycodes.h").read_text()
            (directory / "keycodes.h").write_text(
                keycodes.replace("enum qk_keycode_ranges : uint16_t {", "enum qk_keycode_ranges {")
            )
            for name in ["matrix.h", "layout.h", "user_layout.h", "kb.h", "user_matrix.h",
                         "kbdef.h", "host.h", "delay.h", "indicators.h", "sleep.h"]:
                (directory / name).write_text('#include "mock.h"\n')
            (directory / "debug.h").write_text('#define dprintf(...) ((void)0)\n')
            # Verbatim copies let quoted includes find the hardware/transport mocks.
            for name in ["matrix.c", "report.c", "report.h"]:
                (directory / name).write_text((SMK / name).read_text())
            (directory / "test.c").write_text(HARNESS.replace("LAYOUT_PATH", str(LAYOUT / "layout.c"))
                                        .replace("POLICY_PATH", str(LAYOUT / "lighting.c")))
            subprocess.run(["cc", "-std=c11", "-fgnu89-inline", "-DNKRO_ENABLE",
                            "-Wall", "-Wextra", "-Werror", "-I", temp, "-I", str(LAYOUT.parent.parent),
                            str(directory / "test.c"), "-o", str(directory / "test")], check=True)
            subprocess.run([str(directory / "test")], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
