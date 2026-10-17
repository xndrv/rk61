#include "kbdef.h"
#include "layout.h"
#include "keymap.h"

// Physical keyboard order. Corne-inspired bindings are documented in KEYMAP.md.
// OFF = no output; PASS = explicitly reuse BASE (Fn only, not unassigned layers).
#define OFF  KC_NO
#define PASS KC_TRNS
#define L1   MO(RK61_LAYER_1)
#define L2   MO(RK61_LAYER_2)
#define L3   MO(RK61_LAYER_3)
#define FN   MO(RK61_FN)

// clang-format off
const uint16_t keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [RK61_BASE] = RK61_LAYOUT_ANSI(
        KC_ESC,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,    KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_MINS, KC_EQL,  KC_BSPC,
        KC_TAB,  KC_Q,    KC_W,    KC_E,    KC_R,    KC_T,    KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_LBRC, KC_RBRC, KC_BSLS,
        KC_CAPS, KC_A,    KC_S,    KC_D,    KC_F,    KC_G,    KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, KC_QUOT,          KC_ENT,
        KC_LSFT, KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH,                   KC_RSFT,
        KC_LCTL, KC_LALT, L1,                      KC_SPC,                    L2,      KC_LGUI, L3,                        FN
    ),
    [RK61_LAYER_1] = RK61_LAYOUT_ANSI(
        OFF,     OFF,    OFF,    OFF,    OFF,    OFF,    OFF,     OFF,     OFF,   OFF,    OFF,    OFF,    OFF,    KC_BSPC,
        KC_TAB,  KC_1,   KC_2,   KC_3,   KC_4,   KC_5,   KC_6,    KC_7,    KC_8,  KC_9,   KC_0,   OFF,    OFF,    OFF,
        OFF,     OFF,    OFF,    OFF,    OFF,    OFF,    KC_LEFT, KC_DOWN, KC_UP, KC_RGHT, OFF,    OFF,            KC_ENT,
        KC_LSFT, KC_F1,  KC_F2,  KC_F3,  KC_F4,  KC_F5,  KC_F6,   KC_F7,   KC_F8, KC_F9,  KC_F10,                         KC_RSFT,
        KC_LCTL, KC_LALT, L1,                    KC_SPC,                    L2,    KC_LGUI, L3,                             FN
    ),
    [RK61_LAYER_2] = RK61_LAYOUT_ANSI(
        OFF,     OFF,        OFF,        OFF,        OFF,        OFF,        OFF,        OFF,        OFF,           OFF,           OFF,           OFF,    OFF,    KC_BSPC,
        KC_TAB,  LSFT(KC_1), LSFT(KC_2), LSFT(KC_3), LSFT(KC_4), LSFT(KC_5), LSFT(KC_6), LSFT(KC_7), LSFT(KC_8),    LSFT(KC_9),    LSFT(KC_0),    OFF,    OFF,    OFF,
        OFF,     OFF,        OFF,        OFF,        OFF,        OFF,        KC_MINS,    KC_EQL,     KC_LBRC,       KC_RBRC,       KC_BSLS,       KC_GRV,         KC_ENT,
        KC_LSFT, OFF,        OFF,        OFF,        OFF,        OFF,        LSFT(KC_MINS), LSFT(KC_EQL), LSFT(KC_LBRC), LSFT(KC_RBRC), LSFT(KC_BSLS),                  KC_RSFT,
        KC_LCTL, KC_LALT,    L1,                                 KC_SPC,                             L2,            KC_LGUI,       L3,                              FN
    ),
    [RK61_LAYER_3] = RK61_LAYOUT_ANSI(
        OFF,             OFF,     OFF,     OFF,              OFF,     OFF, OFF,     OFF,     OFF,     OFF, OFF, OFF, OFF, KC_BSPC,
        RK61_LED_TOGGLE, KC_VOLD, KC_VOLU, RK61_LED_CHANNEL, OFF,     OFF, KC_PSCR, OFF,     OFF,     OFF, OFF, OFF, OFF, OFF,
        OFF,             OFF,     OFF,     OFF,              KC_BRIU, OFF, KC_MPRV, KC_MNXT, KC_MPLY, OFF, OFF, OFF,      KC_ENT,
        KC_LSFT,         OFF,     OFF,     OFF,              KC_BRID, OFF, OFF,     OFF,     OFF,     OFF, OFF,           KC_RSFT,
        KC_LCTL,         KC_LALT, L1,                                KC_SPC,               L2,      KC_LGUI, L3,        FN
    ),
    [RK61_FN] = RK61_LAYOUT_ANSI(
        KC_GRV, KC_F1, KC_F2, KC_F3, KC_F4, KC_F5, KC_F6, KC_F7, KC_F8, KC_F9, KC_F10, KC_F11, KC_F12, KC_DEL,
        PASS, RK61_BT1, RK61_BT2, RK61_BT3, RK61_RF_24G, RK61_USB_MODE, RK61_RF_STATUS, PASS, PASS, PASS, RK61_BT_PAIR, RK61_LED_BRIGHTNESS_DOWN, RK61_LED_BRIGHTNESS_UP, PASS,
        PASS, KC_LEFT, KC_DOWN, KC_RGHT, PASS, PASS, PASS, PASS, PASS, PASS, PASS, PASS,      PASS,
        PASS, PASS, PASS, PASS, PASS, RK61_BT1, RK61_BT2, RK61_BT3, PASS, RK61_LED_CHANNEL, PASS, PASS,
        PASS, PASS, L1,                PASS,           L2,  PASS, L3,                      FN
    ),
};
// clang-format on
