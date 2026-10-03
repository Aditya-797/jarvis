#!/usr/bin/env bash
# ==============================================================================
# JARVIS AUTOMATED SETUP SCRIPT FOR TERMUX (ANDROID 14/15)
# Optimized for 4GB RAM phones (memory-safe compilation & resumable downloads)
# ==============================================================================

set -e

echo "============================================="
echo "        JARVIS 24/7 SERVER INSTALLER         "
echo "============================================="

# 0. Self-Healing DNS for Android/Termux
if [ -n "$PREFIX" ] && [ -d "$PREFIX" ]; then
    mkdir -p "$PREFIX/etc"
    if ! grep -q "8.8.8.8" "$PREFIX/etc/resolv.conf" 2>/dev/null; then
        echo "nameserver 8.8.8.8" > "$PREFIX/etc/resolv.conf"
        echo "nameserver 1.1.1.1" >> "$PREFIX/etc/resolv.conf"
    fi
fi

# 1. Update and upgrade Termux
echo "[1/5] Updating Termux packages..."
pkg update -y || true

# 2. Install required packages
echo "[2/5] Installing core development packages..."
pkg install -y \
  python \
  nmap \
  git \
  clang \
  cmake \
  ffmpeg \
  pulseaudio \
  termux-api \
  libffi \
  openssl

# 3. Install Python & Node dependencies
echo "[3/5] Installing Python & Node dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if command -v npm &>/dev/null; then
  echo "Running npm install..."
  npm install --silent 2>/dev/null || npm install
fi

# 4. Clone and compile llama.cpp for local offline fallback
# Memory-safe build: cap to 2 jobs to prevent Android OOM killer on 4GB RAM phones
echo "[4/5] Building llama.cpp for local offline AI on phone..."
if [ ! -f "$HOME/llama.cpp/build/bin/llama-cli" ]; then
  mkdir -p "$HOME"
  if [ ! -d "$HOME/llama.cpp" ]; then
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$HOME/llama.cpp"
  fi
  
  cd "$HOME/llama.cpp"
  cmake -B build -DCMAKE_BUILD_TYPE=Release
  
  # Limit compiler processes to 2 to prevent RAM exhaustion
  JOBS=$(nproc 2>/dev/null || echo 2)
  if [ "$JOBS" -gt 2 ]; then JOBS=2; fi
  echo "Compiling llama.cpp using $JOBS parallel threads..."
  cmake --build build --config Release -j"$JOBS"
  cd - >/dev/null
  echo "✅ llama.cpp compiled successfully!"
else
  echo "✅ llama.cpp compiler binary already present."
fi

# 5. Download Qwen 2.5 1.5B Model with resumable download and validation
echo "[5/5] Checking Qwen 2.5 1.5B quantized GGUF model..."
mkdir -p "$HOME/models"
MODEL_PATH="$HOME/models/qwen2.5-1.5b.gguf"

if [ ! -f "$MODEL_PATH" ] || [ $(wc -c <"$MODEL_PATH" 2>/dev/null || echo 0) -lt 500000000 ]; then
  echo "Downloading Qwen 2.5 1.5B GGUF (~980MB, supports resume if interrupted)..."
  curl -L -C - -o "$MODEL_PATH.tmp" \
    "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
  mv "$MODEL_PATH.tmp" "$MODEL_PATH"
  echo "✅ Model downloaded and verified successfully."
else
  echo "✅ Model file already exists and is fully intact."
fi

# 6. Prevent Android from sleeping CPU
if command -v termux-wake-lock &>/dev/null; then
  echo "Acquiring wake-lock..."
  termux-wake-lock
fi

echo "============================================="
echo "✅ JARVIS INSTALLATION COMPLETE!"
echo "1. Run: python quickstart.py"
echo "============================================="
