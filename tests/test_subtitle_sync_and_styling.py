import os
import sys
sys.path.insert(0, r"e:\applications\youtube-automate")
import asyncio
from core.tts_engine import generate_voiceover, _fmt_srt
from core.video_composer import _parse_srt, _make_subtitle_clips
import config

config.reload()

scenes = [
    {"narration": "Most people don't know that the Taos Hum has been driving residents insane for decades.", "duration_sec": 10},
    {"narration": "Researchers record the hum at sub-20-hertz tones, frequencies humans sense more than hear.", "duration_sec": 10},
    {"narration": "Like this video if it intrigued you, and subscribe for more science.", "duration_sec": 10}
]

print("=== 1. TESTING VOICEOVER GENERATION ===")
audio_path, srt_path, timings, dur = generate_voiceover(scenes)
print(f"Audio path: {audio_path}, Duration: {dur:.2f}s")
print(f"SRT path: {srt_path}")

with open(srt_path, "r", encoding="utf-8") as f:
    srt_text = f.read()

print(f"SRT length: {len(srt_text.splitlines())} lines")
print("First 15 lines of generated SRT:")
for l in srt_text.splitlines()[:15]:
    print(" ", l)

print("\n=== 2. TESTING PARSE_SRT GROUPING ===")
chunks = _parse_srt(srt_path)
print(f"Total chunks: {len(chunks)}")
for start, end, text in chunks[:8]:
    print(f"[{start:6.3f}s -> {end:6.3f}s] ({end-start:4.2f}s): {text}")

print("\n=== 3. TESTING SUBTITLE CLIPS CREATION ===")
clips = _make_subtitle_clips(srt_path, dur)
print(f"Successfully created {len(clips)} subtitle clips!")
