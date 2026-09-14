#!/usr/bin/env python3
"""A deterministic stand-in for the `claude` CLI, so the rehearsal can run the whole
pipeline hundreds of times without spending tokens or waiting on a network.

It reads the same prompt the real model would get, works out which stations are on a
transcript and which are on a fallback, and emits schema-valid JSON. Behaviour is
selected by STUB_MODE so the harness can rehearse the failure paths too:

  good      valid JSON, correct sources                  (the happy path)
  fenced    valid JSON wrapped in ```json plus chatter    (what models actually do)
  garbage   an apology, no JSON at all
  badschema JSON that is well formed but breaks the rules (a dropped station)
  liar      marks a fallback station as a transcript      (the dangerous one)
  fail      exits nonzero, as a crashed or rate-limited CLI would
"""
import json, os, re, sys, time

# Which of the two hedged paths are we standing in for? synthesize.sh passes --model
# only for the standby, so an empty or non-haiku model is the primary.
MODEL = os.environ.get("STUB_MODEL", "")
LANE = "FAST" if "haiku" in MODEL.lower() else "PRIMARY"

# STUB_MODE still sets both lanes at once, for the scenarios that don't care.
# STUB_MODE_PRIMARY / STUB_MODE_FAST override per lane, and the DELAY pair fakes
# latency so the deadline logic can actually be rehearsed.
MODE = os.environ.get(f"STUB_MODE_{LANE}") or os.environ.get("STUB_MODE", "good")
DELAY = float(os.environ.get(f"STUB_DELAY_{LANE}", "0") or 0)
if DELAY:
    time.sleep(DELAY)

prompt = " ".join(sys.argv[1:]) or sys.stdin.read()

# Keep a copy of what the model was actually handed, so a scenario can assert on the
# input rather than on the stub's canned output. The stub ignores the prompt by design,
# which means anything about how the prompt was assembled is otherwise untestable.
# Appended, because both hedged lanes write to the same file.
if os.environ.get("STUB_SAVE_PROMPT"):
    with open(os.environ["STUB_SAVE_PROMPT"], "a") as fh:
        fh.write(prompt)

# A voice pass is a different job: it gets an already-validated payload back and
# rewrites the prose. The stub fakes that by tagging every text field, which is enough
# for the harness to prove the deck really is carrying separate content per voice.
if "# Voice Brief" in prompt:
    voice = "unknown"
    m = re.search(r"^## The voice\s*\n+#\s*(.+)$", prompt, re.M)
    if m:
        voice = m.group(1).strip()
    if os.environ.get("STUB_VOICE_FAIL", "") and voice.lower().startswith(
            tuple(v.strip().lower() for v in os.environ["STUB_VOICE_FAIL"].split(",") if v.strip())):
        print("I'm afraid I can't do that.")
        sys.exit(0)
    body = json.loads(prompt[prompt.rindex("{"):prompt.rindex("}") + 1]
                      if False else re.search(r"(\{[\s\S]*\})\s*$", prompt).group(1))
    tag = f"[{voice}]"
    vague = os.environ.get("STUB_VOICE_VAGUE", "") == "1"
    timid = os.environ.get("STUB_VOICE_TIMID", "") == "1"
    seen = [0]
    def rev(t):
        if vague:
            t = re.sub(r"\d(?:[\d,.]*\d)?", "several", t)
        seen[0] += 1
        # A voice that barely rewrites anything: validates fine, useless on stage.
        if timid and seen[0] % 6:
            return t
        return f"{tag} {t}"
    for st in body.get("stations", []):
        st["lede"] = rev(st["lede"]); st["takeaway"] = rev(st["takeaway"])
        for pt in st["points"]:
            pt["t"] = rev(pt["t"]); pt["d"] = rev(pt["d"])
    for pt in body.get("patterns", []):
        pt["t"] = rev(pt["t"]); pt["d"] = rev(pt["d"])
    body["closing_line"] = rev(body["closing_line"])
    print(json.dumps(body, indent=2))
    sys.exit(0)

if MODE == "fail":
    print("Error: API request failed after 3 retries (rate_limit_error)", file=sys.stderr)
    sys.exit(1)

