# Sprint 10-13 Meeting Notes Definitions
## 4 Meeting Notes — Sprints 10-13
## May to June 2025

---

## GLOBAL RULES

**Format:** Word document (.docx)
**Note taker:** Shristi Sharmistha
**Tone:** Direct, startup energy, captures real conversations
not sanitised summaries. Each discussion must show who said
what and what decision was reached.

---

---

# MEETING NOTE 1 — SPRINT 10
## Weekly Team Sync — May 20, 2025

**Date:** May 20, 2025
**Time:** 11:00 AM IST
**Sprint:** Sprint 10 (May 13-26)
**Attendees:** Shristi Sharmistha, Arjun Mehta, Priya Nair,
Kabir Sharma, Ananya Iyer
**Note taker:** Shristi Sharmistha

---

**Sprint Health Check:**

MON-001 metrics dashboard: Complete. Live since May 15.
MON-002 pregnant women analysis: Complete. Results shared in
email thread this morning. 3.1x engagement confirmed.
BUG-010 and BUG-011: Both complete and deployed.
NPS-001: Survey launched this morning — results coming in.
AN-CR-003: Complete. Analysis load time 0.7 seconds.
RES-001 interviews: 3 of 5 complete. Remaining 2 this week.
V2-PLAN-001: In progress. Draft priorities shared in Slack.

Overall: Sprint on track. 6 of 9 tickets done with 6 days remaining.

---

**Key Discussion 1 — Pregnant Women Cohort Analysis Results**

Shristi opened by asking Arjun to walk the team through the
cohort analysis results formally.

Arjun presented the numbers: sessions per day 4.2 vs 1.8 overall,
session length 6.3 vs 2.8 minutes, Day 7 retention 81.8% vs 41.9%.
Combined engagement multiple: 3.1x. Methodology verified — not
survivorship bias, not a small-sample coincidence.

The iodine finding was the most surprising to the team. 54% of
pregnant users tracking iodine vs under 5% of all other users.
Arjun explained that iodine deficiency is a serious prenatal risk
for fetal brain development — users tracking iodine specifically
are medically informed users with doctor-prescribed targets.

Kabir asked the design question: what does this mean for the
product? If these users have specific trimester-based targets
that the current app does not support, what are they doing?

Ananya answered from the interviews. All 3 users she has spoken
to so far are manually editing their micronutrient goals every
time they transition between trimesters. One user said she
recalculates her iron target from a spreadsheet her doctor gave
her. The app is not supporting the trimester transition workflow
at all.

Shristi made the decision: prenatal presets become Q3 priority 2
immediately. The 3.1x engagement is confirmed, the user pain is
confirmed from interviews, and the feature gap is clear. Trimester-
specific micronutrient targets. ICMR guidelines not WHO.

Priya asked a practical question: how would users identify
themselves as pregnant in the current onboarding? There is no
pregnancy option. Shristi confirmed this will be part of the
Sprint 12 simplified onboarding redesign — pregnancy will be
added as a fourth health goal option.

---

**Key Discussion 2 — NPS Survey First Results**

Ananya shared the first batch of NPS survey responses (survey
launched this morning, 47 responses in the first 3 hours).

Score so far: 31 (small sample, expected to move). More important
is the open text.

Top themes emerging from first 47 responses:
Custom recipe builder: 11 mentions
Goal setup complexity: 8 mentions
Barcode scanner: 7 mentions

Ananya read one open text response directly: The calorie goal
setup was confusing. What is EER? I had to Google it.

And another: I completed the setup but I am not sure I did it
right.

Shristi stopped on the second quote. A user who completed the
setup is not confident they did it right. This is not just a
completion problem — it is a confidence problem. Users who
doubt their goals trust the app less and churn sooner.

Arjun confirmed he can check this in the data. Users who revisit
the goal settings screen multiple times in the first week likely
have lower Day 7 retention than users who set goals once and
never revisit.

Action: Arjun to run goal settings revisit analysis by May 22.

---

**Key Discussion 3 — V2 Priorities and Q3 Roadmap**

