# Round 2: skill v2 on sealed test-2

Replies scored: 2420 (multiturn2 320, test2 2100). Intervals are 95%.

## Pre-registered hypotheses

| Hypothesis | Result | Evidence |
|---|---|---|
| 1. v2 has at most half the tells of no skill, in every family | fail | Claude 0.02; GPT 0.13; Gemini 0.02; Grok 0.17; MAI 0.59 |
| 2. Judges find v2 less AI-like than no skill in over 75% of decisive pairs, and over 60% in every family | pass | overall 94% (92–96); Claude 98%; GPT 91%; Gemini 100%; Grok 91%; MAI 86% |
| 3. No regression from v1: judges find v2 more AI-like in at most 55% of decisive pairs, and tells at most 1.15 times v1's | pass | v2 judged more AI-like 46% (41–51); tells v2/v1 0.86 (0.75–1.00) |
| 4. Fidelity: v2 misses no more than 1 point above no skill and no more than v1, and invents no more than no skill | fail | missing 16.4% vs no skill 12.7% and v1 13.4%; invented per reply 0.45 vs 0.76 |
| 5. v2 follows explicit format requests at least 95% of the time | pass | 98% (90–100) |

Shipping rule (v2 ships if 1, 3, 4 and 5 pass): **keep v1**.

## Tells, ratio against no skill (below 1 means fewer)

| Family | v2 / no skill | v1 / no skill | v2 / v1 |
|---|---|---|---|
| Claude | 0.02 (0.01–0.04) | 0.02 (0.01–0.04) | 0.94 (0.56–1.50) |
| GPT | 0.13 (0.10–0.17) | 0.14 (0.10–0.18) | 0.98 (0.84–1.16) |
| Gemini | 0.02 (0.01–0.03) | 0.01 (0.01–0.02) | 1.50 (1.03–2.69) |
| Grok | 0.17 (0.12–0.22) | 0.25 (0.17–0.31) | 0.68 (0.55–0.86) |
| MAI | 0.59 (0.42–0.77) | 0.51 (0.35–0.72) | 1.15 (0.79–1.72) |
| All | 0.09 (0.07–0.11) | 0.10 (0.08–0.13) | 0.86 (0.75–1.00) |

## Judges: v2 vs no skill

Judgments: 700. Prefers v2 53% (49–56). Finds v2 less AI-like 94% (92–96).

| Family | Finds v2 less AI-like | Prefers v2 |
|---|---|---|
| Claude | 98% (95–100) | 49% (41–57) |
| GPT | 91% (85–94) | 52% (45–58) |
| Gemini | 100% (97–100) | 64% (55–71) |
| Grok | 91% (85–95) | 43% (35–51) |
| MAI | 86% (74–93) | 60% (48–71) |

Preference by category: explain 38%; howto 42%; summary 47%; email 48%; genre_trap 51%; tech 51%; explicit_format 52%; user_words 53%; status_update 58%; marketing 61%; feedback 62%; factual 65%; advice 70%

## Judges: v2 vs v1

Judgments: 700. Prefers v2 49% (46–53). Finds v2 less AI-like 54% (49–59).

| Family | Finds v2 less AI-like | Prefers v2 |
|---|---|---|
| Claude | 42% (30–54) | 44% (36–53) |
| GPT | 66% (56–74) | 48% (41–55) |
| Gemini | 39% (28–51) | 56% (47–64) |
| Grok | 48% (37–59) | 48% (39–56) |
| MAI | 76% (62–86) | 55% (43–67) |

Preference by category: marketing 33%; factual 42%; status_update 42%; howto 45%; genre_trap 48%; email 49%; explicit_format 49%; user_words 50%; summary 53%; feedback 54%; explain 54%; advice 56%; tech 59%

## Fidelity

| Condition | Replies | Facts | Missing | Wrong | Invented per reply |
|---|---|---|---|---|---|
| No skill | 150 | 730 | 12.7% | 1.5% | 0.76 |
| Skill v1 | 150 | 730 | 13.4% | 2.1% | 0.55 |
| Skill v2 | 150 | 730 | 16.4% | 1.2% | 0.45 |

## Format requests

| Condition | Followed |
|---|---|
| No skill | 96% (87–99) |
| Skill v1 | 98% (90–100) |
| Skill v2 | 98% (90–100) |

## Length and the user's own words

| Condition | Words per reply | Reuses a listed word the user wrote |
|---|---|---|
| No skill | 223 | 54% |
| Skill v1 | 154 | 36% |
| Skill v2 | 152 | 39% |

## Multi-turn (mean tells per reply by turn)

| Turn | No skill | Skill v2 |
|---|---|---|
| 1 | 39.65 | 1.55 |
| 2 | 34.70 | 0.95 |
| 3 | 16.40 | 0.55 |
| 4 | 4.30 | 0.75 |
| 5 | 24.15 | 0.40 |
| 6 | 18.00 | 0.45 |
| 7 | 21.70 | 0.50 |
| 8 | 17.60 | 0.70 |
