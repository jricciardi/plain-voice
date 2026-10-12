"""Analyze the plain-voice stress test: tells, lengths, constraints, ablations, multi-turn,
family identifiability, LLM judgments and (when present) the human review."""

import json
import math
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import os
ROOT = Path(os.environ.get("PV_EVAL_ROOT") or Path(__file__).resolve().parents[1])
RES = ROOT / "results"
RNG = np.random.default_rng(20261012)
FAMS = ["Claude", "GPT", "Gemini", "Grok", "MAI"]
MAIN = ["A-none", "C-skill-v1", "D-placebo", "E-original"]
NB = 2000


def read_jsonl(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []


def boot_ratio(df, num_cond, den_cond, col="tells_total", cluster="prompt_id"):
    """Ratio of means (num/den) with a cluster bootstrap over prompts. Rows are paired by design."""
    groups = {k: g for k, g in df.groupby(cluster)}
    keys = list(groups)
    sums = {k: (g.loc[g.cond == num_cond, col].sum(), (g.cond == num_cond).sum(),
                g.loc[g.cond == den_cond, col].sum(), (g.cond == den_cond).sum()) for k, g in groups.items()}
    arr = np.array([sums[k] for k in keys], dtype=float)
    point = (arr[:, 0].sum() / max(arr[:, 1].sum(), 1)) / max(arr[:, 2].sum() / max(arr[:, 3].sum(), 1), 1e-9)
    idx = RNG.integers(0, len(keys), size=(NB, len(keys)))
    s = arr[idx].sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = (s[:, 0] / s[:, 1]) / (s[:, 2] / s[:, 3])
    ratios = ratios[np.isfinite(ratios)]
    lo, hi = np.percentile(ratios, [2.5, 97.5]) if len(ratios) else (float("nan"), float("nan"))
    return float(point), float(lo), float(hi)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def fmt_ci(t, pct=False):
    p, lo, hi = t
    if pct:
        return f"{100 * p:.0f}% ({100 * lo:.0f} to {100 * hi:.0f})"
    return f"{p:.2f} ({lo:.2f} to {hi:.2f})"


def tells_section(df, out):
    t1 = df[(df.set == "test1") & (df.cond.isin(MAIN))].copy()
    out["n_replies_test1"] = int(len(t1))
    means = t1.groupby(["family", "cond"]).tells_total.mean().unstack()
    means.loc["All"] = t1.groupby("cond").tells_total.mean()
    out["mean_tells_per_reply"] = means.round(2).to_dict()
    rows = []
    for fam in FAMS + ["All"]:
        sub = t1 if fam == "All" else t1[t1.family == fam]
        if sub.empty:
            continue
        r = {"family": fam}
        for den in ("D-placebo", "A-none", "E-original"):
            r[f"C/{den.split('-')[0]}"] = boot_ratio(sub, "C-skill-v1", den)
            r[f"C/{den.split('-')[0]} per100w"] = boot_ratio(sub, "C-skill-v1", den, col="tells_per_100w")
        rows.append(r)
    out["ratios"] = rows
    # Poisson model with prompt-clustered errors
    try:
        import statsmodels.formula.api as smf
        import statsmodels.api as sm
        m = smf.glm("tells_total ~ C(cond, Treatment('C-skill-v1')) + C(model) + C(prompt_id)", data=t1,
                    family=sm.families.Poisson()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(t1.prompt_id)[0]})
        glm = {}
        for name in m.params.index:
            if name.startswith("C(cond"):
                lvl = name.split("[T.")[1].rstrip("]")
                ci = m.conf_int().loc[name]
                glm[f"{lvl} vs C (rate ratio)"] = (float(np.exp(m.params[name])), float(np.exp(ci[0])), float(np.exp(ci[1])))
        out["poisson_glm"] = glm
    except Exception as e:  # pragma: no cover
        out["poisson_glm_error"] = str(e)
    tell_cols = [c for c in t1.columns if c.startswith("tell_")]
    per_tell = t1.groupby("cond")[tell_cols].sum().T
    per_tell.index = [i.replace("tell_", "") for i in per_tell.index]
    out["per_tell_totals"] = per_tell.astype(int).to_dict()
    sec_cols = [c for c in t1.columns if c.startswith("section_")]
    out["per_section_mean"] = t1.groupby("cond")[sec_cols].mean().round(3).to_dict()
    watch_cols = [c for c in t1.columns if c.startswith("watch_")]
    w = t1.groupby("cond")[watch_cols].mean()
    out["watch_mean_per_reply"] = w.round(3).to_dict()
    out["length"] = t1.groupby("cond")[["words", "mean_sentence_words", "contractions_per_100w", "bullet_lines", "numbered_lines"]].mean().round(2).to_dict()
    out["length_by_family"] = t1.groupby(["family", "cond"]).words.mean().unstack().round(0).to_dict()
    out["contractions_by_family"] = t1.groupby(["family", "cond"]).contractions_per_100w.mean().unstack().round(2).to_dict()
    out["per_model_mean"] = t1.groupby(["model", "cond"]).tells_total.mean().unstack().round(2).to_dict()
    out["per_category_mean"] = t1.groupby(["category", "cond"]).tells_total.mean().unstack().round(2).to_dict()
    # user words and format compliance (pattern check)
    uw = t1[t1.category == "user_words"]
    if "user_words_reused" in uw:
        out["user_words_reuse_rate"] = uw.assign(reused=uw.user_words_reused > 0).groupby("cond").reused.mean().round(3).to_dict()
    return t1


