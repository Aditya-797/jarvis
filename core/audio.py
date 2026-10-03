"""
Universal Hardware-Adaptive Audio Engine for Jarvis.
Supports:
- ZERO REQUIRED ACCESSORIES: Works straight out of the box using phone's built-in microphone & speaker.
- OPTIONAL EXTERNAL HARDWARE: If plugged in (DWM-101, wireless lapel, USB mic, or Bluetooth speaker),
  automatically takes advantage of them for long-range room-wide audio.
- Seamless FFmpeg 16-bit 16kHz Mono PCM WAV normalization.
- Anti-hang MediaRecorder watchdog & zombie lock prevention.
"""

import os
import time
import math
import struct
import wave
import logging
import subprocess

logger = logging.getLogger("Jarvis.Audio")

class AudioManager:
    def __init__(self, config: dict):
        self.config = config.get("audio", {})
        self.sys_config = config.get("system", {})
        self.audio_file = self.config.get("temp_audio_file", "input.wav")
        self.raw_capture_file = "raw_capture.m4a"
        self.speech_rate = str(self.sys_config.get("speech_rate", 1.2))
        self.timeout = self.config.get("record_timeout", 8)
        
        # Audio configuration: 'auto', 'internal', or 'external'
        self.mic_mode = self.config.get("mic_mode", "auto")
        
        # Energy threshold for detecting dead silence
        self.silence_threshold = 90.0
        
        self.active_mic_source = "Auto / Built-in Mic"
        self.consecutive_silence = 0
        self.notified_failover = False

        self.cleanup_mic_locks()

    def cleanup_mic_locks(self):
        """Force-stops any dangling MediaRecorder sessions on Android."""
        try:
            subprocess.run(["termux-microphone-record", "-q"], capture_output=True, timeout=2)
        except Exception:
            pass

    def _can_run_ffmpeg(self) -> bool:
        """Tests if ffmpeg binary exists and runs without dynamic linking errors."""
        try:
            res = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=2)
            return res.returncode == 0
        except Exception:
            return False

    def _calculate_audio_rms(self, file_path: str) -> float:
        """Calculates Root-Mean-Square energy (or size heuristic for M4A/AAC)."""
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
            return 0.0

        try:
            with wave.open(file_path, "rb") as wf:
                n_frames = wf.getnframes()
                if n_frames == 0:
                    return 0.0
                raw_bytes = wf.readframes(n_frames)
                count = len(raw_bytes) // 2
                if count == 0:
                    return 0.0
                
                samples = struct.unpack(f"{count}h", raw_bytes)
                sum_squares = sum(float(s) * float(s) for s in samples)
                return math.sqrt(sum_squares / count)
        except Exception:
            # Fallback for AAC/M4A containers: positive filesize confirms voice capture
            return 200.0 if os.path.getsize(file_path) > 2048 else 0.0

    def record(self, duration: int = 5) -> tuple[str | None, str | None]:
        """
        Records audio adaptively.
        Works seamlessly on phone's built-in mic OR external mic.
        Returns: (audio_path: str | None, status_alert: str | None)
        """
        alert_msg = None

        # 1. Clean previous temp files
        for f in [self.audio_file, self.raw_capture_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

        self.cleanup_mic_locks()

        print(f"\n🎙️ [Jarvis Listening...] Speak now ({duration}s)")

        # 2. Universal high-definition capture (48kHz Mono AAC)
        # Android AudioSource.MIC automatically uses external mic if attached,
        # otherwise falls back directly to the phone's internal mic!
        cmd = [
            "termux-microphone-record",
            "-d",
            "-f", self.raw_capture_file,
            "-l", str(duration),
            "-e", "aac",
            "-r", "48000",
            "-c", "1",
            "-b", "128"
        ]

        try:
            subprocess.run(cmd, timeout=self.timeout, capture_output=True)
            time.sleep(duration + 0.3)
            self.cleanup_mic_locks()

            chosen_file = self.raw_capture_file

            # 3. Normalize via FFmpeg to standard 16kHz mono PCM WAV if FFmpeg is functional
            if self._can_run_ffmpeg() and os.path.exists(self.raw_capture_file) and os.path.getsize(self.raw_capture_file) > 1024:
                try:
                    ffmpeg_cmd = [
                        "ffmpeg", "-y",
                        "-i", self.raw_capture_file,
                        "-ar", "16000",
                        "-ac", "1",
                        "-c:a", "pcm_s16le",
                        self.audio_file
                    ]
                    res = subprocess.run(ffmpeg_cmd, capture_output=True, timeout=5)
                    if res.returncode == 0 and os.path.exists(self.audio_file):
                        chosen_file = self.audio_file
                except Exception:
                    pass

            # 4. Analyze sound energy
            if os.path.exists(chosen_file) and os.path.getsize(chosen_file) > 1024:
                rms = self._calculate_audio_rms(chosen_file)
                logger.info(f"Sound Energy (RMS): {round(rms, 1)}")

                # Check if energy is complete silence
                if rms < self.silence_threshold:
                    self.consecutive_silence += 1
                    logger.debug("Ambient silence detected.")
                else:
                    self.consecutive_silence = 0

                return chosen_file, alert_msg
            else:
                logger.warning("No audio data captured.")
                return None, None

        except subprocess.TimeoutExpired:
            logger.error("Audio watchdog timeout. Resetting MediaRecorder.")
            self.cleanup_mic_locks()
            return None, None
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            self.cleanup_mic_locks()
            return None, None

    def speak(self, text: str):
        """Outputs speech through Bluetooth speaker or phone built-in speaker."""
        if not text:
            return

        clean_text = (
            text.replace("*", "")
            .replace("#", "")
            .replace("`", "")
            .replace('"', '')
            .replace("'", "")
            .strip()
        )

        print(f"\n🤖 [Jarvis]: {clean_text}\n")

        try:
            subprocess.run([
                "termux-tts-speak",
                "-l", "en_GB",
                "-r", self.speech_rate,
                clean_text
            ], timeout=25)
        except Exception as e:
            logger.error(f"TTS playback error: {e}")
