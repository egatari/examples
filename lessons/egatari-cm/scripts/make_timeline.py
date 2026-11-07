"""Write timeline.json: fix every step to its beats (96 BPM). (11/7: the CM is built silent;
the original full_15s.wav is laid under the exported video as one uncut track, see make_video.sh.)

OLD NOTE, kept for the record: this used to cut the CM music into one clip per step.

The format plays audio per step (spec §5.2), so the 15 s track is cut at beat
boundaries (96 BPM, 0.625 s per beat) and each step is fixed to its clip's
length with lead 0 and pad_after 0 (spec §5.5). Usage: python3 scripts/split_music.py
"""
import json, subprocess, sys
SEGS = [("s-kp7qne:0", 0, 2.5), ("s-7xootv:0", 2.5, 3.75), ("s-htits5:0", 3.75, 5.0), ("s-bllpfp:0", 5.0, 6.25), ("s-bllpfp:1", 6.25, 8.75),
        ("s-e25tve:0", 8.75, 9.375), ("s-e25tve:1", 9.375, 12.5), ("s-fmdlgo:0", 12.5, 12.8), ("s-fmdlgo:1", 12.8, 15.0)]
man, tl = {"segments": {}}, {}
for i, (k, a, b) in enumerate(SEGS):
    tl[k] = {"dur": round(b - a, 3), "lead": 0, "pad_after": 0}
json.dump(tl, open("timeline.json", "w"), indent=1)
