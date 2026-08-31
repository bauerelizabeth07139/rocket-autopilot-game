import sys, os, time
from PIL import Image

try:
    import mss
except ImportError:
    print("mss not installed."); sys.exit(1)

# Try finding game window via ctypes
game_mon = None
try:
    from ctypes import windll, byref, Structure, c_int, c_int64, create_unicode_buffer, WINFUNCTYPE
    user32 = windll.user32
    class RECT(Structure):
        _fields_ = [("Left", c_int), ("Top", c_int), ("Right", c_int), ("Bottom", c_int)]
    ENUM_PROC = WINFUNCTYPE(c_int, c_int64, c_int64)
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
    if found:
        _, _, left, top, w, h = found[0]
        game_mon = {"left": left, "top": top, "width": w, "height": h}
        print(f"Game window found at ({left},{top}) size {w}x{h}")
except Exception as e:
    print(f"Could not detect window: {e}")

# Capture all requested shots
filenames = sys.argv[1:] if len(sys.argv) > 1 else ["shot.png"]

with mss.mss() as sct:
    # Default to full primary monitor
    default_mon = sct.monitors[1]
    for i, fname in enumerate(filenames):
        mon = game_mon if game_mon else default_mon
        img = sct.grab(mon)
        raw_mode = "BGRX" if len(img.rgb) == (img.width * img.height * 4) else "BGR"
        stride = img.width * 4 if raw_mode == "BGRX" else img.width * 3
        image = Image.frombytes("RGB", (img.width, img.height), img.rgb, "raw", raw_mode, stride, 1)
        image.save(fname)
        sz = os.path.getsize(fname) / 1024
        print(f"Shot {fname}: {img.width}x{img.height} ~{sz:.0f}KB")
        if i < len(filenames) - 1:
            time.sleep(0.5)

print("Capture complete!")
