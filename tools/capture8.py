import sys, os, time
from PIL import Image
import screeninfo
from scipy import ndimage

# Try using screeninfo + mss with different approach
try:
    import mss
    import numpy as np

    # Get monitor info
    monitors = screeninfo.get_monitors()
    print(f"Monitors: {len(monitors)}")
    for m in monitors:
        print(f"  {m.name}: x={m.x} y={m.y} w={m.width} h={m.height}")

    # Find the monitor containing the game window (308, 213, 1296x759)
    game_left, game_top, game_w, game_h = 308, 213, 1296, 759

    with mss.mss() as sct:
        # Try capturing with different methods
        for method in ['directx', 'gdi', 'd3d11']:
            try:
                with mss.mss(method=method) as sct_method:
                    mon = sct_method.monitors[1]  # primary
                    raw = sct_method.grab(mon)
                    print(f"  Method {method}: size={raw.width}x{raw.height}, rgb_len={len(raw.rgb)}")

                    # Convert to numpy array
                    if len(raw.rgb) == raw.width * raw.height * 4:
                        img_array = np.frombuffer(raw.rgb, dtype=np.uint8).reshape((raw.height, raw.width, 4))
                        # Convert BGRA to RGB
                        img_rgb = img_array[:, :, :3]
                    else:
                        img_array = np.frombuffer(raw.rgb, dtype=np.uint8).reshape((raw.height, raw.width, 3))
                        img_rgb = img_array

                    # Crop to game window
                    cropped = img_rgb[game_top:game_top+game_h, game_left:game_left+game_w]

                    # Save as PNG
                    from PIL import Image as PILImage
                    pil_img = PILImage.fromarray(cropped)
                    fname = f"C:/rocket-autopilot-game/tools/shot_{method}.png"
                    pil_img.save(fname)
                    sz = os.path.getsize(fname) / 1024
                    print(f"  Saved {fname}: {game_w}x{game_h} ~{sz:.0f}KB")

                    # Check if image has non-black pixels
                    non_black = np.sum(cropped > 0)
                    total = cropped.shape[0] * cropped.shape[1]
                    print(f"  Non-black pixels: {non_black}/{total} ({100*non_black/total:.1f}%)")

            except Exception as e:
                print(f"  Method {method} failed: {e}")

except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()

print("Done!")
