# Swamp Planet: Question List and Seeded Answers

**Theme:** Technical debt and data quality issues
**Station pilot:** Michael Muncy, CTO, Aveanna Healthcare
**Status:** draft, 2026-09-11

The ship sank because nobody had dealt with what was underneath it. This station is about the swamp under every AI project: the data nobody cleaned up, the schema nobody updated, the owner who left, and the pilot that became production without anyone rebuilding it. Roughly nine questions, more than we will get through, which is the point. Each question has a *Run it* line: the mechanic for getting twenty-five people into it rather than three. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What did you discover about your data the first time an AI system actually tried to use it?

*Run it:* Round the room. One word each for the state of your data. Then two or three stories.

*Seeded likely answer:* That the documented schema and the real contents had diverged years earlier, and everyone downstream had quietly been working around it the whole time.

## Q2. If you can't answer "where does my data flow today," you probably can't fix your data problems. How many of you actually know the map of your data landscape, and what would knowing it change for you?

*Run it:* Hands up: who could actually draw the map, start to finish, right now. Count out loud, expect it to be small. Then: for the hands that stayed down, what would knowing it change?

*Seeded likely answer:* Almost no hands. The map lives in three people's heads and one out-of-date diagram nobody trusts. Knowing it would mostly change where people stop being afraid to touch something, because right now nobody changes a pipeline without tracing it by hand first.

## Q3. How much of your AI project turned into a data cleanup project, in percentage terms?

*Run it:* Round the room, a percentage each. Say the range out loud. Then: was any of it in the budget?

*Seeded likely answer:* Most of it. Seventy to eighty percent of the effort is the commonly quoted split, and none of it was in the original budget.

## Q4. Where is your worst data, and does anyone actually own it today?

*Run it:* Hands up: who can name an owner for their worst data. Count out loud. Then: what happened when the last person who understood it left?

*Seeded likely answer:* Usually customer records tangled by a merger or acquisition, owned by nobody since the one person who understood them left the company.

## Q5. Did you fix the underlying data or build around it, and what has that workaround cost you since?

*Run it:* Split the room: fixed it versus built around it. One story from each side.

*Seeded likely answer:* Built around it, because the deadline was real and the cleanup was never scoped. The workaround is now something the business quietly depends on.

## Q6. What broke downstream that nobody knew depended on the thing you changed?

*Run it:* Hands up. Then: how long before anyone noticed, and who noticed?

*Seeded likely answer:* A report finance uses for board reporting, and it took about three weeks for anyone to notice the numbers had shifted.

## Q7. Which pilot went to production without ever being rebuilt, and what is holding it up now?

*Run it:* Hands up: who has one running right now. Then: what is it actually running on, and who is the one person it depends on?

*Seeded likely answer:* A notebook, a script on one person's machine, or a prompt in a vendor console, running a real business process. Held up by the person who wrote it, and nothing else.

## Q8. When bad data produced a confidently wrong answer, did you catch it before or after a customer did, and how?

*Run it:* Hands: before versus after. Then the how, from each side.

*Seeded likely answer:* After, more often than anyone will admit, and noticed by a customer or someone downstream rather than by any monitor. Silence was the failure mode; an outage would have been louder.

## Q9. If someone on your team is about to start an AI project Monday, what's the one thing you'd tell them to do with their data first?

*Run it:* The closer. Ask it at the five-minute warning no matter where you are. Round the room, one thing each.

*Seeded likely answer:* Profile it before you promise anything to anyone. An honest audit up front is cheaper than finding out the truth in front of a customer.
