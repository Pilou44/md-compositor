#pragma once
#include <cstdint>
#include <vector>

struct Screen {
    std::vector<Tile> tiles;
    Plane plane_a;
    Plane plane_b;
    Color backdrop;
    Palette palettes[3];
};
