#pragma once
#include <cstdint>
#include "TilemapEntry.h"

#ifndef PLANE_WIDTH
#define PLANE_WIDTH 40
#endif

#ifndef PLANE_HEIGHT
#define PLANE_HEIGHT 21
#endif

struct Plane {
    TilemapEntry tiles[PLANE_WIDTH][PLANE_HEIGHT];

    TilemapEntry entry(int x, int y) const {
        int tile_x = x / 8;
        int tile_y = y / 8;
        return tiles[tile_x][tile_y];
    }
};
