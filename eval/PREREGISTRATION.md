# Pre-registration: plain-voice stress test, round 1

Written 2026-10-12, before any test-1 replies were generated. Prompt-file hashes are in [prompts/SHA256SUMS](prompts/SHA256SUMS), and the skill version under test is `plain-voice/SKILL.md` at the commit that adds this file.

## What's being tested

Whether the plain-voice skill (v1) makes everyday replies read less like stock AI across model families, without making them less useful, and which of its sections do the work.

## Hypotheses and thresholds

Primary (confirmatory, on test-1):

1. Tells: replies written with the skill (C) have at most half as many counted tells per reply as replies written with a one-line placebo skill (D), in every model family (Claude, GPT, Gemini, Grok, MAI).
2. Human preference: the human rater prefers the with-skill reply in more than 60% of decisive (non-tie) pairs against the no-skill reply (A).
3. Fidelity: replies written with the skill don't miss more required facts than no-skill replies (difference under 2 percentage points), and don't invent more.
4. Format compliance: when a message explicitly asks for a format, replies written with the skill follow it at least 95% of the time.

Secondary:

5. C has fewer tells than A and than the original Claude-only skill (E), overall and per family.
6. The rater judges C less like stock AI than A in more than 60% of decisive pairs.
7. C reuses words the user wrote at least as often as A (within 10 points). The skill says the user's own words are fine.
8. A classifier trained to guess a reply's model family is less accurate on C replies than on A replies.

Exploratory: which sections matter (ablations F1 to F6), whether the effect fades over an 8-turn conversation, whether models swap listed tells for unlisted substitutes (en dashes, semicolons, connective adverbs), and how length and contraction use change.

## Design

- Models (10): claude-opus-5.5, claude-haiku-5.5, gpt-6.1-sol, gpt-5.5, gpt-5-mini, gemini-3.8-flash, gemini-3.7-flash, grok-4.7, grok-4.5, mai-code-1.1-flash. All run through GitHub Copilot's agent harness.
- Conditions: A no skill; C skill v1; D placebo (the same skill name and description, with the body replaced by "Write plainly and naturally."); E the original Claude-only skill; F1 to F6 the skill with one section removed (defaults, punctuation and cadence, phrases, vocabulary, structure, framing).
- Skill delivery: the skill text is placed in the model's instructions as an installed skill, so loading is guaranteed.
- Prompts: test-1 has 53 single-turn messages and 4 eight-turn conversations. 26 are real first messages from the WildChat-1M dataset; 27 were drafted by four different model families (summaries of pasted documents, status updates from notes, genre traps, messages that use listed words, and explicit format requests), so no single family wrote the test. The dev set (28) is for tuning. Test-2 (35 messages and 2 conversations) stays sealed until the revised skill is scored once.
- Repeats: 3 per prompt, model and condition. Each model and repeat gets its own random prompt order, split into 4 batches; all four main conditions share that batching so replies can be paired.
- Ablations: a fixed 12-prompt subset (one per category), 1 repeat, all 10 models, with the full skill rerun on the same batch for comparison.
- Multi-turn: the model reads each user turn from a file only after writing its reply to the previous one.

## Measures

- Tell counts from suite v2.1 (`scripts/tells.py`; see the amendments below): 30 patterns grouped by the skill's sections (17 phrase, 8 structure, 4 punctuation, 1 vocabulary list). Formatting the user asked for and words the user used first aren't counted. Precision is measured by labeling a random sample of matches (two LLM labelers from different families, plus a human subset).
- Watch list, not scored: spaced en dashes, spaced hyphens, semicolons, parentheticals, connective adverbs, hedges, hashtags, "~" for approximately.
- Length, sentence length and contractions per 100 words.
- Blind pairwise LLM judges: two judges per pair, never from the writer's family, with sides randomized. They answer the same two questions as the human: which reply they'd rather receive, and which sounds more like stock AI.
- Fidelity graders for prompts with required facts: missing facts and invented facts.
- Format compliance: pattern check plus grader.
- Family identifiability: TF-IDF and logistic regression, cross-validated with prompts grouped so no prompt appears in both training and test folds, balanced accuracy per condition.

## Human review

