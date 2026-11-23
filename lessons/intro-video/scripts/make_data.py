"""Fictional numbers for the Egatari CM (業務改善の例). Run: python3 scripts/make_data.py

A fictional office checks applications. Waiting time follows the M/M/c queue
(Erlang C): applications arrive at LAM per day, one checker handles MU per day.
Writes data/queue.json: the curves before and after the check gets 2 割 faster
(MU 10 -> 12 per day, one checker), and today's point. Near capacity a small
speed-up cuts the wait a lot: that is the story of the CM's second panel.
"""
import json, math
from pathlib import Path

MU = 10.0      # applications the check handles per day now (fictional)
MU2 = 12.0     # after the improvement: 2 割 faster (fictional)
LAM = 9.8      # applications arriving per day now (fictional)

def wait_days(lam, mu, c):
    """Mean time in system W = Wq + 1/mu for M/M/c (Erlang C)."""
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return math.inf
    s = sum(a**k / math.factorial(k) for k in range(c))
    top = a**c / math.factorial(c) / (1 - rho)
    pw = top / (s + top)                 # probability an arrival waits
    wq = pw / (c * mu - lam)
    return wq + 1 / mu

xs = [round(x * 0.1, 1) for x in range(0, 100)]   # 0.0 .. 9.9 per day
one = [[x, round(wait_days(x, MU, 1), 3)] for x in xs if wait_days(x, MU, 1) <= 6.0]
two = [[x, round(wait_days(x, MU2, 1), 3)] for x in xs if wait_days(x, MU2, 1) <= 6.0]
now1 = round(wait_days(LAM, MU, 1), 1)
now2 = round(wait_days(LAM, MU2, 1), 2)
assert abs(wait_days(5, 10, 1) - 0.2) < 1e-9          # M/M/1 check: 1/(mu-lam)
assert wait_days(LAM, MU2, 1) < wait_days(LAM, MU, 1)
out = {"note": "架空の業務。M/M/c 待ち行列（Erlang C）で計算", "mu": MU, "mu_after": MU2, "lam": LAM,
       "curve_now": one, "curve_after": two, "wait_now": now1, "wait_after": now2}
Path(__file__).resolve().parent.parent.joinpath("data", "queue.json").write_text(
    json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")
print("now:", now1, "days; after:", now2, "days; points:", len(one), len(two))