Shristi shared the draft Q3 priorities document. Three confirmed
priorities based on Sprint 10 data:

Priority 1 — Simplified onboarding: NPS open text (goal setup
complexity is top complaint), expected funnel analysis confirmation
in Sprint 11.

Priority 2 — Prenatal presets: 3.1x engagement, user interviews
confirming trimester-specific need.

Priority 3 — Custom recipe builder: top NPS feature request,
also the top missing capability for users who cook Indian food.

Arjun gave complexity estimates. Simplified onboarding 2 sprints.
Prenatal presets 1.5 sprints. Custom recipe builder 2 sprints.
All three fit in Q3 if onboarding starts Sprint 12.

Kabir presented an initial sketch for simplified onboarding on
his iPad. 3 questions: what is your main goal, how active are you
(3 plain language options), what is your current weight. EER runs
invisibly. User sees only their personalised calorie goal.

The team reacted positively. Priya said the routing change is
straightforward — the EER form moves to profile settings, not
deleted. New users see the 3-question flow. Existing users are
not affected.

Shristi approved the direction. Sprint 12 begins simplified
onboarding design and implementation. Sprint 12-13 begins prenatal
presets.

---

**User and Market Updates:**

NPS survey live this morning. Full results by May 21.
Dr. Kavitha Rao partnership post went live May 21 — 89 installs
in first 48 hours from tracking link. Partnership performing well.
Instagram following: 487 followers. Engagement rate 4.8%.
MAU trending toward 1,200 by end of May. 47% growth since launch.
Zero paid acquisition. All organic and partnership-driven.

---

**Decisions Made:**

1. Prenatal micronutrient presets confirmed as Q3 priority 2.
   ICMR values to be used over WHO values for Indian users.

2. Pregnancy to be added as fourth health goal option in
   simplified onboarding flow being designed for Sprint 12.

3. Q3 priority order locked: simplified onboarding, prenatal
   presets, custom recipe builder.

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Share pregnant women cohort data with Ravi in investor update | Shristi | May 28 |
| Run goal settings revisit vs Day 7 retention analysis | Arjun | May 22 |
| Complete remaining 2 pregnant women interviews | Ananya | May 22 |
| Finalise Q3 priorities document and share with Ravi | Shristi | May 30 |
| NPS full results shared with team | Ananya | May 21 |

**Next Week Focus:**
Sprint 11 begins May 27. Pure research sprint. Feature adoption
reports for Custom Food and Nutrient Analysis. Formal funnel
analysis confirming goal setup drop-off. Retention cohort analysis.
No new feature work until the research is complete.

---

---

# MEETING NOTE 2 — SPRINT 11
## Weekly Team Sync — June 3, 2025

**Date:** June 3, 2025
**Time:** 11:00 AM IST
**Sprint:** Sprint 11 (May 27 - June 9)
**Attendees:** Shristi Sharmistha, Arjun Mehta, Priya Nair,
Kabir Sharma, Ananya Iyer
**Note taker:** Shristi Sharmistha

---

**Sprint Health Check:**

RES-002 Custom Food report: In progress. 2.3x confirmed.
First-3-sessions insight under investigation.
RES-003 Analysis report: Complete. 67% weekly engagement,
29% lift from AN-CR-001 redesign confirmed.
RES-004 Funnel analysis: Complete. 38% confirmed. Results
being shared today.
RES-005 March interview notes: In progress. Almost complete.
RES-006 Competitive update: Complete. No new threats.
MET-001 May metrics: In progress. Finalising today.
RET-001 Retention cohort: In progress.
BUG-012: Complete. Double-counting fixed.
FUN-001: In progress. March funnel complete. June funnel
being written from RES-004 data.

Overall: 3 of 9 fully complete, 6 in progress. All on track
for June 9 completion.

---

**Key Discussion 1 — 38% Drop-off Confirmed**

Arjun presented the funnel analysis results.

Account creation to profile complete: 94%.
Profile to calorie goal start: 87%.
Calorie goal start to calorie goal complete: 62%.
Goal complete to first food log: 89%.

