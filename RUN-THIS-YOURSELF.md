# Run This Yourself

This repo is the whole method for an event called "Your AI Program Has a Bad Feeling About This": five parallel rooms, nobody in more than one of them, and a closeout session built from all five in the ten minutes it took people to walk back to their seats.

Two things are worth taking. The **event format**, which is a way to get a room of senior people to say true things out loud. And the **discipline behind the closeout**, which is a small, boring set of rules that made an AI system reliable enough to stand behind in front of a hundred people, with no chance to review the output.

The second one is the point. The event is about why enterprise AI initiatives fail. It would be embarrassing to run it on an AI program that fails, so the program was built the way we keep telling people to build theirs, and this document is what that actually meant in practice.

---

## Part one: the principles

Each of these has a concrete implementation in this repo and, in most cases, a specific defect it caught. They are ordered by how much they save you.

### 1. Be deterministic wherever determinism is available

The model wrote the words on the station slides. Everything else was written by code: the running order, the branding, which stations are flagged as unreliable, the navigation, the QR codes, and the two screens explaining the method.

The reason is not tidiness. Anything a model produces has to be checked by a human, and on the night there is no time to check anything. So the useful move is not "review the output faster", it is **shrink the surface the model is allowed to decide**. A model that cannot choose the running order cannot get the running order wrong, and nobody has to check it.

Ask of your own system: what is it deciding that has exactly one correct answer? Move that into code. You will usually find more of it than you expect.

*Here: [`tools/build-deck/`](tools/build-deck/) owns structure; the model only supplies content.*

### 2. Never ask a model a question you can already answer

Which stations produced a usable recording is a fact sitting on a disk. An early version asked the model to report it back, and a model that relabelled a failed station as a real one silently removed the on-screen warning that existed to catch exactly that failure.

The fix was not a better prompt. The fix was to stop asking. The source is read from disk, injected into the renderer, and whatever the model says about it is discarded.

This is the cheapest reliability win available and almost everyone leaves it on the table, because asking is easier than plumbing.

### 3. Constrain the output until it can be validated

The model is asked for JSON against a fixed schema. Not for a deck, not for HTML, not for markdown. Unknown station id, a missing station, the wrong number of bullets: rejected outright, and the deck already on disk stands untouched.

You cannot check free text. You can check a schema. The narrower the thing you ask for, the more of the answer a machine can verify without you.

*Here: [`framework.md`](tools/synthesize-closeout/framework.md) is the brief; the schema is enforced in code before anything renders.*

### 4. Separate "wrong" from "untidy"

The first version rejected any field over its length cap. On a real run the model returned a sentence 26 characters too long and the entire synthesis was thrown away, two minutes before it was needed.

Structural problems mean the model misunderstood the task, so the rest of its output should not be trusted either: reject those. Cosmetic problems are cosmetic: trim them and report it. Conflating the two is how a system becomes brittle in exactly the moment you need it.

### 5. Design the degraded path first, and make it real

Before knowing whether any recording would fail, we knew what a failed recording would look like on screen. There are three rungs, each presentable on its own:

1. The primary model on the real transcripts.
2. A faster standby model on the same real transcripts.
3. A deck built days earlier from what each station planned to ask and what we expected to hear.

Rung three is the important one. It exists on disk before the event starts, so every later run can only improve on it, and no failure on the night can leave you with nothing. **A fallback invented under time pressure is not a fallback.**

It has two depths, and the difference is worth the afternoon. A question list gets that station a slide describing an agenda. An **expected transcript**, the same guess written out at the length a room actually talks, with the numbers and the disagreements in it, gets that station a slide with something on it worth saying out loud. Both carry the banner and neither is a recording. Write the expected transcripts for the stations whose capture you trust least, and then write the rest of them anyway.

### 6. Label provenance where the audience can see it

Any station running on a fallback says so, in a banner, on its own slide. Any deck written by the standby model says so on the method screen.

The failure to fear is not a wrong answer. It is a wrong answer that looks exactly like a right one. If your system degrades silently, it does not degrade, it lies.

A related trap we walked into: the pre-event preview originally told early visitors that each station's *recording had failed*, which was false, because the sessions had not happened yet. The same flag meant two different things depending on when the page was built, and only one of them was true. Check what your warnings claim in every state your system can be in, not just the one you were thinking about.

### 7. Write the evals before the night, and test the disasters

There are 192 automated checks across 34 rehearsals of the evening. They include: no transcript at all, prose instead of JSON, a crashed CLI, a transcript arriving late, both models failing at once, and a narrator quietly dropping the numbers.

The happy path is the least useful thing you can test, because it is the one you will notice anyway. Everything expensive lives in the paths you have never seen.

*Here: [`tests/`](tests/), the whole suite in about two minutes.*

### 8. Score the things you would otherwise argue about

Three checks replace judgement calls nobody would have time to make on the night:

| Question | How it is answered |
|---|---|
| Did a narrator keep every figure from the default version? | The numbers are diffed and anything missing is named. |
| Did a narrator change enough to be worth a button? | Under 60% of fields rewritten and it is flagged. |
| Are the jokes piling up? | Counted per screen, flagged above one. |

