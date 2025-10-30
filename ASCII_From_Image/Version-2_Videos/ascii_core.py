#!/usr/bin/env python3

from PIL import Image

# Default character set — darkest to lightest
DEFAULT_CHARSET = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# Basic ANSI 8-color subset
COLORS_8 = {
    'red': '\033[31m',
    'green': '\033[32m',
    'blue': '\033[34m',
    'reset': '\033[0m'
}


def map_pixel_to_char(luminance, charset=DEFAULT_CHARSET, invert=False):
    """Map pixel brightness (0–255) to a character index."""
    if invert:
        luminance = 255 - luminance
    pos = luminance / 255
    idx = int(pos * (len(charset) - 1))
    return charset[idx]


def image_to_ascii(img, width=100, scale=0.55,
                   charset=DEFAULT_CHARSET, invert=False):
    """Convert a Pillow image to ASCII string,
        return (ascii_text, resized_image)."""
    orig_w, orig_h = img.size
    new_w = max(1, width)
    new_h = max(1, int((orig_h / orig_w) * new_w * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS).convert("RGB")
    pixels = img.load()
    lines = []
    for y in range(new_h):
        line_chars = []
        for x in range(new_w):
            r, g, b = pixels[x, y]
            lum = int(0.2126*r + 0.7152*g + 0.0722*b)
            ch = map_pixel_to_char(lum, charset, invert)
            line_chars.append(ch)
        lines.append("".join(line_chars))
    return "\n".join(lines), img


def ascii_with_ansi(ascii_lines, image_rgb):
    """Apply full 24-bit ANSI colors to ASCII text."""
    w, h = image_rgb.size
    pixels = image_rgb.load()
    lines = []
    for y, line in enumerate(ascii_lines.splitlines()):
        row = []
        for x, ch in enumerate(line):
            r, g, b = pixels[x, y]
            row.append(f"\033[38;2;{r};{g};{b}m{ch}\033[0m")
        lines.append("".join(row))
    return "\n".join(lines)


def ascii_3_gradient(ascii_lines, image_rgb):
    """Apply simplified RGB 3-color gradient coloring."""
    w, h = image_rgb.size
    pixels = image_rgb.load()
    lines = []
    for y, line in enumerate(ascii_lines.splitlines()):
        row = []
        for x, ch in enumerate(line):
            r, g, b = pixels[x, y]
            if r >= g and r >= b:
                colored = COLORS_8['red'] + ch + COLORS_8['reset']
            elif g >= r and g >= b:
                colored = COLORS_8['green'] + ch + COLORS_8['reset']
            else:
                colored = COLORS_8['blue'] + ch + COLORS_8['reset']
            row.append(colored)
        lines.append("".join(row))
    return "\n".join(lines)
