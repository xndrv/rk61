#pragma once

#include "kbdef.h"
#include <stdbool.h>

extern const uint16_t keymaps[][MATRIX_ROWS][MATRIX_COLS];

void set_default_layer(uint8_t layer);
// Atomic snapshot of the active held overlay (0 means no held overlay).
uint8_t get_action_layer(void);
