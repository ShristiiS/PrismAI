## SPRINT 13 CONTEXT

**Sprint dates:** June 24 to June 30, 2025
**Sprint goal:** Complete prenatal presets implementation, ship
simplified onboarding to 100% of users based on A/B test results,
complete Q2 OKR review, and close Q2 with all metrics documented
and verified. This is the final sprint of Q2.
**Total tickets:** 8
**Focus:** Q2 closure, prenatal completion, simplified onboarding
full rollout, investor update

**Metrics at Sprint 13 start (June 24):**
- MAU: approximately 2,891
- Day 7 retention: 47%
- Custom foods: approximately 720
- App Store rating: 4.1

**Metrics at Sprint 13 end (June 30) — LOCKED Q2 CLOSING NUMBERS:**
- MAU: 3,512
- Day 7 retention: 47%
- App Store rating: 4.2
- NPS: 41 (June 30 survey)
- Custom foods: 847
- Simplified onboarding completion: 84% vs 61%
- Pregnant women engagement: 3.1x confirmed
- Goal setting drop-off: 38% confirmed

**Key events this sprint:**
- Prenatal presets completed and shipped June 26
- Simplified onboarding shipped to 100% of users June 28
- Q2 OKR review completed June 30
- Q2 investor update sent to Ravi June 30
- NPS survey June 30 — result 41
- All Q2 metrics locked and verified

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
| PRE-003-COMPLETE | Prenatal presets — complete and ship | Tier 1 | 8 |
| ONBD-005 | Simplified onboarding — ship to 100% of users | Tier 2 | 4 |
| MET-003 | Weekly metrics — June complete and Q2 final numbers | Tier 2 | 4 |
| Q2-REVIEW-001 | Q2 OKR review — all objectives assessed | Tier 1 | 8 |
| RET-002 | Retention cohort analysis — June cohort | Tier 2 | 4 |
| BUG-014 | Prenatal goal values showing wrong units on analysis screen | Tier 2 | 4 |
| INVEST-001 | Q2 investor update to Ravi Kapoor | Tier 3 | 2 |
| MET-004 | June metrics sheet complete and Q2 documentation | Tier 3 | 2 |

**Total comments:** 36

---

## TICKET 1

**Ticket ID:** PRE-003-COMPLETE
**Title:** Prenatal presets — complete and ship
**Type:** Story — Frontend Technical
**Status:** Done
**Priority:** P0
**Assignee:** Priya Nair
**Sprint:** Sprint 13
**Story Points:** 3
**Tier:** Tier 1 (8 comments)

**Description:**
Complete the prenatal micronutrient presets frontend implementation
carried over from Sprint 12. This is Sprint 13 first priority and
must ship before June 26 so that pregnant women users experience
the feature and provide NPS feedback in the June 30 survey.
Remaining Sprint 13 scope: trimester change notification UI, edge
cases for users without due dates, user testing with actual pregnant
users, and production deployment.

**Acceptance Criteria:**
- Trimester change notification UI complete with specific nutrient
  changes listed (e.g. Your folate goal updated from 400mcg to 600mcg)
- Edge case handled: user does not provide due date, manually selects
  trimester, can change trimester selection at any time in profile
- User tested with minimum 2 pregnant users from interview cohort
- Feature deployed to production by June 26
- Existing users who are pregnant prompted to update to prenatal presets
- Zero P0 bugs in first 24 hours post-deployment

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Priya, June 24): Picks up from Sprint 12. Remaining work: notification UI for trimester transitions, edge case handling for users without due date, and final user testing. Notification UI is the most complex remaining piece — needs to show specific nutrient changes not just a generic message.
- Comment 2 (Arjun, June 24): Backend confirmation. Trimester calculation and auto-update logic from PRE-002 is running correctly in staging. Tested with 5 simulated users transitioning through trimesters. All notifications generated correctly with specific nutrient change values.
- Comment 3 (Kabir, June 25): Reviews the trimester change notification UI. One problem — the current notification uses an alert icon and the word Important which makes it look like an error. Changes to a softer design: a green banner notification saying Your pregnancy trimester has updated. Your micronutrient goals have been refreshed. With a tap to review option.
- Comment 4 (Ananya, June 25): Tests the complete prenatal flow with 2 pregnant interview participants who agreed to test. Both complete the prenatal onboarding setup in under 90 seconds. Both confirm the trimester-specific targets match their doctor's recommendations. One says finally an app that knows I am in my second trimester and needs 600mcg folate not just 400mcg.
- Comment 5 (Shristi, June 25): User testing passed. Feature approved for production deployment. The quote from the user is the best product validation we have received since the Indian food gap discovery.
- Comment 6 (Priya, June 26): Feature deployed to production. Existing pregnant users (the 11 identified users) receive an in-app prompt: We added pregnancy support. Update your goals to get trimester-specific micronutrient targets designed for Indian women.
- Comment 7 (Arjun, June 26): Post-deployment monitoring. 7 of the 11 identified pregnant users updated to prenatal presets within 2 hours of the prompt going live. Zero errors in the deployment logs. Notification system working correctly.
- Comment 8 (Shristi, June 27): All 11 identified pregnant women users have now updated to prenatal presets. Average time to complete the prenatal setup: 87 seconds. This is the fastest feature adoption of any feature in the project. These users were waiting for this.

