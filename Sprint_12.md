
## SPRINT 12 CONTEXT

**Sprint dates:** June 10 to June 23, 2025
**Sprint goal:** Begin building the two Q3 priority features —
simplified onboarding and prenatal micronutrient presets. Ship
simplified onboarding to A/B test by end of sprint. Begin prenatal
presets design and backend work. By end of sprint the team has
data proving simplified onboarding works before full rollout.
**Total tickets:** 11
**Focus:** Simplified onboarding design and implementation,
prenatal presets research and design, A/B testing, metrics

**Metrics at Sprint 12 start (June 10):**
- MAU: approximately 1,456
- Day 7 retention: 45%
- App Store rating: 4.1
- Custom foods: approximately 430

**Metrics at Sprint 12 end (June 23):**
- MAU: approximately 2,234
- Day 7 retention: 46%
- Custom foods: approximately 634
- Simplified onboarding A/B test: 84% vs 61% completion confirmed

**Key events this sprint:**
- Simplified onboarding 3-question flow designed and implemented
- A/B test confirms 84% vs 61% goal setup completion
- Prenatal presets ICMR research completed
- Prenatal presets design completed and user tested
- Prenatal frontend implementation started (carries to Sprint 13)
- NPS round 2 set up for June 30

**Team:**
- Shristi Sharmistha — CEO/PM (shristi@nutrivana.in)
- Arjun Mehta — CTO (arjun@nutrivana.in)
- Priya Nair — Frontend (priya@nutrivana.in)
- Kabir Sharma — Designer (kabir@nutrivana.in)
- Ananya Iyer — Marketing (ananya@nutrivana.in)

---

## TICKET TIER STRUCTURE

| Ticket ID | Title | Tier | Comments |
|---|---|---|---|
| ONBD-001 | Simplified onboarding — 3 question flow design | Tier 1 | 8 |
| ONBD-002 | Simplified onboarding — backend implementation | Tier 2 | 4 |
| ONBD-003 | Simplified onboarding — frontend implementation | Tier 2 | 4 |
| PRE-001 | Prenatal micronutrient presets — research and design | Tier 1 | 8 |
| PRE-002 | Prenatal presets — trimester auto-update logic | Tier 2 | 4 |
| MET-002 | Weekly metrics sheet — June week 1 and 2 | Tier 3 | 2 |
| ONBD-004 | Simplified onboarding A/B test setup | Tier 2 | 4 |
| BUG-013 | Retention numbers inconsistent between dashboard and reports | Tier 3 | 2 |
| MKT-002 | Press outreach — building the data story | Tier 3 | 2 |
| NPS-002 | NPS survey round 2 — June 30 | Tier 2 | 4 |
| PRE-003 | Prenatal presets — frontend implementation (partial) | Tier 2 | 4 |

**Total comments:** 46

---

## TICKET 1

**Ticket ID:** ONBD-001
**Title:** Simplified onboarding — 3 question flow design
**Type:** Story — Frontend Design
**Status:** Done
**Priority:** P0
**Assignee:** Kabir Sharma
**Sprint:** Sprint 12
**Story Points:** 5
**Tier:** Tier 1 (8 comments)

**Description:**
Design the complete simplified onboarding flow that replaces the
EER formula setup with a 3-question flow. The funnel analysis in
Sprint 11 confirmed 38% of users abandon at the calorie goal setup
step — 80% of those churn within 3 days. This design is the direct
response to that finding. The user answers three questions and sees
their personalised calorie goal without ever encountering the EER
formula. Must be user tested with minimum 5 users before
implementation begins.

**Acceptance Criteria:**
- 3-question flow designed in Figma with all states and transitions
- Each question fits on one screen — no scrolling
- Activity level options use plain everyday language not exercise science terms
- Result screen shows personalised calorie goal with one clear sentence explanation
- Adjust manually option provided for users who want fine control
- Pregnancy added as fourth health goal option (separate from main 3-question flow)
- User tested with minimum 5 users including users who previously
  abandoned the original EER onboarding
