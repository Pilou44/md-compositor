#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#include <cstdint>
#include <vector>

int main() {
    const int W = 128, H = 128;
    std::vector<uint8_t> rgb(W * H * 3);

    for (int y = 0; y < H; ++y) {
        for (int x = 0; x < W; ++x) {
            uint8_t* px = &rgb[(y * W + x) * 3];
            px[0] = static_cast<uint8_t>(x * 2); // R monte horizontalement
            px[1] = static_cast<uint8_t>(y * 2); // G monte verticalement
            px[2] = 128;                         // B constant
        }
    }

    // dernier argument = stride : nombre d'octets par ligne (W pixels × 3 canaux)
    stbi_write_png("toolchain_test.png", W, H, 3, rgb.data(), W * 3);
    return 0;
}
