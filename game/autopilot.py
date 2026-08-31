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
        "hold": "HOLD POSITION",
        "climb": "CLIMB",
        "transit": "TRANSIT",
        "approach": "APPROACH",
        "descend": "DESCENT",
        "final": "FINAL APPROACH",
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
            self.cruise_y = max(self.w.moon_top() - 150.0, 60.0)
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
            tx, ty = self.w.pad_cx, self.w.ground_y
            if self.phase == "approach":
                if abs(r.x - tx) < 26.0 and abs(r.y - (ty - C.AP_SAFE_HEIGHT)) < 40.0:
                    self.phase = "descend"
                return tx, ty - C.AP_SAFE_HEIGHT, 0.0, 0.0
            # descent: vertical axis is pure speed control (target follows
            # the ship), horizontal axis keeps the pad aligned.
            # y grows downward, so a positive target speed descends.
            return tx, r.y, 0.0, C.AP_DESCEND_SPEED

        if self.mode == self.MODE_MOON:
            mx, my, mr = self.w.moon
            top = my - mr
            if self.phase == "climb":
                if r.y <= self.cruise_y + 12.0:
                    self.phase = "transit"
                return r.x, self.cruise_y, 0.0, 0.0
            if self.phase == "transit":
                if abs(r.x - mx) < 20.0:
                    self.phase = "descend"
                return mx, self.cruise_y, 0.0, 0.0
            return mx, r.y, 0.0, C.AP_DESCEND_SPEED

        if self.mode == self.MODE_DOCK:
            sx, py = self.w.port
            if self.phase == "approach":
                if abs(r.x - sx) < 30.0 and abs(r.y - (py + 70.0)) < 40.0:
                    self.phase = "final"
                return sx, py + 70.0, 0.0, 0.0
            return sx, r.y, 0.0, -16.0

        # manual / safety fallback: just hold still
        return r.x, r.y, 0.0, 0.0

    # -- controller ----------------------------------------------------------
    def update(self, dt):
        """Return (thrust_frac, ang_accel) for the current frame."""
        r = self.r
        if self.mode == self.MODE_MANUAL:
            return 0.0, 0.0

        gx, gy, gvx, gvy = self._targets()

        # desired net acceleration
        ax = C.AP_POS_KP * (gx - r.x) + C.AP_VEL_KD * (gvx - r.vx)
        ay = C.AP_POS_KP * (gy - r.y) + C.AP_VEL_KD * (gvy - r.vy)
        m_a = math.hypot(ax, ay)
        if m_a > C.AP_MAX_ACCEL:
            s = C.AP_MAX_ACCEL / m_a
            ax *= s
            ay *= s

        # speed limiter: long transits must not overshoot the target
        speed = math.hypot(r.vx, r.vy)
        if speed > C.AP_MAX_SPEED and speed > 1e-6:
            k = (speed - C.AP_MAX_SPEED) * 1.6
            ax += -r.vx / speed * k
            ay += -r.vy / speed * k

        # engine acceleration needed to produce that net acceleration
        ex, ey = ax, ay - C.GRAVITY
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
