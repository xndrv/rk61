#include "report.h"
#include "usb.h"
#include "lighting.h"

// Earlier wired/LED diagnostic layouts have no per-layer colour overrides.
uint8_t rk61_led_override_colour(void)
{
    return RK61_COLOUR_NORMAL;
}

uint8_t rk61_led_connection_colour(void)
{
    return RK61_COLOUR_NORMAL;
}

void kb_send_report(__xdata report_keyboard_t *report)
{
    usb_send_report(report);
}

void kb_send_nkro(__xdata report_nkro_t *report)
{
    usb_send_nkro(report);
}

void kb_send_extra(__xdata report_extra_t *report)
{
    usb_send_extra(report);
}