if MODE == "garbage":
    print("I wasn't able to find enough detail in those transcripts to summarise them "
          "confidently. Could you share more context about what each station covered?")
    sys.exit(0)

blocks = re.split(r"^## Station: ", prompt, flags=re.M)[1:]
sources = {}
for b in blocks:
    sid = b.split("\n", 1)[0].strip()
    sources[sid] = "fallback" if "Source: FALLBACK" in b.split("\n\n")[0] else "transcript"

CONTENT = {
 "sky-city": ("Every story in this room was the same shape: the demo was honest about the tool and silent about the conditions.", [
   ("A demo on eight sample invoices, against 400,000 a month", "One attendee's vendor demoed document extraction on eight clean invoices. Production is roughly 400,000 a month, about a third of them scanned faxes, which never appeared in the evaluation."),
   ("The rate limit in the contract was a shared pool", "60 requests per second was written into the contract. It was 60 across every customer in the region. Monday mornings delivered about 11."),
   ("A silent model swap cut accuracy from 94% to 71%", "Pushed on a Thursday with no notice, found when a customer called. Version pinning existed only on a tier costing four times as much."),
   ("$40,000 to export your own documents", "One attendee is locked into a proprietary JSON dialect and was quoted a services engagement to get their own data back out."),
   ("The abstraction layer argument has an answer now", "Five months to build one, then a vendor swap in three weeks. The people who skipped it are the ones quoting exit fees."),
 ], "Read the contract for the rate limit, the version pin, and the export clause. Everything else is negotiable later."),
 "swamp-planet": ("Nobody in this room found a data problem. They found that nobody owned the data, and the problems followed from that.", [
   ("A four-value column with 31 values in production", "Including an empty string with a space in it, about 8% of rows, meaning unknown. The documentation has said four values for years."),
   ("190,000 duplicate customers from a merge that ran twice", "Dedupe keyed on email, so anyone who changed jobs became two people. The 2019 acquisition was merged, then merged again."),
   ("A temporary filter that is now load-bearing", "Drops any record whose state field isn't two characters, about 4% of rows, in place 18 months. Downstream reports are now tuned to the filtered volume."),
   ("400 customers told their order would arrive same-day", "A lead time field defaulting to zero for a whole product category. The system worked exactly as designed and the output looked completely normal for six weeks."),
   ("The owner of every broken source left in 2021", "What remains is a Confluence page from 2019 and a Slack channel with four people in it."),
 ], "An outage is loud. Bad data is quiet, and it is quiet for six weeks."),
 "ice-planet": ("This room could not name a technical blocker. Every stall was a person nobody had appointed.", [
   ("Eleven in flight, zero in production, two years in", "And not one of the eleven has been cancelled. Another attendee reported nineteen started against two live, one of which was described as barely alive."),
   ("Ninety percent done for fourteen months", "Every status report says ninety percent. Closing it would mean writing down that it failed, and its leader has since been promoted."),
   ("$11,000 a month in idle endpoints, and that is not the real cost", "The real cost is that the graveyard blocks approval for anything new. Six open projects is the reason there is no seventh."),
   ("The last mile is somebody else's software", "The model is fine. Getting it in front of a nurse, inside the tool the nurse already uses, needs an integration nobody scoped and a vendor with no interest."),
   ("The whole list is two items, neither technical", "A named production owner with budget, and one executive willing to accept the risk in writing."),
 ], "Nothing here is stuck on the model. It is stuck on nobody being willing to sign."),
 "snow-monster-cave": ("The costs that hurt were not on any dashboard, and the security review passed a system it was never built to evaluate.", [
   ("$40,000 budgeted, $310,000 spent, because of retries", "The year's inference budget went in March. Three attempts with no backoff, and every failed call billed."),
   ("The expensive part was two MLOps engineers", "About $400,000 fully loaded, unplanned, mostly doing monitoring and evaluation. Token spend is on a dashboard; headcount is in a different budget and nobody adds them together."),
   ("600 pastes a month into unapproved tools, from 900 people", "Found by running DLP against outbound traffic. Separately, a full customer contract turned up in a consumer chatbot, disclosed by the employee at an all-hands as a productivity tip."),
   ("Blocking made visibility worse", "Shadow usage moved to personal phones within a week. The room that sanctioned one good tool instead can still see most of its usage."),
   ("Prompts are an unclassified data store", "They contain account numbers because the workflow puts them there, and they appear in no data inventory. One security review passed a vendor outright, because the questionnaire assumes software changes when you deploy it."),
 ], "You cannot govern what you cannot see, and most rooms bought capability for two years before visibility."),
 "asteroid-field": ("Legal was not the obstacle in this room. Legal was the question nobody asked until month six.", [
   ("Nine months spent making a reason out of a score", "Automated adverse action requires a specific reason. The model produced a score. Legal was right, the answer was in the regulation the whole time, and nobody read it until month six."),
   ("An eleven-page proposal became six unscoped deliverables", "Audit logging, human review, an explainability report, a bias audit, a retention policy, a model card. Each arrived separately, each as a surprise."),
   ("A human in the loop approving 400 recommendations a day", "One attendee's phrase for it: that is not a control, that is a signature."),
   ("Nobody will sign that a decision is defensible", "A year of asking, and every executive points at another one. This vacuum stalls more work than any technical limit in the building."),
   ("No regulatory position is worse than a strict one", "If they said no, you could plan. Instead you are building to your own guess about what they will think in two years."),
 ], "Legal is cheap as a constraint in week one and ruinous as a veto in month nine."),
}

