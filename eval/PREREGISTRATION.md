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
