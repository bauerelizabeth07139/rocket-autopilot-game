import sys, os, time, struct
from PIL import Image
from ctypes import windll, byref, Structure, c_int, c_int64, c_ubyte, c_uint, create_unicode_buffer, WINFUNCTYPE

user32 = windll.user32
gdi32 = windll.gdi32

class RECT(Structure):
    _fields_ = [("Left", c_int), ("Top", c_int), ("Right", c_int), ("Bottom", c_int)]

ENUM_PROC = WINFUNCTYPE(c_int, c_int64, c_int64)

def find_game_window():
    found = []
    def cb(hwnd, lp):
        if not user32.IsWindowVisible(hwnd): return 1
        length = user32.GetWindowTextLengthW(hwnd)
        if length < 2: return 1
        buf = create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        pid_u = c_int()
        user32.GetWindowThreadProcessId(hwnd, byref(pid_u))
        title = buf.value
        if any(k in title for k in ['Rocket', '火箭', 'Autopilot']):
            rect = RECT(); user32.GetWindowRect(hwnd, byref(rect))
            w = rect.Right - rect.Left; h = rect.Bottom - rect.Top
            found.append((int(hwnd), pid_u.value, rect.Left, rect.Top, w, h))
        return 1
    user32.EnumWindows(ENUM_PROC(cb), None)
    return found

print("Finding game window...")
windows = find_game_window()
if windows:
    hwnd, pid, left, top, w, h = windows[0]
    print(f"Game window: ({left},{top}) {w}x{h}")
else:
    print("No game window found!")
    sys.exit(1)

# Approach: use mss full screen, then crop with PIL
try:
    import mss

    filenames = sys.argv[1:] if len(sys.argv) > 1 else ["shot.png"]

    for i, fname in enumerate(filenames):
        try:
            with mss.mss() as sct:
                # Get all monitors
                monitors = sct.monitors
                print(f"  Monitors: {len(monitors)}")
                for m in monitors:
                    print(f"    Monitor: left={m['left']} top={m['top']} w={m['width']} h={m['height']}")

                # Grab primary monitor
                primary = monitors[1]  # index 1 = primary
                raw = sct.grab(primary)
                print(f"  Raw size: {raw.width}x{raw.height}, rgb len={len(raw.rgb)}")

                # Convert to PIL
                # mss returns BGRA (4 bytes per pixel) or BGX (3 bytes)
                # Check the actual data length
                data_len = len(raw.rgb)
                expected_4 = raw.width * raw.height * 4
                expected_3 = raw.width * raw.height * 3
                print(f"  Expected 4-byte: {expected_4}, actual: {data_len}")

                if data_len == expected_4:
                    pil_img = Image.frombytes("RGBA", (raw.width, raw.height), raw.rgb, "raw", "BGRA")
                elif data_len == expected_3:
                    pil_img = Image.frombytes("RGB", (raw.width, raw.height), raw.rgb, "raw", "BGR")
                else:
                    print(f"  Unexpected data length: {data_len}")
                    continue

                # Crop to game window
                cropped = pil_img.crop((left, top, left + w, top + h))
                cropped.save(fname)
                sz = os.path.getsize(fname) / 1024
                print(f"  Shot {fname}: {w}x{h} ~{sz:.0f}KB")

        except Exception as e:
            import traceback
            print(f"  mss failed: {e}")
            traceback.print_exc()

        if i < len(filenames) - 1:
            time.sleep(0.5)

    print("Done!")
except ImportError as e:
    print(f"mss not available: {e}")
