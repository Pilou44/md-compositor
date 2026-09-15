#pragma once
#include <cstdint>

struct Tile {
    uint8_t data[32];

    uint8_t pixel(int x, int y, bool flip_h, bool flip_v) const {
        if (flip_h) {
            x = 7 - x;
        }
        if (flip_v) {
            y = 7 - y;
        }

        int byte_index = y * 4 + (x / 2);
        uint8_t byte = data[byte_index];
        if (x % 2 == 0) {
            return (byte >> 4) & 0x0F;
        } else {
            return byte & 0x0F;
        }
    }
};
