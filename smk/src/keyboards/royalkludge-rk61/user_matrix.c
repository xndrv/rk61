#include "kbdef.h"
#include "user_matrix.h"

void user_matrix_cols_deselect_all(void)
{
    P6 = 0xFF;
    P5 |= 0x87;
    P4 |= 0x05;
}

void user_matrix_col_select(uint8_t col)
{
    switch (col) {
        case 0:
            P6_0 = 0;
            break;
        case 1:
            P6_1 = 0;
            break;
        case 2:
            P6_2 = 0;
            break;
        case 3:
            P6_3 = 0;
            break;
        case 4:
            P6_4 = 0;
            break;
        case 5:
            P6_5 = 0;
            break;
        case 6:
            P6_6 = 0;
            break;
        case 7:
            P6_7 = 0;
            break;
        case 8:
            P5_0 = 0;
            break;
        case 9:
            P5_1 = 0;
            break;
        case 10:
            P5_2 = 0;
            break;
        case 11:
            P5_7 = 0;
            break;
        case 12:
            P4_0 = 0;
            break;
        case 13:
            P4_2 = 0;
            break;
    }
}

void user_matrix_col_deselect(uint8_t col)
{
    switch (col) {
        case 0:
            P6_0 = 1;
            break;
        case 1:
            P6_1 = 1;
            break;
        case 2:
            P6_2 = 1;
            break;
        case 3:
            P6_3 = 1;
            break;
        case 4:
            P6_4 = 1;
            break;
        case 5:
            P6_5 = 1;
            break;
        case 6:
            P6_6 = 1;
            break;
        case 7:
            P6_7 = 1;
            break;
        case 8:
            P5_0 = 1;
            break;
        case 9:
            P5_1 = 1;
            break;
        case 10:
            P5_2 = 1;
            break;
        case 11:
            P5_7 = 1;
            break;
        case 12:
            P4_0 = 1;
            break;
        case 13:
            P4_2 = 1;
            break;
    }
}

uint8_t user_matrix_read_rows(void)
{
    // SMK expects high = released and the unused row bits held high.
    return (uint8_t)(((P7 >> 1) & 0x07) | (P5 & 0x18) | 0xE0);
}
