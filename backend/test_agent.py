
#pip install groq sounddevice scipy playsound python-dotenv langchain
import os
import time
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import wave
from dotenv import load_dotenv

from groq import Groq
from langchain_core.messages import SystemMessage, HumanMessage

# =========================
# CONFIG
# =========================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAMPLE_RATE = 16000
RECORD_SECONDS = 4

INPUT_AUDIO = "input.wav"
OUTPUT_AUDIO = "response.wav"

STT_MODEL = "whisper-large-v3-turbo"
LLM_MODEL = "llama-3.1-8b-instant"
TTS_MODEL = "canopylabs/orpheus-v1-english"

SYSTEM_PROMPT = """
You are a professional AI receptionist.
You are calm, polite, and concise.
Keep responses under 2 sentences.
speak only english or german
"""

client = Groq(api_key=GROQ_API_KEY)


def play_audio(path):
    """Play audio using sounddevice"""
    try:
        # Read the WAV file
        with wave.open(path, 'rb') as wav_file:
            frames = wav_file.readframes(wav_file.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
            sample_rate = wav_file.getframerate()
        
        # Play using sounddevice
        sd.play(audio_data, sample_rate)
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")

# =========================
# AUDIO RECORDING
# =========================
def record_audio():
    print("\n🎙️ Listening...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    wav.write(INPUT_AUDIO, SAMPLE_RATE, audio)
    print("🛑 Recording finished")

# =========================
# SPEECH TO TEXT
# =========================
def speech_to_text():
    print("🧠 Transcribing...")
    with open(INPUT_AUDIO, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=f,
            model=STT_MODEL,
        )
    print(f"👤 User: {transcription.text}")
    return transcription.text

# =========================
# LLM
# =========================
def generate_response(user_text):
    print("🤖 Thinking...")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=150,
    )

    reply = completion.choices[0].message.content
    print(f"🤖 Agent: {reply}")
    return reply

# =========================
# TEXT TO SPEECH
# =========================
def text_to_speech(text):
    print("🔊 Speaking...")
    audio = client.audio.speech.create(
        model=TTS_MODEL,
        voice="Aaliyah-PlayAI",
        input=text,
        response_format="wav"
    )

    with open(OUTPUT_AUDIO, "wb") as f:
        for chunk in audio.iter_bytes():
            f.write(chunk)

    play_audio(OUTPUT_AUDIO)

# =========================
# MAIN LOOP
# =========================
def run_voice_agent():
    print("✅ Voice Agent started (Ctrl+C to stop)")
    while True:
        record_audio()
        user_text = speech_to_text()

        if not user_text.strip():
            print("⚠️ No speech detected")
            continue

        response = generate_response(user_text)
        text_to_speech(response)

        time.sleep(0.3)

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_voice_agent()