- Progress indicator shows users how many questions remain

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Kabir, June 10): Presents initial design. Question 1 What is your main goal — 3 options: Lose weight, Gain weight, Maintain weight. Question 2 How active are you — 3 options: Lightly active (office work with some walking), Moderately active (some exercise most days), Very active (daily exercise or physical job). Question 3 What is your current weight — simple kg input. Result screen shows personalised calorie goal with a single sentence.
- Comment 2 (Shristi, June 11): Activity level descriptions are good. One concern — the health goal options feel clinical. Proposes warmer language: instead of Lose weight use Lose some weight. Instead of Gain weight use Build muscle or gain weight. The language should feel like a conversation not a medical form.
- Comment 3 (Arjun, June 11): Technical note on the mapping. Question 1 maps to weight_goal_type. Question 2 maps to activity_level multiplier — Lightly active 1.375, Moderately active 1.55, Very active 1.725. Question 3 maps to current_weight_kg. Age and gender must still be collected but move them to profile settings after the user sees their initial goal.
- Comment 4 (Kabir, June 12): Age and gender moved to profile completion step that comes after the user sees their first calorie goal. User gets the immediate win — here is your goal — before being asked for more personal information. Better onboarding psychology. Adds a step indicator showing 1 of 3, 2 of 3, 3 of 3.
- Comment 5 (Ananya, June 12): Tests the Figma prototype with 3 waitlist users who previously abandoned the original EER onboarding (identified from funnel data). All 3 complete the simplified flow. Average time: 1 minute 43 seconds. One says: this is much simpler than the other app I tried. It just asked what I need to know.
- Comment 6 (Shristi, June 13): User testing passed. 3 of 3 completions from users who previously abandoned. This is the strongest validation data in the project. Approves proceeding to implementation.
- Comment 7 (Kabir, June 16): Full Figma designs complete for all states. Question screens, result screen, profile completion screen, adjust manually flow, progress indicators. Also designed the pregnancy variant — when user selects Pregnant on the health goal screen a fourth question appears asking which trimester.
- Comment 8 (Priya, June 17): Reviews designs from frontend implementation perspective. Request — the result screen needs both a Looks right CTA and an Adjust manually option. Some users will want to override the calculated goal. The Adjust manually option should link to the full EER onboarding which is being moved to profile settings — not deleted.

**Cross-references:** RES-004, FUN-001, V2-PLAN-001

---

## TICKET 2

**Ticket ID:** ONBD-002
**Title:** Simplified onboarding — backend implementation
**Type:** Story — Backend
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 12
**Story Points:** 5
**Tier:** Tier 2 (4 comments)

**Description:**
Implement the backend changes for simplified onboarding. The existing
EER formula logic is unchanged — only the API interface changes. The
new onboarding endpoint accepts a simplified 3-field input and maps
to the full EER parameters internally. Age and gender are optional
with statistical defaults. When the user later adds these in profile
the goal auto-recalculates using the GOAL-BUG-002 fix logic already
in production.

**Acceptance Criteria:**
- New onboarding API endpoint accepts simplified input:
  goal type, activity description, current weight
- EER calculation runs with full accuracy internally
- Age defaults to 30, gender defaults to neutral EER average
  if not provided at onboarding time
