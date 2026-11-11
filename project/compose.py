"""Builds spade A..10 faces from Chris Aguilar's deck glyphs, laid out with the
pip/index geometry measured on razlozhi.ru cards (142x192 grid), and keeps the
J/Q/K faces cut straight from the deck. Output: faces2.json (rank -> data URI)."""
from PIL import Image, ImageDraw
import numpy as np, io, base64, json
Image.MAX_IMAGE_PIXELS = None
im = Image.open('huge.png').convert('RGBA')
CW, CH = 622, 866


def card(i):
    l = (651 + i * 366) * 2
    return im.crop((l, 2496 * 2, l + CW, 2496 * 2 + CH))


def mask_of(img, box):
    g = np.array(img.crop(box).convert('L')).astype(float)
    a = np.clip((255 - g) / 255, 0, 1)
    ys, xs = np.where(a > 0.5)
    return Image.fromarray((a[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype('uint8'))


c2 = card(1)
PIP = mask_of(c2, (253, 88, 367, 228))
SUIT = mask_of(c2, (5, 136, int(CW * .18), 200))
RANK = {i + 1: mask_of(card(i), (5, 36, int(CW * .18), 133)) for i in range(10)}

blank = card(0).copy()
ImageDraw.Draw(blank).rectangle([12, 12, CW - 13, CH - 13], fill=(255, 255, 255, 255))
corner = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(corner).rounded_rectangle([0, 0, CW - 1, CH - 1], radius=28, fill=255)

sx, sy = CW / 142, CH / 192
P = {1: [[34, 50, 78, 78]], 2: [[56, 20], [56, 142]], 3: [[56, 20], [56, 82], [56, 142]],
     4: [[30, 20], [82, 20], [30, 142], [82, 142]],
     5: [[30, 20], [82, 20], [56, 78], [30, 142], [82, 142]],
     6: [[30, 20], [82, 20], [30, 78], [82, 78], [30, 142], [82, 142]],
     7: [[30, 20], [82, 20], [56, 54], [30, 82], [82, 82], [30, 142], [82, 142]],
     8: [[30, 20], [82, 20], [30, 62], [82, 62], [30, 100], [82, 100], [30, 142], [82, 142]],
     9: [[30, 20], [82, 20], [30, 60], [82, 60], [56, 78], [30, 104], [82, 104], [30, 142], [82, 142]],
     10: [[30, 20], [82, 20], [56, 40], [30, 62], [82, 62], [30, 100], [82, 100], [56, 122], [30, 142], [82, 142]]}
INDEX = {1: (4, 8, 22, 24), 10: (6, 8, 18, 24)}


def paste(canvas, m, cx, cy, w=None, h=None, flip=False):
    if h is None:
        h = w * m.size[1] / m.size[0]
    if w is None:
        w = h * m.size[0] / m.size[1]
    mm = m.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
    if flip:
        mm = mm.rotate(180)
    ink = Image.new('RGBA', mm.size, (0, 0, 0, 255))
    ink.putalpha(mm)
    canvas.alpha_composite(ink, (round(cx - mm.size[0] / 2), round(cy - mm.size[1] / 2)))


out = json.load(open('faces.json'))
for r in range(1, 11):
    cv = blank.copy()
    for p in P[r]:
        x, y = p[0], p[1]
        w, h = (p[2], p[3]) if len(p) > 2 else (30, 30)
        cy192 = y + h / 2
        paste(cv, PIP, (x + w / 2) * sx, cy192 * sy, w=w * sx, flip=cy192 > 105)
    ix, iy, iw, ih = INDEX.get(r, (8, 8, 14, 24))
    for flip in (False, True):
        layer = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        paste(layer, RANK[r], (ix + iw / 2) * sx, (iy + ih / 2) * sy, h=ih * sy)
        paste(layer, SUIT, 15 * sx, 48 * sy, w=18 * sx)
        if flip:
            layer = layer.rotate(180)
        cv.alpha_composite(layer)
    cv.putalpha(Image.fromarray(np.minimum(np.array(cv.getchannel('A')), np.array(corner))))
    small = cv.resize((300, 418), Image.LANCZOS)
    small.save(f'n{r}.png')
    b = io.BytesIO()
    small.save(b, 'WEBP', quality=90, method=6)
    out[str(r)] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
json.dump(out, open('faces2.json', 'w'))
strip = Image.new('RGBA', (310 * 10, 418), (44, 115, 59, 255))
for r in range(1, 11):
    strip.alpha_composite(Image.open(f'n{r}.png'), ((r - 1) * 310, 0))
strip.resize((1550, 209), Image.LANCZOS).save('strip.png')
