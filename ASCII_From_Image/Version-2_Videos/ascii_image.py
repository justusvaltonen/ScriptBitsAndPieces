#!/usr/bin/env python3

import argparse
import sys
import os
from PIL import Image
import ascii_core as core


def main():
    parser = argparse.ArgumentParser(description="Convert image to ASCII art.")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-w", "--width", type=int, default=100)
    parser.add_argument("-s", "--scale", type=float, default=0.55)
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--mode", choices=["grayscale", "3-gradient", "hdr"], default="hdr")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    try:
        img = Image.open(args.input)
    except Exception as e:
        print(f"❌ Cannot open image: {e}")
        sys.exit(2)

    ascii_text, resized_img = core.image_to_ascii(
        img, width=args.width, scale=args.scale, invert=args.invert
    )

    if args.mode == "hdr":
        output = core.ascii_with_ansi(ascii_text, resized_img)
    elif args.mode == "3-gradient":
        output = core.ascii_3_gradient(ascii_text, resized_img)
    else:
        output = ascii_text

    print(output)


if __name__ == "__main__":
    main()