- When user later adds age and gender goal auto-recalculates
- All GOAL-BUG-002 profile change listener logic applies
- New endpoint has tests covering all 3 question combinations

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 10): Designs the new endpoint. Activity description maps to multiplier via lookup table. Lightly active 1.375, Moderately active 1.55, Very active 1.725. These are the three most statistically common activity levels in the existing user base. Default age 30 and gender neutral average produces EER within 150-250 calories of the exact value for most users — close enough for day 1, corrected when profile is completed.
- Comment 2 (Shristi, June 11): Asks about accuracy impact of the defaults. A 45 year old woman and a 22 year old man both getting the neutral default — how wrong could that be?
- Comment 3 (Arjun, June 12): Maximum error with neutral defaults is approximately 250 calories for extreme cases. This is much smaller than the 500+ calorie error from GOAL-BUG-002. And critically when the user completes their profile the recalculation brings them to exact accuracy. The simplified flow trades minor initial imprecision for a 38 percentage point improvement in completion rate.
- Comment 4 (Arjun, June 18): Backend complete and tested. 20 test profiles run. All within 200 calories of full EER calculation for the neutral defaults. Profile completion trigger for recalculation confirmed working correctly.

**Cross-references:** GOAL-001, GOAL-BUG-002, ONBD-001

---

## TICKET 3

**Ticket ID:** ONBD-003
**Title:** Simplified onboarding — frontend implementation
**Type:** Story — Frontend Technical
**Status:** Done
**Priority:** P0
**Assignee:** Priya Nair
**Sprint:** Sprint 12
**Story Points:** 5
**Tier:** Tier 2 (4 comments)

**Description:**
Implement the simplified onboarding frontend based on Kabir's
approved Figma designs. Replace the existing EER formula onboarding
screens with the 3-question flow. The existing detailed goal setting
screens are not deleted — they are moved to profile settings as
Advanced goal settings accessible to users who want fine control.

**Acceptance Criteria:**
- 3-question onboarding flow replaces EER formula screens for new users
- Pregnancy variant shows trimester question when Pregnant is selected
- Result screen shows personalised goal with Looks right and
  Adjust manually options
- Adjust manually links to Advanced goal settings in profile
- Old EER onboarding moved to profile settings not deleted
- Existing users not affected — they see their existing goals unchanged
- Completion trackable per user for A/B test measurement

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Priya, June 12): Implementation started. Main complexity is routing — new users go to simplified flow, existing users returning to goal settings go to the full EER form. Solving with an is_new_user flag in the routing logic.
- Comment 2 (Priya, June 17): Implementation complete. Routing works correctly. One design improvement made during implementation — the calorie goal display on the result screen was showing 1847 kcal per day and the per day was redundant since kcal implies daily. Changed to 1847 kcal with subtitle Your daily calorie goal. Cleaner.
- Comment 3 (Kabir, June 18): Design review complete. All screens match Figma. Progress indicators working. Pregnancy variant showing trimester question correctly. Looks right CTA and Adjust manually both functional.
- Comment 4 (Shristi, June 19): Testing the flow on a fresh account. Completed in 1 minute 47 seconds from registration to first goal set. Target was under 3 minutes. Well within. Approved for A/B test deployment.

**Cross-references:** ONBD-001, ONBD-002

---

## TICKET 4

**Ticket ID:** PRE-001
**Title:** Prenatal micronutrient presets — research and design
**Type:** Story — Frontend Design
**Status:** Done
**Priority:** P1
**Assignee:** Kabir Sharma
**Sprint:** Sprint 12
**Story Points:** 5
**Tier:** Tier 1 (8 comments)

**Description:**
Research the clinically accurate trimester-specific micronutrient
targets for pregnancy and design the prenatal presets feature.
This is the Q3 priority 2 feature driven by the 3.1x engagement
discovery from Sprint 10. Critical requirement: values must be
sourced from ICMR (Indian Council of Medical Research) guidelines
not just WHO — Indian pregnant women have different baseline
nutritional profiles and ICMR accounts for this.

**Acceptance Criteria:**
- Research sourced from ICMR and FSSAI prenatal nutrition guidelines
- Trimester-specific targets defined for minimum 8 nutrients:
  folate, iron, calcium, vitamin D, iodine, zinc, B12, omega-3
