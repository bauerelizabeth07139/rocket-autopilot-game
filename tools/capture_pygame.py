import sys, os, time
from PIL import Image
import pygame
from ctypes import windll, byref, Structure, c_int, c_int64, c_ubyte, create_unicode_buffer, WINFUNCTYPE

user32 = windll.user32

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

# Try using mss with GDI method (BitBlt)
try:
    import mss

    filenames = sys.argv[1:] if len(sys.argv) > 1 else ["shot.png"]

    for i, fname in enumerate(filenames):
        try:
            # Try GDI method which uses BitBlt
            with mss.mss() as sct:
                # Get primary monitor
                mon = sct.monitors[1]
                raw = sct.grab(mon)

                print(f"  Raw: {raw.width}x{raw.height}, rgb_len={len(raw.rgb)}")

                # Convert to PIL
                # mss returns BGRA (4 bytes) or RGB (3 bytes)
                data_len = len(raw.rgb)
                expected_4 = raw.width * raw.height * 4
                expected_3 = raw.width * raw.height * 3

                if data_len == expected_4:
                    # BGRA format
                    pil_img = Image.frombytes("RGBA", (raw.width, raw.height), raw.rgb, "raw", "BGRA")
                elif data_len == expected_3:
                    # RGB format
                    pil_img = Image.frombytes("RGB", (raw.width, raw.height), raw.rgb, "raw", "RGB")
                else:
                    print(f"  Unexpected data length: {data_len}")
                    continue

                # Crop to game window
                cropped = pil_img.crop((left, top, left + w, top + h))

                # Save
                cropped.save(fname)
                sz = os.path.getsize(fname) / 1024
                print(f"  Shot {fname}: {w}x{h} ~{sz:.0f}KB")

                # Check content
                pixels = list(cropped.getdata())
                unique = len(set(pixels))
                non_black = sum(1 for p in pixels if p != (0,0,0))
                print(f"  Unique colors: {unique}, Non-black: {non_black}/{len(pixels)}")

        except Exception as e:
            import traceback
            print(f"  mss failed: {e}")
            traceback.print_exc()

        if i < len(filenames) - 1:
            time.sleep(0.5)

    print("Done!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
