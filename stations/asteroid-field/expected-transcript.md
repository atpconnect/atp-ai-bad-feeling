# Asteroid Field: Expected Transcript

**This is not a recording. Nobody has said any of this.**

Fleet Command wrote this before the event, from the question list in [`questions.md`](questions.md), as a fuller version of the seeded answers in it: what this room is likely to say, in the shape a transcript arrives in, so the closeout has something with real texture to fall back on if this station's recording fails. On the night it is replaced by `transcript.md`, which is the real one.

There are no names in it because there will not be any. The station is captured on one laptop in a loud room, so Teams attributes the whole session to the meeting host and not to the twenty-five people actually talking.

---

Asteroid Field, September 17, 2026

Station pilot 0:15
Asteroid Field. Compliance, legal, and security. Speak toward the laptop, this is recorded. We are going round the room first. One question each that Legal actually asked you about your AI system that you genuinely could not answer. Just the question, we will come back and see who has an answer now.

Speaker 1 0:52
What data was this model trained on.

Speaker 2 0:58
If a customer asks us to delete their data, does it come out of the model.

Speaker 3 1:07
Can you explain this particular output to a regulator in plain language.

Speaker 4 1:16
Is this a decision or a recommendation. Which sounds like a small question and it is not.

Speaker 5 1:28
Who is liable when it is wrong. Us, the vendor, or the employee who accepted it.

Speaker 6 1:40
Where is the data physically processed, and is that still true next month.

Speaker 7 1:51
What is our retention obligation for a prompt.

Station pilot 2:02
Good. Which of those does anybody here have an answer to now?

Speaker 4 2:13
We answered the decision versus recommendation one, and the way we answered it was to change the product. We made a person press a button. That was cheaper than the argument.

Speaker 2 2:36
Nobody has answered the deletion one. I have asked three vendors. The answers were no, effectively no, and a paragraph that means no.

Station pilot 2:56
Second. Has a compliance or security requirement ever killed an AI use case outright? Hands. About nine. Two stories, and then I want to know from the room whether it was the right call, because I expect you to split.

Speaker 8 3:24
We wanted to summarise recorded customer calls. We operate in a state that requires both parties to consent to the recording being used that way, and our consent script covered recording for quality, not processing by a third party. Legal killed it in about a week. The fix is a consent change that takes eighteen months to work through, so it is dead.

Speaker 3 4:04
Resume screening. Our counsel read the bias audit requirements in two of the jurisdictions we hire in and said no, and I think that was right, and half my engineering team still thinks we lost a year of advantage.

Station pilot 4:33
Was it the right call? Hands for yes. About thirteen. Hands for no. Six. Somebody from the no pile.

Speaker 9 4:52
It is not that the review was wrong. It is that it arrived at the end. We spent four months and about two hundred thousand dollars building something that was never going to be legal, and somebody could have told us that in the first week for free.

Station pilot 5:20
Third. Who actually signs off that an AI decision, or an AI vendor, is safe enough to put in front of a customer? Round the room, name the role, not the person. I am going to count the number of times I hear nobody yet.

Speaker 1 5:47
Nobody yet.

Speaker 5 5:50
Our CISO signs the vendor. Nobody signs the decision.

Speaker 7 5:58
Nobody yet.

Speaker 4 6:01
A risk committee, and it meets monthly, which functionally means nobody for up to four weeks.

Speaker 2 6:12
Nobody yet.

Speaker 6 6:15
The CIO, because somebody has to, and the CIO has said out loud that it should not be the CIO.

Speaker 3 6:26
Nobody yet.

Speaker 8 6:29
Legal signs the contract. Nobody signs the output.

Speaker 9 6:36
Nobody yet.

Station pilot 6:41
That is five nobody yets out of nine, and the other four are somebody who did not want the job. Say the general version for the recording: this is a vacuum, and the vacuum stalls more work than any technical limit in any of your buildings.

Station pilot 7:08
Fourth. Have you tried to put an AI vendor through your normal security review, and what happened? Hands. Nearly everybody. Did it pass, stall, or pass something it should not have? One story for each.

Speaker 5 7:36
Stalled. Seven months. Our questionnaire has a hundred and eighty questions written for software that ships in versions, and about forty of them do not have a meaningful answer for a service whose behaviour changes without a release. The vendor kept answering not applicable and we kept sending it back.

Speaker 6 8:12
Passed, and it should not have. They inherited a certification from their cloud provider and we accepted it. What we did not read is that the contract lets them add a subprocessor with notice, and notice means a page on their website. So the thing we reviewed can become a different thing and we have agreed to that in writing.

