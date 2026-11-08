"""Prefectural population, 1920–2020, from the official census (e-Stat). Run:
  uv run --with openpyxl python scripts/make_data.py
Sources (総務省統計局, via e-Stat; 政府標準利用規約 / CC BY 4.0 compatible):
  raw/pop_1920_2015.csv   国勢調査 時系列データ「男女別人口－都道府県（大正９年～平成27年）」 statInfId=000031524010
  raw/census2020_t1-1.xlsx 令和２年国勢調査 人口等基本集計 第１－１表 statInfId=000032142402
Writes data/population.json. Numbers are only computed, never edited.
"""
import csv, json
from pathlib import Path
import openpyxl

R = Path(__file__).resolve().parent.parent
pop = {}   # code -> {year: population}
names = {}
with open(R / "raw" / "pop_1920_2015.csv", encoding="shift_jis") as f:
    for row in csv.DictReader(f):
        code = row["都道府県コード"]
        if not code.isdigit(): continue  # 0A, 0B: groupings, not prefectures
        names[code] = row["都道府県名"]
        v = (row.get("人口（総数）") or "").replace(",", "")
        if not row.get("西暦（年）"): continue
        if v.isdigit():
            pop.setdefault(code, {})[int(row["西暦（年）"])] = int(v)
ws = openpyxl.load_workbook(R / "raw" / "census2020_t1-1.xlsx", read_only=True, data_only=True).worksheets[0]
for row in ws.iter_rows(min_row=16, values_only=True):
    code5 = str(row[5] or "")
    if len(code5) == 5 and code5.endswith("000") and isinstance(row[7], int):
        pop.setdefault(code5[:2], {})[2020] = row[7]
assert len([c for c in pop if c != "00"]) == 47 and all(2020 in pop[c] for c in pop)
nat = pop["00"]
peak_year = max(nat, key=nat.get)
chg = {c: round((pop[c][2020] / pop[c][2015] - 1) * 100, 2) for c in pop if c != "00"}
since1920 = {c: round(pop[c][2020] / pop[c][1920], 2) for c in pop if c != "00"}
out = {
    "source": "総務省統計局「国勢調査」（e-Stat）を加工して作成",
    "national": sorted(nat.items()),
    "national_peak": [peak_year, nat[peak_year]],
    "names": {c: names.get(c) for c in pop},
    "change_2015_2020_pct": chg,
    "increased_2015_2020": sorted([c for c, v in chg.items() if v > 0]),
    "ratio_2020_to_1920": since1920,
    "below_1920": sorted([c for c, v in since1920.items() if v < 1]),
    "pop2020": {c: pop[c][2020] for c in pop},
    "pop1920": {c: pop[c][1920] for c in pop},
}
(R / "data" / "population.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("national 1920", nat[1920], "2020", nat[2020], "peak", peak_year, nat[peak_year])
print("increased", [names[c] for c in out["increased_2015_2020"]])
print("below 1920", [(names[c], since1920[c]) for c in out["below_1920"]])
top = sorted(since1920.items(), key=lambda kv: -kv[1])[:5]; print("top growth", [(names[c], v) for c, v in top])
print("min/max change", min(chg.values()), max(chg.values()))
