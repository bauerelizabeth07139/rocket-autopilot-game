import sys, os, time
from PIL import ImageGrab, Image
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
    _, _, left, top, w, h = windows[0]
    print(f"Game window: ({left},{top}) {w}x{h}")
else:
    print("No game window found!")
    sys.exit(1)

# Use PrintWindow via GDI to capture the window pixels
def capture_window(hwnd, path):
    rect = RECT()
    user32.GetWindowRect(hwnd, byref(rect))
    w = rect.Right - rect.Left
    h = rect.Bottom - rect.Top

    hdesktop = user32.GetDesktopWindow()
    hwindc = user32.GetWindowDC(hdesktop)
    hdc = gdi32.CreateCompatibleDC(hwindc)
    hbmp = gdi32.CreateCompatibleBitmap(hwindc, w, h)
    gdi32.SelectObject(hdc, hbmp)

    # PrintWindow with RENDERFULLCONTENT flag
    result = user32.PrintWindow(hwnd, hdc, 0x00000002)
    print(f"  PrintWindow result: {result}")

    # Get pixel data using GetDIBits
    bi = (c_int * 12)(0)
    # BITMAPINFOHEADER
    bi[0] = 40  # biSize
    bi[1] = w   # biWidth
    bi[2] = -h  # biHeight (negative = top-down)
    bi[3] = 1   # biPlanes
    bi[4] = 32  # biBitCount
    bi[5] = 0   # biCompression = BI_RGB
    bi[6] = w * h * 4  # biSizeImage
    bi[7] = 0   # biXPelsPerMeter
    bi[8] = 0   # biYPelsPerMeter

    pixels = (c_ubyte * (w * h * 4))()
    bytes_read = c_uint(0)
    success = gdi32.GetDIBits(hdc, hbmp, 0, h, pixels, bi, 0)
    print(f"  GetDIBits success: {bool(success)}, bytes read: {bytes_read.value}")

    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc)
    user32.ReleaseDC(hdesktop, hwindc)

    # Convert BGRA to RGBA for PIL
    # GetDIBits with top-down returns BGRA (or BGRA reversed)
    # For top-down (negative height), pixels are row-major top-to-bottom
    # Each pixel is BGR + alpha (4 bytes)
    # PIL expects RGBA
    from array import array
    rgba_data = bytearray(w * h * 4)
    for i in range(w * h):
        b = pixels[i * 4]
        g = pixels[i * 4 + 1]
        r = pixels[i * 4 + 2]
        a = pixels[i * 4 + 3]
        rgba_data[i * 4] = r
        rgba_data[i * 4 + 1] = g
        rgba_data[i * 4 + 2] = b
        rgba_data[i * 4 + 3] = a

    img = Image.frombytes("RGBA", (w, h), bytes(rgba_data), "raw", "RGBA")
    img = img.convert("RGB")
    img.save(path)
    sz = os.path.getsize(path) / 1024
    print(f"  Saved: {path} ({w}x{h}, ~{sz:.0f} KB)")

filenames = sys.argv[1:] if len(sys.argv) > 1 else ["shot.png"]

for i, fname in enumerate(filenames):
    capture_window(windows[0][0], fname)
    if i < len(filenames) - 1:
        time.sleep(0.5)

print("Done!")
