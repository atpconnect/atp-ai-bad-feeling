# Transcript Intake

Files the transcripts that land on Fleet Command's laptop during the event.

```bash
tools/intake-transcript/intake.sh              # from ~/Downloads
tools/intake-transcript/intake.sh --dry-run    # show what it would do
tools/intake-transcript/intake.sh /path/to/dir
```

## Why this exists

On the night, transcripts arrive two ways and both land in `~/Downloads`:

- **Teams exports**, once a station's meeting has been ended. Named like `Sky City-20260917_190412-Meeting Recording.docx`.
- **Email attachments** from a station pilot's own second-device recorder, named however that pilot's phone felt like naming them.

Copying five files into five directories, converting the `.docx` ones, under time pressure, in a bar, with a room waiting, is exactly the kind of step that goes wrong. So it is a script.

## What it does

Matches the station from the filename on the distinctive word, so `Sky City-2026...docx`, `skycity.txt` and `Ice Planet transcript (1).docx` all land correctly. Converts `.docx` to text with pandoc on the way in. Prints a status table for all five stations at the end, which is the thing worth looking at before you run synthesis.

Two rules it will not break:

- **A transcript already filed is never overwritten.** If a station has a real transcript and a second file shows up for it, the existing one wins and the new one is reported as skipped. Re-running intake is always safe.
- **It never guesses.** A file it cannot match to a station is listed as unmatched for you to handle by hand, rather than being filed somewhere plausible.
