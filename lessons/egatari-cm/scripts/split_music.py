"""Cut the CM music into one clip per step and write audio/manifest.json and timeline.json.

The format plays audio per step (spec §5.2), so the 15 s track is cut at beat
boundaries (96 BPM, 0.625 s per beat) and each step is fixed to its clip's
length with lead 0 and pad_after 0 (spec §5.5). Usage: python3 scripts/split_music.py <full_15s.wav>
"""
import json, subprocess, sys
src = sys.argv[1]
SEGS = [("s-kp7qne:0", 0, 2.5), ("s-7xootv:0", 2.5, 5.0), ("s-bllpfp:0", 5.0, 5.625), ("s-bllpfp:1", 5.625, 8.75),
        ("s-e25tve:0", 8.75, 9.375), ("s-e25tve:1", 9.375, 12.5), ("s-fmdlgo:0", 12.5, 15.0)]
man, tl = {"segments": {}}, {}
for i, (k, a, b) in enumerate(SEGS):
    f = f"bgm_{i}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ss", str(a), "-to", str(b), "-c:a", "pcm_s16le", f"audio/{f}"], check=True)
    man["segments"][k] = {"file": f, "dur": round(b - a, 3), "cues": [], "kind": "imported"}
    tl[k] = {"dur": round(b - a, 3), "lead": 0, "pad_after": 0}
json.dump(man, open("audio/manifest.json", "w"), indent=1)
json.dump(tl, open("timeline.json", "w"), indent=1)