**Cross-references:** PRE-001, PRE-002, PRE-003

---

## TICKET 2

**Ticket ID:** ONBD-005
**Title:** Simplified onboarding — ship to 100% of users
**Type:** Story — Full Stack
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 13
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Based on A/B test final results (84% vs 61% goal setup completion,
1.9 vs 4.1 minutes, Day 7 retention improvement), remove the
control variant and ship simplified onboarding to 100% of new users.
The original EER onboarding is moved permanently to Advanced goal
settings in profile — not deleted. All A/B test code is cleaned
from the codebase.

**Acceptance Criteria:**
- A/B test final results documented before rollout decision
- Simplified onboarding is the only path for all new users
- EER form accessible in profile settings as Advanced goal settings
- A/B test variant column retained in database for analysis
  but no longer used for routing
- All new users from June 28 onwards see simplified onboarding
- Existing users not affected

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 24): Final A/B test results after 10 days. Control EER: 61.3% completion, 4.2 minutes average, Day 7 retention 43.1%. Simplified: 84.7% completion, 1.8 minutes average, Day 7 retention 47.3%. The simplified onboarding improves Day 7 retention by 4.2 percentage points — not just completion rate but actual retention.
- Comment 2 (Shristi, June 24): The Day 7 retention improvement is the most important finding. It means the simplified onboarding did not just help more people set up goals — it helped them have a better first week. Users who complete setup faster and more confidently are more likely to return. Approves 100% rollout immediately.
- Comment 3 (Arjun, June 27): Simplified onboarding shipped to 100% of new users. A/B test routing code removed. EER form moved to profile settings. onboarding_variant column kept in database for historical analysis — not deleted.
- Comment 4 (Shristi, June 28): The simplified onboarding shipped before June 30 means our Q2 closing retention numbers reflect the improvement. The 47% Day 7 retention at Q2 close is partly driven by this change. Q3 will open with this foundation.

**Cross-references:** ONBD-001, ONBD-002, ONBD-003, ONBD-004

---

## TICKET 3

**Ticket ID:** MET-003
**Title:** Weekly metrics — June complete and Q2 final numbers
**Type:** Technical Task
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 13
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Complete the June metrics tracking sheet with all 4 weeks of June
data and document the final Q2 closing numbers. These numbers will
be used in the Q2 OKR review and the investor update to Ravi.
All numbers must be verified against Supabase raw data before
the Q2 OKR review is written.

**Acceptance Criteria:**
- All 4 weeks of June documented in metrics sheet
- Q2 closing numbers confirmed and verified against Supabase:
  MAU 3512, Day 7 retention 47%, App Store 4.2, NPS 41,
  custom foods 847
- Custom food top 10 list updated with June 30 final counts
- Marketing metrics added: Instagram followers, partnership installs
- Numbers ready for Q2 OKR review and investor update

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 28): June weeks 3 and 4 metrics. Week 3 June 15-21: MAU 2,234, Day 7 retention 46%, custom foods 720. Week 4 June 22-28: MAU 2,891, retention 47%, custom foods 789.
- Comment 2 (Arjun, June 30): Final Q2 numbers as of June 30. MAU 3,512. Day 7 retention 47%. App Store 4.2. NPS 41. Custom foods 847. All verified against Supabase raw data. Numbers are clean and auditable.
- Comment 3 (Shristi, June 30): Validates all numbers. Confirms these are the official Q2 closing metrics. Notes the growth trajectory — MAU grew from 847 at May 1 launch to 3,512 at June 30. 315% growth in 2 months with zero paid acquisition.
- Comment 4 (Ananya, June 30): Adds marketing metrics. Instagram 623 followers at 5.2% engagement rate. Nutritionist partnerships: 2 active. Organic installs from Dr. Nambiar: 267. Organic installs from Dr. Kavitha Rao: 145. Total partnership-driven installs: 412.

