# plain-voice stress test, round 1: tables

Generated from `results/summary.json`. Tell suite v2.2. Replies scored: 8400 (ablation 840, dev 560, multiturn 640, test1 6360).

Intervals are 95%: cluster bootstrap over prompts for ratios, Wilson for rates.

## Pre-registered hypotheses

| Hypothesis | Result | Evidence |
|---|---|---|
| H1. Skill has at most half the tells of the placebo, in every family | fail (MAI above 0.5) | Claude 0.06; GPT 0.20; Gemini 0.02; Grok 0.31; MAI 0.50 |
| H2. Human prefers the skill reply over no skill in more than 60% of decisive pairs | fail | 53% (30–75) |
| H3. Skill doesn't miss more required facts (under 2 points) or invent more | pass | missing 10.1% vs 8.3%; invented per reply 0.72 vs 0.82 |
| H4. Skill follows explicit format requests at least 95% of the time | pass | 98% (93–99) |
| H5. Fewer tells than no skill and than the original skill, per family (interval below 1) | partial | vs no skill: 5/5 families; vs original: 4/5 |
| H6. Human finds the skill reply less like stock AI in more than 60% of decisive pairs | pass | 92% (67–99) |
| H7. Skill reuses the user's own listed words about as often as no skill (within 10 points) | fail | 17% vs 39% |
| H8. Model family is harder to identify with the skill | pass | 0.63 vs 0.70 (chance 0.20) |

## Mean counted tells per reply (test-1)

| Family | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| Claude | 8.99 | 0.28 | 4.57 | 0.63 |
| GPT | 5.81 | 1.00 | 4.94 | 1.77 |
| Gemini | 15.68 | 0.22 | 10.18 | 0.54 |
| Grok | 9.03 | 1.87 | 6.00 | 2.49 |
| MAI | 3.42 | 1.50 | 2.99 | 1.50 |
| All | 8.82 | 0.93 | 5.93 | 1.41 |

## Ratio of tells, skill v1 against each comparison

Below 1 means fewer tells with the skill. The per-100-words column adjusts for reply length.

| Family | vs placebo | vs no skill | vs original skill | vs no skill, per 100 words |
|---|---:|---:|---:|---:|
| Claude | 0.06 (0.03–0.10) | 0.03 (0.02–0.05) | 0.45 (0.29–0.60) | 0.04 (0.02–0.07) |
| GPT | 0.20 (0.17–0.25) | 0.17 (0.14–0.21) | 0.57 (0.48–0.68) | 0.23 (0.18–0.28) |
| Gemini | 0.02 (0.01–0.04) | 0.01 (0.01–0.03) | 0.40 (0.25–0.54) | 0.04 (0.01–0.06) |
| Grok | 0.31 (0.25–0.38) | 0.21 (0.16–0.26) | 0.75 (0.61–0.90) | 0.29 (0.23–0.36) |
| MAI | 0.50 (0.40–0.61) | 0.44 (0.37–0.51) | 1.00 (0.84–1.19) | 0.49 (0.40–0.57) |
| All | 0.16 (0.13–0.18) | 0.10 (0.09–0.13) | 0.66 (0.59–0.72) | 0.16 (0.14–0.20) |

Poisson model with model and prompt effects (rate ratio against skill v1, prompt-clustered intervals): A-none 9.53 (7.82–11.61); D-placebo 6.41 (5.39–7.62); E-original 1.53 (1.38–1.69).

## By model (mean tells per reply)

| Model | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| claude-haiku-5.5 | 5.21 | 0.28 | 3.16 | 0.45 |
| claude-opus-5.5 | 12.78 | 0.28 | 5.98 | 0.81 |
| gemini-3.7-flash | 15.38 | 0.25 | 10.35 | 0.76 |
| gemini-3.8-flash | 15.97 | 0.19 | 10.02 | 0.33 |
| gpt-5-mini | 3.19 | 1.80 | 2.99 | 1.92 |
| gpt-5.5 | 6.69 | 1.04 | 5.55 | 2.40 |
| gpt-6.1-sol | 7.55 | 0.17 | 6.28 | 0.99 |
| grok-4.5 | 14.50 | 3.38 | 10.51 | 4.45 |
| grok-4.7 | 3.55 | 0.35 | 1.49 | 0.52 |
| mai-code-1.1-flash | 3.42 | 1.50 | 2.99 | 1.50 |

