# Ice Planet: Expected Transcript

**This is not a recording. Nobody has said any of this.**

Fleet Command wrote this before the event, from the question list in [`questions.md`](questions.md), as a fuller version of the seeded answers in it: what this room is likely to say, in the shape a transcript arrives in, so the closeout has something with real texture to fall back on if this station's recording fails. On the night it is replaced by `transcript.md`, which is the real one.

There are no names in it because there will not be any. The station is captured on one laptop in a loud room, so Teams attributes the whole session to the meeting host and not to the twenty-five people actually talking.

---

Ice Planet, September 17, 2026

Station pilot 0:13
Ice Planet. Use cases, costs, and scope creep. Speak toward the laptop, this is recorded, and the recording is the whole reason we are doing it this way. We start with arithmetic. Round the room, two numbers. How many AI use cases has your company started, and how many are actually in production today. I am keeping a running total and I will read it out at the end for the recording.

Speaker 1 0:52
Fourteen started. Two in production.

Speaker 2 0:58
Nine and one.

Speaker 3 1:03
I genuinely do not know the first number. Somewhere north of thirty, because every function started their own. Four live.

Speaker 4 1:16
Six and zero.

Speaker 5 1:20
Twenty-two and three.

Speaker 6 1:25
Three, and one of them is a chatbot on our website that nobody uses and nobody will turn off.

Speaker 7 1:36
Eleven and one, and the one is internal.

Speaker 8 1:43
We have four and all four are live, but I should say we only started four, because we have a rule that you cannot start a fifth until one of them lands.

Station pilot 2:01
Hold that, we are coming back to it. Keep going.

Speaker 9 2:09
Eighteen. Two.

Speaker 10 2:14
Twenty-something. One and a half, and the half is a pilot that is serving real customers without having been promoted, which I realise is its own answer.

Station pilot 2:33
So for the recording: this room has started something like a hundred and forty-seven AI use cases and has nineteen and a half of them in production. I am counting the half. That ratio is the whole station and we are three minutes in. Second question. What is the single most common reason a use case stalls before it ships? I am going to poll it, one hand each. Budget. Two. No owner. Seven. Data. Four. Legal. Two. Nobody ever actually decided. Nine hands. That is the biggest pile. Stories.

Speaker 3 3:29
Ours do not get cancelled. They get quiet. The pilot ends, the team that built it moves to the next thing, and there is no meeting where anybody says this is finished or this is dead. It just stops having a next step. Two years later it is still on a slide.

Speaker 7 3:59
It is the handoff. The innovation team builds it, and to put it in production it has to go to the platform team, and the platform team's answer is not no, it is that this is not in this year's plan. Which is a no that nobody has to own.

Speaker 1 4:28
Same shape. Nobody with budget authority wants to take on an operating cost for something somebody else's team is going to get credit for.

Station pilot 4:47
Third. If you had fifty thousand dollars to invest in AI tomorrow, where would you put it, and how would you know you picked the right use case? One answer each: the use case, then the number you would check to know it worked. If you stall, walk through it out loud: where is the business value, what will it cost, how long should it take, what data does it need, how do you keep it from growing, how do you measure the payoff.

Speaker 9 5:12
Invoice matching in accounts payable. Boring, one team, real volume. I would check hours saved per week against the team's own timesheet, not a vendor number.

Speaker 2 5:34
I would not spend it on a new use case at all. I would spend it finishing one of the four things already half-built, because the marginal fifty thousand on something new is more scope, not more value.

Speaker 6 5:52
Contract review for one type of contract, the one we do nine hundred times a year. Value is legal hours. Cost is mostly the review, not the model. I would want the data question answered before the money moves: do we actually have nine hundred clean examples, or three hundred good ones and a lot of noise.

Speaker 10 6:19
Same instinct, different lever. I would put it toward the people reviewing model output, not the model itself, because every project that has died on us died on that line, not on tokens.

Speaker 4 6:41
Scope creep is the whole risk with fifty thousand, because it is a small enough number that everyone thinks their pet feature fits inside it. I would want it written down on day one what is not included, and who has to sign off to change that.

Speaker 8 7:02
I would spend it on the eval, not the feature. Fifty thousand buys you a real test set and a clear pass or fail number before you build anything, and that number is what tells you whether you picked the right use case at all.

Speaker 3 7:20
Honestly, the ROI question is the one nobody answers cleanly. I would pick something where the baseline already exists, like current handle time or current error rate, because if you cannot measure the before, the after is just a story.

Station pilot 7:41
Fourth. What does a stalled project cost you every month it sits there, uncancelled? Hands up, who has one sitting there right now. That is most of the room. What is still being paid for?

Speaker 5 8:07
Dev and test environments we never turned off. About six thousand a month. I found them during a cost review and my honest reaction was relief that it was only six.

Speaker 9 8:30
A vendor contract with eleven months left on it. Two hundred and forty thousand a year for a platform that has one pilot on it with nine users.

