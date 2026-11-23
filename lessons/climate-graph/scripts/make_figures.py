"""From data/*.csv: print the numbers the lesson uses (and check the quiz answers), and draw one
climograph per station (images/<key>.png) on the same axes so they can be compared side by side.
Usage: uv run --no-project --with pandas --with matplotlib python scripts/make_figures.py
"""
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAMES = {"sapporo": "札幌", "kanazawa": "金沢", "tokyo": "東京", "naha": "那覇"}
for f in ["/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc"]:
    if pathlib.Path(f).exists():
        font_manager.fontManager.addfont(f); plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name(); break
d = {k: pd.read_csv(ROOT / "data" / f"{k}.csv", comment="#") for k in NAMES}

rng = {k: round(v.temp_mean_c.max() - v.temp_mean_c.min(), 1) for k, v in d.items()}
win = {k: round(v[v.month.isin([12, 1, 2])].precip_mm.sum(), 1) for k, v in d.items()}
summer = {k: round(v[v.month.isin([6, 7, 8])].precip_mm.sum(), 1) for k, v in d.items()}
for k in NAMES:
    v = d[k]
    print(f"{NAMES[k]}: 年平均 {v.temp_mean_c.mean():.1f} ℃, 最暖月 {v.temp_mean_c.max()} ℃ / 最寒月 {v.temp_mean_c.min()} ℃, 年較差 {rng[k]} ℃, "
          f"年降水量 {v.precip_mm.sum():.1f} mm, 冬（12〜2 月） {win[k]} mm, 夏（6〜8 月） {summer[k]} mm")
qa1 = max(rng, key=rng.get); qa2 = max(win, key=win.get)
print("問 1（年較差が最も大きい）:", NAMES[qa1], rng); print("問 2（冬の降水量が最も多い）:", NAMES[qa2], win)
assert (qa1, qa2) == ("sapporo", "kanazawa"), "quiz answers changed: fix deck.html"
# claims in the narration and slides
K = d["kanazawa"]; assert K.loc[K.precip_mm.idxmax(), "month"] == 12, "金沢の最多月は 12 月"
assert round(win["kanazawa"] / win["tokyo"]) == 4, "金沢の冬は東京のおよそ 4 倍"
assert d["sapporo"].temp_mean_c.min() < 0 and d["naha"].temp_mean_c.min() == 17.3
for k in ("tokyo", "naha"): assert summer[k] > win[k], k + " は夏に雨が多い"
print("claims ok")

TMAX, PMAX = 30, 350
for k, v in d.items():
    fig, ax = plt.subplots(figsize=(6.4, 4.6), dpi=150)
    ax.bar(v.month, v.precip_mm, color="#4a7fc1", width=0.7, label="降水量")
    ax.set_ylim(0, PMAX); ax.set_ylabel("降水量（mm）", fontsize=22); ax.set_xticks([1, 3, 5, 7, 9, 11]); ax.tick_params(labelsize=20)
    ax.set_xlabel("月", fontsize=22)
    t = ax.twinx(); t.plot(v.month, v.temp_mean_c, color="#c0392b", marker="o", lw=2.5, label="気温")
    t.set_ylim(-10, TMAX); t.set_ylabel("気温（℃）", fontsize=22); t.tick_params(labelsize=20); t.axhline(0, color="#999", lw=0.8)
    ax.set_title(NAMES[k], fontsize=26)
    for s in ("top",): ax.spines[s].set_visible(False); t.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(ROOT / "images" / f"{k}.png"); plt.close(fig)
# winter totals, wide (for a full-width slot)
order = sorted(NAMES, key=lambda k: win[k])
fig, ax = plt.subplots(figsize=(12.8, 3.4), dpi=150)
bars = ax.barh([NAMES[k] for k in order], [win[k] for k in order], color=["#9db8dc" if k != "kanazawa" else "#1f4e8c" for k in order], height=0.62)
for b_, k in zip(bars, order): ax.text(b_.get_width() + 8, b_.get_y() + b_.get_height() / 2, f"{win[k]} mm", va="center", fontsize=22)
ax.set_xlim(0, 820); ax.tick_params(labelsize=22); ax.set_xticks([])
for s_ in ("top", "right", "bottom"): ax.spines[s_].set_visible(False)
ax.set_title("冬（12〜2 月）の降水量の合計（平年値）", fontsize=24)
fig.tight_layout(); fig.savefig(ROOT / "images" / "winter.png"); plt.close(fig)
print("wrote images/*.png")
