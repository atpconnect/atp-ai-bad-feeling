# Snow Monster Cave: Expected Transcript

**This is not a recording. Nobody has said any of this.**

Fleet Command wrote this before the event, from the question list in [`questions.md`](questions.md), as a fuller version of the seeded answers in it: what this room is likely to say, in the shape a transcript arrives in, so the closeout has something with real texture to fall back on if this station's recording fails. On the night it is replaced by `transcript.md`, which is the real one.

There are no names in it because there will not be any. The station is captured on one laptop in a loud room, so Teams attributes the whole session to the meeting host and not to the twenty-five people actually talking.

---

Snow Monster Cave, September 17, 2026

Station pilot 0:12
Snow Monster Cave. This one is about development: what is actually happening inside the build. Speak toward the laptop, we are recording. First question, round the room, one phrase each. What did tested mean for the last AI feature you shipped? And I will tell you now that vibes is an acceptable answer.

Speaker 1 0:47
Vibes.

Station pilot 0:50
There it is, forty seconds in.

Speaker 2 0:56
Forty examples in a spreadsheet that the product manager wrote.

Speaker 3 1:04
One engineer read outputs for an afternoon and said it seemed fine.

Speaker 4 1:14
We actually had three hundred golden cases. All happy path. Nothing adversarial, nothing empty, nothing in the wrong language.

Speaker 5 1:30
A demo to the sponsor. That was the test.

Speaker 6 1:38
We had a real eval harness, and I want to be honest about why. We had an incident on the previous feature and we built it after.

Station pilot 1:56
Who decided it was enough? Anybody?

Speaker 2 2:04
Nobody decided. The date decided.

Speaker 4 2:11
Same. There was a launch on the calendar before there was a test plan.

Station pilot 2:24
Second. What is a change that passed every test you had and still broke behaviour in production? Hands. Most of you. Two stories, and then I want to know what caught it, a dashboard or a user.

Speaker 6 2:51
We tightened a prompt to make answers shorter. It passed a hundred and twenty cases. In production it started dropping a required disclaimer on one category of answer, because the disclaimer was the longest sentence and shorter was what we asked for. A quality lead reading tickets caught it. Nine days.

Speaker 3 3:29
We rebuilt the retrieval index with different chunking. Every eval passed, and every eval passed because the eval used a cached retrieval set from before the rebuild. We were testing the old index against the new model. It took a week and a very confused afternoon to work that out.

Speaker 1 4:02
Ours was a vendor-side change, so we did not change anything at all. That is the part that gets me. The tests pass because nothing in our repository moved.

Station pilot 4:24
Dashboard or user, round the room quickly.

Speaker 6 4:31
User.

Speaker 3 4:33
Engineer, by accident.

Speaker 2 4:37
Customer. In writing. To our CEO.

Speaker 5 4:43
Nobody caught it. We found it two months later looking for something else.

Station pilot 4:56
Third. Who is actually on call when the AI feature misbehaves at two in the morning, and did they know that was part of the job when they signed up? Hands up if you have a formal on-call rotation for an AI feature. One, two, three. Three, out of about twenty-two. So who is really carrying it?

Speaker 4 5:33
The two people who built it. There is no rotation. There is a phone number that is one of their mobile numbers, in a runbook, that somebody typed in during the launch.

Speaker 7 5:56
For us it is worse than informal. The alert goes to the platform on-call, who is a good engineer with no idea what the thing does, and the actual escalation is that they message the builder on Teams and hope.

Speaker 2 6:22
We had a genuine two a.m. one. A queue backed up. The on-call engineer could see it and could not fix it, because the only thing that would have fixed it was a setting in the vendor console and one person had the login. That person was asleep and had no reason to think that was part of their job.

Station pilot 6:56
Did they know when they signed up?

Speaker 4 7:03
No. They volunteered to build a prototype. Nobody has ever gone back and renegotiated that.

Station pilot 7:19
Fourth. Say it's three months in, the AI is running, your teams are using it. How are you measuring whether it is actually working, not is the tool being used but is the outcome improving? And here is the harder part: whose budget or scorecard does that outcome show up on?

Speaker 6 7:48
We have a usage dashboard everybody loves showing the sponsor. We do not have an outcome metric. Nobody has gone back and asked whether the thing it was supposed to move actually moved.

Speaker 3 8:11
Ours moved a real number, ticket resolution time, but the number lives in a spreadsheet the team lead keeps for herself. It is not on any scorecard leadership actually looks at.

Speaker 4 8:34
This is the one that got us. The outcome shows up on the business owner's budget, as headcount they did not have to add. It does not show up anywhere on engineering's side, which is part of why engineering never gets asked to build the next one with any urgency.

Speaker 7 8:58
We built usage into the product because it was easy. Adoption, active users, queries per day. Every one of those can go up while the actual outcome gets worse, and for about two months ours did exactly that and nobody noticed because the dashboard was green.

