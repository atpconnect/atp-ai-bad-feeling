#!/usr/bin/env python3
"""Turn a validated JSON payload into the self-contained Throne Room deck.

The model's only job is content: a lede, some points, and a takeaway per station,
plus the cross-cutting patterns. Everything else about the deck (structure, order,
branding, the method screens, the QR code, navigation) is generated here, in code,
where it cannot vary between runs.

That split is deliberate and it is the whole reliability argument:
  - The model does the part that genuinely needs judgment.
  - Code does the part that has one correct answer.
  - Invalid model output is rejected outright, and an existing deck is never
    overwritten with something that failed validation.

Usage:
  build_deck.py --payload payload.json --out closeout/presentation.html
  build_deck.py --payload payload.json --out ... --mode seeded
"""

import argparse
import base64
import subprocess
import html
import json
import pathlib
import re
import sys
from datetime import datetime

REPO = pathlib.Path(__file__).resolve().parents[2]
QR_PATH = REPO / "assets" / "repo-qr-code.png"
SPONSOR_DIR = REPO / "assets" / "sponsors"
REPO_URL = "https://github.com/atpconnect/atp-ai-bad-feeling"

# Station sponsors, shown on the screen for the station they paid for and nowhere
# else. Two of the three sit on a dark theme, so the variant is chosen from the
# screen's own palette rather than from the reader's OS the way the README does it.
SPONSORS = {
    "swamp-planet": "LogicSpree",
    "ice-planet": "Griffin",
    "snow-monster-cave": "Allata",
}

STATIONS = [
    ("sky-city", "Sky City", "Infrastructure and integration with third-party tools"),
    ("swamp-planet", "Swamp Planet", "Technical debt and data quality"),
    ("ice-planet", "Ice Planet", "Use cases, costs, and scope creep"),
    ("snow-monster-cave", "Snow Monster Cave", "Development"),
    ("asteroid-field", "Asteroid Field", "Compliance, legal, and security"),
]
STATION_IDS = [s[0] for s in STATIONS]
STATION_NAME = {s[0]: s[1] for s in STATIONS}
STATION_THEME = {s[0]: s[2] for s in STATIONS}

# Cosmetic caps. These protect the layout, not the truth, so going over one is not a
# reason to throw away a whole run at 7:50pm. Overlong text is trimmed on a word
# boundary and reported. Structural problems (a missing station, a bad id, the wrong
# number of points, output that isn't JSON) are still hard rejections, because those
# mean the model misunderstood the task rather than got wordy.
# A full palette per station, not just an accent, because an accent was not enough to
# tell the room it had moved. Dark for the swamp, the cave and the asteroid field;
# light for Sky City and Ice Planet.
#
# `bg` is the page behind the card and can be any CSS background, so the clouds and the
# murk are gradients rather than images and the file stays self-contained and offline.
# Everything else is a flat colour, and every text colour is measured against its own
# surface at build time. The build fails below threshold, because five palettes is five
# chances to make something unreadable and this gets projected into a bar.
#
# The check earned its keep twice before any of these existed: the original brand blue
# was failing at 3.98:1 and the original muted grey at 3.80:1.
THEMES = {
    "sky-city": {  # above the clouds, late afternoon
        "bg": ("radial-gradient(1200px 520px at 12% 8%, #FFE7C7 0%, rgba(255,231,199,0) 62%), "
               "radial-gradient(900px 420px at 88% 22%, #FFD1B0 0%, rgba(255,209,176,0) 60%), "
               "radial-gradient(1000px 500px at 50% 100%, #F7B98A 0%, rgba(247,185,138,0) 65%), "
               "linear-gradient(170deg, #FFF3E2 0%, #FBD9BC 55%, #EFA97A 100%)"),
        "surface": "#FFFBF5", "fill": "#FBF1E4", "line": "#EBDCC8",
        "ink": "#2A1A0C", "ink2": "#5C4531", "ink3": "#7A6047",
        "accent": "#9A4F08", "warn": "#8F4B08", "warnbg": "#FDF1E1",
    },
    "swamp-planet": {  # under the swamp canopy
        "bg": ("radial-gradient(900px 480px at 20% 10%, #2C4020 0%, rgba(44,64,32,0) 60%), "
               "radial-gradient(760px 420px at 82% 78%, #1B3018 0%, rgba(27,48,24,0) 62%), "
               "linear-gradient(165deg, #16210F 0%, #1B2A13 50%, #0E170A 100%)"),
        "surface": "#1E2C15", "fill": "#26361B", "line": "#3A4E2C",
        "ink": "#EDF3E4", "ink2": "#C3D2B2", "ink3": "#9DB088",
        "accent": "#A8D06A", "warn": "#E8B45C", "warnbg": "#33280F",
    },
    "ice-planet": {  # daylight on the ice plain
        "bg": ("radial-gradient(1100px 480px at 24% 6%, #FFFFFF 0%, rgba(255,255,255,0) 60%), "
               "radial-gradient(900px 500px at 78% 82%, #BFDCEC 0%, rgba(191,220,236,0) 62%), "
               "linear-gradient(175deg, #F2F9FD 0%, #DCEBF5 55%, #C2DAEA 100%)"),
        "surface": "#FFFFFF", "fill": "#F0F7FB", "line": "#D6E5EF",
        "ink": "#0E2430", "ink2": "#3A5665", "ink3": "#5B7787",
        "accent": "#0F5B78", "warn": "#8F4B08", "warnbg": "#FDF1E1",
    },
    "snow-monster-cave": {  # inside the cave
        "bg": ("radial-gradient(820px 420px at 78% 12%, #3A1E1B 0%, rgba(58,30,27,0) 62%), "
               "radial-gradient(900px 500px at 14% 88%, #2A1412 0%, rgba(42,20,18,0) 60%), "
               "linear-gradient(170deg, #1A1110 0%, #241514 55%, #0F0908 100%)"),
        "surface": "#241615", "fill": "#2E1C1A", "line": "#452926",
        "ink": "#F6E9E7", "ink2": "#D6B8B4", "ink3": "#B08F8B",
        "accent": "#F0736B", "warn": "#F0A35C", "warnbg": "#3A2412",
    },
    "asteroid-field": {  # deep space, and the rocks
        "bg": ("radial-gradient(2px 2px at 18% 22%, #7C8B95 0%, rgba(124,139,149,0) 100%), "
               "radial-gradient(3px 3px at 62% 14%, #6B7A85 0%, rgba(107,122,133,0) 100%), "
               "radial-gradient(2px 2px at 84% 62%, #7C8B95 0%, rgba(124,139,149,0) 100%), "
               "radial-gradient(900px 520px at 70% 20%, #1D242A 0%, rgba(29,36,42,0) 64%), "
               "linear-gradient(168deg, #0C0F12 0%, #141A1F 55%, #080A0C 100%)"),
        "surface": "#171B1E", "fill": "#1F262B", "line": "#333D44",
        "ink": "#E9EDF0", "ink2": "#B8C2C9", "ink3": "#93A0A8",
        "accent": "#7FB4D4", "warn": "#E8B45C", "warnbg": "#2A2412",
    },
}