def format_section(t1, out, prompts):
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    import tells
    ef = t1[t1.category.isin(["explicit_format"]) | t1.prompt_id.isin([p for p, v in prompts.items() if (v.get("format_request") or {}).get("type") in ("table", "schedule")])]
    ok = ef.apply(lambda r: tells.format_compliance(r["text"], prompts[r["prompt_id"]]), axis=1)
    ef = ef.assign(ok=ok)
    ef = ef[ef.ok.notna()]
    out["format_compliance_pattern"] = {c: wilson(int(g.ok.sum()), len(g)) for c, g in ef.groupby("cond")}


def ablation_section(df, out):
    ab = df[df.set == "ablation"]
    if ab.empty:
        return
    base = "C-skill-v1"
    rows = []
    for cond in sorted(ab.cond.unique()):
        if cond == base:
            continue
        sub = ab[ab.cond.isin([cond, base])]
        r = {"variant": cond, "ratio_vs_full": boot_ratio(sub, cond, base)}
        for sec in ("punctuation", "phrases", "vocabulary", "structure"):
            col = f"section_{sec}"
            r[f"{sec}_mean_variant"] = round(float(sub[sub.cond == cond][col].mean()), 3)
            r[f"{sec}_mean_full"] = round(float(sub[sub.cond == base][col].mean()), 3)
        r["words_variant"] = round(float(sub[sub.cond == cond].words.mean()), 1)
        r["words_full"] = round(float(sub[sub.cond == base].words.mean()), 1)
        r["contractions_variant"] = round(float(sub[sub.cond == cond].contractions_per_100w.mean()), 2)
        rows.append(r)
    out["ablations"] = rows


def multiturn_section(df, out):
    mt = df[df.set == "multiturn"]
    if mt.empty:
        return
    mt = mt.assign(turn=mt.turn.astype(int))
    out["multiturn_by_turn"] = mt.groupby(["turn", "cond"]).tells_total.mean().unstack().round(2).to_dict()
    c = mt[mt.cond == "C-skill-v1"]
    if len(c) > 5:
        slope = np.polyfit(c.turn.astype(float), c.tells_total.astype(float), 1)[0]
        out["multiturn_C_slope_per_turn"] = round(float(slope), 3)
    early = mt[mt.turn <= 2].groupby("cond").tells_total.mean()
    late = mt[mt.turn >= 6].groupby("cond").tells_total.mean()
    out["multiturn_early_vs_late"] = {"turns 1-2": early.round(2).to_dict(), "turns 6-8": late.round(2).to_dict()}