None of these is clever. Each one turns "does this feel right?" into a number, and a number can be checked at 7:50pm by someone who is also doing four other things.

### 9. Measure, do not estimate

The run of show budgeted about a minute for the synthesis. Rehearsal against full-length transcripts measured **69 to 167 seconds**, and the slowest run was on the *smallest* input, so it cannot be shortened by trimming the input.

Then the night itself went past the top of that range. The primary model never made its 180 second deadline and the standby carried the room; a later run of the primary against the same transcripts took **379 seconds**, on 166KB of real transcript rather than the 285KB the rehearsal had fed it. The slowest run on record is still the one on the smallest input.

That measurement moved the plan by several minutes and changed the run of show, and the number it produced was still too optimistic. It came from running the thing with a stopwatch, which nobody does, because estimating feels close enough right up until it isn't.

### 10. Rehearse the pipeline, not the parts

Every defect below was found by running the whole thing end to end. Not one was found by reading the code.

- **A bug that would only ever appear live.** The prompt was passed as a shell argument. Linux caps a single argument at 128KB, the rehearsal's full-length fixtures came to 285KB and the five real transcripts to 166KB, so it passed every small test and would have died on the night, in the room, in front of everyone.
- **Parallel model calls that ran in sequence**, producing correct output the whole time. Caught only because a test asserted on elapsed time rather than on the result.
- **QR codes that rendered as perfectly sized blank squares.** Right dimensions, right position, nothing inside. No assertion about the markup would have caught it, so the test now scans the code back with a barcode reader.
- **A narrator that changed 9% of the words and passed every check.** Correcting one failure produced its exact opposite: the first Elder voice inverted nearly every sentence into something you had to read twice, and the fix came back 91% identical to the plain text, validating perfectly and pointless on stage. Enforcer landed at 58% of fields rewritten. Worked examples fixed both, and a divergence score now flags it, because the answer to fear is never the obviously wrong one, it is the one that looks exactly right.

If your tests only assert on output, they will miss anything about time, size, or whether the thing is actually visible.

---

## Part two: running the event

The format is straightforward and the logistics are where it goes wrong. Both runbooks are in this repo: [`coordinator-checklist.md`](coordinator-checklist.md) for whoever is running it and [`station-pilot-instructions.md`](station-pilot-instructions.md) for the people leading each room.

**Split the room.** Five stations of roughly 25, each on a distinct way AI programs fail. Ours were third-party integration, data quality, use cases with their costs and scope creep, development, and compliance, legal, and security. Pick failure modes your audience has actually lived.

**Make each station a discussion, not a talk.** The station pilot puts roughly eight questions to their room and the room answers. The value is entirely in what attendees say, so the pilot's job is to keep it moving and make sure it lands on the recording.

**Record centrally, not per speaker.** One person hosts all five meetings from one account. No session depends on a presenter remembering to press a button correctly.

**Get the questions in advance.** They are the running order, and they are also the fallback if a recording fails. Ours were due two days out.

**Then the closing session is the whole point.** Nobody has heard more than one fifth of the evening. Reassembling and telling them what the other four rooms said is the thing they cannot get anywhere else, and it has to happen while they are still in the building.

### The things that will actually bite you

Learned the expensive way, mostly from a planning call and one rehearsal:

- **Turn off noise suppression** on every laptop. It is tuned to isolate one voice at a desk and will strip out the room discussion you came to capture. This is the single most important setting and it is off by default in nobody's software.
- **Ending a meeting is what generates the transcript.** Leaving it does not. Say this three times.
- **The pilot's own voice was never at risk.** The room's answers are. Have the pilot tell people to speak toward the laptop, repeatedly, and echo good answers back so they survive in a voice near the microphone.
- **A second recorder must be a genuinely different device.** A second app on the same laptop shares every failure mode of the first, and can fight it for the microphone.
- **Budget the gap honestly.** Transcripts take a few minutes to generate after each meeting ends, the endings are staggered, and the synthesis takes one to six minutes on top. Ours was about ten minutes end to end, and only because the standby answered when the primary did not.
- **Nobody past the fourth row can read a normal web page on a projector.** Build the presentation to enlarge itself, and check it from the back of the actual room before anyone arrives.

---

## Part three: using this in your own organization

Everything here is plain files and small scripts. There is no framework to adopt and nothing to install beyond a command line model tool.

```bash
git clone https://github.com/atpconnect/atp-ai-bad-feeling
cd atp-ai-bad-feeling
tests/rehearse.sh          # rehearse the whole evening against mock data, ~2 minutes
```

If that passes, the pipeline works on your machine and you can start replacing our event with yours.

### What to change

| Change | Where |
|---|---|
| The five stations, their ids and themes | `STATIONS` in [`build_deck.py`](tools/build-deck/build_deck.py), and the list in [`framework.md`](tools/synthesize-closeout/framework.md) |
| What the synthesis is asked for | [`framework.md`](tools/synthesize-closeout/framework.md) |
| Your question lists | `stations/<name>/questions.md`, one per station |
| What you expect each room to say | `stations/<name>/expected-transcript.md`, the deeper of the two fallbacks |
| The two method screens | `method_screens()` and `receipts_screen()` in `build_deck.py`. Replace ours with something true about how you ran yours. |
| Branding and the published URL | `--brand` in the template, and `FOLLOW_URL` |
| Fixtures the rehearsal runs against | [`tests/fixtures/`](tests/) |