38% of users who start calorie goal setup do not complete it.
80% of those users churn within 3 days.

Arjun shared the abandon time data. Users who complete the EER
form spend 4.2 minutes on average. Users who abandon spend 1.8
minutes. They are not trying hard and giving up. They see the
form, decide in under 2 minutes that it is too complicated, and
leave.

Kabir's reaction was immediate and honest. He said he designed
the current EER onboarding. He thought detailed meant trustworthy.
He did not consider that detailed could mean intimidating. The
1.8 minute abandon data changes how he thinks about this.

Shristi made the key point: the solution is not a better
explanation of EER. The solution is making EER invisible. The
3-question sketch from Sprint 10 is the right direction. Arjun
confirmed the 3 question inputs map directly to EER formula
parameters — the formula still runs, the user just never sees it.

Priya said the routing change is straightforward. She confirmed
she can build this. The EER form moves to profile settings as
Advanced goal settings. It is not deleted.

Team consensus: simplified onboarding is Sprint 12 top priority.
No further debate needed.

---

**Key Discussion 2 — Custom Food 2.3x Retention and First-3-Sessions Insight**

Shristi shared the RES-002 findings.

Users with at least one custom food: Day 30 retention 34%.
Users with zero custom foods: Day 30 retention 15%.
Ratio: 2.27x rounded to 2.3x. Sample sizes: 287 vs 413 users.
Statistically significant.

But the more important finding: when users create their first
custom food matters as much as whether they create one.

Users who create first custom food in sessions 1-3: Day 30
retention 41%.
Users who create first custom food in sessions 4-10: 27%.
Users who never create custom food: 15%.

The first 3 sessions are the critical personalisation window.

Kabir said this changes the onboarding design. If users who
personalise in the first 3 sessions retain at 41% then onboarding
should actively push users to create their first custom food.
Not as a hidden feature. As part of the core setup flow.

Ananya said the marketing implication is significant. The top 20
custom foods are all Indian foods. Every single entry is a user
solving the Indian food gap problem that every other app failed
to solve. This is the investor story.

Shristi made the product decision: add a custom food creation
nudge as a step in the simplified onboarding. Not mandatory but
prominently placed. Show users the retention benefit explicitly.

---

**Key Discussion 3 — March Interview Notes Connection**

Ananya shared a finding from formalising the March interview notes.

In March 4 of 8 users mentioned goal setup confusion. At the time
the team did not act on it because there was no funnel data to
confirm severity. The funnel data now confirms 38% drop-off.

Shristi said this out loud for the team to hear. The user research
in March told us about goal setup confusion. The NPS survey in May
confirmed it from 23 respondents. The funnel analysis in June
quantified the exact drop-off. We had 3 months of signal before
we acted.

This is the most important process lesson of Q2: when user
research identifies a friction point, do not wait for quantitative
confirmation before acting. User voices are data. We should have
simplified onboarding in Sprint 4, not Sprint 12.

The team was quiet after this. Kabir said the reason we did not
act earlier is that building features felt more productive than
redesigning existing flows. Shristi said that is exactly the
wrong instinct and it is now explicitly named as a team failure
mode to avoid in Q3.

---

**User and Market Updates:**

MAU June 1: 1,456. Growing from 1,247 end of May.
Custom foods cumulative: approximately 430.
Day 7 retention holding at 45%.
App Store: 4.1.
Dr. Nambiar Instagram post driving steady organic installs —
267 total from that single post since May 3.
No new App Store reviews below 3 stars this sprint.

---

**Decisions Made:**

1. Simplified onboarding confirmed as Sprint 12 top priority
   with formal data justification. 38% drop-off, 80% of
   abandoners churn in 3 days, 1.8 minute abandon time.

2. Custom food creation nudge to be included in simplified
   onboarding — first-3-sessions data justifies prominent
   placement in the onboarding flow.

3. Internal testing is not a proxy for real user behaviour.
   Sprint 12 user testing for ONBD-001 must include users who
   previously abandoned the EER onboarding — not just new users.

