import os
import time
import signal
from PIL import Image
import imageio.v3 as iio
import ascii_core as core


class VideoPlayer:
    """Handles video reading, ASCII conversion, and synchronization."""

    def __init__(self, video_path, width=100, scale=0.55,
                 color_mode="grayscale", invert=False,
                 fps_limit=30, audio_manager=None):
        self.video_path = video_path
        self.width = width
        self.scale = scale
        self.color_mode = color_mode
        self.invert = invert
        self.fps_limit = fps_limit
        self.audio_manager = audio_manager

        self.total_shown = 0
        self.total_skipped = 0
        self.sync_offset = 0.0

    def _setup_signal_handling(self):
        def handler(sig, frame):
            print("\n🛑 Interrupt detected, stopping gracefully...")
            if self.audio_manager:
                self.audio_manager.stop()
            exit(0)
        signal.signal(signal.SIGINT, handler)

    def play(self):
        """Main video-to-ASCII playback loop with adaptive sync."""
        if self.audio_manager:
            self._setup_signal_handling()
            self.audio_manager.start()

        try:
            video_reader = iio.imiter(self.video_path)
            video_meta = iio.immeta(self.video_path)
        except Exception as error:
            print(f"❌ Failed to open video: {error}")
            return

        video_fps = video_meta.get("fps", self.fps_limit) or self.fps_limit
        frame_duration = 1.0 / video_fps
        print(f"🎞 Detected FPS: {video_fps:.2f}")

        start_time = time.time()
        correction_strength = 0.3
        frame_number = 0

        for frame in video_reader:
            frame_number += 1
            target_time = frame_number * frame_duration
            elapsed_time = time.time() - start_time

            # Adaptive synchronization
            self.sync_offset = (self.sync_offset * 0.9) + (
                (elapsed_time - target_time) * 0.1)
            if self.sync_offset > frame_duration:
                self.total_skipped += 1
                continue

            sleep_time = target_time - elapsed_time - (
                self.sync_offset * correction_strength)
            if sleep_time > 0:
                time.sleep(sleep_time)

            # Render frame
            image = Image.fromarray(frame)
            ascii_text, resized_image = core.image_to_ascii(
                image, width=self.width, scale=self.scale, invert=self.invert
            )

            if self.color_mode == "hdr":
                rendered_output = core.ascii_with_ansi(
                    ascii_text, resized_image)
            elif self.color_mode == "3-gradient":
                rendered_output = core.ascii_3_gradient(
                    ascii_text, resized_image)
            else:
                rendered_output = ascii_text

            os.system("cls" if os.name == "nt" else "clear")
            print(f"\033[93mSync offset: {
                self.sync_offset:+.3f}s | Frame: {frame_number}\033[0m\n")
            print(rendered_output)
            self.total_shown += 1

        if self.audio_manager:
            self.audio_manager.stop()

        total_time = time.time() - start_time
        print(f"\n✅ Done: {self.total_shown} shown, {
            self.total_skipped} skipped, {total_time:.2f}s total.")