Optional: `pandoc` for `.docx` transcripts, `qrencode` for the QR codes. Both degrade gracefully if missing.

### Using a different model or provider

The pipeline shells out to one command. `CLAUDE_BIN` points at it, and the only contract is that it accepts a prompt on **stdin**, accepts `-p` and `--model`, and writes the answer to **stdout**.

So any provider works behind a ten line shim. [`tests/stubs/claude`](tests/stubs/claude) is a working example of exactly that shim, written for the rehearsal harness:

```bash
CLAUDE_BIN=./my-provider-shim tools/synthesize-closeout/synthesize.sh
```

Keep the JSON schema and the validation regardless of provider. That is the part doing the work.

### Prompts to get started

These are plain text and portable. Paste them into whatever your organization has approved: Claude Code, Claude Cowork, GitHub Copilot, ChatGPT, Gemini or anything else. The distinction that matters is not the brand, it is whether the tool can read and run this repo itself, or whether you are pasting files into a chat window. Where it matters, both versions are given.

**1. Adapt the repo to your event** (for a tool that can read and edit the checkout)

> This repo runs a five-room workshop and builds the closeout session from the room transcripts. Read RUN-THIS-YOURSELF.md and coordinator-checklist.md first. Adapt it for us: our event is [WHAT IT IS] for [WHO IS COMING], and our five sessions are [LIST]. Update the station ids and themes everywhere they appear, rewrite tools/synthesize-closeout/framework.md for our themes, and replace the two method screens with placeholders I can fill in. Then run tests/rehearse.sh and fix anything that fails. Do not change the JSON schema or the validation.

**2. Draft the question lists**

> You are preparing one session of a workshop on [THEME] for [AUDIENCE, SENIORITY, INDUSTRY]. Write eight questions the session lead will put to a room of about 25 people. They must be answerable from direct experience, not opinion, and each one should invite a specific number, example or disagreement rather than a general view. No yes/no questions. Then, under each, write two or three sentences of the answer you would expect a room like this to give, clearly marked as a guess. Output as markdown.

The guessed answers are not padding. They are the fallback that stands in for that room if its recording fails, so they are worth writing properly. Go one step further for any station you would hate to lose:

> Here is the question list for one session of this workshop, with the answers we expect. Write what a room of about 25 senior [ROLES] would actually say over 45 minutes if a session lead put these questions to them in that order. Transcript shape, speaker labels only, no names. Specific numbers, real examples, and at least one place where the room disagrees with itself. Nobody has said any of this: it is our guess, and it will be labelled as our guess wherever it is used.

That file is a fallback like the question list, not a transcript, and the tooling treats it as one. Anything built from it says on screen that every number on it is yours and not the room's.

**3. Rewrite the synthesis brief**

> Read tools/synthesize-closeout/framework.md. It tells a model how to turn five session transcripts into closeout content, and it returns JSON against a fixed schema. Keep the schema, the length targets and the ground rules exactly as they are. Rewrite the event context and the five session descriptions for our event: [DESCRIBE]. Remove the theme section and replace it with [YOUR THEME, OR NOTHING].

**4. Pressure-test it before you rely on it**

> Read tests/rehearse.sh and tests/README.md. Add scenarios for three failure modes specific to our setup that are not covered yet, then run the whole suite and show me what breaks. I want the disasters tested, not the happy path.

**5. If your tool cannot run the repo** (chat window only)

> Here are five transcripts from five parallel sessions of a workshop about [SUBJECT], and a brief describing what to produce. Follow the brief exactly and return only the JSON it specifies, with no commentary and no markdown fences. If a transcript is labelled as a fallback rather than a real recording, do not write anything implying a person said it.
>
> [PASTE framework.md, THEN EACH TRANSCRIPT LABELLED WITH ITS SOURCE]

Then save the JSON and run the deck builder on it directly:

```bash
python3 tools/build-deck/build_deck.py --payload out.json \
  --out closeout/presentation.html \
  --sources sky-city=transcript,swamp-planet=transcript,...
```

The validation still applies, which is the whole point: the checking does not depend on which tool produced the answer.

**6. Review it the way we did**

> Read RUN-THIS-YOURSELF.md, then review [OUR SYSTEM] against those ten principles one at a time. For each, say whether we follow it, and if not what specifically we would change. Be concrete and skip the ones that do not apply. I am most interested in anything we are asking the model to decide that has exactly one correct answer.

### A word on the prompts themselves

None of these ask a model to be careful, thorough or accurate, because that never works. They ask for a narrow, checkable output and say what to do at the edges. That is the same principle as the rest of this document, applied to the prompt instead of the pipeline.

If you only take one thing from any of this, take the third rung of the degraded path: **build the deck that exists before the event.** Everything else here is an improvement on a floor that already stops you failing in public.
