# OKR Document Definitions — Corrected and Final
## Q1 2025 and Q2 2025

---

## DOCUMENT 3 (REVISED): OKR DOCUMENT — Q1 2025

**Document name:** Nutrivana Q1 2025 OKRs
**Format:** Excel (.xlsx)
**Date created:** January 1, 2025
**Author:** Shristi Sharmistha
**Period:** January 1 to March 31, 2025
**Reviewed by:** Full team in January 1 kickoff meeting
**Sheets:** 3 sheets — Q1 OKRs, Initiatives List, Q1 Review

---

### SHEET 1: Q1 OKRs

**Column structure:**
Objective | Key Result | KR Type (Output/Outcome) | Target |
Baseline | Current Value | % Complete | Owner | Status | Notes

---

**OBJECTIVE 1:**
Become the most accurate nutrition tracker Indians can actually trust
with their health data

*Context written in document:*
Nutrivana handles health data. If the EER formula is wrong, a user could
eat the wrong number of calories for their body. If data is lost, users
lose their health history. Accuracy and reliability are the foundation
everything else is built on. Before we ask anyone to trust us with their
health, we need to prove we deserve that trust internally.

| Key Result | Type | Target | Baseline | Owner |
|---|---|---|---|---|
| EER formula outputs match USDA reference values within 1% error across all 15 formula variants for 5 diverse test profiles (male/female, ages 19-65, all activity levels) | Outcome | 100% match | 0% verified | Arjun |
| Zero data loss incidents — all logged food persists across logout, browser refresh, and browser close in all test scenarios | Outcome | 0 incidents | Unknown | Arjun/Priya |
| All PRD performance targets met — USDA search under 1 second, diary date switch under 2 seconds, nutrient recalculation under 1 second | Outcome | 100% | 0% tested | Arjun |
| 8 out of 10 internal testers complete full food logging flow end to end without asking for help or hitting a blocking bug | Outcome | 80% | 0% | Shristi |
| Zero RLS data isolation failures — User A cannot read, edit, or delete User B's food logs, goals, or custom foods | Outcome | 0 failures | Untested | Arjun |

---

**OBJECTIVE 2:**
Deeply understand Indian users' nutrition tracking frustrations before
we ask them to use our product

*Context written in document:*
We discovered in Sprint 2 that the USDA database is missing most Indian
foods. But one gap is not enough insight to build a product Indians will
love. We need to know what else is broken for Indian users — what makes
them abandon MyFitnessPal, what language they use to describe their
nutrition goals, what their actual daily eating patterns look like. We
cannot build for Indian users without talking to Indian users.

| Key Result | Type | Target | Baseline | Owner |
|---|---|---|---|---|
| Complete minimum 5 user interviews with health-conscious urban Indians (ages 22-45) identifying their top 3 frustrations with existing nutrition apps | Output (leads to outcome insight) | 5 interviews | 0 | Ananya/Shristi |
| 7 out of 10 waitlist users confirm Indian food database gap as their top 1 or top 2 pain point (validated via pre-launch survey) | Outcome | 70% | Hypothesis only | Ananya |
| Document 20+ Indian foods missing from USDA database with user-confirmed priority ranking for custom food creation order | Outcome | 20 foods | 10 identified Sprint 2 | Shristi |
| Competitive analysis completed comparing Nutrivana vs MyFitnessPal vs HealthifyMe vs Cronometer on Indian food coverage, micronutrient tracking depth, and UX clarity | Output | Done by Feb 28 | 0 | Shristi |

---

**OBJECTIVE 3:**
Ship an MVP the entire team is proud to put in front of real users on
March 31

*Context written in document:*
This is a startup. The first impression is everything. A slow, buggy,
confusing MVP will not get a second chance with Indian health-conscious
users who already have MyFitnessPal and HealthifyMe as alternatives.
We ship on time and we ship with quality. These are not negotiable.