- Pregnancy added as fourth option on health goal question
- Trimester selection screen designed for Q1 Q2 Q3 options
- Prenatal result screen shows which nutrients will be preset
- User tested with minimum 3 pregnant users before implementation
- B12 ICMR value (2.8mcg) used not WHO value (2.6mcg) for
  vegetarian Indian women baseline

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Shristi, June 10): Assigns prenatal research to Kabir with specific instruction — use ICMR guidelines not just WHO. Indian pregnant women, especially vegetarians, have different baseline nutritional statuses. ICMR publishes India-specific dietary reference values.
- Comment 2 (Kabir, June 12): Research complete. Key ICMR trimester targets. Folate: 400mcg T1, 600mcg T2, 500mcg T3. Iron: 35mg all trimesters (ICMR recommends 35mg for Indian women vs WHO 27mg due to higher baseline iron deficiency prevalence). Calcium: 1000mg T1-T2, 1200mg T3. Vitamin D: 600 IU all trimesters. Iodine: 220mcg all trimesters. B12: 2.8mcg all trimesters. Zinc: 11mg all trimesters.
- Comment 3 (Arjun, June 13): The B12 concern is particularly important for the Indian context. Vegetarian Indian women have significantly higher rates of B12 deficiency than the global average. The ICMR 2.8mcg vs WHO 2.6mcg difference is small in absolute terms but reflects a real population health difference. Using ICMR is the right call for our user base.
- Comment 4 (Ananya, June 13): Validates with one interviewed pregnant user (with permission). Her OB-GYN prescribed 35mg iron and 600mcg folate in second trimester — exactly matching ICMR values not WHO values. This real-world validation confirms using ICMR is clinically correct for Indian users.
- Comment 5 (Kabir, June 14): Design complete. Pregnancy flow: user selects Pregnant on health goal question. New question appears: Which trimester — First weeks 1-12, Second weeks 13-26, Third weeks 27-40. Result screen shows personalised prenatal targets for the 4 most critical nutrients (folate, iron, calcium, vitamin D) with See all 8 nutrients expandable section.
- Comment 6 (Shristi, June 15): One design change. The pregnancy detection trigger Kabir originally proposed was too complex. Adding Pregnant as the fourth option directly to the main health goal question is simpler and more direct. Users who are pregnant know they are pregnant — no detection needed.
- Comment 7 (Kabir, June 16): Agreed. Pregnant added as fourth option to Question 1. If selected Question 2 becomes Which trimester. Question 3 remains current weight. Pregnant users go through a 4-question flow vs 3 for other users. Clean and logical.
- Comment 8 (Priya, June 17): Reviews designs. One critical product question raised — when a user transitions from first to second trimester does the system automatically update their micronutrient goals or do they manually change? This needs a decision before implementation begins.

**Cross-references:** MON-002, RES-001, V2-PLAN-001

---

## TICKET 5

**Ticket ID:** PRE-002
**Title:** Prenatal presets — trimester auto-update logic
**Type:** Story — Backend
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 12
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Design and implement the backend logic for automatic trimester
transitions. When a pregnant user provides their expected due date
the system calculates their current trimester and updates their
micronutrient goals when they transition between trimesters.
The auto-update pattern mirrors the GOAL-BUG-002 fix — profile
changes automatically trigger goal recalculation with user notification.

**Acceptance Criteria:**
- User can optionally enter expected due date during pregnancy onboarding
- System calculates current trimester from due date
- Weekly check at midnight IST detects trimester transitions
- On transition: in-app notification sent with specific nutrient changes
  listed (e.g. Your folate goal updated from 400mcg to 600mcg)
