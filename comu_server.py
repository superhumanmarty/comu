import sounddevice as sd
import queue
import json
import os
import time
from vosk import Model, KaldiRecognizer
from googletrans import Translator
import nest_asyncio

# Setup
nest_asyncio.apply()
q = queue.Queue()
model = Model("vosk-model")
rec = KaldiRecognizer(model, 16000)
translator = Translator()

# Display function
def display_big(text):
    os.system('clear')
    print("\n\n")
    print(f"\033[1m\033[92m{text.upper()}\033[0m".center(os.get_terminal_size().columns))
    print("\n\n")

# Mic callback
def callback(indata, frames, time, status):
    q.put(bytes(indata))

# Real-time translator loop
def live_translate():
    with sd.InputStream(samplerate=16000, blocksize=2000, dtype='int16',
                        channels=1, callback=callback):
        print("🎤 Fast subtitles active... start speaking.")
        last_partial = ""
        last_translated = ""
        last_update = 0

        while True:
            data = q.get()
            rec.AcceptWaveform(data)
            partial = json.loads(rec.PartialResult()).get("partial", "").strip()

            # only update screen if partial changed and ~300ms passed
            if partial and partial != last_partial and time.time() - last_update > 0.3:
                try:
                    translated = translator.translate(partial, dest='es').text
                    if translated != last_translated:
                        display_big(translated)
                        last_translated = translated
                except:
                    pass  # silent fail
                last_partial = partial
                last_update = time.time()

# Run it
live_translate()
