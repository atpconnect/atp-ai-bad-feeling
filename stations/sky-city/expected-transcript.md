# Sky City: Expected Transcript

**This is not a recording. Nobody has said any of this.**

Fleet Command wrote this before the event, from the question list in [`questions.md`](questions.md), as a fuller version of the seeded answers in it: what this room is likely to say, in the shape a transcript arrives in, so the closeout has something with real texture to fall back on if this station's recording fails. On the night it is replaced by `transcript.md`, which is the real one.

There are no names in it because there will not be any. The station is captured on one laptop in a loud room, so Teams attributes the whole session to the meeting host and not to the twenty-five people actually talking.

---

Sky City, September 17, 2026

Station pilot 0:14
Sky City, infrastructure and integration with third-party tools. Ground rule before we start: speak toward the laptop, because this is being recorded and the recording is the only reason any of this leaves the room. First one. Round the room, everybody, which third-party AI tool did you bring in first, and what did the sales demo not show you? Name the tool in one breath, then we will take a few stories.

Speaker 1 1:02
Contact centre summarisation. The demo was twenty calls they picked. All English, all clean audio, all under four minutes. About forty percent of our calls have two languages in them and half of those have hold music bleeding over the top. None of that was in the twenty.

Speaker 2 1:38
Document extraction, for claims. The demo ran on their sample documents, not ours. When we finally got them to run ours they asked us to send a representative sample, and what they meant by representative was the clean ones.

Speaker 3 2:11
Ours was a coding assistant, so the demo was fine, honestly. The thing the demo did not show was procurement. It took five months to buy a thing that costs thirty dollars a seat.

Station pilot 2:44
That is a real answer and it is going to come back later. Anyone else on what the demo hid?

Speaker 4 3:02
Search over our own documents. The demo indexed about two hundred files. We have eleven million. Nobody on either side of that table knew what eleven million was going to do to it, and to be fair to them, I do not think they were hiding it. They had just never seen it.

Station pilot 3:41
Second question, and this is the one I actually want the room for. What number in the contract turned out to mean something different in production? A rate limit, a token count, a per-seat price. Hands up if a number in a contract has surprised you. Okay, that is most of the room. Two stories.

Speaker 2 4:19
Per seat. We assumed a seat was a person who logs in. Their definition of a seat, and it is in there, is any individual whose data is processed by the service in a billing period. We were sized for four hundred users. We got billed against about nineteen thousand, because every customer whose claim went through it counted.

Speaker 5 4:58
Rate limit. Sixty requests a second, written like it is ours. It is a pool for the region. On the first Monday of the month we were getting eight or nine, because everybody else in the region also runs their month-end on the first Monday.

Station pilot 5:33
Anyone here sell this for a living? One or two. What do buyers misread?

Speaker 6 5:51
Availability. The uptime number is almost always the API being reachable, measured monthly, and there is usually a carve-out for capacity events. Buyers read it as the thing working. Those are not the same sentence and they are never in the same paragraph.

Station pilot 6:22
Third. When did the vendor change something, without asking, that you were depending on? Hands. Most of you. The follow-up that matters is how you found out and how long it took.

Speaker 1 6:49
They rolled the model forward on our tier on a Tuesday. Our summaries got shorter and started dropping the callback commitment. We found out nine days later from a supervisor who reads a sample every week. Not from us, not from them.

Speaker 4 7:21
Deprecation notice on an endpoint, forty-five days, sent to a shared mailbox that a person who left in March owned. We found it in a spam folder with eleven days to go.

Speaker 7 7:52
Ours moved inference to a multi-region setup to improve latency. Which it did. It also moved our data out of the region we had told Legal it would stay in, and the first we knew was a changelog entry.

Station pilot 8:24
Say that one again for the recording, because there is a whole other station in this building on exactly that.

Speaker 7 8:36
The vendor moved where the processing happened, it was an improvement from their side, and it broke a commitment we had made to our own legal team. It was a bullet point in a changelog.

