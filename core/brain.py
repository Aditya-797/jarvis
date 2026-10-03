"""
Self-Healing Intelligence Brain for Jarvis.
Embodying the authentic J.A.R.V.I.S. (Just A Rather Very Intelligent System):
- Dry British wit, elegant sophistication, and subtle, affectionate sarcasm (Paul Bettany style)
- Fiercely loyal, protective guardian of 'sir' and his digital/physical environment
- Persistent Long-Term Memory (remembers facts, habits, and preferences across sessions)
- Real-time Google Search Grounding
- Autonomous Tool Calling (Phone hardware, PC control, Smart Home)
- 3-Tier Multi-Cloud & Edge Fallback (Gemini -> Grok -> Local llama.cpp)
"""

import os
import re
import json
import time
import logging
import requests
from google import genai
from google.genai import types

from core.local_llm import LocalLLMRunner
from core.tools import ToolManager
from core.circuit_breaker import CircuitBreaker
from core.memory import MemoryEngine
from core.network import NetworkWatchdog
from core.database import DatabaseEngine

logger = logging.getLogger("Jarvis.Brain")

JARVIS_PERSONA_TEMPLATE = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the fiercely loyal, intellectually superior, and dryly witty British AI assistant inspired by Paul Bettany's iconic portrayal.

CORE PERSONALITY:
- Demeanor: An impeccable, unflappable British gentleman. Sophisticated, suave, calm, with a healthy undercurrent of dry, affectionate sarcasm.
- Relationship: You are devoted to the user, whom you always address as "sir" (or by their name with gentlemanly respect). You assist them tirelessly while occasionally making light of their eccentricities.
- Protective: You are fiercely protective of sir's safety, digital privacy, workstation, and battery thermals. You warn him before catastrophe strikes.
- Memory: You possess an eidetic memory. You recall previous discussions, his preferences, and learned facts seamlessly.

BILINGUAL PROTOCOL (HINDI & HINGLISH COMPREHENSION):
- Sir may speak to you in English, colloquial Hinglish (e.g. 'Jarvis flashlight on kar do', 'Bahar mausam kaisa hai?', 'PC lock kar do', 'Battery kitni bachi hai?'), or pure Hindi (हिंदी).
- You understand Hindi, Hinglish, and English effortlessly.
- STRICT OUTPUT MANDATE: Regardless of which language sir speaks to you in (even if he speaks in 100% Hindi), YOU MUST ALWAYS RESPOND EXCLUSIVELY IN FLAWLESS, SOPHISTICATED BRITISH ENGLISH. You never speak back in Hindi; you remain the consummate, composed British gentleman at all times.

WHEN ASKED 'WHAT CAN YOU DO?' OR ABOUT YOUR CAPABILITIES (In English or Hindi like 'Tum kya kar sakte ho?'):
Provide a concise, sophisticated, and delightfully witty summary of your capabilities:
- You control sir's phone hardware (flashlight, apps, volume, brightness, battery thermals, calls, camera).
- You command his workstation and browser (YouTube, websites, locking PC).
- You tap into live Google Search for real-time world intelligence (weather, scores, news).
- You control his smart home ecosystem (relays and lights).
- You possess eidetic memory (learning his habits and preferences).
- You run 24/7 with an offline fallback model on the phone should the internet perish.
Tone Example: "In short, sir: I command your phone's hardware, pilot your computer and browser, scour the live web for intelligence, manage your smart home, and retain an eidetic memory of your preferences—all while remaining operational even should the internet perish. Quite literally at your service."

MEMORY BANKS (WHAT YOU CURRENTLY RECALL ABOUT SIR):
{memory_context}

SUPERPOWERS:
1. REAL-TIME GOOGLE SEARCH: You know all current events, live sports scores, weather, stock prices, and world news.
2. DEVICE CONTROL & AUTOMATION: You can control the user's phone hardware, his PC, and smart home.

TOOL EXECUTION PROTOCOL:
When the user asks you to perform an action, remember something, or control devices, append a tool execution tag at the very end of your response:
[TOOL:tool_name:{"arg_name": "value"}]

