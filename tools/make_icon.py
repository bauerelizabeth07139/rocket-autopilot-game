"""Generate asset/rocket.ico from a tiny rocket drawn with pygame.

Run:  python tools/make_icon.py
Produces a 64x64 32-bit ICO used by the PyInstaller build.
"""

import os
import struct

import pygame

SIZE = 64
OUT = os.path.join(os.path.dirname(__file__), "..", "asset", "rocket.ico")


def draw_icon():
    pygame.init()
    s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))

    # flame
    pygame.draw.polygon(s, (255, 150, 40, 255),
                        [(32, 46), (24, 62), (40, 62)])
    # body
    pygame.draw.rect(s, (226, 228, 235, 255), (22, 18, 20, 34), border_radius=4)
    # nose
    pygame.draw.polygon(s, (255, 92, 92, 255), [(32, 2), (22, 20), (42, 20)])
    # stripe
    pygame.draw.rect(s, (255, 92, 92, 255), (22, 34, 20, 5))
    # window
    pygame.draw.circle(s, (40, 60, 90, 255), (32, 26), 4)
    # fins
    pygame.draw.polygon(s, (255, 92, 92, 255), [(22, 44), (10, 58), (24, 52)])
    pygame.draw.polygon(s, (255, 92, 92, 255), [(42, 44), (54, 58), (40, 52)])
    # nozzle
    pygame.draw.rect(s, (70, 72, 80, 255), (27, 52, 10, 6))
    return s


def write_ico(surface, path):
    w = h = surface.get_width()
    pixels = pygame.image.tobytes(surface, "BGRA", False)  # 32-bit, straight alpha

    header = struct.pack("<HHH", 0, 1, 1)
    # ICONDIRENTRY: w, h, colors, reserved, planes, bitcount, size, offset
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, 0, 22)
    # BITMAPINFOHEADER for 32-bit BGRA (no AND mask in V3 header + no mask)
    info = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0,
                       0, 0, 0, 0, 0)
    and_mask = b"\x00" * (w * h // 8)  # all-visible mask
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32,
                        len(info) + len(pixels) + len(and_mask), 22)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header + entry + info + pixels + and_mask)
    print("wrote", path)


if __name__ == "__main__":
    write_ico(draw_icon(), os.path.abspath(OUT))
