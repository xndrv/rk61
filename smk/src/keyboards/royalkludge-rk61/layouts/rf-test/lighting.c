#include "lighting.h"
#include "layout.h"
#include "keymap.h"

uint8_t rk61_led_layer_key_colour(uint8_t column)
{
    // Physical bottom row: Ctrl, Alt, L1, Space, L2, Win, L3, Fn.
    // Matrix columns come from RK61_LAYOUT_ANSI; this is independent of holds.
    switch (column) {
        case 2:
            return RK61_COLOUR_GREEN;
        case 8:
            return RK61_COLOUR_BLUE;
        case 10:
            return RK61_COLOUR_MAGENTA;
        case 13:
            return RK61_COLOUR_YELLOW;
        default:
            return RK61_COLOUR_NORMAL;
    }
}

uint8_t rk61_led_override_colour(void)
{
    switch (get_action_layer()) {
        case RK61_LAYER_1:
            return RK61_COLOUR_GREEN;
        case RK61_LAYER_2:
            return RK61_COLOUR_BLUE;
        case RK61_LAYER_3:
            return RK61_COLOUR_MAGENTA;
        case RK61_FN:
            return RK61_COLOUR_YELLOW;
        default:
            return RK61_COLOUR_NORMAL;
    }
}
