#pragma once

// FN remains separate from the three Corne-inspired user layers.
enum rk61_layers {
    RK61_BASE,
    RK61_LAYER_1,
    RK61_LAYER_2,
    RK61_LAYER_3,
    RK61_FN,
};

// Physical ANSI order: 14 / 14 / 13 / 12 / 8 keys, left to right.
// Hide the electrical holes; they must always remain KC_NO.
#define RK61_LAYOUT_ANSI(K00, K01, K02, K03, K04, K05, K06, K07, K08, K09, K0A, K0B, K0C, K0D, K10, K11, K12, K13, K14, K15, K16, K17, K18, K19, K1A, K1B, K1C, K1D, K20, K21, K22, K23, K24, K25, K26, K27, K28, K29, K2A, K2B, K2D, K30, K31, K32, K33, K34, K35, K36, K37, K38, K39, K3A, K3D, K40, K41, K42, K45, K48, K49, K4A, K4D) \
    {                                                                                                                                                                                                                                                                                                                                     \
        {K00, K01, K02, K03, K04, K05, K06, K07, K08, K09, K0A, K0B, K0C, K0D}, {K10, K11, K12, K13, K14, K15, K16, K17, K18, K19, K1A, K1B, K1C, K1D}, {K20, K21, K22, K23, K24, K25, K26, K27, K28, K29, K2A, K2B, KC_NO, K2D}, {K30, K31, K32, K33, K34, K35, K36, K37, K38, K39, K3A, KC_NO, KC_NO, K3D},                             \
        {                                                                                                                                                                                                                                                                                                                                 \
            K40, K41, K42, KC_NO, KC_NO, K45, KC_NO, KC_NO, K48, K49, K4A, KC_NO, KC_NO, K4D                                                                                                                                                                                                                                              \
        }                                                                                                                                                                                                                                                                                                                                 \
    }
