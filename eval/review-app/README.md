# Review app

A small local app for the blind human review. It shows two replies to the same message at a time, records which one you'd rather receive and which sounds more like stock AI, and saves every answer as you go.

Run it from the `eval` folder:

```sh
./scripts/review.sh
```

Then open http://127.0.0.1:8765. Answers save to `human/responses.json`. Python 3 standard library only, no install step.

Keys: 1/2/3 for preference, Q/W/E for stock-AI-ness, select text and press T to tag a tell, F to flag a problem, N for a note, arrow keys to move, ? for the full list.
