"""Global configuration: window, physics, autopilot, camera constants."""

# --- window ---------------------------------------------------------------
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Rocket Autopilot 火箭自动驾驶"

# --- physics --------------------------------------------------------------
GRAVITY = 320.0            # px/s^2, downward (default gravity)
MAX_THRUST = 520.0         # px/s^2, max engine acceleration
MAX_ANG_ACCEL = 340.0      # deg/s^2
MAX_ANG_VEL = 200.0        # deg/s
FUEL_CAPACITY = 100.0      # fuel units
FUEL_BURN_RATE = 0.45      # fuel per second at full thrust

ROCKET_HALF_H = 23.0       # distance from rocket centre to engine nozzle

# --- autopilot gains -------------------------------------------------------
AP_MAX_ACCEL = 400.0       # cap on desired acceleration (increased for gravity)
AP_MAX_SPEED = 320.0       # speed limiter for transit phases
AP_POS_KP = 2.8            # position gain
AP_VEL_KD = 3.8            # velocity gain
AP_SAFE_HEIGHT = 200.0     # cruise height above a landing site
AP_DESCEND_SPEED = 45.0    # px/s, vertical speed during final descent (increased for gravity)
AP_ANG_GAIN = 5.5          # angular gain
AP_TURN_RATE = 13.0        # turn rate

# --- world -----------------------------------------------------------------
GROUND_Y = 660.0           # surface of the home planet
PAD_CX = 640.0             # landing pad centre
PAD_HALF = 135.0           # half width of the landing pad
MOON = (1800.0, 100.0, 74.0)  # second planet (moon): centre x, y, radius (moved very far right)
STATION = (1020.0, 150.0)    # space station centre
STATION_PORT_Y = 34.0        # docking port offset below the station centre

# --- success / failure thresholds ------------------------------------------
MAX_LAND_SPEED = 165.0     # |vy| allowed at touchdown
MAX_LAND_VX = 130.0        # |vx| allowed at touchdown
MAX_LAND_ANGLE = 14.0      # degrees
DOCK_DIST = 20.0           # distance to the port that counts as docked
DOCK_SPEED = 30.0          # |vx|+|vy| allowed when docking
DOCK_ANGLE = 8.0

# --- camera ----------------------------------------------------------------
CAM_W = WIDTH               # camera viewport width
CAM_H = HEIGHT              # camera viewport height
CAM_SMOOTH = 0.06           # camera follow speed (0-1)

# --- time acceleration -----------------------------------------------------
TIME_SCALES = [1, 2, 4, 8, 16, 32, 64, 128, 256]
DEFAULT_TIME_SCALE = 1

# --- gravity system --------------------------------------------------------
GRAVITY_CONSTANT = 1e6      # G * mass scaling factor

# --- screenshot path -------------------------------------------------------
SCREENSHOT_DIR = "screenshots"
