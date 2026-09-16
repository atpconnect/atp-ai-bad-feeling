# Rehearsal Harness

This is how we ran reps on the night before the night. Every scenario runs the real tools against real files in a scratch copy of the repo: intake from a mock Downloads folder, synthesis, schema validation, deck build. Nothing is mocked except the model, and the model stub is swapped between modes so its failures get rehearsed too.

```bash
tests/rehearse.sh                    # every scenario, against the model stub, ~2 seconds
tests/rehearse.sh happy mixed        # named scenarios
tests/rehearse.sh --keep disaster    # keep the scratch dir and print its path
REAL_MODEL=1 tests/rehearse.sh fullsize    # the real claude CLI, real-length transcripts
```

## The scenarios

| Scenario | What night it is |
|---|---|
| `seed` | Days before. Question lists exist, no transcripts. Builds the floor. |
| `expected` | Days before, with the expected transcripts written. The deeper fallback outranks the question list, is still labelled a fallback, and never blocks the real transcript. |
| `happy` | All five recordings worked. |
| `mixed` | Three Teams exports, one emailed backup from a pilot's own device, one total loss. |
| `docx` | All five arrive as Teams `.docx` exports and have to be converted. |
| `disaster` | Every recording failed. Five fallbacks, and there is still a deck. |
| `late` | A transcript lands after a deck was already built. Re-run must improve, not clobber. |
| `garbage` | The model returns an apology instead of JSON. |
| `badschema` | Well-formed JSON that drops a station. |
| `liar` | The model relabels a fallback as a real transcript. |
| `crash` | The CLI exits nonzero, rate limited. |
| `nothing` | No transcript and no question list. The one case we refuse to paper over. |
| `noprior` | A bad model run with no seeded deck behind it. The case `seed.sh` exists to prevent. |
| `fullsize` | Transcripts inflated to the ~8,500 words a real 45-minute station produces, and timed. |
| `hedge-primary` | Both models run; the primary is fine and the standby is ignored. |
| `hedge-standby` | The primary blows the deadline and the standby carries the room. |
| `hedge-primary-bad` | The primary returns fast but useless; switch immediately rather than waiting out the deadline. |
| `hedge-both-bad` | Both models fail. The seeded deck is the whole point. |
| `hedge-disabled` | `FAST_MODEL=""`. Single path, and no hang waiting on a standby that was never started. |
| `no-hedge-flag` | `--no-hedge` on a run that succeeds: one model, no standby, complete deck. |
| `voices` | Two character voices generated and toggleable in the deck. |
| `voices-partial` | One voice fails validation. Drop it, keep the other, never lose the deck. |
| `voices-all-fail` | Every voice fails. The straight deck stands and the run still exits clean. |
| `voices-launder` | A voice quietly drops the figures, and gets called out for it. |
| `voices-timid` | A voice that validates perfectly and is pointless on stage. |
| `refs-overdone` | Film quotes turning up on a slide when the brief asks for none. |
| `project` | Projector mode exists, scales off one variable, and fits itself to the screen. |
| `follow` | Every screen carries a QR and a link to its own anchor, and `--no-follow` removes them. |
| `qr-decodes` | The QR is rendered and scanned back with zbarimg. Skips if the tools are missing. |
| `demo` | A demo build says so on every screen, and a live build never does. |
| `theming` | Five distinct station accents, applied per screen, every one clearing WCAG AA. |
| `sponsors` | The three sponsor logos land on their own station and nowhere else, inlined, each in the light or dark variant its theme needs. |
| `hints` | Pilot-flagged moments are found in real transcripts and never in a fallback, decoy phrasings are ignored, and the coverage check reports what landed without rejecting anything. |
| `docs` | Every scenario in the runner appears in this table. It has drifted twice. |

## What the reps actually found

Every one of these was a real defect found by running the thing, not by reading it.

**The prompt was passed as a shell argument, which breaks at exactly the wrong moment.** `claude -p "$(cat prompt)"` works fine on a 3KB test transcript. Linux caps a single argv string at 128KB (`MAX_ARG_STRLEN`, 32 pages, independent of the much larger `ARG_MAX`), and five real 45-minute transcripts come to about 285KB. So the tool worked in every small test and would have died with `Argument list too long` on the night, with a room full of people waiting. Found by `fullsize`. Fixed by piping the prompt on stdin.

