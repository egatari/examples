"""Write the part data for the ja and en decks from data/budget.json (same numbers in both).
Run after make_data.py: python3 scripts/make_parts.py
"""
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
d = json.loads((R / "data" / "budget.json").read_text(encoding="utf-8"))
for lang in ("ja", "en"):
    L = (lambda k: k) if lang == "ja" else (lambda k: d["en"][k])
    out = R / lang / "data"
    out.mkdir(parents=True, exist_ok=True)
    yen = "億円" if lang == "ja" else "¥100M"
    if lang == "ja":
        kpi = {"cards": [
            {"label": "予算の総額", "value": d["total"], "digits": 0, "unit": "億円",
             "delta": {"dir": "up", "text": f"前年度比 +{d['growth_pct']} %", "good": True}},
            {"label": "市民 1 人あたり", "value": d["per_person_man"], "digits": 1, "unit": "万円"},
            {"label": "人口", "value": d["population"] // 10000, "unit": "万人"}]}
    else:  # same numbers, English units: 620 億円 = ¥62.0bn, 41.3 万円 = ¥413k
        kpi = {"cards": [
            {"label": "Total budget", "value": round(d["total"] / 10, 1), "digits": 1, "prefix": "¥", "unit": "bn",
             "delta": {"dir": "up", "text": f"+{d['growth_pct']} % on last year", "good": True}},
            {"label": "Per resident", "value": round(d["per_person_man"] * 10), "prefix": "¥", "unit": "k"},
            {"label": "Population", "value": d["population"] // 1000, "unit": "k"}]}
    pie = {"slices": [{"label": L(k), "value": v, **({"tone": "emph"} if k == "福祉" else {})} for k, v in d["spend"].items()],
           "center": ("総額\n620 億円" if lang == "ja" else "Total\n¥62.0bn")}
    per10k = {"series": [{"label": "1 万円のうち" if lang == "ja" else "Out of ¥10,000"}],
              "groups": [{"label": L(k), "value": int(v), **({"tone": "emph"} if k == "福祉" else {})}
                         for k, v in sorted(d["per_10k"].items(), key=lambda kv: -kv[1])]}
    delta = {"series": [{"label": "前年度からの増減" if lang == "ja" else "Change from last year"}],
             "groups": [{"label": L(k), "value": (v if lang == "ja" else round(v / 10, 2)), **({"tone": "emph"} if v < 0 else {})} for k, v in d["delta"].items()]}
    income = {"slices": [{"label": L(k), "value": v, **({"tone": "emph"} if k == "借り入れ（市債）" else {})} for k, v in d["income"].items()],
              "center": ("収入\n620 億円" if lang == "ja" else "Income\n¥62.0bn")}
    for name, obj in [("kpi", kpi), ("pie", pie), ("per10k", per10k), ("delta", delta), ("income", income)]:
        (out / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
print("ok")
