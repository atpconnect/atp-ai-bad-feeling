# The Throne Room

The closeout session. This is where the five stations stop being five separate stories and start being one picture.

Yavin 4, at the end. Everyone who flew the battle in a different ship, in different squadrons, seeing only their own slice of it, back in one room together to find out what actually happened. That's this room, and it's why the medals get handed out at the end rather than the beginning.

`presentation.html` lands here: one self-contained file, no network, arrow keys or Next to move, and a QR code back to this repo on the way out.

Press **P** for projector mode, which sizes itself to the screen it is on. Every screen also carries a QR to its own anchor on the published copy, so anyone in the room can scan mid-talk and land on that exact screen with the full detail the projector cannot show:

**https://atpconnect.github.io/atp-ai-bad-feeling/closeout/presentation.html**

That URL serves whatever deck was last committed here, so it is live from the moment the pre-seeded version is pushed and improves as real transcripts land.

A first version is built days before the event by [`tools/synthesize-closeout/seed.sh`](../tools/synthesize-closeout/) from the station question lists alone, so a presentable deck exists before anyone speaks. It is rebuilt in the gap after the stations wrap, from whatever transcripts actually arrived, and any station still running on its question list is labelled as such on its own slide.

Fleet Command drives it live and adapts. It is a set of talking points that happens to be shaped like slides, not a script.
