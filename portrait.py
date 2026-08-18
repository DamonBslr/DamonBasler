"""Regenerate the ASCII portrait embedded in update_profile.py.

Run `python portrait.py` and paste the output into the ART literal. Kept in the
repo so the art can be re-tuned instead of hand-edited glyph by glyph.

The SVG paints light glyphs on a dark card, so a denser glyph reads as a
BRIGHTER pixel -- the model below works in brightness, not ink. That suits the
reference photo, which is low-key: dark background, dark hair, dark tee, and a
face picked out by a key light from the upper left.

Everything is laid out in (column, row) space because at 42x27 glyphs the
facial features sit barely one row apart and have to be placed by hand.
"""
import math

COLS, ROWS = 42, 27
RAMP = " .:-=+*#%@"          # dark -> bright

CX, CY = 20.5, 7.6           # head centre (col, row)
RX, RY = 11.0, 8.3           # head radii (cols, rows)

BROW, EYE = 6.5, 8.5
NOSE, NOSTR, MOUTH = 10.5, 11.5, 13.5
EYE_X, TURN = 4.2, 0.7       # eye offset from face axis; head turned our way

NECK_TOP, NECK_BOT = 13.0, 18.4
SHOULDER_TOP = 17.8


def clamp(t, lo=0.0, hi=1.0):
    return lo if t < lo else hi if t > hi else t


def smooth(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0))
    return t * t * (3 - 2 * t)


def blob(du, dv, su, sv):
    return math.exp(-((du / su) ** 2) - ((dv / sv) ** 2))


def half_width(v):
    """Skull half-width: widest at the cheekbones, tapering into the jaw."""
    return RX * (1.0 - 0.34 * smooth(CY + 0.5, CY + RY, v)
                     - 0.10 * smooth(CY - 3.0, CY - RY, v))


def head_r(u, v):
    return math.hypot((u - CX) / half_width(v), (v - CY) / RY)


def hairline(u):
    t = (u - CX) / RX
    return 4.1 + 1.5 * t * t - 1.0 * t          # swept from his right


def neck_half(v):
    return 6.3 - 0.10 * (v - NECK_TOP)


def shoulder_half(v):
    return 6.8 + (v - SHOULDER_TOP) * 2.1


def key(u, v):
    """Key light from the upper left, 0..1."""
    return clamp(0.55 - (u - CX) / 26.0 - (v - CY) / 42.0)


def brightness(u, v):
    r = head_r(u, v)
    lit = key(u, v)

    if r <= 1.0:
        edge = smooth(1.02, 0.86, r)            # silhouette falling into the dark
        # ...but not across the jaw, where the neck carries the tone onward
        edge += (1.0 - edge) * 0.85 * smooth(MOUTH - 1.0, MOUTH + 2.0, v)

        # ---- hair ----
        if v < hairline(u):
            b = 0.20
            b += 0.44 * smooth(CX - 3.0, CX - 11.5, u)   # warm rim, our left
            b += 0.14 * smooth(3.8, -0.5, v)             # crown sheen
            return b * (0.45 + 0.55 * edge)

        # ---- face ----
        fu = u - CX + TURN
        b = 0.60 + 0.30 * lit

        b -= 0.34 * blob(abs(fu) - EYE_X - 0.3, v - BROW, 2.4, 0.70)
        for s in (-1, 1):
            b -= 0.16 * blob(fu - s * EYE_X, v - EYE, 2.4, 1.0)
            b -= 0.44 * blob(fu - s * (EYE_X - 0.4), v - EYE, 1.05, 0.65)
        b -= 0.10 * blob(fu, v - NOSE, 1.8, 1.5)
        b -= 0.30 * blob(abs(fu) - 1.7, v - NOSTR, 0.9, 0.6)
        b -= 0.30 * blob(fu, v - MOUTH, 2.9, 0.58)
        b -= 0.22 * smooth(NOSTR - 0.5, MOUTH, v) * smooth(1.10, 0.30, r)   # stubble
        b -= 0.20 * smooth(MOUTH + 0.3, MOUTH + 2.8, v)                     # under-jaw
        return clamp(b) * edge

    # ---- ear (his right, our left) ----
    if u < CX - 8.0 and blob(u - (CX - RX - 0.3), v - (CY + 0.6), 2.0, 2.4) > 0.37:
        return 0.52 + 0.18 * lit

    # ---- neck ----
    nu = u - CX + 0.6
    if NECK_TOP < v <= NECK_BOT and abs(nu) < neck_half(v):
        b = 0.42 - 0.16 * smooth(NECK_BOT - 3.5, NECK_BOT, v) + 0.10 * lit
        return b * smooth(neck_half(v) + 0.6, neck_half(v) - 1.6, abs(nu))

    # ---- tee ----
    su = u - CX + 1.1
    if v > SHOULDER_TOP and abs(su) < shoulder_half(v):
        skin = smooth(SHOULDER_TOP + 3.2, SHOULDER_TOP + 0.6, v) * smooth(5.0, 2.0, abs(su))
        b = 0.13 + 0.26 * skin + 0.11 * lit
        return b * smooth(shoulder_half(v), shoulder_half(v) - 1.6, abs(su))

    # ---- the purple wash the photo has behind the subject ----
    return 0.058 * math.exp(-(((r - 1.12) / 0.45) ** 2)) * smooth(25.0, 19.5, v)


def render():
    lines = []
    for row in range(ROWS):
        line = "".join(RAMP[min(9, round(clamp(brightness(col + 0.5, row + 0.5)) * 9))]
                       for col in range(COLS))
        lines.append(line.rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
