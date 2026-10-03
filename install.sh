#!/usr/bin/env bash
# ==============================================================================
# ⚡ JARVIS 1-CLICK INSTANT INSTALLER & LAUNCHER (15 SECONDS)
# ==============================================================================

set -e

clear
echo "============================================="
echo "   ⚡ JARVIS 1-CLICK INSTANT INSTALLER      "
echo "============================================="

# 0. Suppress interactive apt prompts & clean environment
export DEBIAN_FRONTEND=noninteractive

# 1. Termux & Android DNS Self-Healing (Fixes "Could not resolve host" issue)
if [ -n "$PREFIX" ] && [ -d "$PREFIX" ]; then
    mkdir -p "$PREFIX/etc"
    printf "nameserver 8.8.8.8\nnameserver 1.1.1.1\n" > "$PREFIX/etc/resolv.conf"
fi

# 2. Install prerequisites on Termux (including nmap, python, ffmpeg, termux-api)
if command -v pkg &> /dev/null; then
    echo "📦 Installing Termux prerequisites (python, nmap, ffmpeg, termux-api)..."
    pkg update -y -qq 2>/dev/null || true
    pkg install -y -qq python nmap ffmpeg termux-api 2>/dev/null || pkg install -y python nmap ffmpeg termux-api
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