| Key Result | Type | Target | Baseline | Owner |
|---|---|---|---|---|
| Full end-to-end demo completed — new user creates account, sets goals, logs 3 meals, views analysis — zero P0 bugs encountered by March 25 | Output (quality gate) | 1 clean demo | 0 | Shristi |
| Technical architecture spec documenting all major decisions (DB schema, auth, search, timezone handling) approved before any feature implementation | Output (process quality) | Done by Jan 15 | 0 | Arjun |
| Beta waitlist of 150+ users collected and pre-screened (health-conscious Indians, ages 22-45) ready for April 1 invite | Output | 150 users | 0 | Ananya |

---

### SHEET 2: Q1 INITIATIVES LIST

*This sheet lists HOW the team plans to achieve the OKRs above.*
*Each initiative links to specific Jira epics and stories.*

| Initiative | Links to KR | Owner | Sprint | Status |
|---|---|---|---|---|
| USDA bulk import — 300,000 foods into Supabase with GIN + B-tree search indexes | KR: performance targets | Arjun | Sprint 2 | Done |
| EER formula research — all 15 variants across age, gender, activity level | KR: EER accuracy | Arjun | Sprint 1 | Done |
| EER formula implementation with unit tests for all 15 variants | KR: EER accuracy | Arjun | Sprint 2 | Done |
| Supabase RLS policy implementation on all tables | KR: zero isolation failures | Arjun | Sprint 1 | Done |
| Data isolation test suite — User A vs User B scenarios | KR: zero isolation failures | Arjun | Sprint 9 | Done |
| Performance test suite — all PRD timing requirements | KR: performance targets | Arjun | Sprint 6 | Done |
| 5 user interviews — urban Indian health-conscious 22-45 | KR: user interviews | Ananya/Shristi | March | Done |
| Pre-launch waitlist survey — Indian food gap validation | KR: 70% confirm gap | Ananya | February | Done |
| Beta waitlist collection via Instagram + nutritionist network | KR: 150 users | Ananya | Jan-Mar | Done |
| Competitive analysis — MFP vs HealthifyMe vs Cronometer | KR: competitive analysis | Shristi | March | Done late |
| End-to-end demo dry run with full team | KR: clean demo | Shristi | Mar 25 | Done |

---

### SHEET 3: Q1 REVIEW

*Written by Shristi Sharmistha on April 1, 2025*
*Reviewed in April 2 team retrospective*

**Overall Q1 Assessment: Strong on technical delivery. Gaps in user
research and marketing preparation.**

---

**OBJECTIVE 1 — ACCURACY AND RELIABILITY**
Status: ACHIEVED

All 5 KRs achieved by March 31.

EER formula verified against USDA reference values — all 15 variants
correct. Arjun documented the formula matrix in GOAL-002 unit tests.
The BMR two-path validation (GOAL-004) took extra care but was
implemented correctly. GOAL-BUG-005 in Sprint 8 was a regression from
a refactoring — not an original implementation error.

Data persistence fully verified. No data loss incidents in internal
testing. The JWT + refresh token strategy from TECH-003 gives users a
seamless 30-day session experience.

Performance targets all met or exceeded after the batched analysis
query optimisation found in TECH-004 (20 sequential queries → 1 batched
query).

Data isolation verified in TECH-005. Supabase RLS policies are solid.

The end-to-end demo ran cleanly on March 25 with zero blocking bugs.
Team was genuinely proud of what we shipped.

**What went well:** Arjun's systematic approach — write the research
first (spikes), then implement, then test — meant almost no rework on
technical OKRs.

**What to improve:** We should have written regression tests alongside
every implementation. GOAL-BUG-005 in Sprint 8 was a regression from
TECH-004 refactoring that would have been caught by a test.
Tests-first for health-critical features is now a team standard.

---

**OBJECTIVE 2 — USER UNDERSTANDING**
Status: PARTIAL — 2 out of 4 KRs achieved

User interviews completed: 3 out of 5 target. The remaining 2 were
scheduled but Shristi was deep in Sprint 5-6 engineering reviews.
Lesson: user research cannot share bandwidth with engineering oversight.
In Q2 Ananya owns all user research scheduling independently.

