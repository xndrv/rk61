#include "kbdef.h"
#include "user_init.h"

void user_init(void)
{
    // Prototype: leave unported LED/radio/control pins high-impedance.
    // This is not a replacement for mapping their actual enable/power signals.
    P0CR = P1CR = P2CR = P3CR = P4CR = P5CR = P6CR = P7CR = 0;
    P0PCR = P1PCR = P2PCR = P3PCR = P4PCR = P5PCR = P6PCR = P7PCR = 0;

    // Load idle-high latches BEFORE enabling the verified matrix outputs.
    P6 = 0xFF;
    P5 |= 0x87;
    P4 |= 0x05;

    P7PCR |= 0x0E; // rows P7.1..3
    P5PCR |= 0x18; // rows P5.3..4
    P6CR = 0xFF;
    P5CR |= 0x87;
    P4CR |= 0x05;
}
