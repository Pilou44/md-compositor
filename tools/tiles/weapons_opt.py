"""Weapon tile optimisation study: symmetry, and tile dedup with flips when each frame
is free to choose its 8x8 grid alignment (it's a sprite, placed at pixel precision)."""
import itertools
import numpy as np
from weapons import w, GROUPS, visible
from wad import tile_key, md_quantize

pal = w.playpal()
names = w.names()

def trim(img):
    r = np.where((img >= 0).any(1))[0]; c = np.where((img >= 0).any(0))[0]
    return img[r[0]:r[-1] + 1, c[0]:c[-1] + 1]

def tiles_at(img, dx, dy):
    h, wd = img.shape
    H, W = -(-(h + dy) // 8) * 8, -(-(wd + dx) // 8) * 8
    p = np.full((H, W), -1, np.int16); p[dy:dy + h, dx:dx + wd] = img
    return [p[y:y + 8, x:x + 8] for y in range(0, H, 8) for x in range(0, W, 8)
            if (p[y:y + 8, x:x + 8] >= 0).any()]

def symmetry(img):
    """Best vertical mirror axis: share of opaque pixels whose mirror is identical."""
    h, wd = img.shape
    best = (0, None)
    for ax2 in range(wd // 2, 3 * wd // 2):          # axis at ax2/2
        m = img[:, ::-1]
        # mirrored x' = ax2 - 1 - x
        sh = ax2 - wd
        a = np.full((h, 3 * wd), -1, np.int16); b = a.copy()
        a[:, wd:2 * wd] = img
        b[:, wd + sh:2 * wd + sh] = m
        op = a >= 0
        same = (a == b) & op
        s = same.sum() / op.sum()
        if s > best[0]:
            best = (s, ax2 / 2)
    return best

if __name__ == '__main__':
    print('%-16s %6s %8s %10s %12s %10s' % ('Arme', 'frames', 'somme', 'symétrie', 'dédup+flips', 'gain'))
    for label, prefixes in GROUPS:
        lumps = sorted({n for n in names if any(n.startswith(p) and len(n) >= 6 for p in prefixes)})
        if not lumps:
            continue
        imgs = []
        for n in lumps:
            img, _ = visible(n)
            if img is not None and (img >= 0).any():
                imgs.append((n, md_quantize(trim(img), pal)))
        base = sum(len(tiles_at(i, 0, 0)) for _, i in imgs)
        sym = np.mean([symmetry(i)[0] for _, i in imgs])
        # greedy: each frame picks the alignment that adds the fewest new tiles
        pool = set()
        for n, i in sorted(imgs, key=lambda t: -t[1].size):
            best = None
            for dx, dy in itertools.product(range(8), range(8)):
                ks = {tile_key(t, True) for t in tiles_at(i, dx, dy)}
                new = len(ks - pool)
                if best is None or new < best[0]:
                    best = (new, ks)
            pool |= best[1]
        print('%-16s %6d %8d %9.0f%% %12d %9.0f%%' % (label, len(imgs), base, 100 * sym, len(pool),
                                                    100 * (1 - len(pool) / base)))