Indian food gap validation: 73% of waitlist users confirmed it as top 2
pain point — exceeded 70% target. The custom food feature (fast-tracked
in Sprint 2 after NUTR-TASK-001 discovery) was the right call.

20 Indian foods documented: achieved with 31 specific foods documented
in user research. Top priority foods: Chapati, Dal, Paneer, Rice, Idli,
Dosa, Poha, Rajma, Chole, Sabzi varieties.

Competitive analysis: completed March 15 (2 weeks late). Key finding —
HealthifyMe has better Indian food coverage than MFP but zero
micronutrient tracking. Nutrivana's deep micronutrient tracking is a
genuine differentiator not matched by either competitor.

---

**OBJECTIVE 3 — MVP QUALITY**
Status: ACHIEVED — with one caveat

Clean demo achieved March 25. All team members ran through it without
hitting a P0 bug.

Technical spec approved January 10 — 5 days ahead of target. This
early documentation decision paid off throughout the quarter — every
sprint referenced the spec for architecture consistency.

Beta waitlist: 187 users by March 31 (13 short of 150 target — wait,
187 exceeds 150 target. Actually our stretch goal was 200 — missed that
by 13). Quality of waitlist users is high — 89% are health-conscious
Indian users in 22-40 age range per signup survey.

**The one caveat:** The bar graph user confusion discovered in AN-002
(Sprint 6, 3 days before MVP) means we shipped with a known UX issue
patched rather than properly fixed. AN-CR-001 was created for the proper
redesign. We should not have had this discovery 3 days before launch —
design review with real users should happen in Sprint 4-5 for critical
visualisations, not Sprint 6.

---

**3 Things to carry into Q2:**

1. Ananya owns all user research scheduling independently — no more
   shared bandwidth with engineering oversight
2. Tests-first for all health-critical features (BMR, EER, data
   isolation)
3. User testing of key visualisations (bar graphs, trend charts) happens
   in Sprint 4-5, not Sprint 6

---

---

## DOCUMENT 4 (REVISED): OKR DOCUMENT — Q2 2025

**Document name:** Nutrivana Q2 2025 OKRs
**Format:** Excel (.xlsx)
**Date created:** March 28, 2025
**Author:** Shristi Sharmistha
**Period:** April 1 to June 30, 2025
**Reviewed by:** Full team in March 28 planning session
**Sheets:** 3 sheets — Q2 OKRs, Initiatives List, Q2 Review

---

### SHEET 1: Q2 OKRs

---

**OBJECTIVE 1:**
Prove Nutrivana creates genuine daily nutrition tracking habits —
not just downloads

*Context written in document:*
Downloads are a vanity metric. Any app with a decent Instagram campaign
can get downloads. The only metric that proves we have built something
people actually need is habit formation — do they come back tomorrow,
and the day after, and the day after that? Day 7 retention is our
north star this quarter. If we hit 50% Day 7 retention it means 1 in 2
users who tried Nutrivana is still using it a week later. That is
product-market fit in a health app.

| Key Result | Type | Target | Baseline (Apr 1) | Owner |
|---|---|---|---|---|
| Day 7 retention reaches 50% by June 30 | Outcome | 50% | 34% (beta week 1) | Shristi |
| 40% of active users log food across breakfast, lunch AND dinner at least once per week by end of June | Outcome | 40% | 22% (beta) | Shristi |
| Average food logging streak (consecutive days) reaches 5 days by end of June | Outcome | 5 days | 2.3 days (beta) | Shristi |
| Users who create at least 1 custom food show 2x or higher Day 30 retention vs users who do not | Outcome | 2x | Hypothesis | Arjun/Shristi |

---

**OBJECTIVE 2:**
Make Nutrivana the nutrition app Indian users actually come back to —
not just the one they downloaded once

*Context written in document:*
Our differentiation is Indian food coverage and deep micronutrient
tracking. If users who log Indian foods retain better than those who
do not, we have evidence that our core differentiation is working.
If app store ratings and NPS are improving month over month, we are
building trust. These are the signals that will matter for fundraising
conversations in Q3.