4. Process change: when user research identifies a friction point
   the team acts within one sprint. No waiting for funnel data
   confirmation of what users already said directly.

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Start ONBD-001 Figma designs | Kabir | June 10 |
| Ananya identifies previous abandoners for Kabir's user testing | Ananya | June 11 |
| Share 38% funnel data with Ravi as Q3 rationale | Shristi | June 12 |
| Arjun builds A/B test infrastructure for Sprint 12 | Arjun | June 13 |
| Finalise RES-002 with data quality note on 847 vs 312 | Shristi | June 4 |

**Next Week Focus:**
Sprint 12 begins June 10. Simplified onboarding design and
implementation. Prenatal presets research and design. Both
features have data justification locked. Time to build.

---

---

# MEETING NOTE 3 — SPRINT 12
## Weekly Team Sync — June 17, 2025

**Date:** June 17, 2025
**Time:** 11:00 AM IST
**Sprint:** Sprint 12 (June 10-23)
**Attendees:** Shristi Sharmistha, Arjun Mehta, Priya Nair,
Kabir Sharma, Ananya Iyer
**Note taker:** Shristi Sharmistha

---

**Sprint Health Check:**

ONBD-001 design: Complete. User tested June 13.
ONBD-002 backend: In progress. Testing complete Friday.
ONBD-003 frontend: In progress. Implementation complete June 19.
PRE-001 research and design: Complete. ICMR values confirmed.
PRE-002 backend: Complete.
MET-002 June week 1: Complete. MAU 1,456.
ONBD-004 A/B test: Complete. Live from June 13.
BUG-013: Complete. Metric definition standardised.
MKT-002: In progress. Pitch document ready.
NPS-002: Complete. Configured for June 30.
PRE-003 frontend: In progress. Sprint 12 scope on track.

Overall: 8 of 11 complete or in progress as planned. On track.

---

**Key Discussion 1 — Simplified Onboarding User Test Results**

Kabir shared the user testing results for ONBD-001.

He tested the Figma prototype with 3 users identified by Ananya
from the funnel data — users who had previously abandoned the
original EER onboarding. All 3 completed the simplified flow.
Average time: 1 minute 43 seconds.

One user quote Kabir read to the team: This is much simpler than
the other app I tried. It just asked me what I need to know.

Priya said she had started implementation on June 12 based on
the approved designs. She expects to complete by June 19.

Arjun shared preliminary A/B test data after the first week:
Simplified group: 84% goal setup completion, 1.9 minutes average.
Control group (EER): 61% completion, 4.1 minutes average.

Shristi calculated this for the team in real numbers. At 1,000
new users the simplified onboarding generates 135 more users who
complete goal setup and have better Day 7 retention. At current
growth rates that is not a small number.

The team agreed this is the most impactful product change since
the custom food creator.

---

**Key Discussion 2 — ICMR vs WHO Prenatal Values Decision**

Kabir presented the prenatal research findings and the ICMR vs
WHO decision.

Key difference: iron 35mg ICMR vs 27mg WHO. B12 2.8mcg vs 2.6mcg.
Calcium T3 1200mg vs 1000mg.

Arjun explained the ICMR rationale. Indian women have higher
baseline rates of iron and B12 deficiency than the global average.
ICMR guidelines account for this. WHO standards are designed for
global populations that do not reflect Indian dietary baselines.

Ananya shared the real-world validation. She showed a photograph
(with user permission) of a prescription from one user's OB-GYN.
The prescribed iron was 45mg — higher than both ICMR and WHO because
this specific user has a diagnosed deficiency. But the ICMR 35mg
is the correct baseline for healthy Indian pregnant women.

The team consensus was clear. Use ICMR values. No dissent.

Shristi added a product decision: the prenatal result screen will
show an attribution line: Targets based on ICMR dietary guidelines
for Indian pregnant women. This is both transparency and
differentiation. No competitor can say this.

