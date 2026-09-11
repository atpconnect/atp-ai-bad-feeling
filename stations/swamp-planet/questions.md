# Swamp Planet: Question List and Seeded Answers

**Theme:** Technical debt and data quality issues
**Station pilot:** Michael Muncy, CTO, Aveanna
**Status:** draft, 2026-09-11

"That is why you fail." Yoda said it watching the X-wing sink into the swamp, because nobody had dealt with what was underneath it. This station is about the swamp under every AI project: the data nobody cleaned up, the schema nobody updated, the owner who left. Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What did you discover about your data the first time an AI system actually tried to use it?

*Seeded likely answer:* That the documented schema and the real contents had diverged years earlier, and everyone downstream had quietly been working around it the whole time.

## Q2. How much of your AI project turned into a data cleanup project, in percentage terms?

*Seeded likely answer:* Most of it. Seventy to eighty percent of the effort is the commonly quoted split, and none of it was in the original budget.

## Q3. Where is your worst data, and can you name who owns it today?

*Seeded likely answer:* Usually customer records tangled by a merger or acquisition, owned by nobody since the one person who understood them left the company.

## Q4. Did you fix the underlying data or build around it, and what has that workaround cost you since?

*Seeded likely answer:* Built around it, because the deadline was real and the cleanup was never scoped. The workaround is now something the business quietly depends on.

## Q5. What broke downstream that nobody knew depended on the thing you changed?

*Seeded likely answer:* A report finance uses for board reporting, and it took about three weeks for anyone to notice the numbers had shifted.

## Q6. How do you explain a data quality problem to an executive who just watched a flawless demo?

*Seeded likely answer:* Badly. The demo ran on the clean subset, and the gap between that and production is invisible from the executive's seat.

## Q7. Has an AI system ever confidently given a customer a wrong answer because the data underneath it was bad?

*Seeded likely answer:* Yes, and it did more damage than an outage would have, because nobody noticed for weeks.

## Q8. If someone on your team is about to start an AI project Monday, what's the one thing you'd tell them to do with their data first?

*Seeded likely answer:* Profile it before you promise anything to anyone. An honest audit up front is cheaper than finding out the truth in front of a customer.
