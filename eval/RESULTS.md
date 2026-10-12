# Results

Two rounds, run October 12, 2026. Round 1 scored skill v1 against no skill, a placebo and the original Claude-only skill on test-1, plus ablations, a multi-turn check and a blind human review. Round 2 scored the revised skill (v2) once on the sealed test-2 set. Every table is in [results/TABLES.md](results/TABLES.md) (round 1) and [results/ROUND2.md](results/ROUND2.md) (round 2). Hypotheses and thresholds were written down first, in [PREREGISTRATION.md](PREREGISTRATION.md).

## Summary

The skill does what it says. Across 10 models from 5 families, replies written with it had about a tenth as many counted tells as replies written without it, and a sixth as many as replies written with a one-line placebo ("Write plainly and naturally."). Judges from other model families found the skill's reply less like stock AI in 93% of pairs, and the human rater did in 12 of 13 pairs where he picked a side.

It doesn't make replies better on average. Judges preferred the skill's reply about half the time. They favored it for emails, status updates and posts, where it sounds more natural and invents less, and favored the no-skill reply for summaries, how-tos and format requests, where they valued completeness and lists that are easy to scan. The human rater's preferences split evenly too, and weren't consistent enough to say more.

A revised version, v2, added two rules: use a real list for steps, options, action items and dates, and never drop a fact, name, date or step while shortening. On the sealed test-2 prompts it matched v1 on stock-AI-ness and overall tells, cut Grok's tells by about a third and invented fewer details. It also missed more required facts, and MAI stayed above the tells bar. By the rule written before the round, v1 stays. Most of v2's fidelity gap came from a single advice prompt; without it, v2 and v1 missed facts at about the same rate.

v1's main result replicated on the sealed prompts: 0.10 of the no-skill tell count, the same as round 1.

## Round 1: skill v1 on test-1

10 models (Claude Opus 5.5 and Haiku 5.5; GPT-6.1 Sol, GPT-5.5 and GPT-5 mini; Gemini 3.8 Flash and 3.7 Flash; Grok 4.7 and 4.5; MAI-Code-1.1-Flash), 53 prompts, 4 conditions, 3 repeats: 6,360 single-turn replies, plus 640 multi-turn replies and 840 for ablations.

### Tells

Mean counted tells per reply: 8.8 with no skill, 5.9 with the placebo, 1.4 with the original skill and 0.9 with v1.

| Family | v1 against placebo | v1 against no skill | v1 against original skill |
|---|---|---|---|
| Claude | 0.06 (0.03–0.10) | 0.03 (0.02–0.05) | 0.45 (0.29–0.60) |
| GPT | 0.20 (0.17–0.25) | 0.17 (0.14–0.21) | 0.57 (0.48–0.68) |
| Gemini | 0.02 (0.01–0.04) | 0.01 (0.01–0.03) | 0.40 (0.25–0.54) |
| Grok | 0.31 (0.25–0.38) | 0.21 (0.16–0.26) | 0.75 (0.61–0.90) |
| MAI | 0.50 (0.40–0.61) | 0.44 (0.37–0.51) | 1.00 (0.84–1.19) |
| All | 0.16 (0.13–0.18) | 0.10 (0.09–0.13) | 0.66 (0.59–0.72) |

Ratios of mean tells per reply, with 95% intervals from resampling prompts. Below 1 means fewer tells with v1.

The pre-registered bar was half the placebo's tells in every family. Four families clear it easily. MAI's ratio is 0.503, so hypothesis 1 fails by a hair. MAI-Code-1.1-Flash also gains nothing from v1 over the original skill.

The original Claude-only skill already did most of the work: 84% fewer tells than no skill overall, ranging from 40% fewer for GPT-5 mini to 98% fewer for Gemini 3.8 Flash. Extending the list across families removed another third of what was left.

Most tells were structural. Bold labels, bold through prose, bold or markdown headers, horizontal rules, option menus, emoji and unrequested tables made up 68% of counted tells without the skill, and fell 95% with it. Em dashes dropped 86%; the ones left came almost entirely from GPT-5 mini and Grok 4.5. The other eight models used none.

