#pragma once
#include <stdint.h>
#include <stdbool.h>
#include "report.h"

void rk61_radio_init(void);
void rk61_radio_select(bool wireless);
void rk61_radio_select_link(uint8_t link, bool pairing);
void rk61_radio_status(void);
void rk61_radio_task(void);
void rk61_radio_keyboard(__xdata report_keyboard_t *report);
void rk61_radio_nkro(__xdata report_nkro_t *report);
void rk61_radio_extra(__xdata report_extra_t *report);
void rk61_radio_release(void);