DEFAULT_THEME = {  # the three screens that are ours
    "bg": "#f5f7f8", "surface": "#ffffff", "fill": "#f5f7f8", "line": "#e3e7e9",
    "ink": "#14181a", "ink2": "#4a5257", "ink3": "#697276",
    "accent": "#2C6FBF", "warn": "#B4610C", "warnbg": "#fdf6ee",
}

# Minimum contrast of each text colour against its own surface. ink is held to AAA
# because it is the body of the slide and the back of the room is a long way away.
CONTRAST_FLOORS = {"ink": 7.0, "ink2": 4.5, "ink3": 4.5, "accent": 4.5, "warn": 4.0}


def _relative_luminance(hex_colour):
    h = hex_colour.lstrip("#")
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast_ratio(fg, bg):
    a, b = sorted((_relative_luminance(fg), _relative_luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def check_themes():
    """Refuse to build a deck nobody at the back can read. Returns a list of failures."""
    bad = []
    for name, t in [("default", DEFAULT_THEME)] + sorted(THEMES.items()):
        for key, floor in CONTRAST_FLOORS.items():
            r = contrast_ratio(t[key], t["surface"])
            if r < floor:
                bad.append(f"{name}.{key} {t[key]} on {t['surface']} is {r:.2f}:1, needs {floor}:1")
    return bad


VOICE_LABELS = {"default": "Default", "interpreter": "Interpreter",
                "elder": "Elder", "enforcer": "Enforcer"}

# Screens written by us, not by the model. They stay in one voice: they are the
# credibility of the whole deck, and a joke is a bad place to keep your evidence.
UNVOICED = ("method", "reliability", "receipts")

LIMITS = {"lede": 500, "takeaway": 280, "t": 150, "d": 560, "closing_line": 360}

CLAMPED = []


class ValidationError(Exception):
    pass


# This repo doesn't use em dashes, and models reach for them constantly. Fixing that
# in code rather than in the prompt: it has exactly one correct answer, so it isn't
# the model's job, and a rule the prompt has to keep winning is a rule that eventually
# loses. A dash between two numbers is a range; anywhere else it's a comma.
DASHES = re.compile(r"\s*[\u2014\u2013]\s*")


def _dedash(value):
    def repl(m):
        i = m.start()
        before = value[:i].rstrip()[-1:] if i else ""
        after = value[m.end():].lstrip()[:1]
        return " to " if before.isdigit() and after.isdigit() else ", "
    return DASHES.sub(repl, value)


# --------------------------------------------------------------------------- validate

def _text(value, field, limit_key, required=True):
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ValidationError(f"{field}: missing or empty")
        return ""
    if not isinstance(value, str):
        raise ValidationError(f"{field}: expected a string, got {type(value).__name__}")
    value = " ".join(value.split())
    value = _dedash(value)
    limit = LIMITS[limit_key]
    if len(value) > limit:
        cut = value[:limit - 1]
        if " " in cut[limit // 2:]:
            cut = cut.rsplit(" ", 1)[0]
        CLAMPED.append(f"{field}: {len(value)} chars, trimmed to {len(cut) + 1} (cap {limit})")
        value = cut.rstrip(" ,;:.") + "\u2026"
    return value


def _points(raw, field, lo=3, hi=5):
    if not isinstance(raw, list):
        raise ValidationError(f"{field}: expected a list")
    if not (lo <= len(raw) <= hi):
        raise ValidationError(f"{field}: {len(raw)} points, expected {lo} to {hi}")
    out = []
    for i, p in enumerate(raw):
        if not isinstance(p, dict):
            raise ValidationError(f"{field}[{i}]: expected an object with t and d")
        out.append({
            "t": _text(p.get("t"), f"{field}[{i}].t", "t"),
            "d": _text(p.get("d"), f"{field}[{i}].d", "d"),
        })
    return out


def validate(payload, sources):
    """sources maps station id -> "transcript"|"fallback", established by the caller
    from what is actually on disk. Any `source` the model volunteers is discarded.
    We do not ask the model to report a fact we already know, so it cannot get it
    wrong, and it cannot launder a fallback into a transcript."""
    if not isinstance(payload, dict):
        raise ValidationError("top level: expected a JSON object")

    raw_stations = payload.get("stations")
    if not isinstance(raw_stations, list):
        raise ValidationError("stations: expected a list")

    seen, stations = {}, []
    for i, st in enumerate(raw_stations):
        if not isinstance(st, dict):
            raise ValidationError(f"stations[{i}]: expected an object")
        sid = st.get("id")
        if sid not in STATION_IDS:
            raise ValidationError(
                f"stations[{i}].id: {sid!r} is not one of {', '.join(STATION_IDS)}")
        if sid in seen:
            raise ValidationError(f"stations[{i}].id: {sid!r} appears twice")
        seen[sid] = True
        claimed = st.get("source")
        source = sources[sid]
        if claimed in ("transcript", "fallback") and claimed != source:
            print(f"NOTE: model claimed {sid} was a {claimed}; it was a {source}. "
                  f"Ignoring the model and using what is on disk.", file=sys.stderr)
        stations.append({
            "id": sid,
            "name": STATION_NAME[sid],
            "theme": STATION_THEME[sid],
            "source": source,
            "lede": _text(st.get("lede"), f"stations[{i}].lede", "lede"),
            "points": _points(st.get("points"), f"stations[{i}].points"),
            "takeaway": _text(st.get("takeaway"), f"stations[{i}].takeaway", "takeaway"),
        })

    missing = [s for s in STATION_IDS if s not in seen]
    if missing:
        raise ValidationError(f"stations: missing {', '.join(missing)}")

    stations.sort(key=lambda s: STATION_IDS.index(s["id"]))
    return {
        "stations": stations,
        "patterns": _points(payload.get("patterns"), "patterns"),
        "closing_line": _text(payload.get("closing_line"), "closing_line", "closing_line"),
    }


# --------------------------------------------------------------------------- render

NUMBERS = re.compile(r"\d(?:[\d,.]*\d)?")


def all_text(data):
    out = [data["closing_line"]]
    for st in data["stations"]:
        out += [st["lede"], st["takeaway"]]
        out += [p["t"] for p in st["points"]] + [p["d"] for p in st["points"]]
    out += [p["t"] for p in data["patterns"]] + [p["d"] for p in data["patterns"]]
    return " ".join(out)


def numbers_lost(default_deck, voiced):
    """Figures present in the straight deck that the voice pass dropped.

    The voice brief says every number survives, and that is the only reason the joke
    is allowed near the findings at all. Reported rather than fatal, because a voice
    may legitimately spell a figure out in words, which this cannot see. Worth looking
    at before you present it."""
    before = set(NUMBERS.findall(all_text(default_deck)))
    after = set(NUMBERS.findall(all_text(voiced)))
    return sorted(n for n in before - after if len(n.replace(",", "").replace(".", "")) >= 2)


def fields(data):
    out = [data["closing_line"]]
    for st in data["stations"]:
        out += [st["lede"], st["takeaway"]]
        for p in st["points"]:
            out += [p["t"], p["d"]]
    for p in data["patterns"]:
        out += [p["t"], p["d"]]
    return out


def voice_divergence(default_deck, voiced):
    """Share of fields the voice pass actually rewrote.

    A voice that comes back almost identical to the default deck is a failure the
    schema cannot see: it validates perfectly and is simply pointless on stage. This
    is the cheap automatic version of noticing that by eye, which is how it was found
    the first time. Low scores mean the direction was too timid, not that the deck
    is broken, so it warns rather than rejects."""
    a, b = fields(default_deck), fields(voiced)
    if len(a) != len(b) or not a:
        return 1.0
    return sum(1 for x, y in zip(a, b) if x.strip() != y.strip()) / len(a)


# Counted, not policed. The brief asks for no film quotes at all, both because two on
# a slide is where the room stops hearing the finding and starts waiting for the next
# gag, and because quoting someone else's film in a public deck is not ours to do. A
# model will drift into them anyway, and drift is invisible while you are reading any
# single slide and obvious across a whole deck. This is a blocklist of the lines a
# model reaches for; the event's own title is not on it.
REFERENCES = [
    "older code", "tell me the odds", "how the force works",
    "lack of", "droids you", "do or do not", "there is no try", "no try",
    "it's a trap", "garbage will do", "high ground", "i am your father",
    "the force is strong", "these are not the droids", "great, kid",
]


def reference_report(data):
    """(per-screen overuse, total count). Advisory only."""
    over, total = [], 0
    for st in data["stations"] + [{"id": "patterns", "lede": "", "takeaway": data["closing_line"],
                                   "points": data["patterns"]}]:
        blob = " ".join([st.get("lede", ""), st.get("takeaway", "")]
                        + [p["t"] for p in st["points"]] + [p["d"] for p in st["points"]]).lower()
        n = sum(blob.count(r) for r in REFERENCES)
        total += n
        if n > 0:
            over.append((st["id"], n))
    return over, total


def e(s):
    return html.escape(s, quote=False)


def points_html(points):
    items = "".join(
        '<li><span class="n">{n:02d}</span><span><span class="t">{t}</span>'
        '<br><span class="d">{d}</span></span></li>'.format(n=i + 1, t=e(p["t"]), d=e(p["d"]))
        for i, p in enumerate(points))
    return f'<ol class="points">{items}</ol>'


DEFAULT_FOLLOW_URL = ("https://atpconnect.github.io/atp-ai-bad-feeling/"
                      "closeout/presentation.html")


def qr_svg(url):
    """A minimal inline SVG QR for one URL, via qrencode.

    Inline and offline on purpose: the venue's wifi is not something to bet the
    closeout on, and a QR that needs the network to render is a QR that fails in
    exactly the room it was made for. Returns "" if qrencode is missing, and the
    deck falls back to showing the link as text."""
    try:
        out = subprocess.run(["qrencode", "-t", "SVG", "-m", "1", "-s", "4", "-l", "M",
                              "--svg-path", "-o", "-", url],
                             capture_output=True, check=True).stdout.decode()
    except (OSError, subprocess.CalledProcessError):
        return ""
    box = re.search(r'viewBox="([^"]+)"', out)
    path = re.search(r'<path[^>]*?d="([^"]+)"', out)
    xform = re.search(r'<path[^>]*?transform="([^"]+)"', out)
    if not (box and path):
        return ""
    # qrencode draws the modules as STROKED one-unit horizontal segments, not as filled
    # shapes, and it offsets them with a transform. Re-emit it with fill and no stroke
    # and every segment has zero area, so you get a correctly sized, perfectly blank
    # square. Keep the stroke and keep the transform.
    t = f' transform="{xform.group(1)}"' if xform else ""
    return (f'<svg class="followqr" viewBox="{box.group(1)}" xmlns="http://www.w3.org/2000/svg" '
            f'shape-rendering="crispEdges" role="img" aria-label="QR code to this screen">'
            f'<rect width="100%" height="100%" fill="#fff"/>'
            f'<path{t} d="{path.group(1)}" stroke="#000" stroke-width="1" fill="none"/></svg>')


def qr_data_uri():
    if not QR_PATH.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(QR_PATH.read_bytes()).decode()


def sponsor_logos():
    """station id -> {name, src}, the logo inlined as a data URI.

    Inlined for the same reason as the QR: a logo that needs the venue wifi to
    appear is a logo that is missing from the one room it was bought for. The
    -dark asset is the light-ink version meant to sit on a dark background, so
    the station's own surface colour picks the variant.
    """
    out = {}
    for sid, name in SPONSORS.items():
        surface = THEMES.get(sid, {}).get("surface", "#ffffff")
        dark = int(surface[1:3], 16) < 64
        path = SPONSOR_DIR / (f"{name.lower()}-dark.png" if dark else f"{name.lower()}.png")
        if not path.exists():
            continue
        out[sid] = {"name": name,
                    "src": "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()}
    return out


def method_screens(mode, generated_at, counts, engine=""):
    live, fell_back = counts
    qr = qr_data_uri()
    qr_block = (f'<img class="qr" alt="QR code to {REPO_URL}" src="{qr}">' if qr else "")

    if mode == "demo":
        provenance = (
            "This copy is a <b>demo</b>, built from invented transcripts so the format can be "
            "clicked through before the event. The timings and the machinery are real; the "
            "people, companies and numbers are not.")
    elif mode == "seeded":
        provenance = (
            "This copy was built <b>before the stations ran</b>, from the question lists and "
            "the answers we expected to hear. It is the floor, not the deck: if every recording "
            "in the building had failed, this is what you would be looking at, and it would say "
            "so on every screen.")
    else:
        provenance = (
            f"This copy was built <b>in the room, minutes ago</b>. {live} of 5 stations came from "
            f"a real transcript" + (f", {fell_back} fell back to the pre-written question list"
                                    if fell_back else ", none needed a fallback") + ".")
    if engine:
        provenance += f" Written by {engine}."

    return [
        {
            "id": "method",
            "kicker": "How this was made",
            "title": "Five rooms, one picture, ten minutes",
            "takeaway": "The AI did the reading. Everything that had one correct answer was done by code.",
            "body":
                '<p class="lede">Five stations ran in parallel. Nobody was in more than one of them. '
                'This deck existed before the last one finished talking.</p>'
                + points_html([
                    {"t": "Every station was recorded to its own meeting, hosted by one person",
                     "d": "Not by the pilot running the room. One account owned all five, so no session "
                          "depended on a presenter remembering to press a button correctly."},
                    {"t": "Ending the meeting is what starts the transcript",
                     "d": "Teams generates a transcript 2.5 to 5 minutes after a meeting is ended, not "
                          "left. Five staggered endings, then one to three minutes for the model to read "
                          "every word said in this building and answer. That is the budget you just "
                          "watched us spend, and every number in it was measured in rehearsal."},
                    {"t": "The model was given the transcripts and a written brief, and asked for data",
                     "d": "Not for a deck. It returns structured content, which is checked against a schema "
                          "before anything is rendered. Wrong shape, wrong station name, too many bullets: "
                          "rejected, and the previous deck stands."},
                    {"t": "The slides you are looking at were generated by code, not by the model",
                     "d": "Order, branding, navigation, this screen, the QR code: all deterministic. "
                          "The model only wrote the parts that needed judgment about what was said."},
                    {"t": "Two models ran at once, and it was not a race",
                     "d": "A fast standby answered the same question in parallel. The good model got the "
                          "whole deadline to itself and the standby was only used if it missed. Measured "
                          "on the night's transcripts: 81 seconds against 167. A race would have handed "
                          "you the weaker deck most times it ran."},
                    {"t": "There was always a deck",
                     "d": "A version of this file was built days ago from the question lists alone. Three "
                          "rungs down from here, and every one of them presentable: the good model, the "
                          "standby on the real transcripts, then that. Nothing could leave us with nothing."},
                ])
                + f'<div class="callout"><div class="h">Provenance of this copy</div>'
                  f'<div class="b">{provenance} Generated {generated_at}.</div></div>',
        },
        {
            "id": "reliability",
            "kicker": "The transferable part",
            "title": "Why this worked when your AI program did not",
            "takeaway": "Give the model the judgment call. Never give it anything you could check by machine instead.",
            "body":
                '<p class="lede">Nothing here needed a better model. It needed the unglamorous things '
                'around the model to be decided in advance, and every one of them is a thing your '
                'program can do on Monday.</p>'
                + points_html([
                    {"t": "Deterministic wherever determinism is available",
                     "d": "The model wrote the words. Code decided the running order, the branding, "
                          "which stations are flagged, the navigation, the QR, and this sentence. A "
                          "model that cannot choose the running order cannot get the running order "
                          "wrong. Shrink what it is allowed to decide and you shrink what a human has "
                          "to check at 7:50pm."},
                    {"t": "Never ask a model a question you can already answer",
                     "d": "Which stations produced a real recording is a fact sitting on a disk. The "
                          "deck reads it from there and throws away whatever the model says about it. "
                          "That closed a real hole: a model that relabelled a failed station as a real "
                          "one silently deleted the warning built to catch exactly that."},
                    {"t": "Constrain the output until it can be validated",
                     "d": "It returns JSON against a fixed schema, not slides. Unknown station, missing "
                          "station, too many bullets: rejected, and the deck already on disk stands "
                          "untouched. You cannot check free text. You can check a schema."},
                    {"t": "Write the evals before the night, and test the disasters",
                     "d": "137 automated checks across 24 rehearsals of this evening, including no "
                          "transcript at all, prose instead of JSON, a crashed CLI, a transcript "
                          "arriving late, and a narrator quietly dropping the numbers. The happy path "
                          "is the least useful thing you can test."},
                    {"t": "Score the things you would otherwise argue about",
                     "d": "Did the voices keep every figure? Diffed, not eyeballed. Did a voice change "
                          "anything worth a button? Under 60% of fields rewritten and it is flagged. Too "
                          "many jokes on one slide? Counted. Each one replaced a judgement call somebody "
                          "would have had to make under time pressure, badly."},
                    {"t": "Measure it, do not estimate it",
                     "d": "The run of show budgeted one minute for this synthesis. Measured against real "
                          "full-length transcripts it is 69 to 167 seconds, and the slowest run was on "
                          "the smallest input. Every number on the first screen came from a stopwatch."},
                ]),
        },
    ]


def receipts_screen(qr_block):
    """The last screen: what the discipline on the previous one actually caught.

    This is the event's own premise turned on the event. A room full of people who do
    not run an honest debrief at their own company is owed one, and the only one we can
    honestly give them is ours."""
    return {
        "id": "receipts",
        "kicker": "Our own bad feeling",
        "title": "What that discipline caught, in this deck, this week",
        "takeaway": "Every one of these was found by running the thing. Not one was found by reading it.",
        "body":
            '<p class="lede">This is an AI program too, so it had a bad feeling about itself. '
            'Six defects, all of them from rehearsal, none of them from review.</p>'
            + points_html([
                {"t": "A bug that would have failed live, in this room, tonight",
                 "d": "The prompt was passed as a shell argument. Linux caps a single argument at 128KB "
                      "and five real transcripts come to 285KB, so it worked in every small test and "
                      "would have died the moment it saw the real thing, with everyone sitting here."},
                {"t": "The model could quietly promote a failed station to a real one",
                 "d": "Which deleted the on-screen warning that exists to prevent precisely that. Not "
                      "fixed with a better prompt. Fixed by never asking."},
                {"t": "A 26-character overrun threw away an entire run",
                 "d": "Validation could not tell the difference between output that was wrong and output "
                      "that was merely too long. Now it can: one rejects, the other gets trimmed."},
                {"t": "Two models running in parallel were running in sequence",
                 "d": "And producing perfect output the whole time. Caught only because a test asserted "
                      "on elapsed time rather than on the result."},
                {"t": "The QR codes rendered as perfectly sized blank squares",
                 "d": "Right dimensions, right position, nothing inside. No assertion about the markup "
                      "would have caught it, so the test now scans the code back with a barcode reader."},
                {"t": "A narrator that changed 9% of the words and passed every check",
                 "d": "Correcting one failure produced its exact opposite. The first Elder voice inverted "
                      "nearly every sentence into something you had to read twice. The fix came back "
                      "91% identical to the plain text: it validated perfectly and was pointless on "
                      "stage. Enforcer landed at 58% of fields rewritten and is now at 100%. Three worked "
                      "examples per character fixed both, showing one real sentence too weak, right, "
                      "and too far. The answer to fear is never the obviously wrong one. It is the one "
                      "that looks exactly right."},
            ])
            + '<div class="callout"><div class="h">Take the whole thing</div>'
              '<div class="b">The principles above, each with the code that implements it and the '
              'defect it caught, plus how to run this format yourself: read RUN-THIS-YOURSELF.md. '
              'The runbooks, the tool, the brief and every transcript are public too. Scan any '
              'screen, or go to <b>' + REPO_URL + '</b>.</div>' + qr_block + '</div>',
    }


def station_screen(st, mode="live"):
    """One station's screen.

    A flagged station means two completely different things depending on when the deck
    was built, and saying the wrong one is worse than saying nothing. Before the event
    nothing has failed, it simply has not happened yet, and someone who finds the deck
    early should be told that rather than left to conclude five recordings broke."""
    flagged = st["source"] == "fallback"
    if not flagged:
        banner = ""
        tag = ('<span class="pill warn">MOCK TRANSCRIPT</span>' if mode == "demo"
               else '<span class="pill">TRANSCRIPT</span>')
    elif mode == "seeded":
        banner = ('<div class="flag"><b>This session has not happened yet.</b> You are early. '
                  'What follows is what this station\'s pilot planned to ask and the answers '
                  'we expect to hear, written in advance and published so the link works before '
                  'anyone needs it. On the night it is replaced by what the room actually said.</div>')
        tag = '<span class="pill warn">PREVIEW</span>'
    else:
        banner = ('<div class="flag"><b>Not from a transcript.</b> This station\'s recording did not '
                  'produce usable audio. What follows is built from what its pilot planned to ask '
                  'and the answers we expected, written before the event. Every number and every '
                  'argument on this screen is ours, not the room\'s.</div>')
        tag = '<span class="pill warn">FALLBACK</span>'
    return {
        "id": st["id"],
        "kicker": st["name"],
        "title": st["theme"],
        "takeaway": st["takeaway"],
        "body": banner + f'<p class="lede">{e(st["lede"])} {tag}</p>' + points_html(st["points"]),
    }


def build(data, mode, generated_at, engine=""):
    live = sum(1 for s in data["stations"] if s["source"] == "transcript")
    qr = qr_data_uri()
    qr_block = f'<img class="qr" alt="QR code to {REPO_URL}" src="{qr}">' if qr else ""

    screens = method_screens(mode, generated_at, (live, 5 - live), engine)
    screens += [station_screen(s, mode) for s in data["stations"]]
    screens.append({
        "id": "patterns",
        "kicker": "Across all five",
        "title": "What nobody in one room could see",
        "takeaway": data["closing_line"],
        "body":
            ('<p class="lede">Nobody has said any of this yet. These are the patterns we expect to '
             'connect the five stations, written in advance. The real ones get written on the night, '
             'from what the rooms actually say.</p>' if mode == "seeded" else
             '<p class="lede">Each station saw its own failure mode. These showed up in more than '
             'one of them, which is the only reason this session exists.</p>')
            + points_html(data["patterns"])
            + '<div class="callout"><div class="h">' + e(data["closing_line"]) + '</div>'
              '<div class="b">Everything behind this deck, including the station transcripts and the '
              'tool that built it, is at <b>' + REPO_URL + '</b>. Take it and run this at your own '
              'company.</div>' + qr_block + '</div>',
    })
    screens.append(receipts_screen(qr_block))
    return screens


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
<style>
  :root {
    /* Everything sizes off --fs so presentation mode is one number, not a restyle.
       --s is nudged live with + and - because the only way to know what reads from
       the back of a particular room is to stand in it. */
    --base-fs: 15px;
    --s: 1;
    --fs: calc(var(--base-fs) * var(--s));
    --maxw: 940px;
    --qrw: 92px;
    /* Set per screen from THEMES. The defaults here are the method-screen palette. */
    --brand: #2C6FBF;
    --page: #f5f7f8;
    --warnbg: #fdf6ee;
    --warn: #B4610C;
    --ink: #14181a;
    --ink-2: #4a5257;
    --ink-3: #697276;
    --line: #e3e7e9;
    --fill: #f5f7f8;
    --bg: #ffffff;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--page); color: var(--ink);
    transition: background 320ms ease, color 200ms ease;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: var(--fs); line-height: 1.5;
  }
  /* Presentation mode is one number. Everything sizes off --fs, so doubling --s
     doubles the whole deck rather than restyling it screen by screen. */
  :root.presenting { --s: 2; --maxw: 1760px; }
  :root.presenting .shell { padding: 12px 16px 20px; }
  :root.presenting .stage { padding: 20px 26px 18px; }
  :root.presenting ol.points li { margin-bottom: calc(var(--fs) * 0.55); }
  :root.presenting .lede { margin-bottom: calc(var(--fs) * 0.7); }
  :root.presenting .rule { margin: 10px 0 16px; }
  :root.presenting .takeaway { margin-top: calc(var(--fs) * 0.7); }
  /* Headline big, detail a step down. On a projector the headline is what carries the
     room and the detail is what the phone is for. */
  /* The projector shows headlines. The phone shows the detail.

     This is not a compromise, it is the measurement: five headlines each followed by
     two lines of detail needs 1458px of a 993px screen at readable type, so something
     has to go, and it should be the thing nobody reads off a wall in a bar. Headlines
     plus the takeaway is a slide. Headlines plus 400 characters of detail is a document
     being projected at people. Press D to reveal the detail on any screen. */
  :root.presenting ol.points .d { display: none; }
  :root.presenting.details ol.points .d { display: block; font-size: calc(var(--fs) * .72); }
  :root.presenting ol.points .t { font-size: calc(var(--fs) * 1.05); }
  :root.presenting ol.points li { margin-bottom: calc(var(--fs) * 0.42); }
  /* Big enough to scan from the back of the room, which is the only size that counts.
     A QR only the front two rows can reach is decoration. */
  :root.presenting { --qrw: calc(var(--fs) * 6.4); }
  :root.presenting .head { gap: calc(var(--fs) * 1.1); }
  .shell { max-width: var(--maxw); margin: 0 auto; padding: 28px 24px 64px; }
  .stage { background: var(--bg); border: 1px solid var(--line); border-radius: 6px; padding: 34px 38px 30px;
           box-shadow: 0 1px 3px rgba(0,0,0,.07), 0 14px 44px rgba(0,0,0,.12); }

  .rail { display: flex; gap: 4px; margin-bottom: 22px; }
  .rail span { flex: 1; height: 3px; background: var(--line); cursor: pointer; }
  .rail span.done { background: var(--ink-3); }
  .rail span.now { background: var(--brand); }

  /* Several elements here carry a display rule and are toggled with the hidden
     attribute, which a bare display wins against. Without this an unsponsored
     station renders a src-less img: a broken-image icon and its alt text. */
  [hidden] { display: none !important; }

  /* The QR rides in the top right corner, beside the title rather than below the
     takeaway. At the foot of the card it was the last thing on the screen and the
     first thing the room's eye skipped; up here it is next to the only other thing
     anyone is looking at. The header is two columns so the QR can never overlap a
     long title, whatever the auto-fit does to the type size. */
  .head { display: flex; align-items: flex-start; gap: 22px; }
  .headmain { flex: 1; min-width: 0; }

  .topline { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .wordmark { color: var(--brand); font-weight: 800; letter-spacing: .18em; font-size: calc(var(--fs) * .8); }
  .divider-v { width: 1px; height: 12px; background: var(--line); }
  .kicker { font-size: calc(var(--fs) * .8); letter-spacing: .08em; color: var(--ink-3); text-transform: uppercase; }

  h1 { font-size: calc(var(--fs) * 1.6); line-height: 1.25; margin: 4px 0 0; font-weight: 650; }
  .rule { width: 48px; height: 2px; background: var(--brand); margin: 12px 0 24px; }
  p { margin: 0 0 12px; }
  .lede { font-size: calc(var(--fs) * 1.07); margin-bottom: 20px; }

  ol.points { list-style: none; margin: 0; padding: 0; }
  ol.points li { display: flex; gap: 14px; margin-bottom: 15px; }
  ol.points .n { color: var(--brand); font-weight: 700; font-variant-numeric: tabular-nums; min-width: calc(var(--fs) * 1.35); }
  ol.points .t { font-weight: 600; }
  ol.points .d { color: var(--ink-2); }

  .pill { display: inline-block; font-size: calc(var(--fs) * .7); letter-spacing: .07em; font-weight: 700;
          color: var(--brand); border: 1px solid var(--brand); border-radius: 3px;
          padding: 1px 6px; vertical-align: 2px; margin-left: 4px; }
  .pill.warn { color: var(--warn); border-color: var(--warn); }

  .flag { border: 1px solid var(--warn); border-left-width: 3px; background: var(--warnbg);
          color: var(--ink-2); padding: 11px 14px; border-radius: 4px; margin-bottom: 18px; font-size: calc(var(--fs) * .93); }
  .flag b { color: var(--warn); }

  .callout { border: 1px solid var(--line); border-left: 3px solid var(--brand); background: var(--fill);
             padding: 12px 14px; border-radius: 4px; margin-top: 20px; }
  .callout .h { font-weight: 650; margin-bottom: 4px; }
  .callout .b { color: var(--ink-2); }
  .qr { display: block; width: 132px; height: 132px; margin: 12px 0 2px; image-rendering: pixelated; }

  .takeaway { border-left: 3px solid var(--brand); background: var(--fill); padding: 10px 14px; margin-top: 24px; }
  .takeaway .h { font-size: calc(var(--fs) * .77); letter-spacing: .08em; color: var(--ink-3); font-weight: 700; margin-bottom: 3px; }
  .takeaway .b { font-weight: 600; }

  .nav { display: flex; align-items: center; gap: 8px; margin-top: 22px; }
  button { font: inherit; font-size: calc(var(--fs) * .87); padding: 6px 14px; border-radius: 4px; border: 1px solid var(--line); background: var(--fill); color: var(--ink); cursor: pointer; }
  button.primary { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  button:disabled { opacity: .4; cursor: default; }
  .nav .right { margin-left: auto; font-size: calc(var(--fs) * .8); color: var(--ink-3); }

  .voices { display: flex; align-items: center; gap: 6px; margin-top: 14px;
            padding-top: 14px; border-top: 1px solid var(--line); }
  .voices .lab { font-size: calc(var(--fs) * .77); letter-spacing: .08em; color: var(--ink-3); font-weight: 700; margin-right: 4px; }
  .voices button { font-size: calc(var(--fs) * .8); padding: 4px 10px; }
  .voices button.on { background: var(--brand); color: var(--bg); border-color: var(--brand); }
  /* Demo builds carry this on every screen, not just the first. A page of invented
     people and invented numbers sitting at a public URL has to say so wherever the
     reader happens to land, including on a deep link straight into station four. */
  /* Selecting a narrator on a screen that never changes voice used to do nothing at
     all, with the only explanation in small grey type at the far edge of the voice
     bar. The deck opens on one of those screens, so the first thing anyone tried
     looked broken. Say it where they are looking. */
  .voicenote { border-left: 3px solid var(--brand); background: var(--fill);
               padding: 9px 13px; border-radius: 4px; margin-bottom: 18px;
               font-size: calc(var(--fs) * .85); color: var(--ink-2); }
  .voicenote b { color: var(--ink); }

  .demobar { border: 1px solid var(--warn); border-left-width: 3px; background: var(--warnbg);
             color: var(--ink-2); padding: 9px 13px; border-radius: 4px;
             margin-bottom: 16px; font-size: calc(var(--fs) * .8); }
  .demobar b { color: var(--warn); }

  /* Sponsor logo sits left of the code, matched to its height. It carries no caption
     for the same reason the QR does not: a label under a logo in the corner of a slide
     is read by nobody, and the two of them together are already the only things up
     there that are not the title. */
  .corner { flex: none; display: flex; align-items: center; gap: calc(var(--qrw) * .22); }
  /* On the dark themes the sponsor asset is a white plate rather than inverted ink,
     so it gets the same rounded corner as the QR and the two read as a deliberate
     pair of cards instead of one logo and one rectangle. */
  .sponsor { height: var(--qrw); width: auto; max-width: calc(var(--qrw) * 2.1);
             object-fit: contain; display: block; border-radius: 3px; }
  .follow { flex: none; display: block; }
  .followqr { width: var(--qrw); aspect-ratio: 1 / 1; flex: none; display: block;
              background: #fff; padding: 4px; border-radius: 3px; }
  /* The URL is the no-qrencode fallback, so it only shows when there is no QR to
     scan. In the corner a full URL would be taller than the code it replaces. */
  .follow .u { display: none; }
  .follow.noqr { max-width: calc(var(--fs) * 13); }
  .follow.noqr .u { display: block; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
               font-size: calc(var(--fs) * .72); color: var(--ink-3); word-break: break-all; }

  .voices .hint { margin-left: auto; font-size: calc(var(--fs) * .77); color: var(--ink-3); }

  #printAll { display: none; }
  @media print {
    body { background: #fff; --page: #fff; }
    .rail, .nav, .stage { display: none !important; }
    .shell { max-width: none; padding: 0; }
    #printAll { display: block; }
    #printAll .page { page-break-after: always; padding: 0 0 24px; }
    #printAll .page:last-child { page-break-after: auto; }
  }
</style>
</head>
<body>
<div class="shell">
  <div class="stage">
    <div class="rail" id="rail"></div>
    <div class="demobar" id="demobar" hidden></div>
    <div class="head">
      <div class="headmain">
        <div class="topline">
          <span class="wordmark">ATP</span>
          <span class="divider-v"></span>
          <span class="kicker" id="kicker"></span>
        </div>
        <h1 id="title"></h1>
        <div class="rule"></div>
      </div>
      <div class="corner">
        <img class="sponsor" id="sponsor" alt="" hidden>
        <div class="follow" id="follow" hidden>
          <span id="followQr"></span>
          <span class="u" id="followUrl"></span>
        </div>
      </div>
    </div>
    <div class="voicenote" id="voicenote" hidden></div>
    <div id="body"></div>
    <div class="takeaway">
      <div class="h">THE LINE FOR THE ROOM</div>
      <div class="b" id="takeaway"></div>
    </div>
    <div class="nav">
      <button id="prev">Previous</button>
      <button id="next" class="primary">Next</button>
      <div class="right">__FOOTER__</div>
    </div>
    <div class="voices" id="voices" hidden>
      <span class="lab">VOICE</span>
      <span id="voiceButtons"></span>
      <span class="hint" id="voiceHint"></span>
    </div>
  </div>
  <div id="printAll"></div>
</div>
<script>
// VOICES is [[key, label], ...] in display order.
// UNVOICED lists the screen ids that never change voice: they are ours, not the model's.
const DECKS = __DECKS__;
const VOICES = __VOICES__;
const UNVOICED = __UNVOICED__;
const THEMES = __THEMES__;
const DEFAULT_THEME = __DEFAULT_THEME_JS__;
const QRS = __QRS__;            // screen id -> inline SVG, one per screen, not per voice
const SPONSORS = __SPONSORS__;  // station id -> {name, src}, only for stations that have one
const FOLLOW_URL = __FOLLOW_URL__;
const DEMO_NOTICE = __DEMO_NOTICE__;
let i = 0;
let voice = "default";
const el = id => document.getElementById(id);
const screens = () => DECKS[voice] || DECKS.default;

// Themes are applied by setting the CSS variables, so one object drives the whole
// look of a screen and nothing about the layout knows which station it is on.
const VARS = {surface: "--bg", fill: "--fill", line: "--line", ink: "--ink",
              ink2: "--ink-2", ink3: "--ink-3", accent: "--brand", warn: "--warn",
              warnbg: "--warnbg", bg: "--page"};
function themeFor(id) { return THEMES[id] || DEFAULT_THEME; }
function applyTheme(id) {
  const t = themeFor(id), st = document.documentElement.style;
  for (const k in VARS) st.setProperty(VARS[k], t[k]);
}
function themeVars(id) {  // inline form, for the print view where each page differs
  const t = themeFor(id);
  return Object.keys(VARS).map(k => VARS[k] + ":" + t[k]).join(";");
}

const store = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
const load = (k, d) => { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } };

let scale = parseFloat(load("atp-scale", "")) || 0;
let presenting = load("atp-presenting", "0") === "1";

function applyMode() {
  document.documentElement.classList.toggle("presenting", presenting);
  // A saved nudge only means anything for the mode it was set in.
  document.documentElement.style.setProperty("--s", scale || (presenting ? 2 : 1));
  store("atp-presenting", presenting ? "1" : "0");
  autofit();
}

// Shrink until the screen fits the screen. A projector cannot scroll, and the takeaway
// is the last thing on every slide, so anything that overflows takes the line for the
// room with it. Skipped the moment the presenter nudges the size by hand: at that point
// they are standing in the room and know better than this does.
function autofit() {
  if (!presenting || scale) return;
  const root = document.documentElement;
  let s = 2;
  root.style.setProperty("--s", s);
  while (s > 1.15 && root.scrollHeight > window.innerHeight) {
    s = Math.round((s - 0.05) * 100) / 100;
    root.style.setProperty("--s", s);
  }
}
function nudge(delta) {
  const cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--s")) || 1;
  scale = Math.min(5, Math.max(0.6, Math.round((cur + delta) * 20) / 20));
  store("atp-scale", scale);
  applyMode();
}

function setVoice(v) {
  if (!DECKS[v]) return;
  voice = v;
  document.querySelectorAll("#voiceButtons button").forEach(b =>
    b.classList.toggle("on", b.dataset.voice === v));
  render();
}

function render() {
  const SCREENS = screens();
  const s = SCREENS[i];
  applyTheme(s.id);
  if (DEMO_NOTICE) { el("demobar").hidden = false; el("demobar").innerHTML = DEMO_NOTICE; }
  el("kicker").textContent = s.kicker.toUpperCase();
  el("title").textContent = s.title;
  el("body").innerHTML = s.body;
  el("takeaway").textContent = s.takeaway;

  const rail = el("rail");
  rail.innerHTML = "";
  SCREENS.forEach((sc, n) => {
    const seg = document.createElement("span");
    seg.title = (n + 1) + ". " + sc.title;
    seg.className = n === i ? "now" : n < i ? "done" : "";
    seg.onclick = () => { i = n; render(); };
    rail.appendChild(seg);
  });

  if (FOLLOW_URL) {
    const qr = QRS[s.id] || "";
    el("follow").hidden = false;
    el("followQr").innerHTML = qr;
    el("followUrl").textContent = FOLLOW_URL + "#" + s.id;
    el("follow").classList.toggle("noqr", !qr);
  }
  const sponsor = SPONSORS[s.id];
  el("sponsor").hidden = !sponsor;
  if (sponsor) {
    el("sponsor").src = sponsor.src;
    el("sponsor").alt = sponsor.name + ", station sponsor";
  } else {
    el("sponsor").removeAttribute("src");
    el("sponsor").alt = "";
  }
  // The address bar always points at the screen on show, so the presenter's own URL
  // is shareable mid-talk and a scanned deep link lands on the right slide.
  try { history.replaceState(null, "", "#" + s.id); } catch (e) {}
  autofit();

  el("prev").disabled = i === 0;
  el("next").disabled = i === SCREENS.length - 1;
  const unvoiced = UNVOICED.indexOf(s.id) !== -1;
  const label = (VOICES.find(v => v[0] === voice) || ["", ""])[1];
  el("voiceHint").textContent =
    unvoiced ? "this screen is ours, so it stays default"
             : "keys 1-" + VOICES.length + ", V to cycle, P to project, D for detail";

  // Say plainly why nothing changed, on the screen where nothing changed.
  const note = el("voicenote");
  if (unvoiced && voice !== "default") {
    note.hidden = false;
    note.innerHTML = "<b>" + label + " is not narrating this screen.</b> The screens about " +
      "how this was built are ours, not the model's, so they stay in one voice. " +
      "Move to any station screen and " + label + " takes over.";
  } else {
    note.hidden = true;
  }
  // Dim the buttons here too, so the control looks as inert as it is.
  document.querySelectorAll("#voiceButtons button").forEach(b => {
    b.style.opacity = unvoiced && b.dataset.voice !== "default" ? "0.45" : "";
  });
  window.scrollTo(0, 0);
}
el("prev").onclick = () => { i = Math.max(0, i - 1); render(); };
el("next").onclick = () => { i = Math.min(screens().length - 1, i + 1); render(); };

if (VOICES.length > 1) {
  el("voices").hidden = false;
  el("voiceButtons").innerHTML = VOICES.map(([k, label]) =>
    '<button data-voice="' + k + '">' + label + '</button>').join(" ");
  document.querySelectorAll("#voiceButtons button").forEach(b =>
    b.onclick = () => setVoice(b.dataset.voice));
}

document.onkeydown = ev => {
  if (ev.key.toLowerCase() === "p") { presenting = !presenting; scale = 0; applyMode(); return; }
  if (ev.key.toLowerCase() === "d") {
    document.documentElement.classList.toggle("details");
    scale = 0; applyMode(); return;
  }
  if (ev.key === "+" || ev.key === "=") { nudge(0.1); return; }
  if (ev.key === "-" || ev.key === "_") { nudge(-0.1); return; }
  if (ev.key === "ArrowRight" || ev.key === " " || ev.key === "PageDown") el("next").click();
  if (ev.key === "ArrowLeft" || ev.key === "PageUp") el("prev").click();
  if (ev.key === "Home") { i = 0; render(); }
  if (ev.key === "End") { i = screens().length - 1; render(); }
  // Voice switching is meant to happen live, mid-sentence, without losing your place.
  if (VOICES.length > 1) {
    if (ev.key.toLowerCase() === "v") {
      const n = VOICES.findIndex(v => v[0] === voice);
      setVoice(VOICES[(n + 1) % VOICES.length][0]);
    }
    const d = parseInt(ev.key, 10);
    if (d >= 1 && d <= VOICES.length) setVoice(VOICES[d - 1][0]);
  }
};
function buildPrint() {
  const SCREENS = screens();
  el("printAll").innerHTML = SCREENS.map(s =>
    '<div class="page" style="' + themeVars(s.id) + '">' +
    '<div class="topline"><span class="wordmark">ATP</span>' +
    '<span class="divider-v"></span><span class="kicker">' + s.kicker.toUpperCase() + '</span></div>' +
    '<h1>' + s.title + '</h1><div class="rule"></div>' + s.body +
    '<div class="takeaway"><div class="h">THE LINE FOR THE ROOM</div><div class="b">' +
    s.takeaway + '</div></div></div>').join("");
}
window.onbeforeprint = buildPrint;
if (location.hash === "#print") buildPrint();

// Deep link: land on the screen the QR pointed at.
function fromHash() {
  const id = decodeURIComponent(location.hash.replace(/^#/, ""));
  const n = screens().findIndex(s => s.id === id);
  if (n >= 0) i = n;
}
fromHash();
window.addEventListener("hashchange", () => { fromHash(); render(); });
window.addEventListener("resize", autofit);

applyMode();
render();
</script>
</body>
</html>
"""


DEMO_NOTICE = (
    '<b>This is a demo build, not the event.</b> Every person, company and number on '
    'these screens is invented, generated from mock transcripts to show how the format '
    'works. The workshop is on September 17, 2026 and has not happened yet. Nothing here '
    'was said by anybody.')


def render_html(decks, order, mode, generated_at, follow_url=""):
    title = "The Throne Room, ATP September 17, 2026"
    label = {"seeded": "Pre-seeded", "demo": "DEMO, invented content", "live": "Live"}[mode]
    if mode != "live":
        title += f" ({'demo' if mode == 'demo' else 'pre-seeded'})"
    footer = f"ATP &middot; {label} &middot; {generated_at}"
    voices = [[k, VOICE_LABELS.get(k, k.title())] for k in order]
    qrs = {}
    if follow_url:
        for scr in decks["default"]:
            qrs[scr["id"]] = qr_svg(f"{follow_url}#{scr['id']}")
    return (TEMPLATE
            .replace("__TITLE__", html.escape(title))
            .replace("__FOOTER__", footer)
            .replace("__DECKS__", json.dumps(decks, ensure_ascii=False, indent=1))
            .replace("__VOICES__", json.dumps(voices, ensure_ascii=False))
            .replace("__UNVOICED__", json.dumps(list(UNVOICED)))
            .replace("__QRS__", json.dumps(qrs, ensure_ascii=False))
            .replace("__SPONSORS__", json.dumps(sponsor_logos(), ensure_ascii=False))
            .replace("__FOLLOW_URL__", json.dumps(follow_url))
            .replace("__DEMO_NOTICE__", json.dumps(DEMO_NOTICE if mode == "demo" else ""))
            .replace("__THEMES__", json.dumps(THEMES, ensure_ascii=False))
            .replace("__DEFAULT_THEME_JS__", json.dumps(DEFAULT_THEME, ensure_ascii=False)))


# --------------------------------------------------------------------------- payload loading

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_json(raw):
    """Pull a JSON object out of model output that may be fenced or have chatter around it."""
    raw = raw.strip()
    if not raw:
        raise ValidationError("model returned nothing at all")
    for candidate in ([m.group(1) for m in FENCE.finditer(raw)] + [raw]):
        candidate = candidate.strip()
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        start, end = candidate.find("{"), candidate.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(candidate[start:end + 1])
            except json.JSONDecodeError:
                continue
    raise ValidationError("could not find valid JSON in the model output")


def main():
    ap = argparse.ArgumentParser(description="Build the Throne Room deck from a JSON payload.")
    ap.add_argument("--payload", required=True, help="JSON payload file, or - for stdin")
    ap.add_argument("--out", required=True, help="output .html path")
    ap.add_argument("--mode", choices=["live", "seeded", "demo"], default="live")
    ap.add_argument("--voice", action="append", default=[], metavar="NAME=PATH",
                    help="a character-voice payload; repeatable. Same schema, same validation.")
    ap.add_argument("--follow-url", default=DEFAULT_FOLLOW_URL,
                    help="base URL of the published deck; each screen shows a QR to its own "
                         "anchor so the room can follow along. Empty string disables it.")
    ap.add_argument("--check", action="store_true",
                    help="validate the payload and exit; write nothing")
    ap.add_argument("--engine", default="",
                    help="what produced this payload, shown in the deck's provenance note")
    ap.add_argument("--sources", required=True,
                    help="ground truth from disk, e.g. sky-city=transcript,swamp-planet=fallback,...")
    args = ap.parse_args()

    sources = {}
    for pair in args.sources.split(","):
        sid, _, kind = pair.strip().partition("=")
        if sid not in STATION_IDS or kind not in ("transcript", "fallback"):
            print(f"REJECTED: --sources entry {pair!r} is not <station-id>=transcript|fallback",
                  file=sys.stderr)
            return 2
        sources[sid] = kind
    if set(sources) != set(STATION_IDS):
        print(f"REJECTED: --sources must cover all five stations, got {sorted(sources)}",
              file=sys.stderr)
        return 2

    raw = sys.stdin.read() if args.payload == "-" else pathlib.Path(args.payload).read_text()
    out = pathlib.Path(args.out)

    try:
        data = validate(extract_json(raw), sources)
    except ValidationError as exc:
        print(f"REJECTED: {exc}", file=sys.stderr)
        if args.check:
            return 2
        if out.exists():
            print(f"REJECTED: {out} left untouched. The previous deck still stands.", file=sys.stderr)
        else:
            print(f"REJECTED: no deck at {out} to fall back to. Run seed.sh.", file=sys.stderr)
        return 2

    if args.check:
        return 0

    over, total = reference_report(data)
    if over:
        detail = ", ".join(f"{sid} ({n})" for sid, n in over)
        print(f"NOTE: film quote on a screen: {detail}. "
              f"{total} in the deck overall. The brief asks for none; "
              f"cut them before presenting.", file=sys.stderr)

    for warning in CLAMPED:
        print(f"CLAMPED: {warning}", file=sys.stderr)

    failures = check_themes()
    if failures:
        for f in failures:
            print(f"REJECTED: contrast: {f}", file=sys.stderr)
        print("REJECTED: fix THEMES in build_deck.py. Nothing was written.", file=sys.stderr)
        return 2

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    decks = {"default": build(data, args.mode, generated_at, args.engine)}
    order = ["default"]

    # A voice is just another payload. It goes through the identical validator, and a
    # voice that fails is dropped rather than taking the deck down with it: the default
    # version is the deck, and the voices are a party trick layered on top of it.
    for spec in args.voice:
        name, _, path = spec.partition("=")
        name = name.strip().lower()
        if not name or not path:
            print(f"REJECTED: --voice {spec!r} is not NAME=PATH", file=sys.stderr)
            return 2
        try:
            vdata = validate(extract_json(pathlib.Path(path).read_text()), sources)
        except (ValidationError, OSError) as exc:
            print(f"DROPPED voice {name}: {exc}", file=sys.stderr)
            continue
        div = voice_divergence(data, vdata)
        if div < 0.6:
            print(f"WARNING voice {name}: only {div:.0%} of fields were actually rewritten. "
                  f"This reads as the default deck with a few words moved, which is not "
                  f"worth a button. Strengthen voices/{name}.md and re-run.", file=sys.stderr)
        lost = numbers_lost(data, vdata)
        if lost:
            print(f"WARNING voice {name}: these figures are in the default deck but not "
                  f"in this voice: {', '.join(lost)}. Check the slides before presenting it.",
                  file=sys.stderr)
        decks[name] = build(vdata, args.mode, generated_at, args.engine)
        order.append(name)

    screens = decks["default"]

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.with_suffix(out.suffix + ".prev").write_text(out.read_text())
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(render_html(decks, order, args.mode, generated_at, args.follow_url))
    tmp.replace(out)

    live = sum(1 for s in data["stations"] if s["source"] == "transcript")
    print(f"Deck written to {out}")
    print(f"  {len(screens)} screens, {live}/5 stations from a real transcript, mode={args.mode}")
    if live < 5:
        fb = [s["name"] for s in data["stations"] if s["source"] == "fallback"]
        print(f"  flagged as fallback on screen: {', '.join(fb)}")
    if CLAMPED:
        print(f"  {len(CLAMPED)} field(s) trimmed to fit the layout")
    if len(order) > 1:
        print(f"  voices: {', '.join(order[1:])} (press 1-{len(order)} or V while presenting)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