Speaker 1 8:50
Ours passed properly and took five weeks, and the only reason is that it was a vendor we already had. The AI product was a new module on a contract from 2021, which means it got almost no scrutiny. That is not a success story, it is a gap.

Station pilot 9:22
Fifth. When you actually looked at what employees were putting into AI tools, sanctioned or not, what did you find? Hands up, who has looked. About twelve. So half of you have not. From the half who have.

Speaker 7 9:50
We ran the proxy logs for a month. Thirty-four distinct AI tools in use. Three were approved.

Speaker 2 10:06
Our DLP found customer contracts, an unsigned commercial agreement, source code, and a board deck. The board deck was the one that changed the conversation, because it was pasted in by somebody senior enough that nobody wanted to write the incident report.

Speaker 9 10:36
We found a nurse pasting patient information into a consumer chat tool to help write a summary. No malice at all. They were doing unpaid work at nine at night and the tool made it faster.

Station pilot 11:04
Now split the room. Who blocked it. Who allowed it. Who did neither. Blocked, seven. Allowed with a sanctioned option, nine. Neither, six. One story from each side.

Speaker 3 11:30
We blocked. Domain blocks, DLP rules, the lot. And I will be honest, it did not stop. It moved to phones. Our data is still going into these tools, we just cannot see it any more, which is arguably a worse position than the one we started in.

Speaker 6 12:00
We sanctioned one tool with an enterprise agreement and no training on our data, and we put it in front of everybody and told them to use it. Usage of the unapproved stuff dropped by something like eighty percent in two months. It did not go to zero. But eighty percent of a problem is a lot of problem.

Speaker 8 12:34
We did neither, and I am sitting here realising that doing neither is a decision and we made it by accident.

Station pilot 12:52
Sixth. What did you have to add after the fact that nobody scoped up front. Audit logs, human review, explainability, or a security control. Hands for audit logs. Fourteen. Human review. Eleven. Explainability. Six. A security control. Thirteen. Story from the audit log pile.

Speaker 4 13:30
We had to start logging prompts and outputs, because we could not answer a single question about what the system had done. Reasonable requirement. Then about six weeks later Legal came back and pointed out that we are now retaining a complete record of everything every employee has ever asked, indefinitely, and it is all discoverable. So we solved a compliance problem by creating a different compliance problem, and nobody had scoped either one.

Speaker 5 14:12
Human review, for us. Which is a cost, and I want to say it plainly: it is two and a half people, permanently, and it turned the business case upside down. It was still the right thing to do.

Station pilot 14:38
Seventh. What has your auditor, regulator, or cyber insurer actually asked you about AI so far? Hands up if you have been asked anything at all. About sixteen. By whom, and what?

Speaker 1 15:04
Cyber insurer. Four new questions on the renewal questionnaire this year, and one of them asked whether we use AI in any process affecting customer eligibility. Answering it honestly required a conversation we had not had internally.

Speaker 6 15:34
Our external auditors. They want to know where AI touches anything in the financial reporting path, and they want the control documented. That is the first time anybody outside the company forced us to write down what the system does.

Speaker 9 15:59
Nothing from a regulator. Plenty from customers. Our biggest customer's security questionnaire now has an AI annex that is harder than anything any regulator has published, and if we do not answer it we lose the account. So our regulator is effectively our customer.

Speaker 3 16:29
That is the pattern, and the silence from regulators is not a relief. You cannot design to a position that does not exist yet. A strict rule you can build against. Nothing is worse, because whatever you build might be wrong in two years.

Station pilot 16:54
Last one, at the five-minute mark. Round the room. What did the review catch that you are glad it caught? And if the answer is nothing, say nothing, because that is a finding.

Speaker 5 17:16
A data flow nobody had drawn. Our prompts were being logged by the vendor for quality purposes, in a different region, and it was in their documentation and nobody on our side had read it.

Speaker 2 17:38
Personally identifiable information in our own application logs. The review found it. It had been there for three years and had nothing to do with AI.

Speaker 7 17:56
A shared service account that the integration used, with far more access than the use case needed. That one could have been genuinely bad.

Speaker 4 18:12
The retention question, eventually. Late, but they did catch it.

Speaker 9 18:22
Nothing. I will say it. Our review caught nothing, it took five months, and I do not think it was free. It cost us the thing we were building.

Station pilot 18:38
And that is on the recording too, which is the point of the evening. That is time. Thank you.
