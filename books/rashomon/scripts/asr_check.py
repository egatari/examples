"""ASR pass over the synthesized narration of 羅生門: are the marked readings heard as intended?

First make the audio with Egatari Studio's local TTS (Irodori), in a copy of this folder:
    uv run --project tts python tts/synth.py <copy of books/rashomon>
then, on Apple silicon:
    uv run --no-project --with mlx-whisper --with pykakasi python scripts/asr_check.py <copy> <out.json>

For every step whose narration has a reading to check, transcribe its wav with Whisper large-v3 (mlx, local) twice:
  A. plain (Whisper writes kanji),
  B. with a hiragana-only initial prompt, which pushes Whisper to write what it hears in kana.
A term passes when no misreading form appears in A or B, and the expected kana appears in B (converted to hiragana)
or the term itself appears in A. 仕方がなく、した passes when neither pass hears 仕方を.
"""
import json
import re
import sys
from pathlib import Path

import mlx_whisper
import pykakasi

LESSON, OUT = Path(sys.argv[1]), Path(sys.argv[2])
MODEL = "mlx-community/whisper-large-v3-mlx"
TERMS = {  # term: (expected kana, misreadings)
    "二重傍線": ("にじゅうぼうせん", ["そばせん", "そば線", "側線"]),
    "傍線": ("ぼうせん", ["そばせん", "そば線", "側線"]),
    "下人": ("げにん", ["したひと", "下の人", "しもびと", "したびと"]),
    "盗人": ("ぬすびと", ["ぬすっと", "盗っ人", "ぬすと"]),
    "六分": ("ろくぶ", ["ろくふん", "ろっぷん", "6分", "六分間"]),
    "四分": ("しぶ", ["よんふん", "よんぷん", "4分", "四分間"]),
    "己": ("おれ", ["おのれ"]),
    "引剥": ("ひはぎ", ["ひきはぎ", "ひきはがし"]),
}
KANA_PROMPT = "これは、ひらがなだけでかいたぶんしょうです。げにんは、ろうばのはなしをきいていました。"
kks = pykakasi.kakasi()
hira = lambda s: "".join(x["hira"] for x in kks.convert(s))


def steps():
    md = (LESSON / "narration.md").read_text(encoding="utf-8")
    sid = None
    for line in md.split("\n"):
        m = re.match(r"## .*\{#([^}]+)\}", line)
        if m:
            sid = m.group(1)
            continue
        m = re.match(r"\[(\w+)\]\s*(.*)", line)
        if m and sid:
            yield f"{sid}:{m.group(1)}", m.group(2)


man = json.loads((LESSON / "audio" / "manifest.json").read_text(encoding="utf-8"))
print("manifest keys:", list(man)[:6], file=sys.stderr)
results = []
for key, text in steps():
    terms = [t for t, _ in re.findall(r"\{([^|{}]+)\|([^{}]*)\}", text) if t in TERMS]
    pause = "仕方がなく、した" in text
    if not terms and not pause:
        continue
    seg = man.get("segments", man).get(key) if isinstance(man.get("segments", man), dict) else None
    if seg is None:
        seg = next((s for s in man.get("segments", []) if s.get("key") == key), None)
    wav = LESSON / "audio" / (seg.get("file") or seg.get("wav"))
    a = mlx_whisper.transcribe(str(wav), path_or_hf_repo=MODEL, language="ja")["text"].strip()
    b = mlx_whisper.transcribe(str(wav), path_or_hf_repo=MODEL, language="ja", initial_prompt=KANA_PROMPT)["text"].strip()
    hb = hira(b)
    checks = []
    for t in dict.fromkeys(terms):
        want, bad = TERMS[t]
        n = len(re.findall(r"\{" + t + r"\|", text))
        badhit = [x for x in bad if x in a or x in b or x in hb]
        heard = want in hb or (t in a and t not in ("六分", "四分"))
        if t in ("六分", "四分"):   # Whisper writes 六分 for both readings; only kana can tell
            heard = want in hb
        checks.append({"term": t, "want": want, "times": n, "ok": heard and not badhit, "misread": badhit})
    if pause:
        bad = [x for x in ("仕方を", "しかたを") if x in a or x in b or x in hb]
        checks.append({"term": "仕方がなく、した", "want": "しかたがなく", "ok": not bad and ("しかたがなく" in hb or "仕方がなく" in a), "misread": bad})
    r = {"key": key, "plain": a, "kana": b, "checks": checks}
    results.append(r)
    print(key, "OK" if all(c["ok"] for c in checks) else "CHECK", [(c["term"], c["ok"], c["misread"]) for c in checks], file=sys.stderr)
OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
