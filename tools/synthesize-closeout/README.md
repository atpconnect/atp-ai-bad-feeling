# Closeout Synthesis

The tool that turns the five station transcripts into the Throne Room deck, in the few minutes between the stations ending and the group reassembling. Checked in here so the whole process, not just the resulting content, is visible.

```bash
tools/synthesize-closeout/seed.sh          # days before: build the floor from question lists
tools/synthesize-closeout/synthesize.sh    # on the night: rebuild from whatever has arrived

tools/synthesize-closeout/synthesize.sh --no-hedge          # one model, half the tokens
tools/synthesize-closeout/synthesize.sh --voices            # add the character voices
tools/synthesize-closeout/synthesize.sh --voices=yoda,vader # just these two
tools/synthesize-closeout/synthesize.sh --help
```

Both write `closeout/presentation.html`. Both are safe to re-run as often as you like.

## How it fits into the event

1. **Days before.** Question lists land in `stations/<name>/questions.md`, each with pre-filled likely answers. `seed.sh` builds a complete, presentable deck from them, with every station marked as a fallback. From this point on there is always a deck. Nothing that happens on the night can leave Fleet Command in front of the room with nothing.
2. **On the night.** As each station wraps, its transcript is filed by [`tools/intake-transcript/`](../intake-transcript/) into `stations/<name>/transcript.md`.
3. **In the gap.** `synthesize.sh` reads whatever is currently there, prefers a real transcript over a question list per station, asks the model for structured content, validates it, and rebuilds the deck.
4. **Presenting.** Open the HTML in a browser. Arrow keys or Next. Fleet Command drives it live and adapts; it is not read verbatim.

Per station, in priority order: `transcript.md` / `transcript.txt`, then `transcript.docx` via pandoc, then `questions.md` as the flagged fallback. A station with none of those is a hard error, because a deck that silently drops a station is worse than no deck.

## What the model is and isn't asked for

It gets the transcripts and the brief in [`framework.md`](framework.md), and it returns **JSON, not a deck**. No HTML, no formatting, no slide order, and specifically not which stations had a real transcript, because that is already known from disk. The deck is assembled from that JSON by [`tools/build-deck/`](../build-deck/), which rejects anything that doesn't fit the schema and leaves the existing deck in place when it does.

The prompt is piped on **stdin**, not passed as an argument. Five real 45-minute transcripts come to about 285KB, and Linux caps a single argv string at 128KB, so the obvious `-p "$(cat ...)"` works in every small test and fails only when the transcripts are full length. Which is to say, only on the night. See [`tests/README.md`](../../tests/README.md).

## Timing

Measured, not estimated, against five full-length transcripts with the real CLI:

| Step | Measured |
|---|---|
| Teams generating one transcript after a meeting is **ended** | 2.5 to 5 min |
| Five staggered endings, last transcript in hand | ~7 min |
| Primary model call | **69 s to 167 s** |
| Standby model call (haiku), same 290KB prompt, alone | **81 s** |
| Standby model call, running concurrently with the primary | **~138 s** |
| Validation and deck build | < 1 s |

Call it ten minutes end to end, worst case.

The model call is the part worth understanding. Real runs came in at 69, 81, 102, 105 and 167 seconds, and **the slowest was on the smallest input**. Latency varies more than twofold run to run and is not driven by transcript length, so plan against the slow end and not the median. Re-measure any time with `REAL_MODEL=1 tests/rehearse.sh fullsize`.

## The hedge: two models, in parallel, not a race

Two requests go out at once. The primary gets the whole deadline to itself; the standby is only used if the primary misses it or comes back unusable.

```
PRIMARY_MODEL=""       the CLI default
FAST_MODEL=haiku       empty string disables the hedge entirely
DEADLINE_S=180         how long the primary gets
GRACE_S=45             extra time to wait for the standby after that
```

**It is optional.** `--no-hedge`, or `HEDGE=off`, runs a single model and halves the tokens. That is the right call for a dry run, for a re-run when you already know the model is behaving, and for any time you are not standing in front of a room. It is on by default because the night is the case it was built for.

**Why not a race.** Taking whichever finishes first means presenting the weaker deck any time the standby happens to land a few seconds earlier, which on these measurements is most of the time. Quality is the thing we are protecting; the deadline is the thing we are insuring against.

**Why not a sequential retry.** A serial fallback burns the primary's entire deadline before the standby even starts. At the measured numbers that is 180 seconds gone, then 81 more. Running them together caps the worst case at roughly the deadline.

**What it actually buys**, in order of how likely you are to need it:

1. **Tail latency.** Two calls go slow independently, so it takes two bad draws to hurt you.
2. **A second attempt at valid output** if the primary returns something the schema rejects.
3. **Nothing at all** if the venue network is down or the account is rate limited. Both paths share those. That is what the seeded deck is for, and it is why the hedge does not replace it.

