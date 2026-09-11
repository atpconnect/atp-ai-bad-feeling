# Sky City: Question List and Seeded Answers

**Theme:** Infrastructure and integration challenges with third-party tools
**Station pilot:** Dorren Schmitt, VP IT Strategy and Innovation, Allen Media
**Status:** draft, 2026-09-11

Every vendor deal in this room started the same way Lando's did: negotiated in good faith, on terms that made sense at the time. This station is about the moment those terms changed underneath someone, and what it cost to find out mid-flight rather than in the contract review. Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. Which third-party AI tool did you bring in first, and what did the sales demo not show you?

*Seeded likely answer:* The demo ran on a clean slice of data with one tenant and no real load behind it. The gap showed up the first week of real traffic, not before.

## Q2. What number in the contract turned out to mean something different in production: a rate limit, a token count, a per-seat price?

*Seeded likely answer:* A shared rate limit written as if it were dedicated capacity. It read fine until three other customers were also having their busy Monday.

## Q3. When did the vendor change something, without asking, that you were depending on?

*Seeded likely answer:* A model or API version swapped in on their schedule, with no pinning option on the tier anyone had actually bought. Output quality moved and nobody had a regression test watching for it.

## Q4. Who actually gets the call at 2am when the integration is down: you, or the vendor?

*Seeded likely answer:* Almost always the customer's own team. The SLA covers the vendor's uptime, not the workflow built on top of it.

## Q5. How long did it take from signing to anything real running in production, against what you were told at the sale?

*Seeded likely answer:* Six to nine months against a sales cycle that promised weeks. The gap was integration work nobody scoped, not the model itself.

## Q6. Did you build an abstraction layer to keep switching costs low, and are you glad you did either way?

*Seeded likely answer:* Split room. The people who built one spent real months on it up front; the people who didn't are the ones quoting exit fees now.

## Q7. What would it cost you today to walk away from this vendor, in time or in dollars?

*Seeded likely answer:* A real number exists and it is uncomfortable: a services engagement to export data, months to rebuild the integration, or both.

## Q8. What line would you refuse to sign if you were negotiating this deal again Monday morning?

*Seeded likely answer:* Anything without version pinning, a real exit clause, and data export in a format the buyer controls, not the vendor.
