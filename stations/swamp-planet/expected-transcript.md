# Swamp Planet: Expected Transcript

**This is not a recording. Nobody has said any of this.**

Fleet Command wrote this before the event, from the question list in [`questions.md`](questions.md), as a fuller version of the seeded answers in it: what this room is likely to say, in the shape a transcript arrives in, so the closeout has something with real texture to fall back on if this station's recording fails. On the night it is replaced by `transcript.md`, which is the real one.

There are no names in it because there will not be any. The station is captured on one laptop in a loud room, so Teams attributes the whole session to the meeting host and not to the twenty-five people actually talking.

---

Swamp Planet, September 17, 2026

Station pilot 0:11
Swamp Planet. Technical debt and data quality. Talk toward the laptop, we are recording, and the recording is the only way any of this gets out of this room. We are going to start easy. Round the room, one word each for the state of your data the first time an AI system actually tried to use it. One word.

Speaker 1 0:44
Undocumented.

Speaker 2 0:47
Duplicated.

Speaker 3 0:50
Optimistic.

Speaker 4 0:53
Fiction.

Speaker 5 0:57
Haunted.

Speaker 6 1:02
Fine, actually.

Station pilot 1:06
Hold on. Say more, because you are the only person in the room who said that.

Speaker 6 1:14
We did a warehouse migration two years ago and it was miserable and it took eighteen months. So when we pointed a model at it, it worked. I am not claiming we are clever. We just already paid for it and we paid for it for a different reason.

Station pilot 1:41
Noted, and we are coming back to you. Let us hear two or three from the other side. What did you actually discover?

Speaker 4 1:56
We have a status field on the customer record. The documentation says it has fourteen values. Production has just over sixty, because it has been free text since 2019 and nobody knew. Half of them are typos of the other half. Every report we have ever run has been quietly wrong at the edges and nobody downstream ever said anything, because they all built their own filters.

Speaker 2 2:38
Dates. Three formats in one column, stored as strings, and one of them is ambiguous for the first twelve days of every month.

Speaker 1 3:02
Ours is worse and it is not technical. We have four definitions of an active customer across three systems, and every one of them is correct for the team that owns it. The model did not have a data problem. We had a disagreement problem, and it had been going on for nine years without anyone having to resolve it.

Station pilot 3:44
That is the line of the night so far. Second question. If you cannot answer where does my data flow today, you probably cannot fix your data problems. Hands up: who could actually draw that map, start to finish, right now?

Speaker 3 4:03
One hand. Mine, barely, and only because I drew it myself last year after an incident, and I already know two systems on it are wrong.

Station pilot 4:18
One hand out of twenty-five. For everyone whose hand stayed down, what would knowing it change?

Speaker 1 4:31
We would stop being afraid to touch things. Right now nobody changes a pipeline without tracing it by hand first, because the last person who guessed was wrong and it took three weeks to find.

Speaker 4 4:54
Vendor selection, honestly. We keep buying tools that promise to sit on top of our data and none of us can tell the vendor what the data actually looks like when they ask.

Speaker 5 5:16
It would change who we blame. Right now when something breaks it defaults to blaming the newest system, because that is the only one anybody has a diagram for.

Speaker 7 5:38
For us it would change the AI roadmap completely. Half of what is on it assumes data lives in one place, and it does not, and everyone building the roadmap knows that and nobody has said it in the room where the roadmap gets approved.

Speaker 6 5:57
I will say the honest thing, which is that knowing it would probably kill three of our current projects, and that is exactly why nobody has funded drawing the map.

Station pilot 6:14
Third. How much of your AI project turned into a data cleanup project, in percentage terms? Round the room, a number.

Speaker 3 6:32
Eighty.

Speaker 2 6:35
Seventy.

Speaker 1 6:38
Ninety, and I think ninety is generous to us.

Speaker 5 6:44
All of it. We never got to the AI part. We are ten months in and what we have delivered is a clean customer table, which everybody now uses and nobody will fund.

Speaker 6 7:04
Forty, because of the migration.

Speaker 7 7:10
Sixty, but I want to say the sixty was not the hard part. The hard part was that the cleanup needed decisions from four departments and we could not get them in a room.

Station pilot 7:33
So the room is forty to a hundred, and most of you are somewhere in the seventies and eighties. Was any of it in the budget?

Speaker 3 7:48
No.

Speaker 1 7:50
No, and worse, we had told the board the data was ready, because the last vendor who assessed it told us it was ready.

Station pilot 8:06
Fourth. Where is your worst data, and does anybody actually own it today? Hands up if you can name an owner for your worst data. One, two, three. Three hands out of twenty-five. So what happened to the rest of it?

Speaker 5 8:39
Acquisition. We bought a company in 2019 and the customer records were merged by a contractor on a fixed-bid project. The one person who understood the mapping left in 2023. We now pay them as a consultant, four hours a month, to answer questions. That is our data governance strategy and I am saying it out loud on purpose.

