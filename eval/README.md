# plain-voice evaluation

How the skill was stress-tested, with everything needed to rerun it.

- [PREREGISTRATION.md](PREREGISTRATION.md): hypotheses, design, measures and thresholds, written before any test-1 replies existed, plus amendments made after the pilot.
- [RESULTS.md](RESULTS.md): what happened, written up after the run. [results/TABLES.md](results/TABLES.md) has every table.

## Layout

| Path | What it is |
|---|---|
| `prompts/` | Dev, test-1 and sealed test-2 prompt sets, multi-turn scripts and their SHA-256 hashes. Sources and licenses are in [prompts/README.md](prompts/README.md). |
| `conditions/` | The text placed in each model's instructions per condition: none, skill v1, placebo, the original Claude-only skill, and six versions with one section removed. |
| `manifest.json` | Every generation job (model, condition, repeat, batch, full instructions). |
| `scripts/` | Prompt assembly, manifest building, the tell-counting suite and its tests, scoring, judging, analysis and reporting. |
| `review-app/` | The local app used for the blind human review. |
| `human/` | Human review tasks, the answer key used to unblind them, and the responses. |
| `results/` | Scored replies, judgments, the summary and tables. |

Raw generation and judge outputs (`raw/`, `judgments/`) aren't committed; `results/replies.jsonl` holds every reply's text and scores.

## Rerunning

Requires Python 3.9+ with pandas, numpy, scipy, scikit-learn and statsmodels for analysis. Generation and judging ran through GitHub Copilot agent workflows; any harness that can send each manifest job's `prompt` to its `model` and save the reply file will do.

```sh
python scripts/assemble_prompts.py    # rebuild prompt sets (checks against prompts/SHA256SUMS)
python scripts/build_manifest.py      # rebuild generation jobs
# run every job in manifest.json, then:
python scripts/parse_and_score.py     # results/replies.jsonl
python scripts/build_human_tasks.py   # human/tasks.json and human/answer_key.json
python scripts/build_judging.py       # judge_manifest.json; run its jobs, then:
./scripts/review.sh                   # human review at http://127.0.0.1:8765
python scripts/analyze.py             # results/summary.json
python scripts/report.py              # results/TABLES.md
python scripts/test_tells.py          # tell-suite unit tests
```
