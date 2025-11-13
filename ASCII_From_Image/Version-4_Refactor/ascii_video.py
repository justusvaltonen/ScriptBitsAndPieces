#!/usr/bin/env python3
"""
ascii_video.py — Entry point for playing videos as
ASCII art with synchronized audio.
"""

import argparse
from audio_manager import AudioManager
from video_player import VideoPlayer


def main():
    parser = argparse.ArgumentParser(
        description="Play video as ASCII art with optional sound."
    )
    parser.add_argument("input", help="Path to video file")
    parser.add_argument("-w", "--width", type=int, default=100)
    parser.add_argument("-s", "--scale", type=float, default=0.55)
    parser.add_argument("--invert", action="store_true")
    parser.add_argument(
        "--mode",
        choices=["grayscale", "3-gradient", "hdr"],
        default="grayscale",
    )
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Enable synchronized audio playback",
    )

    args = parser.parse_args()

    audio_manager = AudioManager(args.input) if args.audio else None
    player = VideoPlayer(
        video_path=args.input,
        width=args.width,
        scale=args.scale,
        color_mode=args.mode,
        invert=args.invert,
        fps_limit=args.fps,
        audio_manager=audio_manager,
    )

    player.play()


if __name__ == "__main__":
    main()
