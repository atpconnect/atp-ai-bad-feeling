# Snow Monster Cave: Question List and Seeded Answers

**Theme:** Development
**Station pilot:** Mike Park, CIO, Infor
**Status:** draft, 2026-09-11

Nobody wants to be the one left hanging upside down in the cave. This station is about what's actually happening inside the build: the testing, the on-call, the ownership decisions nobody wrote down, and the engineer who ends up holding all of it when something breaks. Roughly eight questions, more than we will get through, which is the point. Each question has a *Run it* line: the mechanic for getting twenty-five people into it rather than three. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What did "tested" mean for the last AI feature you shipped, and who decided that was enough?

*Run it:* Round the room, one phrase each. "Vibes" is an acceptable answer; it will get a laugh and then a real one. Then: who made the call?

*Seeded likely answer:* A handful of hand-checked examples that someone on the team said looked right. Nobody formally decided it was enough; the deadline did.

## Q2. What's a change that passed every test you had and still broke behavior in production?

*Run it:* Hands up. Two stories. Then: what caught it, a dashboard or a user?

*Seeded likely answer:* A prompt or model version bump that looked fine against the eval set and shifted tone or accuracy at real volume, caught by a user complaint before any dashboard flagged it.

## Q3. Who's actually on call when the AI feature misbehaves at 2am, and did they know that was part of the job when they signed up?

*Run it:* Hands up: who has a formal on-call rotation for an AI feature. Count out loud. Then: who is really carrying it?

*Seeded likely answer:* Usually the one or two engineers who built it, informally, because it never went through the process that assigns a new service a real on-call rotation.

## Q4. What skill was missing on your engineering team when this started, and how did you actually close the gap?

*Run it:* Poll it: hired, trained, contracted, or still missing. Hands for each. Then a story from each pile that has hands.

*Seeded likely answer:* Nobody had run an eval pipeline before. Closed by pulling in one person who had done it elsewhere, not by training the existing team first.

## Q5. How much of what you call "your AI feature" is genuinely your code, versus a thin wrapper around someone else's API?

*Run it:* Round the room, a percentage each. Then: does leadership know that number?

*Seeded likely answer:* Thinner than leadership assumes. Most of the actual behavior lives in a prompt and a vendor's model, and the owned code is plumbing around both.

## Q6. Where does the prompt actually live in your shop: source control, a vendor console, someone's laptop? And what has that cost you?

*Run it:* Hands for each of the three. Count out loud. Then: the change nobody could trace.

*Seeded likely answer:* Split between a vendor console and source control, with at least one shop admitting a laptop. The cost was a change nobody could trace, made by someone who didn't know a second feature depended on the same prompt.

## Q7. When a model or prompt change goes bad, what does rolling back actually look like?

*Run it:* Hands up: who has actually rolled one back. Then: what could you revert, and what couldn't you?

*Seeded likely answer:* You can pin the model and revert the prompt, but you can't force the vendor's underlying weights back, so a rollback is sometimes only a partial fix.

## Q8. What would you tell a dev team about to build their first real AI feature, about what actually eats the time?

*Run it:* The closer. Ask it at the five-minute warning no matter where you are. Round the room, one thing each.

*Seeded likely answer:* Not the model integration. The eval set, the on-call plan, and deciding who owns it after the person who built it moves on.
