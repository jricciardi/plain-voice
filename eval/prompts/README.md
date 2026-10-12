# Prompt sets

- `dev.jsonl`: used to tune the skill.
- `test1.jsonl` and `multiturn_test1.jsonl`: scored once, for skill v1.
- `test2.jsonl` and `multiturn_test2.jsonl`: sealed until the revised skill is scored once.
- `SHA256SUMS`: hashes recorded before any replies were generated.

Each line has an `id`, a `source`, a `category`, the message `text`, and where relevant `required_facts` (facts a faithful reply must keep), `format_request` (a format the user explicitly asked for) and `listed_words` (skill-listed words the user used first).

## Sources and licenses

- `source: "wildchat"`: real first messages from [WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) (Zhao et al., 2024, "WildChat: 1M ChatGPT Interaction Logs in the Wild"), released by the Allen Institute for AI under the [Open Data Commons Attribution License (ODC-BY) 1.0](https://opendatacommons.org/licenses/by/1-0/). These records keep that license and aren't covered by this repository's license. They were filtered to English, non-toxic, non-redacted first turns without code, roleplay or personal details, then hand-selected.
- `source: "drafted-*"`: written for this test by GPT-6.1 Sol (summaries), Gemini 3.8 Flash (status updates), Grok 4.7 (genre traps and messages that use listed words) and Claude Opus 5.5 (explicit format requests), using fictional names and companies. Multi-turn scripts were written by GPT-5.6 Sol.
- `source: "first-test"`: the eight prompts from the first, smaller test.
