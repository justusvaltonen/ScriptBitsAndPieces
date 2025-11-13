import os
import csv
import time
from collections import deque


class PlaybackHUD:
    """
    Displays and logs real-time playback statistics
    such as FPS, sync offset, and frame skips.
    Also provides a small ASCII graph visualizing FPS stability.
    """

    def __init__(self, enable_logging=False, log_path="playback_log.csv",
                 graph_width=40, graph_height=8, fps_target=30.0):
        self.enable_logging = enable_logging
        self.log_path = log_path
        self.graph_width = graph_width
        self.graph_height = graph_height
        self.fps_target = fps_target

        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.frame_count = 0
        self.skipped_count = 0
        self.sync_offset = 0.0

        self.fps_history = deque(maxlen=self.graph_width)

        if self.enable_logging:
            self._initialize_log()

    # -------------------------------------
    # Logging Setup and Writing
    # -------------------------------------
    def _initialize_log(self):
        """Prepare the CSV file for recording playback metrics."""
        try:
            with open(self.log_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "timestamp", "frame", "fps", "skipped", "sync_offset"])
        except OSError as error:
            print(f"⚠️ Could not create log file: {error}")

    def _write_log(self, timestamp: float, fps: float):
        """Append playback metrics to CSV."""
        try:
            with open(self.log_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    f"{timestamp:.3f}",
                    self.frame_count,
                    f"{fps:.2f}",
                    self.skipped_count,
                    f"{self.sync_offset:.4f}"
                ])
        except OSError as error:
            print(f"⚠️ Could not write to log: {error}")

    # -------------------------------------
    # Graph Rendering
    # -------------------------------------
    def _render_graph(self):
        """Return an ASCII graph visualizing FPS history."""
        if not self.fps_history:
            return ""

        max_fps = max(max(self.fps_history), self.fps_target)
        scale = self.graph_height / max_fps if max_fps > 0 else 1.0

        # Build graph lines from top to bottom
        lines = []
        for y in range(self.graph_height, 0, -1):
            threshold = y / scale
            line = ""
            for fps in self.fps_history:
                line += "█" if fps >= threshold else " "
            lines.append(line)

        footer = f"└{'─' * (self.graph_width - 2)}┘"
        header = f"┌{'─' * (self.graph_width - 2)}┐"
        graph_str = header + "\n" + "\n".join(lines) + "\n" + footer
        return graph_str

    # -------------------------------------
    # Main update & summary
    # -------------------------------------
    def update(self, sync_offset: float, skipped: int):
        """Update the HUD with new frame metrics."""
        now = time.time()
        delta_time = now - self.last_frame_time
        self.last_frame_time = now
        self.frame_count += 1
        self.skipped_count = skipped
        self.sync_offset = sync_offset

        fps = 1.0 / delta_time if delta_time > 0 else 0.0
        self.fps_history.append(fps)

        os.system("cls" if os.name == "nt" else "clear")

        # Print textual stats
        print(
            f"\033[93mFrame: {self.frame_count:<5} | "
            f"FPS: {fps:5.1f} | "
            f"Skipped: {self.skipped_count:<3} | "
            f"Sync offset: {self.sync_offset:+.3f}s\033[0m\n"
        )

        # Print live FPS graph
        print(self._render_graph())

        if self.enable_logging:
            self._write_log(now - self.start_time, fps)

    def summary(self):
        """Print summary and average statistics at end of playback."""
        total_time = time.time() - self.start_time
        avg_fps = self.frame_count / total_time if total_time > 0 else 0.0
        print(
            f"\n✅ HUD Summary: {
                self.frame_count} frames in {total_time:.2f}s "
            f"| Avg FPS: {avg_fps:.2f}"
        )
