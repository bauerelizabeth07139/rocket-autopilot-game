"""Rocket Autopilot — 2D rocket game with manual flight and four
autopilot modes: hover, auto landing on the pad, auto landing on the
moon, and auto docking with the space station.

Run:            python main.py
Self-test:      python main.py --selftest
"""

import math
import sys

import pygame

from game import fonts
from game import hud
from game.autopilot import Autopilot
from game.config import FPS, GROUND_Y, HEIGHT, TITLE, WIDTH
from game.rocket import Rocket
from game.rules import check_docked, resolve_contact
from game.world import World


def restart(rocket, ap, world):
    rocket.__init__(300.0, 300.0)
    ap.to_manual()


def main(demo=None, demo_mode="dock"):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    bg = hud.Background()
    world = World()
    rocket = Rocket(300.0, 300.0)
    ap = Autopilot(rocket, world)

    result = None            # last game outcome
    state = "playing"        # "playing" | "finished"
    t = 0.0
    demo_engaged = False

    while True:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return 0
                if event.key == pygame.K_r and state == "finished":
                    state = "playing"
                    result = None
                    restart(rocket, ap, world)

        keys = pygame.key.get_pressed()

        # --- demo mode: engage an autopilot automatically ----------------
        if demo and not demo_engaged and t > 0.1:
            demo_engaged = True
            ap.engage(demo)

        # --- autopilot mode switching -----------------------------------
        if keys[pygame.K_h]:
            ap.engage(ap.MODE_HOVER)
        elif keys[pygame.K_l]:
            ap.engage(ap.MODE_LAND)
        elif keys[pygame.K_p]:
            ap.engage(ap.MODE_MOON)
        elif keys[pygame.K_d]:
            ap.engage(ap.MODE_DOCK)
        elif keys[pygame.K_SPACE] or keys[pygame.K_BACKSPACE]:
            ap.to_manual()

        # --- controls ----------------------------------------------------
        if state == "playing":
            if ap.mode == ap.MODE_MANUAL:
                thrust = 1.0 if (keys[pygame.K_UP] or keys[pygame.K_w]) else 0.0
                ang = 0.0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    ang = -260.0
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    ang = 260.0
            else:
                thrust, ang = ap.update(dt)

            rocket.step(dt, thrust, ang)

            # outcome checks
            if check_docked(rocket, world, ap):
                result = "docked"
                state = "finished"
            if state == "playing":
                outcome = resolve_contact(rocket, world, ap)
                if outcome:
                    result = outcome
                    state = "finished"
        else:
            rocket.step(dt, 0.0, 0.0)
            # keep the rocket visible on screen after a crash
            if rocket.y > GROUND_Y + 200:
                rocket.vy = 0.0
                rocket.y = GROUND_Y + 200

        # --- rendering ---------------------------------------------------
        bg.draw(screen, t)
        hud.draw_world(screen, world, t)
        hud.draw_target(screen, ap)
        hud.draw_rocket(screen, rocket)
        fuel_warn = rocket.fuel < 20.0
        hud.draw_hud(screen, rocket, ap, fuel_warn, result)

        if state == "finished":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg, sub = outcome_text(result)
            big = fonts.font(54, bold=True)
            col = (120, 255, 200) if result in ("landed_pad", "landed_moon",
                                                "docked") else (255, 120, 120)
            line = big.render(msg, True, col)
            screen.blit(line, (WIDTH // 2 - line.get_width() // 2, HEIGHT // 2 - 60))
            sub_line = fonts.font(24).render(sub, True, (220, 220, 220))
            screen.blit(sub_line, (WIDTH // 2 - sub_line.get_width() // 2, HEIGHT // 2 + 10))
            hint = fonts.font(20).render("Press R to restart  按 R 重新开始", True, (180, 190, 200))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()


def outcome_text(result):
    table = {
        "landed_pad": ("PERFECT LANDING 完美降落!",
                       "Landed on the pad. 成功降落在降落坪上."),
        "landed_moon": ("MOON LANDING SUCCESS 登陆成功!",
                        "You touched down on the moon. 成功登陆月球."),
        "landed_planet": ("LANDED ON PLANET 降落在星球表面",
                          "Safe but not on the pad. 安全降落,但不在降落坪上."),
        "docked": ("DOCKING SUCCESS 对接成功!",
                   "Latched onto the station port. 成功对接空间站."),
        "crash": ("CRASH 坠毁!", "Touchdown too fast or tilted. 着陆速度过快或姿态倾斜."),
        "crash_moon": ("HIT THE MOON 撞上月球!", "You flew into the moon's body. 飞船撞上了月球."),
    }
    return table.get(result, ("GAME OVER", ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        from game.selftest import run
        sys.exit(run())
    demo = None
    if "--demo" in args:
        mode = "dock"
        for a in args:
            if a.startswith("--mode="):
                mode = a.split("=", 1)[1]
        demo = {"hover": Autopilot.MODE_HOVER,
                "land": Autopilot.MODE_LAND,
                "moon": Autopilot.MODE_MOON,
                "dock": Autopilot.MODE_DOCK}.get(mode, Autopilot.MODE_DOCK)
    sys.exit(main(demo=demo))
