# Swamp Planet: Question List and Seeded Answers

**Theme:** Technical debt and data quality issues
**Station pilot:** Corey Boglesong, CTO, Aaron's
**Status:** final, sent to Fleet Command 2026-09-15

Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What did you discover about your data the first time an AI system tried to use it?

*Seeded likely answer:* That the documented schema and the actual contents diverged years ago, and everybody downstream had been quietly compensating.

## Q2. How much of your AI project turned out to be a data cleanup project?

*Seeded likely answer:* Most of it. The commonly quoted split is 70 to 80 percent of effort, and leadership budgeted for none of it.

## Q3. Where is your worst data, and does anyone own it?

*Seeded likely answer:* Customer records merged through an acquisition, owned by nobody since the person who understood them left.

## Q4. Did you fix the data or work around it, and what did that cost you later?

*Seeded likely answer:* Worked around it, because the deadline was real and the cleanup was not scoped. The workaround is now load-bearing.

## Q5. What broke that you did not know depended on the thing you changed?

*Seeded likely answer:* A downstream report finance uses for board reporting, discovered three weeks later.

## Q6. How do you explain a data quality problem to an executive who just saw a great demo?

*Seeded likely answer:* Badly. The demo used the clean subset, and the difference is invisible from the outside.

## Q7. Has an AI system ever confidently produced a wrong answer from bad data, in front of a customer?

*Seeded likely answer:* Yes, and it was more damaging than an outage because nobody noticed for weeks.

## Q8. What would you tell someone about to start, about their data?

*Seeded likely answer:* Profile it before you promise anything. The honest audit is cheaper than the reputational cost of finding out later.