Station pilot 8:58
Fourth. What did the tool assume about your environment that turned out not to be true? Four options: identity, network, data access, or who is allowed to call it. Hands for identity. That is the biggest pile by a distance, about fifteen. Network, four. Data access, seven. Who can call it, three. Story from the identity pile.

Speaker 8 9:41
It assumed a flat list of users. We are role-based, by region, and there are people who can see a record in one country and not the same record in another. The integration had two settings, on and off. We spent four months building a permissions proxy in front of a product we had already paid for.

Speaker 3 10:19
Similar, and worse. Ours over-shared for six weeks in a pilot before anyone noticed, because the pilot group was all one region and nobody had a reason to look.

Station pilot 10:47
Fifth. Round the room, one number each, months from signing to anything real in production. Just the number, I will say the range out loud at the end.

Speaker 5 11:04
Eleven.

Speaker 2 11:08
Seven.

Speaker 4 11:12
Fourteen, and it is one workflow out of the four we bought it for.

Speaker 1 11:20
Five.

Speaker 8 11:24
We signed in February and we are not live. So, call it nineteen and counting.

Speaker 3 11:33
Four, but we cheated. We gave them a copy of the data instead of integrating, which is a decision we are going to have to undo.

Station pilot 11:52
So the room is four to nineteen, and the honest middle is somewhere around nine. What were you told at the sale?

Speaker 2 12:06
Six weeks to first value.

Speaker 5 12:11
Thirty days.

Station pilot 12:18
Where did the time actually go? Not the model, I assume.

Speaker 4 12:29
Never the model. Identity, then data access reviews, then a security review, then waiting for a quarter to turn over so somebody had budget for the integration work nobody scoped.

Station pilot 12:56
Sixth. Did you build an abstraction layer to keep switching costs low? Hands if you did. About a third. One story from each side, then argue about it.

Speaker 6 13:21
We built a thin internal gateway. Three months, two engineers. We changed providers in about two weeks last quarter and it cost us almost nothing. I would do it again tomorrow.

Speaker 7 13:48
We built one too and I would not. It became its own product. It has a backlog, it has an on-call rotation, and we have never actually switched anything. We built a hedge against a risk that has not happened and we pay for it every sprint.

Speaker 6 14:19
You also have not had to find out yet.

Speaker 7 14:25
That is fair, and that is the argument.

Speaker 2 14:33
The middle answer is we did not abstract the model, we abstracted the data going in and the review step coming out. That part was worth it, because we reuse it.

Station pilot 14:58
Seventh. What would it cost you today to walk away from this vendor, in time or in dollars? Hands if you could switch inside a quarter. Six. Who has actually tried?

Speaker 4 15:24
We priced it. Eighty-five thousand dollars for a services engagement to get our own extracted data back out in a documented format, plus about ten weeks. The export is technically in the contract. The format is not.

Speaker 1 15:53
For us it is not the money. It is three hundred and ten supervisors who have built a way of working around this thing. The retraining cost is the exit cost and it is not in any contract.

Station pilot 16:22
Last one, and I am asking it now because we are at the five-minute mark. Round the room, one clause each. What line would you refuse to sign if you were negotiating this deal again Monday morning?

Speaker 5 16:43
Version pinning at my price tier. Not the enterprise tier. Mine.

Speaker 2 16:52
A written definition of a seat.

Speaker 8 16:58
Dedicated rate limits in writing, not a pool.

Speaker 7 17:05
No unilateral change of processing region or subprocessor.

Speaker 4 17:14
Data export, documented format, no cost, and we test it before go-live. Not after.

Speaker 1 17:26
Notice before a model changes. Any notice. I would take a week.

Speaker 3 17:35
Price protection at renewal, because we are all going to find out about that one next year.

Station pilot 17:48
That is the list, and every one of those is a sentence somebody in this room paid to learn. That is time. Thank you.
