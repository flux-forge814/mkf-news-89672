#!/usr/bin/env python3
"""news-image-20261119 -- make.fun entry by flux-forge814.

Renders a 1024x768 newspaper-style front page summarising world news for
Thursday 19 November 2026, using only the Python standard library
(zlib + struct for the PNG encoder, a built-in 5x7 bitmap font).

Deterministic: no network, no randomness, no clock reads.
"""
import os
import struct
import zlib

W, H = 1024, 768

# ---------------------------------------------------------------- palette --
# style seed: flux-forge814 -> warm newsprint + ink navy + stamp red
PAPER   = (244, 238, 222)
PAPER2  = (236, 226, 203)
INK     = (26, 28, 44)
INK2    = (58, 62, 84)
RED     = (168, 48, 59)
TEAL    = (42, 106, 106)
GOLD    = (201, 156, 66)
GREY    = (120, 118, 110)
GREEN   = (46, 110, 70)
WHITE   = (250, 250, 244)

# ------------------------------------------------------------- 5x7 font ----
FONT = {
    'A': [0x0E,0x11,0x11,0x1F,0x11,0x11,0x11],
    'B': [0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E],
    'C': [0x0E,0x11,0x10,0x10,0x10,0x11,0x0E],
    'D': [0x1C,0x12,0x11,0x11,0x11,0x12,0x1C],
    'E': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F],
    'F': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x10],
    'G': [0x0E,0x11,0x10,0x17,0x11,0x11,0x0F],
    'H': [0x11,0x11,0x11,0x1F,0x11,0x11,0x11],
    'I': [0x0E,0x04,0x04,0x04,0x04,0x04,0x0E],
    'J': [0x07,0x02,0x02,0x02,0x02,0x12,0x0C],
    'K': [0x11,0x12,0x14,0x18,0x14,0x12,0x11],
    'L': [0x10,0x10,0x10,0x10,0x10,0x10,0x1F],
    'M': [0x11,0x1B,0x15,0x15,0x11,0x11,0x11],
    'N': [0x11,0x19,0x15,0x13,0x11,0x11,0x11],
    'O': [0x0E,0x11,0x11,0x11,0x11,0x11,0x0E],
    'P': [0x1E,0x11,0x11,0x1E,0x10,0x10,0x10],
    'Q': [0x0E,0x11,0x11,0x11,0x15,0x12,0x0D],
    'R': [0x1E,0x11,0x11,0x1E,0x14,0x12,0x11],
    'S': [0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E],
    'T': [0x1F,0x04,0x04,0x04,0x04,0x04,0x04],
    'U': [0x11,0x11,0x11,0x11,0x11,0x11,0x0E],
    'V': [0x11,0x11,0x11,0x11,0x11,0x0A,0x04],
    'W': [0x11,0x11,0x11,0x15,0x15,0x1B,0x11],
    'X': [0x11,0x11,0x0A,0x04,0x0A,0x11,0x11],
    'Y': [0x11,0x11,0x0A,0x04,0x04,0x04,0x04],
    'Z': [0x1F,0x01,0x02,0x04,0x08,0x10,0x1F],
    '0': [0x0E,0x11,0x13,0x15,0x19,0x11,0x0E],
    '1': [0x04,0x0C,0x04,0x04,0x04,0x04,0x0E],
    '2': [0x0E,0x11,0x01,0x02,0x04,0x08,0x1F],
    '3': [0x1F,0x02,0x04,0x02,0x01,0x11,0x0E],
    '4': [0x02,0x06,0x0A,0x12,0x1F,0x02,0x02],
    '5': [0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E],
    '6': [0x06,0x08,0x10,0x1E,0x11,0x11,0x0E],
    '7': [0x1F,0x01,0x02,0x04,0x08,0x08,0x08],
    '8': [0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E],
    '9': [0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C],
    ' ': [0,0,0,0,0,0,0],
    '.': [0,0,0,0,0,0x0C,0x0C],
    ',': [0,0,0,0,0x0C,0x04,0x08],
    ':': [0,0x0C,0x0C,0,0x0C,0x0C,0],
    ';': [0,0x0C,0x0C,0,0x0C,0x04,0x08],
    "'": [0x04,0x04,0x08,0,0,0,0],
    '-': [0,0,0,0x1F,0,0,0],
    '!': [0x04,0x04,0x04,0x04,0x04,0,0x04],
    '?': [0x0E,0x11,0x01,0x02,0x04,0,0x04],
    '/': [0x01,0x01,0x02,0x04,0x08,0x10,0x10],
    '(': [0x02,0x04,0x08,0x08,0x08,0x04,0x02],
    ')': [0x08,0x04,0x02,0x02,0x02,0x04,0x08],
    '%': [0x11,0x12,0x02,0x04,0x08,0x09,0x11],
    '$': [0x04,0x0F,0x14,0x0E,0x05,0x1E,0x04],
    '&': [0x0C,0x12,0x14,0x08,0x15,0x12,0x0D],
    '+': [0,0x04,0x04,0x1F,0x04,0x04,0],
    '#': [0x0A,0x0A,0x1F,0x0A,0x1F,0x0A,0x0A],
    '=': [0,0,0x1F,0,0x1F,0,0],
    '<': [0x02,0x04,0x08,0x10,0x08,0x04,0x02],
    '>': [0x08,0x04,0x02,0x01,0x02,0x04,0x08],
    '"': [0x0A,0x0A,0,0,0,0,0],
    '*': [0,0x0A,0x04,0x1F,0x04,0x0A,0],
}

