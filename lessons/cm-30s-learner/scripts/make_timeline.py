"""Write timeline.json for the 30 s CM for learners (pictures only; owner 11/25, storyboard 2, made 30 s long).
Two bars of 2.5 s (96 BPM) per scene: the PDF (still), moves, can be heard, can be read (the page turn ends on the next spread), can be written on (a pen on the slide, then a marker in the book), logo.
No voice; the narration only mirrors the caption words and is not read out.
Usage: python3 scripts/make_timeline.py
"""
import json, re
IDS = re.findall(r'<section[^>]*id="(s-[a-z0-9]+)"', open("deck.html").read())
DURS = [[5.0], [1.6, 1.7, 1.7], [2.0, 1.6, 1.4], [3.4, 1.0], [0.6], [0.7, 1.3], [1.0, 1.0, 1.0], [1.5, 3.5]]
tl = {f"{i}:{k}": {"dur": d, "lead": 0, "pad_after": 0} for i, ds in zip(IDS, DURS) for k, d in enumerate(ds)}
json.dump(tl, open("timeline.json", "w"), indent=1)
print(f"{len(tl)} steps, {sum(v['dur'] for v in tl.values()):.2f} s")