- User can manually override if auto-calculation is wrong
- If no due date provided user manually selects current trimester
- pregnancy_due_date, pregnancy_trimester, last_trimester_check
  columns added to user_profiles

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 13): Designs trimester calculation. If due date provided: weeks remaining = (due_date - today) / 7. T1 = 40-28 weeks remaining. T2 = 27-14 weeks remaining. T3 = 13-0 weeks remaining. Weekly check runs at midnight IST using the date_string timezone approach from NUTR-022.
- Comment 2 (Shristi, June 14): Approves. Critical requirement — the auto-update must never happen silently. User must see a notification showing exactly which goals changed and what the new values are. Not a generic goals updated message. Specific changes listed.
- Comment 3 (Arjun, June 17): Implementation complete. Three new columns in user_profiles: pregnancy_due_date (nullable date), pregnancy_trimester (1/2/3 nullable), last_trimester_check (date). Notification template includes the exact changed values.
- Comment 4 (Shristi, June 18): Approved. The GOAL-BUG-002 lesson applied correctly — any auto-change to health-critical goals must notify the user with specific numbers not generic messages. Users deserve to know exactly what changed.

**Cross-references:** PRE-001, GOAL-BUG-002

---

## TICKET 6

**Ticket ID:** MET-002
**Title:** Weekly metrics sheet — June week 1 and 2
**Type:** Technical Task
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 12
**Story Points:** 1
**Tier:** Tier 3 (2 comments)

**Description:**
Document weekly metrics for June weeks 1 and 2 in the June
metrics tracking sheet. Continued from the May metrics sheet
format established in MET-001.

**Acceptance Criteria:**
- Week 1 (June 1-7) and Week 2 (June 8-14) metrics documented
- All key metrics tracked: MAU, DAU, Day 7 retention, custom foods,
  App Store rating, session length
- Numbers verified against Supabase raw data

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Arjun, June 9): June week 1 metrics. MAU 1,456. Day 7 retention 45%. Custom foods cumulative 512. App Store rating 4.1.
- Comment 2 (Arjun, June 16): June week 2 metrics. MAU 1,847. Day 7 retention 46%. Custom foods cumulative 634. App Store rating 4.1. Growth accelerating — 391 new MAU in one week.

**Cross-references:** MET-001, Q2 OKR

---

## TICKET 7

**Ticket ID:** ONBD-004
**Title:** Simplified onboarding A/B test setup
**Type:** Story — Full Stack
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 12
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Set up a proper A/B test to measure the impact of simplified
onboarding on goal setup completion rate and Day 7 retention.
50% of new users see the original EER onboarding. 50% see the
simplified 3-question flow. Results after 7 days determine whether
to ship simplified onboarding to 100% of users in Sprint 13.

**Acceptance Criteria:**
- A/B test assignment implemented at account creation
- onboarding_variant column in user_profiles with values control
  or simplified
- 50/50 random split on new user registration
- Goal setup completion tracked per variant
- Time to complete onboarding tracked per variant
- Day 7 retention tracked per variant
- Test runs minimum 7 days before results are read

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 13): A/B test setup complete. Random assignment at account creation using a simple modulo on user ID. onboarding_variant column added to user_profiles. 50/50 split confirmed across first 100 registrations.
- Comment 2 (Shristi, June 14): Asks Arjun to also track time-to-complete-onboarding as a metric — not just completion rate. The hypothesis is more users complete AND they complete faster. Both parts need data.
- Comment 3 (Arjun, June 18): First week A/B results preliminary. Control group EER: 61% goal setup completion, average 4.1 minutes. Simplified group: 84% completion, average 1.9 minutes. The hypothesis is confirmed on both dimensions.
- Comment 4 (Shristi, June 19): 84% vs 61% completion and 1.9 vs 4.1 minutes. This is the most impactful product change since the custom food creator. Confirms shipping simplified onboarding to 100% of users in Sprint 13 pending final 10-day A/B results.

**Cross-references:** ONBD-001, ONBD-002, ONBD-003

---

## TICKET 8

**Ticket ID:** BUG-013
**Title:** Retention numbers inconsistent between dashboard and reports
**Type:** Backend Bug
**Status:** Done
**Priority:** P2
**Assignee:** Arjun Mehta
**Sprint:** Sprint 12
**Story Points:** 2
**Tier:** Tier 3 (2 comments)

