"""Counts Megadrive tiles needed by the Doom status bar (Window plane, 40x4 cells, y=168..199).

Every widget is enumerated in all its states, drawn at its real Doom position (patch offsets
applied), and each 8x8 cell of the Window is cut out. Widgets that share a cell are combined
(cartesian product of their states restricted to that cell)."""
import itertools, sys
import numpy as np
from wad import Wad, tile_key, md_quantize

WAD = sys.argv[1] if len(sys.argv) > 1 else 'freedoom-0.13.0/freedoom1.wad'
w = Wad(WAD)
pal = w.playpal()
ST_Y = 168

def put(canvas, name, x, y):
    """V_DrawPatch onto a 320x32 canvas (screen coords), -1 = transparent."""
    img, lo, to = w.patch(name)
    x -= lo; y -= to; y -= ST_Y
    h, wd = img.shape
    sub = canvas[y:y + h, x:x + wd]
    m = img[:sub.shape[0], :sub.shape[1]] >= 0
    sub[m] = img[:sub.shape[0], :sub.shape[1]][m]

# --- static background
bg = np.full((32, 320), -1, np.int16)
put(bg, 'STBAR', 0, 168)
put(bg, 'STARMS', 104, 168)          # single player: arms panel, drawn over STBAR
assert (bg >= 0).all()

# --- widgets: name -> list of layers (320x32, -1 = untouched)
def layer():
    return np.full((32, 320), -1, np.int16)

def number_states(font, x, y, width, values, minus=None):
    """STlib_drawNum: clears its rect back to the background, draws right-aligned digits."""
    pw, ph = w.patch(font + '0')[0].shape[1], w.patch(font + '0')[0].shape[0]
    states = []
    for v in values:
        L = layer()
        x0 = x - width * pw
        L[y - ST_Y:y - ST_Y + ph, x0:x] = bg[y - ST_Y:y - ST_Y + ph, x0:x]
        if v is not None:
            xx = x
            if v == 0:
                put(L, font + '0', xx - pw, y)
            n = v
            nd = width
            while n and nd:
                xx -= pw
                put(L, font + str(n % 10), xx, y)
                n //= 10; nd -= 1
        states.append(L)
    return states

def icon_states(names, x, y):
    """STlib_updateMultIcon: None = background restored (no icon)."""
    states = []
    for nm in names:
        L = layer()
        if nm is None:
            img, lo, to = w.patch(names[1] if names[0] is None else names[0])
        if nm is not None:
            put(L, nm, x, y)
        states.append(L)
    # "None" state: copy background over the union of the icons' rects
    return states

def with_bg_restore(states):
    """The 'no icon' state restores the background: make its layer the bg over the union
    of the other states' footprints so compositing is exact."""
    fp = np.zeros((32, 320), bool)
    for L in states:
        fp |= L >= 0
    out = []
    for L in states:
        M = layer(); M[fp] = bg[fp]
        m = L >= 0; M[m] = L[m]
        out.append(M)
    return out