| Key Result | Type | Target | Baseline (Apr 1) | Owner |
|---|---|---|---|---|
| 3000 MAU by June 30 | Output (growth) | 3000 | 0 (pre-launch) | Ananya |
| 200+ custom Indian food entries created by users by June 30 — confirms Indian food gap solution is working | Outcome | 200 | 47 (beta) | Shristi |
| App Store rating reaches 4.0 or above by June 30 | Outcome | 4.0 | 3.8 (beta avg) | Shristi |
| NPS score of 35 or above by end of May, 40 or above by June 30 | Outcome | 35 by May, 40 by June | Unknown (first NPS May 20) | Ananya |
| Users who log Indian foods (via custom food or USDA Indian entries) have 20% higher Day 7 retention than users who do not | Outcome | 20% higher | Hypothesis | Shristi/Arjun |

---

**OBJECTIVE 3:**
Discover one unexpected insight that fundamentally changes what we
build in Q3

*Context written in document:*
Every product that found product-market fit did so by discovering a
user segment or use case they did not plan for. We built Nutrivana for
general health-conscious Indians. But who within that segment is most
engaged? Why are they engaged? What do they need that we have not built?
Finding this one unexpected insight is worth more than shipping 3
planned features. This objective deliberately creates space for
discovery over execution.

| Key Result | Type | Target | Baseline | Owner |
|---|---|---|---|---|
| Identify at least one user segment with 3x or more engagement than overall average by May 31 | Outcome | 1 segment | None identified | Shristi |
| Complete user research with minimum 13 users across 3 different user personas by May 31 | Output | 13 interviews | 3 done in Q1 | Ananya/Shristi |
| 7 out of 10 users validate top 3 V2 features as important enough to prioritise over new user acquisition | Outcome | 70% validation | 0 | Shristi |
| Feature adoption report completed for Custom Food and Nutrient Analysis by May 31 | Output | 2 reports | 0 | Shristi |

---

**OBJECTIVE 4:**
Build a marketing foundation that generates organic trust — not just
paid installs

*Context written in document:*
We are a 5-person team with limited marketing budget. Paid ads will not
scale us to product-market fit. We need organic trust signals —
nutritionist endorsements, press coverage, word of mouth from users who
genuinely love the micronutrient tracking. This quarter we build the
foundation. We are not trying to go viral. We are trying to make the
right 3000 people love us.

| Key Result | Type | Target | Baseline | Owner |
|---|---|---|---|---|
| 2 or more nutritionist partnerships generating active recommendations to their clients | Outcome | 2 | 0 | Ananya |
| Instagram following reaches 500 with engagement rate above 4% (not just follower count) | Outcome | 500 followers + 4% ER | 0 | Ananya |
| At least 3 user testimonials from beta users published on app store and website | Output | 3 testimonials | 0 | Ananya |
| 1 piece of earned media coverage in a health or nutrition publication | Output | 1 article | 0 | Ananya |

---

### SHEET 2: Q2 INITIATIVES LIST

| Initiative | Links to KR | Owner | Sprint | Status |
|---|---|---|---|---|
| Beta launch — 200 users April 1 | MAU, Day 7 retention baseline | Shristi/Ananya | Sprint 7 | Done |
| All P1 beta bugs fixed by April 28 | Day 7 retention, App Store rating | Arjun/Priya | Sprints 7-8 | Done |
| Bar graph redesign (AN-CR-001) | NPS, App Store rating | Kabir/Priya | Sprint 8 | Done |
| Public launch May 1 with full marketing | MAU 3000 | All | Sprint 9 | Done |
| Instagram campaign — fitness and health communities | MAU, Instagram following | Ananya | April-June | In Progress |
| NPS survey round 1 — May 20 | NPS KR | Ananya | May | Done |
| NPS survey round 2 — June 30 | NPS KR | Ananya | June | Done |
| User research — 10 beta users May | Discovery objective | Ananya/Shristi | May | Done |
| User research — pregnant women segment June | Discovery objective | Shristi | June | Done |
| Feature adoption report — Custom Food | Discovery objective | Shristi | May | Done |
| Feature adoption report — Nutrient Analysis | Discovery objective | Shristi | May | Done |
| Nutritionist outreach — 5 approached, 2 target | Nutritionist KR | Ananya | April-May | Partial |
| User testimonial collection from happy beta users | Testimonial KR | Ananya | May | Done |
| App Store listing optimisation — keywords, screenshots | App Store rating | Ananya/Kabir | April | Done |
| Retention cohort analysis — monthly | Day 7 retention KR | Arjun/Shristi | Monthly | Ongoing |
| Custom food retention correlation analysis | Custom food 2x KR | Arjun | June | Done |

