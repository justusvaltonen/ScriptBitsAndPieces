#!/usr/bin/env python3

import os
import sys
import csv
import datetime
import time
import argparse
import threading
import subprocess
import queue
from PIL import Image
import imageio.v3 as iio
import ascii_core as core


def video_to_ascii(video_path, width=120, scale=0.45, mode="hdr",
                   invert=False, fps_limit=40, show_hud=True, log_data=True):
    try:
        reader = iio.imiter(video_path)
    except Exception as e:
        print(f"❌ Cannot open video: {e}")
        sys.exit(1)

    delay = 1.0 / max(1, fps_limit)
    frame_count = 0
    start_time = time.time()
    prev_time = start_time
    total_render_time = 0.0

    log_records = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_filename = f"ascii_perf_{timestamp}.csv"

    for frame in reader:
        frame_start = time.time()
        frame_count += 1

        img = Image.fromarray(frame)
        ascii_text, resized_img = core.image_to_ascii(
            img, width=width, scale=scale, invert=invert
        )

        if mode == "hdr":
            out = core.ascii_with_ansi(ascii_text, resized_img)
        elif mode == "3-gradient":
            out = core.ascii_3_gradient(ascii_text, resized_img)
        else:
            out = ascii_text

        now = time.time()
        frame_render_time = (now - frame_start)
        total_render_time += frame_render_time
        elapsed = now - start_time
        inst_fps = 1.0 / frame_render_time if frame_render_time > 0 else 0
        avg_fps = frame_count / elapsed if elapsed > 0 else 0

        if log_data:
            log_records.append({
                "frame": frame_count,
                "render_ms": round(frame_render_time * 1000, 3),
                "inst_fps": round(inst_fps, 3),
                "avg_fps": round(avg_fps, 3),
            })

        os.system("cls" if os.name == "nt" else "clear")

        if show_hud:
            hud = (
                f"\033[93mFrame: {frame_count:<6d} "
                f"Instant FPS: {inst_fps:6.2f} "
                f"Average FPS: {avg_fps:6.2f} "
                f"Render: {frame_render_time*1000:7.2f} ms\033[0m\n"
            )
            print(hud)

        print(out)

        elapsed = time.time() - start_time
        expected_time = frame_count * delay
        sleep_time = expected_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

        sys.stdout.flush()

        # FPS limiter for performance tweaking
        frame_end = time.time()
        frame_duration = frame_end - frame_start
        sleep_time = delay - frame_duration
        if sleep_time > 0:
            time.sleep(sleep_time)

    if log_data and log_records:
        with open(log_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_records[0].keys())
            writer.writeheader()
            writer.writerows(log_records)
        print(f"📊 Saved performance log: {log_filename}")

    total_elapsed = time.time() - start_time
    print(f"\n✅ Finished {frame_count} frames in {total_elapsed:.2f}s "
          f"(avg {frame_count / total_elapsed:.2f} FPS)")
    print(f"🧠 Mean render time per frame: {(
        total_render_time / frame_count) * 1000:.2f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream video frames as ASCII animation with HUD.")
    parser.add_argument("input", help="Path to video file")
    parser.add_argument("-w", "--width", type=int, default=100)
    parser.add_argument("-s", "--scale", type=float, default=0.55)
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--mode", choices=["grayscale", "3-gradient", "hdr"], default="hdr")
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument("--no-hud", action="store_true", help="Hide performance HUD overlay")
    args = parser.parse_args()

    video_to_ascii(
        args.input,
        width=args.width,
        scale=args.scale,
        mode=args.mode,
        invert=args.invert,
        fps_limit=args.fps,
        show_hud=not args.no_hud,
    )
