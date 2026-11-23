"""ASR pass over the synthesized narration of this lesson: are the words that are easy to misread heard as intended?

Make the audio with Egatari Studio's local TTS (Irodori) in a copy of this folder:
    uv run --project tts python tts/synth.py <copy of lessons/tsurezure-ninnaji>
then, on Apple silicon, with the ja-tts-bench folder that holds scorer.py:
    uv run --no-project --with mlx-whisper --with pykakasi --with torch --with transformers --with soundfile \
        --with scipy python scripts/asr_check.py <copy> <out.json> <ja-tts-bench folder>

Same method as books/rashomon/scripts/asr_check.py, check 2 (teacher forcing): for each term in a step, the spoken
step (as synth.py sent it, readings applied; audio/seg_<digest>.json) is written in kana once per candidate reading,
differing only in the term, and Whisper large-v3 scores each kana sentence against the audio (sum of token
log-likelihoods). The term passes when the expected reading scores above every misreading; "margin" is that lead.
The free transcription in kana (Whisper with a hiragana prompt) is kept in the output for reading by eye.
Irodori is deterministic: the same text and voice give byte-identical audio, so a step is one sample.
"""
import json
import sys
from pathlib import Path

import mlx_whisper
import pykakasi

LESSON, OUT, BENCH = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]).expanduser()
sys.path.insert(0, str(BENCH))
from scorer import Scorer  # noqa: E402

MODEL = "mlx-community/whisper-large-v3-mlx"
KANA_PROMPT = "これは、ひらがなだけでかいたぶんしょうです。えーあいがすらいどをかきます。"
# term as synth.py speaks it: (expected kana, kana misreadings). Longer terms first.
# ALSO: other kana spellings of the expected reading (Whisper writes エーアイ as えいあい); the best of them is compared.
TERMS = {
    "兼好法師": ("けんこうほうし", ["かねよしほうし"]),
    "兼好": ("けんこう", ["かねよし"]),
    "法師": ("ほうし", ["ほうじ", "のりし"]),
    "八幡宮": ("はちまんぐう", ["やはたぐう", "はちまんみや"]),
    "現代語訳": ("げんだいごやく", ["げんだいごわけ"]),
    "助動詞": ("じょどうし", ["じょどうじ"]),
    "地の文": ("じのぶん", ["ちのぶん"]),
    "品詞": ("ひんし", ["ひんじ", "しなし"]),
    "本社": ("ほんしゃ", ["もとしゃ", "ほんじゃ"]),
    "仲間": ("なかま", ["ちゅうかん"]),
    "拝みます": ("おがみます", ["はいみます"]),
    "尊く": ("とうとく", ["そんく"]),
    "麓": ("ふもと", ["ろく"]),
    "一つ目": ("ひとつめ", ["いちつめ"]),
    "三つ目": ("みっつめ", ["さんつめ"]),
    "二つ": ("ふたつ", ["につ"]),
    "三つ": ("みっつ", ["さんつ"]),
    "表": ("ひょう", ["おもて"]),
}
ALSO = {"尊く": ["たっとく"]}
kks = pykakasi.kakasi()


def kana(s):
    """Kana of a spoken step; every term is replaced by its expected reading (pykakasi reads the rest)."""
    for t, (want, _) in TERMS.items():
        s = s.replace(t, "\0" + want + "\0")
    parts = s.split("\0")
    return "".join(p if i % 2 else "".join(x["hira"] for x in kks.convert(p)) for i, p in enumerate(parts)).replace(" ", "")


def variants(text, term):
    """The spoken step in kana once per candidate reading of term; longer terms that contain it keep their reading."""
    want, bad = TERMS[term]
    out = {}
    for c in [want] + ALSO.get(term, []) + bad:
        s = text
        for t in TERMS:
            if t != term and term in t:
                s = s.replace(t, "\0" + TERMS[t][0] + "\0")
        s = s.replace(term, "\0" + c + "\0")
        out[c] = "".join(p if i % 2 else kana(p) for i, p in enumerate(s.split("\0")))
    return out


man = json.loads((LESSON / "audio" / "manifest.json").read_text(encoding="utf-8"))["segments"]
scorer = Scorer()
results = []
for key, seg in man.items():
    wav = LESSON / "audio" / seg["file"]
    spoken = " ".join(p for turn in json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["tts"] for p in turn)
    rest, terms = spoken, []
    for t in TERMS:
        if t in rest:
            terms.append(t)
            rest = rest.replace(t, "")
    heard = mlx_whisper.transcribe(str(wav), path_or_hf_repo=MODEL, language="ja", initial_prompt=KANA_PROMPT)["text"].strip()
    checks = []
    for t in terms:
        sc = scorer.score(wav, variants(spoken, t), scale="sum")
        wants = [TERMS[t][0]] + ALSO.get(t, [])
        want = max(wants, key=lambda k: sc[k])
        margin = sc[want] - max(v for k, v in sc.items() if k not in wants)
        checks.append({"term": t, "want": want, "ok": margin > 0, "margin": round(margin, 1),
                       "scores": {k: round(v, 1) for k, v in sc.items()}})
    results.append({"key": key, "spoken": spoken, "kana": heard, "checks": checks})
    print(key, "OK" if all(c["ok"] for c in checks) else "CHECK",
          [(c["term"], c["margin"]) for c in checks], "|", heard, file=sys.stderr)
OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
