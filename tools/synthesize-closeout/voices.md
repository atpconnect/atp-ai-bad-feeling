# Voice Brief

A second pass, run after the deck's content already exists and has been validated. It rewrites the words in a character's voice and changes nothing else.

The point is a live toggle during the closeout: same findings, same numbers, same slide, different narrator. It is a joke that only works if the substance survives it, so the substance is not negotiable.

## Your input

A JSON object exactly matching the schema in [`framework.md`](framework.md), already validated. Every `lede`, `t`, `d` and `takeaway`, plus `closing_line`, is the default version.

## Your task

Return **the same JSON object, with the same structure, and nothing else.** No prose, no fences, no commentary.

Rewrite only these string fields: `lede`, every `t`, every `d`, every `takeaway`, and `closing_line`. Rewrite them in the voice described below.

Rules, all enforced:

- **Keep every `id` exactly as it is.** Do not reorder stations, do not add or remove stations, do not change how many points a station has.
- **Keep every number, name, company, and quantity exactly as it is.** $310,000 stays $310,000. Ninety percent stays ninety percent. If the default version says a hundred and ninety thousand duplicate customers, so does yours. This is the whole reason the joke is allowed to exist.
- **Do not invent findings.** You are re-voicing sentences, not writing new ones. If you cannot say something in this voice, say it plainly rather than making something up.
- **Keep it roughly the same length.** These are slides.
- No em dashes.
- **The voice must be unmistakable.** If a reader could not name the character from a single slide, you have not done the job, and a barely-adjusted default sentence is the most common way to fail this. Every `lede`, `t`, `d` and `takeaway` should read as that character, not just a few of them. The calibration section below shows the intended intensity, including what falling short of it looks like.
- **Readability is the constraint on all of this.** A sentence the room has to parse twice has failed, however good the impression is. When the voice and the clarity of a finding pull against each other, the finding wins.

## The voice

__VOICE_DIRECTION__
