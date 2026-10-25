#include "kbdef.h"
#include "radio.h"
#include "packet.h"
#include "delay.h"
#include "systick.h"
#include "debug.h"
#include "battery.h"
#include "lighting.h"

// Derived from stock 0x8BF6/0xAD80 (TX), 0x962D/0xAA99 (RX).
// P0.2 wake; P7.5 select; P4.7 clock; P0.4 MOSI; P0.3 MISO; P4.1 ACK.
static uint8_t tx[32];
static uint8_t pending[32];
static uint8_t pending_tries;
static uint8_t response[4];
static uint8_t last_status_poll;

// Main-loop state machine: no radio traffic before the boot allowance expires.
#define RADIO_BOOT_MS        1500u
#define RADIO_COMMAND_GAP_MS 20u
enum {
    SELECT_IDLE,
    SELECT_WAKE,
    SELECT_LINK,
    SELECT_REPEAT,
    SELECT_STATUS
};
static bool     boot_ready;
static uint16_t boot_since, stage_since;
static uint8_t  select_stage, selected_link;
static bool     selected_wireless, selected_pairing;
static uint16_t consumer_usage, system_usage;
static bool     extra_pending;

static bool link_ready(void)
{
    return boot_ready && select_stage == SELECT_IDLE;
}

static void bus_release(void)
{
    P4_7 = 1;
    P7_5 = 1;
    P0_2 = 1;
    P0_4 = 1;
    P4CR &= (uint8_t)~0x80u;
    P7CR &= (uint8_t)~0x20u;
    P0CR &= (uint8_t)~0x14u;
}

static void bus_begin(bool sending)
{
    P4_7 = 1;
    P7_5 = 1;
    P0_2 = 1;
    P0_4 = 1;
    P4CR |= 0x80;
    P7CR |= 0x20;
    P0CR |= sending ? 0x14 : 0x04;
    P0_2 = 0;
    delay_us(3);
}

static void write_byte(uint8_t value)
{
    for (uint8_t bit = 0; bit < 8; ++bit) {
        P4_7 = 0;
        delay_us(2);
        P0_4 = (value & 0x80u) != 0;
        P4_7 = 1;
        delay_us(2);
        value <<= 1;
    }
    P0_4 = 1;
}

static uint8_t read_byte(void)
{
    uint8_t value = 0;
    for (uint8_t bit = 0; bit < 8; ++bit) {
        P4_7 = 0;
        delay_us(2);
        value = (uint8_t)((value << 1) | (P0_3 ? 1 : 0));
        P4_7  = 1;
        delay_us(2);
    }
    return value;
}

static bool transmit(const uint8_t *data, uint8_t length)
{
    bus_begin(true);
    const bool ack = P4_1;
    P7_5           = 0;
    delay_us(53);
    for (uint8_t i = 0; i < length; ++i) {
        write_byte(data[i]);
    }
    bus_release();
    for (uint8_t tries = 0; tries < 50; ++tries) {
        if ((bool)P4_1 != ack) {
            return true;
        }
        delay_us(30);
    }
    return false;
}

static bool command(uint8_t cmd, uint8_t a, uint8_t b)
{
    rk61_packet_command(tx, cmd, a, b);
    return transmit(tx, 6);
}

static bool query_status(void)
{
    const bool ack = command(0x0A, 0, 0);
    delay_us(223);
    __critical
    {
        bus_begin(false);
        P7_5 = 0;
        delay_us(3);
        for (uint8_t i = 0; i < 4; ++i) {
            response[i] = read_byte();
        }
        bus_release();
    }
    last_status_poll = rk61_led_status_clock();
    // The owner gets valid replies with ack=0. Trust header/checksum, not ACK.
    rk61_battery_observe(response, last_status_poll);
    return ack;
}

void rk61_radio_status(void)
{
    if (!link_ready()) {
        return;
    }
    const bool ack = query_status();
    dprintf("RF ack=%u rx=%02x %02x %02x %02x valid=%u P55=%u P56=%u battery_code=%u\r\n", (unsigned)ack, (unsigned)response[0], (unsigned)response[1], (unsigned)response[2], (unsigned)response[3], (unsigned)rk61_packet_status_valid(response), (unsigned)P5_5, (unsigned)P5_6, (unsigned)rk61_packet_battery_code(response));
    ack; // dprintf is a no-op in release builds
}

