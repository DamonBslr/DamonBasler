"""Regenerate the ASCII portrait embedded in update_profile.py.

    pip install Pillow && python portrait.py

Prints the art; paste it into the ART literal. This is a one-off authoring
tool -- the daily Actions run never imports it, so update_profile.py stays
stdlib-only and dependency-free.

The source is the GitHub avatar itself, sampled pixel by pixel rather than
drawn by hand. It is a light-background image, so density means INK here:
the dark hair and tee come out dense, the lit face stays sparse, and the
white backdrop falls away to spaces. That is why the card mounts the art on
a light panel in both themes -- on a dark panel it would read as a negative.
"""
import io
import urllib.request

from PIL import Image, ImageEnhance, ImageOps

# numeric id, because the /DamonBslr.png redirect is not always reachable
AVATAR = "https://avatars.githubusercontent.com/u/63117642?v=4&s=460"

COLS = 69
CELL_ASPECT = (8.0 * 0.6) / 8.6   # glyph advance / line step, matching render()
GAMMA, CONTRAST = 1.15, 1.25
RAMP = " .:-=+*#%@"               # bare paper -> solid ink


def fetch(url=AVATAR):
    with urllib.request.urlopen(url) as r:
        return Image.open(io.BytesIO(r.read())).convert("L")


def convert(im, cols=COLS, aspect=CELL_ASPECT, gamma=GAMMA, contrast=CONTRAST):
    box = ImageOps.invert(im).point(lambda p: 255 if p > 5 else 0).getbbox()
    if box:
        im = im.crop(box)                       # trim the flat studio backdrop
    w, h = im.size
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = im.resize((cols, max(1, round(h / w * cols * aspect))), Image.LANCZOS)

    lines = []
    for y in range(im.height):
        row = "".join(
            RAMP[min(9, max(0, round(((1 - im.getpixel((x, y)) / 255.0) ** gamma) * 9)))]
            for x in range(im.width)
        )
        lines.append(row.rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    print(convert(fetch()))
