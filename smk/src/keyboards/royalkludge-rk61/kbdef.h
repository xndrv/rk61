#pragma once

#include "sh68f90.h"
#include "keycodes.h"

#define MATRIX_ROWS 5
#define MATRIX_COLS 14

// Diagnostic LED keys; the default keys-only layout does not use these.
enum rk61_keycodes {
    RK61_LED_TOGGLE = SAFE_RANGE,
    RK61_LED_CHANNEL,
    RK61_RF_24G,
    RK61_USB_MODE,
    RK61_RF_STATUS,
    RK61_BT1,
    RK61_BT2,
    RK61_BT3,
    RK61_BT_PAIR,
    RK61_LED_BRIGHTNESS_DOWN,
    RK61_LED_BRIGHTNESS_UP,
    KB_SAFE_RANGE,
};