**Description:**
Shristi noticed the Day 7 retention on the MON-001 dashboard shows
46% but the retention cohort analysis in RET-001 shows 45% for the
same period. The discrepancy is small but undermines data credibility
for investor communications. Root cause is different definitions of
Day 7 retention being used in different places.

**Acceptance Criteria:**
- Root cause of discrepancy identified and documented
- Both metrics standardised on the same definition
- Definition documented formally: Day 7 retention equals user who
  opens app AND logs at least one food item on exactly day 7
  from registration date
- All existing reports updated to use standard definition

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Arjun, June 14): Root cause found. Dashboard counts Day 7 as user who logged in on day 7. Cohort analysis counts user who logged food in days 6-8 (3-day window). Different definitions. Standardising on the stricter definition — must log food on exactly day 7.
- Comment 2 (Arjun, June 16): Standard definition applied everywhere. Day 7 retention locked definition: user who opens app AND logs at least one food item on exactly day 7 from registration date. All reports and dashboard now use this definition.

**Cross-references:** MON-001, RET-001

---

## TICKET 9

**Ticket ID:** MKT-002
**Title:** Press outreach — building the data story
**Type:** Marketing Task
**Status:** In Progress
**Priority:** P2
**Assignee:** Ananya Iyer
**Sprint:** Sprint 12
**Story Points:** 2
**Tier:** Tier 3 (2 comments)

**Description:**
Build the press-ready data story for outreach to health and nutrition
publications. The Q2 OKR review identified earned media as a
complete failure — 0 articles — because previous pitches lacked
compelling data. This sprint Ananya builds 3 data-driven story
angles that publications will actually want to cover.

**Acceptance Criteria:**
- Press pitch document with 3 story angles created
- Angle 1: Indian food gap in nutrition apps — quantified with data
- Angle 2: Pregnant women segment discovery — 3.1x engagement story
- Angle 3: Custom food personalisation drives 2.3x retention
- Pitch ready for outreach in Sprint 13

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Ananya, June 16): Draft press pitch complete. Three angles ready. Angle 2 (pregnant women discovery) is the most newsworthy — an unexpected segment finding with 3.1x engagement is a genuine product story. Angle 1 (Indian food gap) is the evergreen story. Angle 3 (retention correlation) is more of a business metric than press story — moving it to investor update.
- Comment 2 (Shristi, June 19): Reviews pitch. Approves angles 1 and 2 for press. Angle 3 moves to investor communications as Ananya suggested. Outreach to maternal health publications starts Sprint 13 — the pregnant women story is the strongest angle for earning media coverage.

**Cross-references:** Q2 OKR Objective 4

---

## TICKET 10

**Ticket ID:** NPS-002
**Title:** NPS survey round 2 — June 30
**Type:** Story — Full Stack
**Status:** Done
**Priority:** P1
**Assignee:** Ananya Iyer
**Sprint:** Sprint 12
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Set up and launch the second formal NPS survey on June 30 to
measure Q2 closing NPS. Target is 40 or above per Q2 OKR KR.
The survey uses the same format as NPS-001 with one additional
question measuring simplified onboarding satisfaction for users
who went through the new flow.

**Acceptance Criteria:**
- Survey set up and ready to launch June 30
- Standard NPS question plus open text improvement question
- Additional question for simplified onboarding users:
  How easy was it to set up your nutrition goals (1-5 scale)
- Returning users from May survey see slightly different message
- Results available same day for Q2 OKR review

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Ananya, June 13): Sets up June 30 NPS survey. Adds the simplified onboarding satisfaction question. Users who went through simplified flow (onboarding_variant = simplified) see the extra question. Control group users do not.
- Comment 2 (Arjun, June 14): Implements the variant-aware survey trigger. Users who completed the May survey see a message acknowledging they already gave feedback once: We have made improvements since May. We would love your updated view.
- Comment 3 (Ananya, June 30): Survey launched at 10 AM June 30. Preliminary results by 6 PM.
- Comment 4 (Ananya, June 30): Final results. 312 responses from approximately 2,100 active users (15% response rate). NPS 41 — exceeds Q2 target of 40. Simplified onboarding satisfaction: 4.2 out of 5 from users who used the new flow. Goal setup mentioned positively in open text for the first time — setting goals is much easier now from 23 respondents.

