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
};
