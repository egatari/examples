"""Fetch the 1991-2020 normals (monthly mean temperature, monthly precipitation) for four stations
from the Japan Meteorological Agency (気象庁「過去の気象データ検索」の平年値の表) and save one CSV each.
The data is published under the 公共データ利用規約（第 1.0 版）, compatible with CC BY 4.0.
Usage: uv run --no-project --with pandas --with lxml --with requests python scripts/fetch_normals.py
"""
import datetime, io, pathlib
import pandas as pd, requests

STATIONS = {  # name: (prec_no, block_no)
    "sapporo": ("札幌", 14, 47412),
    "kanazawa": ("金沢", 56, 47605),
    "tokyo": ("東京", 44, 47662),
    "naha": ("那覇", 91, 47936),
}
URL = "https://www.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?prec_no={p}&block_no={b}&year=&month=&day=&view="
out = pathlib.Path(__file__).resolve().parent.parent / "data"
out.mkdir(exist_ok=True)
today = datetime.date.today().isoformat()
for key, (name, p, b) in STATIONS.items():
    url = URL.format(p=p, b=b)
    html = requests.get(url, headers={"User-Agent": "egatari-sample-fetch"}, timeout=30).content.decode("utf-8")
    t = [x for x in pd.read_html(io.StringIO(html)) if x.shape[0] >= 13][0]
    t.columns = ["_".join(dict.fromkeys(str(c) for c in col if "Unnamed" not in str(c))) for col in t.columns]
    first = t.columns[0]
    rows = t[t[first].astype(str).str.fullmatch(r"\d{1,2}月")]
    prec = [c for c in t.columns if c.startswith("降水量") and "合計" in c][0]
    temp = [c for c in t.columns if c.startswith("気温") and "平均" in c][0]
    df = pd.DataFrame({"month": rows[first].str.replace("月", "").astype(int),
                       "temp_mean_c": pd.to_numeric(rows[temp]), "precip_mm": pd.to_numeric(rows[prec])})
    with open(out / f"{key}.csv", "w", encoding="utf-8") as f:
        f.write(f"# {name} 平年値（1991～2020 年）。気象庁 {url} を {today} に取得\n")
        df.to_csv(f, index=False)
    print(key, name, len(df), "rows; annual precip", round(df.precip_mm.sum(), 1))
