# Asteroid Field: Question List and Seeded Answers

**Theme:** Compliance, legal, and security
**Station pilot:** Dante Jackson, Chief Executive Officer, Serket-Tech Security
**Status:** draft, 2026-09-11

"Very dangerous. We should stay away from it." And then you fly straight through anyway, because turning back wasn't actually an option. This station is about the compliance, legal, and security review everyone dreaded and went through anyway: what it actually caught, and what it cost to go around it instead. Roughly eight questions, more than we will get through, which is the point. The seeded answers below are Fleet Command's pre-written guesses at what this room is likely to say. They exist only as the fallback if this station's recording fails. Nobody has said any of this yet.

## Q1. What did Legal ask you about your AI system that you genuinely could not answer?

*Seeded likely answer:* Where the training data came from, and whether the output can be explained to a regulator in plain language.

## Q2. Has a compliance or security requirement ever killed an AI use case outright?

*Seeded likely answer:* Yes, usually where a human decision has to be explainable and the model cannot be made to explain itself, or where a security review found a control that simply didn't exist yet.

## Q3. Who actually signs off that an AI decision, or an AI vendor, is safe enough to put in front of a customer?

*Seeded likely answer:* Nobody wants to. That vacuum stalls more work than any technical limit in the building.

## Q4. Have you tried to put an AI vendor through your normal security review, and what happened?

*Seeded likely answer:* Yes, and the review process wasn't built for a system whose behavior changes without a release, so it either passed something it shouldn't have or stalled indefinitely.

## Q5. What's your actual exposure if that vendor is breached and your prompts are sitting in their logs?

*Seeded likely answer:* Larger than assumed. Prompts routinely carry customer data nobody classified as sensitive in the first place.

## Q6. What did you have to add after the fact that nobody scoped up front: audit logs, human review, explainability, a security control?

*Seeded likely answer:* Usually more than one of those, discovered separately, each one treated as a surprise instead of a known cost of doing this at all.

## Q7. Are you regulated, and did your regulator have a formal position on AI yet?

*Seeded likely answer:* Often no formal position at all, which is worse than a strict rule, because you cannot design to a position that doesn't exist.

## Q8. What would you tell someone to do in week one, to avoid the compliance and security problem you had?

*Seeded likely answer:* Bring Legal and Security into the design conversation, not the review at the end. Both are cheaper as a constraint up front than as a veto later.
