"""All rendering: stars, planets, station, rocket, flame, HUD, trajectory.

Inspired by Simple Rockets (简单火箭) - 2D side-view rocket game with:
- Camera that follows the rocket
- Trajectory prediction visualization
- Distance indicators and visual guidance
- Star rating system for landing quality
- Time acceleration display
"""

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
        # Generate stars in a larger area for parallax scrolling
        self.stars = []
        for _ in range(300):
            # Stars spread across a wider area for parallax effect
            x = random.randrange(C.WIDTH * 3) - C.WIDTH
            y = random.randrange(C.HEIGHT * 3) - C.HEIGHT
            size = random.choice((1, 1, 1, 2))
            phase = random.random()
            self.stars.append((x, y, size, phase))

    def draw(self, screen, t, camera=None):
        """Draw stars with parallax effect (parallax based on camera position)."""
        if camera:
            # Parallax: stars move slower than camera for depth effect
            # Use 0.15 for subtle parallax (like Simple Rockets)
            parallax_x = camera.x * 0.15
            parallax_y = camera.y * 0.15

            for x, y, s, ph in self.stars:
                # Apply parallax offset
                px = x - parallax_x
                py = y - parallax_y

                # Wrap around screen for seamless scrolling (handle negative values)
                px = ((px % C.WIDTH) + C.WIDTH) % C.WIDTH
                py = ((py % C.HEIGHT) + C.HEIGHT) % C.HEIGHT

                # Twinkle effect
                b = 120 + int(80 * math.sin(t * 2.0 + ph * 6.28))
                color = (b, b, min(255, b + 30))
                pygame.draw.rect(screen, color, (int(px), int(py), s, s))
        else:
            # No camera: draw stars normally
            for x, y, s, ph in self.stars:
                b = 120 + int(80 * math.sin(t * 2.0 + ph * 6.28))
                pygame.draw.rect(screen, (b, b, b + 20), (int(x), int(y), s, s))


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


def draw_rocket(screen, rocket, camera=None):
    """Draw rocket with flame, using camera offset if provided."""
    if camera:
        cx, cy = camera.to_screen(rocket.x, rocket.y)
    else:
        cx, cy = int(rocket.x), int(rocket.y)

    # flame (drawn first, under the body)
    if rocket.flame > 0.02:
        fx = cx - 8 * math.sin(math.radians(rocket.angle))
        fy = cy + 14 * math.cos(math.radians(rocket.angle))
        fl = int(18 + rocket.flame * 34)
        pygame.draw.polygon(
            screen, (255, 170, 40),
            [(fx - 9, fy), (fx + 9, fy),
             (fx + rocket.flame * 4, fy + fl)])
        pygame.draw.polygon(
            screen, (255, 240, 150),
            [(fx - 5, fy), (fx + 5, fy), (fx, fy + int(fl * 0.6))])

    rotated = pygame.transform.rotate(ROCKET_SURF, -rocket.angle)
    rect = rotated.get_rect(center=(cx, cy))
    screen.blit(rotated, rect)


