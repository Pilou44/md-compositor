"""Tiles needed by the player weapon (psprites -> Megadrive sprites) and by the message font."""
import sys, re
import numpy as np
from wad import Wad, tile_key, md_quantize

WAD = sys.argv[1] if len(sys.argv) > 1 else 'freedoom-0.13.0/freedoom1.wad'
w = Wad(WAD)
VIEWH = 168
CENTERY = VIEWH // 2

GROUPS = [('Poing', ['PUNG']), ('Pistolet', ['PISG', 'PISF']), ('Fusil', ['SHTG', 'SHTF']),
          ('Super fusil', ['SHT2']), ('Mitrailleuse', ['CHGG', 'CHGF']),
          ('Lance-roquettes', ['MISG', 'MISF']), ('Tronçonneuse', ['SAWG']),
          ('Plasma', ['PLSG', 'PLSF']), ('BFG', ['BFGG', 'BFGF'])]

def visible(name):
    """Patch at rest position (sx=1, sy=WEAPONTOP=32), clipped to the 3D view (y < 168)."""
    img, lo, to = w.patch(name)
    x = 1 - lo
    # R_DrawPSprite: top = centery - texturemid, texturemid = BASEYCENTER - (sy - topoffset)
    y = CENTERY - (100 - (32 - to))
    h, wd = img.shape
    # clip to view
    y0, y1 = max(0, y), min(VIEWH, y + h)
    x0, x1 = max(0, x), min(320, x + wd)
    if y0 >= y1 or x0 >= x1:
        return None, (x, y)
    return img[y0 - y:y1 - y, x0 - x:x1 - x], (x0, y0)

def cells(img):
    """Cuts the image into 8x8 cells from its own top-left (a sprite is placed at pixel precision).
    Returns (bbox cells, non-empty cells, list of non-empty tiles)."""
    h, wd = img.shape
    H, W = -(-h // 8) * 8, -(-wd // 8) * 8
    pad = np.full((H, W), -1, np.int16); pad[:h, :wd] = img
    # trim fully transparent borders first
    rows = np.where((pad >= 0).any(1))[0]; cols = np.where((pad >= 0).any(0))[0]
    pad = pad[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
    h, wd = pad.shape
    H, W = -(-h // 8) * 8, -(-wd // 8) * 8
    p2 = np.full((H, W), -1, np.int16); p2[:h, :wd] = pad
    tiles = [p2[y:y + 8, x:x + 8] for y in range(0, H, 8) for x in range(0, W, 8)]
    ne = [t for t in tiles if (t >= 0).any()]
    return len(tiles), len(ne), ne, (wd, h)

if __name__ == '__main__':
    names = w.names()
    print('WAD:', WAD)
    print('\n%-16s %-9s %6s %6s %6s %9s %9s' % ('Arme', 'frame', 'l x h', 'cases', 'nonvid', '', ''))
    summary = []
    for label, prefixes in GROUPS:
        lumps = sorted({n for n in names if any(n.startswith(p) and len(n) >= 6 for p in prefixes)})
        if not lumps:
            continue
        per = []
        allt_nf, allt_f = set(), set()
        for n in lumps:
            img, pos = visible(n)
            if img is None or not (img >= 0).any():
                per.append((n, 0, 0, (0, 0))); continue
            nb, ne, tiles, size = cells(img)
            for t in tiles:
                allt_nf.add(tile_key(t, False)); allt_f.add(tile_key(t, True))
            per.append((n, nb, ne, size))
        guns = [p for p in per if not re.match(r'^(PISF|SHTF|CHGF|MISF|PLSF|BFGF)', p[0])]
        flashes = [p for p in per if p not in guns]
        mg = max(guns, key=lambda p: p[2]); mf = max(flashes, key=lambda p: p[2]) if flashes else None
        for n, nb, ne, size in per:
            print('%-16s %-9s %3dx%-3d %6d %6d' % (label, n, size[0], size[1], nb, ne))
        summary.append((label, len(per), mg, mf, sum(p[2] for p in per), len(allt_f)))
    print('\n%-16s %6s %22s %22s %12s %12s' % ('Arme', 'frames', 'plus grosse frame', 'plus gros flash',
                                               'somme frames', 'uniques+flip'))
    for label, nfr, mg, mf, tot, uf in summary:
        print('%-16s %6d %14s %4d t. %14s %4s t. %12d %12d' % (label, nfr, mg[0], mg[2],
              mf[0] if mf else '-', mf[2] if mf else '-', tot, uf))
