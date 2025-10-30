#!/usr/bin/env python3

import argparse
from PIL import Image
import sys
import os

# These are used from dark to light
DEFAULT_CHARSET = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# ANSI COLORS
COLORS_8 = {
    'red': '\033[31m', 'green': '\033[32m',
    'blue': '\033[34m', 'reset': '\033[0m'
}


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert image to ASCII art (3 COLOR MODES!)")
    parser.add_argument(
        "input", help="Path to input image file")
    parser.add_argument(
        "-w", "--width", type=int, default=100,
        help="Output character width (default: 100)")
    parser.add_argument(
        "-s", "--scale", type=float, default=0.55,
        help="Vertical scale correction (default: 0.55)")
    parser.add_argument(
        "-c", "--charset", default=DEFAULT_CHARSET,
        help="Characters from darkest to lightest")
    parser.add_argument(
        "--invert", action="store_true", help="Invert brightness mapping")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--grayscale", action="store_true",
                       help="Grayscale ASCII (default)")
    group.add_argument("--3-gradient", action="store_true",
                       help="3-color gradient (Red/Green/Blue)")
    group.add_argument("--full-hdr", action="store_true",
                       help="Full 24-bit color HDR")
    parser.add_argument("--color-terminal", action="store_true",
                        help="Enable 24-bit color output directly in terminal")

    parser.add_argument(
        "--output", "-o",
        default=None, help="Write ASCII text output to this file")
    parser.add_argument(
        "--html", default=None,
        help="Write a colored HTML preview to this file")
    parser.add_argument(
        "--color", action="store_true",
        help="Enable colored HTML output when --html is used")
    parser.add_argument(
        "--bg", default="#000000",
        help="Background color for HTML (default: #000000)")
    parser.add_argument(
        "--fg", default="#FFFFFF",
        help="Foreground text color for HTML (default: #FFFFFF)")
    return parser.parse_args()


def map_pixel_to_char(luminance, charset, invert=False):
    if invert:
        luminance = 255 - luminance
    pos = luminance / 255
    idx = int(pos * (len(charset) - 1))
    return charset[idx]


def image_to_ascii(img, width=100, scale=0.55,
                   charset=DEFAULT_CHARSET, invert=False):
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
            ch = map_pixel_to_char(lum, charset, invert=invert)
            line_chars.append(ch)
        lines.append("".join(line_chars))
    return "\n".join(lines), img


def ascii_3_gradient(ascii_lines, image_rgb):
    w, h = image_rgb.size
    pixels = image_rgb.load()
    lines = []
    for y, line in enumerate(ascii_lines.splitlines()):
        row = []
        for x, ch in enumerate(line):
            r, g, b = pixels[x, y]
            if r >= g and r >= b:
                colored_ch = COLORS_8['red'] + ch + COLORS_8['reset']
            elif g >= r and g >= b:
                colored_ch = COLORS_8['green'] + ch + COLORS_8['reset']
            else:
                colored_ch = COLORS_8['blue'] + ch + COLORS_8['reset']
            row.append(colored_ch)
        lines.append("".join(row))
    return "\n".join(lines)


def make_html(ascii_lines, image_rgb, bg="#000000"):
    w, h = image_rgb.size
    pixels = image_rgb.load()
    html = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><metaname='viewport'content='width=device-width,initial-scale=1'>",
        f"<style>body{{background:{bg};color:white;white-space:pre;font-family:monospace;font-size:8px;line-height:7px;}}</style>",
        "</head><body><pre>"
    ]
    for y, line in enumerate(ascii_lines.splitlines()):
        row = []
        for x, ch in enumerate(line):
            r, g, b = pixels[x, y]
            row.append(f"<span style='color: rgb({r},{g},{b});'>{ch}</span>")
        html.append("".join(row))
    html.append("</pre></body></html>")
    return "\n".join(html)


def ascii_with_ansi(ascii_lines, image_rgb):
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


def main():
    args = get_args()
    if not os.path.isfile(args.input):
        print(f"❌ Input file doesn't exist: {args.input}", file=sys.stderr)
        sys.exit(2)

    try:
        img = Image.open(args.input)
        print(f"✅ Loading: {os.path.basename(args.input)}")
    except Exception as e:
        print(f"❌ Failed to open image: {e}", file=sys.stderr)
        sys.exit(3)

    ascii_text, resized_img = image_to_ascii(img, width=args.width,
                                             scale=args.scale,
                                             charset=args.charset,
                                             invert=args.invert)

    output_text = ascii_text

    if args.full_hdr or args.color_terminal:
        output_text = ascii_with_ansi(ascii_text, resized_img)
        print("🌈 Full HDR Mode!")
    elif getattr(args, '3_gradient'):
        output_text = ascii_3_gradient(ascii_text, resized_img)
        print("🌈 3-Gradient Mode (R/G/B)!")
    else:
        print("⚪ Grayscale Mode!")

    print("\n" + "="*80)
    print(output_text)
    print("="*80)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            plain_text = output_text
            for code in COLORS_8.values():
                plain_text = plain_text.replace(code, '')
            f.write(plain_text)
        print(f"💾 Saved plain text to: {args.output}")

    if args.html:
        html_content = make_html(ascii_text, resized_img, bg=args.bg)
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"🌐 Saved HTML to: {args.html}")
        print("   📁 Open in browser for FULL COLORS!")


if __name__ == "__main__":
    main()
