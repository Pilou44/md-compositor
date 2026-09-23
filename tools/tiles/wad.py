import struct
import numpy as np

class Wad:
    def __init__(self, path):
        self.data = open(path, 'rb').read()
        ident, n, off = struct.unpack_from('<4sii', self.data, 0)
        self.lumps = []
        for i in range(n):
            lo, sz, name = struct.unpack_from('<ii8s', self.data, off + 16 * i)
            self.lumps.append((name.rstrip(b'\0').decode('ascii', 'replace').upper(), lo, sz))
        self.index = {}
        for i, (nm, lo, sz) in enumerate(self.lumps):
            self.index[nm] = i  # last one wins, like Doom

    def names(self):
        return [l[0] for l in self.lumps]

    def lump(self, name):
        nm, lo, sz = self.lumps[self.index[name]]
        return self.data[lo:lo + sz]

    def has(self, name):
        return name in self.index

    def patch(self, name):
        """Returns (img int16 HxW with -1 = transparent, leftoffset, topoffset)."""
        d = self.lump(name)
        w, h, lo, to = struct.unpack_from('<hhhh', d, 0)
        img = np.full((h, w), -1, dtype=np.int16)
        for x in range(w):
            p = struct.unpack_from('<I', d, 8 + 4 * x)[0]
            top = -1
            while d[p] != 0xFF:
                td = d[p]
                top = td if td > top else top + td  # tall patch support
                ln = d[p + 1]
                img[top:top + ln, x] = np.frombuffer(d, np.uint8, ln, p + 3)
                p += ln + 4
        return img, lo, to

    def playpal(self):
        return np.frombuffer(self.lump('PLAYPAL'), np.uint8, 768).reshape(256, 3)


def tile_key(t, flips):
    """t: 8x8 int16 array. Canonical key, optionally invariant to H/V flips."""
    if not flips:
        return t.tobytes()
    return min(t.tobytes(), t[:, ::-1].tobytes(), t[::-1, :].tobytes(), t[::-1, ::-1].tobytes())


def md_quantize(img, pal):
    """Maps Doom palette indices to a Megadrive 9-bit color id (3 bits per channel).
    Transparent (-1) stays -1."""
    # MD: 8 levels per channel, keep top 3 bits
    md = (pal[:, 0] >> 5).astype(np.int16) * 64 + (pal[:, 1] >> 5) * 8 + (pal[:, 2] >> 5)
    out = np.where(img >= 0, md[np.clip(img, 0, 255)], -1).astype(np.int16)
    return out
