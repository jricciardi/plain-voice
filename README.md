# plain-voice
Over the past two years, I have gotten fed up with the ai 'voice'. The ai voice is present in, seemingly, 90% of all written content on the internet, which is a true crisis for the quality of the written word as the democratization of voices on the web is reduced to a handul of uncannily consistent AI model's voices. This is a bad thing. And I do believe those who train models should be held responsible for effectively nuking variety and diversity from the written word online. 

We now live in a written word environment where, despite the profile picture next to the byline, it seems like most things are actually just written by Claude. 

I made this skill because I am also sick of hearing that voice AT WORK, where I am required to use AI on a daily basis to improve operational systems. I do find LLMs to be practical and useful in the work place. But, god, they still all sound like themselves and I'm sick of hearing how they write.

So, this skill is designed to be a lightweight set of guidelines to keep my AI assistants' everyday replies from reading like stock AI. It covers the house-style tells of Claude, GPT, Gemini and Grok (I wish I didn't have to mention Grok, but here we are). In this skill, you'll find a remedy to the over-used em dashes, "It's not X, it's Y," "Great question," "Here is why:" lead-ins, bolded slogans in bullet lists, "If you want, I can…" closers, "That's worth sitting with", and rest. And "genuinely" — I loathe that I now loathe the word 'genuinely', Claude.

This skill is meant for routine replies and working docs. It doesn't imitate a particular voice, it just strips out the most annoying tells of the LLMs house-styles. It does very little to address the structural assumptions and judgements and ordering of ideas and flow.

This skill is not meant to be used to "fool" human readers if you attempt to use it as such. Trust me, people will still be able to tell. AI generated writing has many structural elements that will absolutely and crystal-clearly identify it as AI generated. If you are considering using this skill to that end: don't. Go write for yourself and learn the skill and craft of writing and make your communication to other people from you. You are what matters in good writing.

Instead, please use this skill for things like AI-generated private documentation, personal queries, interfacing with AI in the workplace, personal projects, etc.

For transparency's sake: The rest of this readme is written using this skill.

-Jay
## Install

With the GitHub CLI, which asks which agent to install it for:

```sh
gh skill install jricciardi/plain-voice plain-voice --scope user
```

Or copy the `plain-voice` folder into your agent's personal skills folder:

