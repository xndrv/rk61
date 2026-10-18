"""Linked LED checks and real driver/policy execution with mock registers."""

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_prototype as prototype

ROOT = Path(__file__).resolve().parent
BOARD = ROOT / "smk/src/keyboards/royalkludge-rk61"
STEM = "royalkludge-rk61_led-test_smk"


class LedImageChecks(prototype.PrototypeChecks):
    LED_TOGGLE_LAYER = None
    LED_TOGGLE_POSITION = (1, 1)
    LED_CYCLE_POSITION = (1, 3)

    def led_toggle_keycode(self):
        layer = self.FN_LAYER if self.LED_TOGGLE_LAYER is None else self.LED_TOGGLE_LAYER
        return self.key(layer, *self.LED_TOGGLE_POSITION)

    @classmethod
    def setUpClass(cls):
        cls.image = prototype.load_hex(prototype.BUILD / f"{STEM}.hex")
        cls.mapping = json.loads((ROOT / "matrix.json").read_text())
        cls.linkmap = (prototype.BUILD / f"{STEM}.map").read_text()

    def test_interrupt_check_passed(self):
        self.assertTrue((prototype.BUILD / "royalkludge-rk61_led-test_smk.interrupts-ok").is_file())

    def test_led_shortcuts(self):
        toggle = self.led_toggle_keycode()
        channel = self.key(self.FN_LAYER, *self.LED_CYCLE_POSITION)
        self.assertGreaterEqual(toggle, 0x7E00)
        self.assertEqual(channel, toggle + 1)