**Cross-references:** NPS-001, Q2 OKR Objective 2, ONBD-003

---

## TICKET 11

**Ticket ID:** PRE-003
**Title:** Prenatal presets — frontend implementation (partial)
**Type:** Story — Frontend Technical
**Status:** In Progress
**Priority:** P1
**Assignee:** Priya Nair
**Sprint:** Sprint 12
**Story Points:** 5
**Tier:** Tier 2 (4 comments)

**Description:**
Implement the prenatal presets frontend based on Kabir's approved
designs. This ticket starts in Sprint 12 and carries over to Sprint 13.
Sprint 12 scope: pregnancy option in onboarding, trimester selection
screen, prenatal micronutrient result display. Sprint 13 scope:
trimester change notification UI, edge cases, user testing, and
production deployment.

**Acceptance Criteria Sprint 12:**
- Pregnancy option added to onboarding health goal question
- Trimester selection screen implemented and functional
- Prenatal micronutrient targets display correctly on result screen
- Top 4 nutrients visible by default, 4 more in expandable section

**Acceptance Criteria Sprint 13:**
- Trimester change notification UI complete
- Edge cases handled: no due date provided, manual trimester override
- User tested with pregnant users
- Feature deployed to production

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Priya, June 17): Implementation started. Pregnancy option added to onboarding goal question. Conditional routing working — selecting Pregnant shows trimester question, other options skip it. State management is cleaner than expected.
- Comment 2 (Kabir, June 18): Reviews first build in staging. One design note — prenatal result screen showing all 8 nutrients at once is overwhelming on mobile. Suggests default showing only the 4 most critical with expandable section for the other 4.
- Comment 3 (Priya, June 19): Updated with expandable section. Cleaner. Top 4 visible: folate, iron, calcium, vitamin D. Expandable shows: iodine, B12, zinc, omega-3.
- Comment 4 (Shristi, June 20): Good progress but carrying over to Sprint 13 as planned. Sprint 12 deliverables are complete. Remaining Sprint 13 work: trimester notification UI, edge cases, user testing with actual pregnant users, production deployment.

**Cross-references:** PRE-001, PRE-002

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 12

Generate one Excel file: sprint12_jira.xlsx
Save in generated/jira/

Sheet 1 — Tickets:
Columns: Ticket ID, Title, Type, Status, Priority, Assignee,
Sprint, Story Points, Description, Acceptance Criteria

Sheet 2 — Comments:
Columns: Ticket ID, Comment Number, Author, Date, Comment Text
One row per comment.

Use the same CRISPE system prompt from Sprints 4-9.

Comment counts must match tier:
ONBD-001: 8 comments (Tier 1)
ONBD-002: 4 comments (Tier 2)
ONBD-003: 4 comments (Tier 2)
PRE-001: 8 comments (Tier 1)
PRE-002: 4 comments (Tier 2)
MET-002: 2 comments (Tier 3)
ONBD-004: 4 comments (Tier 2)
BUG-013: 2 comments (Tier 3)
MKT-002: 2 comments (Tier 3)
NPS-002: 4 comments (Tier 2)
PRE-003: 4 comments (Tier 2)

Critical consistency:
Simplified onboarding A/B test: 84% simplified vs 61% control
Time to complete: 1.9 minutes simplified vs 4.1 minutes control
MAU June week 1: 1,456. June week 2: 1,847
Day 7 retention: 45-46% during this sprint
NPS June 30: 41
Custom foods cumulative June 23: approximately 634
ICMR iron for Indian pregnant women: 35mg (not WHO 27mg)
ICMR folate T2: 600mcg
PRE-003 is a partial implementation — carries to Sprint 13