Speaker 2 9:22
Honestly nobody in this room has answered the second half of the question yet. Whose scorecard. I do not think ours is on anyone's. It is on a slide.

Station pilot 9:41
Anybody have it on an actual scorecard, reviewed regularly, not a slide?

Speaker 6 9:49
One. Finance owns it because it touches invoice processing, and finance reviews everything quarterly whether you want them to or not. That is the only reason it happened.

Station pilot 10:02
Fifth. What skill was missing on your engineering team when this started, and how did you close the gap? Poll. Hired. Four. Trained. Six. Contracted. Five. Still missing. That is nine hands and it is the biggest pile. What is the skill?

Speaker 3 10:21
Nobody had ever built an eval pipeline. Not a unit test, an eval. How to decide what good looks like when the output is a paragraph and there are twenty acceptable versions of it.

Speaker 6 10:48
We closed it by hiring one person who had done it somewhere else, and honestly that worked, but it also means we have one person who understands it and we are back to the same problem in a different shape.

Speaker 8 11:14
The missing skill on our team was not technical. It was somebody who could say this is not ready. Everybody could see it. Nobody had the standing to stop a launch.

Speaker 5 11:36
We contracted it and the contractors were good, and when they left they took the understanding with them and left us the code.

Station pilot 11:58
Sixth. How much of what you call your AI feature is genuinely your code, versus a thin wrapper around somebody else's API? Round the room, a percentage.

Speaker 1 12:20
Fifteen percent ours.

Speaker 7 12:25
Twenty.

Speaker 2 12:30
Five, and I will defend five. The whole thing is a prompt and a queue.

Speaker 4 12:40
I would say ninety percent ours, but the ten percent is the part that makes it work, so the number is misleading in our favour and I know it.

Speaker 6 12:57
Thirty. Most of what we own is retrieval, permissions, and the review step. Which is also where all the bugs are.

Station pilot 13:17
Does leadership know that number?

Speaker 2 13:24
Absolutely not. There is a slide with our logo on it and an architecture diagram with nine boxes, and eight of those boxes are ours and the ninth one does the work.

Station pilot 13:48
Seventh. Where does the prompt actually live in your shop? Source control, a vendor console, or somebody's laptop. Hands for source control. Eight. Vendor console. Six. Laptop. Two, and I appreciate the honesty. What has that cost you?

Speaker 5 14:22
The change nobody could trace. Output quality dropped on a Monday. Nothing in the release notes, nothing in the repository, no deployment. Somebody had edited the prompt in the console on Friday at five, for a good reason, for a different feature, and both features read the same prompt.

Speaker 7 14:58
That is exactly ours. Two features, one prompt, and nobody knew because the console does not tell you what is calling it.

Speaker 3 15:17
We moved ours into the repository after something like that, and the thing I would say to anyone who has not is that the win is not version control. The win is that a change now has a person and a reason attached to it.

Station pilot 15:42
Eighth. When a model or prompt change goes bad, what does rolling back actually look like? Hands if you have actually rolled one back. About seven. What could you revert, and what could you not?

Speaker 6 16:09
We could revert the prompt in about four minutes. We could pin the model version, because we pay for the tier that allows it. What we could not do is get the vendor's underlying weights back, so the behaviour we rolled back to was not the behaviour we had two weeks earlier. It was close. Close was enough that time.

Speaker 3 16:44
Ours looked like a successful rollback and was not, because the embeddings in the index had been regenerated with the new model. We reverted the code and the data was still from the new world. Quality stayed bad for another day and a half while we argued about whether the rollback had worked.

Speaker 2 17:18
For us rolling back took forty minutes, and thirty-nine of those minutes were finding out where the prompt was.

Speaker 8 17:33
I want to add the one nobody mentions. You can roll back the system. You cannot roll back the four thousand answers it already gave people.

Station pilot 17:54
Say that again.

Speaker 8 17:59
The output is already gone. It is in somebody's inbox, it is in a ticket, it is in a decision somebody made. A rollback fixes the next answer. It does not fix the ones that already went out, and none of our incident processes have a step for that.

Station pilot 18:26
Last question, at the five-minute mark. A dev team is about to build their first real AI feature. Round the room, one thing each about what actually eats the time.

Speaker 3 18:48
Not the integration. The integration is an afternoon. The eval set is a month.

Speaker 6 19:01
Deciding what good looks like, with the business, in writing, before you build.

Speaker 4 19:14
The on-call plan. Write it before launch or you will be it.

Speaker 7 19:26
Put the prompt in the repository on day one. It costs nothing on day one.

Speaker 2 19:38
Assume the vendor will change something and build the regression test that would tell you.

Speaker 5 19:51
Decide who owns it after the person who built it moves on. That person will move on.

Speaker 1 20:05
Budget for version two. Version one is the thing that teaches you what to build.

Speaker 8 20:18
And write down what you will do about the answers that already went out.

Station pilot 20:31
That is time. Thank you.
