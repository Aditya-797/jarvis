#!/usr/bin/env python3
"""
⚡ JARVIS 10-SECOND INSTANT SETUP WIZARD
No manual editing required. Prompts for your key and starts Jarvis immediately.
"""

import os
import sys
import yaml
import time
import subprocess

CONFIG_PATH = "config.yaml"

def print_banner():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║          ⚡ J.A.R.V.I.S. INSTANT QUICK-SETUP          ║
    ║        Up and running in literally 15 seconds         ║
    ╚═══════════════════════════════════════════════════════╝
    """)

def check_requirements():
    print("🔍 [1/4] Verifying Python packages...")
    package_checks = {
        "google-genai": lambda: __import__("google.genai"),
        "pyyaml": lambda: __import__("yaml"),
        "requests": lambda: __import__("requests"),
        "websockets": lambda: __import__("websockets"),
    }
    missing = []
    for pkg_name, check_fn in package_checks.items():
        try:
            check_fn()
        except ImportError:
            missing.append(pkg_name)
    
    if missing:
        print(f"📦 Installing missing packages: {', '.join(missing)}...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
    print("✅ Core packages ready.")

def configure_keys():
    print("\n🔑 [2/4] API Key Configuration:")
    
    # Auto-create config.yaml from template if missing
    import shutil
    if not os.path.exists(CONFIG_PATH) and os.path.exists("config.example.yaml"):
        shutil.copy("config.example.yaml", CONFIG_PATH)
        print("📄 Initialized config.yaml from template.")

    # Load existing config
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    # 1. Gemini API Key (Primary)
    gemini_key = config.get("api_keys", {}).get("gemini_api_key", "").strip()
    if gemini_key and not gemini_key.startswith("YOUR_"):
        print(f"✅ Found existing Gemini API key: {gemini_key[:8]}...{gemini_key[-4:]}")
        change_gemini = input("Do you want to change it? (y/N): ").strip().lower()
        if change_gemini == "y":
            gemini_key = ""

    if not gemini_key or gemini_key.startswith("YOUR_"):
        print("\n1️⃣  Gemini 2.0 Flash (Primary Cloud Intelligence)")
        print("    Get your FREE key from: https://aistudio.google.com")
        gemini_key = input("👉 Paste Gemini API Key: ").strip()

    # 2. Grok xAI API Key (Secondary Fallback)
    grok_key = config.get("api_keys", {}).get("grok_api_key", "").strip()
    if grok_key and not grok_key.startswith("YOUR_"):
        print(f"✅ Found existing Grok API key: {grok_key[:8]}...{grok_key[-4:]}")
        change_grok = input("Do you want to change it? (y/N): ").strip().lower()
        if change_grok == "y":
            grok_key = ""

    if not grok_key or grok_key.startswith("YOUR_"):
        print("\n2️⃣  Grok xAI (Secondary Fallback Engine - Optional)")
        print("    Get your key from: https://console.x.ai (Press Enter to skip if not available)")
        grok_key = input("👉 Paste Grok API Key (or press Enter to skip): ").strip()

    # Save to config
    config["api_keys"]["gemini_api_key"] = gemini_key
    config["api_keys"]["grok_api_key"] = grok_key

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    print("\n✅ API credentials safely persisted to config.yaml.")

def test_audio():
    print("\n🔊 [3/4] Audio Transducer Test...")
    try:
        subprocess.run(["termux-wake-lock"], capture_output=True)
        subprocess.run([
            "termux-tts-speak",
            "-l", "en_GB",
            "-r", "1.2",
            "Jarvis instant setup complete, sir. I am at your service."
        ], timeout=5)
        print("✅ Audio output verified.")
    except Exception:
        print("⚠️ Skipped speaker check (will test on launch).")

def check_local_model():
    print("\n🛡️ [4/4] Local Offline AI Engine (Qwen 2.5 1.5B):")
    model_path = os.path.expanduser("~/models/qwen2.5-1.5b.gguf")
    llama_cli = os.path.expanduser("~/llama.cpp/build/bin/llama-cli")

    if os.path.exists(model_path) and os.path.exists(llama_cli):
        print("✅ Local offline model and llama.cpp compiler are installed and ready!")
        return

    print("Jarvis can run 100% offline on your phone's CPU via Qwen 2.5 (1.5B).")
    choice = input("👉 Download & build offline model (~980MB) now? (y/N): ").strip().lower()
    if choice == "y":
        print("\n⚙️ Building llama.cpp and downloading Qwen 2.5 (1.5B)...")
        subprocess.run(["bash", "setup/termux_setup.sh"])
    else:
        print("⏩ Skipped for now. (Jarvis will use cloud APIs. To install later: bash setup/termux_setup.sh)")

def main():
    print_banner()
    check_requirements()
    configure_keys()
    test_audio()
    check_local_model()

    print("""
    ═══════════════════════════════════════════════════════
    🎉 ALL DONE! JARVIS IS COMPLETELY CONFIGURED.
    ═══════════════════════════════════════════════════════
    """)
    launch = input("🚀 Launch Jarvis right now? (Y/n): ").strip().lower()
    if launch != "n":
        print("\nStarting Master Supervisor (daemon.py)...")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable, "daemon.py"])

if __name__ == "__main__":
    main()
