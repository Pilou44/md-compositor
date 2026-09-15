#pragma once
#include <cstdint>
#include <vector>
#include "Tile.h"
#include "Plane.h"
#include "Color.h"
#include "Palette.h"

struct Screen {
    std::vector<Tile> tiles;
    Plane plane_a;
    Plane plane_b;
    Color backdrop;
    Palette palettes[3];

    Color pixel(int x, int y) const {
        Color color = backdrop;

        int pixel_x = x % 8;
        int pixel_y = y % 8;

        TilemapEntry entry_b = plane_b.entry(x, y);
        uint16_t pixel_b = tiles[entry_b.tile_index()].pixel(pixel_x, pixel_y, entry_b.flip_h(), entry_b.flip_v());
        if (pixel_b != 0) {
            color = palettes[entry_b.palette_index()].colors[pixel_b - 1];
        }

        TilemapEntry entry_a = plane_a.entry(x, y);
        uint16_t pixel_a = tiles[entry_a.tile_index()].pixel(pixel_x, pixel_y, entry_a.flip_h(), entry_a.flip_v());
        if (pixel_a != 0) {
            color = palettes[entry_a.palette_index()].colors[pixel_a - 1];
        }   
        return color;
    }
};
