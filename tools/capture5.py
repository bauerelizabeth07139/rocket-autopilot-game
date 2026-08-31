import sys, os, time
from PIL import Image
from ctypes import windll, byref, Structure, c_int, c_int64, c_ubyte, create_unicode_buffer, WINFUNCTYPE

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

# Use BitBlt to capture window
def capture_with_bitblt(hwnd, path):
    rect = RECT()
    user32.GetWindowRect(hwnd, byref(rect))
    w = rect.Right - rect.Left
    h = rect.Bottom - rect.Top

    # Create memory DC
    hdesktop = user32.GetDesktopWindow()
    hwindc = user32.GetWindowDC(hdesktop)
    hdcMem = gdi32.CreateCompatibleDC(hwindc)

    # Create bitmap
    hbmp = gdi32.CreateCompatibleBitmap(hwindc, w, h)
    gdi32.SelectObject(hdcMem, hbmp)

    # Copy from desktop to memory DC (this captures what's visible)
    gdi32.BitBlt(hdcMem, 0, 0, w, h, hwindc, left, top, 0x00CC0020)  # SRCCOPY

    # Get pixel data
    bi = (c_int * 12)(0)
    bi[0] = 40
    bi[1] = w
    bi[2] = -h
    bi[3] = 1
    bi[4] = 32
    bi[5] = 0

    pixels = (c_ubyte * (w * h * 4))()
    success = gdi32.GetDIBits(hdcMem, hbmp, 0, h, pixels, bi, 0)

    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdcMem)
    user32.ReleaseDC(hdesktop, hwindc)

    if not success:
        print(f"  GetDIBits failed!")
        return False

    # Convert BGRA to RGBA
    rgba = bytearray(w * h * 4)
    for i in range(w * h):
        b, g, r, a = pixels[i*4], pixels[i*4+1], pixels[i*4+2], pixels[i*4+3]
        rgba[i*4] = r
        rgba[i*4+1] = g
        rgba[i*4+2] = b
        rgba[i*4+3] = a

    img = Image.frombytes("RGBA", (w, h), bytes(rgba), "raw", "RGBA")
    img = img.convert("RGB")
    img.save(path)
    sz = os.path.getsize(path) / 1024
    print(f"  Saved: {path} ({w}x{h}, ~{sz:.0f}KB)")
    return True

filenames = sys.argv[1:] if len(sys.argv) > 1 else ["shot.png"]

for i, fname in enumerate(filenames):
    capture_with_bitblt(hwnd, fname)
    if i < len(filenames) - 1:
        time.sleep(0.5)

print("Done!")