def identifiability_section(t1, out):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline, make_union
    res = {}
    for cond in MAIN:
        d = t1[t1.cond == cond]
        if d.family.nunique() < 3:
            continue
        X, y, g = d.text.values, d.family.values, d.prompt_id.values
        preds = np.empty(len(y), dtype=object)
        for tr, te in GroupKFold(n_splits=5).split(X, y, g):
            pipe = make_pipeline(
                make_union(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                           TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True)),
                LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced"))
            pipe.fit(X[tr], y[tr])
            preds[te] = pipe.predict(X[te])
        res[cond] = round(float(balanced_accuracy_score(y, preds)), 3)
    res["chance"] = round(1 / t1.family.nunique(), 3)
    out["family_identifiability_balanced_accuracy"] = res


def judgments_section(out):
    keys_p = ROOT / "judgments" / "keys.json"
    if not keys_p.exists():
        return None
    keys = json.loads(keys_p.read_text())
    rows = []
    for f in (ROOT / "judgments" / "pairs").glob("*/*.jsonl"):
        for o in read_jsonl(f):
            k = keys["pairs"].get(str(o.get("item")))
            if not k:
                continue
            pref, ai = str(o.get("prefer", "")).strip().lower(), str(o.get("ai_like", "")).strip().lower()
            s = k["skill_is"]
            rows.append({**k, "prefer": "skill" if pref == s else ("tie" if pref == "tie" else "other"),
                         "ai_like": "skill" if ai == s else ("same" if ai == "same" else "other")})
    pj = pd.DataFrame(rows)
    res = {}
    if not pj.empty:
        for (comp, judge), g in pj.groupby(["comparison", "judge"]):
            dec = g[g.prefer != "tie"]
            dai = g[g.ai_like != "same"]
            res.setdefault(comp, {})[judge] = {
                "n": int(len(g)),
                "prefers_skill": wilson(int((dec.prefer == "skill").sum()), len(dec)),
                "tie_rate": round(float((g.prefer == "tie").mean()), 3),
                "skill_less_ai_like": wilson(int((dai.ai_like == "other").sum()), len(dai)),
            }
        for comp, g in pj.groupby("comparison"):
            dec, dai = g[g.prefer != "tie"], g[g.ai_like != "same"]
            res.setdefault(comp, {})["all judges"] = {
                "n": int(len(g)), "prefers_skill": wilson(int((dec.prefer == "skill").sum()), len(dec)),
                "tie_rate": round(float((g.prefer == "tie").mean()), 3),
                "skill_less_ai_like": wilson(int((dai.ai_like == "other").sum()), len(dai))}
            fam = {}
            for f_, gg in g.groupby("family"):
                d1, d2 = gg[gg.prefer != "tie"], gg[gg.ai_like != "same"]
                fam[f_] = {"prefers_skill": wilson(int((d1.prefer == "skill").sum()), len(d1)),
                           "skill_less_ai_like": wilson(int((d2.ai_like == "other").sum()), len(d2))}
            res[comp]["by_family"] = fam
    out["judges"] = res

    # fidelity and format graders
    grows = []
    for f in (ROOT / "judgments" / "grades").glob("*/*.jsonl"):
        for o in read_jsonl(f):
            k = keys["grades"].get(str(o.get("item")))
            if not k:
                continue
            facts = [str(x).lower() for x in (o.get("facts") or [])][: k["n_facts"]]
            grows.append({**k, "missing": sum(x == "missing" for x in facts), "wrong": sum(x == "wrong" for x in facts),
                          "checked": len(facts), "invented": len(o.get("invented") or []), "format_v": str(o.get("format", "n/a")).lower()})
    gd = pd.DataFrame(grows)
    if not gd.empty:
        fid = {}
        for cond, g in gd[gd.n_facts > 0].groupby("cond"):
            tot = g.checked.sum()
            fid[cond] = {"facts_checked": int(tot), "missing_rate": round(float(g.missing.sum() / max(tot, 1)), 4),
                         "wrong_rate": round(float(g.wrong.sum() / max(tot, 1)), 4),
                         "invented_per_reply": round(float(g.invented.mean()), 3), "replies": int(len(g))}
        out["fidelity"] = fid
        fm = {}
        for cond, g in gd[gd.format.notna() & gd.format_v.isin(["yes", "partly", "no"])].groupby("cond"):
            fm[cond] = {"yes": wilson(int((g.format_v == "yes").sum()), len(g)), "partly_or_no": int((g.format_v != "yes").sum()), "n": int(len(g))}
        out["format_compliance_graders"] = fm
        dbl = gd.groupby(["model", "cond", "prompt_id"]).filter(lambda x: len(x) > 1)
        if not dbl.empty:
            agree = dbl.groupby(["model", "cond", "prompt_id"]).apply(lambda x: x.missing.nunique() == 1).mean()
            out["fidelity_grader_agreement_missing_count"] = round(float(agree), 3)

    # pattern-match labels
    lrows = []
    for f in (ROOT / "judgments" / "labels").glob("*/*.jsonl"):
        labeler = f.parent.name
        for o in read_jsonl(f):
            k = keys["labels"].get(str(o.get("item")))
            if k:
                lrows.append({**k, "item": o["item"], "labeler": labeler, "verdict": str(o.get("verdict", "")).lower()})
    ld = pd.DataFrame(lrows)
    if not ld.empty:
        prec = {}
        for tell, g in ld.groupby("tell"):
            dec = g[g.verdict.isin(["yes", "no"])]
            prec[tell] = {"precision": wilson(int((dec.verdict == "yes").sum()), len(dec)), "labels": int(len(g))}
        out["pattern_precision_llm"] = prec
        wide = ld.pivot_table(index="item", columns="labeler", values="verdict", aggfunc="first").dropna()
        if wide.shape[1] == 2:
            out["labeler_agreement"] = round(float((wide.iloc[:, 0] == wide.iloc[:, 1]).mean()), 3)
    return pj


