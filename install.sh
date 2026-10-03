#!/usr/bin/env bash
# ==============================================================================
# ⚡ JARVIS 1-CLICK INSTANT INSTALLER & LAUNCHER (15 SECONDS)
# ==============================================================================

set -e

clear
echo "============================================="
echo "   ⚡ JARVIS 1-CLICK INSTANT INSTALLER      "
echo "============================================="

# 0. Termux & Android DNS Self-Healing (Fixes "Could not resolve host" issue)
if [ -n "$PREFIX" ] && [ -d "$PREFIX" ]; then
    mkdir -p "$PREFIX/etc"
    if ! grep -q "8.8.8.8" "$PREFIX/etc/resolv.conf" 2>/dev/null; then
        echo "nameserver 8.8.8.8" > "$PREFIX/etc/resolv.conf"
        echo "nameserver 1.1.1.1" >> "$PREFIX/etc/resolv.conf"
    fi
fi

# 1. Install prerequisites on Termux (including nmap, python, ffmpeg, termux-api)
if command -v pkg &> /dev/null; then
    echo "📦 Installing Termux prerequisites (python, nmap, ffmpeg, termux-api)..."
    pkg update -y 2>/dev/null || true
    pkg install -y python nmap ffmpeg termux-api
fi

# 2. Automatically run npm install
if command -v npm &> /dev/null; then
    echo "📦 Running npm install..."
    npm install --silent 2>/dev/null || npm install
fi

# 3. Acquire wake-lock if available
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock 2>/dev/null || true
fi

# 4. Launch the interactive quickstart wizard
python3 quickstart.py 2>/dev/null || python quickstart.py