## Totals by tell (test-1, all repeats)

| Tell | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| bold_inline | 3753 | 203 | 2483 | 475 |
| bold_label | 2714 | 140 | 1971 | 278 |
| em_dash | 1613 | 232 | 1171 | 251 |
| md_header | 1014 | 30 | 560 | 34 |
| bold_header_line | 1004 | 68 | 716 | 153 |
| shorthand | 782 | 162 | 482 | 236 |
| horizontal_rule | 710 | 2 | 274 | 16 |
| filler_adverb | 402 | 59 | 327 | 90 |
| scare_quotes | 333 | 79 | 255 | 107 |
| contrast_formula | 313 | 138 | 260 | 171 |
| offer_closer | 227 | 149 | 179 | 137 |
| emoji | 181 | 0 | 44 | 17 |
| answer_label | 171 | 103 | 147 | 114 |
| option_menu | 151 | 2 | 84 | 10 |
| listed_vocab | 141 | 30 | 92 | 24 |
| signpost | 121 | 5 | 88 | 11 |
| draft_preamble | 74 | 3 | 65 | 9 |
| padding | 63 | 21 | 51 | 34 |
| real_intensifier | 50 | 14 | 55 | 30 |
| table | 50 | 1 | 27 | 8 |
| significance | 40 | 8 | 26 | 10 |
| recap | 30 | 6 | 18 | 7 |
| stock_opener | 26 | 4 | 11 | 5 |
| hope_closer | 26 | 5 | 19 | 7 |
| praise_opener | 14 | 5 | 3 | 2 |
| reframe | 13 | 1 | 10 | 4 |
| slogan | 11 | 1 | 14 | 6 |
| disclaimer | 2 | 1 | 0 | 1 |
| fragment_reveal | 1 | 0 | 0 | 0 |
| unnamed_authority | 0 | 0 | 0 | 0 |

## By prompt category (mean tells per reply)

| Category | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| advice | 9.64 | 0.68 | 5.78 | 1.08 |
| email | 4.76 | 0.66 | 3.29 | 0.81 |
| explain | 9.18 | 0.59 | 5.32 | 0.74 |
| explicit_format | 10.76 | 1.84 | 8.25 | 2.70 |
| factual | 7.90 | 0.69 | 4.69 | 1.07 |
| feedback | 5.60 | 0.39 | 3.54 | 0.64 |
| genre_trap | 5.43 | 0.71 | 3.73 | 0.96 |
| howto | 15.41 | 1.51 | 10.51 | 2.87 |
| marketing | 3.43 | 0.12 | 2.15 | 0.08 |
| status_update | 7.98 | 0.68 | 6.23 | 1.33 |
| summary | 12.68 | 1.23 | 9.23 | 2.39 |
| tech | 10.34 | 1.38 | 6.36 | 1.53 |
| user_words | 9.70 | 0.76 | 5.87 | 1.06 |

## Watch list: unscored patterns (mean per reply)

Rises here with the skill would suggest substitution: dropping a listed tell for an unlisted one.

| Pattern | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| connective_adverb | 0.01 | 0.00 | 0.01 | 0.00 |
| double_hyphen | 0.00 | 0.00 | 0.00 | 0.00 |
| ellipsis | 0.05 | 0.01 | 0.03 | 0.01 |
| en_dash_spaced | 0.06 | 0.00 | 0.03 | 0.00 |
| hashtag | 0.01 | 0.00 | 0.00 | 0.00 |
| hedge | 0.91 | 0.62 | 0.87 | 0.62 |
| parenthetical | 2.27 | 0.69 | 1.52 | 0.87 |
| semicolon | 0.66 | 0.33 | 0.48 | 0.32 |
| spaced_hyphen_dash | 0.05 | 0.06 | 0.05 | 0.06 |
| tilde_approx | 0.17 | 0.05 | 0.12 | 0.04 |