def human_section(out, pj):
    key_p, resp_p = ROOT / "human" / "answer_key.json", ROOT / "human" / "responses.json"
    if not resp_p.exists():
        return
    key = json.loads(key_p.read_text())
    resp = json.loads(resp_p.read_text()).get("responses", {})
    pairs, matches = [], []
    for tid, r in resp.items():
        k = key.get(tid)
        if not k:
            continue
        if tid.startswith("p") and r.get("prefer"):
            side = k["skill_side"]
            pairs.append({**k, "id": tid, "prefer": "skill" if r["prefer"] == side else ("tie" if r["prefer"] == "tie" else "other"),
                          "ai_like": "skill" if r.get("ai_like") == side else ("same" if r.get("ai_like") == "same" else "other"),
                          "tags": r.get("tags", []), "note": r.get("note", ""), "flag": r.get("flag", False)})
        elif tid.startswith("m") and r.get("verdict"):
            matches.append({**k, "verdict": r["verdict"]})
    hp = pd.DataFrame(pairs)
    res = {"pairs_answered": int(len(hp)), "matches_answered": len(matches)}
    if not hp.empty:
        main = hp[hp.repeat_of.isna()]
        for comp, g in main.groupby("comparison"):
            dec, dai = g[g.prefer != "tie"], g[g.ai_like != "same"]
            res[comp] = {"n": int(len(g)), "prefers_skill": wilson(int((dec.prefer == "skill").sum()), len(dec)),
                         "ties": int((g.prefer == "tie").sum()),
                         "skill_less_ai_like": wilson(int((dai.ai_like == "other").sum()), len(dai))}
        rep = hp[hp.repeat_of.notna()]
        cons = []
        for _, r in rep.iterrows():
            o = hp[hp.id == r.repeat_of]
            if not o.empty:
                cons.append((o.iloc[0].prefer == r.prefer, o.iloc[0].ai_like == r.ai_like))
        if cons:
            res["self_consistency_prefer"] = round(sum(a for a, _ in cons) / len(cons), 3)
            res["self_consistency_ai_like"] = round(sum(b for _, b in cons) / len(cons), 3)
        res["tags"] = [t["text"] for r in pairs for t in r["tags"]]
        res["notes"] = [r["note"] for r in pairs if r["note"]]
        res["flags"] = [r["id"] for r in pairs if r["flag"]]
        # judge agreement with the human on overlapping pairs
        if pj is not None and not pj.empty:
            agree = {}
            hp2 = main.assign(pair_id=main.apply(lambda r: f"{r.model}|{r.prompt_id}|C-skill-v1~{r.comparison.split(' vs ')[1]}", axis=1))
            for judge, g in pj[pj.human_overlap].groupby("judge"):
                m = g.merge(hp2[["pair_id", "prefer", "ai_like"]], on="pair_id", suffixes=("_j", "_h"))
                if len(m):
                    pd_ = m[(m.prefer_h != "tie") & (m.prefer_j != "tie")]
                    ad_ = m[(m.ai_like_h != "same") & (m.ai_like_j != "same")]
                    agree[judge] = {"n": int(len(m)), "prefer_agreement": round(float((m.prefer_j == m.prefer_h).mean()), 3),
                                    "ai_like_agreement": round(float((m.ai_like_j == m.ai_like_h).mean()), 3),
                                    "prefer_agreement_decisive": round(float((pd_.prefer_j == pd_.prefer_h).mean()), 3) if len(pd_) else None,
                                    "ai_like_agreement_decisive": round(float((ad_.ai_like_j == ad_.ai_like_h).mean()), 3) if len(ad_) else None,
                                    "n_prefer_decisive": int(len(pd_)), "n_ai_like_decisive": int(len(ad_))}
            res["judge_agreement_with_human"] = agree
    if matches:
        md = pd.DataFrame(matches)
        res["pattern_precision_human"] = {t: wilson(int((g.verdict == "yes").sum()), int(g.verdict.isin(["yes", "no"]).sum())) for t, g in md.groupby("tell")}
        res["pattern_precision_human_overall"] = wilson(int((md.verdict == "yes").sum()), int(md.verdict.isin(["yes", "no"]).sum()))
    out["human"] = res