Priya raised a product question that needed a decision: when a
user transitions between trimesters does the system update
automatically or manually? Arjun said the backend in PRE-002
supports automatic update if due date is provided. Shristi made
the decision: auto-update with explicit notification showing
exactly which nutrients changed and their new values. Never
silently.

---

**Key Discussion 3 — PRE-003 Carry-Over Plan**

Priya explained the PRE-003 scope split between Sprint 12 and 13.

Sprint 12 scope: pregnancy option in onboarding, trimester
selection screen, prenatal micronutrient result display. On track
for June 20 completion.

Sprint 13 scope: trimester change notification UI, edge cases for
users without due dates, user testing with actual pregnant users,
production deployment.

Shristi confirmed the carry-over is planned and not a concern.
She said explicitly: we planned this from the start of Sprint 12.
PRE-003 carrying to Sprint 13 is the correct scope decision not
a failure to deliver.

One important constraint Shristi added: PRE-003 must be deployed
by June 26 so that pregnant users experience the feature before
the June 30 NPS survey. Their satisfaction with prenatal presets
will be reflected in the NPS score if they have at least 4 days
to use it.

---

**User and Market Updates:**

MAU June 14 (week 2 end): 1,847.
Growth is accelerating. 391 new MAU in week 2 alone.
Day 7 retention: 46%.
Custom foods cumulative: 634.
App Store: 4.1.
NPS-002 configured and ready for June 30.
MKT-002 press pitch document complete. Ananya begins outreach
to maternal health publications next week.

---

**Decisions Made:**

1. ICMR values confirmed for all prenatal presets. Attribution
   line added to prenatal result screen.

2. Trimester auto-update: automatic with explicit notification
   showing specific nutrient changes. Never silent.

3. PRE-003 carry-over to Sprint 13 confirmed. Deployment
   deadline June 26 to capture prenatal user NPS feedback.

4. Day 7 retention standard definition locked: user who opens
   app AND logs at least one food item on exactly day 7 from
   registration date. Applied to all reports and dashboard.

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| ONBD-003 frontend complete | Priya | June 19 |
| ONBD-005 A/B test final results and 100% rollout decision | Arjun | June 24 |
| PRE-003 Sprint 13 scope — notification UI and edge cases | Priya | June 25 |
| User testing PRE-003 with 2 pregnant users | Ananya | June 25 |
| Deploy PRE-003 to production | Priya | June 26 |
| Launch NPS-002 survey | Ananya | June 30 |

**Next Week Focus:**
Final week of Sprint 12. ONBD-003 completes and ships into A/B
test. PRE-003 Sprint 12 scope completes. Then Sprint 13 begins
June 24 — Q2 closure sprint. 7 days. Everything that matters
must ship by June 30.

---

---

# MEETING NOTE 4 — SPRINT 13
## Weekly Team Sync — June 27, 2025

**Date:** June 27, 2025
**Time:** 11:00 AM IST
**Sprint:** Sprint 13 (June 24-30)
**Attendees:** Shristi Sharmistha, Arjun Mehta, Priya Nair,
Kabir Sharma, Ananya Iyer
**Note taker:** Shristi Sharmistha

---

**Sprint Health Check:**

PRE-003-COMPLETE: Complete. Deployed June 26.
BUG-014 (not in original plan): Discovered June 26, fixed
same day within 4 hours.
ONBD-005 simplified onboarding rollout: In progress.
Final A/B results reviewed. 100% rollout on June 28.
MET-003 June metrics: In progress. June week 3 and 4 data
being pulled.
Q2-REVIEW-001: In progress. Shristi writing today.
RET-002 retention cohort: In progress.
INVEST-001: Not started. Sends June 30.
MET-004: Not started. Completes June 30.

Overall: Q2 close on track. All tickets will complete by June 30.

---

**Key Discussion 1 — Prenatal Presets Launch and BUG-014**

Priya led the discussion on the prenatal presets launch and the
bug that followed.

Prenatal presets deployed June 26 at 2 PM IST. By 5 PM 7 of the
11 identified pregnant users had updated to prenatal presets.
By June 27 all 11 had updated. Average setup time: 87 seconds.

