#pragma once
#include <stdint.h>

typedef enum {
    SYSTICK_SLOT_MATRIX_SCAN,
    SYSTICK_SLOT_LED_SUBFRAME,
} systick_slot_t;

void systick_init(void);
void systick_arm(systick_slot_t slot);

void systick_pause(void);
void systick_resume(void);

// SH68F90: conservative elapsed timer time; ISR/dispatch overhead is excluded.
// Wraps at 65536 ms. Available without USB and independent of LED brightness.
uint16_t systick_millis(void);