Measurement check. Two LLM labelers (agreement 89%) and the human rater checked a sample of matches. Precision ranges from 100% (headers, tables, horizontal rules) down to 9% for "offer closers", where the pattern mostly catches conditional advice like "if you want low stress, pick the cabin". Re-estimating with only the patterns that are at least 75% precise, or weighting every pattern by its precision, gives the same answer or a stronger one: 0.07 to 0.09 of the no-skill count.

Models didn't swap listed tells for unlisted ones. Semicolons, parentheticals, en dashes and connective adverbs all fell with the skill too.

### Judges

Four judges (Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash, Grok 4.7) compared replies blind, two per pair, never judging their own family's writing, with the order randomized. Each answered two questions: which reply would you rather receive, and which sounds more like stock AI.

| Comparison | Judgments | Find v1 less AI-like | Prefer v1 |
|---|---|---|---|
| v1 against no skill | 1,087 | 93% (92–95) | 49% (46–52) |
| v1 against placebo | 1,077 | 87% (85–89) | 45% (42–48) |
| v1 against original skill | 1,060 | 68% (64–72) | 46% (43–49) |

Percentages of decisive judgments, with 95% intervals.

Preference depended on the task. Against no skill, judges preferred v1 for genre traps (61%), status updates (59%) and emails (57%), and the no-skill reply for summaries (30%), explicit format requests (41%) and how-tos (42%). Their reasons were consistent: the no-skill reply covered more, or laid out owners, steps and action items in a list. Many added that it read more like a chatbot. Shorter replies lost slightly more often, but at equal length judges still split evenly.

### Human review

The skill's author rated 40 blind pairs (25 against no skill, 15 against the placebo), plus 4 repeats with sides swapped, and checked 32 flagged phrases.

- Stock AI: he found the v1 reply less like stock AI in 12 of 13 decisive pairs against no skill (92%, interval 67–99%) and in 6 of 8 against the placebo. Hypothesis 6 passes.
- Preference: 12 pairs for v1, 11 for the other reply, 17 ties. Against no skill, 8 to 7. Hypothesis 2 (over 60%) fails.
- Reliability: he reported fatigue a few pairs in, ties that meant "both bad" as often as "both fine", and prompts that felt unreal. Ties rose from 4 of the first 15 pairs to 16 of the last 29, and his preference matched itself on 2 of 4 repeated pairs. His stock-AI calls matched on all 4.
- Agreement with the judges: on pairs where both picked a side, the judges agreed with his stock-AI call 92% of the time and with his preference 53% of the time. Stock-AI-ness is something people and models recognize the same way. Preference isn't reliably measured here by either.

### Fidelity and format

Graders from other families checked 1,280 replies against the facts the user supplied and any format they asked for (15% were graded twice).

| Condition | Required facts missing | Stated wrongly | Invented details per reply | Format requests followed |
|---|---|---|---|---|
| No skill | 8.3% | 0.5% | 0.82 | 100% |
| v1 | 10.1% | 1.1% | 0.72 | 98% |
| Placebo | 8.4% | 0.6% | 0.84 | 98% |
| Original skill | 8.2% | 0.5% | 0.78 | 99% |

v1 missed 1.8 more points of required facts than no skill, just inside the 2-point limit, and invented fewer details. It followed explicit format requests 98% of the time. Hypotheses 3 and 4 pass.

### Side effects

- Length: replies were a third shorter (146 words against 215).
- The user's own words: when a user wrote a word from the skill's list, v1 replies reused it 17% of the time against 39% without the skill. Hypothesis 7 fails. Most of the gap came from one prompt about "the landscape" and what to "leverage", where rewording was harmless; ordinary words from the user's message were reused at 90% of the no-skill rate.
- House style: a classifier could still guess the model family from v1 replies 63% of the time, against 70% without the skill (chance is 20%). The skill strips surface tells, not every trace of a model's habits. Hypothesis 8 passes.

### Which sections matter

Removing one section at a time (12 prompts, 10 models):

| Removed | Tells against the full skill | What came back |
|---|---|---|
| Defaults | 2.02 (1.53–2.85) | Bold through prose (0 to 47), bold headers (3 to 24), em dashes |
| Structure | 1.27 (0.92–1.56) | Bold labels, bold through prose, scare quotes |
| Punctuation and cadence | 1.07 (0.81–1.41) | Em dashes (25 to 45) |
| Phrases | 1.07 (0.80–1.43) | Filler adverbs, preambles, answer labels |
| Vocabulary | 0.95 (0.68–1.22) | A few listed words |
| Framing paragraphs | 0.87 (0.68–1.15) | Scare quotes |

