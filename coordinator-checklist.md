# Fleet Command Checklist, ATP Event, September 17, 2026

Fleet Command hosts and records every station's Teams meeting, monitors all five during the event, and runs the closeout synthesis in the window before the Throne Room, the closeout session. This is that role's runbook.

## Before the event

- [ ] Schedule 5 independent Teams meetings, one per station, sometime before the event. No Team or channel structure needed, just standalone calendar invites.
- [ ] For each meeting, confirm it does not require lobby admission (this account doesn't default to it, but verify per meeting).
- [ ] Send each station pilot their station's individual meeting link.
- [ ] **Book all five dry runs live during the prep meeting on Monday, September 14.** Waiting on pilots to reach out did not work: zero of five had booked by the 8th. Have your own calendar open in that meeting, get everyone to open theirs, and send the invites on the spot before anyone leaves. Slots run the 14th through the 16th.

## Dry run, mandatory, per station pilot, 15 minutes

- [ ] Join the pilot's actual meeting link with them at the scheduled test time.
- [ ] Confirm they get in with no lobby or waiting room.
- [ ] **Confirm Teams noise suppression is set to Off, not Auto** (Settings > Devices > Noise suppression). This is the setting the whole capture depends on. Auto is tuned to isolate a single voice at a desk and will strip out the room discussion.
- [ ] Have them walk a few steps away from the laptop and talk at normal volume, the way an attendee in the room will. That, not their close-up voice, is the audio that has to survive. Since the pilot is the one asking questions, their own voice was never the thing at risk.
- [ ] Confirm the laptop is theirs, that they know its password, and that they can change their own settings. A donor laptop that nobody can unlock is the most likely single point of failure on the day.
- [ ] Confirm the laptop arrives fully charged and that they're bringing the power cord, and that it won't sleep or lock mid-session. Charged in advance is the point: venue power at every station isn't guaranteed.
- [ ] Ask whether they run their own recorder or transcription service, and encourage it if they do. Confirm two things. First, **it's a completely different device**, not a second app on the laptop already running Teams: same microphone, same spot, same power and sleep and lock failures, plus a real chance the two fight over microphone access and take out the primary. Second, that they can actually export and email the file to john@johntrainor.com within minutes of their session ending. A login wall, a manual export step, or an unpredictable processing queue makes it unusable as backup. Better to know that now than to be waiting on it during the synthesis window.
- [ ] Start recording and transcription. Confirm both actually capture correctly.
- [ ] Walk them through **ending** the meeting rather than leaving it, and why.
- [ ] Note any fixes needed (mic, connection, anything) and resolve before September 17. This is the same link and setup used on the day.

## Collecting questions, the backup plan

Each station runs as a guided discussion off a list of roughly eight questions. Tom Lasswell is drafting those lists, since the pilots asked him to rather than writing their own. The question list, with likely answers pre-filled against it, is the fallback that stands in for a station whose transcript fails.

- [ ] Collect each station's question list as soon as it exists, even in draft. Save it into `stations/<name>/questions.md` in this repo.
- [ ] Chase the pilots for their final, reviewed version by **Tuesday, September 15**. Wednesday is workable. Thursday morning is the outer edge, and still fine to absorb, since integrating a late list is cheap. An absent list is not.
- [ ] Pre-fill likely answers against each station's questions and keep them in `questions.md` alongside the questions themselves. This is the actual work that makes the fallback usable, and it has to be done before the day.
- [ ] Write an `expected-transcript.md` per station: the same guess at what the room will say, at the length a room actually says it, with the numbers and the disagreements in. A question list gives the closeout an agenda to describe; this gives it something to quote. Worth doing for every station, and worth doing first for any station whose capture you are least confident about.
- [ ] Once lists start coming in, run `tools/synthesize-closeout/seed.sh`. It builds a complete, presentable deck from the question lists alone, with every station marked as a fallback. **From that moment there is always a deck**, and every later run can only improve on it. Nothing on the night can leave you standing in front of the room with nothing.
- [ ] **Commit and push that seeded deck.** `closeout/presentation.html` is generated, not tracked by default, so the published URL that every screen's QR points at does not exist until a deck is pushed. Doing it now means the follow-along link is already live and already tested days before anyone scans it, rather than depending on a push made ninety seconds before you start talking.
- [ ] Run `tests/rehearse.sh` after any change to the question lists or the tools. It rehearses the whole night, including the disasters, in about two seconds. See [`tests/README.md`](tests/README.md).

## Day before / morning of

Fleet Command's table is the cockpit for the day. It needs working Wi-Fi and reliable power, or nothing else on this list happens.

- [ ] Confirm venue Wi-Fi and power availability at Fleet Command's table (Social House Roswell). Bring a mobile hotspot too, but only as a backup. It is not the primary connection.
- [ ] Kit: laptop plus charger, hotspot plus charged battery pack, headphones, all 5 meeting links pinned or bookmarked.
- [ ] Open all 5 meetings and re-confirm no lobby is configured.
- [ ] Print the QR code (`assets/repo-qr-code.png`) as signage, large enough to scan from a few feet away, and place it prominently so attendees can find the repo after the event.
- [ ] Confirm GitHub Pages is enabled on the repo (Settings, Pages, deploy from `master` / root). Every screen of the closing deck shows a QR to its own anchor on that site so the room can follow along on their phones, and none of those links work until Pages is on. Check by loading the published URL on a phone.
- [ ] Rehearse on the actual projector at 5:00 setup: press **P**, walk to the back of the room, and confirm you can read a station screen and scan its QR. Nudge with + and - until you can.

## Arrival and setup

- [ ] **Fleet Command on site at 5:00 PM.** Station pilots are called for 5:15, which is the window for setting up their laptops, confirming noise suppression is off, and running a live test meeting on the actual venue Wi-Fi before the room fills.
- [ ] Assign the five **Flight Engineers** on arrival, one per station, and brief them (see below). These can be ATP volunteers drafted that evening. Confirm with Kyle, ATP's volunteer coordinator, that anyone assigned to Fleet Command is coordinated through him rather than reporting in two directions.
- [ ] **Cadet: William.** Fleet Command's runner for the evening, briefed on the full program and able to be pointed at any problem without further explanation. Registered through Kyle, working directly with Fleet Command.
- [ ] Tom Lasswell is day-of tech support and the backup on any laptop that misbehaves.
- [ ] Scott Harris is the timekeeper. Everything in the synthesis window below depends on the stations actually ending when they're called.

### Briefing the Flight Engineers

One per station. The pilot runs the room; the Flight Engineer watches the machine.

- [ ] Recording is running, and the **live transcript is visibly building** in Teams. This is the real tell that capture is working, and it's visible in the Teams UI without interrupting anything.
- [ ] Laptop is plugged in, awake, and unlocked. Power, sleep, and lock are the three failure modes.
- [ ] Network hasn't dropped.
- [ ] **If the station pilot brought a second device, work the room with it.** The laptop is fixed in place and straining to hear; a handheld carried toward whoever is speaking captures exactly what the primary can't. This is an active job, not a passive one. Then make sure it gets emailed to john@johntrainor.com before anyone leaves.
- [ ] If anything looks wrong, get Tom or Fleet Command. Don't try to fix it mid-discussion.

## As each station kicks off

- [ ] Click **Start recording and transcription** the moment the room settles, then leave. It keeps running without you.
- [ ] Record audio only, not video. Nobody needs the video, and audio-only measurably speeds up transcript generation, which is the whole constraint in the synthesis window.
- [ ] Mark it on the tracker below.
- [ ] At some point mid-session, quietly spot-check audio (headphones) to confirm it's actually being captured.

| Station | Flight Engineer assigned | Recording started | Audio spot-checked |
|---|---|---|---|
| Sky City | ☐ | ☐ | ☐ |
| Swamp Planet | ☐ | ☐ | ☐ |
| Ice Planet | ☐ | ☐ | ☐ |
| Snow Monster Cave | ☐ | ☐ | ☐ |
| Asteroid Field | ☐ | ☐ | ☐ |

## As each station wraps

- [ ] **Confirm the meeting was ended, not just left.** Ending the meeting is what triggers Teams to finalize the session and generate the transcript. A pilot who closes their laptop or hits Leave has not started that clock. As meeting owner, Fleet Command can end any of the five directly, so sweep all five as the sessions wrap rather than assuming.
- [ ] The transcript already lives on Fleet Command's own machine. Export it to `~/Downloads` and run `tools/intake-transcript/intake.sh`, which files it, converts the `.docx`, and prints the status of all five. It never overwrites a transcript already filed, so run it as often as you like.
- [ ] Mark it on the tracker below.

| Station | Transcript captured | Notes (e.g. fallback needed) |
|---|---|---|
| Sky City | ☐ | |
| Swamp Planet | ☐ | |
| Ice Planet | ☐ | |
| Snow Monster Cave | ☐ | |
| Asteroid Field | ☐ | |

## In the gap before the Throne Room

**Measured worst case: about 10 minutes from last station ending to a presentable deck.** Every number below was measured in rehearsal against full-length transcripts, not estimated:

- 2.5 to 5 minutes for Teams to generate a single transcript once the meeting is ended. Five minutes was the worst observed, audio-only.
- The five stations won't end simultaneously. Assume a couple of minutes of stagger, which puts the last transcript landing around 7 minutes after the first station wraps.
- **69 to 164 seconds** for the model to read every word said in the building and answer. This was budgeted at one minute until the rehearsal harness measured it. Note the spread: four runs varied more than twofold, and the slowest was on the smallest input, so this is not something you can shorten by trimming the transcripts. Plan against three minutes, not the median.
- Under a second to validate and build the deck.

That 10 minutes has to be absorbed by the run of show while the room moves back to the closeout area. **Adjust this section against the real run of show once Scott and Tom have it**, since it's the one number here that depends on somebody else's document. Re-measure any time with `REAL_MODEL=1 tests/rehearse.sh fullsize`.

- [ ] Run `tools/intake-transcript/intake.sh` one last time and read its five-station status table.
- [ ] Run `./tools/synthesize-closeout/synthesize.sh`. It fires two models in parallel: the primary gets 180 seconds, and a haiku standby answers the same question as insurance against a slow night. You do not have to do anything differently; it picks one and tells you which. Add `--no-hedge` to run a single model, which is the right call for a dry run and the wrong one tonight.
- [ ] Read its output. It says how many stations came from a real transcript, names any on a fallback, says which model wrote the deck, and names anything it trimmed. If it says the standby carried it, that is fine and the deck says so on screen.
- [ ] **If it says REJECTED, do not panic and do not re-run blindly.** The deck already on disk is untouched and presentable. Present that.
- [ ] **Commit and push the deck now, before presenting.** The QR on every screen points at the published copy, and it 404s until this is done. Pages publishes in under a minute, which is about slide three.
- [ ] Open `closeout/presentation.html` in a browser, put it on the projector, and **press P**. It sizes itself to the screen. Use + and - if the back of the room still cannot read it, and D to reveal the detail on any screen. Arrow keys to move. Fleet Command presents live, adapting rather than reading it verbatim.
- [ ] **Optional, only if the room is still settling:** re-run with `--voices` to add the character voices, then press 1 to 5 or V mid-presentation to switch narrator. This takes a few minutes and is never on the critical path, because the deck you already have stays exactly where it is until the voices are ready. If the run of show is tight, skip it: generate them the day before against the seeded deck instead and rehearse with those.

## If something fails mid-session

There are three independent layers under each station, not one:

- Recording or transcription didn't start, or stopped: rejoin and restart it. The meeting is still running. This is what the Flight Engineers are watching for.
- Teams fails entirely for a station: fall back to the pilot's second device, if they brought one, emailed to john@johntrainor.com as the session ends. Where the Flight Engineer carried it around the room, this may actually be the better capture of the two.
- No usable audio at all: the synthesis script automatically falls back to that station's `expected-transcript.md` if one exists, and to `questions.md` if not. Either way the deck flags it in a banner on that station's own slide. The station still appears, clearly marked as not sourced from a transcript, and every number on that screen is described as ours rather than the room's.
- The primary model is slow, or returns nonsense: the haiku standby has been running the same job in parallel the whole time, and its answer is used instead. The deck credits it on the provenance line. Rehearsed under `hedge-standby` and `hedge-primary-bad`.
- Both models fail, or the venue network is down: the run is rejected, nothing is overwritten, and the deck already on disk stands. Rehearsed under `garbage`, `badschema`, `crash` and `hedge-both-bad`.

## Crew manifest

- [ ] Keep [`crew-manifest.md`](crew-manifest.md) current. It's the single list of who holds which role, and its real job is making the unfilled rows obvious while there's still time to fill them.

## Approaches considered and rejected

Recorded here because the repo is meant to document the method, and because these are the first three things anyone else planning this will reach for.

- **Dedicated microphones, lapel or wireless, per station, feeding Teams.** Rejected. It means either buying gear or depending on five pilots to each own, understand, and correctly connect a mic, and on most laptops a decent mic means USB and driver roulette. The upside was real, but the format is a room discussion where the biggest win comes from disabling noise suppression, not from a better capsule near the pilot's mouth. Note the distinction from a pilot's own separate recorder, which is encouraged: the objection is to extra gear in the primary capture path, not to independent insurance sitting alongside it.
- **A phone joining the meeting as a roving handheld mic, passed around by a runner.** Rejected, and it was the most tempting one, because a passed handheld is what an audience instinctively understands. But it means two live audio sources per station, which means mute and unmute management during a discussion, crosstalk between the two feeds, and a transcript with overlapping speakers. It traded a capture problem for a coordination problem.
- **Station pilots writing their own questions.** Not so much rejected as declined by the pilots, all of whom asked for the questions to be written for them. Worth naming because the plan assumed otherwise, and the whole fallback design had to change once the question lists became a central artifact rather than a pilot's private notes.

## After the event

- [ ] Commit and push the final transcripts and the closeout draft to this repo.
