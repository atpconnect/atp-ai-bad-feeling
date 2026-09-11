# Swamp Planet

**Theme:** Technical debt and data quality issues

The ship sank because nobody had dealt with what was underneath it.

Before the event: this station's question list, with pre-filled likely answers, goes in `questions.md`. It doubles as the fallback if no transcript is captured.
After the event: the exported transcript goes in `transcript.md` (or `.txt`/`.docx`), used by [`tools/synthesize-closeout/`](../../tools/synthesize-closeout/) to build the closeout draft.