The Defaults section does the most. The others mostly control their own tells, which a 12-prompt subset can't separate from noise overall.

### Over a conversation

In 8-turn conversations, v1 held steady: about 0.7 tells per reply in the first two turns and 0.6 in the last three, against 15 and 11 without the skill.

## Round 2: skill v2 on sealed test-2

10 models, 35 sealed prompts, 3 conditions (no skill, v1, v2) and 2 repeats: 2,100 single-turn replies, plus 320 multi-turn replies. Judges and graders scored repeat 1.

| Hypothesis | Result | Evidence |
|---|---|---|
| 1. v2 has at most half the tells of no skill, in every family | fail | MAI 0.59 (v1 was 0.51 on the same prompts); other families 0.02 to 0.17 |
| 2. Judges find v2 less AI-like than no skill in over 75% of decisive pairs, and over 60% in every family | pass | 94% overall; MAI lowest at 86% |
| 3. No regression from v1 | pass | Judged more AI-like than v1 in 46% of pairs; tells 0.86 of v1's |
| 4. Fidelity no worse than no skill plus 1 point, or than v1 | fail | Missing 16.4%, against 12.7% (no skill) and 13.4% (v1); invented 0.45 details per reply, against 0.76 and 0.55 |
| 5. Format requests followed at least 95% of the time | pass | 98% |

v2 needed hypotheses 1, 3, 4 and 5 to ship. It failed 1 and 4, so v1 stays.

Two exploratory checks put the failures in context:

- MAI misses the tells bar with either version on these prompts. Its replies carry few tells to begin with (2.0 per reply without the skill), so small absolute changes swing the ratio.
- 19 of the 22 extra facts v2 missed came from one advice prompt, where the "required facts" were the user's own life story. An advice reply doesn't need to repeat those. Without that prompt, v2 misses 11.6% of facts, v1 11.2% and no skill 9.9%. The 95% interval for v2 against v1 runs from 1.4 points better to 8.7 points worse.

Other results:

- Against v1, v2 cut Grok's tells from 2.4 to 1.6 per reply (ratio 0.68, interval 0.55–0.86), raised Gemini's from 0.2 to 0.3, and left the other families unchanged.
- Judges preferred v2 over no skill 53% of the time and over v1 49%.
- Over 8-turn conversations, v2 stayed between 0.4 and 1.6 tells per reply, against 4 to 40 without the skill.
- Users' own listed words were reused in 39% of v2 replies, 36% of v1 replies and 54% without the skill.

## What this means for the skill

v1 ships unchanged. It cuts surface tells in every family tested, and both models and a person find its replies less like stock AI. It isn't a quality upgrade: judges and the human rater preferred its replies about half the time.

It costs something on summaries, how-tos and format-heavy answers, where judges wanted complete, scannable lists. It also drops up to 2 points more of the facts users supply, and avoids listed words even when the user used them first. The two fixes tried in v2 didn't measurably help with any of this.

It helps most with emails, status updates, posts and other writing a person will send or publish, where judges preferred it and it invented fewer details.

Ideas for a next round, each needing new sealed prompts: a fix aimed at MAI-Code-1.1-Flash and Grok 4.5, which changed least; checking required facts by hand before grading; and a shorter human review with separate "both good" and "both bad" options.

## Limits

- One agent harness (GitHub Copilot). GitHub Models, the only raw API available, was retired in July 2026. The harness holds back some chat-app habits such as emoji, and replies were written in batches of 11 to 14, which shortens them.
- Most measures come from models: the tell counter, the judges and the graders. The judges agree with a human on stock-AI-ness but not on preference.
- One human rater, the skill's author, who reviewed 44 pairs in one sitting and reported fatigue. A shorter review with separate "both good" and "both bad" options would give cleaner data.
- Test-1 informed the v2 revision, so only round 2 confirms it.
- Prompts mix real WildChat messages (some messy or stilted) with drafted ones. The rater found several unrealistic.
- House styles shift with every release. These are October 2026 models.