void rk61_radio_init(void)
{
    P0CR &= (uint8_t)~0x08u; // MISO input
    P4CR &= (uint8_t)~0x02u; // ACK input
    P5CR &= (uint8_t)~0x60u; // stock switch/USB-detect inputs
    P5PCR |= 0x60;
    bus_release();
    pending_tries    = 0;
    last_status_poll = rk61_led_status_clock();
    rk61_battery_init(last_status_poll);
    boot_ready     = false;
    boot_since     = systick_millis();
    select_stage   = SELECT_IDLE;
    consumer_usage = system_usage = 0;
    extra_pending                 = false;
}

void rk61_radio_select_link(uint8_t link, bool pairing)
{
    // Stock 0xA249: link 0 = dongle, links 1..3 = Bluetooth slots.
    // Pairing is explicit and Bluetooth-only; never re-pair the working dongle.
    if (link > 3 || (pairing && link == 0)) {
        return;
    }
    pending_tries  = 0;
    consumer_usage = system_usage = 0;
    extra_pending                 = false;
    selected_wireless             = true;
    selected_link                 = link;
    selected_pairing              = pairing;
    select_stage                  = SELECT_WAKE;
}

void rk61_radio_select(bool wireless)
{
    if (wireless) {
        rk61_radio_select_link(0, false);
    } else {
        pending_tries  = 0;
        consumer_usage = system_usage = 0;
        extra_pending                 = false;
        selected_wireless             = false;
        selected_pairing              = false;
        select_stage                  = SELECT_WAKE;
    }
}

// At most one command per main-loop pass. A new selection replaces any staged
// old selection, including an explicit pairing request that has not yet sent.
static void select_task(uint16_t now)
{
    switch (select_stage) {
        case SELECT_WAKE:
            command(selected_wireless ? 0x0C : 6, selected_wireless ? 0 : 1, 0);
            stage_since  = systick_millis();
            select_stage = selected_wireless ? SELECT_LINK : SELECT_STATUS;
            break;
        case SELECT_LINK:
            if ((uint16_t)(now - stage_since) < RADIO_COMMAND_GAP_MS) return;
            command(1, selected_pairing ? 1 : 0, selected_link);
            stage_since  = systick_millis();
            select_stage = selected_pairing ? SELECT_STATUS : SELECT_REPEAT;
            break;
        case SELECT_REPEAT:
            if ((uint16_t)(now - stage_since) < RADIO_COMMAND_GAP_MS) return;
            command(1, 0, selected_link);
            select_stage = SELECT_STATUS;
            break;
        case SELECT_STATUS:
            query_status();
            select_stage = SELECT_IDLE;
            break;
    }
}

static void queue_keyboard(uint8_t mods, const uint8_t *keys, const uint8_t *bits)
{
    rk61_packet_keyboard(pending, mods, keys, bits);
    pending_tries = 3;
}

void rk61_radio_task(void)
{
    const uint16_t now = systick_millis();
    if (!boot_ready) {
        if ((uint16_t)(now - boot_since) < RADIO_BOOT_MS) return;
        boot_ready = true;
    }
    if (select_stage != SELECT_IDLE) {
        select_task(now);
        return;
    }
    if (extra_pending) {
        rk61_packet_extra(tx, consumer_usage, system_usage);
        transmit(tx, 14);
        extra_pending = false;
        return;
    }
    if (pending_tries) {
        --pending_tries;
        if (transmit(pending, 32)) {
            pending_tries = 0;
        }
    }
}

void rk61_radio_battery_task(void)
{
    const uint8_t now = rk61_led_status_clock();
    rk61_battery_expire(now);
    if (!link_ready()) return;
    if (!pending_tries && (uint8_t)(now - last_status_poll) >= RK61_BATTERY_POLL_EPOCHS) {
        // Bounded existing bus transaction, in the main loop only. No wake,
        // route reassertion, pairing or debug spam in the periodic path.
        query_status();
    }
}

void rk61_radio_keyboard(__xdata report_keyboard_t *report)
{
    queue_keyboard(report->mods, report->keys, 0);
}

void rk61_radio_nkro(__xdata report_nkro_t *report)
{
    queue_keyboard(report->mods, 0, report->bits);
}

void rk61_radio_extra(__xdata report_extra_t *report)
{
    if (report->report_id == REPORT_ID_CONSUMER) {
        consumer_usage = report->usage;
    } else {
        system_usage = report->usage;
    }
    extra_pending = true;
    if (link_ready()) {
        rk61_packet_extra(tx, consumer_usage, system_usage);
        transmit(tx, 14);
        extra_pending = false;
    }
}

void rk61_radio_release(void)
{
    queue_keyboard(0, 0, 0);
    // Never advance a deferred selection while releasing the old route.
    if (link_ready()) {
        transmit(pending, 32);
        pending_tries = 0;
    }
}