## Tells by skill section (mean per reply)

| Section | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| phrases | 1.10 | 0.31 | 0.87 | 0.40 |
| punctuation | 1.61 | 0.31 | 1.13 | 0.38 |
| structure | 6.02 | 0.28 | 3.87 | 0.62 |
| vocabulary | 0.09 | 0.02 | 0.06 | 0.01 |

## Length and style

| Measure | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| words | 215.1 | 145.6 | 191.3 | 151.7 |
| mean_sentence_words | 13.3 | 13.5 | 13.0 | 13.3 |
| contractions_per_100w | 1.8 | 1.7 | 2.0 | 1.3 |
| bullet_lines | 4.1 | 1.4 | 3.3 | 1.5 |
| numbered_lines | 0.8 | 0.5 | 0.6 | 0.6 |

Words per reply by family:

| Family | No skill | Skill v1 | Placebo | Original skill |
|---|---:|---:|---:|---:|
| Claude | 253 | 178 | 231 | 181 |
| GPT | 164 | 137 | 159 | 142 |
| Gemini | 267 | 119 | 214 | 126 |
| Grok | 223 | 149 | 189 | 157 |
| MAI | 172 | 153 | 166 | 161 |

## Explicit format requests (pattern check)

| Condition | Followed |
|---|---:|
| No skill | 78% (72–83) |
| Skill v1 | 84% (78–88) |
| Placebo | 79% (73–84) |
| Original skill | 81% (76–86) |

## User's own listed words reused

| Condition | Replies reusing a listed word the user wrote |
|---|---:|
| No skill | 39% |
| Skill v1 | 17% |
| Placebo | 33% |
| Original skill | 24% |

## Ablations: removing one section at a time (12-prompt subset, 1 repeat)

Ratio above 1 means more tells without that section.

| Variant | Tells vs full skill | Words (variant / full) | Contractions per 100 words |
|---|---:|---:|---:|
| F1-no-defaults | 2.02 (1.53–2.85) | 178 / 164 | 1.4 |
| F2-no-punctuation | 1.07 (0.81–1.41) | 148 / 164 | 2.0 |
| F3-no-phrases | 1.07 (0.80–1.43) | 152 / 164 | 2.0 |
| F4-no-vocabulary | 0.95 (0.68–1.22) | 149 / 164 | 1.9 |
| F5-no-structure | 1.27 (0.92–1.56) | 153 / 164 | 2.1 |
| F6-no-framing | 0.87 (0.68–1.15) | 147 / 164 | 2.1 |

## Multi-turn: mean tells per reply by turn

| Turn | No skill | Skill v1 |
|---|---:|---:|
| 1 | 17.45 | 0.92 |
| 2 | 13.12 | 0.57 |
| 3 | 8.55 | 0.28 |
| 4 | 7.10 | 0.45 |
| 5 | 8.22 | 0.35 |
| 6 | 9.90 | 0.55 |
| 7 | 8.25 | 0.48 |
| 8 | 14.48 | 0.62 |

Skill v1 trend: -0.022 tells per reply per turn.

## Family identifiability

Balanced accuracy of a classifier guessing the model family from reply text (5-fold, prompts grouped). Lower means less house style.

| Condition | Balanced accuracy |
|---|---:|
| No skill | 0.70 |
| Skill v1 | 0.63 |
| Placebo | 0.69 |
| Original skill | 0.63 |
| chance | 0.20 |

## LLM judges (blind pairwise, never from the writer's family)

