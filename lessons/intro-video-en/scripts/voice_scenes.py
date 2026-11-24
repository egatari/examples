"""Voice each scene's sentence once (no choppy per-step voice), cut it at the phrase boundaries and
register the pieces as imported audio for the scene's steps; write timeline.json so each step lasts as long
as its piece and the last step of a scene pads to the scene's bar boundary (96 BPM, 2.5 s bars).

English version (bob, --engine voxcpm2). Usage (owner 11/24: one sentence = one voice; 0.5 s of silence on the logo at the end):
  1. egatari tts on a copy whose narration has the whole sentence in each scene's first step  -> WHOLE/audio
  2. word timestamps of those clips (mlx-whisper) -> words.json, CUT_AFTER below names the last word of each phrase
  3. python scripts/voice_scenes.py WHOLE/audio/manifest.json words.json PERSTEP/audio/manifest.json
     (PERSTEP = egatari tts on the real narration, only for the steps' inputHash)
"""
import hashlib, json, pathlib, sys
import numpy as np, soundfile as sf

HERE = pathlib.Path(__file__).resolve().parent.parent
SCENES = [  # (first-step key of the whole clip, step keys in order, scene end on the timeline, number of phrase cuts by word index after which to cut)
    ("s-ul4ddb:0", ["s-ul4ddb:0", "s-mxm2rm:0", "s-c6djpf:0", "s-dm2ae2:0"], 5.0, ["with", "AI,", "still"]),
    ("s-fcany4:0", ["s-fcany4:0", "s-fcany4:1", "s-fcany4:2"], 15.0, ["instructions,", "reply,"]),
    ("s-xex3aj:0", ["s-xex3aj:0", "s-xex3aj:1", "s-xex3aj:2"], 22.5, ["Overflows.", "them,"]),
    ("s-ilwy72:0", ["s-ilwy72:0", "s-ilwy72:1"], 27.5, ["is,"]),
    ("s-fmdlgo:0", ["s-fmdlgo:0", "s-fmdlgo:1"], 30.5, ["file"]),   # 30.0 + 0.5 s of silence on the logo
]
# a short held pause after a comma, where a slide needs time for its motion (silence after the piece, before the next one)
HOLD = {"s-mxm2rm:0": 0.45}
whole_man, words_path, per_man = (json.load(open(p)) for p in sys.argv[1:4])
whole_dir = pathlib.Path(sys.argv[1]).parent
words = json.load(open(words_path)) if isinstance(words_path, str) else words_path
words = json.load(open(sys.argv[2]))
seg = per_man["segments"]
out_dir = HERE / "audio"; out_dir.mkdir(exist_ok=True)
man = {"segments": {}}; tl = {}; t0 = 0.0
for key, steps, end, cut_after in SCENES:
    x, sr = sf.read(whole_dir / whole_man["segments"][key]["file"], dtype="float32")
    mono = x if x.ndim == 1 else x.mean(axis=1)
    ws = words[key]; cuts = []; i = 0
    for target in cut_after:   # the next word (in order) that ends with this text
        while not ws[i][0].endswith(target): i += 1
        a = ws[i][2]; b = min(a + 0.35, ws[i + 1][1] + 0.4 if i + 1 < len(ws) else a + 0.35); i += 1
        fr = int(0.02 * sr); lo, hi = int((a - 0.03) * sr), int(b * sr)
        rms = [np.sqrt(np.mean(mono[s:s + fr] ** 2)) for s in range(lo, hi - fr, fr // 2)]
        cuts.append((lo + int(np.argmin(rms)) * (fr // 2) + fr // 2) / sr)
    bounds = [0.0] + cuts + [len(mono) / sr]
    for j, k in enumerate(steps):
        piece = x[int(bounds[j] * sr):int(bounds[j + 1] * sr)]
        tmp = out_dir / "_piece.wav"; sf.write(tmp, piece, sr, subtype="PCM_16")
        h = hashlib.sha256(tmp.read_bytes()).hexdigest(); f = f"imp_{h[:16]}.wav"; tmp.rename(out_dir / f)
        dur = round(len(piece) / sr, 3)
        man["segments"][k] = {"file": f, "dur": dur, "cues": [], "sync": "none", "kind": "imported", "inputHash": seg[k]["inputHash"]}
        last = j == len(steps) - 1
        d = round(end - t0, 3) if last else round(dur + HOLD.get(k, 0), 3)
        tl[k] = {"dur": d, "lead": 0, "pad_after": 0}; t0 += d
        print(k, "piece", dur, "step", d)
json.dump(man, open(out_dir / "manifest.json", "w"), indent=1, ensure_ascii=False)
json.dump(tl, open(HERE / "timeline.json", "w"), indent=1)
print("total", round(t0, 3))