# --------------------------------------------------------------------------
# world
# --------------------------------------------------------------------------
def draw_world(screen, world, camera):
    """Draw world objects with camera offset."""
    def to_screen(wx, wy):
        if camera:
            return camera.to_screen(wx, wy)
        return (wx, wy)

    # Home planet (large circle below the ground line)
    home = world.planets[0]
    px, py = to_screen(home.x, home.y)
    pygame.draw.circle(screen, (52, 74, 120), (px, py), int(home.radius))

    # Ground line (top of home planet)
    gx, gy = to_screen(0, home.y - home.radius)
    pygame.draw.rect(screen, (44, 62, 100), (gx, gy, C.WIDTH + 20, C.HEIGHT - gy + 20))
    pygame.draw.line(screen, (120, 150, 200), (gx, gy), (gx + C.WIDTH + 20, gy), 2)

    # Landing pad on home planet
    px_pad, py_pad = to_screen(world.pad_cx, world.pad_y - 14)
    pygame.draw.rect(screen, (70, 74, 84), (px_pad - world.pad_half, py_pad, world.pad_half * 2, 16))
    for i in range(10):
        x0 = px_pad - world.pad_half + i * 27
        color = (250, 220, 60) if i % 2 == 0 else (40, 40, 46)
        pygame.draw.rect(screen, color, (x0, py_pad + 2, 27, 8))
    pygame.draw.rect(screen, (250, 220, 60), (px_pad - 4, py_pad, 8, 4))

    # Moon (second planet)
    moon = world.planets[1]
    msx, msy = to_screen(moon.x, moon.y)
    pygame.draw.circle(screen, (150, 156, 170), (msx, msy), int(moon.radius))
    # Craters
    for cx, cy, cr in ((moon.x - 26, moon.y - 18, 12), (moon.x + 20, moon.y + 12, 9), (moon.x + 4, moon.y - 34, 7)):
        csx, csy = to_screen(cx, cy)
        pygame.draw.circle(screen, (122, 128, 142), (csx, csy), cr)
    # Atmosphere glow (if has atmosphere)
    if moon.name != 'Moon':
        pygame.draw.arc(screen, (90, 200, 120), (msx - moon.radius, msy - moon.radius, moon.radius * 2, moon.radius * 2),
                        math.radians(200), math.radians(340), 2)
    # Landing marker
    lmx, lmy = to_screen(moon.x, world.moon_top())
    pygame.draw.circle(screen, (120, 220, 160), (lmx, lmy - 4), 3)

    # Space station (orbiting home planet)
    sx, sy = world.port_x - 34, world.port_y - 34  # approximate station position
    ssx, ssy = to_screen(sx, sy)
    pygame.draw.rect(screen, (170, 180, 220), (ssx - 26, ssy - 14, 52, 30), border_radius=6)
    pygame.draw.rect(screen, (90, 110, 190), (ssx - 40, ssy - 6, 14, 18))
    pygame.draw.rect(screen, (90, 110, 190), (ssx + 26, ssy - 6, 14, 18))
    pygame.draw.circle(screen, (255, 90, 90), (ssx, ssy - 6), 4)
    # Docking port (below the station)
    px2, py2 = world.port_x, world.port_y
    psx2, psy2 = to_screen(px2, py2)
    blink = 255 if int(pygame.time.get_ticks() / 250) % 2 == 0 else 120
    pygame.draw.rect(screen, (blink, blink, 60), (psx2 - 12, psy2 - 3, 24, 6))
    pygame.draw.circle(screen, (60, 255, 120), (psx2, psy2 + 6), 3)


def draw_target(screen, ap, camera):
    """Marker showing where the autopilot is steering towards."""
    if ap.mode == ap.MODE_MANUAL:
        return
    tgt = ap.target()
    if tgt is None:
        return
    tx, ty = tgt[0], tgt[1]

    # Convert to screen coords
    if camera:
        sx, sy = camera.to_screen(tx, ty)
    else:
        sx, sy = tx, ty

    # Only draw if on screen (with margin)
    if sx < -60 or sx > C.WIDTH + 60 or sy < -60 or sy > C.HEIGHT + 60:
        return

    color = (120, 255, 200)
    pygame.draw.circle(screen, color, (int(sx), int(sy)), 10, 2)
    # Line from rocket to target
    if camera:
        rx, ry = camera.to_screen(ap.r.x, ap.r.y)
    else:
        rx, ry = int(ap.r.x), int(ap.r.y)
    pygame.draw.line(screen, (color[0], color[1], color[2]),
                     (rx, ry), (int(sx), int(sy)), 1)
    label = fonts.font(16).render(ap.phase_label(), True, color)
    screen.blit(label, (int(sx) + 14, int(sy) - 8))


def draw_trajectory(screen, predictor, rocket, thrust_frac, ang_accel, camera, world):
    """Draw predicted trajectory path (like Simple Rockets / KSP).

    Uses dots with fading opacity for a cleaner, more professional look.
    """
    points = predictor.predict(rocket, thrust_frac, ang_accel, world)

    if camera:
        screen_points = [camera.to_screen(x, y) for x, y in points]
    else:
        screen_points = [(x, y) for x, y in points]

    # Draw trajectory as dots with fading opacity
    for i, (sx, sy) in enumerate(screen_points):
        # Only draw if on screen
        if sx < -10 or sx > C.WIDTH + 10 or sy < -10 or sy > C.HEIGHT + 10:
            continue

        # Fade out older points (more recent = brighter)
        alpha = int(255 * (1.0 - i / len(screen_points)))
        alpha = max(30, alpha)

        # Color: green for trajectory, brighter for recent points
        color = (100, 255, 180)

        # Draw dot (small circle)
        radius = max(1, int(2 * (1.0 - i / len(screen_points))))
        pygame.draw.circle(screen, color, (int(sx), int(sy)), radius)