One rater (the skill's author) reviews about 40 blind pairs from test-1 repeat 1 (C against A, and C against D), stratified by model family and category and limited to replies under 450 words. Four pairs repeat with sides swapped to measure self-consistency. The rater also checks about 32 pattern matches for precision. LLM judges are calibrated against the rater's answers.

## Analysis

- Primary statistic: ratio of mean tells per reply between conditions, per family and overall, with 95% cluster-bootstrap intervals (resampling prompts, 2,000 draws).
- Secondary: a Poisson model with model and prompt effects and prompt-clustered standard errors.
- Preference rates with Wilson intervals, judge-to-human agreement (Cohen's kappa), and all results reported, including nulls and losses.

## Changes from the stress-test plan, and why

- One surface instead of three. GitHub Models, the only raw API available, was retired on July 30, 2026, and consumer chat apps can't be automated here. All replies come from one agent harness, which holds back some chat-app formatting; comparisons between conditions are still like for like.
- 53 prompts with 3 repeats instead of 40 with 5. Variation between prompts is larger than between repeats, so more prompts buys more than more repeats.
- One human rater instead of three, with LLM judges calibrated against that rater.
- No "installed normally" condition. In an agent harness the decision to load a skill isn't representative of chat use.

## Iteration protocol

After the human review, the skill is revised using the dev set, the human feedback and test-1 results. Because test-1 informs the revision, it can't confirm it. The revised skill is scored once on sealed test-2 against no skill and v1.

## Amendments before the main run (2026-10-12)

A 12-job pilot checked the prompt template, output parsing and multi-turn mechanics. It produced skill-condition replies only (the one no-skill pilot batch didn't finish), so no comparison between conditions was visible. Based on it, before any main-run reply was generated:

- Tell suite v2.1. Table rows no longer count toward em dashes, shorthand or bold, because cells in a table the user asked for aren't prose. "~" for "approximately" moved to the unscored watch list, since the skill doesn't name it. "Takeaway:" was added to the answer labels as a reworded form of the skill's "Key takeaways:" example.
- Run order. Jobs now run with test-1 repeat 1 first and slow models first, so human review can start sooner. No job's content changed.
- The pilot's replies are kept, since they came from the same prompts as the main run.

## Changes during analysis (2026-10-12)

- Tell suite v2.2. Version 2.1 sometimes reported a match at the wrong place in the reply: it located matches by searching for the first occurrence of the matched text, even when the pattern had only looked at the start or end of the reply. Counting was never affected; rescoring all 8,040 single-turn replies with v2.2 gives identical counts. What was affected: the first round of LLM precision labels and the human phrase checks. Both were rebuilt with correct positions before the human review began, and the superseded files are kept in `judgments/superseded/` and `human/superseded/`.
- Generation recovered from two workflow interruptions. Every job validates its own output, so no reply was lost or duplicated.
- The review server checked answer IDs against the task list it read at startup. It was started before the phrase checks were rebuilt, so it rejected those 32 saves; the 44 pair answers saved normally. The app kept the rejected answers and included them in its exported copy. That export is the record: it matches the server on all 44 pairs and adds the 32 phrase checks. The server now re-reads the task list on every save.

## Human review: what happened

The rater reported fatigue a few pairs in, ties that meant "both bad" about as often as "both fine", and some prompts that felt unreal or advice he disagreed with. The data shows the same: ties rose from 4 of the first 15 pairs to 16 of the last 29, and preference matched itself on only 2 of 4 repeated pairs, while stock-AI calls matched on all 4. Two prompts he flagged as stilted were real WildChat messages. The preference results are reported as planned but weighted lightly.

# Round 2: skill v2 on sealed test-2

Written 2026-10-12, before any test-2 reply was generated. Test-2 was sealed until now; its hashes are in `prompts/SHA256SUMS`.

## What changed in v2 and why

v2 (`conditions/H-skill-v2.md`) is v1 with two edits, chosen on the dev set and on test-1 (see [TUNING.md](TUNING.md)):

1. "Lists only when the content is a list, and then use one: steps, options, action items, dates." Judges preferred no-skill replies on summaries, how-tos and format requests, mostly for scannability.
2. "...but never a fact, name, date or step the user gave or asked for." v1 missed slightly more required facts than no skill.

Two other candidate edits (no offer as the closing step; use the user's word instead of a synonym) had no measurable effect and were dropped. The bold-label rule stays: the rater's phrase checks marked three bolded list items as not tells, but the judges, who matched the rater's stock-AI calls 92% of the time when both picked a side, often cite bold as chatbot style.

## Design

- Conditions: A no skill, C skill v1, H skill v2. Multi-turn: A and H.
- Models: the same 10. Prompts: test-2's 35 messages and 2 eight-turn conversations. Two repeats, each with its own prompt order in 3 batches shared across conditions.
- Measures: tell suite v2.2; blind pairwise judges (two per pair, never from the writer's family) on repeat 1 for v2 against no skill and against v1; fidelity and format graders on repeat 1 for all three conditions.
- No new human review. The rater's stock-AI judgments validated the judges for that question; preference proved unreliable for both the rater and the judges, so it's reported but not used for decisions.

## Hypotheses (confirmatory) and the shipping rule

1. Tells: v2 has at most half the tells of no skill in every family.
2. Stock-AI judgments: judges find the v2 reply less like stock AI than the no-skill reply in more than 75% of decisive pairs overall, and more than 60% in every family.
3. No regression from v1: judges find the v2 reply more AI-like than the v1 reply in at most 55% of decisive pairs, and v2's tells are at most 1.15 times v1's overall.
4. Fidelity: v2's missing-fact rate is no more than 1 point above no skill's and no higher than v1's, and v2 doesn't invent more details per reply than no skill.
5. Format: v2 follows explicit format requests at least 95% of the time.

v2 ships if hypotheses 1, 3, 4 and 5 hold. Otherwise v1 stays. Preference, length, reuse of the user's words and the multi-turn trend are reported as exploratory.

# Round 3: people judge reader fatigue

Written 2026-10-14, while the chat-lines dev test was generating and before any of its replies or any human rating had been seen. Round 1 showed that model judges agree with a person on which reply sounds more like stock AI (83 to 94% of decisive pairs) and don't agree on which reply is better to read (40 to 60%). Reader fatigue is the second kind of question, so round 3 asks people. Model judges keep the stock-AI question.

## Part 1: chat lines, on the dev set

Candidate `conditions/I-skill-v1-chat.md` is v1 plus two lines: say only what's new in a follow-up, and skip agreement or praise at the start of one (fix your own mistakes, and say so when the user is mistaken). It runs against no skill and v1 on one model per family (Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash, Grok 4.7, MAI-Code-1.1-Flash) over the five six-turn conversations in `prompts/dev_multiturn_r3.jsonl`, one repeat, 125 follow-ups per condition. This is tuning: it decides what goes into the candidate for the final test, and the final test decides what ships. Decision rules:

- The agreement line stays if, against v1, follow-ups that open with agreement or praise fall by at least half and by at least 3, the candidate doesn't give way more often than v1 when the user is wrong (dmt-05, turn 2), and its counted tells are at most 1.15 times v1's. If v1 already has 2 or fewer such openers, the line is dropped as unneeded.
- The repetition line stays if the share of five-word sequences repeated from earlier replies falls by at least a fifth against v1, and median follow-up length doesn't rise by more than 10%.
- Openers are matched by pattern (`scripts/analyze_chat_lines.py`), and every probe-turn reply is read by hand before deciding.

Generation change for round 3: job instructions tell agents to use only file reads and writes for their own files. In round 1, some agents followed an always-on todo rule in the harness and ended replies with lines like "Logged 4 todos." (under 1% of replies, in every condition).

## Part 2: the human reading test, shared set

Raters: up to six friends and coworkers of the author, in three pairs, plus the author. The primary analysis leaves the author out; his ratings are reported separately.

Material: public test-1 and test-2 replies (repeat 1) from Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash, Grok 4.7 and MAI-Code-1.1-Flash, without the skill (A) and with v1 (C). Prompts under 120 words, replies under 400, leaving out the two prompts the round 1 rater flagged as stilted and any reply with a leaked agent line. Each rater does four sessions; each session has one model and two batches of four replies, one per condition, in alternating order. Both raters in a pair read the same prompts in the same positions with the conditions swapped. Kits are built by `scripts/build_rater_kits.py` with seed `round3-shared-v1`.

For each reply, raters tap any sentence that bugs them, rate how tiring it was to read (1 to 5) and whether it would do the job (yes, mostly, no). After each batch they rate how worn out it left them (1 to 5), and at the end of a session they pick the batch they'd rather keep getting, with "both fine" and "both bad" as separate choices.

Hypotheses, tested on raters other than the author:

1. Replies with the skill are less tiring. For each prompt and model read both ways within a pair, take the skill reply's rating minus the no-skill reply's. Passes if the upper end of the 95% bootstrap interval of the mean is below 0.
2. Replies with the skill do the job as well. Scoring yes 2, mostly 1 and no 0, the same difference must have a 95% interval whose lower end is above -0.25.
3. Batches with the skill are less wearing. Within each session, the skill batch's rating minus the no-skill batch's; passes if the upper end of the 95% bootstrap interval is below 0.

Exploratory: which batch raters would keep, flags per 100 words, how often readers flag each tell the skill lists, flagged sentences that contain no listed tell, and results by model family, by rater and for the author.

How the results get used:

- The README reports hypotheses 1 to 3 as they come out, passing or failing.
- The slim version keeps entries that readers flag, and becomes a candidate to cut entries that both models rarely produce and readers rarely flag. Flagged sentences with no listed tell are candidates to add.
- If hypothesis 2 fails, keeping replies useful becomes the first job of the next version, ahead of cutting words.

Results are analyzed once: when every kit is back, or three weeks after the kits go out, whichever comes first. Until then, returned files are only checked to be readable.
