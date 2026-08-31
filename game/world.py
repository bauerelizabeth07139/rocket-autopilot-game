"""The play area: home planet with landing pad, a second planet (moon)
and a space station with a docking port."""

import math

from . import config as C


class World:
    def __init__(self):
        self.ground_y = C.GROUND_Y
        self.pad_cx = C.PAD_CX
        self.pad_half = C.PAD_HALF
        self.moon = C.MOON            # (x, y, r)
        self.station = C.STATION      # (x, y)
        self.port = (C.STATION[0], C.STATION[1] + C.STATION_PORT_Y)

    def moon_top(self):
        return self.moon[1] - self.moon[2]

    def moon_hit(self, x, y):
        """True when the ship's centre has hit the moon's body."""
        mx, my, mr = self.moon
        return math.hypot(x - mx, y - my) < mr - 8.0

    def surface_y_at(self, x):
        """Solid surface height below a given x: moon platform or ground."""
        mx, _, mr = self.moon
        if abs(x - mx) < mr - 8.0:
            return self.moon_top()
        return self.ground_y
