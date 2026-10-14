# plain-voice evaluation

How the skill was stress-tested, with everything needed to rerun it.

- [RESULTS.md](RESULTS.md): what happened in both rounds and what it means for the skill.
- [PREREGISTRATION.md](PREREGISTRATION.md): hypotheses, design and pass marks for each round, written before its replies existed, plus every later change and why.
- [TUNING.md](TUNING.md): how the v2 candidate was chosen, and why it didn't ship.
- [results/TABLES.md](results/TABLES.md) (round 1) and [results/ROUND2.md](results/ROUND2.md) (round 2): every table.

## Layout

| Path | What it is |
|---|---|
| `prompts/` | Dev, test-1 and sealed test-2 prompt sets, multi-turn scripts, their SHA-256 hashes, and the drafts and WildChat filter they were built from. Sources and licenses are in [prompts/README.md](prompts/README.md). |
| `conditions/` | The text placed in each model's instructions: none, skill v1, placebo, the original Claude-only skill, six versions with one section removed, and the v2 candidates. |
| `manifest*.json` | Every generation job: model, condition, repeat, batch and the full instructions sent. File paths are written as `<eval>`, meaning this folder; the scripts map it to wherever the repo is checked out. |
| `scripts/` | Prompt assembly, manifests, the tell-counting suite and its tests, scoring, judging, analysis and reporting. |
| `review-app/` | The local app used for the blind human review. |
| `rater-kit/` | Round 3, in progress: a reading test raters do in short sessions, a form for sending in real prompts, and how to build kits and analyze results. See [rater-kit/README.md](rater-kit/README.md). |
| `human/` | Review tasks, the answer key used to unblind them, the responses, and superseded files kept for the record. |
| `judgments/` | Every judge, grader and labeler answer, with the keys that map them back to replies. |
| `results/` | Scored replies with full text, summaries and tables. |

Raw generation files (`raw/`) and judge input manifests aren't committed: the replies are all in `results/*.jsonl`, and the judge manifests can be rebuilt with the scripts below.

## Rerunning

Requires Python 3.9+ with pandas, numpy, scipy, scikit-learn and statsmodels. Generation and judging ran through GitHub Copilot agent workflows; any harness that can send each manifest job's `prompt` to its `model` and save the reply file will do.

```sh
python scripts/test_tells.py                 # tell-suite unit tests
python scripts/assemble_prompts.py           # rebuild prompt sets and check them against prompts/SHA256SUMS

# Round 1: skill v1 on test-1
python scripts/build_manifest.py             # generation jobs; run them, then:
python scripts/parse_and_score.py            # results/replies.jsonl
python scripts/build_human_tasks.py          # human/tasks.json and human/answer_key.json
python scripts/build_judging.py              # judge_manifest.json; run its jobs, then:
./scripts/review.sh                          # human review at http://127.0.0.1:8765
python scripts/analyze.py                    # results/summary.json
python scripts/report.py                     # results/TABLES.md

# Round 2: skill v2 on sealed test-2
python scripts/build_manifest_round2.py      # run its jobs, then:
python scripts/parse_and_score.py --manifest manifest_round2.json --out results/replies_round2.jsonl
python scripts/build_judging_round.py --replies results/replies_round2.jsonl --set test2 \
    --skill H-skill-v2 --against A-none C-skill-v1 --round t2   # run its jobs, then:
python scripts/analyze_round2.py             # results/round2_summary.json and results/ROUND2.md

# Round 3 (in progress): human reading test
python scripts/build_rater_kits.py --out rater-kit/out --blank-names --raters "Rater 1,Rater 2,Jay"
python scripts/analyze_ratings.py --key rater-kit/out/key.json path/to/results/
```
