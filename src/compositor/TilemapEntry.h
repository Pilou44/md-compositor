#pragma once
#include <cstdint>

class TilemapEntry {
public:

    TilemapEntry(int tile_index,
                 int palette_line,
                 bool flip_h,
                 bool flip_v,
                 bool priority)
    {
        raw = (tile_index & 0x07FF)
            | (flip_h   ? 0x0800 : 0)
            | (flip_v   ? 0x1000 : 0)
            | ((palette_line & 0x03) << 13)
            | (priority ? 0x8000 : 0);
    }

    explicit TilemapEntry(uint16_t packed) : raw(packed) {}

    TilemapEntry() : raw(0) {}

    int  tile_index()   const { return raw & 0x07FF; }
    bool flip_h()       const { return raw & 0x0800; }
    bool flip_v()       const { return raw & 0x1000; }
    int  palette_line() const { return (raw >> 13) & 0x03; }
    bool priority()     const { return raw & 0x8000; }

private:
    uint16_t raw;
};