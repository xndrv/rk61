#include "lighting.h"
#include "layout.h"
#include "keymap.h"

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
