#!/usr/bin/env python3
"""
ascii_profile.py — Benchmark different ASCII render modes automatically.

Usage:
    python ascii_profile.py video.mp4 --width 100 --scale 0.55 --fps 20
"""

import subprocess
import os
import sys
import datetime
import csv


MODES = ["grayscale", "3-gradient", "hdr"]


def run_profile(video_path, width=100, scale=0.55, fps=20):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    summary_log = f"ascii_profile_summary_{timestamp}.csv"
    summary_data = []

    print(f"🧪 Starting benchmark for {video_path}\n")

    for mode in MODES:
        print(f"▶ Running mode: {mode}")
        cmd = [
            sys.executable, "ascii_video.py",
            video_path,
            "--width", str(width),
            "--scale", str(scale),
            "--mode", mode,
            "--fps", str(fps),
            "--no-hud"
        ]
        # Launch the subprocess and capture output
        process = subprocess.run(cmd, capture_output=True, text=True)
        print(process.stdout)
        print(process.stderr)

        # Find the performance log line in stdout
        log_file = None
        for line in process.stdout.splitlines():
            if "ascii_perf_" in line and line.strip().endswith(".csv"):
                log_file = line.strip().split()[-1]
                break

        if not log_file or not os.path.isfile(log_file):
            print(f"⚠️ No log found for {mode}. Skipping.")
            continue

        # Read performance log
        with open(log_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
            if not records:
                continue
            avg_fps = sum(float(r["inst_fps"]) for r in records) / len(records)
            avg_render = sum(float(r["render_ms"]) for r in records) / len(records)
            summary_data.append({
                "mode": mode,
                "frames": len(records),
                "avg_fps": round(avg_fps, 2),
                "avg_render_ms": round(avg_render, 2),
                "log_file": log_file
            })
            print(f"✅ {mode}: avg {avg_fps:.2f} FPS, {avg_render:.2f} ms/frame\n")

    # Save summary
    if summary_data:
        with open(summary_log, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
        print(f"📈 Summary saved: {summary_log}")
        print("Results:")
        for row in summary_data:
            print(f" - {row['mode']:>10}: {row['avg_fps']:>6.2f} FPS | "
                  f"{row['avg_render_ms']:>6.2f} ms/frame | {row['frames']:>5} frames")
    else:
        print("⚠️ No valid data collected.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ascii_profile.py video.mp4 [--width N] [--scale F] [--fps N]")
        sys.exit(0)

    # simple manual parsing for optional args
    video = sys.argv[1]
    width = 100
    scale = 0.55
    fps = 20
    for i, arg in enumerate(sys.argv):
        if arg == "--width" and i+1 < len(sys.argv):
            width = int(sys.argv[i+1])

        if arg == "--scale" and i+1 < len(sys.argv):
            scale = float(sys.argv[i+1])

        if arg == "--fps" and i+1 < len(sys.argv):
            fps = float(sys.argv[i+1])

    run_profile(video, width, scale, fps)
