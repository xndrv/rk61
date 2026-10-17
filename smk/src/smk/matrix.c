#include "matrix.h"
#include "report.h"
#include "debug.h"
#include "layout.h"
#include "user_layout.h"
#include "kb.h"
#include "user_matrix.h"
#include "kbdef.h"
#include "host.h"
#include "delay.h"
#include "indicators.h"
#include "sleep.h"
#include <stdlib.h>
#include <stdbool.h>

typedef uint8_t matrix_col_t;

matrix_col_t matrix[MATRIX_COLS];
matrix_col_t matrix_previous[MATRIX_COLS];

volatile bool matrix_updated;

// Read by the LED ISR; publish layer changes in one atomic byte write.
volatile uint8_t action_layer;

uint8_t default_layer;

// A release must undo the action chosen at key-down, even after a layer change.
static __xdata uint16_t held_actions[MATRIX_ROWS][MATRIX_COLS];

void matrix_init()
{
    action_layer   = 0;
    default_layer  = 0;
    matrix_updated = false;
    set_weak_mods(0);

    for (int i = 0; i < MATRIX_COLS; i++) {
        matrix[i]          = 0;
        matrix_previous[i] = 0;
        for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
            held_actions[row][i] = KC_NO;
        }
    }
}

void set_default_layer(uint8_t layer)
{
    default_layer = layer;
}

uint8_t get_action_layer(void)
{
    return action_layer;
}

static uint16_t resolve_keycode(uint16_t base, uint8_t row, uint8_t col)
{
    if (!action_layer) {
        return base;
    }

    const uint16_t overlay = keymaps[action_layer][row][col];
    return (overlay == KC_TRANSPARENT) ? base : overlay;
}

static void update_weak_mods(void)
{
    uint8_t mods = 0;
    for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
        for (uint8_t col = 0; col < MATRIX_COLS; col++) {
            const uint16_t action = held_actions[row][col];
            if (IS_QK_MODS(action)) {
                const uint8_t encoded = QK_MODS_GET_MODS(action);
                // QMK-style encoding: four modifier bits + right-hand flag.
                mods |= (uint8_t)((encoded & 0x0F) << ((encoded & 0x10) ? 4 : 0));
            }
        }
    }
    set_weak_mods(mods);
}

static bool keycode_still_held(uint16_t keycode)
{
    // E.g. base 1 and layer ! share a usage. Releasing one must keep the other.
    for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
        for (uint8_t col = 0; col < MATRIX_COLS; col++) {
            uint16_t action = held_actions[row][col];
            if (IS_QK_MODS(action)) {
                action = QK_MODS_GET_BASIC_KEYCODE(action);
            }
            if (action == keycode) {
                return true;
            }
        }
    }
    return false;
}

static void send_keycode(uint16_t qcode, bool pressed)
{
    if (IS_QK_MODS(qcode)) {
        // Recompute the union so overlapping shifted symbols don't release Shift
        // early, and never remove a separately held physical Shift modifier.
        update_weak_mods();
        qcode = QK_MODS_GET_BASIC_KEYCODE(qcode);
    }
    if (IS_MODIFIER_KEYCODE(qcode)) {
        if (pressed) {
            add_mods(MOD_BIT((uint8_t)(qcode & 0xFF)));
        } else if (!keycode_still_held(qcode)) {
            del_mods(MOD_BIT((uint8_t)(qcode & 0xFF)));
        }
        send_keyboard_report();
        return;
    }

    if (IS_BASIC_KEYCODE(qcode)) {
        if (pressed) {
            add_key((uint8_t)(qcode & 0xFF));
        } else if (!keycode_still_held(qcode)) {
            del_key((uint8_t)(qcode & 0xFF));
        }
        send_keyboard_report();
        return;
    }

    if (IS_SYSTEM_KEYCODE(qcode)) {
        host_system_send(pressed ? keycode_to_system(qcode) : 0);
        return;
    }

    if (IS_CONSUMER_KEYCODE(qcode)) {
        host_consumer_send(pressed ? keycode_to_consumer(qcode) : 0);
        return;
    }
}

static void update_action_layer(void)
{
    // Highest numbered held layer wins. Releasing it restores any lower one.
    uint8_t selected_layer = 0;
    for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
        for (uint8_t col = 0; col < MATRIX_COLS; col++) {
            const uint16_t action = held_actions[row][col];
            if (IS_QK_MOMENTARY(action)) {
                const uint8_t layer = QK_MOMENTARY_GET_LAYER(action);
                if (layer > selected_layer) {
                    selected_layer = layer;
                }
            }
        }
    }
    action_layer = selected_layer;
}

static void process_key_state(uint8_t row, uint8_t col, bool pressed)
{
    uint16_t qcode;
    if (pressed) {
        const uint16_t base = keymaps[default_layer][row][col];
        // Base layer controls remain available even on an otherwise empty layer.
        qcode                  = IS_QK_MOMENTARY(base) ? base : resolve_keycode(base, row, col);
        held_actions[row][col] = qcode;
    } else {
        qcode                  = held_actions[row][col];
        held_actions[row][col] = KC_NO;
    }

    if (IS_QK_MOMENTARY(qcode)) {
        update_action_layer();
        return;
    }

    if (!kb_process_record(qcode, pressed)) {
        return;
    }

    if (!layout_process_record(qcode, pressed)) {
        return;
    }

    send_keycode(qcode, pressed);
}

void matrix_scan_full(void)
{
    indicators_pwm_disable();

    user_matrix_sinks_off();

    user_matrix_scan_pre();
    user_matrix_cols_deselect_all();

    for (uint8_t col = 0; col < MATRIX_COLS; col++) {
        user_matrix_col_select(col);

        delay_us(10); // let the row lines settle before sampling
        const uint8_t sample1 = user_matrix_read_rows();
        delay_us(10);
        const uint8_t sample2 = user_matrix_read_rows();

        if (sample1 == sample2) {
            matrix[col] = ~sample1;
        }

        user_matrix_col_deselect(col);
    }

    user_matrix_scan_post();

    indicators_pwm_enable();

    matrix_updated = true;
}

uint8_t matrix_task()
{
    if (!matrix_updated) {
        return false;
    }

    // Snapshot the scan-written matrix[], then diff it against
    // matrix_previous[]. No lock needed: each column byte reads atomically, so a
    // concurrent scan lands cleanly on one side of the read - at worst a
    // transition is split across two main-loop iterations, never lost.
    matrix_col_t snapshot[MATRIX_COLS];
    matrix_updated = false;
    for (uint8_t i = 0; i < MATRIX_COLS; i++) {
        snapshot[i] = matrix[i];
    }

    bool matrix_changed = false;

    for (uint8_t col = 0; col < MATRIX_COLS; col++) {
        const matrix_col_t current_col = snapshot[col];
        const matrix_col_t col_changes = current_col ^ matrix_previous[col];
        if (!col_changes) {
            continue;
        }
        matrix_changed = true;
        sleep_note_activity(); // a key changed state; reset the inactivity timer

        matrix_col_t row_mask = 1;
        for (uint8_t row = 0; row < MATRIX_ROWS; row++, row_mask <<= 1) {
            if (col_changes & row_mask) {
                const bool key_pressed = current_col & row_mask;
                process_key_state(row, col, key_pressed);
            }
        }

        matrix_previous[col] = current_col;
    }

    return matrix_changed;
}
