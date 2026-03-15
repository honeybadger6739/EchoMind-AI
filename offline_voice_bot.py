import threading
import sounddevice as sd
import queue
import json
import requests
import pyttsx3
from vosk import Model, KaldiRecognizer

model = Model("model")
rec = KaldiRecognizer(model, 16000)
audio_q = queue.Queue()

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3",  
        "prompt": prompt,
        "stream": False      
    }

    response = requests.post(url, json=data)

    result = response.json()
    return result["response"]
def audio_callback(indata, frames, time, status):
    audio_q.put(bytes(indata))

def voice_loop():
    with sd.RawInputStream(samplerate=16000, blocksize=8000,
                           dtype='int16', channels=1, callback=audio_callback):
        while True:
            data = audio_q.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "")
                if text:
                    print("\n🎤 You:", text)
                    reply = ask_ollama(text)
                    print("🤖 Bot:", reply)
                    speak(reply)

def text_loop():
    while True:
        text = input("\n⌨️ Type: ")
        if text.lower() == "exit":
            break
        reply = ask_ollama(text)
        print("🤖 Bot:", reply)
        speak(reply)

print("✅ Voice + Text Bot Ready")
print("Type or Speak (say something)…")
print("Type 'exit' to quit")

threading.Thread(target=voice_loop, daemon=True).start()
text_loop()