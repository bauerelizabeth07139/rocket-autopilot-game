"""Rocket Autopilot — 2D rocket game with manual flight and four
autopilot modes: hover, auto landing on the pad, auto landing on the
moon, and auto docking with the space station.

Run:            python main.py
Self-test:      python main.py --selftest
Screenshot:     press F12 during gameplay

Inspired by Simple Rockets (简单火箭) - a 2D side-view rocket game similar
to Kerbal Space Program (KSP). Features camera follow, trajectory prediction,
visual guidance, and star rating.

Future features (in progress):
- Solar system scale map with multiple planets
- Time acceleration (1x to 256x)
- Gravity wells (stronger near planets, weaker in deep space)
- Orbital mechanics
"""

import math
import os
import sys

import pygame

from game import fonts
from game import hud
from game.autopilot import Autopilot
from game.config import FPS, GROUND_Y, HEIGHT, TITLE, WIDTH, SCREENSHOT_DIR
from game.rocket import Rocket
from game.rules import check_docked, resolve_contact
from game.world import Camera, TrajectoryPredictor, World


def restart(rocket, ap, world, camera):
    rocket.__init__(300.0, 300.0)
    ap.to_manual()
    camera.x = 0.0
    camera.y = 0.0


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
        "crash_home": ("HIT THE HOME PLANET 撞上母星!", "You flew into the home planet's body. 飞船撞上了母星."),
    }
    return table.get(result, ("GAME OVER", ""))


def draw_start_menu(screen, t):
    """Draw the start menu with mode selection (like Simple Rockets)."""
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Title
    title = fonts.font(48, bold=True)
    title_text = title.render("ROCKET AUTOPILOT", True, (120, 255, 200))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))

    subtitle = fonts.font(24).render("火箭自动驾驶 — 简单火箭风格", True, (200, 220, 240))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 140))

    # Mode buttons
    modes = [
        ("HOVER 悬停", "hover", (100, 180, 255)),
        ("LAND 自动降落", "land", (100, 255, 150)),
        ("MOON 登陆星球", "moon", (200, 200, 255)),
        ("DOCK 自动对接", "dock", (255, 150, 100)),
    ]

    btn_y = 200
    for label, mode_key, color in modes:
        btn_w, btn_h = 300, 50
        btn_x = WIDTH // 2 - btn_w // 2

        # Button background
        hover = pygame.mouse.get_pos()[0] > btn_x and pygame.mouse.get_pos()[0] < btn_x + btn_w
        bg_color = (color[0] + 40, color[1] + 40, color[2] + 40) if hover else color
        pygame.draw.rect(screen, bg_color, (btn_x, btn_y, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(screen, color, (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)

        # Button text
        btn_text = fonts.font(22, bold=True).render(label, True, (255, 255, 255))
        screen.blit(btn_text, (WIDTH // 2 - btn_text.get_width() // 2, btn_y + 12))

        btn_y += 70

    # Instructions
    instructions = [
        "W/↑ 推力  A/D/←/→ 旋转",
        "H 悬停  L 自动降落  P 登陆月球  D 自动对接",
        "空格/退格 切回手动  R 重新开始  ESC 退出",
        "F12 截图  鼠标点击菜单选择模式",
    ]
    for i, text in enumerate(instructions):
        line = fonts.font(16).render(text, True, (180, 190, 210))
        screen.blit(line, (WIDTH // 2 - line.get_width() // 2, 480 + i * 24))

    # Click handler for mode selection
    mouse_pos = pygame.mouse.get_pos()
    btn_y = 200
    for label, mode_key, color in modes:
        btn_w, btn_h = 300, 50
        btn_x = WIDTH // 2 - btn_w // 2
        if (btn_x <= mouse_pos[0] <= btn_x + btn_w and
                btn_y <= mouse_pos[1] <= btn_y + btn_h):
            return mode_key
        btn_y += 70

    return None


def main(demo=None, demo_mode="dock"):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    bg = hud.Background()
    world = World()
    rocket = Rocket(300.0, 300.0)
    ap = Autopilot(rocket, world)
    camera = Camera()
    predictor = TrajectoryPredictor(steps=30, sample_every=8)

    result = None            # last game outcome
    state = "menu"           # "menu" | "playing" | "finished"
    t = 0.0
    demo_engaged = False
    screenshot_count = 0

    # Ensure screenshot directory exists
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    while True:
        # Apply time scale to dt
        dt = clock.tick(FPS) / 1000.0 * world.time_scale
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return 0

                # Time acceleration with T key
                if event.key == pygame.K_t:
                    world.next_time_scale()

                # Screenshot on F12
                if event.key == pygame.K_f12:
                    path = os.path.join(SCREENSHOT_DIR, f"screenshot_{screenshot_count:03d}.png")
                    pygame.image.save(screen, path)
                    print(f"Screenshot saved: {path}")
                    screenshot_count += 1

                if event.key == pygame.K_r and state == "finished":
                    state = "playing"
                    result = None
                    restart(rocket, ap, world, camera)

            if event.type == pygame.MOUSEBUTTONDOWN and state == "menu":
                # Handle menu mode selection
                modes = [
                    ("hover", (100, 180, 255)),
                    ("land", (100, 255, 150)),
                    ("moon", (200, 200, 255)),
                    ("dock", (255, 150, 100)),
                ]
                btn_y = 200
                for mode_key, color in modes:
                    btn_w, btn_h = 300, 50
                    btn_x = WIDTH // 2 - btn_w // 2
                    if (btn_x <= event.pos[0] <= btn_x + btn_w and
                            btn_y <= event.pos[1] <= btn_y + btn_h):
                        mode_map = {
                            "hover": Autopilot.MODE_HOVER,
                            "land": Autopilot.MODE_LAND,
                            "moon": Autopilot.MODE_MOON,
                            "dock": Autopilot.MODE_DOCK,
                        }
                        demo = mode_map[mode_key]
                        state = "playing"
                        demo_engaged = True
                        break
                    btn_y += 70

        keys = pygame.key.get_pressed()

        # --- menu mode -----------------------------------------------------
        if state == "menu":
            draw_start_menu(screen, t)
            pygame.display.flip()
            continue

        # --- playing / finished ------------------------------------------
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

        # --- demo mode: engage an autopilot automatically ----------------
        if demo and not demo_engaged and t > 0.1:
            demo_engaged = True
            ap.engage(demo)

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

            rocket.step(dt, thrust, ang, world)

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
            rocket.step(dt, 0.0, 0.0, world)
            # keep the rocket visible on screen after a crash
            if rocket.y > GROUND_Y + 200:
                rocket.vy = 0.0
                rocket.y = GROUND_Y + 200

        # --- camera update -----------------------------------------------
        camera.update(rocket, dt)

        # --- rendering ---------------------------------------------------
        bg.draw(screen, t, camera)
        hud.draw_world(screen, world, camera)

        # Trajectory prediction (only in manual or when thrust is on)
        if ap.mode == ap.MODE_MANUAL and (thrust > 0 or keys[pygame.K_UP] or keys[pygame.K_w]):
            hud.draw_trajectory(screen, predictor, rocket, thrust, ang, camera, world)

        hud.draw_target(screen, ap, camera)
        hud.draw_rocket(screen, rocket, camera)
        fuel_warn = rocket.fuel < 20.0
        hud.draw_hud(screen, rocket, ap, fuel_warn, result, camera, world)

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
