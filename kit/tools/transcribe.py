"""Arabic word-level transcription.  usage: python3 -I transcribe.py audio16k.wav "initial prompt with brand names, prices" > tr.txt
Make the wav with: ffmpeg -i src.mov -ac 1 -ar 16000 audio.wav   (large-v3 on CPU: ~6 min per minute of audio)"""
import sys, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "large-v3", device="cpu", compute_type="int8")
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(a, language="ar", word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                       initial_prompt=sys.argv[2] if len(sys.argv) > 2 else None)
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for x in s.words:
        print(f"   {x.start:.2f}-{x.end:.2f} {x.word}")
