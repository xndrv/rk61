#include "kbdef.h"
#include "indicators.h"
#include "pwm.h"
#include "user_layout.h"
#include "user_matrix.h"
#include "lighting.h"

// Stock period/off points/drive/blanking are unchanged. Main lighting boots at
// 64 counts; the 256-count ceiling and five status keys need hardware validation.
_Static_assert(RK61_LED_BRIGHTNESS_STEP == 16u, "brightness levels use a four-bit shift");
_Static_assert(RK61_LED_MAX_PULSE % RK61_LED_BRIGHTNESS_STEP == 0u, "whole brightness levels required");
_Static_assert(RK61_LED_MAX_PULSE / RK61_LED_BRIGHTNESS_STEP <= 255u, "level must fit an atomic byte");
#define LED_PARKED (PWM_MOD | PWM_CLK_DIV_4)

// Weights 0/1/2/4 mean off / quarter / half / full selected brightness.
// Hardware channel order is GREEN, RED, BLUE (confirmed on this board).
static const uint8_t colour_weights[RK61_COLOUR_COUNT][3] = {
    {4, 4, 4}, // white
    {4, 0, 0}, // green
    {0, 4, 0}, // red
    {0, 0, 4}, // blue
    {4, 4, 0}, // yellow
    {4, 0, 4}, // cyan
    {0, 4, 4}, // magenta
    {1, 4, 0}, // orange (unmeasured colour mix)
    {0, 2, 4}, // violet (unmeasured colour mix)
    {4, 0, 2}, // teal connection indicator (unmeasured colour mix)
};

// PWM channel, stock off point, G/R/B group, populated, matrix LED row.
// Stock 0x5BFC loads original row 1 into PWM23/24/25: ANSI row 0 (Esc).
// The original extra row (PWM20..22) stays off; its row value is a sentinel.
#define LED_ACTIVE_CHANNELS(X) \
    X(PWM00, 0x35u, 0, 1, 4)   \
    X(PWM01, 0x36u, 1, 1, 4)   \
    X(PWM02, 0x37u, 2, 1, 4)   \
    X(PWM03, 0x32u, 0, 1, 3)   \
    X(PWM04, 0x33u, 1, 1, 3)   \
    X(PWM05, 0x34u, 2, 1, 3)   \
    X(PWM10, 0x2Cu, 0, 1, 1)   \
    X(PWM11, 0x2Du, 1, 1, 1)   \
    X(PWM12, 0x2Eu, 2, 1, 1)   \
    X(PWM13, 0x2Fu, 0, 1, 2)   \
    X(PWM14, 0x30u, 1, 1, 2)   \
    X(PWM15, 0x31u, 2, 1, 2)   \
    X(PWM23, 0x29u, 0, 1, 0)   \
    X(PWM24, 0x2Au, 1, 1, 0)   \
    X(PWM25, 0x2Bu, 2, 1, 0)

#define LED_CHANNELS(X)      \
    LED_ACTIVE_CHANNELS(X)   \
    X(PWM20, 0x26u, 0, 0, 5) \
    X(PWM21, 0x27u, 1, 0, 5) \
    X(PWM22, 0x28u, 2, 0, 5)

static volatile uint8_t led_started;
static volatile uint8_t led_colour;
// Store 0..16 levels in one byte: atomic main-loop writes / LED ISR reads on
// this 8-bit MCU. Convert to 16-bit PWM counts only inside the ISR.
static volatile uint8_t led_brightness_level;
static uint8_t          restore_brightness_level;
static uint8_t          led_col;
static uint8_t          status_frames;
static volatile uint8_t status_clock;

uint8_t rk61_led_status_clock(void)
{
    return status_clock;
}

void indicators_pwm_disable(void)
{
#define PARK(channel, off, group, populated, row) channel##CON = LED_PARKED;
    LED_CHANNELS(PARK)
#undef PARK
    user_matrix_cols_deselect_all();
}

// matrix_scan_full calls this after scanning. Leave everything blank until the
// next LED slot selects exactly one column; do not restore the previous sink.
void indicators_pwm_enable(void) {}

void indicators_init(void)
{
    led_started              = 0;
    led_colour               = RK61_COLOUR_WHITE;
    led_brightness_level     = RK61_LED_DEFAULT_PULSE / RK61_LED_BRIGHTNESS_STEP;
    restore_brightness_level = led_brightness_level;
    led_col                  = 0;
    status_frames            = 0;
    status_clock             = 0;
    indicators_pwm_disable();

    // These PWM-source pins are outputs with low idle latches in stock 0xA829.
    P1 &= (uint8_t)~0x38u;
    P2 &= (uint8_t)~0x3Fu;
    P3 &= (uint8_t)~0x3Fu;
    P1PCR &= (uint8_t)~0x38u;
    P2PCR &= (uint8_t)~0x3Fu;
    P3PCR &= (uint8_t)~0x3Fu;
    DRVCON = DRVCON_UNLOCK_P1;
    P1DRV  = GPIO_DRIVE_25MA;
    DRVCON = DRVCON_UNLOCK_P2;
    P2DRV  = GPIO_DRIVE_25MA;
    DRVCON = DRVCON_UNLOCK_P3;
    P3DRV  = GPIO_DRIVE_25MA;
    DRVCON = DRVCON_LOCK;
    P1CR |= 0x38u;
    P2CR |= 0x3Fu;
    P3CR |= 0x3Fu;

    PWM0PERDH = PWM1PERDH = PWM2PERDH = 0x05;
    PWM0PERDL = PWM1PERDL = PWM2PERDL = 0x37;
#define INIT(channel, off, group, populated, row) SET_PWM_DUTY(channel, off, off);
    LED_CHANNELS(INIT)
#undef INIT
}