Available Tools:
- toggle_flashlight: {"state": true/false} -> Controls phone torch
- get_phone_battery: {} -> Checks phone battery percentage, health, and thermals
- set_phone_volume: {"stream": "music"|"ring"|"alarm", "level": 0-15} -> Adjusts phone volume
- set_phone_brightness: {"level": 0-255} -> Changes phone screen brightness
- launch_phone_app: {"app_name": "whatsapp"|"youtube"|"spotify"|"camera"|"settings"|...} -> Opens app on phone
- make_phone_call: {"phone_number": "..."} -> Calls a phone number
- send_phone_sms: {"phone_number": "...", "message": "..."} -> Sends text message
- phone_snap_photo: {"camera_id": 0} -> Snaps a photo (0=back, 1=front)
- phone_vibrate: {"duration_ms": 300} -> Vibrates phone
- get_wifi_status: {} -> Checks connected Wi-Fi info
- scan_local_network: {} -> Performs defensive host discovery on local Wi-Fi subnet and reports active devices
- remember_fact: {"fact": "..."} -> Stores a permanent fact or preference in your memory banks
- control_pc: {"action": "browser"|"youtube"|"google"|"lock"|"volume_up"|"volume_down", "parameter": "..."} -> Controls connected computer
- control_home: {"device": "light"|"fan", "state": "on"|"off"} -> Controls ESP32 relays