def calculate_star_rating(rocket, world, ap):
    """Calculate landing quality rating (1-5 stars).

    Based on:
    - Landing speed (lower is better)
    - Landing angle (closer to vertical is better)
    - Landing precision (closer to center of pad is better)
    """
    score = 0

    # Speed score (max 2 stars)
    if rocket.vy <= 30:
        score += 1
    if rocket.vy <= 15:
        score += 1

    # Angle score (max 2 stars)
    angle_err = abs(ap._wrap_angle(rocket.angle)) if hasattr(ap, '_wrap_angle') else abs(rocket.angle % 360)
    if angle_err <= 5:
        score += 1
    if angle_err <= 10:
        score += 1

    # Precision score (max 1 star)
    if abs(rocket.x - world.pad_cx) < 20:
        score += 1

    return min(score, 5)


def draw_hud(screen, rocket, ap, fuel_warn, result=None, camera=None, world=None):
    """Draw HUD with all game information."""
    # Top mode banner
    banner = fonts.font(30, bold=True)
    color = (120, 255, 200) if ap.mode != ap.MODE_MANUAL else (255, 255, 255)
    text = banner.render(ap.label(), True, color)
    screen.blit(text, (C.WIDTH // 2 - text.get_width() // 2, 12))

    phase = fonts.font(18).render(ap.phase_label(), True, (170, 200, 220))
    screen.blit(phase, (C.WIDTH // 2 - phase.get_width() // 2, 50))

    # Time scale display (like KSP)
    time_text = f"TIME {world.time_scale}x"
    time_surf = fonts.font(16).render(time_text, True, (200, 200, 220))
    screen.blit(time_surf, (C.WIDTH - time_surf.get_width() - 16, 12))

    # Left panel
    x0, y0 = 16, 16
    # Fuel bar
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
        ("ALT 高度", f"{C.GROUND_Y - rocket.y:7.0f} m"),
        ("VSPD 垂直速度", f"{rocket.vy:8.1f} m/s"),
        ("HSPD 水平速度", f"{rocket.vx:8.1f} m/s"),
        ("ANGLE 姿态角", f"{rocket.angle % 360:6.1f} deg"),
        ("THRUST 推力", f"{int(rocket.thrust_frac * 100):4d} %"),
        ("GRAV 重力", f"{world.get_total_gravity(rocket.x, rocket.y)[1]:7.1f} m/s²"),
    ]
    for name, val in rows:
        screen.blit(fonts.font(17).render(name, True, (170, 190, 210)), (x0, y))
        screen.blit(fonts.font(17).render(val, True, (240, 240, 240)), (x0 + 150, y))
        y += 26

    # Distance to target (like Simple Rockets)
    if ap.mode != ap.MODE_MANUAL:
        tgt = ap.target()
        if tgt:
            tx, ty = tgt[0], tgt[1]
            dist = math.hypot(rocket.x - tx, rocket.y - ty)
            dist_text = f"DIST 距离: {dist:6.0f} m"
            dist_surf = fonts.font(16).render(dist_text, True, (200, 200, 220))
            screen.blit(dist_surf, (x0, y + 10))

    # Bottom help bar
    help_lines = "W/UP thrust   A/D or LEFT/RIGHT rotate   H hover   L auto land   P moon   D dock   SPACE manual   R restart   ESC quit   T time accel   F12 screenshot"
    bar = fonts.font(16).render(help_lines, True, (150, 160, 175))
    screen.blit(bar, (C.WIDTH // 2 - bar.get_width() // 2, C.HEIGHT - 26))

    if fuel_warn:
        w = fonts.font(22, bold=True).render("LOW FUEL 燃料不足!", True, (255, 110, 110))
        screen.blit(w, (C.WIDTH // 2 - w.get_width() // 2, 90))

    # Star rating for landing (shown after landing)
    if result and result in ("landed_pad", "landed_moon"):
        stars = calculate_star_rating(rocket, world, ap)
        star_str = "★" * stars + "☆" * (5 - stars)
        star_surf = fonts.font(36).render(star_str, True, (255, 220, 60))
        screen.blit(star_surf, (C.WIDTH // 2 - star_surf.get_width() // 2, 120))