**The model could launder a fallback into a real transcript.** The deck took each station's `source` from the model's own output, so a model that claimed a fallback was a transcript got believed, and the on-screen "not from a transcript" warning silently disappeared. Found by `liar`. Fixed by not asking: the source is established from what is on disk and injected into the builder, and anything the model says about it is discarded. The general rule is that you should never ask a model to report a fact you already know.

**A 26-character overrun threw away an entire run.** The real model returned a takeaway 226 characters long against a 200-character cap, and the whole synthesis was rejected two minutes before it was needed. Found by `REAL_MODEL=1 happy`. Fixed by splitting validation in two: structural problems (missing station, unknown id, wrong number of points, not JSON) are hard rejections because they mean the model misunderstood the task; length caps are cosmetic, so overlong text is trimmed on a word boundary and reported.

**Synthesis takes between 69 and 164 seconds, and the coordinator checklist said 60.** Four real-model runs came in at 69, 102, 105 and 164 seconds. The important part is not the median, it is that **the slowest run was on the smallest input**: latency varies more than twofold for reasons that have nothing to do with how much we ask it to read, so it cannot be shortened by trimming transcripts. The run of show now gets a three-minute slice rather than a one-minute one, which moves the end-to-end worst case from roughly 8 minutes to roughly 10. Had we measured once and written that number down, we would have planned against 105 seconds and been wrong by a minute on the night.

**A 600-word test transcript flatters everything.** The fixtures are written to be readable. Real stations produce something like 8,500 words each. `tests/inflate.py` pads the fixtures to that length so the timing rep measures the real thing; without it, two of the four findings above stay hidden.

**The parallel models ran strictly in sequence, and looked fine doing it.** `primary_pid=$(spawn primary ...)` starts a background subshell, but the subshell inherits the command substitution's pipe, and `$( )` blocks until every holder of that pipe closes it. So each "background" call blocked the caller until it finished. The hedge produced correct output the entire time; it was simply useless, because both calls were serial. Found only because `hedge-primary` asserts on elapsed time rather than on the result. A test that had checked the output alone would have passed forever.

**Calibrating a prompt by adjective does not work, in either direction.** The first live Sage pass inverted nearly every sentence into things like "Assigned it a category to be tracked in, nobody had." The fix was a rule saying invert at most one sentence in three and let readability win. The next live pass came back **91% textually identical to the straight deck**: it validated perfectly, and it was pointless, because a button that changes four words is not worth pressing. Neither version was catchable by the schema. What fixed it was replacing the adjectives with a three-point worked example in each voice file, showing the same real sentence rendered too little, at target, and too far. There is now an automatic check for the second failure, because it is the one you do not notice: if under 60% of fields were actually rewritten, the run says so and names the file to strengthen.

**The themed flourishes drifted past their cap, and nobody would notice slide by slide.** The brief asked for three or four across the deck; a live run produced seven, including two on one slide. Each one read fine on its own, which is exactly the problem: reference density is invisible while you are looking at any single screen and obvious across a whole deck. The brief now bans film quotes outright, which is a rule a machine can check, and a counter reports any screen carrying one. Advisory, not fatal.

**`kill` on an already-dead process tripped `set -e`.** Cleaning up the losing model ended the script with a nonzero status even after a completely successful run. Found by `hedge-primary` asserting `exits 0`.

## Layout

```
tests/
  rehearse.sh              the scenarios
  inflate.py               grows fixtures to real 45-minute length
  fixtures/questions/      the five question lists with pre-filled likely answers
  fixtures/arrivals/       mock Teams exports, .txt and .docx, named as Teams names them
  stubs/claude             stands in for the CLI on PATH
  stubs/model_stub.py      deterministic model, STUB_MODE selects good/fenced/garbage/badschema/liar/fail
```

The fixtures are invented. The people, companies, and numbers in them are not real, and they exist so the pipeline has something of the right shape and size to chew on.
