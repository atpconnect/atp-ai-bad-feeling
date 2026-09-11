# Your AI Program Has a Bad Feeling About This

Public archive for the ATP event "Your AI Program Has a Bad Feeling About This." It's an interactive workshop on why enterprise AI initiatives fail, run as the honest, hands-on debrief nobody runs at their own company.

- **Date:** September 17, 2026, 6:00 to 8:00 PM
- **Location:** Social House Roswell, 1098 Green St, Roswell, GA 30075
- **Details / registration:** https://atpconnect.org/events/your-ai-program-has-a-bad-feeling-about-this/
- **Event Council:** Scott Harris (One Inc, ATP Finance Chair), Tom Lasswell (DC BLOX, ATP Director of Technology), John Slaughter (Alliant Health, ATP Executive Advisory Board)
- **Fleet Command:** John Trainor (President, Four Technologies, ATP Executive Advisory Board)

<p align="center"><img src="assets/repo-qr-code.png" alt="QR code linking to this repo" width="200"></p>

Scan the QR code above to come back to this repo after the event. It's also displayed at the event itself, where you'll find the station transcripts and the closeout session talking points.

## Format

Attendees split into five themed stations (about 25 people each), each covering a distinct way enterprise AI programs go wrong:

| Station | Theme | Sponsor |
|---|---|---|
| [Sky City](stations/sky-city/) | Infrastructure and integration challenges with third-party tools | |
| [Swamp Planet](stations/swamp-planet/) | Technical debt and data quality issues | [LogicSpree](https://www.logicspree.com/) |
| [Ice Planet](stations/ice-planet/) | Use cases, costs, and scope creep | [Griffin](https://griffinglobaltech.com/) |
| [Snow Monster Cave](stations/snow-monster-cave/) | Development | [Allata](https://www.allata.com/) |
| [Asteroid Field](stations/asteroid-field/) | Compliance, legal, and security | |

Each station is a guided discussion, not a talk: the station pilot puts a list of roughly eight questions to their station and the room answers. Fleet Command hosts, records, and transcribes each one via an independent Teams meeting, not the pilot, and every station has a Flight Engineer whose only job is to watch that the capture is actually working. No one in any single station gets the full picture. That's the point of what comes next.

Immediately afterward, the group reassembles for **the Throne Room**, the closeout session. Everyone who spent the evening in a different room, back together at the end. It's the one vantage point that actually sees the patterns across all five stations at once, distilled into shared talking points. See [`closeout/`](closeout/).

This repo documents the full method, not just the output. That includes [how the Throne Room deck was actually synthesized](tools/synthesize-closeout/) from the five station transcripts in the few minutes between sessions ending and the group reassembling, and [the rehearsal harness](tests/) we used to run the whole night end to end beforehand, including every way it could fail.

## Who is running it

<img src="assets/people/john-trainor.jpg" alt="John Trainor" width="160" align="right">

**Fleet Command: John Trainor**, President of Four Technologies, a rapidly growing AI-first FinTech company. His previous roles include CTO of Wahoo Fitness and CIO of Aaron's, and he holds an Electrical Engineering degree from Georgia Tech. John has been an active member of ATP for over 15 years and has led a number of technology industry organizations in Atlanta. An avid endurance athlete, he runs marathons with his wife Heather, but his favorite thing to do is spend time with his two grandchildren.

On the night he hosts, records, and transcribes all five stations, runs the closing synthesis, and presents the Throne Room.

<br clear="all">

**Station pilots**, each running one room as a guided discussion. Full bios are in each station's README.

| Station | Pilot |
|---|---|
| [Sky City](stations/sky-city/) | Dorren Schmitt, PhD, VP of IT Strategy and Innovation, The Weather Channel and Allen Media Group |
| [Swamp Planet](stations/swamp-planet/) | Michael Muncy, CTO, Aveanna |
| [Ice Planet](stations/ice-planet/) | Mat Mathews, Chief Information Officer, Fortrex |
| [Snow Monster Cave](stations/snow-monster-cave/) | Mike Park, Chief Information Officer, Infor |
| [Asteroid Field](stations/asteroid-field/) | Dante Jackson, Founder and CEO, Serket-Tech Security |

## Station sponsors

<table align="center"><tr>
<td align="center" width="240"><a href="https://www.logicspree.com/"><img src="assets/sponsors/logicspree.png" alt="LogicSpree" width="220"></a><br><sub>Swamp Planet</sub></td>
<td align="center" width="240"><a href="https://griffinglobaltech.com/"><img src="assets/sponsors/griffin.png" alt="Griffin" width="220"></a><br><sub>Ice Planet</sub></td>
<td align="center" width="240"><a href="https://www.allata.com/"><img src="assets/sponsors/allata.png" alt="Allata" width="220"></a><br><sub>Snow Monster Cave</sub></td>
</tr></table>

- **Swamp Planet**, technical debt and data quality: [LogicSpree](https://www.logicspree.com/)
- **Ice Planet**, use cases, costs, and scope creep: [Griffin](https://griffinglobaltech.com/)
- **Snow Monster Cave**, development: [Allata](https://www.allata.com/)

## Take this and run it yourself

**[RUN-THIS-YOURSELF.md](RUN-THIS-YOURSELF.md)** is the transferable part: ten principles that made the closeout session reliable enough to present unreviewed in front of a hundred people, each with the code that implements it and the defect it caught, followed by how to run the event format at your own organization.

The short version, since the event is about why enterprise AI programs fail and it would be embarrassing to run it on one that does: be deterministic wherever determinism is available, never ask a model a question you can already answer, constrain the output until a machine can validate it, write the evals before the night and test the disasters, score the things you would otherwise argue about, and measure instead of estimating.

## Contents

- [`RUN-THIS-YOURSELF.md`](RUN-THIS-YOURSELF.md): the principles behind the method, and how to run it at your own organization
- [`crew-manifest.md`](crew-manifest.md): who held which role on the day, and what was still unfilled going in
- [`station-pilot-instructions.md`](station-pilot-instructions.md): what station pilots needed to prepare and run their session
- [`coordinator-checklist.md`](coordinator-checklist.md): Fleet Command's runbook for hosting, recording, and monitoring all five stations, and running the closing synthesis
- `stations/`: question list per station before the event, transcript and notes after it
- [`closeout/`](closeout/): the Throne Room, the synthesized closeout session deck, added after the event. [Read it here.](https://atpconnect.github.io/atp-ai-bad-feeling/closeout/presentation.html)
- [`tools/synthesize-closeout/`](tools/synthesize-closeout/): the tool and guiding framework used to turn the five transcripts into the closeout deck
- [`tools/intake-transcript/`](tools/intake-transcript/): files transcripts off the laptop and out of email as they arrive
- [`tools/build-deck/`](tools/build-deck/): validates the model's output and renders the deck, deterministically
- [`tests/`](tests/): the rehearsal harness we ran the night on before the night, and the four real defects it caught

## Contributing

Pull requests are welcome. Corrections to a transcript, additional context on a station's topic, or your own notes if you were in the room are all fair game. This is meant to be a living record of the event, not a frozen archive.