**It is not free.** Haiku answered the same prompt in 81 seconds alone and about 138 seconds while the primary was running beside it. Two concurrent calls slow each other down, so the standby is insurance against a bad draw, not a fast lane you can count on to beat the deadline by itself. `GRACE_S` exists precisely because the standby can land after the deadline it was meant to cover, and in the live test it did.

**The deck says which one wrote it.** If the standby carried the room, the provenance line on the method screen says so. Same principle as the fallback banners: the failure to fear is not a worse answer, it is a worse answer that looks identical to a better one.

This gives three rungs, each one presentable on its own: the primary model, the standby on the same real transcripts, and the seeded deck built from question lists days earlier.

## Requires

The `claude` CLI, logged in. `pandoc` for `.docx` transcripts. Python 3 for the builder and validator.

## Character voices

A live toggle during the closeout: same findings, same numbers, same slide, different narrator. Press **1** to **5**, or **V** to cycle. The screen you are on does not change, so you can switch mid-sentence and keep your place.

```bash
tools/synthesize-closeout/synthesize.sh --voices             # yoda,vader,threepio
tools/synthesize-closeout/synthesize.sh --voices=yoda,vader
```

Voices are defined one per file in [`voices/`](voices/), so adding one is writing a paragraph of direction. The shared rules live in [`voices.md`](voices.md).

**Off by default, and always a second pass after the deck is already written.** A single voice pass measured at 174 seconds even though its input is twenty times smaller than the main prompt, because latency here tracks output tokens and plain variance, not input size. So it never goes on the critical path: the straight deck is on disk and presentable before the first voice call is made. Run it the day before, or on the night once the deck is up and people are still walking back to their seats.

**A voice is just another payload.** It goes through the identical schema validator, so it cannot drop a station, rename one, or change how many points a slide has. One that fails validation is dropped and the others carry on; if all of them fail, the straight deck stands and the run still exits clean.

**The numbers are checked, not trusted.** After a voice validates, its figures are compared against the straight deck's and anything missing is named in a warning. The joke is only allowed near the findings because the findings survive it, so that claim gets verified rather than asserted. It is a warning and not a rejection, because a voice may legitimately spell a figure out in words.

**Three quality checks the schema cannot make**, all of them advisory, and all of them real failures in live runs before they became checks:

| Check | Catches |
|---|---|
| Figures diff | A voice that dropped numbers the straight deck had. The findings must survive the joke. |
| Divergence | A voice that rewrote under 60% of its fields, so it validates perfectly and is not worth a button. |
| Reference density | More than one Star Wars reference on a single screen. Invisible slide by slide, obvious across a deck. |

**The two method screens never change voice.** They are our words rather than the model's, and they are the evidence for everything else in the deck. A joke is a bad place to keep your evidence.

## Presenting it

Press **P**. That switches the deck into projector mode and it sizes itself to the screen it is actually on.

| Key | Does |
|---|---|
| Arrows, space, PageUp/Down | Move between screens |
| **P** | Projector mode on and off |
| **D** | Reveal the detail text on the current screen |
| **+** / **-** | Nudge the type size, which overrides the automatic fit |
| **1** to **5**, **V** | Character voices |
| Home / End | First and last screen |

**Projector mode shows headlines, not detail, and that is a measurement rather than a preference.** Five headlines each followed by two lines of detail needs 1458px of a 993px screen at type large enough to read from the back of a room. Something has to go, and it should be the thing nobody reads off a wall in a bar. Headlines plus the takeaway is a slide; headlines plus 400 characters of detail is a document being projected at people. Press D if you want the detail on a particular screen.

**It fits itself to the room.** The deck starts at double size and shrinks until the screen fits the screen, because a projector cannot scroll and the takeaway is the last element on every slide, so anything that overflows takes the line for the room with it. The moment you nudge with + or -, the automatic fit stops arguing with you: at that point you are standing in the room and it is not.

## Following along on a phone

Every screen carries a QR to **its own anchor**, so someone scanning during station four lands on station four, with the full detail that would not fit on the projector.

```
FOLLOW_URL=https://atpconnect.github.io/atp-ai-bad-feeling/closeout/presentation.html
tools/synthesize-closeout/synthesize.sh --no-follow      # no QR, no link
```

The QRs are generated at build time with `qrencode` and inlined as SVG, so they render with no network. A QR that needs the venue wifi to appear is a QR that fails in exactly the room it was made for. If `qrencode` is not installed the deck falls back to showing the link as text.

**The link only resolves once the deck is pushed.** Two things have to be true: GitHub Pages enabled on the repo, and this run's deck committed and pushed. Push it immediately after synthesis and before you start talking; Pages takes under a minute to publish, which is roughly slide three.