Ananya shared user feedback from the two testers from the
interview cohort: finally an app that knows I am in my second
trimester and needs 600mcg folate not just 400mcg.

Then Priya disclosed BUG-014. Discovered 3 hours after deployment.
Folate was displaying as 600mg on the analysis screen instead of
600mcg. Value correct. Unit wrong. Health-critical because 600mg
of folate would be a toxic dose.

Priya explained the root cause: formatNutrient utility had correct
unit mappings for standard RDA nutrients but prenatal preset
nutrients were added with new nutrient IDs. The utility did not
have mappings for these new IDs. It defaulted to mg.

Fix time: 4 hours from discovery to deployment. Shristi confirmed
this meets the health-critical response standard.

Arjun made the technical point: this bug class is harder to catch
than normal bugs because the value is correct and all value-based
tests pass. The error is in the label. We need explicit unit
display tests not just value tests.

Shristi asked the hard question: how did this get through user
testing? Priya checked her testing notes. The 2 testers went
through the onboarding flow but did not navigate to the analysis
screen. The unit error was only visible on the analysis screen.

Shristi named the lesson directly: new feature testing must cover
the complete user journey not just the new screens. This goes in
the definition of done immediately. Any feature touching
micronutrient display must be verified on the analysis screen AND
the onboarding flow.

---

**Key Discussion 2 — A/B Test Final Results and 100% Rollout**

Arjun presented the final 10-day A/B test results.

Control group (EER onboarding):
61.3% goal setup completion. 4.2 minutes average. Day 7 retention 43.1%.

Simplified group (3-question flow):
84.7% completion. 1.8 minutes average. Day 7 retention 47.3%.

Shristi calculated the retention difference in real numbers for
the team. At 1,000 new users, simplified onboarding generates
135 more users who complete setup. Of those completers, 47.3%
return on Day 7 vs 43.1% for EER completers. The retention
improvement compounds.

Priya asked why Day 7 retention is higher not just completion.
Arjun explained: users who complete setup quickly and confidently
have a better first experience. They start logging food sooner.
They build the habit faster. The confidence from a smooth setup
carries through to the first week.

Decision: ship to 100% of new users on June 28. No more A/B test.
EER form moves to Advanced goal settings in profile. The A/B
test code is removed from the codebase. The onboarding_variant
column stays in the database for historical analysis.

---

**Key Discussion 3 — Q2 OKR Review Preview**

Shristi gave the team a preview of the Q2 OKR review she is
writing.

Overall assessment: strong on growth and discovery. Missed the
retention north star by 3 points. Found the segment that changes
Q3 completely.

The honest parts:
Day 7 retention 47% vs 50% target. The cause is identified.
The fix is in motion. The A/B test shows 51.2% retention from
simplified onboarding users. We would have hit the target if
simplified onboarding had shipped earlier.

Earned media 0 articles. Complete failure. Publications want
data and relationships. We now have both. Q3 will approach press
differently.

The proud parts:
MAU 3,512 vs 3,000 target. 315% growth in 2 months. Zero paid.
Custom foods 847 vs 200 target. 312 unique Indian foods.
Prenatal presets shipped. 87 second average setup.
Simplified onboarding shipped. 84.7% completion.
Pregnant women 3.1x engagement confirmed.

Arjun added a technical reflection the team had not discussed
before. The retention improvement from 34% to 47% across Q2
came almost entirely from fixing things not building things.
FoodDiaryContext fixed in Sprint 7. Codebase audit in Sprint 8.
Simplified onboarding in Sprint 12. Three invisible improvements
that users never asked for and never noticed — but that changed
their experience fundamentally.

Kabir said this is the hardest lesson of the project: the most
impactful work is often the work users do not see.

Shristi said this goes in the Q3 OKR as a standing principle:
at least one sprint per quarter dedicated to invisible improvements.
No new features. Only fixes, optimisations, and friction removal.

---

**User and Market Updates:**

