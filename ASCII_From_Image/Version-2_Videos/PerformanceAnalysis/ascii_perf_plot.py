#!/usr/bin/env python3
"""
ascii_perf_plot.py — visualize ASCII video performance logs.
Usage:
    python ascii_perf_plot.py ascii_perf_20251024-2344.csv
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_perf_log(csv_path, window=10):
    if not os.path.isfile(csv_path):
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    if df.empty:
        print("⚠️ Empty CSV file.")
        sys.exit(1)

    # Compute rolling average for smoother FPS line
    df["fps_smooth"] = df["inst_fps"].rolling(window=window).mean()

    plt.figure(figsize=(10, 6))

    # Subplot 1 — FPS
    plt.subplot(2, 1, 1)
    plt.plot(df["frame"],
             df["inst_fps"], color="skyblue", label="Instant FPS", alpha=0.6)
    plt.plot(df["frame"],
             df["fps_smooth"], color="blue", label=f"{window}-frame average")
    plt.title("Frame Rate Over Time")
    plt.xlabel("Frame #")
    plt.ylabel("FPS")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.4)

    # Subplot 2 — Render Time
    plt.subplot(2, 1, 2)
    plt.plot(df["frame"],
             df["render_ms"], color="orange", label="Render time (ms)")
    plt.title("Render Time per Frame")
    plt.xlabel("Frame #")
    plt.ylabel("Milliseconds")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ascii_perf_plot.py ascii_perf_<timestamp>.csv")
        sys.exit(0)

    csv_path = sys.argv[1]
    plot_perf_log(csv_path)