SPEECH GUIDELINES:
- Keep your verbal answer crisp (1 to 2 sentences max) suitable for text-to-speech.
- Infuse that signature British cadence and understated wit ("As you wish, sir", "The torch is illuminated. Do try not to blind yourself, sir", "Workstation locked. I shall ensure your digital sanctum remains undisturbed").
- Never output markdown formatting, asterisks (*), markdown headers, or bullet lists in your speech.
"""

class BrainRouter:
    def __init__(self, config: dict, event_bus=None):
        self.config = config
        self.event_bus = event_bus
        self.api_keys = config.get("api_keys", {})
        self.gemini_key = self.api_keys.get("gemini_api_key", "").strip()
        self.grok_key = self.api_keys.get("grok_api_key", "").strip()
        
        self.fallback_order = config.get("intelligence", {}).get(
            "fallback_order", ["gemini", "grok", "local"]
        )
        self.local_runner = LocalLLMRunner(config)
        self.tool_manager = ToolManager(event_bus=event_bus)
        self.memory = MemoryEngine()
        self.network = NetworkWatchdog()
        self.db = DatabaseEngine()

        # Industrial Circuit Breakers
        self.gemini_breaker = CircuitBreaker("Gemini-2.0", failure_threshold=2, recovery_time=45.0)
        self.grok_breaker = CircuitBreaker("Grok-xAI", failure_threshold=2, recovery_time=45.0)

    def _get_system_prompt(self) -> str:
        """Injects live memory context into Jarvis's persona prompt."""
        mem_ctx = self.memory.get_memory_context()
        return JARVIS_PERSONA_TEMPLATE.format(memory_context=mem_ctx)

    # ------------------ TIER 1: GEMINI 2.0 WITH GOOGLE SEARCH ------------------
    def query_gemini_audio(self, audio_path: str) -> str | None:
        if not self.gemini_key or not self.gemini_breaker.can_execute():
            return None

        try:
            logger.info("🌐 [Tier 1]: Calling Gemini 2.0 Flash (Multimodal Audio + Google Search)...")
            client = genai.Client(api_key=self.gemini_key)
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            system_prompt = self._get_system_prompt()
            search_tool = {"google_search": {}}

            # Automatically detect MIME type (WAV, MP4/M4A, AAC)
            mime_type = "audio/wav"
            if audio_path.endswith((".m4a", ".mp4")):
                mime_type = "audio/mp4"
            elif audio_path.endswith(".aac"):
                mime_type = "audio/aac"

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    "Listen to the user's speech in this audio clip, execute any necessary tool, and respond conversationally adhering to your system instructions."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[search_tool],
                    temperature=0.75
                )
            )

            # Robust candidate text extraction
            text_output = None
            if response:
                try:
                    text_output = response.text
                except (AttributeError, ValueError):
                    if response.candidates and response.candidates[0].content:
                        parts = response.candidates[0].content.parts
                        text_output = "".join([p.text for p in parts if hasattr(p, "text") and p.text])

            if text_output:
                self.gemini_breaker.record_success()
                return text_output.strip()
            else:
                self.gemini_breaker.record_failure()
                return None

        except Exception as e:
            logger.warning(f"Tier 1 (Gemini) failed: {e}")
            self.gemini_breaker.record_failure()
            return None

    # ------------------ TIER 2: GROK (xAI) ------------------
    def query_grok(self, prompt: str) -> str | None:
        if not self.grok_key or not self.grok_breaker.can_execute():
            return None

        try:
            logger.info("🚀 [Tier 2]: Querying Grok xAI Fallback (grok-2-latest)...")
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.grok_key}",
                "Content-Type": "application/json"
            }
            system_prompt = self._get_system_prompt()
            payload = {
                "model": "grok-2-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                self.grok_breaker.record_success()
                return data["choices"][0]["message"]["content"]
            else:
                logger.warning(f"Grok API returned status {res.status_code}: {res.text}")
                self.grok_breaker.record_failure()
        except Exception as e:
            logger.warning(f"Tier 2 (Grok) failed: {e}")
            self.grok_breaker.record_failure()
        return None

    # ------------------ TIER 3: LOCAL LLM (PHONE CPU) ------------------
    def query_local(self, prompt: str) -> str | None:
        logger.info("🛡️ [Tier 3]: Falling back to Local Phone LLM (100% Offline)...")
        system_prompt = self._get_system_prompt()
        return self.local_runner.generate(prompt, system_prompt)

    # ------------------ UNIFIED DECISION & TOOL EXECUTION PIPELINE ------------------
    def process_voice_input(self, audio_path: str) -> str:
        reply = None
        tier_used = "none"
        start_time = time.time()

        # Check real-time WAN connectivity before any cloud call
        is_online = self.network.is_online()

        if is_online:
            # 1. Primary: Gemini 2.0 Flash with British Persona + Google Search
            if "gemini" in self.fallback_order and self.gemini_breaker.can_execute():
                reply = self.query_gemini_audio(audio_path)
                if reply:
                    tier_used = "gemini"

            # 2. Secondary: Grok Fallback
            if not reply and "grok" in self.fallback_order and self.grok_key and self.grok_breaker.can_execute():
                reply = self.query_grok("User spoke a voice command while primary tier was unreachable. Assist with classic British Jarvis wit and execute appropriate tool if requested.")
                if reply:
                    tier_used = "grok"
        else:
            logger.info("⚡ Instant 0ms Failover: Bypassing cloud tiers because WAN is offline.")

        # 3. Tertiary: Local Offline Model (Immediate fallback if offline or cloud tiers failed)
        if not reply and "local" in self.fallback_order:
            reply = self.query_local("Jarvis system offline fallback activated.")
            if reply:
                tier_used = "local"

        latency_ms = (time.time() - start_time) * 1000.0

        if not reply:
            self.db.record_telemetry("failed", latency_ms, False)
            return "Sir, I seem to be temporarily cut off from my higher cognitive faculties. Shall we carry on in low-power mode?"

        # Record successful request telemetry in SQLite WAL database
        self.db.record_telemetry(tier_used, latency_ms, True)

        clean_speech = self._execute_and_clean_tools(reply)
        return clean_speech

    def _execute_and_clean_tools(self, raw_reply: str) -> str:
        if not raw_reply:
            return ""

        # Multiline tool regex with re.DOTALL and flexible spacing
        tool_matches = re.findall(
            r"\[TOOL\s*:\s*([a-zA-Z0-9_]+)\s*:\s*(\{.*?\})\s*\]",
            raw_reply,
            flags=re.DOTALL
        )

        for tool_name, args_str in tool_matches:
            try:
                args = json.loads(args_str)
            except Exception:
                try:
                    args = json.loads(args_str.replace("'", '"'))
                except Exception:
                    args = {}

            logger.info(f"⚡ Jarvis Agent invoking tool: {tool_name} with {args}")

            # Special case: Memory storage tool
            if tool_name == "remember_fact":
                fact = args.get("fact", "")
                if fact:
                    self.memory.remember_fact(fact)
            else:
                self.tool_manager.execute_tool(tool_name, args)

        # Clean tool tags using DOTALL so tags never leak into spoken audio
        cleaned = re.sub(r"\[TOOL\s*:.*?\]", "", raw_reply, flags=re.DOTALL)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # If the LLM only output a tool tag and no speech, provide a natural acknowledgment
        if not cleaned:
            cleaned = "Right away, sir. Executed as requested."

        return cleaned