MAU June 26: approximately 3,200 and growing.
June 30 target: 3,512 is within reach based on daily growth rate.
Custom foods: 820 as of June 27.
Day 7 retention: 47%.
NPS-002 launches June 30 at 10 AM. Target 40+.
Ananya: 4 press pitches sent to maternal health publications.
No responses yet. Expected — press cycles are slow.

---

**Decisions Made:**

1. Simplified onboarding ships to 100% of users June 28.
   A/B test code removed. EER form in profile settings.

2. Definition of done updated: any feature touching micronutrient
   display must be verified on analysis screen AND onboarding
   flow before deployment.

3. Q3 standing principle: at least one sprint per quarter
   dedicated to invisible improvements — fixes, optimisations,
   friction removal.

4. Press outreach strategy for Q3: relationship-first approach
   with maternal health journalists before pitching the pregnant
   women story.

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Ship simplified onboarding to 100% | Arjun | June 28 |
| Pull final Q2 closing metrics from Supabase | Arjun | June 30 EOD |
| Complete Q2 OKR review and share with Ravi | Shristi | June 30 |
| Send Q2 investor update to Ravi | Shristi | June 30 |
| Launch NPS-002 survey | Ananya | June 30 10 AM |
| Write Q3 OKR draft based on Q2 review | Shristi | July 7 |

**Next Week Focus:**
Q2 closes June 30. Final tasks: metrics verification, Q2 OKR
review, investor update, NPS survey. Then Q3 planning begins
the week of July 7. Q3 priorities are clear: simplified
onboarding as the standard baseline, prenatal features and
marketing, custom recipe builder, and at least one invisible
improvements sprint.

---

---

## SUMMARY TABLE

| Meeting | Date | Sprint | Key Discussions |
|---|---|---|---|
| Meeting Note 10 | May 20, 2025 | Sprint 10 | Pregnant women 3.1x confirmed, NPS 34 first results, V2 priorities |
| Meeting Note 11 | June 3, 2025 | Sprint 11 | 38% drop-off confirmed, 2.3x retention confirmed, March interview connection |
| Meeting Note 12 | June 17, 2025 | Sprint 12 | Simplified onboarding user test results, ICMR vs WHO decision, PRE-003 plan |
| Meeting Note 13 | June 27, 2025 | Sprint 13 | Prenatal launch and BUG-014, A/B test final results, Q2 OKR preview |

---

## GPT-4o GENERATION INSTRUCTIONS

Generate 4 Word documents:
- sprint10_meeting_notes.docx
- sprint11_meeting_notes.docx
- sprint12_meeting_notes.docx
- sprint13_meeting_notes.docx

Save in generated/word/

Use the same CRISPE system prompt from Sprint 1-9 meeting notes.

**Format per document:**
- Header: date, sprint number, attendees
- Sprint Health Check: ticket status table
- Key Discussion 1, 2, 3: full narrative with who said what
- User and Market Updates: specific numbers
- Decisions Made: numbered list
- Action Items: table with Action, Owner, Due Date
- Next Week Focus: brief paragraph

**Content rules:**
- Each discussion must show real debate not just outcomes
- Every person must have a distinct voice
- Decisions must reference specific data points
- Team health and morale must feel authentic

**Critical consistency — all numbers must be exact:**
Sprint 10 meeting: 3.1x engagement, 81.8% Day 7 retention pregnant women
NPS first results May 20: 31 (small sample), final May 21: 34
Sprint 11 meeting: 38% drop-off, 80% churn within 3 days, 1.8 min abandon
Sprint 12 meeting: 84% vs 61% preliminary, 1.9 vs 4.1 minutes
ICMR iron 35mg vs WHO 27mg
Sprint 13 meeting: BUG-014 fixed in 4 hours, 84.7% vs 61.3% final,
47.3% vs 43.1% Day 7 retention, 87 seconds prenatal setup,
all 11 pregnant users updated by June 27
MAU trajectory: Sprint 10 ~1100, Sprint 11 ~1456, Sprint 12 ~1847,
Sprint 13 closing 3512