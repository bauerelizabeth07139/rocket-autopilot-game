"""All rendering: stars, planets, station, rocket, flame, HUD."""

import math
import random

import pygame

from . import config as C
from . import fonts


# --------------------------------------------------------------------------
# background
# --------------------------------------------------------------------------
class Background:
    def __init__(self):
        self.stars = [(random.randrange(C.WIDTH), random.randrange(C.HEIGHT),
                       random.choice((1, 1, 1, 2)), random.random())
                      for _ in range(140)]

    def draw(self, screen, t):
        for x, y, s, ph in self.stars:
            b = 120 + int(80 * math.sin(t * 2.0 + ph * 6.28))
            pygame.draw.rect(screen, (b, b, b + 20), (x, y, s, s))


# --------------------------------------------------------------------------
# rocket sprite
# --------------------------------------------------------------------------
def make_rocket_surface():
    s = pygame.Surface((56, 64), pygame.SRCALPHA)
    # nose cone
    pygame.draw.polygon(s, (255, 92, 92), [(28, 2), (14, 26), (42, 26)])
    # hull
    pygame.draw.rect(s, (226, 228, 235), (16, 24, 24, 26))
    pygame.draw.rect(s, (255, 92, 92), (16, 38, 24, 5))
    # window
    pygame.draw.circle(s, (40, 60, 90), (28, 32), 4)
    # fins
    pygame.draw.polygon(s, (255, 92, 92), [(16, 46), (4, 60), (17, 54)])
    pygame.draw.polygon(s, (255, 92, 92), [(40, 46), (52, 60), (39, 54)])
    # engine nozzle
    pygame.draw.rect(s, (70, 72, 80), (19, 52, 18, 8))
    return s


ROCKET_SURF = make_rocket_surface()


def draw_rocket(screen, rocket):
    center = (int(rocket.x), int(rocket.y))
    # flame (drawn first, under the body)
    if rocket.flame > 0.02:
        fx, fy = rocket.x - 8 * math.sin(math.radians(rocket.angle)), \
                 rocket.y + 14 * math.cos(math.radians(rocket.angle))
        fl = int(18 + rocket.flame * 34)
        pygame.draw.polygon(
            screen, (255, 170, 40),
            [(fx - 9, fy), (fx + 9, fy),
             (fx + rocket.flame * 4, fy + fl)])
        pygame.draw.polygon(
            screen, (255, 240, 150),
            [(fx - 5, fy), (fx + 5, fy), (fx, fy + int(fl * 0.6))])
    rotated = pygame.transform.rotate(ROCKET_SURF, -rocket.angle)
    rect = rotated.get_rect(center=center)
    screen.blit(rotated, rect)


# --------------------------------------------------------------------------
# world
# --------------------------------------------------------------------------
def draw_world(screen, world, t):
    # home planet: big circle below the ground line
    pygame.draw.circle(screen, (52, 74, 120), (C.PAD_CX, C.GROUND_Y + 240), 400)
    pygame.draw.rect(screen, (44, 62, 100), (0, C.GROUND_Y, C.WIDTH, C.HEIGHT - C.GROUND_Y))
    pygame.draw.line(screen, (120, 150, 200), (0, C.GROUND_Y), (C.WIDTH, C.GROUND_Y), 2)

    # landing pad
    px = int(C.PAD_CX)
    pygame.draw.rect(screen, (70, 74, 84), (px - C.PAD_HALF, C.GROUND_Y - 14, C.PAD_HALF * 2, 16))
    for i in range(10):
        x0 = px - C.PAD_HALF + i * 27
        color = (250, 220, 60) if i % 2 == 0 else (40, 40, 46)
        pygame.draw.rect(screen, color, (x0, C.GROUND_Y - 12, 27, 8))
    pygame.draw.rect(screen, (250, 220, 60), (px - 4, C.GROUND_Y - 14, 8, 4))

    # moon (second planet)
    mx, my, mr = world.moon
    pygame.draw.circle(screen, (150, 156, 170), (mx, my), mr)
    for cx, cy, cr in ((mx - 26, my - 18, 12), (mx + 20, my + 12, 9), (mx + 4, my - 34, 7)):
        pygame.draw.circle(screen, (122, 128, 142), (cx, cy), cr)
    pygame.draw.arc(screen, (90, 200, 120), (mx - mr, my - mr, mr * 2, mr * 2),
                    math.radians(200), math.radians(340), 2)
    pygame.draw.circle(screen, (120, 220, 160), (mx, int(world.moon_top()) - 4), 3)

    # space station
    sx, sy = world.station
    pygame.draw.rect(screen, (170, 180, 220), (sx - 26, sy - 14, 52, 30), border_radius=6)
    pygame.draw.rect(screen, (90, 110, 190), (sx - 40, sy - 6, 14, 18))
    pygame.draw.rect(screen, (90, 110, 190), (sx + 26, sy - 6, 14, 18))
    pygame.draw.circle(screen, (255, 90, 90), (sx, sy - 6), 4)
    # docking port (below the station)
    px2, py2 = world.port
    blink = 255 if int(t * 4) % 2 == 0 else 120
    pygame.draw.rect(screen, (blink, blink, 60), (px2 - 12, py2 - 3, 24, 6))
    pygame.draw.circle(screen, (60, 255, 120), (px2, py2 + 6), 3)


