# Snow Monster Cave: Question List and Seeded Answers

**Theme:** Dev
**Station pilot:** Michael Park, CIO, Infor
**Status:** draft, 2026-09-11

Nobody wants to be the one left hanging upside down in the cave. This station is about what's actually happening inside the build: the testing, the on-call, the ownership decisions nobody wrote down, and the engineer who ends up holding all of it when something breaks. Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What's genuinely different about testing and code review for an AI feature versus a normal feature at your shop?

*Seeded likely answer:* Nondeterministic output breaks the usual pass/fail test suite, so most shops end up with a smaller, hand-checked eval set that a person reviews instead of CI, which is slower and gets skipped under deadline pressure.

## Q2. What's a change that passed every test you had and still broke behavior in production?

*Seeded likely answer:* A prompt or model version bump that looked fine against the eval set and shifted tone or accuracy at real volume, caught by a user complaint before any dashboard flagged it.

## Q3. Who's actually on call when the AI feature misbehaves at 2am, and did they know that was part of the job when they signed up?

*Seeded likely answer:* Usually the one or two engineers who built it, informally, because it never went through the process that assigns a new service a real on-call rotation.

## Q4. What skill was missing on your engineering team when this started, and how did you actually close the gap?

*Seeded likely answer:* Nobody had run an eval pipeline before. Closed by pulling in one person who had done it elsewhere, not by training the existing team first.

## Q5. How much of what you call "your AI feature" is genuinely your code, versus a thin wrapper around someone else's API?

*Seeded likely answer:* Thinner than leadership assumes. Most of the actual behavior lives in a prompt and a vendor's model, and the owned code is plumbing around both.

## Q6. What broke because two teams each assumed they owned the same piece of AI behavior?

*Seeded likely answer:* Two features quietly shared a prompt template, and one team's fix for their own use case silently changed the other team's output.

## Q7. How do you roll back a system whose "code" is partly a prompt and partly a model version you don't control?

*Seeded likely answer:* You can pin the model and revert the prompt, but you can't force the vendor's underlying weights back, so a rollback is sometimes only a partial fix.

## Q8. What would you tell a dev team about to build their first real AI feature, about what actually eats the time?

*Seeded likely answer:* Not the model integration. The eval set, the on-call plan, and deciding who owns it after the person who built it moves on.
