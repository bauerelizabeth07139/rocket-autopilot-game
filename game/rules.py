"""Shared outcome rules: contact resolution and docking detection.

These are used both by the interactive game loop and the headless
self-tests, so the autopilot is verified by the same logic the player
sees.

Supports solar system scale with multiple planets and gravity wells.
"""

import math

from . import config as C


def wrap_angle(deg):
    return (deg + 180.0) % 360.0 - 180.0


def check_docked(rocket, world, ap):
    """Return True once the rocket is latched onto the station port."""
    if ap.mode != ap.MODE_DOCK or ap.phase != "final":
        return False
    px, py = world.port_x, world.port_y
    if math.hypot(rocket.x - px, rocket.y - py) < C.DOCK_DIST \
            and abs(rocket.vx) + abs(rocket.vy) < C.DOCK_SPEED \
            and abs(wrap_angle(rocket.angle)) < C.DOCK_ANGLE:
        return True
    return False


def resolve_contact(rocket, world, ap):
    """Evaluate a touchdown on a solid surface.

    Returns one of: "landed_pad", "landed_moon", "landed_planet", "crash",
    "crash_moon", "crash_home" or None when there is no contact yet.
    """
    # Check moon collision
    if world.moon_hit(rocket.x, rocket.y):
        return "crash_moon"

    # Check home planet collision
    if world.home_hit(rocket.x, rocket.y):
        return "crash_home"

    if rocket.vy <= 0.0:
        return None

    bottom = rocket.bottom_y()
    mx, my, mr = world.planets[1].x, world.planets[1].y, world.planets[1].radius
    in_moon_x = abs(rocket.x - mx) < mr - 8.0
    if in_moon_x and rocket.y < my and bottom >= world.moon_top():
        surface = world.moon_top()
    elif bottom >= world.pad_y:
        surface = world.pad_y
    else:
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
