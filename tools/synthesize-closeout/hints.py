#!/usr/bin/env python3
"""Pilot-flagged moments: the things a station pilot asked out loud to have in the deck.

Station pilots were told that if they want something to reach the closeout, they should
say so plainly on the recording, in words like "that is a really good point, I'd like to
see that get into the presentation". This finds those moments.

It finds them in code rather than asking the model to spot them, for the same reason the
deck takes the fallback flags off disk: it is a question with an exact answer, and a model
asked to find eight needles in 285KB of transcript will miss some and invent others. Code
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

# A flag needs BOTH halves in the same breath: wanting something, and naming where it
# should go. Either alone is ordinary conversation. "I want to get this right" is not a
# flag, and neither is "we'll see it in the presentation later".
INTENT = re.compile(
    r"\b(want|wanted|would like|i'd like|like to see|make sure|makes? it into|"
    r"needs? to|has to|have to|should|must|capture|captur\w+|include|includ\w+|"
    r"put (?:that|this|it)|get (?:that|this|it)|don'?t lose|do not lose|"
    r"flag (?:that|this|it)|worth (?:capturing|noting|having))\b", re.I)

TARGET = re.compile(
    r"\b(presentation|deck|close ?-? ?out|closing session|throne room|"
    r"read ?-? ?out|final slides?|closing slides?|wrap ?-? ?up)\b", re.I)

# "Name 12:34" or "Name 1:02:03" on a line of its own opens a turn. Covers both the Teams
# export and the expected transcripts, which are written in the same shape on purpose.
SPEAKER = re.compile(r"^(?P<who>\S.{0,58}?)\s+(?P<at>\d{1,3}:\d{2}(?::\d{2})?)\s*$")

# How much of what came before the flag to carry with it. The flag itself is usually a
# pronoun pointing backwards ("I'd like to see THAT in the deck"), so the substance is
# almost never in the sentence that marks it.
LOOKBACK_TURNS = 3
MAX_EXCERPT_CHARS = 1400

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


def turns(text):
    """[(speaker, timestamp, said)] in order. Teams puts a bare [] between turns."""
    out, who, at, buf = [], None, None, []
    for line in text.splitlines():
        if line.strip() == "[]":
            continue
        m = SPEAKER.match(line)
        if m:
            if who is not None:
                out.append((who, at, "\n".join(buf).strip()))
            who, at, buf = m.group("who").strip(), m.group("at"), []
        elif who is not None:
            buf.append(line)
    if who is not None:
        out.append((who, at, "\n".join(buf).strip()))
    return out


def flagged_sentence(said):
    """The one sentence that carries the flag, for quoting back in the report."""
    for s in re.split(r"(?<=[.!?])\s+", said):
        if INTENT.search(s) and TARGET.search(s):
            return " ".join(s.split())
    return " ".join(said.split())[:240]


def find(text):
    """Every flagged moment in one transcript, with the turns leading up to it."""
    found, seen = [], set()
    tt = turns(text)
    for i, (who, at, said) in enumerate(tt):
        if not (INTENT.search(said) and TARGET.search(said)):
            continue
        start = max(0, i - LOOKBACK_TURNS)
        # Two pilots flagging the same exchange should not become two hints.
        if start in seen:
            continue
        seen.add(start)
        chunk = []
        for w, a, s in tt[start:i + 1]:
            chunk.append(f"{w} {a}\n{s}" if a else f"{w}\n{s}")
        excerpt = "\n\n".join(chunk)
        if len(excerpt) > MAX_EXCERPT_CHARS:
            excerpt = "..." + excerpt[-MAX_EXCERPT_CHARS:]
        # Kept apart from the excerpt so coverage can score each candidate turn on its
        # own. A flag points at one thing that was just said, not at the whole window,
        # so scoring the window as a lump lets three unrelated turns bury the match.
        context = [s for _, _, s in tt[start:i] if s.strip()]
        found.append({"at": at, "speaker": who, "marker": flagged_sentence(said),
                      "excerpt": excerpt, "context_turns": context})
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
        "with the turns that came before it, because the flag itself is usually a pronoun "
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
            lines.append(f"Flagged by {h['speaker']} at {h['at']}: \"{h['marker']}\"")
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
        # Score each turn the flag could have been pointing at and keep the best. The
        # marker sentence itself is the pilot's boilerplate, never the substance.
        candidates = h.get("context_turns") or [h["excerpt"].replace(h["marker"], " ")]
        best, hit = 0.0, set()
        for turn in candidates:
            want = tokens(turn)
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
        print(f"  {mark:8} {r['station']} {r['at']} {r['speaker']}: \"{r['marker'][:90]}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
