"""Fictional budget of a fictional city (A 市), for residents. Run: python3 scripts/make_data.py
Every number on the slides (ja and en) comes from data/budget.json. Amounts in 億円.
"""
import json
from pathlib import Path

POP = 150_000
SPEND = {"福祉": 229.4, "教育": 74.4, "道路・まちづくり": 68.2, "健康・ごみ": 55.8,
         "借金の返済": 62.0, "市の運営": 74.4, "その他": 55.8}
SPEND_PREV = {"福祉": 220.1, "教育": 70.2, "道路・まちづくり": 71.5, "健康・ごみ": 54.9,
              "借金の返済": 63.8, "市の運営": 73.6, "その他": 53.1}
INCOME = {"市税": 217.0, "国・県からのお金": 155.0, "地方交付税": 93.0, "借り入れ（市債）": 55.8, "その他": 99.2}
EN = {"福祉": "Welfare", "教育": "Education", "道路・まちづくり": "Roads & town", "健康・ごみ": "Health & waste",
      "借金の返済": "Debt repayment", "市の運営": "Administration", "その他": "Other",
      "市税": "City taxes", "国・県からのお金": "National & prefectural grants", "地方交付税": "Tax allocation",
      "借り入れ（市債）": "Borrowing (bonds)"}
total = round(sum(SPEND.values()), 1)
total_prev = round(sum(SPEND_PREV.values()), 1)
assert abs(total - round(sum(INCOME.values()), 1)) < 1e-6, "spending and income must balance"
per_person = round(total * 1e8 / POP / 1e4, 1)            # 万円
per_10k = {k: round(v / total * 10000, -1) for k, v in SPEND.items()}   # 1 万円あたり（10 円単位）
per_10k[max(per_10k, key=per_10k.get)] += 10000 - sum(per_10k.values())  # round so it sums to 10,000
delta = {k: round(SPEND[k] - SPEND_PREV[k], 1) for k in SPEND}
out = {"population": POP, "total": total, "total_prev": total_prev,
       "growth_pct": round((total / total_prev - 1) * 100, 1), "per_person_man": per_person,
       "spend": SPEND, "per_10k": per_10k, "delta": delta, "income": INCOME, "en": EN}
assert sum(per_10k.values()) == 10000
Path(__file__).resolve().parent.parent.joinpath("data", "budget.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(total, total_prev, out["growth_pct"], per_person, per_10k, delta)