**Cross-references:** MET-001, MET-002, Q2 OKR

---

## TICKET 4

**Ticket ID:** Q2-REVIEW-001
**Title:** Q2 OKR review — all objectives assessed
**Type:** Product Task
**Status:** Done
**Priority:** P0
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 13
**Story Points:** 3
**Tier:** Tier 1 (8 comments)

**Description:**
Complete the Q2 OKR review document assessing all 4 objectives and
17 key results against actual outcomes. This is the most important
document of Sprint 13. It closes Q2 formally, acknowledges what was
achieved and what was missed honestly, and sets the strategic
narrative for Q3. Shared with the full team and with investor Ravi
Kapoor on June 30.

**Acceptance Criteria:**
- All 4 Q2 objectives assessed with honest outcome rating
- Every KR has actual vs target comparison with real numbers
- Missed KRs explain the real reason for the miss — not a softened version
- Q2 unexpected discovery (pregnant women 3.1x engagement) documented
- Simplified onboarding A/B test result documented as Sprint 13 win
- 3 things to carry into Q3 documented with specific actions
- Review completed and shared by June 30

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Shristi, June 28): Starts Q2 OKR review. Objective 1 Habit Formation: Partial. Day 7 retention 47% vs 50% target — missed by 3 percentage points. The 38% goal setting drop-off is the confirmed cause. Simplified onboarding shipped but too late to move the June 30 closing number. However the A/B test shows 47.3% retention from simplified onboarding users — the target was achievable. Q3 will prove it.
- Comment 2 (Shristi, June 28): Objective 2 Indian Users Coming Back: Exceeded on 4 of 5 KRs. MAU 3,512 vs 3,000 target. Custom foods 847 vs 200 target — 4x above. NPS 41 vs 40 target. App Store 4.2 vs 4.0 target. Indian food retention 31% higher confirmed. The one missed KR: 40% of users logging all 3 meals — actual was 43% so actually exceeded. All 5 KRs achieved or exceeded.
- Comment 3 (Arjun, June 29): Adds data validation note. All Q2 numbers are verified against Supabase raw data. The review can be shared with Ravi with confidence — every number is auditable.
- Comment 4 (Shristi, June 29): Objective 3 Unexpected Discovery: Fully achieved. Pregnant women segment confirmed at 3.1x engagement. 5 user interviews complete. Prenatal presets shipped June 26. Feature adoption report complete. This objective not only achieved — it changed Q3 strategy entirely.
- Comment 5 (Ananya, June 29): Objective 4 Marketing Foundation: Partial. Nutritionist partnerships 2 — achieved. Instagram 623 at 5.2% engagement — achieved. Testimonials 7 — exceeded target of 3. Earned media 0 articles — complete failure. The reason is honest: publications need data and story before writing about an unknown app. We now have both. Q3 plan is to pitch the pregnant women discovery story to maternal health publications.
- Comment 6 (Shristi, June 30): Overall Q2 assessment written. Strong on growth and discovery. Missed retention north star by 3 points — but the cause is identified and the fix is in motion. Found the segment that changes Q3 completely. The product direction is validated.
- Comment 7 (Shristi, June 30): 3 things to carry into Q3 documented. 1: Simplified onboarding now standard — 84% completion vs 61% is proven. Build on this momentum. 2: Prenatal women are Q3 priority — serve them explicitly with trimester presets and marketing to maternal health communities. 3: Build and pitch the data story — Indian food gap data, 2.3x retention correlation, pregnant women 3.1x engagement are all newsworthy. Stop pitching the app. Start pitching the story.
- Comment 8 (Arjun, June 30): Adds a technical note to the review. The three biggest technical decisions of Q2 that paid off: FoodDiaryContext finally implemented (fixed NUTR-BUG-001 and AN-BUG-003), codebase audit creating shared utility functions (ended the fix-one-place-miss-another pattern), and simplified onboarding hiding the EER formula complexity behind 3 questions. These three changes collectively drove the retention improvement from 34% to 47%.

**Cross-references:** Q2 OKR document, MET-003, all RES tickets

---

## TICKET 5

**Ticket ID:** RET-002
**Title:** Retention cohort analysis — June cohort
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 13
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Build the June retention cohort analysis. The key comparison is
simplified onboarding users vs original EER onboarding users.
This is the first cohort that captures the impact of simplified
onboarding on Day 7 retention. Also provides early data on prenatal
presets user retention — the most engaged segment in the product.