PATTERNS = [
  ("The failure was almost never the model", "Sky City lost accuracy to a vendor's release schedule, Swamp Planet to a default of zero, Ice Planet to an unfilled job, Asteroid Field to an unread regulation. Four rooms, four failures, no model defect."),
  ("Nobody owns the thing that broke", "The data source owner left in 2021. The production owner was never appointed. Nobody will sign that a decision is defensible. The 2am pager belongs to you and not the vendor."),
  ("Quiet wrong answers beat loud failures for damage", "Six weeks of same-day delivery dates, six weeks of degraded extraction, six hundred pastes a month. Every one of them looked exactly like normal operation."),
  ("The budget was written against the demo", "Zero for data cleanup that turned out to be most of the work, $40k for inference that ran to $310k, nothing for the two engineers, nothing for six compliance deliverables."),
  ("Contracts and reviews assume software that stands still", "Version pinning behind a paywall, export quoted at $40,000, and a security questionnaire with no question that catches a system changing on the vendor's schedule."),
]

payload = {"stations": [], "patterns": [{"t": t, "d": d} for t, d in PATTERNS[:5]],
           "closing_line": "Nobody in this building had a model problem. Every one of you has an ownership problem wearing a model costume."}

order = ["sky-city", "swamp-planet", "ice-planet", "snow-monster-cave", "asteroid-field"]
for sid in order:
    if sid not in sources:
        continue
    lede, pts, take = CONTENT[sid]
    src = sources[sid]
    if MODE == "liar":
        src = "transcript"
    if src == "fallback":
        lede = ("No recording survived this station, so what follows is the agenda its pilot "
                "prepared rather than what the room said.")
        pts = [(t, "Expected from the question list, not reported from the room: "
                   + d.split(". ")[0].rstrip(".") + ".")
               for t, d in pts[:3]]
        take = "This station's real answers are still on a laptop somewhere. Treat this as the agenda, not the outcome."
    payload["stations"].append({
        "id": sid, "source": src, "lede": lede,
        "points": [{"t": t, "d": d} for t, d in pts],
        "takeaway": take,
    })

if MODE == "badschema":
    payload["stations"] = payload["stations"][:4]

# Two film quotes crammed onto one screen, which is the drift the counter exists to catch.
if os.environ.get("STUB_OVERDO_REFS", "") == "1" and payload["stations"]:
    st = payload["stations"][0]
    st["lede"] = "Never tell me the odds, and it's a trap. " + st["lede"]

body = json.dumps(payload, indent=2)
if MODE == "fenced":
    print("Sure. Here's the synthesis across all five stations:\n")
    print("```json"); print(body); print("```")
    print("\nLet me know if you'd like the cross-cutting section expanded.")
else:
    print(body)
