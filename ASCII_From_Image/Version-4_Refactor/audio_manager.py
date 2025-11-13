import os
import time
import tempfile
import subprocess
import threading
import sounddevice as sd
import soundfile as sf


class AudioManager:
    """Handles audio extraction, playback, and cleanup."""

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.temp_audio_path = None
        self.playback_thread = None
        self.start_event = threading.Event()
        self.stop_event = threading.Event()

    def extract_audio(self):
        """Extracts the audio track from the video using ffmpeg."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        self.temp_audio_path = temp_file.name
        temp_file.close()

        command = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "44100", "-ac", "2",
            self.temp_audio_path, "-loglevel", "error"
        ]
        print("🎵 Extracting audio track...")
        try:
            subprocess.run(command, check=True)
        except Exception as error:
            print(f"⚠️ Audio extraction failed: {error}")
            self.temp_audio_path = None

    def _play_audio_with_sounddevice(self):
        """Play audio using sounddevice in a background thread."""
        try:
            data, samplerate = sf.read(self.temp_audio_path, dtype='float32')
            self.start_event.wait()
            sd.play(data, samplerate)
            while not self.stop_event.is_set() and sd.get_stream().active:
                time.sleep(0.05)
            sd.stop()
        except Exception as error:
            print(f"⚠️ Audio playback failed: {error}")

    def _play_audio_with_ffplay(self):
        """Fallback audio playback using ffplay."""
        command = [
            "ffplay", "-nodisp", "-autoexit",
            "-loglevel", "error", self.temp_audio_path
        ]
        self.start_event.wait()
        subprocess.run(command)

    def start(self):
        """Extract and begin audio playback."""
        self.extract_audio()
        if not self.temp_audio_path or not os.path.isfile(self.temp_audio_path):
            print("❌ No audio track found.")
            return

        try:
            sd.check_output_settings()
            self.playback_thread = threading.Thread(
                target=self._play_audio_with_sounddevice,
                daemon=True
            )
        except Exception:
            print("⚙️ Falling back to ffplay for audio output.")
            self.playback_thread = threading.Thread(
                target=self._play_audio_with_ffplay,
                daemon=True
            )

        self.playback_thread.start()
        self.start_event.set()

    def stop(self):
        """Stop playback and clean up the temporary audio file."""
        self.stop_event.set()
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
        if self.temp_audio_path and os.path.exists(self.temp_audio_path):
            try:
                os.remove(self.temp_audio_path)
                print(f"🧹 Removed temporary file: {self.temp_audio_path}")
            except OSError:
                print(f"⚠️ Could not delete: {self.temp_audio_path}")
