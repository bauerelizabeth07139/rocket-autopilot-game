"""Headless self-tests: verify every autopilot mode actually works.

Run with:  python main.py --selftest
Each scenario simulates the same physics / rules code the game uses and
asserts the expected outcome.  Exits 0 only when everything passes.

Supports solar system scale with gravity wells.
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from . import config as C          # noqa: E402
from .autopilot import Autopilot   # noqa: E402
from .rocket import Rocket         # noqa: E402
from .rules import check_docked, resolve_contact   # noqa: E402
from .world import World           # noqa: E402

DT = 1.0 / 60.0


def simulate(start, mode, max_seconds=60.0, hook=None):
    """Run the sim until an outcome occurs or the time budget runs out."""
    world = World()
    rocket = Rocket(*start[:2])
    if len(start) > 2:
        rocket.vx, rocket.vy = start[2], start[3]
    rocket.fuel = 1e9  # tests never starve on fuel
    ap = Autopilot(rocket, world)
    ap.engage(mode)

    frames = int(max_seconds / DT)
    for i in range(frames):
        thrust, ang_accel = ap.update(DT)
        rocket.step(DT, thrust, ang_accel, world)

        if hook:
            verdict = hook(rocket, world, ap, i)
            if verdict:
                return verdict

        if check_docked(rocket, world, ap):
            return "docked"
        outcome = resolve_contact(rocket, world, ap)
        if outcome:
            return outcome

    return "timeout"


def hover_check(rocket, world, ap, i):
    if i == int(5.0 / DT):
        # Hover target is (300, 150) - same as start position
        drift = math.hypot(rocket.x - 300.0, rocket.y - 150.0)
        speed = rocket.speed()
        ok = drift < 60.0 and speed < 20.0
        return ("hover_ok" if ok else "hover_drift")
    return None


def run():
    results = []

    def record(name, ok, detail):
        results.append((name, ok, detail))
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<22} {detail}")

    print("Rocket Autopilot self-test")

    # 1. hover: start at rest, must stay put
    # Start high up where gravity is weaker
    out = simulate((300, 150), Autopilot.MODE_HOVER, max_seconds=10.0,
                   hook=hover_check)
    record("hover", out == "hover_ok", f"-> {out}")

    # 2. auto land on the home-planet pad
    # Start higher with more time to descend
    out = simulate((500, 350, 50.0, -15.0), Autopilot.MODE_LAND, max_seconds=80.0)
    record("auto land (pad)", out == "landed_pad", f"-> {out}")

    # 3. auto land on the moon (second planet)
    # Moon is at (1800, 100) with radius 74, top at y=26
    # Start directly above moon to test vertical landing
    out = simulate((1800, 400), Autopilot.MODE_MOON, max_seconds=180.0)
    record("moon landing", out == "landed_moon", f"-> {out}")

    # 4. auto dock with the space station
    # Start far away from station and moon
    out = simulate((200, 150), Autopilot.MODE_DOCK, max_seconds=120.0)
    record("auto dock (distant)", out == "docked", f"-> {out}")

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} scenarios passed")
    if passed != total:
        sys.exit(1)
    print("SELFTEST PASS")
    return 0