def draw_target(screen, ap):
    """Marker showing where the autopilot is steering towards."""
    if ap.mode == ap.MODE_MANUAL:
        return
    tgt = ap.target()
    if tgt is None:
        return
    tx, ty = tgt[0], tgt[1]
    if tx < -200 or tx > C.WIDTH + 200 or ty < -200 or ty > C.HEIGHT + 200:
        return
    x, y = int(tx), int(ty)
    color = (120, 255, 200)
    pygame.draw.circle(screen, color, (x, y), 10, 2)
    pygame.draw.line(screen, (color[0], color[1], color[2]),
                     (int(ap.r.x), int(ap.r.y)), (x, y), 1)
    label = fonts.font(16).render(ap.phase_label(), True, color)
    screen.blit(label, (x + 14, y - 8))


# --------------------------------------------------------------------------
# HUD
# --------------------------------------------------------------------------
def draw_hud(screen, rocket, ap, fuel_warn, result=None):
    # top mode banner
    banner = fonts.font(30, bold=True)
    color = (120, 255, 200) if ap.mode != ap.MODE_MANUAL else (255, 255, 255)
    text = banner.render(ap.label(), True, color)
    screen.blit(text, (C.WIDTH // 2 - text.get_width() // 2, 12))

    phase = fonts.font(18).render(ap.phase_label(), True, (170, 200, 220))
    screen.blit(phase, (C.WIDTH // 2 - phase.get_width() // 2, 50))

    # left panel
    x0, y0 = 16, 16
    # fuel bar
    label = fonts.font(18).render("FUEL 燃料", True, (220, 220, 220))
    screen.blit(label, (x0, y0))
    bw, bh = 180, 14
    pygame.draw.rect(screen, (60, 60, 66), (x0, y0 + 22, bw, bh))
    frac = max(0.0, rocket.fuel / C.FUEL_CAPACITY)
    fcolor = (255, 90, 90) if frac < 0.2 else (255, 200, 60)
    pygame.draw.rect(screen, fcolor, (x0, y0 + 22, int(bw * frac), bh))
    screen.blit(fonts.font(16).render(f"{rocket.fuel:5.1f}", True, (240, 240, 240)),
                (x0 + bw + 8, y0 + 20))

    y = y0 + 48
    rows = [
        ("ALT 高度", f"{C.GROUND_Y - rocket.y:7.0f} px"),
        ("VSPD 垂直速度", f"{rocket.vy:8.1f} px/s"),
        ("HSPD 水平速度", f"{rocket.vx:8.1f} px/s"),
        ("ANGLE 姿态角", f"{rocket.angle % 360:6.1f} deg"),
        ("THRUST 推力", f"{int(rocket.thrust_frac * 100):4d} %"),
    ]
    for name, val in rows:
        screen.blit(fonts.font(17).render(name, True, (170, 190, 210)), (x0, y))
        screen.blit(fonts.font(17).render(val, True, (240, 240, 240)), (x0 + 150, y))
        y += 26

    # bottom help bar
    help_lines = "W/UP thrust   A/D or LEFT/RIGHT rotate   H hover   L auto land   P moon   D dock   SPACE manual   R restart   ESC quit"
    bar = fonts.font(16).render(help_lines, True, (150, 160, 175))
    screen.blit(bar, (C.WIDTH // 2 - bar.get_width() // 2, C.HEIGHT - 26))

    if fuel_warn:
        w = fonts.font(22, bold=True).render("LOW FUEL 燃料不足!", True, (255, 110, 110))
        screen.blit(w, (C.WIDTH // 2 - w.get_width() // 2, 90))