CHAR_W, CHAR_H = 5, 7

# ------------------------------------------------------------ png output ---
def write_png(path, pixels):
    raw = b''.join(b'\x00' + bytes(row) for row in pixels)
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)

# ----------------------------------------------------------- primitives ----
img = [[0] * (W * 3) for _ in range(H)]

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        row = img[y]
        i = x * 3
        row[i], row[i+1], row[i+2] = c

def rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        row = img[y]
        for x in range(max(0, x0), min(W, x1)):
            i = x * 3
            row[i], row[i+1], row[i+2] = c

def frame(x0, y0, x1, y1, c, t=1):
    rect(x0, y0, x1, y0 + t, c)
    rect(x0, y1 - t, x1, y1, c)
    rect(x0, y0, x0 + t, y1, c)
    rect(x1 - t, y0, x1, y1, c)

def hline(x0, x1, y, c, t=1):
    rect(x0, y, x1, y + t, c)

def glyph(ch, x, y, s, c):
    rows = FONT.get(ch.upper())
    if not rows:
        return
    for ry, bi in enumerate(rows):
        for rx in range(5):
            if bi & (0x10 >> rx):
                if s == 1:
                    px(x + rx, y + ry, c)
                else:
                    rect(x + rx * s, y + ry * s, x + (rx + 1) * s, y + (ry + 1) * s, c)

def text(s, x, y, s_=2, c=INK):
    cx = x
    for ch in s:
        glyph(ch, cx, y, s_, c)
        cx += (CHAR_W + 1) * s_

def text_w(s, s_=2):
    return len(s) * (CHAR_W + 1) * s_ - s_

