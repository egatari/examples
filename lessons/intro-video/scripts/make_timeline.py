"""Write timeline.json for the 30 s intro video (紹介動画): fix every step's length (lead 0, pad_after 0; spec §5.5).

For people who make slides: how Egatari saves work (owner 11/23).
Scenes: 1 a generic slide app, hand work (5.0 s) / 2 "Egatari なら、AI の返事を貼るだけ。" copy the prompt, paste the reply,
the slides are built — real Studio screens (10.0 s) / 3 "はみ出しも、AI が直す。" quality-check error, fix request, before and after (7.5 s) /
4 "そのままプレゼン、音声付き再生も。" (5.0 s) / logo (2.5 s) = 30.0 s.
Scene cuts fall on bar heads at 96 BPM (2.5 s): 5, 15, 22.5, 27.5 s.
The AI replies are real outputs of a chat AI from our nightly evaluation (fictional subject 需要と供給): the first reply had a quality-check error, the second is its fix.
Music is laid under the exported video as one uncut track (make_video.sh).
Usage: python3 scripts/make_timeline.py
"""
import json
STEPS = [
    ("s-ul4ddb:0", 1.3), ("s-mxm2rm:0", 1.3), ("s-c6djpf:0", 1.0), ("s-dm2ae2:0", 1.4),   # scene 1
    ("s-fcany4:0", 3.0), ("s-fcany4:1", 3.5), ("s-fcany4:2", 3.5),                        # scene 2
    ("s-xex3aj:0", 2.5), ("s-xex3aj:1", 2.5), ("s-xex3aj:2", 2.5),                        # scene 3
    ("s-ilwy72:0", 2.5), ("s-ilwy72:1", 2.5),                                             # scene 4
    ("s-fmdlgo:0", 1.0), ("s-fmdlgo:1", 1.5),                                             # logo
]
tl = {k: {"dur": d, "lead": 0, "pad_after": 0} for k, d in STEPS}
json.dump(tl, open("timeline.json", "w"), indent=1)
print(f"{len(STEPS)} steps, {sum(d for _, d in STEPS):.2f} s")
