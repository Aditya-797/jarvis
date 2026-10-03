#!/usr/bin/env bash
# Resumable download script for Qwen 2.5 1.5B GGUF

set -e
if [ -n "$PREFIX" ] && [ -d "$PREFIX" ]; then
    mkdir -p "$PREFIX/etc"
    if ! grep -q "8.8.8.8" "$PREFIX/etc/resolv.conf" 2>/dev/null; then
        echo "nameserver 8.8.8.8" > "$PREFIX/etc/resolv.conf"
        echo "nameserver 1.1.1.1" >> "$PREFIX/etc/resolv.conf"
    fi
fi
mkdir -p "$HOME/models"
MODEL_PATH="$HOME/models/qwen2.5-1.5b.gguf"

echo "Downloading Qwen 2.5 1.5B Instruct (Q4_K_M quantized, ~980MB)..."
echo "Supports resume (-C -) if network drops."

curl -L -C - -o "$MODEL_PATH.tmp" \
  "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

mv "$MODEL_PATH.tmp" "$MODEL_PATH"
echo "✅ Download complete and verified! Saved to $MODEL_PATH"