---

### SHEET 3: Q2 REVIEW

*Written by Shristi Sharmistha on June 30, 2025*
*Reviewed in July 1 team retrospective*

**Overall Q2 Assessment: Exceeded growth targets. Missed retention
north star by a small but meaningful margin. Found the unexpected
insight that changes everything for Q3.**

---

**OBJECTIVE 1 — HABIT FORMATION**
Status: PARTIAL — 3 out of 4 KRs achieved or exceeded

Day 7 retention: 47% vs 50% target. Close but missed. The funnel
analysis (conducted in June) reveals the drop-off is almost entirely
at the Goal Setting step — 38% of users who complete onboarding
abandon during EER formula setup. The formula is too complex for
casual users. Q3 priority: simplify goal setting to a 3-question
onboarding flow.

3-meal logging (breakfast, lunch, dinner): 43% vs 40% target. Exceeded.
Users who complete goal setting are highly engaged with all meal
sections. The problem is getting users THROUGH goal setting, not
keeping them once they are past it.

Average logging streak: 4.2 days vs 5 day target. Missed. Streak
resets on any missed day — even users who log 6 out of 7 days lose
their streak. Q3 consideration: should streaks be more forgiving
(weekly goals vs daily)?

Custom food 2x retention correlation: CONFIRMED. Users with at least
1 custom food created have 2.3x Day 30 retention vs non-custom-food
users (34% vs 15%). This is our most important product insight of the
quarter. Custom food is not just a feature — it is the mechanism by
which Nutrivana becomes personal to the user. Personalisation drives
retention. Q3 implication: every new user should be nudged to create
their first custom food within the first 3 sessions.

---

**OBJECTIVE 2 — INDIAN USERS COMING BACK**
Status: EXCEEDED on 4 out of 5 KRs

MAU: 3,512 vs 3,000 target. 17% above target. Ananya's Instagram
campaign and the nutritionist partnership with Dr. Priya Nambiar
(Mumbai-based dietitian, 23k followers) drove significant organic
installs in May and June.

Indian food entries: 847 custom food entries created by June 30 vs
200 target. 4x above target. Top 10 Indian foods created by users:
Chapati (234 entries), Dal Tadka (187), Homemade Paneer (156),
Masala Oats (143), Poha (128), Rajma (112), Chole (98), Upma (87),
Paratha (76), Idli (64). The Indian food gap is clearly the most
painful problem we solved.

App Store rating: 4.2 vs 4.0 target. The beta users who reported bugs
and received direct responses from Shristi became our best reviewers.
Community trust built through responsive bug fixing.

NPS: 34 in May, 41 in June. June target of 40 exceeded. The bar
graph redesign (AN-CR-001 deployed in late April) is the single
biggest driver of NPS improvement — the before/after user feedback
is stark.

Indian food retention correlation: Users logging Indian custom foods
show 31% higher Day 7 retention vs non-custom-food users. Exceeded
the 20% target. Indian food personalisation is our retention engine.

---

**OBJECTIVE 3 — UNEXPECTED DISCOVERY**
Status: ACHIEVED — and this insight changes Q3 completely

The unexpected segment: pregnant women.