Speaker 2 8:50
Three people who are ten percent allocated to it. Which means they are not on it, and they are also not fully on anything else, and every time it comes up in a planning meeting we spend twenty minutes on it.

Speaker 3 9:17
The part nobody puts a number on is credibility. We went to the board twice with AI proposals. The third one is going to be judged against two things that are still technically in flight and have not produced anything, and it is a better proposal than either of them.

Station pilot 9:48
Does any of that show up as a line item anybody reviews?

Speaker 5 9:57
No. That is the point. If it showed up, somebody would kill it, and it would be a mercy.

Station pilot 10:12
Fifth. How much did the scope grow between the day it was approved and where it stands today, and who added what? Hands if you have a project that picked up a second business unit or an executive's feature. Almost everybody.

Speaker 4 10:38
Approved as a summariser for one team, forty people. It picked up a second region, which meant translation. It picked up a compliance review, which meant an audit log and a human approval step. And then an executive saw it and asked for it on mobile. That is three things, none of which was in the estimate, and the budget did not move once.

Speaker 10 11:16
Ours grew because it worked. The pilot was good, so four other departments asked for it, and saying no to them looked like we did not believe in our own project.

Speaker 6 11:38
I want to say something slightly different. The scope did not grow. The requirements got discovered. They were always there, we just did not know about the compliance step or the accessibility standard when we wrote the estimate. Calling it creep lets us pretend the original number was ever real.

Station pilot 12:12
Who added what, though. Did the budget follow?

Speaker 4 12:21
Never. Not once. The budget is approved at the gate and the gate does not reopen.

Station pilot 12:36
Sixth. Have you ever killed an AI project outright? Hands. Two. Two out of twenty-five. What did it actually take?

Speaker 8 12:58
A reorg. The sponsor left, the new one did not care about it, and it died of neglect rather than a decision. I would not call that killing it.

Speaker 5 13:19
Ours was a real decision and it was ugly. We built the three-year run cost with real volume assumptions instead of pilot ones, and it was about four times the benefit case. Somebody senior had to stand up in a room and say this is my call, we are stopping. It cost that person something to do it. That is why it almost never happens.

Station pilot 13:56
Seventh. What did the bill look like against the pilot estimate once real users hit it? Round the room, give me a multiple, not a percentage. Then tell me which line was the surprise.

Speaker 1 14:20
Four times.

Speaker 9 14:24
Six.

Speaker 3 14:27
Eleven, but I have to be fair, we were also about eleven times the volume. Per transaction we were roughly flat.

Speaker 7 14:41
Three, and the surprise was not the model at all. It was people. We need a human reviewing output on a regulated workflow, and that is two and a half full-time people we never budgeted, forever.

Speaker 2 15:07
Seats. We priced for the pilot group and then the product got rolled out, and the seat count went from sixty to eleven hundred over about five months.

Speaker 10 15:29
Storage and retrieval, weirdly. Re-embedding the corpus every time we changed anything. And the eval work, which is a real engineering cost nobody had a line for.

Station pilot 15:55
Anybody surprised by the token price itself?

Speaker 9 16:04
Down. Ours came down twice. That is not where the money went.

Station pilot 16:16
Eighth. Which use case did ship and stick, and what was different about it? Hands if you have one that stuck. About eight. Two stories.

Speaker 8 16:41
Routing inbound email for a shared mailbox. Deeply boring. One workflow, one team, one owner in the business who wanted it, and a number we agreed before we started. Handle time went from about nine minutes to five and a half. It is still running and nobody talks about it.

Speaker 2 17:14
Ours was drafting the first response in a support queue, with a person approving every one. The thing that made it work is that we never tried to remove the person. Every project we failed at started with removing the person.

Station pilot 17:41
How do you know it paid off? I expect disagreement here.

Speaker 8 17:51
We measured before and after on handle time and on reopen rate. Reopen rate was the one that mattered and it did not move, which is what let us keep it.

Speaker 3 18:11
We did not measure anything. We call it a win because it is still running and nobody has complained. I am aware of what that sounds like in this room.

Speaker 7 18:30
I will push back slightly. People liking it is a real signal. If forty people would fight you to keep a tool, that is not nothing.

Speaker 8 18:46
It is not nothing, but it is not a number, and when the budget is cut you need a number.

Station pilot 19:02
Last one, and we are at the five-minute mark. What would have to be true for the thing sitting in your backlog right now to ship next quarter? Round the room, one thing each.

Speaker 4 19:23
A named production owner. An actual person, with a name, who takes it.

Speaker 7 19:34
A support model. Who gets called, what the target is.

Speaker 5 19:45
One executive willing to accept the risk in writing. Not in a meeting. In writing.

Speaker 3 19:58
A decision date. Just a date on a calendar where somebody has to say yes or no.

Speaker 10 20:11
Somebody with the authority to say no to the next feature request.

Speaker 1 20:23
Operating budget approved at the same time as the build budget, not nine months later.

Speaker 6 20:37
Honestly, permission to cancel the other six.

Station pilot 20:48
And not one person in this room said a better model. That is time. Thank you.
