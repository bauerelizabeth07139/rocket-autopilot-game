"""Font loading with CJK fallback for the Chinese HUD labels."""

import os

import pygame

_CJK_FONT = None


def _find_cjk():
    global _CJK_FONT
    if _CJK_FONT is not None:
        return _CJK_FONT
    candidates = (
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\Deng.ttf",
    )
    for path in candidates:
        if os.path.exists(path):
            _CJK_FONT = path
            return _CJK_FONT
    _CJK_FONT = ""  # none found
    return _CJK_FONT


def font(size, bold=False):
    if _find_cjk():
        return pygame.font.Font(_CJK_FONT, size)
    f = pygame.font.Font(None, size)
    f.set_bold(bold)
    return f