We did not build Nutrivana for pregnant women. We built it for general
health-conscious Indians. But our June user research (5 interviews with
pregnant women beta users) revealed:

- Pregnant women are 3.1x more engaged than the average user
- They use the micronutrient tracking feature (specifically folate,
  iron, calcium) 4x more than other users
- They have specific doctor-recommended targets that no other app
  supports at the micronutrient level
- They refer other pregnant women — the segment is self-propagating

This discovery immediately becomes the centrepiece of Q3 strategy.
The pregnant women segment validates our core differentiation
(deep micronutrient tracking) better than any other user group.
If we build for them explicitly — supplement tracking, prenatal
micronutrient presets, doctor-recommended target templates — we
create a defensible niche that MyFitnessPal and HealthifyMe cannot
easily copy.

---

**OBJECTIVE 4 — MARKETING FOUNDATION**
Status: PARTIAL — 2 out of 4 KRs achieved

Nutritionist partnerships: 2 active partnerships (Dr. Priya Nambiar,
Mumbai and Dt. Kavitha Rao, Bangalore). Target achieved.

Instagram: 623 followers, 5.2% engagement rate. Both target and
engagement rate exceeded.

User testimonials: 7 published (exceeded 3 target).

Press coverage: 0 articles. No health publication coverage despite
outreach to 4 publications. Lesson: publications want data and case
studies before they will write about an unknown app. We need to build
our own data story (retention numbers, Indian food gap data) and pitch
that as the story in Q3.

---

**3 Things to carry into Q3:**

1. Simplify goal setting onboarding — EER formula complexity is the
   single biggest retention blocker. Target: new user completes goal
   setup in under 3 minutes
2. Build explicitly for pregnant women segment — prenatal micronutrient
   presets, supplement tracking enhancement, doctor-target templates
3. Create and pitch our own data story to press — Indian food gap data,
   custom food retention correlation, pregnant women engagement data
   are all newsworthy. Build the story, then pitch it.

---

## SUMMARY OF CORRECTED OKR DOCUMENTS

| Document | Objectives | Key Results | Key Insight |
|---|---|---|---|
| Q1 OKRs | 3 objectives | 12 KRs | EER accuracy + Indian food gap validated |
| Q2 OKRs | 4 objectives | 17 KRs | Pregnant women 3x engaged, custom food 2.3x retention |

---

## GPT-4o GENERATION INSTRUCTIONS FOR BOTH OKR DOCUMENTS

Generate two Excel files with 3 sheets each.

**For Q1:**
Sheet 1 — Q1 OKRs table with all objectives, key results, types,
targets, baselines, owners. Colour code: green header for objective rows,
white rows for KRs. Include a column for current value (all showing
achieved values since Q1 is complete).
Sheet 2 — Initiatives list as a clean table.
Sheet 3 — Q1 review as formatted text with clear section headers.

**For Q2:**
Same structure. Sheet 1 shows Q2 OKRs with actual achieved values
filled in (since Q2 is also complete at time of generation).
Sheet 3 Q2 review is the most important sheet — write it as a genuine
CEO reflection. The pregnant women discovery should feel like a genuine
surprise that the data revealed, not something the team planned for.

**Tone throughout:**
OKR documents at seed-stage startups are written by someone who is both
the CEO and the PM. The language is direct, honest, and focused on
outcomes not activities. The review sections acknowledge misses clearly
without making excuses. The insights sections show genuine product
thinking — connecting data points to strategic implications.

**Critical accuracy requirements:**
- All numbers must be internally consistent across both documents
  and across all other documents in the dataset
- Day 7 retention: 34% at beta start, 41% by end of April, 45% by
  end of May, 47% by end of June
- MAU: 200 beta users April, 1247 by end of May, 3512 by end of June
- NPS: 34 in May survey, 41 in June survey
- App Store rating: 3.8 during beta, 4.0 by end of May, 4.2 by
  end of June
- Custom Indian food entries: 47 at beta end, 847 by June 30
- These numbers must appear consistently in weekly metrics sheets,
  NPS documents, retention cohort sheets, and all email communications