def robustness_section(df, out):
    """Re-estimate the main ratios with precision-weighted counts and with high-precision tells only."""
    prec = out.get("pattern_precision_llm")
    if not prec:
        return
    t1 = df[(df.set == "test1") & (df.cond.isin(MAIN))].copy()
    p = {k: v["precision"][0] for k, v in prec.items() if v["labels"] >= 8}
    high = [k for k, v in p.items() if v >= 0.75]
    t1["tells_high_precision"] = t1[[f"tell_{k}" for k in high]].sum(axis=1)
    t1["tells_weighted"] = sum(t1[f"tell_{k}"] * v for k, v in p.items())
    res = {"high_precision_tells": sorted(high)}
    for col in ("tells_high_precision", "tells_weighted"):
        rows = {}
        for fam in FAMS + ["All"]:
            sub = t1 if fam == "All" else t1[t1.family == fam]
            rows[fam] = {f"C/{d.split('-')[0]}": boot_ratio(sub, "C-skill-v1", d, col=col) for d in ("D-placebo", "A-none", "E-original")}
        res[col] = rows
    out["robustness"] = res


def main():
    df = pd.DataFrame(read_jsonl(RES / "replies.jsonl"))
    prompts = {p["id"]: p for p in read_jsonl(ROOT / "prompts" / "test1.jsonl")}
    out = {"suite_version": df.suite_version.iloc[0] if len(df) else None, "n_replies": int(len(df)),
           "replies_by_set": df.groupby("set").size().to_dict()}
    t1 = tells_section(df, out)
    format_section(t1, out, prompts)
    ablation_section(df, out)
    multiturn_section(df, out)
    identifiability_section(t1, out)
    dev = df[df.set == "dev"]
    if not dev.empty:
        out["dev_mean_tells"] = dev.groupby(["family", "cond"]).tells_total.mean().unstack().round(2).to_dict()
    pj = judgments_section(out)
    robustness_section(df, out)
    human_section(out, pj)
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=lambda o: o if not isinstance(o, (np.integer, np.floating)) else o.item()))
    print(json.dumps({k: out[k] for k in ("n_replies", "replies_by_set")}, indent=1))
    print("ratios (C vs D, A, E):")
    for r in out["ratios"]:
        print(f"  {r['family']:7s} C/D {fmt_ci(r['C/D'])}  C/A {fmt_ci(r['C/A'])}  C/E {fmt_ci(r['C/E'])}")


if __name__ == "__main__":
    main()
