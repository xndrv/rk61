#include "kbdef.h"
#include "radio.h"
#include "usb.h"
#include "report.h"
#include "host.h"
#include "debug.h"
#include "lighting.h"

// Stock 0x7C43..0x7CE8: P5.6 high selects wired; otherwise P5.5 high
// selects Bluetooth and low selects dongle. Hardware switch polarity still needs
// confirmation on the owner's board. Power-off + USB should read wired.
// Fn+Q/W/E (also B/N/M) select BT slots; R/T force dongle/wired.
// A stable physical switch change cancels the temporary manual override.
#define SWITCH_STABLE_SAMPLES 256u
static bool     radio_mode;
static uint8_t  radio_link; // 0=dongle, 1..3=Bluetooth
static uint16_t mode_debounce;
static uint8_t  physical_state;
static uint8_t  candidate_state;
static uint8_t  last_bt_slot;
// Retain the latest early report, including releases; do not replay startup taps.
static uint8_t                   usb_pending_kind;
static __xdata report_keyboard_t usb_pending_keyboard;
static __xdata report_nkro_t     usb_pending_nkro;
static uint16_t                  usb_consumer_usage, usb_system_usage;
static uint8_t                   usb_extra_pending;
static __xdata report_extra_t    usb_pending_extra;
// Published atomically for the five-key LED gauge; selected route, not link confirmation.
static volatile uint8_t          connection_colour;
static __xdata report_keyboard_t blank_keyboard;
static __xdata report_nkro_t     blank_nkro;

static void set_mode(bool wireless, uint8_t link)
{
    if (link > 3 || (radio_mode == wireless && (!wireless || radio_link == link))) {
        return;
    }
    // Stop media/system holds on the old route before selecting a new host.
    host_consumer_send(0);
    host_system_send(0);
    if (radio_mode) {
        rk61_radio_release();
    } else {
        blank_nkro.report_id = REPORT_ID_NKRO;
        usb_send_report(&blank_keyboard);
        usb_send_nkro(&blank_nkro);
    }
    usb_pending_kind   = 0;
    usb_extra_pending  = 0;
    usb_consumer_usage = usb_system_usage = 0;

    radio_mode        = wireless;
    radio_link        = wireless ? link : 0;
    connection_colour = wireless ? (link ? RK61_COLOUR_TEAL : RK61_COLOUR_ORANGE) : RK61_COLOUR_MAGENTA;
    if (wireless && link) {
        last_bt_slot = link;
    }
    if (wireless) {
        rk61_radio_select_link(link, false);
    } else {
        rk61_radio_select(false);
    }
}

uint8_t rk61_led_connection_colour(void)
{
    return connection_colour;
}

static uint8_t read_switches(void)
{
    return (uint8_t)((P5_6 ? 2u : 0u) | (P5_5 ? 1u : 0u));
}

static void apply_physical_mode(void)
{
    if (physical_state & 2u) {
        set_mode(false, 0);
    } else {
        set_mode(true, (physical_state & 1u) ? last_bt_slot : 0);
    }
}

void kb_init(void)
{
    rk61_radio_init();
    radio_mode         = false;
    radio_link         = 0;
    last_bt_slot       = 1; // RAM-only preference; do not alter the radio's bonds.
    connection_colour  = RK61_COLOUR_MAGENTA;
    mode_debounce      = 0;
    physical_state     = read_switches();
    candidate_state    = physical_state;
    usb_pending_kind   = 0;
    usb_extra_pending  = 0;
    usb_consumer_usage = usb_system_usage = 0;
    apply_physical_mode();
    if (!radio_mode) rk61_radio_select(false);
}

void kb_update_switches(void)
{
    const uint8_t sample = read_switches();
    if (sample == physical_state) {
        candidate_state = sample;
        mode_debounce   = 0;
    } else if (sample != candidate_state) {
        candidate_state = sample;
        mode_debounce   = 1;
    } else if (++mode_debounce >= SWITCH_STABLE_SAMPLES) {
        physical_state = sample;
        mode_debounce  = 0;
        apply_physical_mode();
    }
    // Unchanged switches never undo an explicit Fn choice or restart pairing.
}

bool kb_process_record(uint16_t keycode, bool pressed)
{
    switch (keycode) {
        case RK61_RF_24G:
        case RK61_USB_MODE:
            if (pressed) {
                set_mode(keycode == RK61_RF_24G, 0);
            }
            return false;
        case RK61_BT1:
        case RK61_BT2:
        case RK61_BT3:
            if (pressed) {
                set_mode(true, (uint8_t)(keycode - RK61_BT1 + 1));
            }
            return false;
        case RK61_BT_PAIR:
            if (pressed && radio_mode && radio_link >= 1 && radio_link <= 3) {
                host_consumer_send(0);
                host_system_send(0);
                rk61_radio_release();
                rk61_radio_select_link(radio_link, true);
            }
            return false;
        case RK61_RF_STATUS:
            if (pressed) {
                rk61_radio_status();
            }
            return false;
        default:
            return true; // LED keys are handled by layout_process_record
    }
}

void kb_update(void)
{
    rk61_radio_task(); // also completes deferred USB-mode notification
    if (!radio_mode && usb_is_configured()) {
        if (usb_pending_kind == 1 && !(EP1CON & _IEP1RDY)) {
            usb_send_report(&usb_pending_keyboard);
            usb_pending_kind = 0;
        }
        if (usb_pending_kind == 2 && !(EP2CON & _IEP2RDY)) {
            usb_send_nkro(&usb_pending_nkro);
            usb_pending_kind = 0;
        }
        if (usb_extra_pending && !(EP2CON & _IEP2RDY)) {
            const bool consumer         = usb_extra_pending & 1u;
            usb_pending_extra.report_id = consumer ? REPORT_ID_CONSUMER : REPORT_ID_SYSTEM;
            usb_pending_extra.usage     = consumer ? usb_consumer_usage : usb_system_usage;
            usb_send_extra(&usb_pending_extra);
            usb_extra_pending &= consumer ? (uint8_t)~1u : (uint8_t)~2u;
        }
    }
    rk61_radio_battery_task(); // battery sensing continues in wired mode too
}

void kb_send_report(__xdata report_keyboard_t *report)
{
    if (radio_mode) {
        rk61_radio_keyboard(report);
    } else {
        if (!usb_is_configured() || usb_pending_kind) {
            usb_pending_keyboard = *report;
            usb_pending_kind     = 1;
        } else {
            usb_send_report(report);
        }
    }
}

void kb_send_nkro(__xdata report_nkro_t *report)
{
    if (radio_mode) {
        rk61_radio_nkro(report);
    } else {
        if (!usb_is_configured() || usb_pending_kind) {
            usb_pending_nkro = *report;
            usb_pending_kind = 2;
        } else {
            usb_send_nkro(report);
        }
    }
}

void kb_send_extra(__xdata report_extra_t *report)
{
    if (radio_mode) {
        rk61_radio_extra(report);
    } else {
        if (usb_is_configured()) {
            usb_send_extra(report);
            usb_extra_pending &= report->report_id == REPORT_ID_CONSUMER ? (uint8_t)~1u : (uint8_t)~2u;
            return;
        }
        if (report->report_id == REPORT_ID_CONSUMER) {
            usb_consumer_usage = report->usage;
            usb_extra_pending |= 1;
        } else {
            usb_system_usage = report->usage;
            usb_extra_pending |= 2;
        }
    }
}