- Claude Code: `~/.claude/skills/`
- GitHub Copilot CLI: `~/.copilot/skills/`
- Other agents that support [Agent Skills](https://agentskills.io): see their docs for the skills folder.

The skill applies to routine replies on its own. In Claude Code you can also call it with `/plain-voice`.

## Stress test

The skill was stress-tested in October 2026 on 10 models from 5 families (Claude, GPT, Gemini, Grok and MAI), using 88 new prompts and 6 eight-turn conversations, many of them real messages from the WildChat dataset. Hypotheses and pass marks were written down before any replies were generated. Full results are in [eval/RESULTS.md](eval/RESULTS.md), and everything needed to rerun the test is in [eval/](eval/). A human grader (the author of this skill) was presented with pairs of AI generated replies and sorted them based on how much they sounded like stock AI responses.

- Replies written with the skill had a tenth as many counted tells as replies written without it, and a sixth as many as replies written with a one-line placebo ("Write plainly and naturally."). The result held on a second set of prompts.
- Judges from other model families found the skill's reply less like stock AI in 93% of pairs. The skill's author, rating blind, did in 12 of 13 pairs where he picked a side, and the judges agreed with his calls 92% of the time.
- Note: response type matters. The skill doesn't make replies better on average. Judges preferred its replies about half the time: more often for emails, status updates and posts, less often for summaries, how-tos and format requests, where they valued complete, easy-to-scan lists. (For example: This readme document has more AI tells, but that is deemed ok because readme documentation benefits from the extra structure that AI is good at generating.)
- Replies were a third shorter, followed explicit format requests 98% of the time and invented fewer details. They missed up to 2 points more of the facts the user supplied.
- The effect held over 8-turn conversations. MAI-Code-1.1-Flash changed least, and GPT-5 mini and Grok 4.5 kept some em dashes.
- A revised version with two more rules (use a real list for steps and action items; never drop a fact while shortening) didn't beat this current version on a second round of iterative improvements.

Limits: every reply came from one agent harness (the GitHub Copilot App), which already holds back some chat-app habits such as emoji. Most measures come from models, which agree with a person on what sounds like stock AI but not on which reply is better. The one human rater was the skill's author, who reported fatigue during rating. Rating dozens of AI generated responses is an awful and fatiguing process. House styles shift with each model release.

## How the list was built

The first version came from watching Claude's habits. Extending it to other model families drew on two kinds of evidence: published research, and a side-by-side test of 13 models. The stress test above then checked the result on new prompts.

### Published research

The research pass covered Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide, corpus studies of words that AI overuses, xAI's published Grok system prompts, and detector write-ups that name model-specific patterns. Everything used is listed under [Sources](#sources).

### Side-by-side test

Thirteen models answered the same eight prompts: six from OpenAI (GPT-5 mini, GPT-5.3-Codex, GPT-5.5, GPT-5.6 Sol, GPT-6 Luna and GPT-6.1 Sol), two from Google (Gemini 3.7 Flash and 3.8 Flash), three from xAI (Grok 4.5, 4.6 and 4.7), Microsoft's MAI-Code-1.1-Flash, and Anthropic's Claude Sonnet 5.5 as a baseline. That came to 104 replies and about 16,500 words, collected in October 2026.

The prompts cover the kinds of writing where tells tend to cluster: an explainer, personal advice, a team email, a LinkedIn post, feedback on someone's draft, a technical recommendation, a status update built from rough notes, and a short travel description.

Every model ran in the same agent harness (GitHub Copilot) with identical instructions: reply the way it would in an ordinary chat app, at its natural length and formatting, with no web access. The instructions didn't mention writing style or say what the replies were for, so the models had no reason to adjust. Each prompt got one reply per model.

<details>
<summary>Exact instructions and prompts</summary>

Instructions given to every model:

> For each message, write the reply you would send if a user sent you that message in an ordinary chat app: your natural length, formatting, tone, opening and closing. Write it as you normally would; don't adapt it for this task.

Prompts:

1. Why do planes leave white trails in the sky, and why do some disappear right away while others stick around for ages?
2. I've been at my job for 3 years. I'm good at it but bored. A startup offered me a bigger role with 20% less salary plus equity. I'm 34 and have a mortgage. What would you do?
3. Write a short email to my team: our weekly sync is moving from Monday 10am to Thursday 2pm starting next week, and the first Thursday session will run long because we'll use it for Q3 planning.
4. Write a LinkedIn post about what I learned in my first year as an engineering manager.
5. Can you give me feedback on the opening of my blog post? "Every team says they value documentation. Few actually write it. In this post I want to talk about why, and what we did about it on my team."
6. We're a 5-person startup building a B2B SaaS app. Monolith or microservices?
7. Turn my notes into a quick status update for my manager: migration 70% done, blocked on vendor API rate limits, asked vendor for an increase, eta friday. new hire starts monday. dashboard v2 shipped tuesday, 3 bugs reported, 2 fixed.
8. Write about 150 words describing Astoria, Oregon for a travel blog.

</details>

Scoring had two passes. A script counted 16 kinds of tells with pattern matching (em dashes, headers, bold text, contrast constructions such as "It's not X, it's Y", answer labels, offer closers, a candidate word list and others). It also pulled out every opener and closer and ranked the phrases each family used far more often than the rest. Then every reply was read in full to catch what pattern matching misses, such as reframing the user's question or "Come for X, stay for Y" taglines.

A pattern made the list if published research documents it or if it appeared in replies from at least two model families. One-model quirks were left out, such as GPT-5 mini signing off chat replies with "Cheers".

Most tells showed up across several families, so the skill keeps one list instead of a section per model. A few lean toward one family:

- GPT reframes the question ("I'd treat this as a risk decision"), labels answers ("Short answer:"), and writes in slash and arrow shorthand.
- Gemini puts headers on short answers, leads lists with "Here is why:", and offers "Option 1, 2, 3" when you asked for one draft.
- Grok uses em dashes, quips and scare quotes, and staccato slogans ("Default to the monolith. Earn the split.").
- Claude has its own vocabulary: load-bearing, quietly, the shape of, lean into.

## Limitations and Opportunities

### Testing

- Only one person rated replies: the skill's author, in a single sitting. He got tired partway through, and ties rose as the session went on. A tie also meant either "both bad" or "both fine". More raters who didn't write the skill, in shorter sessions with separate "both good" and "both bad" choices, would give cleaner data.
- The list came from 8 prompts. Thirteen models answered 8 everyday prompts once each, and published research filled in the rest. The stress test checked the list on 88 new prompts, but a tell that only appears in other kinds of writing, such as fiction, code comments or long reports, wouldn't have been found.
- Every reply came from one harness, the GitHub Copilot app. Chat apps like ChatGPT, Claude.ai and Gemini add their own system prompts and formatting, so results there could differ. Running the same prompts through each vendor's API and chat app would close that gap.
- The skill was always loaded. Every test placed its text directly in the model's instructions. In normal use an agent decides when to load a skill, and how reliably that happens wasn't measured.
- Models did most of the measuring. A script counted tells, and models judged and fact-checked replies. When both picked a side, the judges matched the human rater 92% of the time on which reply sounded more like stock AI, and only 53% of the time on which reply was better. The counting script also misfires on some patterns: only 9% of the phrases it flagged as offer closers were offers.
- The research left out a lot. It drew on Wikipedia, academic word-frequency studies, xAI's published prompts, AI-detection companies and one engineer's blog. Most of what writers, editors and Substack authors have published about the AI voice wasn't included, and The Economist's 2026 analysis of AI writing was read only through secondhand coverage. Those writers could add tells, and better judgment about which ones bother readers most.
- Prompts were English only, and replies averaged about 150 to 220 words. Other languages and long working documents, which the skill is meant to also cover, weren't tested.  
- Open-weight models weren't tested. Llama, Mistral, DeepSeek and Qwen have house styles of their own.
- The results are a snapshot of October 2026 models. House styles change with each release, and the [eval](eval/) folder can rerun the whole test on new ones.

### The skill

- It works on surface tells and leaves the structure, judgments and ordering of ideas alone. A classifier could still name the model family from 63% of replies written with the skill (chance is 20%). Rules about structure would need a different kind of test.
- It can cost completeness. Judges preferred the no-skill reply for summaries, how-tos and format-heavy answers, where they wanted complete lists that are easy to scan. Replies with the skill also missed up to 2 points more of the facts users supplied. Two rules aimed at this didn't help in testing, so it's still open.
- It avoids its own word list too eagerly. When a user wrote a listed word, like "landscape" or "leverage", replies with the skill reused it 36% of the time, against 54% without it, even though the skill says the user's words are fine. An extra sentence tried during tuning didn't change that.
- Some models follow it less. MAI-Code-1.1-Flash changed least, and GPT-5 mini and Grok 4.5 kept using em dashes. Model-specific notes, or a shorter version for smaller models, could be tested next.

## Sources

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Kobak et al., [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016)
- Juzek and Ward, [Why does ChatGPT "delve" so much?](https://arxiv.org/abs/2412.11385)
- Sun et al., [Idiosyncrasies in large language models](https://arxiv.org/abs/2502.12150)
- [xAI's published Grok system prompts](https://github.com/xai-org/grok-prompts)
- GPTZero, [10 AI patterns](https://gptzero.me/news/ai-patterns/)
- Sean Goedecke, [The OpenAI house style is exhausting](https://www.seangoedecke.com/chatgpt-house-style/)
- [EQ-Bench creative writing leaderboard](https://eqbench.com/creative_writing.html), which tracks a slop score per model

## Contributing

Spotted a tell that isn't listed? Open an issue with an example and the model that wrote it. Samples from chat apps, rather than agent tools, are especially useful.

## License

The license follows MIT terms with one exception: no AI training. You can use, copy, modify and share the skill, and load it into any AI agent or system prompt. You can't use it to train, fine-tune or distill a model, or include it in a training dataset. It also reserves text-and-data-mining rights under EU law.

Because of that exception, the skill is source-available rather than open source as the Open Source Initiative defines it. The full terms are in [LICENSE](LICENSE), and a copy ships inside the skill folder so it travels with every install.
