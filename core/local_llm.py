"""
Local LLM Runner for Jarvis using llama.cpp.
Optimized for 4GB RAM Android devices running in Termux.
"""

import os
import subprocess
import logging

logger = logging.getLogger("Jarvis.LocalLLM")

class LocalLLMRunner:
    def __init__(self, config: dict):
        local_cfg = config.get("intelligence", {}).get("local_model", {})
        self.model_path = os.path.expanduser(local_cfg.get("model_path", "~/models/qwen2.5-1.5b.gguf"))
        self.llama_cli = os.path.expanduser(local_cfg.get("llama_cli_path", "~/llama.cpp/build/bin/llama-cli"))
        self.threads = str(local_cfg.get("threads", 4))
        self.temp = str(local_cfg.get("temp", 0.7))

    def is_available(self) -> bool:
        """Checks if llama.cpp binary and model file exist on the phone."""
        return os.path.exists(self.model_path) and os.path.exists(self.llama_cli)

    def generate(self, user_prompt: str, system_prompt: str) -> str | None:
        """Executes prompt on local model via llama-cli."""
        if not self.is_available():
            logger.warning("Local LLM or llama-cli binary not found.")
            return None

        # Format ChatML prompt (used by Qwen2.5 / SmolLM)
        formatted_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        cmd = [
            self.llama_cli,
            "-m", self.model_path,
            "-p", formatted_prompt,
            "-n", "64",          # Keep response concise for speech
            "-t", self.threads,
            "--temp", self.temp,
            "-no-cnv"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=25
            )
            raw = result.stdout.strip()
            
            # Extract assistant turn
            if "<|im_start|>assistant" in raw:
                raw = raw.split("<|im_start|>assistant")[-1]
            raw = raw.replace("<|im_end|>", "").strip()
            
            return raw if raw else None
        except subprocess.TimeoutExpired:
            logger.error("Local LLM inference timed out.")
            return None
        except Exception as e:
            logger.error(f"Local LLM execution failed: {e}")
            return None
