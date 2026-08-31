"""Rocket physics: position, velocity, attitude, fuel, thrust.

Supports variable gravity from gravity wells (solar system scale).
"""

import math

from . import config as C


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class Rocket:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0        # degrees, 0 = pointing up, + = clockwise
        self.ang_vel = 0.0      # deg/s
        self.fuel = C.FUEL_CAPACITY
        self.thrust_frac = 0.0  # 0..1, for rendering the flame
        self.flame = 0.0        # smoothed flame size for the animation

    # -- helpers ------------------------------------------------------------
    def thrust_dir(self):
        """Unit vector of the engine thrust (ship's 'up')."""
        a = math.radians(self.angle)
        return (math.sin(a), -math.cos(a))

    def bottom_y(self):
        """Y coordinate of the engine nozzle (bottom of the ship)."""
        a = math.radians(self.angle)
        return self.y + C.ROCKET_HALF_H * math.cos(a)

    def speed(self):
        return math.hypot(self.vx, self.vy)

    # -- integration ---------------------------------------------------------
    def step(self, dt, thrust_frac, ang_accel, world):
        """Update rocket state.

        Args:
            dt: time step (already multiplied by time scale)
            thrust_frac: 0..1 thrust level
            ang_accel: angular acceleration in deg/s^2
            world: World object with gravity wells
        """
        # attitude
        self.ang_vel = clamp(self.ang_vel + ang_accel * dt,
                             -C.MAX_ANG_VEL, C.MAX_ANG_VEL)
        self.angle = (self.angle + self.ang_vel * dt) % 360.0

        # engine
        if self.fuel <= 0.0:
            thrust_frac = 0.0
        self.thrust_frac = clamp(thrust_frac, 0.0, 1.0)
        if self.thrust_frac > 0.0:
            tx, ty = self.thrust_dir()
            a = C.MAX_THRUST * self.thrust_frac
            self.vx += tx * a * dt
            self.vy += ty * a * dt
            self.fuel = max(0.0, self.fuel - C.FUEL_BURN_RATE * self.thrust_frac * dt)

        # gravity from all planets (variable gravity)
        gx, gy = world.get_total_gravity(self.x, self.y)
        self.vx += gx * dt
        self.vy += gy * dt

        # integrate position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # flame animation smoothing
        self.flame += (self.thrust_frac - self.flame) * min(1.0, dt * 12.0)
