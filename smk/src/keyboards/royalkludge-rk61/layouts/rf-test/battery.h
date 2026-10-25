#pragma once
#include <stdint.h>
#include <stdbool.h>

#define RK61_BATTERY_POLL_EPOCHS  4u
#define RK61_BATTERY_STALE_EPOCHS 40u
#define RK61_BATTERY_CONFIRM      3u

void rk61_battery_init(uint8_t now);
// Driven by the debounced physical power input, independently of output route.
void rk61_battery_set_available(bool available, uint8_t now);
void rk61_battery_observe(const uint8_t response[4], uint8_t now);
void rk61_battery_expire(uint8_t now);