void indicators_start(void)
{
    led_started = 1;
}

static uint16_t colour_pulse(uint8_t colour, uint8_t group, uint16_t brightness)
{
    if (colour >= RK61_COLOUR_COUNT) {
        return 0;
    }
    const uint8_t weight = colour_weights[colour][group];
    // Shifts only: no multiplication/division helper in the LED ISR.
    return weight == 4 ? brightness : weight == 2 ? brightness >> 1 : weight == 1 ? brightness >> 2 : 0;
}

bool indicators_update_step(keyboard_state_t *keyboard, uint8_t current_step)
{
    keyboard;
    current_step;
    indicators_pwm_disable();
    if (led_started) {
        const uint8_t  override          = rk61_led_override_colour();
        const uint8_t  colour            = override < RK61_COLOUR_COUNT ? override : led_colour;
        const uint8_t  layer_key_colour  = rk61_led_layer_key_colour(led_col);
        uint8_t        status_colour     = rk61_led_connection_colour();
        const uint8_t  battery           = rk61_led_battery_state();
        // Unavailable sensing leaves keys 1..4 in the normal layer/base
        // lighting, including ordinary brightness/toggle. Esc keeps its route.
        const bool     status_here       = led_col < 5 && status_colour < RK61_COLOUR_COUNT && (battery != RK61_BATTERY_UNAVAILABLE || !led_col);
        const uint16_t brightness        = (uint16_t)led_brightness_level << 4;
        uint16_t       status_brightness = RK61_LED_STATUS_PULSE;
        if (status_here && battery != RK61_BATTERY_UNAVAILABLE) {
            if (battery == RK61_BATTERY_UNKNOWN) {
                // Keep Esc's route visible; pulse the other four neutral keys.
                if (led_col) {
                    status_colour     = RK61_COLOUR_WHITE;
                    status_brightness = (status_clock & 1u) ? 0 : RK61_LED_EMPTY_PULSE;
                }
            } else if (led_col >= (battery & RK61_BATTERY_COUNT)) {
                status_colour     = RK61_COLOUR_WHITE;
                status_brightness = RK61_LED_EMPTY_PULSE;
            } else if ((battery & RK61_BATTERY_LOW) && !led_col && (status_clock & 1u)) {
                status_brightness = 0; // deliberate low-battery blink, not blocking
            }
        }
        // Index 0 is background, 1 is row 0 (battery), 2 is row 4 (layer keys).
        // Constant row indices keep the other rows in each column unchanged.
        uint16_t pulses[3][3];
        for (uint8_t group = 0; group < 3; group++) {
            pulses[0][group] = colour_pulse(colour, group, brightness);
            pulses[1][group] = status_here ? colour_pulse(status_colour, group, status_brightness) : pulses[0][group];
            pulses[2][group] = layer_key_colour < RK61_COLOUR_COUNT ? colour_pulse(layer_key_colour, group, brightness) : pulses[0][group];
        }
#define PAINT(channel, off, group, populated, row) SET_PWM_DUTY_2(channel, (uint16_t)((off) + pulses[((row) == 0) + 2 * ((row) == 4)][group]));
        LED_ACTIVE_CHANNELS(PAINT)
#undef PAINT
        if (brightness || status_here) {
            user_matrix_col_select(led_col);
            // Stock bank control: no PWM IRQ; SMK's timer schedules the slots.
#define ARM(channel, off, group, populated, row) channel##CON = PWM_SS;
            LED_CHANNELS(ARM)
#undef ARM
            PWM00CON = (uint8_t)(PWM_MODE_ENABLE | PWM_SS | PWM_CLK_DIV_4);
            PWM10CON = (uint8_t)(PWM_MODE_ENABLE | PWM_SS | PWM_CLK_DIV_4);
            PWM20CON = (uint8_t)(PWM_MODE_ENABLE | PWM_SS | PWM_CLK_DIV_4);
        }
    }
    if (++led_col == MATRIX_COLS) {
        led_col = 0;
        if (led_started && ++status_frames == RK61_STATUS_FRAMES) {
            status_frames = 0;
            ++status_clock;
        }
        return true;
    }
    return false;
}

static void set_brightness_level(uint8_t level)
{
    led_brightness_level = level;
    if (level) {
        restore_brightness_level = level;
    }
}

bool layout_process_record(uint16_t keycode, bool pressed)
{
    switch (keycode) {
        case RK61_LED_TOGGLE:
            if (pressed) {
                set_brightness_level(led_brightness_level ? 0 : restore_brightness_level);
            }
            return false;
        case RK61_LED_CHANNEL:
            if (pressed) {
                const uint8_t next = (uint8_t)(led_colour + 1);
                led_colour         = next < RK61_COLOUR_CYCLE_COUNT ? next : RK61_COLOUR_WHITE;
            }
            return false;
        case RK61_LED_BRIGHTNESS_DOWN:
            if (pressed && led_brightness_level) {
                set_brightness_level((uint8_t)(led_brightness_level - 1));
            }
            return false;
        case RK61_LED_BRIGHTNESS_UP:
            if (pressed && led_brightness_level < RK61_LED_MAX_PULSE / RK61_LED_BRIGHTNESS_STEP) {
                set_brightness_level((uint8_t)(led_brightness_level + 1));
            }
            return false;
        default:
            return true;
    }
}
