#!/usr/bin/env python3
"""
ascii_video.py — Play videos as ASCII art in terminal
with synchronized audio and frame skipping.
"""

import os
import sys
import time
import argparse
import signal
import subprocess
import tempfile
import threading
from PIL import Image
import imageio.v3 as iio
import sounddevice as sd
import soundfile as sf
import ascii_core as core


# ============================================================
#  AUDIO PLAYER CLASS
# ============================================================
class AudioPlayer:
    """Handles audio extraction, playback, and cleanup."""

    def __init__(self, video_path):
        self.video_path = video_path
        self.wav_path = None
        self.thread = None
        self.start_event = threading.Event()
        self.stop_event = threading.Event()

    def extract_audio(self):
        """Extracts audio track to temporary WAV using ffmpeg."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        self.wav_path = tmp.name
        tmp.close()
        cmd = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
            self.wav_path, "-loglevel", "error"
        ]
        print("🎵 Extracting audio...")
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"⚠️ Audio extraction failed: {e}")
            self.wav_path = None

    def _play_audio_native(self):
        """Play audio using sounddevice in a background thread."""
        try:
            data, samplerate = sf.read(self.wav_path, dtype='float32')
            self.start_event.wait()
            sd.play(data, samplerate)
            while not self.stop_event.is_set():
                if not sd.get_stream().active:
                    break
                time.sleep(0.05)
            sd.stop()
        except Exception as e:
            print(f"⚠️ Audio playback failed: {e}")

    def _play_audio_ffplay(self):
        """Fallback to ffplay playback if sounddevice fails."""
        cmd = [
            "ffplay", "-nodisp", "-autoexit", "-loglevel",
            "error", self.wav_path
        ]
        self.start_event.wait()
        subprocess.run(cmd)

    def start(self):
        """Begin extraction and playback."""
        self.extract_audio()
        if not self.wav_path or not os.path.isfile(self.wav_path):
            print("❌ No audio track found.")
            return

        # Try native playback first, fallback to ffplay
        try:
            sd.check_output_settings()
            self.thread = threading.Thread(
                target=self._play_audio_native, daemon=True)
        except Exception:
            print(
                "⚙️ Falling back to ffplay for audio output.")
            self.thread = threading.Thread(
                target=self._play_audio_ffplay, daemon=True)

        self.thread.start()
        self.start_event.set()

    def stop(self):
        """Stop playback and clean up."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.wav_path and os.path.exists(self.wav_path):
            try:
                os.remove(self.wav_path)
                print(f"🧹 Cleaned up {self.wav_path}")
            except OSError:
                print(f"⚠️ Could not delete temp file {self.wav_path}")


def handle_interrupt(audio_player):
    """Graceful shutdown on Ctrl+C."""
    def handler(sig, frame):
        print("\n🛑 Interrupt detected, stopping audio...")
        if audio_player:
            audio_player.stop()
        sys.exit(0)
    return handler


# ============================================================
#  VIDEO TO ASCII FUNCTION
# ============================================================

def video_to_ascii(video_path, width=100, scale=0.55,
                   mode="grayscale", invert=False,
                   fps_limit=30, with_audio=False):
    """Render video as ASCII and sync with audio using frame skipping."""

    audio_player = None
    if with_audio:
        audio_player = AudioPlayer(video_path)
        signal.signal(signal.SIGINT, handle_interrupt(audio_player))
        audio_player.start()

    try:
        video_reader = iio.imiter(video_path)
        video_meta = iio.immeta(video_path)
    except Exception as e:
        print(f"❌ Failed to open video: {e}")
        return

    video_fps_from_meta = video_meta.get("fps", fps_limit) or fps_limit
    print(f"🎞 Detected FPS: {video_fps_from_meta:.2f}")

    start_time_pre_loop = time.time()
    frame_number_source = 0
    shown = skipped = 0

    for frame in video_reader:
        frame_number_source += 1
        target_time = frame_number_source / video_fps_from_meta
        elapsed = time.time() - start_time_pre_loop

        # Frame skip logic, that may be flawed
        if elapsed > target_time + (1.0 / video_fps_from_meta):
            skipped += 1
            continue
        if elapsed < target_time:
            time.sleep(target_time - elapsed)

        # Render frame
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

        os.system("cls" if os.name == "nt" else "clear")
        print(out)
        shown += 1

    total_time = time.time() - start_time_pre_loop
    if audio_player:
        audio_player.stop()

    print(f"\n✅ Done: {shown} frames shown, {
        skipped} skipped, total {total_time:.2f}s.")


# ============================================================
#  CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play video as ASCII art with optional sound.")
    parser.add_argument("input", help="Path to video file")
    parser.add_argument("-w", "--width", type=int, default=100)
    parser.add_argument("-s", "--scale", type=float, default=0.55)
    parser.add_argument("--invert", action="store_true")
    parser.add_argument(
        "--mode", choices=["grayscale", "3-gradient", "hdr"],
        default="grayscale")
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument(
        "--audio",
        action="store_true", help="Enable synchronized audio playback")
    args = parser.parse_args()

    video_to_ascii(
        args.input,
        width=args.width,
        scale=args.scale,
        mode=args.mode,
        invert=args.invert,
        fps_limit=args.fps,
        with_audio=args.audio,
    )
