#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <cstdint>
#include <vector>

#include "compositor/Screen.h"

Tile chequered_tile = {
    0x11, 0x11, 0x00, 0x00,
    0x11, 0x11, 0x00, 0x00,
    0x11, 0x11, 0x00, 0x00,
    0x11, 0x11, 0x00, 0x00,
    0x00, 0x00, 0x11, 0x11,
    0x00, 0x00, 0x11, 0x11,
    0x00, 0x00, 0x11, 0x11,
    0x00, 0x00, 0x11, 0x11,
};

Tile corner_tile = {
    0x11, 0x11, 0x00, 0x00,
    0x11, 0x10, 0x00, 0x00,
    0x11, 0x00, 0x00, 0x00,
    0x10, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
};

int main() {
    Plane plane_b = {};
    Plane plane_a = {};
    
    TilemapEntry chequered_entry(0, 1, false, false, false);
    for (int i = 0; i < PLANE_WIDTH; ++i) {
        for (int j = 0; j < PLANE_HEIGHT; ++j) {
            plane_b.tiles[i][j] = chequered_entry;
        }
    }

    for (int i = 0; i < PLANE_WIDTH; ++i) {
        for (int j = 0; j < PLANE_HEIGHT; ++j) {
            bool h_flip = (i % 2 == 0);
            bool v_flip = (j % 2 == 0);
            TilemapEntry corner_entry(1, 2, h_flip, v_flip, false);
            plane_a.tiles[i][j] = corner_entry;
        }
    }

    Color black = {0, 0, 0};
    Color white = {255, 255, 255};
    Color red = {255, 0, 0};
    Color blue = {0, 0, 255};
    Color green = {0, 255, 0};
    Color yellow = {255, 255, 0};

    Palette palette0 = { black, red, red, red, red, red, red, red, red, red, red, red, red, red, red };
    Palette palette1 = { white, green, green, green, green, green, green, green, green, green, green, green, green, green, green };
    Palette palette2 = { blue, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow, yellow };

    Screen screen = {
        .tiles = { chequered_tile, corner_tile },
        .plane_a = plane_a,
        .plane_b = plane_b,
        .backdrop = black,
        .palettes = { palette0, palette1, palette2 }
    };

    const int W = PLANE_WIDTH * 8, H = PLANE_HEIGHT * 8;
    std::vector<uint8_t> rgb(W * H * 3);

    for (int x = 0; x < W; x++) {
        for (int y = 0; y < H; y++) {
            Color pixel = screen.pixel(x, y);
            uint8_t* px = &rgb[(y * W + x) * 3];
            px[0] = pixel.red;
            px[1] = pixel.green;
            px[2] = pixel.blue;
        }
    }

    // dernier argument = stride : nombre d'octets par ligne (W pixels × 3 canaux)
    stbi_write_png("toolchain_test.png", W, H, 3, rgb.data(), W * 3);
    return 0;
}
