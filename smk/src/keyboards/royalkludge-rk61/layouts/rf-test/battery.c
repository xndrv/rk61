#include "battery.h"
#include "packet.h"
#include "lighting.h"

// Stock 0x962D..0x96D2 constructs this code; 0x7BE8..0x7C31 blinks below 3.
// Upper bands are provisional raw-code bands, NOT calibrated state-of-charge
// percentages. Do not assume either code 10 or the field maximum 15 means full.
static volatile uint8_t display_state;
static uint8_t          last_valid;
static uint8_t          candidate;
static uint8_t          confirmations;

void rk61_battery_init(uint8_t now)
{
    display_state = RK61_BATTERY_UNKNOWN;
    last_valid    = now;
    candidate     = RK61_BATTERY_UNKNOWN;
    confirmations = 0;
}

uint8_t rk61_led_battery_state(void)
{
    return display_state;
}

void rk61_battery_set_available(bool available, uint8_t now)
{
    if (!available) {
        display_state = RK61_BATTERY_UNAVAILABLE;
        confirmations = 0;
    } else if (display_state == RK61_BATTERY_UNAVAILABLE) {
        // Do not resurrect a pre-switch reading or partial confirmation.
        rk61_battery_init(now);
    }
}

void rk61_battery_expire(uint8_t now)
{
    if (display_state == RK61_BATTERY_UNAVAILABLE) return;
    if ((uint8_t)(now - last_valid) >= RK61_BATTERY_STALE_EPOCHS) {
        display_state = RK61_BATTERY_UNKNOWN;
        confirmations = 0;
    }
}

void rk61_battery_observe(const uint8_t response[4], uint8_t now)
{
    if (display_state == RK61_BATTERY_UNAVAILABLE) return;
    rk61_battery_expire(now);
    const uint8_t code = rk61_packet_battery_code(response);
    if (code == 255u) {
        confirmations = 0; // bad frames neither refresh age nor confirm a change
        return;
    }
    last_valid          = now;
    const uint8_t state = code < 3u ? (RK61_BATTERY_LOW | 1u) : code < 5u ? 2u : code < 7u ? 3u : code < 9u ? 4u : 5u;
    // First reading and stock low warning are immediate. Other transitions,
    // including recovery from low, require three consecutive same-band replies.
    if (display_state == RK61_BATTERY_UNKNOWN || (state & RK61_BATTERY_LOW)) {
        display_state = state;
        confirmations = 0;
    } else if (state == display_state) {
        confirmations = 0;
    } else {
        if (candidate != state || !confirmations) {
            candidate     = state;
            confirmations = 0;
        }
        if (++confirmations >= RK61_BATTERY_CONFIRM) {
            display_state = state;
            confirmations = 0;
        }
    }
}
