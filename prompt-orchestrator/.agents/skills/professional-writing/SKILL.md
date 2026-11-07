---
name: professional-writing
description: 'Write short, concrete work messages that read as written by the sender:
  emails and messages to a supervisor, lecturer, client or teammate, submission comments
  and notes on a school or work platform (FPT FAP, LMS, Jira, Slack), PR descriptions,
  issue reports and replies, status updates and progress reports. The point or the
  request first, one fact per sentence, dates and owners named, no meta-commentary,
  no openers or sign-off filler, no AI tells. Use when drafting, shortening, replying
  to or reviewing any work or professional message, client message, platform note,
  Slack or chat update, PR or issue text, or a report to a supervisor, or when a message
  sounds like ChatGPT. Use it on the request alone: ''this message'', ''this issue''
  or ''this update'' with no text attached yet still needs it.'
argument-hint: '[message type] [draft or facts to send]'
---

<!-- Generated from skills/professional-writing.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Professional writing

Work messages are read on a phone, between other tasks, by someone deciding what to do next.
They succeed when the reader knows within two lines what happened and what is asked of them.
The tone is polite and plain; politeness comes from naming the reader's need, not from filler.

Pipeline before sending: this skill, then `concision-and-logic` with its scanner run as
`--genre professional`, then a `human` audit. Commit, PR, tag and issue text also follows
`no-ai-trailer`. Sending is the writer's action; draft, do not send without their word.

## Rules

1. **First line: the news or the request.** "Report 3 is submitted on FAP." "Can we move Friday's
   review to 14:00?" Context comes after, only as much as the reader needs to act.
2. **A request names the action, the owner and the date.** "Please approve the scope change by
   Monday 9 November" instead of "Let us know your thoughts."
3. **One fact per sentence.** No sentence over 30 words.
4. **No talk about the message.** Cut "I am writing to inform you", "This email is to", "Please
   find below", "As per my last email", "I hope this finds you well", "Just a quick note",
   "Feel free to reach out", "Let me know if you have any questions".
5. **Concrete over general.** Files by name, sections by number, versions, dates, counts.
   "Section 3.2 now lists 14 use cases, up from 11" instead of "the document has been improved".
6. **No AI tells.** No "delve", "leverage", "robust", "seamless", "dependable", no "this matters",
   no "not only X but Y", no parenthetical asides, no em dash. No verdict pairs such as "X is
   done, and Y is not"; list each item on its own line instead.
7. **Bad news plainly.** What went wrong, the effect, what is being done and by when. No
   apology paragraph; one "sorry" if it is owed.
8. **Address and close as the relationship expects.** "Dear Mr Hung," or "Dear Ms Lan," for a
   lecturer or supervisor unless they use first names; "Best regards," and the name. Teammates:
   first name and no sign-off in chat.
9. **Keep the writer's facts at their scope.** Add no promise, date or commitment the writer did
   not make. A paraphrase must not widen a fact: "we added two use cases to Section 3" does not
   become "Section 3 is new". Keep relative dates as given ("today", "next week") unless the
   writer supplies the calendar date.

## Formats

| Type | Shape | Budget |
|---|---|---|
| Platform note or submission comment (FAP, LMS) | What was submitted, what changed since the last version, anything the grader must know | 1 to 3 sentences |
| Email to a supervisor | Subject with the topic and the ask; first line the ask or news; facts; the deadline | Under 150 words |
| Status update | Done, in progress, blocked and what unblocks it, next | One line per item |
| PR description | What changed; why; how it was tested; risks or follow-ups | One short paragraph or list each |
| Issue report | Expected, actual, steps to reproduce, environment, evidence such as a log or screenshot | As long as the steps need |
| Issue or review reply | The answer or the decision first, then the evidence: commit, file and line | Usually 1 to 4 sentences |
| Report to a supervisor | Results against the plan, problems with their impact, decisions needed | Set by the template |

## Before and after

| Before | After |
|---|---|
| Dear Sir, I hope this email finds you well. I am writing to inform you that our team has successfully completed and submitted Report 2, which now comprehensively covers all aspects of the system requirements. Please feel free to reach out if you have any questions. | Dear Mr Hung, Report 2 is on FAP. It adds use cases UC-12 to UC-14. Section 5 now lists the non-functional requirements. Could you confirm by Thursday that the offline sync scope in Section 4.3 is acceptable? Best regards, Khoa |
| FAP note: This submission includes the updated register, which reflects the latest discussions with our supervisor and ensures alignment with the project scope. Note that some figures are sample values. | FAP note: Updated register. Scope in Section 3 now matches the supervisor meeting of 6 November. Default values are marked in Table 4. |
| PR: This PR introduces a robust and seamless enhancement to the check-in flow, ensuring a more dependable user experience. | PR: The phone now queues check-ins made without signal. It sends them when the mesh reaches a gateway. Tested on two phones in airplane mode. The test steps are below. Follow-up: #142 tracks the hard-coded retry limit of 5. |
| Status: Great progress this week! The backend is mostly done, and the firmware is not. | Done: backend check-in API. In progress: firmware relay timing. Blocked: relay timing needs the second node. The node arrives on 10 Nov. Next: integration test on 12 Nov. |

## Review checklist

- [ ] The first line carries the news or the request.
- [ ] Every request has an owner and a date.
- [ ] No opener, sign-off filler or note about the message.
- [ ] Names, numbers, sections and versions instead of "the document" and "some changes".
- [ ] `draft_scan.py --genre professional` run; each remaining finding has a reason to stay.
- [ ] Within the budget for its type.
- [ ] No em dash; no AI attribution in commit, PR or issue text.

## Output

The ready-to-send text, then one line listing any fact the writer must confirm before sending:
a date, a number or a name you could not verify.
