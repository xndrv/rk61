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
// Main lighting boots at 64; Esc always uses the maximum for its selected colour.
#define RK61_LED_MAX_PULSE       256u
#define RK61_LED_DEFAULT_PULSE   64u
#define RK61_LED_STATUS_PULSE    RK61_LED_MAX_PULSE
#define RK61_LED_BRIGHTNESS_STEP 16u

// Called by the LED ISR: return NORMAL to use the user's selected base colour.
uint8_t rk61_led_override_colour(void);
// NORMAL disables the Esc override (used by the earlier diagnostic layouts).
uint8_t rk61_led_connection_colour(void);
