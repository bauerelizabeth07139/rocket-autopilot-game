"""Shared outcome rules: contact resolution and docking detection.

These are used both by the interactive game loop and the headless
self-tests, so the autopilot is verified by the same logic the player
sees.
"""

import math

from . import config as C


def wrap_angle(deg):
    return (deg + 180.0) % 360.0 - 180.0


def check_docked(rocket, world, ap):
    """Return True once the rocket is latched onto the station port."""
    if ap.mode != ap.MODE_DOCK or ap.phase != "final":
        return False
    px, py = world.port
    if math.hypot(rocket.x - px, rocket.y - py) < C.DOCK_DIST \
            and abs(rocket.vx) + abs(rocket.vy) < C.DOCK_SPEED \
            and abs(wrap_angle(rocket.angle)) < C.DOCK_ANGLE:
        return True
    return False


def resolve_contact(rocket, world, ap):
    """Evaluate a touchdown on a solid surface.

    Returns one of: "landed_pad", "landed_moon", "landed_planet", "crash",
    "crash_moon" or None when there is no contact yet.
    """
    if world.moon_hit(rocket.x, rocket.y):
        return "crash_moon"

    if rocket.vy <= 0.0:
        return None

    surface = world.surface_y_at(rocket.x)
    if rocket.bottom_y() < surface:
        return None

    # touchdown
    good = (abs(wrap_angle(rocket.angle)) <= C.MAX_LAND_ANGLE
            and rocket.vy <= C.MAX_LAND_SPEED
            and abs(rocket.vx) <= C.MAX_LAND_VX)
    if not good:
        return "crash"
    if surface == world.moon_top():
        return "landed_moon"
    if abs(rocket.x - world.pad_cx) <= world.pad_half:
        return "landed_pad"
    return "landed_planet"