class LedDriverChecks(unittest.TestCase):
    def test_real_driver_and_layer_policy_with_mock_registers(self):
        header = (ROOT / "smk/src/sino51lib/sh68f90/sh68f90.h").read_text()
        names = re.findall(r"^SFRX?\((\w+),", header, re.M)
        declarations = [f"#define {name} mock_regs[{i}]" for i, name in enumerate(names)]
        mock = "\n".join([
            "#pragma once", "#include <stdint.h>", "#include <stdbool.h>",
            "extern volatile uint8_t mock_regs[512];", *declarations,
            "#define MATRIX_COLS 14", "#define DRVCON_UNLOCK_P1 5",
            "#define DRVCON_UNLOCK_P2 0x45", "#define DRVCON_UNLOCK_P3 0x85",
            "#define DRVCON_LOCK 0", "#define GPIO_DRIVE_25MA 0",
            "enum { RK61_LED_TOGGLE = 0x7e00, RK61_LED_CHANNEL,",
            "       RK61_LED_BRIGHTNESS_DOWN = 0x7e09, RK61_LED_BRIGHTNESS_UP };",
            "typedef struct { uint8_t unused; } keyboard_state_t;",
            "uint8_t get_action_layer(void);",
            "void user_matrix_cols_deselect_all(void);",
            "void user_matrix_col_select(uint8_t col);",
        ]) + "\n"
        harness = r'''
#include <assert.h>
#include <stdio.h>
#include "mock.h"
volatile uint8_t mock_regs[512];
static int selected = -1;
static uint8_t held_layer, expected_col;
static uint8_t connection = 255;
static uint8_t battery_display = 5;
uint8_t rk61_led_battery_state(void) { return battery_display; }
uint8_t get_action_layer(void) { return held_layer; }
uint8_t rk61_led_connection_colour(void) { return connection; }
void user_matrix_cols_deselect_all(void) { selected = -1; }
void user_matrix_col_select(uint8_t col) {
    assert(selected == -1 && col < MATRIX_COLS);
    selected = col;
}
#include "POLICY_PATH"
#include "DRIVER_PATH"
static unsigned duty(uint8_t hi, uint8_t lo) { return ((unsigned)hi << 8) | lo; }
static void check_duties(unsigned g, unsigned r, unsigned b,
                         unsigned sg, unsigned sr, unsigned sb, bool status_here) {
    const unsigned normal[] = {g, r, b}, status[] = {sg, sr, sb};
    unsigned brightness = g > r ? g : r;
    if (b > brightness) brightness = b;
    unsigned bottom[] = {g, r, b};
    // Independent physical position/channel expectations, not the policy hook.
    switch (expected_col) {
        case 2:  bottom[0] = brightness; bottom[1] = 0; bottom[2] = 0; break;
        case 8:  bottom[0] = 0; bottom[1] = 0; bottom[2] = brightness; break;
        case 10: bottom[0] = 0; bottom[1] = brightness; bottom[2] = brightness; break;
        case 13: bottom[0] = brightness; bottom[1] = brightness; bottom[2] = 0; break;
    }
#define CHECK(channel, off, group, populated, row) \
    assert(duty(channel##DUTY1H, channel##DUTY1L) == (off)); \
    assert(duty(channel##DUTY2H, channel##DUTY2L) == (off) + \
        ((populated) ? (((row) == 0 && status_here) ? status[group] : (row) == 4 ? bottom[group] : normal[group]) : 0)); \
    assert(duty(channel##DUTY2H, channel##DUTY2L) - (off) <= 256); \
    assert(duty(channel##DUTY2H, channel##DUTY2L) < 0x0537);
    LED_CHANNELS(CHECK)
#undef CHECK
    // Check the physical bottom-row bank independently of row annotations,
    // including columns 8/10/13 where no battery override is present.
    assert(duty(PWM00DUTY2H, PWM00DUTY2L) == 0x35 + bottom[0]);
    assert(duty(PWM01DUTY2H, PWM01DUTY2L) == 0x36 + bottom[1]);
    assert(duty(PWM02DUTY2H, PWM02DUTY2L) == 0x37 + bottom[2]);
    // Check the Esc bank independently of the driver's row annotations, so a
    // mistaken annotation cannot make both production and the test agree.
    if (status_here) {
        assert(duty(PWM23DUTY2H, PWM23DUTY2L) == 0x29 + sg);
        assert(duty(PWM24DUTY2H, PWM24DUTY2L) == 0x2a + sr);
        assert(duty(PWM25DUTY2H, PWM25DUTY2L) == 0x2b + sb);
#define NORMAL_ROW(cg, cr, cb, og, or_, ob) \
        assert(duty(cg##DUTY2H, cg##DUTY2L) == (og) + g); \
        assert(duty(cr##DUTY2H, cr##DUTY2L) == (or_) + r); \
        assert(duty(cb##DUTY2H, cb##DUTY2L) == (ob) + b);
        NORMAL_ROW(PWM03, PWM04, PWM05, 0x32, 0x33, 0x34)
        NORMAL_ROW(PWM10, PWM11, PWM12, 0x2c, 0x2d, 0x2e)
        NORMAL_ROW(PWM13, PWM14, PWM15, 0x2f, 0x30, 0x31)
#undef NORMAL_ROW
    }
}
static void check_parked(void) {
    assert(selected == -1);
#define CHECK_PARK(channel, off, group, populated, row) assert(channel##CON == 0x12);
    LED_CHANNELS(CHECK_PARK)
#undef CHECK_PARK
}
static void check_frame(unsigned g, unsigned r, unsigned b,
                         unsigned sg, unsigned sr, unsigned sb, bool indicator) {
    for (unsigned slot = 0; slot < 14; ++slot) {
        const unsigned phase = rk61_led_status_clock() & 1;
        assert(indicators_update_step(0, 0) == (expected_col == 13));
        bool status_here = indicator && expected_col < 5;
        unsigned eg = sg, er = sr, eb = sb;
        if (status_here) {
            if (!battery_display && expected_col) {
                eg = er = eb = phase ? 0 : 8;
            } else if (battery_display && expected_col >= (battery_display & 7)) {
                eg = er = eb = 8;
            } else if ((battery_display & 0x80) && !expected_col && phase) {
                eg = er = eb = 0;
            }
        }
        if (g || r || b || status_here) {
            assert(selected == expected_col);
            assert(PWM00CON == 0x8a && PWM10CON == 0x8a && PWM20CON == 0x8a);
        } else {
            check_parked();
        }
        check_duties(g, r, b, eg, er, eb, status_here);
        expected_col = (expected_col + 1) % 14;
    }
}
static void frame(unsigned g, unsigned r, unsigned b) {
    check_frame(g, r, b, 0, 0, 0, false);
}
static void press(uint16_t code) {
    assert(!layout_process_record(code, true));
    assert(!layout_process_record(code, false));
}
static void boot(void) {
    indicators_init(); expected_col = 0;
    indicators_start();
}
static void zero(void) {
    for (unsigned i = 0; i < 20; ++i) press(RK61_LED_BRIGHTNESS_DOWN);
}
int main(void) {
    // Only the four physical layer keys get a permanent colour recipe.
    for (unsigned col = 0; col < 14; ++col) {
        unsigned colour = col == 2 ? RK61_COLOUR_GREEN : col == 8 ? RK61_COLOUR_BLUE
                        : col == 10 ? RK61_COLOUR_MAGENTA : col == 13 ? RK61_COLOUR_YELLOW
                        : RK61_COLOUR_NORMAL;
        assert(rk61_led_layer_key_colour(col) == colour);
    }
    assert(rk61_led_layer_key_colour(255) == RK61_COLOUR_NORMAL);
    held_layer = RK61_LAYER_1;
    connection = RK61_COLOUR_TEAL;
    indicators_init();
    check_duties(0, 0, 0, 0, 0, 0, false);
    indicators_update_step(0, 0); // neither layer nor Esc may light before start
    check_parked();
    assert(PWM0PERDH == 5 && PWM0PERDL == 0x37);
    assert(PWM1PERDH == 5 && PWM1PERDL == 0x37);
    assert(PWM2PERDH == 5 && PWM2PERDL == 0x37);
    held_layer = RK61_BASE; connection = RK61_COLOUR_NORMAL;
    boot(); frame(64, 64, 64); // boot at tested v3 brightness, not trial maximum
    indicators_pwm_disable(); check_parked();
    indicators_pwm_enable(); check_parked(); // no stale sink after a scan

    // Releases must not change settings.
    assert(!layout_process_record(RK61_LED_TOGGLE, false));
    assert(!layout_process_record(RK61_LED_CHANNEL, false));
    assert(!layout_process_record(RK61_LED_BRIGHTNESS_DOWN, false));
    assert(!layout_process_record(RK61_LED_BRIGHTNESS_UP, false));
    frame(64, 64, 64);

    // Cross the old 8-bit boundary explicitly: 240 -> 256, saturation, and
    // restoring 256 after zero must never wrap/truncate to zero.
    for (unsigned i = 0; i < 11; ++i) press(RK61_LED_BRIGHTNESS_UP);
    frame(240, 240, 240);
    press(RK61_LED_BRIGHTNESS_UP); frame(256, 256, 256);
    press(RK61_LED_BRIGHTNESS_UP); frame(256, 256, 256);
    press(RK61_LED_TOGGLE); frame(0, 0, 0);
    press(RK61_LED_TOGGLE); frame(256, 256, 256);
    press(RK61_LED_BRIGHTNESS_DOWN); frame(240, 240, 240);

    // Independent expected G/R/B values at 64 counts; teal is status-only.
    static const uint8_t colours[][3] = {
        {64,64,64}, {64,0,0}, {0,64,0}, {0,0,64}, {64,64,0},
        {64,0,64}, {0,64,64}, {16,64,0}, {0,32,64}
    };
    assert(RK61_COLOUR_CYCLE_COUNT == sizeof(colours) / sizeof(colours[0]));
    for (unsigned colour = 0; colour < 9; ++colour) {
        for (unsigned i = 0; i < 20; ++i) press(RK61_LED_BRIGHTNESS_UP);
        for (int step = 16; step >= 0; --step) {
            unsigned b = (unsigned)step * 16;
            held_layer = RK61_BASE;
            frame(colours[colour][0] * step / 4, colours[colour][1] * step / 4,
                  colours[colour][2] * step / 4);
            held_layer = RK61_LAYER_1; frame(b, 0, 0);
            held_layer = RK61_LAYER_2; frame(0, 0, b);
            held_layer = RK61_LAYER_3; frame(0, b, b);
            held_layer = RK61_FN; frame(b, b, 0);
            held_layer = RK61_BASE;
            press(RK61_LED_BRIGHTNESS_DOWN);
        }
        zero(); frame(0, 0, 0); // minimum is true zero; no separate enabled flag
        press(RK61_LED_BRIGHTNESS_UP);
        frame(colours[colour][0] / 4, colours[colour][1] / 4, colours[colour][2] / 4);
        press(RK61_LED_TOGGLE); frame(0, 0, 0);
        press(RK61_LED_TOGGLE);
        frame(colours[colour][0] / 4, colours[colour][1] / 4, colours[colour][2] / 4);
        press(RK61_LED_CHANNEL);
    }
    frame(16, 16, 16); // palette wraps to white, never through status-only teal

    boot(); held_layer = RK61_FN;
    press(RK61_LED_CHANNEL); frame(64, 64, 0);
    press(RK61_LED_BRIGHTNESS_DOWN); frame(48, 48, 0);
    held_layer = RK61_BASE; frame(48, 0, 0);
    press(RK61_LED_TOGGLE); frame(0, 0, 0);
    press(RK61_LED_CHANNEL); // selected red while brightness is zero
    press(RK61_LED_TOGGLE); frame(0, 48, 0); // restore last nonzero level
    zero(); frame(0, 0, 0);
    press(RK61_LED_BRIGHTNESS_UP); frame(0, 16, 0); // knob alone turns it back on
    held_layer = 250; frame(0, 16, 0); // unknown layer falls back to normal colour

    // Battery indicators occupy row 0 / columns 0..4 ONLY. Bottom-row layer
    // keys keep their own colours; all other pixels keep the layer lighting.
    static const uint8_t modes[] = { RK61_COLOUR_TEAL, RK61_COLOUR_ORANGE, RK61_COLOUR_MAGENTA };
    static const uint8_t status_weights[][3] = { {4,0,2}, {1,4,0}, {0,4,4} };
    for (unsigned mode = 0; mode < 3; ++mode) {
        held_layer = RK61_BASE; connection = modes[mode]; boot();
        check_frame(64,64,64,64 * status_weights[mode][0],
                    64 * status_weights[mode][1],64 * status_weights[mode][2],true);
        zero();
        for (unsigned step = 0; step <= 16; ++step) {
            unsigned b = step * 16, sb = 256; // Esc stays at max at EVERY main level
            unsigned sg = sb * status_weights[mode][0] / 4;
            unsigned sr = sb * status_weights[mode][1] / 4;
            unsigned blue = sb * status_weights[mode][2] / 4;
            held_layer = RK61_BASE; check_frame(b,b,b,sg,sr,blue,true);
            held_layer = RK61_LAYER_1; check_frame(b,0,0,sg,sr,blue,true);
            held_layer = RK61_LAYER_2; check_frame(0,0,b,sg,sr,blue,true);
            held_layer = RK61_LAYER_3; check_frame(0,b,b,sg,sr,blue,true);
            held_layer = RK61_FN; check_frame(b,b,0,sg,sr,blue,true);
            press(RK61_LED_BRIGHTNESS_UP);
        }
        // Capped at 256 even after repeated increases; Esc ignores main toggle.
        for (unsigned i = 0; i < 20; ++i) press(RK61_LED_BRIGHTNESS_UP);
        held_layer = RK61_BASE;
        check_frame(256,256,256,64 * status_weights[mode][0],
                    64 * status_weights[mode][1],64 * status_weights[mode][2],true);
        press(RK61_LED_TOGGLE);
        check_frame(0,0,0,64 * status_weights[mode][0],
                    64 * status_weights[mode][1],64 * status_weights[mode][2],true);
        press(RK61_LED_TOGGLE);
        check_frame(256,256,256,64 * status_weights[mode][0],
                    64 * status_weights[mode][1],64 * status_weights[mode][2],true);
    }
    // Every gauge state, mode, background level and held layer. Run long enough
    // to cover both blink phases; compare physical PWM banks independently.
    static const uint8_t states[] = {0, 1, 2, 3, 4, 5, 0x81};
    for (unsigned mode = 0; mode < 3; ++mode) {
        connection = modes[mode];
        for (unsigned state = 0; state < sizeof(states); ++state) {
            battery_display = states[state];
            boot();
            assert(rk61_led_status_clock() == 0);
            for (unsigned step = 0; step <= 16; ++step) {
                zero();
                for (unsigned i = 0; i < step; ++i) press(RK61_LED_BRIGHTNESS_UP);
                unsigned b = step * 16;
                for (unsigned repeat = 0; repeat < 8; ++repeat) {
                    held_layer = RK61_BASE;
                    check_frame(b,b,b,64 * status_weights[mode][0],64 * status_weights[mode][1],64 * status_weights[mode][2],true);
                    held_layer = RK61_LAYER_1;
                    check_frame(b,0,0,64 * status_weights[mode][0],64 * status_weights[mode][1],64 * status_weights[mode][2],true);
                    held_layer = RK61_LAYER_2;
                    check_frame(0,0,b,64 * status_weights[mode][0],64 * status_weights[mode][1],64 * status_weights[mode][2],true);
                    held_layer = RK61_LAYER_3;
                    check_frame(0,b,b,64 * status_weights[mode][0],64 * status_weights[mode][1],64 * status_weights[mode][2],true);
                    held_layer = RK61_FN;
                    check_frame(b,b,0,64 * status_weights[mode][0],64 * status_weights[mode][1],64 * status_weights[mode][2],true);
                }
            }
            assert(rk61_led_status_clock() == (17 * 8 * 5) / 32);
        }
    }
    // Clock is driven by scans, not main-loop speed or keyboard activity.
    connection = RK61_COLOUR_NORMAL; held_layer = RK61_BASE; boot(); zero();
    for (unsigned i = 0; i < 32 * 257; ++i) frame(0,0,0);
    assert(rk61_led_status_clock() == 1); // atomic byte wrap
    connection = RK61_COLOUR_NORMAL; zero(); frame(0,0,0); // diagnostic: all off
    boot(); frame(64,64,64);
    assert(layout_process_record(4, true));
    puts("PASS: fixed layer-key colours at zero..256/all palettes/layers, battery states/modes, blink/unknown, clock/wrap, clamp/blanking");
}
'''.replace("DRIVER_PATH", str(BOARD / "layouts/led-test/indicators.c")).replace(
            "POLICY_PATH", str(BOARD / "layouts/rf-test/lighting.c"))
        with tempfile.TemporaryDirectory(prefix="rk61-led-unit-") as temp:
            directory = Path(temp)
            (directory / "mock.h").write_text(mock)
            for name in ["kbdef.h", "indicators.h", "user_layout.h", "user_matrix.h", "layout.h"]:
                (directory / name).write_text('#include "mock.h"\n')
            (directory / "pwm_hw.h").write_text("#pragma once\n")
            (directory / "test.c").write_text(harness)
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-value",
                            "-I", temp, "-I", str(BOARD), "-I", str(ROOT / "smk/src/sino51lib"),
                            str(directory / "test.c"), "-o", str(directory / "test")], check=True)
            subprocess.run([str(directory / "test")], check=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
