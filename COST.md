# What plain-voice cost

Building and testing plain-voice took 7,964 model requests and about 736 million tokens. At GitHub Copilot's published rates in October 2026, where one AI credit costs $0.01, that comes to $689. Writing the skill, its README and a test plan took about $35, the stress test about $640, and final edits and publishing about $14.

You don't need to spend that again. Installing plain-voice is free, and the test results are public in [eval/RESULTS.md](eval/RESULTS.md). Using it costs little too. The file adds about 1,300 tokens to a conversation, and in chat-style use the shorter replies it produces more than cover that on 9 of the 10 models tested, though the saving per reply is a fraction of a cent.

## Where the money went

| Work | Cost |
|---|---:|
| Researching tells, sampling 13 models, drafting the skill and checking it on 5 models | $32.40 |
| README methodology, test plan and license | $2.48 |
| Preparing the stress test: prompts, WildChat selection, review app and a pilot run | $8.43 |
| Round 1: 8,400 replies from 10 models | $201.43 |
| Round 1: judging and grading | $120.98 |
| Tuning a revised version that didn't ship | $103.06 |
| Round 2: 2,420 replies on sealed prompts, with judging and grading | $123.67 |
| Running and analyzing the tests in the main conversation | $82.38 |
| README edits and publishing | $13.97 |
| Total | $688.80 |

Costs come from the app's usage log, priced at [GitHub's per-model rates](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). The work took about nine hours on October 12, 2026, including 34 minutes of blind human review, plus README edits and publishing the next morning. Later, answering two questions about cost and writing this page and [SIMILAR-SKILLS.md](SIMILAR-SKILLS.md), which meant reviewing 47 similar skills, added about $30.

## Why testing cost so much

The test produced 11,360 replies, 6,784 blind pairwise judgments and 3,299 fact and format grades, and nearly all of it ran through agents. The only plain API available, GitHub Models, was retired in July 2026. Even the smallest agent request was 30,000 to 61,000 input tokens, depending on the model, most of it the agent's own instructions and tool definitions. Requests averaged about 70,000.

Claude Opus 5.5, one of the priciest models, ran the main conversation, wrote test replies and was one of four judges and graders. It accounts for $453 of the total.

Caching kept the bill down: 88% of the 706 million input tokens were read from cache at a fraction of the normal price. Billed at full price, the same work would have cost about $2,000.

## What it costs to use

The skill file is about 1,300 tokens. An agent loads it once per conversation, and later requests read it from cache. With the skill, replies in the stress test averaged about 120 fewer tokens (197 against 317), and output tokens cost 12 to 100 times as much as cached input. On 9 of the 10 models tested, that saving covers the skill's cost within 30 replies, and within 5 on Claude Opus 5.5, both Gemini models and GPT-6.1 Sol.

| Model | Fewer output tokens per reply | Pays for itself after | Saved per 1,000 later replies |
|---|---:|---:|---:|
| Claude Opus 5.5 | 182 | 2 replies | $3.37 |
| Gemini 3.8 Flash | 288 | 1 reply | $0.98 |
| Gemini 3.7 Flash | 241 | 2 replies | $0.80 |
| GPT-6.1 Sol | 80 | 5 replies | $0.67 |
| GPT-5.5 | 41 | 11 replies | $0.57 |
| Grok 4.5 | 126 | 22 replies | $0.09 |
| Claude Haiku 5.5 | 77 | 7 replies | $0.03 |
| GPT-5 mini | 27 | 15 replies | $0.02 |
| MAI-Code-1.1-Flash | 29 | 29 replies | $0.01 |
| Grok 4.7 | 110 | Never | $0.00 |

Reply lengths come from test-1 (159 replies per model in each condition), counted with OpenAI's o200k tokenizer, so other tokenizers give somewhat different numbers. Prices are GitHub's published rates, including Gemini's promotional rate through December 2026. On Grok 4.7, the output saved per reply is worth about what rereading the skill from cache costs, so the first load is never paid back.

The table assumes each later reply reads the skill from cache once, as in a chat. In agent sessions a reply can take many requests, each rereading the skill, so the payback is slower, and on some models the skill can cost more than it saves. Caches also expire after a while without use, and a reload costs about as much as the first load, at most two-thirds of a cent. The table leaves out hidden reasoning tokens, which weren't measured. And shorter isn't always better: judges preferred the longer no-skill replies for summaries, how-tos and format requests, which covered more ([eval/RESULTS.md](eval/RESULTS.md)).

## If you build your own anyway

Check [SIMILAR-SKILLS.md](SIMILAR-SKILLS.md) first, since another skill may fit better. Otherwise:

- Start from this one. You can fork it and change the lists, as long as the license notice stays and no one trains a model on it.
- Test against a placebo as well as against no instructions. A placebo with this skill's name and description and a one-line body ("Write plainly and naturally.") cut counted tells by a third, so a test against no instructions alone would have overstated the effect.
- Generate test replies through a model API instead of an agent if you can.
- Size the test to the question. Round 2 compared two versions of the skill on 10 models for $124. Round 1, which also measured a placebo, the original skill and the skill with each section removed, cost $322.
- Cheaper judges may do. On a small sample, Grok 4.7 and GPT-6.1 Sol agreed with the human rater on which reply sounded more like stock AI as often as Claude Opus 5.5 did (93 to 94% of the 15 or 16 pairs where both picked a side), at half its price per token or less ([eval/results/TABLES.md](eval/results/TABLES.md)).
- Reuse the [eval](eval/) folder. It has the prompts, scripts, tell counter and review app.
