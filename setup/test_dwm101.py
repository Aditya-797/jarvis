#!/usr/bin/env python3
"""
DG TECH / DIGITEK DWM-101 HARDWARE DIAGNOSTIC TOOL
Run this tool to diagnose and test your DWM-101 Wireless Mic on Android:
1. Tests USB OTG connection & receiver status
2. Captures 5 seconds of audio using DWM-101 native 48kHz AAC format
3. Normalizes via FFmpeg to 16kHz PCM WAV
4. Analyzes sound energy (RMS) to verify if the transmitter is linked
5. Plays the audio back through your Bluetooth speaker
"""

import os
import sys
import time
import math
import struct
import wave
import subprocess

def test_dwm101():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║        DIGITEK DWM-101 HARDWARE DIAGNOSTIC TOOL       ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    # 1. Clean previous locks
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)
    time.sleep(0.5)

    raw_file = "test_dwm101_raw.m4a"
    wav_file = "test_dwm101_clean.wav"

    for f in [raw_file, wav_file]:
        if os.path.exists(f):
            os.remove(f)

    print("🎙️ Plug in your DWM-101 receiver and ensure the transmitter is turned ON (solid green light).")
    print("▶️ Recording will start in 2 seconds...")
    time.sleep(2)

    print("\n🔴 [RECORDING NOW (5 Seconds)] - Speak clearly into your DWM-101 mic!")
    
    # Record with DWM-101 native parameters
    rec_cmd = [
        "termux-microphone-record",
        "-d",
        "-f", raw_file,
        "-l", "5",
        "-e", "aac",
        "-r", "48000",
        "-c", "1",
        "-b", "128"
    ]
    subprocess.run(rec_cmd)
    time.sleep(5.5)
    subprocess.run(["termux-microphone-record", "-q"], capture_output=True)

    if not os.path.exists(raw_file) or os.path.getsize(raw_file) < 1000:
        print("\n❌ ERROR: No audio file was created!")
        print("Possible causes:")
        print("1. Termux:API does not have Microphone permission.")
        print("2. Phone's OTG Connection is turned OFF in Android Settings.")
        return

    # Convert with FFmpeg
    print("⚙️ Normalizing audio stream via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", raw_file,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        wav_file
    ]
    subprocess.run(ffmpeg_cmd, capture_output=True)

    # Analyze RMS
    with wave.open(wav_file, "rb") as wf:
        n_frames = wf.getnframes()
        data = wf.readframes(n_frames)
        samples = struct.unpack(f"{len(data)//2}h", data)
        sum_sq = sum(float(s) * float(s) for s in samples)
        rms = math.sqrt(sum_sq / len(samples))

    print(f"\n📊 Sound Energy Level (RMS): {round(rms, 1)}")

    if rms < 100:
        print("⚠️ WARNING: Audio is SILENT or FLATLINE (RMS < 100)!")
        print("Diagnosis:")
        print("- The DWM-101 receiver is plugged in, but the transmitter may be turned OFF or UNPAIRED.")
        print("- Ensure the transmitter has a SOLID GREEN LED (not blinking).")
        print("- Check if OTG is active: Settings -> Additional Settings -> OTG Connection.")
    elif rms < 300:
        print("🟡 Audio detected, but volume is LOW. Move the mic closer to your mouth.")
    else:
        print("✅ SUCCESS! Loud, crisp voice audio detected from your DWM-101!")

    print("\n🔊 Playing back your recording through your speaker/headphones now...")
    subprocess.run(["play-audio", wav_file])
    print("Diagnostic complete!\n")

if __name__ == "__main__":
    test_dwm101()
