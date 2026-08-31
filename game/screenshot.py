"""Built-in screenshot capture for debugging and documentation."""

import os
import pygame


def capture(screen, path="screenshot.png"):
    """Save current screen to a PNG file."""
    pygame.image.save(screen, path)
    print(f"Screenshot saved: {os.path.abspath(path)}")
    return path
