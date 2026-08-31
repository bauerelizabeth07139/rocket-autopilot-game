"""Autopilot: PID flight controller with a phase state machine.

Control law
-----------
The rocket can only rotate and fire its engine along its own axis, so the
autopilot computes a desired net acceleration (position error * kp +
velocity error * kd), then adds gravity compensation to get the required
engine acceleration vector.  The ship is steered so its thrust axis points
along that vector, and the throttle is set from the projection of the
engine axis onto it.  This single law covers hover, waypoint transit and
controlled descents; the mode state machine only has to pick (target,
target velocity, phase).

Supports variable gravity (from gravity wells) for solar system scale.
"""

import math

from . import config as C
from .rocket import clamp


def wrap_angle(deg):
    return (deg + 180.0) % 360.0 - 180.0


class Autopilot:
    MODE_MANUAL = "manual"
    MODE_HOVER = "hover"
    MODE_LAND = "land"     # auto landing on the home-planet pad
    MODE_MOON = "moon"     # auto landing on the second planet (moon)
    MODE_DOCK = "dock"     # auto docking with the space station

    PHASE_LABELS = {
        "hold": "HOLD POSITION 悬停",
        "climb": "CLIMB 爬升",
        "transit": "TRANSIT 巡航",
        "approach": "APPROACH 接近",
        "descend": "DESCENT 下降",
        "final": "FINAL APPROACH 最终接近",
    }

    def __init__(self, rocket, world):
        self.r = rocket
        self.w = world
        self.mode = self.MODE_MANUAL
        self.phase = "idle"
        self.hx = 0.0
        self.hy = 0.0
        self.cruise_y = 0.0
        self.finished = None   # "landed_pad" | "landed_moon" | "docked" | "crash_*"

    # Expose wrap_angle for external use (e.g., HUD star rating)
    def _wrap_angle(self, deg):
        return wrap_angle(deg)

    # -- mode switching ------------------------------------------------------
    def engage(self, mode):
        r = self.r
        self.finished = None
        self.mode = mode
        if mode == self.MODE_HOVER:
            self.hx, self.hy = r.x, r.y
            self.phase = "hold"
        elif mode == self.MODE_LAND:
            self.phase = "approach"
        elif mode == self.MODE_MOON:
            # Cruise high above moon, above home planet's gravity influence
            # Home planet top is at y=660, radius=440, centre at y=1100
            # Cruise at y=20 to be well above home planet's strong gravity
            self.cruise_y = 20.0
            self.phase = "climb"
        elif mode == self.MODE_DOCK:
            self.phase = "approach"

    def to_manual(self):
        self.mode = self.MODE_MANUAL
        self.phase = "idle"
        self.finished = None

    # -- target selection ----------------------------------------------------
    def _targets(self):
        """Return (gx, gy, gvx, gvy): the state the rocket should aim for,
        advancing the phase state machine as waypoints are reached."""
        r = self.r
        if self.mode == self.MODE_HOVER:
            return self.hx, self.hy, 0.0, 0.0

        if self.mode == self.MODE_LAND:
            # Land on home planet pad
            tx = self.w.pad_cx
            ty = self.w.pad_y  # top of home planet
            if self.phase == "approach":
                if abs(r.x - tx) < 26.0 and abs(r.y - (ty - C.AP_SAFE_HEIGHT)) < 40.0:
                    self.phase = "descend"
                return tx, ty - C.AP_SAFE_HEIGHT, 0.0, 0.0
            # descent: vertical axis is pure speed control
            return tx, r.y, 0.0, C.AP_DESCEND_SPEED

        if self.mode == self.MODE_MOON:
            mx, my, mr = self.w.planets[1].x, self.w.planets[1].y, self.w.planets[1].radius
            top = my - mr
            if self.phase == "climb":
                # Climb to cruise altitude above moon
                if r.y <= self.cruise_y + 12.0:
                    self.phase = "transit"
                return r.x, self.cruise_y, 0.0, 0.0
            if self.phase == "transit":
                # Transit horizontally to moon's x position
                # Add speed limiter to prevent horizontal acceleration
                tx, ty = mx, self.cruise_y
                gvx, gvy = 0.0, 0.0
                speed = math.hypot(r.vx, r.vy)
                if speed > C.AP_MAX_SPEED * 0.5 and speed > 1e-6:
                    # Reduce speed during transit
                    k = (speed - C.AP_MAX_SPEED * 0.5) * 0.8
                    tx += -r.vx / speed * k
                    ty += -r.vy / speed * k
                if abs(r.x - mx) < 40.0:
                    self.phase = "descend"
                return tx, ty, gvx, gvy
            # Descend to moon surface
            # Use controlled descent speed to counteract gravity
            return mx, r.y, 0.0, C.AP_DESCEND_SPEED * 0.8

        if self.mode == self.MODE_DOCK:
            sx, py = self.w.port_x, self.w.port_y
            if self.phase == "approach":
                if abs(r.x - sx) < 30.0 and abs(r.y - (py + 70.0)) < 40.0:
                    self.phase = "final"
                return sx, py + 70.0, 0.0, 0.0
            # Final approach: controlled descent to port position
            dist_y = r.y - py
            if dist_y < 40.0:
                return sx, py, 0.0, 0.0
            descent_speed = min(C.AP_DESCEND_SPEED, dist_y * 0.5)
            return sx, py, 0.0, -descent_speed

        # manual / safety fallback: just hold still
        return r.x, r.y, 0.0, 0.0

    # -- controller ----------------------------------------------------------
    def update(self, dt):
        """Return (thrust_frac, ang_accel) for the current frame."""
        r = self.r
        if self.mode == self.MODE_MANUAL:
            return 0.0, 0.0

        gx, gy, gvx, gvy = self._targets()

        # Get actual gravity at rocket position (from gravity wells)
        gx_grav, gy_grav = self.w.get_total_gravity(r.x, r.y)

        # desired net acceleration (PID control)
        ax = C.AP_POS_KP * (gx - r.x) + C.AP_VEL_KD * (gvx - r.vx)
        ay = C.AP_POS_KP * (gy - r.y) + C.AP_VEL_KD * (gvy - r.vy)

        # Engine acceleration needed to produce that net acceleration.
        # Physics: net_accel = engine_output + gravity
        # So: engine_output = desired_net - gravity
        # Gravity is toward planet (positive direction), engine must push opposite
        ex = ax - gx_grav
        ey = ay - gy_grav

        m_a = math.hypot(ex, ey)
        if m_a > C.AP_MAX_ACCEL:
            s = C.AP_MAX_ACCEL / m_a
            ex *= s
            ey *= s

        # speed limiter: long transits must not overshoot the target
        speed = math.hypot(r.vx, r.vy)
        if speed > C.AP_MAX_SPEED and speed > 1e-6:
            k = (speed - C.AP_MAX_SPEED) * 1.6
            ex += -r.vx / speed * k
            ey += -r.vy / speed * k

        m = math.hypot(ex, ey)
        if m < 1e-3:
            return 0.0, 0.0
        dx, dy = ex / m, ey / m

        # steer the thrust axis onto the desired acceleration direction
        target_angle = math.degrees(math.atan2(dx, -dy))
        err = wrap_angle(target_angle - r.angle)
        ang_vel_des = clamp(err * C.AP_ANG_GAIN, -C.MAX_ANG_VEL, C.MAX_ANG_VEL)
        ang_accel = clamp((ang_vel_des - r.ang_vel) * C.AP_TURN_RATE,
                          -C.MAX_ANG_ACCEL, C.MAX_ANG_ACCEL)

        tx, ty = r.thrust_dir()
        dot = tx * dx + ty * dy
        thrust = clamp(dot * m / C.MAX_THRUST, 0.0, 1.0)
        
        # If significantly misaligned but need thrust, apply partial thrust
        # This helps with rotation by providing some acceleration even when not perfectly aligned
        if dot < 0.3 and m > 100:
            # Apply reduced thrust (40% of max) to help with alignment
            thrust = max(thrust, 0.4 * m / C.MAX_THRUST)
            thrust = min(thrust, 1.0)
        
        return thrust, ang_accel

    # -- status for HUD ------------------------------------------------------
    def label(self):
        return {
            self.MODE_HOVER: "HOVER 悬停",
            self.MODE_LAND: "AUTO LAND 自动降落",
            self.MODE_MOON: "MOON LANDING 登陆星球",
            self.MODE_DOCK: "AUTO DOCK 自动对接",
            self.MODE_MANUAL: "MANUAL 手动",
        }.get(self.mode, self.mode)

    def phase_label(self):
        return self.PHASE_LABELS.get(self.phase, self.phase.upper())

    def target(self):
        """Current control target, used by the HUD marker."""
        if self.mode == self.MODE_MANUAL:
            return None
        return self._targets()
