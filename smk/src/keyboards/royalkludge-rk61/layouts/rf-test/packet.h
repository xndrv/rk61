#pragma once
#include <stdint.h>
#include <stdbool.h>

uint8_t rk61_packet_command(uint8_t out[32], uint8_t command, uint8_t a, uint8_t b);
void    rk61_packet_keyboard(uint8_t out[32], uint8_t mods, const uint8_t *keys, const uint8_t *bits);
void    rk61_packet_extra(uint8_t out[32], uint16_t consumer, uint16_t system_usage);
bool    rk61_packet_status_valid(const uint8_t response[4]);
