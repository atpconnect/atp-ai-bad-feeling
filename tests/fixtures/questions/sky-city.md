# Sky City: Question List and Seeded Answers

**Theme:** Infrastructure and integration challenges with third-party tools
**Station pilot:** Dana Whitfield, VP Platform Engineering, Meridian Freight
**Status:** final, sent to Fleet Command 2026-09-15

Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. Which third-party AI tool did you integrate first, and what did the vendor's demo not tell you?

*Seeded likely answer:* Expect the demo to have run on clean sample data with a single tenant. The gap shows up at real volume and with real permissions.

## Q2. Where did the integration actually break: auth, rate limits, data format, or latency?

*Seeded likely answer:* Likely rate limits and auth token lifetime. Vendors size for pilots, not for production concurrency.

## Q3. How long between signing the contract and having anything in production?

*Seeded likely answer:* Six to nine months is the common answer, against a sales cycle that promised weeks.

## Q4. What happened the first time the vendor changed their API or their model version?

*Seeded likely answer:* Silent behavior change with no version pinning available, and output quality moving underneath a system nobody had regression tests for.

## Q5. Who owns the integration when it breaks at 2am, you or the vendor?

*Seeded likely answer:* You do. The SLA covers their uptime, not your workflow.

## Q6. Did you build an abstraction layer, and do you regret the answer either way?

*Seeded likely answer:* Split room. The people who built one spent months on it; the people who didn't are now locked in.

## Q7. What does the vendor's roadmap have to do with your roadmap?

*Seeded likely answer:* Nothing, and that is the problem. Features you depend on get deprecated on their schedule.

## Q8. If you were starting over Monday, what would you refuse to sign?

*Seeded likely answer:* Anything without model version pinning, an exit clause, and data export in a format you can actually read.