Speaker 2 9:22
Product hierarchy. It had an owner. Then there was a reorg, and the team that owned it was split across two functions, and now the answer to who owns it is a Teams channel.

Speaker 8 9:51
Our worst data is the one nobody thinks of as data. Free-text notes on service tickets. Eleven years of them. Nobody owns them, nobody has ever read more than a hundred of them, and every AI use case anybody proposes in our company wants them.

Station pilot 10:26
Fifth. Did you fix the underlying data or build around it? Split the room. Hands for fixed it. Four. Hands for built around it. That is everybody else. One story from each side.

Speaker 6 10:54
We fixed it, and I have already explained that we only fixed it by accident, on a different budget, for a different reason.

Speaker 3 11:11
We built around it. The deadline was real, the cleanup was not scoped, and we shipped a mapping table. It has about eleven hundred rows. A business analyst maintains it by hand. It is now in the path of a process that touches revenue, and it lives in a spreadsheet that syncs to a database nightly. If they are on holiday and something new shows up, we get it wrong and we do not find out for a week.

Station pilot 12:01
What has that workaround cost you since?

Speaker 3 12:09
Two things. That analyst's time, permanently. And the fact that we now cannot fix the real data, because eleven hundred hand-written exceptions are sitting on top of it and unwinding them is its own project that nobody will fund either.

Station pilot 12:37
Sixth. What broke downstream that nobody knew depended on the thing you changed? Hands. Almost everybody. How long before anyone noticed, and who noticed?

Speaker 7 13:01
We deduplicated customer records. Good change, right thing to do. It broke the commission calculation, because commissions were being paid against the duplicates. Sales noticed at quarter end. It was about three weeks and it was a very loud three weeks.

Speaker 1 13:34
Finance. A report that feeds board reporting. We changed how one field was populated and the numbers shifted by about four percent. Nobody noticed for a month and a half, and then we had to explain to the board why last quarter's number had moved.

Speaker 8 14:06
For us it was an export nobody documented. A partner had been pulling a nightly file for six years. We changed a column name. Their integration was silent about it and just stopped loading rows, and we found out when they called us about their own missing revenue.

Station pilot 14:39
Seventh. Which pilot went to production without ever being rebuilt, and what is holding it up now? Hands up if you have one running right this minute. That is a lot of hands and some of them went up slowly. What is it actually running on?

Speaker 4 15:08
A notebook. On a laptop. It classifies inbound support tickets and it has been doing it for fourteen months. The laptop is in an office. The person reboots it when it stops.

Speaker 2 15:29
A prompt in a vendor console that produces the weekly summary the executive team reads on Monday morning. There is no code. There is no repository. There is a text box, and the person who wrote what is in it has taken another job.

Speaker 5 15:58
Ours is a scheduled task on a virtual machine that is not in our asset inventory, which means it is not patched, which means it is going to be somebody else's problem in a different building tonight.

Station pilot 16:23
Eighth. When bad data produced a confidently wrong answer, did you catch it before or after a customer did? Hands for before. Five. Hands for after. Fourteen. How, from each side.

Speaker 6 16:52
Before, and only because we sample. Two hundred outputs a week, read by a human, scored. It is boring and it is the only reason we knew. It caught a stale pricing table about three days in.

Speaker 8 17:22
After. A customer asked the assistant when their contract ended and it told them, with total confidence, a date that was eleven months wrong, because it read a table that stopped being updated when we changed billing systems. Nothing alerted. Nothing could have. It was not down, it was not slow, it was not throwing errors. It was just wrong, politely, at scale.

Station pilot 18:04
Say the general version of that for the recording.

Speaker 8 18:11
An outage pages somebody. A wrong answer does not page anybody. We have spent twenty years building alerting for the loud failure and this is the quiet one.

Station pilot 18:33
Last one, at the five-minute mark. Somebody on your team starts an AI project Monday. One thing you tell them to do with their data first. Round the room.

Speaker 3 18:52
Profile it. Actually profile it. Nulls, distinct values, ranges. Before you promise anybody a date.

Speaker 1 19:05
Write down the definition of your main entity and get the four people who disagree in a room before you build anything.

Speaker 5 19:21
Find out who owns it. If the answer is nobody, that is your first ticket, not your last.

Speaker 4 19:34
Pick one table. Not the warehouse. One table.

Speaker 2 19:44
Assume the documentation is a description of what somebody intended in 2018.

Speaker 7 19:56
Ask who would notice if it were wrong. If the answer is nobody, you have found the real problem.

Speaker 6 20:09
Do the boring migration. It will pay for something you have not thought of yet.

Station pilot 20:22
That is time. Thank you, all of you, that was more honest than I expected.
