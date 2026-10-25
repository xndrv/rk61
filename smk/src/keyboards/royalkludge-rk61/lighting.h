#pragma once

#include <stdint.h>

enum rk61_led_colour {
    RK61_COLOUR_WHITE,
    RK61_COLOUR_GREEN,
    RK61_COLOUR_RED,
    RK61_COLOUR_BLUE,
    RK61_COLOUR_YELLOW,
    RK61_COLOUR_CYAN,
    RK61_COLOUR_MAGENTA,
    RK61_COLOUR_ORANGE,
    RK61_COLOUR_VIOLET,
    RK61_COLOUR_TEAL, // connection indicator; not part of the normal colour cycle
    RK61_COLOUR_COUNT,
};

#define RK61_COLOUR_NORMAL      255u
#define RK61_COLOUR_CYCLE_COUNT RK61_COLOUR_TEAL
// Raw PWM counts, not an 8-bit RGB scale. This is still an experimental ceiling.
// Main lighting boots at 64; active battery segments use the status maximum.
#define RK61_LED_MAX_PULSE       256u
#define RK61_LED_DEFAULT_PULSE   64u
#define RK61_LED_STATUS_PULSE    RK61_LED_MAX_PULSE
#define RK61_LED_BRIGHTNESS_STEP 16u
#define RK61_LED_EMPTY_PULSE     8u

// One atomic byte publishes the gauge to the LED ISR: count 1..5 and low flag.
// Zero means unknown, not discharged. Unavailable is the physical power-off
// state, not a measurement. Earlier diagnostics disable the override.
#define RK61_BATTERY_UNKNOWN     0u
#define RK61_BATTERY_UNAVAILABLE 0x40u
#define RK61_BATTERY_LOW         0x80u
#define RK61_BATTERY_COUNT       0x07u
#define RK61_STATUS_FRAMES       32u // approximate half-second; scan-timed, not a wall clock

// Called by the LED ISR: return NORMAL to use the user's selected base colour.
uint8_t rk61_led_override_colour(void);
// Fixed colour of a physical bottom-row layer key; NORMAL leaves it unchanged.
// These keys follow ordinary brightness/toggle, unlike the battery indicators.
uint8_t rk61_led_layer_key_colour(uint8_t column);
// NORMAL disables all five status keys (earlier diagnostic layouts).
uint8_t rk61_led_connection_colour(void);
uint8_t rk61_led_battery_state(void);
// Atomic scan-derived epoch; advances even with ordinary lighting at zero.
uint8_t rk61_led_status_clock(void);