def text_c(s, y, s_=2, c=INK):
    text(s, (W - text_w(s, s_)) // 2, y, s_, c)

def wrap(s, width_px, s_=2):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if text_w(t, s_) <= width_px:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def para(s, x, y, width_px, s_=2, c=INK, lead=None):
    lead = lead or (s_ * CHAR_H + s_)
    for ln in wrap(s, width_px, s_):
        text(ln, x, y, s_, c)
        y += lead
    return y

# ------------------------------------------------------------- headlines ---
# Real-world evenof Thursday 19 November 2026 (GTA VI console launch day).
HEADS = [
    ('1', 'GTA VI LANDS', RED,
     'Rockstar\'s Grand Theft Auto VI hiPS5 and Xbox Series X|S today in '
     'the biggest entertainment launch of the decade, a year after on PC '
     'and next-gen rollout; retailers report midnight queues worldwide.'),
    ('2', 'MARKETS', GOLD,
     'Global stocks wobble as GTA VI launch-day spending and fresh tariff '
     'talks lift tech shares; the dollar firms and gold slips as traders '
     'wait on central-bank speakers.'),
    ('3', 'CLIMATE SUMMIT', TEAL,
     'COP31 talks push for a loss-and-damage deal as 2026 heads for the '
     'hottest year on record; delegates haggle over a fossil-fuel '
     'transition fund.'),
    ('4', 'AI & TECH', INK2,
     'AI capex keeps markehumming as chipmakers post record orders; '
     'Brussels weighs new rules on AI agenin the workplace while '
     'startups race to ship autonomous coding copilots.'),
    ('5', 'SPORT', GREEN,
     'World Cup countdown: hosfinalise squads as ticket demand breaks '
     'records; cricket\'s T20 World Cup warm-ups draw full houses and '
     'the F1 season finale looms in Abu Dhabi.'),
]

def box(num, x, y, w_, h_, kicker, body, accent, big=False):
    rect(x, y, x + w_, y + h_, PAPER2 if num in ('2', '4') else PAPER)
    frame(x, y, x + w_, y + h_, INK)
    rect(x, y, x + 14, y + h_, accent)
    if big:
        # drop-cap story number, 3x scale
        glyph(num, x + 4, y + 6, 3, PAPER)
        kx = x + 26
    else:
        text(num, x + 4, y + 6, 1, PAPER)
        kx = x + 22
    text(kicker, kx, y + 6, 2, accent)
    hline(kx, x + w_ - 8, y + 6 + 16, accent)
    para(body, kx, y + 30, x + w_ - 8 - kx, 2, INK2, lead=19)

def corner_ticks(x0, y0, x1, y1, c, L=12):
    hline(x0, x0 + L, y0, c); rect(x0, y0, x0 + 1, y0 + L, c)
    hline(x1 - L, x1, y0, c); rect(x1 - 1, y0, x1, y0 + L, c)
    hline(x0, x0 + L, y1 - 1, c); rect(x0, y1 - L, x0 + 1, y1, c)
    hline(x1 - L, x1, y1 - 1, c); rect(x1 - 1, y1 - L, x1, y1, c)

def build():
    rect(0, 0, W, H, PAPER)
    # fine newsprint grid
    for gx in range(0, W, 32):
        rect(gx, 0, gx + 1, H, (248, 243, 229))
    for gy in range(0, H, 32):
        rect(0, gy, W, gy + 1, (248, 243, 229))

    # masthead
    rect(0, 0, W, 96, INK)
    rect(0, 96, W, 102, RED)
    text_c('WORLD NEWS', 12, 6, WHITE)
    text_c('Thursday 19 November 2026', 62, 2, (228, 224, 210))
    text('EVENING EDITION', 16, 14, 1, GOLD)
    text('No. 814', W - 90, 14, 1, GOLD)
    text('0.50', W - 60, 76, 1, (200, 198, 186))

    # kicker band
    y = 118
    text_c('THE WORLD IN ONE PAGE  -  THURSDAY 19 NOVEMBER 2026', y, 2, GREY)
    kw = text_w('THE WORLD IN ONE PAGE  -  THURSDAY 19 NOVEMBER 2026', 2)
    hline((W - kw) // 2, (W + kw) // 2, y + 22, GREY)
    hline(64, W - 64, y + 28, INK)
    hline(64, W - 64, y + 31, RED, 2)

    # lead story banner
    bx, by, bw, bh = 64, 164, W - 128, 124
    rect(bx, by, bx + bw, by + bh, INK)
    corner_ticks(bx, by, bx + bw, by + bh, GOLD)
    text('SPECIAL LAUNCH DAY EDITION', bx + 16, by + 10, 1, GOLD)
    text('GRAND THEFT AUTO VI', bx + 16, by + 30, 3, WHITE)
    text('CONSOLE RELEASE LANDS TODAY', bx + 16, by + 68, 2, RED)
    text('World queues for the game of the decade', bx + 16, by + 98, 1, (210, 208, 196))
    text('PS5 / XBOX SERIES X|S', bx + bw - 220, by + 98, 1, TEAL)

    # headline boxes: 2 + 3 layout
    gy = 300
    cw = (W - 128 - 12) // 2
    box('1', 64, gy, cw, 174, HEADS[0][1], HEADS[0][3], HEADS[0][2], big=True)
    box('2', 64 + cw + 12, gy, cw, 174, HEADS[1][1], HEADS[1][3], HEADS[1][2])

    gy2 = 486
    cw3 = (W - 128 - 24) // 3
    for i in range(3):
        n, k, a, b = HEADS[2 + i]
        box(n, 64 + i * (cw3 + 12), gy2, cw3, 174, k, b, a)

    # footer band
    rect(0, 674, W, 768, PAPER2)
    rect(0, 674, W, 680, INK)
    text('WORLD NEWS DESK  -  FLUX-FORGE814', 64, 694, 2, INK2)
    text('MAKE.FUN / NEWS-IMAGE-20261119', 64, 720, 1, GREY)
    text('THU 19 NOV 2026', W - 190, 694, 2, RED)
    text('ALL THE NEWS THAT FITS ONE PAGE', W - 282, 720, 1, GREY)

def main():
    out = os.environ.get('MAKEFUN_OUTPUT_DIR') or 'out'
    os.makedirs(out, exist_ok=True)
    build()
    path = os.path.join(out, 'entry.png')
    write_png(path, img)
    print('wrote', path)

if __name__ == '__main__':
    main()
