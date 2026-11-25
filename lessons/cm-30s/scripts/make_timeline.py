"""Write timeline.json for the 30 s CM for slide makers (pictures only; owner 11/25: one subject, the phases of the Moon, from the memo to the talk).
Twelve bars of 2.5 s at 96 BPM, the same music and tempo as the learners' 30 s CM:
memo and copy (0–5 s), the AI's reply (5–9 s), the slide stopped at its first step (9–14 s), the room with the presenter view on the laptop and the slide on the screen, moved on three times (14–26 s), logo (26–30 s).
No voice; the narration only mirrors the two caption lines and is not read out.
Usage: python3 scripts/make_timeline.py
"""
import json, re
IDS = re.findall(r'<section[^>]*id="(s-[a-z0-9]+)"', open("deck.html").read())
DURS = [[2.5, 2.5], [1.2, 1.4, 1.4], [5.0], [4.0, 4.0, 4.0], [1.5, 2.5]]
tl = {f"{i}:{k}": {"dur": d, "lead": 0, "pad_after": 0} for i, ds in zip(IDS, DURS) for k, d in enumerate(ds)}
json.dump(tl, open("timeline.json", "w"), indent=1)
print(f"{len(tl)} steps, {sum(v['dur'] for v in tl.values()):.2f} s")
