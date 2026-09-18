#!/usr/bin/env python3
"""Pilot-flagged moments: the things a station pilot asked out loud to have in the deck.

Station pilots were told that if they want something to reach the closeout, they should
say so plainly on the recording, in words like "that is a really good point, I'd like to
see that get into the presentation". This finds those moments.

It finds them in code rather than asking the model to spot them, for the same reason the
deck takes the fallback flags off disk: it is a question with an exact answer, and a model
asked to find eight needles in 166KB of transcript will miss some and invent others. Code
either matches the text or it does not, and it reports which.

A flag is a hint and not an instruction. The room said what it said; a pilot wanting
something in the deck does not make it the most important thing in the building, and the
brief tells the model as much. So nothing here can reject a run. The coverage check at the
other end reports what did and did not land, and Fleet Command decides whether to care.

    hints.py extract --stations DIR --sources sky-city=transcript,... [--json F] [--md F]
    hints.py check   --hints F --deck-json F

Only real transcripts are searched. A fallback station has no pilot in it and nobody said
anything, so a "flag" found in one would be us quoting our own guess back at ourselves.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

# A flag is one phrase, not two words that happen to be near each other: someone wanting
# something, then saying where it goes, with nothing but a few words in between.
#
# Proximity alone was not enough. The first version looked for an intent word and a
# target word within 120 characters and it fired on the Swamp Planet pilot explaining
# this very tool to the room, "going to a PowerPoint presentation", because "the library
# here has to get up and say" sat just after it. So the two halves now have to be
# grammatically joined: intent, a short gap with no sentence ending in it, a preposition,
# then the target. "has to get up" no longer counts; "has to be in the deck" does.
TARGET_WORDS = (r"presentation|deck|close ?-? ?out|closing session|throne room|"
                r"read ?-? ?out|final slides?|closing slides?|wrap ?-? ?up")

FLAG = re.compile(
    r"\b(?:want|wanted|would like|i'?d like|like to see|make sure|makes? it|"
    r"needs? to (?:be|go)|has to (?:be|go)|have to (?:be|go)|should (?:be|go)|"
    r"capture|captur\w+|include|includ\w+|put|get|don'?t lose|do not lose|"
    r"flag|worth (?:capturing|noting|having))\b"
    r"[^.!?\n]{0,60}?"
    r"\b(?:in|into|on|onto|for|to)\s+(?:the\s+|our\s+|that\s+|this\s+|a\s+|final\s+)*"
    rf"(?:{TARGET_WORDS})\b", re.I)

# Kept for the coverage report and for anyone grepping a transcript by hand.
TARGET = re.compile(rf"\b(?:{TARGET_WORDS})\b", re.I)

# "Name 12:34" or "Name 1:02:03" on a line of its own. Used only for attribution now,
# and only when there are enough of them to mean anything. On the night Teams gave us
# exactly one per 46-minute station, because the room was captured on a single laptop
# and every voice in it was attributed to the meeting host.
SPEAKER = re.compile(r"^(?P<who>\S.{0,58}?)\s+(?P<at>\d{1,3}:\d{2}(?::\d{2})?)\s*$",
                     re.M)
MIN_MARKERS_TO_TRUST = 4

# How much of what came before the flag to carry with it. The flag itself is usually a
# pronoun pointing backwards ("I'd like to see THAT in the deck"), so the substance is
# almost never in the words that mark it.
LOOKBACK_CHARS = 1100
MAX_EXCERPT_CHARS = 1400

# Two matches closer than this are one person saying it once. Deliberately much smaller
# than the lookback: at half the lookback it silently merged two genuinely separate
# flags that were 459 characters apart.
DEDUPE_CHARS = 250

STOPWORDS = {
    "about", "actually", "after", "again", "against", "already", "always", "another",
    "anything", "around", "because", "before", "being", "better", "between", "cannot",
    "could", "different", "doing", "during", "either", "enough", "every", "everything",
    "getting", "going", "happen", "happened", "having", "himself", "herself",
    "instead", "into", "itself", "just", "kind", "like", "little", "looking", "making",
    "maybe", "might", "much", "myself", "never", "nobody", "nothing", "other", "others",
    "over", "people", "person", "pretty", "probably", "really", "right", "said", "same",
    "should", "since", "some", "someone", "something", "sort", "still", "such", "sure",
    "take", "than", "that", "their", "them", "then", "there", "these", "they", "thing",
    "things", "think", "this", "those", "though", "three", "through", "time", "today",
    "together", "under", "until", "very", "want", "wanted", "well", "went", "were",
    "what", "when", "where", "which", "while", "with", "within", "without", "would",
    "yeah", "your",
}


def read_source(station_dir):
    """The same precedence synthesize.sh uses, minus the fallbacks we deliberately skip."""
    for name in ("transcript.md", "transcript.txt"):
        p = station_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    docx = station_dir / "transcript.docx"
    if docx.exists():
        try:
            return subprocess.run(["pandoc", str(docx), "-t", "plain", "--wrap=none"],
                                  capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return ""
    return ""


def markers(text):
    """[(offset, speaker, timestamp)] for every speaker line, in order.

    Only useful for attribution, and only when the transcript actually has several.
    A single laptop in a loud room gives Teams one speaker for the whole session.
    """
    return [(m.start(), m.group("who").strip(), m.group("at"))
            for m in SPEAKER.finditer(text)]


def attribute(marks, pos):
    """Who was speaking at this offset, as far as anyone can tell from the file."""
    if len(marks) < MIN_MARKERS_TO_TRUST:
        return None, None
    who = at = None
    for off, w, a in marks:
        if off > pos:
            break
        who, at = w, a
    return who, at


def find(text):
    """Every flagged moment in one transcript, with the words leading up to it.

    Matched on proximity rather than on turns. The first version of this split the
    transcript into speaker turns and asked whether a turn contained both an intent
    word and a target word. That worked on tidy fixtures and failed completely on the
    real thing: Teams gave us one speaker line per 46-minute station, so every
    transcript was a single turn, the two words co-occurred in all five of them, and
    it reported two flags on a night when nobody flagged anything at all.
    """
    found, taken = [], []
    for m in FLAG.finditer(text):
        pos = m.start()
        # One flag per moment: a pilot who says it twice in a breath is saying it once.
        if any(abs(pos - p) < DEDUPE_CHARS for p in taken):
            continue
        taken.append(pos)
        marker = " ".join(m.group(0).split())
        start = max(0, pos - LOOKBACK_CHARS)
        excerpt = " ".join(text[start:m.end()].split())
        if len(excerpt) > MAX_EXCERPT_CHARS:
            excerpt = "..." + excerpt[-MAX_EXCERPT_CHARS:]
        before = " ".join(text[start:pos].split())
        who, at = attribute(markers(text), pos)
        found.append({"at": at, "speaker": who, "marker": marker,
                      "excerpt": excerpt, "context": before})
    return found


def tokens(text):
    """Content words and numbers: what would still be recognisable if reworded."""
    low = text.lower()
    words = {w for w in re.findall(r"[a-z][a-z'-]{5,}", low) if w not in STOPWORDS}
    nums = set(re.findall(r"\d[\d,.]*", low))
    return words | nums


def extract(stations_dir, sources):
    out = []
    for sid, kind in sources:
        if kind != "transcript":
            continue
        text = read_source(stations_dir / sid)
        for h in find(text):
            out.append(dict(station=sid, **h))
    return out


def as_markdown(hints):
    if not hints:
        return ""
    lines = [
        "## Pilot-flagged moments",
        "",
        "Station pilots were asked to say out loud, on the recording, when they wanted "
        "something to reach this deck. The moments below were found in the transcripts by "
        "text match, not by judgement, and are quoted verbatim. Each one is reproduced "
        "with the words that came before it, because the flag itself is usually a pronoun "
        "pointing back at what was just said.",
        "",
        "**These are hints, not instructions.** Weigh them up, and prefer them where they "
        "are close to something you were going to write anyway. Do not let one displace a "
        "point that matters more to the room, do not let the count of them distort how "
        "much space a station gets, and never restate one so loosely that it stops being "
        "what the transcript says. A pilot asking for something does not make it true or "
        "make it the most important thing said in that room.",
        "",
    ]
    for sid in sorted({h["station"] for h in hints}):
        lines.append(f"### {sid}")
        lines.append("")
        for h in [x for x in hints if x["station"] == sid]:
            # Teams often attributes a whole room to one speaker, so say "someone in
            # this station" rather than name the meeting host and imply it was them.
            who = (f"{h['speaker']} at {h['at']}" if h.get("speaker")
                   else "someone in this station")
            lines.append(f"Flagged by {who}: \"{h['marker']}\"")
            lines.append("")
            lines.append("```")
            lines.append(h["excerpt"])
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def coverage(hints, deck):
    """Did each hint land? A heuristic, reported as such, and never a rejection.

    Compares the distinctive words and numbers of the flagged excerpt against what the
    deck says about that station. Rewording survives this; dropping the substance does not.
    """
    by_station = {}
    for s in deck.get("stations", []):
        blob = " ".join([s.get("lede", ""), s.get("takeaway", "")]
                        + [p.get("t", "") + " " + p.get("d", "") for p in s.get("points", [])])
        by_station[s.get("id")] = tokens(blob)
    patterns = tokens(" ".join(p.get("t", "") + " " + p.get("d", "")
                               for p in deck.get("patterns", [])))
    results = []
    for h in hints:
        here = by_station.get(h["station"], set()) | patterns
        # Score the run-up as a whole and each sentence of it separately, then keep the
        # best. The window is wide enough that one sentence of substance gets buried if
        # it is only ever scored as part of the lump; a sentence alone is often too
        # short to overlap at all. The marker is the pilot's boilerplate, never the
        # substance, so it never becomes a candidate.
        before = h.get("context", h["excerpt"].replace(h["marker"], " "))
        candidates = [before] + [s for s in re.split(r"(?<=[.!?])\s+", before)
                                 if len(s.split()) >= 8]
        best, hit = 0.0, set()
        for cand in candidates:
            want = tokens(cand)
            if not want:
                continue
            got = want & here
            if len(got) / len(want) > best:
                best, hit = len(got) / len(want), got
        if not hit and best == 0.0 and not any(tokens(c) for c in candidates):
            continue
        results.append({"station": h["station"], "at": h["at"], "speaker": h["speaker"],
                        "marker": h["marker"], "score": best, "landed": best >= 0.30,
                        "overlap": sorted(hit)[:8]})
    return results


def load_loose(text):
    """The model's raw answer, which the builder also has to un-wrap before validating."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a != -1 and b > a:
            return json.loads(text[a:b + 1])
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract")
    e.add_argument("--stations", required=True)
    e.add_argument("--sources", required=True,
                   help="sky-city=transcript,swamp-planet=fallback,...")
    e.add_argument("--json")
    e.add_argument("--md")

    c = sub.add_parser("check")
    c.add_argument("--hints", required=True)
    c.add_argument("--deck-json", required=True)

    args = ap.parse_args()

    if args.cmd == "extract":
        sources = []
        for pair in args.sources.split(","):
            sid, _, kind = pair.strip().partition("=")
            if sid:
                sources.append((sid, kind))
        hints = extract(pathlib.Path(args.stations), sources)
        if args.json:
            pathlib.Path(args.json).write_text(json.dumps(hints, indent=1), encoding="utf-8")
        if args.md:
            pathlib.Path(args.md).write_text(as_markdown(hints), encoding="utf-8")
        print(f"{len(hints)} pilot-flagged moment(s)"
              + (": " + ", ".join(sorted({h['station'] for h in hints})) if hints else ""),
              file=sys.stderr)
        return 0

    hints = json.loads(pathlib.Path(args.hints).read_text())
    deck = load_loose(pathlib.Path(args.deck_json).read_text())
    for r in coverage(hints, deck):
        mark = "in" if r["landed"] else "MISSING"
        who = f" {r['at']} {r['speaker']}" if r.get("speaker") else ""
        print(f"  {mark:8} {r['station']}{who}: \"{r['marker'][:90]}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