| Comparison | Judge | Judgments | Prefers skill reply | Ties | Finds skill reply less AI-like |
|---|---:|---:|---:|---:|---:|
| Skill v1 vs no skill | claude-opus-5.5 | 328 | 37% (32–42) | 2% | 98% (95–99) |
| Skill v1 vs no skill | gemini-3.8-flash | 273 | 47% (42–53) | 0% | 84% (79–88) |
| Skill v1 vs no skill | gpt-6.1-sol | 232 | 60% (54–67) | 1% | 96% (93–98) |
| Skill v1 vs no skill | grok-4.7 | 254 | 57% (51–63) | 2% | 94% (90–96) |
| Skill v1 vs no skill | all judges | 1087 | 49% (46–52) | 1% | 93% (92–95) |
| Skill v1 vs placebo | claude-opus-5.5 | 259 | 33% (28–39) | 1% | 93% (88–95) |
| Skill v1 vs placebo | gemini-3.8-flash | 267 | 43% (37–49) | 2% | 76% (70–82) |
| Skill v1 vs placebo | gpt-6.1-sol | 240 | 56% (49–62) | 2% | 88% (83–92) |
| Skill v1 vs placebo | grok-4.7 | 311 | 48% (43–54) | 2% | 89% (85–92) |
| Skill v1 vs placebo | all judges | 1077 | 45% (42–48) | 2% | 87% (85–89) |
| Skill v1 vs original skill | claude-opus-5.5 | 246 | 42% (35–48) | 9% | 71% (63–78) |
| Skill v1 vs original skill | gemini-3.8-flash | 293 | 47% (41–52) | 2% | 58% (50–66) |
| Skill v1 vs original skill | gpt-6.1-sol | 254 | 52% (46–59) | 8% | 73% (65–79) |
| Skill v1 vs original skill | grok-4.7 | 267 | 42% (36–48) | 3% | 69% (62–76) |
| Skill v1 vs original skill | all judges | 1060 | 46% (43–49) | 6% | 68% (64–72) |

By writer family, C-skill-v1 vs A-none:

| Family | Prefers skill reply | Finds skill reply less AI-like |
|---|---:|---:|
| Claude | 57% (50–63) | 100% (97–100) |
| GPT | 48% (42–53) | 90% (86–93) |
| Gemini | 54% (48–61) | 100% (98–100) |
| Grok | 40% (34–47) | 90% (85–94) |
| MAI | 47% (38–56) | 80% (70–87) |

By writer family, C-skill-v1 vs D-placebo:

| Family | Prefers skill reply | Finds skill reply less AI-like |
|---|---:|---:|
| Claude | 44% (38–51) | 92% (88–95) |
| GPT | 40% (35–46) | 85% (80–89) |
| Gemini | 51% (45–58) | 100% (98–100) |
| Grok | 45% (38–52) | 81% (75–86) |
| MAI | 47% (38–56) | 61% (50–71) |

By writer family, C-skill-v1 vs E-original:

| Family | Prefers skill reply | Finds skill reply less AI-like |
|---|---:|---:|
| Claude | 46% (40–53) | 69% (60–77) |
| GPT | 43% (38–49) | 64% (57–71) |
| Gemini | 42% (35–49) | 84% (77–90) |
| Grok | 51% (44–58) | 55% (46–64) |
| MAI | 48% (39–58) | 65% (53–75) |

## Fidelity (graded replies with required facts)

| Condition | Replies | Facts checked | Missing | Wrong | Invented details per reply |
|---|---:|---:|---:|---:|---:|
| No skill | 272 | 1235 | 8.3% | 0.5% | 0.82 |
| Skill v1 | 275 | 1229 | 10.1% | 1.1% | 0.72 |
| Placebo | 276 | 1233 | 8.4% | 0.6% | 0.84 |
| Original skill | 278 | 1261 | 8.2% | 0.5% | 0.78 |

## Explicit format requests (graders)

| Condition | Followed fully | Partly or not |
|---|---:|---:|
| No skill | 100% (97–100) | 0 |
| Skill v1 | 98% (93–99) | 2 |
| Placebo | 98% (93–99) | 2 |
| Original skill | 99% (95–100) | 1 |

