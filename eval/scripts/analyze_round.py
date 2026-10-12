"""Summarize a judging round built by build_judging_round.py."""

import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def fmt(t):
    return f"{100 * t[0]:.0f}% ({100 * t[1]:.0f}–{100 * t[2]:.0f})" if t[0] == t[0] else "n/a"


def load(round_name):
    d = ROOT / "judgments" / round_name
    keys = json.loads((d / "keys.json").read_text())
    pairs, grades = [], []
    for f in (d / "pairs").glob("*/*.jsonl"):
        for line in f.read_text().splitlines():
            try:
                o = json.loads(line)
            except Exception:
                continue
            k = keys["pairs"].get(str(o.get("item")))
            if k:
                s = k["skill_is"]
                p, a = str(o.get("prefer", "")).lower(), str(o.get("ai_like", "")).lower()
                pairs.append({**k, "prefer": "skill" if p == s else ("tie" if p == "tie" else "other"),
                              "ai": "skill" if a == s else ("same" if a == "same" else "other"), "reason": o.get("reason", "")})
    for f in (d / "grades").glob("*/*.jsonl"):
        for line in f.read_text().splitlines():
            try:
                o = json.loads(line)
            except Exception:
                continue
            k = keys["grades"].get(str(o.get("item")))
            if k:
                facts = [str(x).lower() for x in (o.get("facts") or [])][: k["n_facts"]]
                grades.append({**k, "missing": sum(x == "missing" for x in facts), "wrong": sum(x == "wrong" for x in facts),
                               "checked": len(facts), "invented": len(o.get("invented") or []), "format_v": str(o.get("format", "n/a")).lower()})
    return pd.DataFrame(pairs), pd.DataFrame(grades)


def main():
    round_name = sys.argv[1]
    pj, gd = load(round_name)
    out = {"round": round_name}
    if not pj.empty:
        res = {}
        for comp, g in pj.groupby("comparison"):
            dec, dai = g[g.prefer != "tie"], g[g.ai != "same"]
            res[comp] = {"n": int(len(g)), "prefers_skill": wilson(int((dec.prefer == "skill").sum()), len(dec)),
                         "skill_less_ai_like": wilson(int((dai.ai == "other").sum()), len(dai)),
                         "by_category": {c: wilson(int((x.prefer == "skill").sum()), int((x.prefer != "tie").sum())) for c, x in g.groupby("category")},
                         "by_family": {c: wilson(int((x.prefer == "skill").sum()), int((x.prefer != "tie").sum())) for c, x in g.groupby("family")}}
            print(f"{comp}: n={len(g)} prefers skill {fmt(res[comp]['prefers_skill'])}, finds skill less AI-like {fmt(res[comp]['skill_less_ai_like'])}")
            print("   by category:", "; ".join(f"{c} {100 * v[0]:.0f}%" for c, v in sorted(res[comp]["by_category"].items(), key=lambda x: x[1][0])))
            print("   by family:", "; ".join(f"{c} {100 * v[0]:.0f}%" for c, v in res[comp]["by_family"].items()))
        out["judges"] = res
    if not gd.empty:
        fid = {}
        for cond, g in gd[gd.n_facts > 0].groupby("cond"):
            tot = g.checked.sum()
            fid[cond] = {"replies": int(len(g)), "missing_rate": float(g.missing.sum() / max(tot, 1)), "wrong_rate": float(g.wrong.sum() / max(tot, 1)),
                         "invented_per_reply": float(g.invented.mean())}
            print(f"fidelity {cond}: replies {len(g)}, missing {100 * fid[cond]['missing_rate']:.1f}%, wrong {100 * fid[cond]['wrong_rate']:.1f}%, invented/reply {fid[cond]['invented_per_reply']:.2f}")
        out["fidelity"] = fid
        fm = {c: wilson(int((g.format_v == "yes").sum()), len(g)) for c, g in gd[gd.format.notna()].groupby("cond")}
        if fm:
            print("format followed:", {c: fmt(v) for c, v in fm.items()})
        out["format"] = fm
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / f"round_{round_name}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