**Acceptance Criteria:**
- June cohort overall Day 7 retention documented
- Simplified onboarding cohort (June 28+) vs EER cohort compared
- Pregnant women cohort retention documented separately
- Custom food segmentation maintained from RET-001
- All numbers verified and locked for Q2 OKR review

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 28): Builds June cohort analysis. Overall June cohort Day 7 retention: 47%. Split by onboarding variant: simplified onboarding users 51.2% Day 7 retention vs EER onboarding users 44.1%. This is the first time the 50% target has been exceeded — by simplified onboarding users.
- Comment 2 (Shristi, June 29): The 51% retention from simplified onboarding users is the most important number in this analysis. It confirms the target was achievable — the original onboarding was the barrier. Q3 opens with this proof point.
- Comment 3 (Arjun, June 30): Pregnant women cohort retention. 11 original identified users: 9 of 11 still active at Day 7 (81.8%). 7 new prenatal preset users from June 26 launch: all 7 still active 4 days after. Too early for Day 7 data on the new cohort but 100% Day 4 retention is extraordinary.
- Comment 4 (Shristi, June 30): All June retention data locked for Q2 OKR review. The story is clear: overall 47%, simplified onboarding users 51%, pregnant women 81.8%. Three different user experiences, three different retention levels, all traceable to specific product decisions. This is what good product work looks like.

**Cross-references:** RET-001, ONBD-004, Q2-REVIEW-001

---

## TICKET 6

**Ticket ID:** BUG-014
**Title:** Prenatal goal values showing wrong units on analysis screen
**Type:** Frontend Bug
**Status:** Done
**Priority:** P1
**Assignee:** Priya Nair
**Sprint:** Sprint 13
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Within hours of the prenatal presets launch one pregnant user
reported that folate is showing as 600mg instead of 600mcg on
the analysis screen. This is a critical health display bug. The
value (600) is correct but the unit is wrong. For folate the
distinction between mg and mcg is critical — 600mg of folate
would represent a dangerously high dose. Treated as P1 requiring
fix within 24 hours of discovery.

**Acceptance Criteria:**
- Folate displays as mcg not mg on analysis screen
- B12 and iodine units also verified correct
- Fix deployed within 24 hours of discovery
- formatNutrient shared utility updated with prenatal nutrient mappings
- Regression test added specifically for mcg vs mg display
- All prenatal micronutrients verified against correct ICMR units

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Priya, June 26): Bug confirmed within 3 hours of launch. Root cause: the formatNutrient shared utility has correct unit definitions for standard RDA nutrients but prenatal preset nutrients were added using a different nutrient_id mapping. Folate prenatal preset was correctly stored in the database as mcg but the display layer was reading the wrong unit field from the nutrients reference table.
- Comment 2 (Arjun, June 26): Escalating to P1 immediately. This is a health-critical display bug. A pregnant user seeing 600mg folate displayed could either be alarmed (thinking she is getting a toxic dose) or conversely might not trust the app's accuracy. Neither outcome is acceptable. All other Sprint 13 work paused for Priya until this is fixed.
- Comment 3 (Priya, June 26): Fix deployed within 4 hours of discovery. Updated the formatNutrient utility to correctly map prenatal preset nutrient IDs to their unit definitions in the nutrients reference table. All 8 prenatal micronutrients now display with correct units. Verified: folate mcg, iron mg, calcium mg, vitamin D IU, iodine mcg, B12 mcg, zinc mg, omega-3 g.
- Comment 4 (Shristi, June 27): Fix approved. Adding this to the health-critical features list — any feature that displays micronutrient values covering both mg and mcg nutrients must have explicit unit display test cases before shipping. The formatNutrient utility regression tests have been updated with prenatal-specific test cases. This bug should not have reached production.

**Cross-references:** PRE-001, PRE-003-COMPLETE, formatNutrient utility

---

## TICKET 7

**Ticket ID:** INVEST-001
**Title:** Q2 investor update to Ravi Kapoor
**Type:** Product Task
**Status:** Done
**Priority:** P1
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 13
**Story Points:** 1
**Tier:** Tier 3 (2 comments)

**Description:**
Send the Q2 investor update to Ravi Kapoor with final Q2 metrics,
Q2 OKR review summary, Sprint 13 wins (prenatal presets, simplified
onboarding), and Q3 strategy overview. This is the formal Q2 close
communication with our lead investor.

