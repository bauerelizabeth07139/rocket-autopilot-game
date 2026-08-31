"""The play area: home planet with landing pad, a second planet (moon)
and a space station with a docking port.

Basic gravity system: each planet exerts gravitational pull based on
inverse-square law. Gravity is stronger near planets, weaker in deep space.
"""

import math

from . import config as C


class GravityWell:
    """A celestial body that exerts gravitational pull.

    Gravity follows inverse-square law: g = G * M / r^2
    Where G is the gravity constant, M is the mass, r is the distance.
    """

    def __init__(self, name, x, y, radius, mass, surface_gravity):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.surface_gravity = surface_gravity  # gravity at surface

    def gravity_at(self, px, py):
        """Calculate gravitational acceleration at position (px, py).

        Returns (gx, gy) tuple - acceleration vector in px/s^2.
        Gravity follows inverse-square law: g = G * M / r^2
        """
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)

        # Don't apply gravity inside the planet
        if dist < self.radius:
            return (0.0, 0.0)

        # Calculate gravity using inverse-square law:
        # g = surface_gravity * (radius / dist)^2
        g_mag = self.surface_gravity * (self.radius / dist) ** 2

        # Direction: toward the planet centre
        gx = -g_mag * dx / dist
        gy = -g_mag * dy / dist

        return (gx, gy)

    def is_hit(self, px, py):
        """True when the rocket has hit this planet's surface."""
        dist = math.hypot(px - self.x, py - self.y)
        return dist < self.radius - 8.0


class World:
    """World with multiple gravity wells (planets)."""

    def __init__(self):
        # Create gravity wells (planets)
        # Home planet: large, with atmosphere
        # Centre at (640, 1100), radius 440, so top is at y=660 (GROUND_Y)
        self.planets = [
            GravityWell(
                'Home',
                C.PAD_CX,           # centre x (at pad location)
                C.GROUND_Y + 440,   # centre y (below ground)
                440.0,              # radius (top at y=660)
                1e6,                # mass
                C.GRAVITY,          # surface gravity
            ),
            # Moon: smaller, no atmosphere
            # Real moon gravity is ~1/6 of Earth (0.165 ratio)
            # Reduce to 1/8 for easier landing in game
            GravityWell(
                'Moon',
                C.MOON[0],          # x
                C.MOON[1],          # y
                C.MOON[2],          # radius
                1e5,                # mass (1/10 of home)
                C.GRAVITY * 0.125,  # surface gravity (~1/8 of home)
            ),
        ]

        # Landing pad on home planet (relative to planet centre)
        self.pad_cx = C.PAD_CX
        self.pad_half = C.PAD_HALF
        self.pad_y = C.GROUND_Y  # top of home planet (ground level)

        # Space station position (orbiting home planet)
        self.station_x = C.STATION[0]
        self.station_y = C.STATION[1]
        self.port_x = C.STATION[0]
        self.port_y = C.STATION[1] + C.STATION_PORT_Y

        # Time acceleration
        self.time_scale = C.DEFAULT_TIME_SCALE
        self.time_scale_index = 0

    def get_total_gravity(self, px, py):
        """Calculate total gravitational acceleration from all planets.

        Returns (gx, gy) tuple - combined acceleration vector.
        """
        gx, gy = (0.0, 0.0)
        for planet in self.planets:
            pgx, pgy = planet.gravity_at(px, py)
            gx += pgx
            gy += pgy
        return (gx, gy)

    def moon_top(self):
        """Get the top Y coordinate of the moon."""
        return self.moon[1] - self.moon[2]

    def moon_hit(self, x, y):
        """True when the rocket has hit the moon's body."""
        return self.planets[1].is_hit(x, y)

    def home_hit(self, x, y):
        """True when the rocket has hit the home planet's body."""
        return self.planets[0].is_hit(x, y)

    def next_time_scale(self):
        """Cycle to next time acceleration level."""
        self.time_scale_index = (self.time_scale_index + 1) % len(C.TIME_SCALES)
        self.time_scale = C.TIME_SCALES[self.time_scale_index]
        return self.time_scale

    def prev_time_scale(self):
        """Cycle to previous time acceleration level."""
        self.time_scale_index = (self.time_scale_index - 1) % len(C.TIME_SCALES)
        self.time_scale = C.TIME_SCALES[self.time_scale_index]
        return self.time_scale

    @property
    def moon(self):
        return C.MOON


class Camera:
    """Smooth camera that follows the rocket (like Simple Rockets / KSP).

    The camera centers on the rocket and smoothly follows it as it moves.
    """

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

    def update(self, rocket, dt):
        """Update camera to follow rocket with smooth interpolation."""
        # Target: center of screen at rocket position
        self.target_x = rocket.x - C.CAM_W / 2
        self.target_y = rocket.y - C.CAM_H / 2

        # Clamp to world bounds (allow some overflow for visual context)
        self.target_x = max(-400, min(self.target_x, C.WIDTH + 400))
        self.target_y = max(-400, min(self.target_y, C.HEIGHT + 400))

        # Smooth follow (higher = snappier, lower = smoother)
        self.x += (self.target_x - self.x) * C.CAM_SMOOTH
        self.y += (self.target_y - self.y) * C.CAM_SMOOTH

    def to_screen(self, wx, wy):
        """Convert world coordinates to screen coordinates."""
        return (wx - self.x, wy - self.y)

    def to_world(self, sx, sy):
        """Convert screen coordinates to world coordinates."""
        return (sx + self.x, sy + self.y)


class TrajectoryPredictor:
    """Predict future rocket trajectory based on current state and gravity.

    This is a key visual aid in Simple Rockets / KSP - shows where the
    rocket will go if you maintain current thrust, accounting for gravity.
    """

    def __init__(self, steps=30, sample_every=8):
        self.steps = steps
        self.sample_every = sample_every

    def predict(self, rocket, thrust_frac, ang_accel, world):
        """Predict trajectory points (world coordinates).

        Returns list of (x, y) tuples representing the predicted path.
        """
        points = []
        x, y = rocket.x, rocket.y
        vx, vy = rocket.vx, rocket.vy
        angle = rocket.angle
        ang_vel = rocket.ang_vel

        # Use actual time scale for prediction
        dt = (1.0 / 60.0) * world.time_scale

        for i in range(self.steps):
            # Get gravity at current position
            gx, gy = world.get_total_gravity(x, y)

            # Apply attitude
            ang_vel = max(-C.MAX_ANG_VEL, min(C.MAX_ANG_VEL, ang_vel + ang_accel * dt))
            angle = (angle + ang_vel * dt) % 360.0

            # Apply thrust
            if thrust_frac > 0:
                a = math.radians(angle)
                tx, ty = math.sin(a), -math.cos(a)
                a_mag = C.MAX_THRUST * thrust_frac
                vx += tx * a_mag * dt
                vy += ty * a_mag * dt

            # Apply gravity
            vx += gx * dt
            vy += gy * dt

            # Integrate position
            x += vx * dt
            y += vy * dt

            # Sample every N steps to reduce density
            if i % self.sample_every == 0:
                points.append((x, y))

        return points