## Robustness: noisy patterns removed or down-weighted

High-precision tells (labeled precision at least 75%): bold_header_line, bold_label, draft_preamble, emoji, horizontal_rule, md_header, option_menu, padding, real_intensifier, recap, shorthand, significance, signpost, slogan, stock_opener, table.

| Family | High-precision only: vs placebo | vs no skill | Precision-weighted: vs placebo | vs no skill |
|---|---:|---:|---:|---:|
| Claude | 0.04 (0.01–0.09) | 0.02 (0.00–0.04) | 0.05 (0.02–0.08) | 0.02 (0.01–0.04) |
| GPT | 0.11 (0.08–0.16) | 0.10 (0.06–0.14) | 0.17 (0.14–0.21) | 0.15 (0.11–0.18) |
| Gemini | 0.01 (0.00–0.01) | 0.00 (0.00–0.01) | 0.01 (0.00–0.02) | 0.01 (0.00–0.02) |
| Grok | 0.41 (0.29–0.51) | 0.25 (0.17–0.33) | 0.31 (0.23–0.39) | 0.20 (0.15–0.26) |
| MAI | 0.61 (0.40–0.91) | 0.48 (0.33–0.63) | 0.46 (0.35–0.58) | 0.40 (0.32–0.47) |
| All | 0.10 (0.08–0.13) | 0.07 (0.05–0.09) | 0.13 (0.11–0.16) | 0.09 (0.07–0.11) |

## Pattern precision (LLM labelers)

Labeler agreement: 0.887.

| Tell | Precision | Labels |
|---|---:|---:|
| offer_closer | 9% (3–24) | 32 |
| praise_opener | 21% (10–40) | 28 |
| hope_closer | 29% (15–47) | 28 |
| scare_quotes | 34% (20–52) | 32 |
| listed_vocab | 41% (26–58) | 32 |
| contrast_formula | 47% (31–64) | 32 |
| answer_label | 50% (34–66) | 32 |
| disclaimer | 50% (22–78) | 8 |
| reframe | 57% (39–73) | 28 |
| bold_inline | 62% (45–77) | 32 |
| em_dash | 69% (51–82) | 32 |
| filler_adverb | 72% (55–84) | 32 |
| bold_header_line | 75% (58–87) | 32 |
| significance | 75% (57–87) | 28 |
| draft_preamble | 79% (60–90) | 28 |
| real_intensifier | 79% (60–90) | 28 |
| slogan | 86% (69–94) | 28 |
| emoji | 88% (72–95) | 32 |
| option_menu | 92% (75–98) | 32 |
| stock_opener | 93% (77–98) | 28 |
| bold_label | 94% (80–98) | 32 |
| md_header | 94% (80–98) | 32 |
| shorthand | 94% (80–98) | 32 |
| signpost | 94% (80–98) | 32 |
| fragment_reveal | 100% (34–100) | 2 |
| horizontal_rule | 100% (89–100) | 32 |
| padding | 100% (88–100) | 28 |
| recap | 100% (88–100) | 28 |
| table | 100% (84–100) | 28 |

## Human review

Pairs answered: 44. Phrase checks answered: 32.

| Comparison | Pairs | Prefers skill reply | Ties | Finds skill reply less AI-like |
|---|---:|---:|---:|---:|
| C-skill-v1 vs A-none | 25 | 53% (30–75) | 10 | 92% (67–99) |
| C-skill-v1 vs D-placebo | 15 | 50% (22–78) | 7 | 75% (41–93) |

Self-consistency on repeated pairs: preference 50%, AI-like 100%.

Judge agreement with the human:

| Judge | Pairs | Same preference | Same AI-like call |
|---|---:|---:|---:|
| claude-opus-5.5 | 32 | 25% | 50% |
| gemini-3.8-flash | 32 | 31% | 41% |
| gpt-6.1-sol | 28 | 36% | 57% |
| grok-4.7 | 32 | 38% | 47% |

Human-checked pattern precision overall: 67% (45–83).