**Acceptance Criteria:**
- Update sent by June 30
- All final Q2 metrics included and verified
- Q3 priorities clearly articulated with data rationale
- Pregnant women segment framed as the strategic Q3 opportunity
- Simplified onboarding A/B test result highlighted as proof
  that data-driven product decisions work

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Shristi, June 30): Q2 investor update sent to Ravi at 5 PM June 30. Key headline metrics: MAU 3,512 (117% of 3,000 target), NPS 41 (exceeded 40 target), pregnant women 3.1x engagement confirmed, simplified onboarding 84% completion vs 61% previous. Q3 priorities: prenatal features, custom recipe builder, earned media through pregnant women story.
- Comment 2 (Arjun, June 30): Ravi responded same evening. His response: The pregnant women segment is the most interesting thing in this update. 3.1x engagement from users you did not target is the definition of product-market fit for a segment. Build for them in Q3. Also confirms continued support and monthly updates going forward.

**Cross-references:** Q2-REVIEW-001, MET-003

---

## TICKET 8

**Ticket ID:** MET-004
**Title:** June metrics sheet complete and Q2 documentation finalised
**Type:** Technical Task
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 13
**Story Points:** 1
**Tier:** Tier 3 (2 comments)

**Description:**
Finalise the June metrics sheet with week 4 data and lock all Q2
closing numbers. This is the final data documentation task of Q2.
The custom food top 10 list is updated with the final June 30 counts
— this list is the clearest illustration of the Indian food gap
problem being solved by real users.

**Acceptance Criteria:**
- June week 4 (June 22-30) metrics documented
- Final Q2 closing numbers confirmed and locked
- Custom food top 10 list updated with final June 30 counts
- All metrics sheets (MET-001 through MET-004) cross-referenced
  in the Q2 OKR review document

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Arjun, June 30): Final June week 4 numbers confirmed. MAU June 30: 3,512. Custom foods June 30: 847 total entries, 312 unique food names. Top 10 custom foods: Chapati 234, Dal Tadka 187, Homemade Paneer 156, Masala Oats 143, Poha 128, Rajma 112, Chole 98, Upma 87, Paratha 76, Idli 64.
- Comment 2 (Shristi, June 30): The top 10 custom foods list tells the entire Nutrivana story in 10 lines. Every single food was missing from the USDA database. Every single entry is a user solving a problem that MyFitnessPal, HealthifyMe, and Cronometer failed to solve for them. This list goes in the Q3 investor deck.

**Cross-references:** MET-001, MET-002, MET-003, CF-EPIC-001

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 13

Generate one Excel file: sprint13_jira.xlsx
Save in generated/jira/

Sheet 1 — Tickets:
Columns: Ticket ID, Title, Type, Status, Priority, Assignee,
Sprint, Story Points, Description, Acceptance Criteria

Sheet 2 — Comments:
Columns: Ticket ID, Comment Number, Author, Date, Comment Text
One row per comment.

Use the same CRISPE system prompt from Sprints 4-9.

Comment counts must match tier:
PRE-003-COMPLETE: 8 comments (Tier 1)
ONBD-005: 4 comments (Tier 2)
MET-003: 4 comments (Tier 2)
Q2-REVIEW-001: 8 comments (Tier 1)
RET-002: 4 comments (Tier 2)
BUG-014: 4 comments (Tier 2)
INVEST-001: 2 comments (Tier 3)
MET-004: 2 comments (Tier 3)

Critical consistency — ALL numbers must be exact:
MAU June 30: 3,512
Day 7 retention June 30: 47%
App Store rating June 30: 4.2
NPS June 30: 41
Custom foods June 30: 847
Custom food unique food names: 312
Top custom food: Chapati 234 entries
Simplified onboarding completion: 84.7% vs 61.3%
Simplified onboarding time: 1.8 min vs 4.2 min
Simplified onboarding Day 7 retention: 47.3% vs 43.1%
Prenatal presets shipped: June 26
All 11 pregnant users updated to prenatal presets: June 27
Average prenatal setup time: 87 seconds
BUG-014 fix time: within 4 hours of discovery
Ravi's response quote: The pregnant women segment is the most
interesting thing in this update. 3.1x engagement from users
you did not target is the definition of product-market fit for
a segment. Build for them in Q3.
Partnership installs: Dr. Nambiar 267, Dr. Kavitha Rao 145,
total 412
Instagram followers: 623 at 5.2% engagement rate
MAU growth from launch to Q2 close: 847 to 3,512 (315% growth
in 2 months with zero paid acquisition)