def run(full_range):
    big = list(range(0, 1000)) if full_range else None
    widgets = {}
    rng = (lambda hi: list(range(0, 1000))) if full_range else (lambda hi: list(range(0, hi + 1)))
    widgets['ammo (big)'] = number_states('STTNUM', 44, 171, 3, [None] + rng(600))  # None = fist/saw (1994)
    widgets['health'] = number_states('STTNUM', 90, 171, 3, rng(200))
    widgets['armor'] = number_states('STTNUM', 221, 171, 3, rng(200))
    L = layer(); put(L, 'STTPRCNT', 90, 171); put(L, 'STTPRCNT', 221, 171)
    widgets['percent signs'] = [L]
    for i in range(6):
        widgets['arms %d' % (i + 2)] = with_bg_restore(
            [x for x in icon_states(['STGNUM%d' % (i + 2), 'STYSNUM%d' % (i + 2)],
                                    111 + (i % 3) * 12, 172 + (i // 3) * 10)])
    faces = sorted(n for n in set(w.names()) if n.startswith('STF') and not n.startswith('STFB'))
    widgets['face'] = with_bg_restore([icon_states([f], 143, 168)[0] for f in faces])
    for i, (kx, ky) in enumerate([(239, 171), (239, 181), (239, 191)]):
        st = icon_states(['STKEYS%d' % i, 'STKEYS%d' % (i + 3)], kx, ky)
        widgets['key %d' % i] = with_bg_restore([layer()] + st)
    ys = [173, 179, 191, 185]
    maxes = [200, 50, 300, 50] if not full_range else [999] * 4
    maxes2 = [400, 100, 600, 100] if not full_range else [999] * 4
    for i in range(4):
        widgets['ammo %d' % i] = number_states('STYSNUM', 288, ys[i], 3, rng(maxes2[i]))
        widgets['max ammo %d' % i] = number_states('STYSNUM', 314, ys[i], 3,
                                                   sorted({maxes[i], maxes2[i]}) if not full_range else rng(999))
    return widgets, faces

def count(widgets, quant):
    """Returns per-cell sets, global unique tile counts (no flip / with flip)."""
    conv = (lambda a: md_quantize(a, pal)) if quant else (lambda a: a)
    B = conv(bg)
    uniq_nf, uniq_f = set(), set()
    per_widget_cells = {}
    static_cells = 0
    per_cell = {}
    # footprint of each widget
    fps = {k: np.any([L >= 0 for L in v], axis=0) for k, v in widgets.items()}
    for cy in range(4):
        for cx in range(40):
            ys, xs = slice(cy * 8, cy * 8 + 8), slice(cx * 8, cx * 8 + 8)
            touching = [k for k in widgets if fps[k][ys, xs].any()]
            # distinct per-widget crops
            opts = []
            for k in touching:
                crops = {}
                for L in widgets[k]:
                    c = conv(L[ys, xs])
                    crops[c.tobytes()] = c
                opts.append(list(crops.values()))
            tiles = set()
            for combo in itertools.product(*opts) if opts else [()]:
                t = B[ys, xs].copy()
                for c in combo:
                    m = c >= 0; t[m] = c[m]
                tiles.add(t.tobytes())
                uniq_nf.add(tile_key(t, False)); uniq_f.add(tile_key(t, True))
            per_cell[(cx, cy)] = (len(tiles), touching)
            if len(tiles) == 1:
                static_cells += 1
    return uniq_nf, uniq_f, per_cell, static_cells

def snapshot_count(quant):
    conv = (lambda a: md_quantize(a, pal)) if quant else (lambda a: a)
    B = conv(bg)
    s_nf = {tile_key(B[y:y+8, x:x+8], False) for y in range(0, 32, 8) for x in range(0, 320, 8)}
    s_f = {tile_key(B[y:y+8, x:x+8], True) for y in range(0, 32, 8) for x in range(0, 320, 8)}
    return len(s_nf), len(s_f)

if __name__ == '__main__':
    print('WAD:', WAD)
    for quant in (False, True):
        print('\n=== couleurs %s ===' % ('Megadrive (9 bits)' if quant else 'index Doom (8 bits)'))
        print('fond seul (STBAR+STARMS), 160 cellules : uniques = %d, avec flips = %d' % snapshot_count(quant))
        for full in (False, True):
            widgets, faces = run(full)
            nf, f, per_cell, static = count(widgets, quant)
            print('%s : uniques = %d, avec flips = %d, cellules jamais modifiées = %d/160' % (
                'plages réalistes' if not full else 'toutes valeurs 0..999', len(nf), len(f), static))
            if not full and not quant:
                print('  visages :', len(faces))
                # per widget-group breakdown: cells touched and variants
                grp = {}
                for (cx, cy), (n, touching) in per_cell.items():
                    key = ' + '.join(sorted({t.split(' ')[0] if t.startswith(('arms', 'key', 'max', 'ammo ')) and not t.startswith('ammo (') else t for t in touching})) or '(fond fixe)'
                    g = grp.setdefault(key, [0, 0]); g[0] += 1; g[1] += n
                for k, (c, n) in sorted(grp.items(), key=lambda kv: -kv[1][1]):
                    print('  %-40s cellules=%3d  variantes (somme)=%5d' % (k, c, n))
