# Sprint 11 Ticket Definitions
## May 27 to June 9, 2025

---

## SPRINT 11 CONTEXT

**Sprint dates:** May 27 to June 9, 2025
**Sprint goal:** Complete all research and analysis documents that
provide the data foundation for Q3 decisions. By end of sprint
the team has formally confirmed the custom food 2.3x retention
correlation, the 38% goal setting drop-off, and the pregnant women
3.1x engagement finding. No new features this sprint — only research.
**Total tickets:** 9
**Focus:** Research reports, funnel analysis, feature adoption,
metrics documentation

**Metrics at Sprint 11 start (May 27):**
- MAU: approximately 1,247 (end of May confirmed)
- Day 7 retention: 45%
- App Store rating: 4.0
- NPS: 34 (May 20 survey)
- Custom foods: approximately 300

**Metrics at Sprint 11 end (June 9):**
- MAU: approximately 1,456 (June week 1)
- Day 7 retention: 45%
- Custom foods: approximately 430
- App Store rating: 4.1

**Key events this sprint:**
- Custom food 2.3x Day 30 retention formally confirmed
- First-3-sessions custom food insight discovered
- 38% goal setting drop-off confirmed via funnel analysis
- Retention cohort analysis completed for May cohort
- Customer interview notes from March formally documented

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
| RES-002 | Feature adoption report — Custom Food Creator | Tier 1 | 8 |
| RES-003 | Feature adoption report — Nutrient Analysis | Tier 2 | 4 |
| RES-004 | Goal setting funnel analysis — 38% drop-off | Tier 1 | 8 |
| RES-005 | Customer interview notes — 8 beta users March | Tier 2 | 4 |
| RES-006 | Competitive analysis update — post-launch | Tier 3 | 2 |
| MET-001 | Weekly metrics sheet — May complete | Tier 2 | 4 |
| RET-001 | Retention cohort analysis — May cohort | Tier 2 | 4 |
| BUG-012 | Trend chart double-counting supplement logs | Tier 3 | 2 |
| FUN-001 | Funnel analysis report — March and June | Tier 2 | 4 |

**Total comments:** 40

---

## TICKET 1

**Ticket ID:** RES-002
**Title:** Feature adoption report — Custom Food Creator
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 11
**Story Points:** 3
**Tier:** Tier 1 (8 comments)

**Description:**
Write a comprehensive feature adoption report for the Custom Food
Creator feature. This is the most important research document of Q2
because it formally confirms the 2.3x Day 30 retention correlation
first observed in Sprint 9. The report covers total adoption rate,
types of foods being created, the retention correlation, the
first-3-sessions insight, and regional patterns in what Indian foods
are most frequently added. This report will be referenced in the Q2
OKR review and the Series A investor story.

**Acceptance Criteria:**
- Report documents total custom foods created (847 by June 30)
- Adoption rate calculated as percentage of active users who
  created at least one custom food
- Top 20 custom foods listed with count per food
- 2.3x Day 30 retention formally confirmed with sample sizes
- First-3-sessions insight documented with data
- Unique food names vs total entries distinction documented
- Recommendations for Q3 onboarding based on retention data

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Shristi, May 27): Starts the report. Pulls initial data from Supabase. 312 unique food names created across all users. 847 total entries (counting duplicates across users). Top 3: Chapati 234 entries, Dal Tadka 187, Homemade Paneer 156. Asks Arjun to run the formal retention correlation.
- Comment 2 (Arjun, May 28): Formal retention analysis complete. Users with at least 1 custom food — Day 30 retention: 34%. Users with 0 custom foods — Day 30 retention: 15%. Sample sizes: 287 users in custom food group, 413 users in non-custom-food group. Ratio: 2.27x. Rounds to 2.3x as reported.
- Comment 3 (Shristi, May 28): 2.3x confirmed. More importantly asks Arjun to check WHEN users create their first custom food relative to registration date. Hypothesis — users who personalise in the first 3 sessions retain much better than those who personalise later.
- Comment 4 (Arjun, May 29): Hypothesis confirmed. Users who create first custom food within sessions 1-3: Day 30 retention 41%. Users who create first custom food in sessions 4-10: Day 30 retention 27%. Users who never create custom food: 15%. The first 3 sessions are the critical personalisation window.
- Comment 5 (Kabir, May 29): This changes the onboarding design conversation. If the first 3 sessions are the critical window then onboarding should actively push users to create their first custom food — not as an optional discovery feature but as a core part of the setup flow. Proposes adding an "Add your first Indian food" step to onboarding.
- Comment 6 (Ananya, May 30): The top 20 foods list tells the Indian food gap story with data. All 20 are Indian foods. Not a single Western food. Every single entry is a user solving a problem the USDA database created for them. This is the marketing story for the next investor update.
- Comment 7 (Shristi, June 2): Report draft complete. Key recommendation added: include custom food creation as a step in the new simplified onboarding flow. Show users the retention benefit explicitly in the onboarding itself. "Users who add their own foods track nutrition 2.3x longer." Make personalisation a stated benefit not a hidden feature.
- Comment 8 (Arjun, June 3): Adds important data quality note to the report. The 847 total entries includes 23 duplicate food names where different users created the same food independently. Unique food names: 312. The report should cite both numbers accurately — 847 entries demonstrates usage volume, 312 unique foods demonstrates database enrichment.

**Cross-references:** CF-EPIC-001, Sprint 9 meeting note, Q2 OKR, V2-PLAN-001

---

## TICKET 2

**Ticket ID:** RES-003
**Title:** Feature adoption report — Nutrient Analysis
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 11
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Feature adoption report for the Nutrient Analysis feature covering
both the bar graph and 7-day trend chart. The key question: are
users actually engaging with analysis or just logging food without
checking their progress? The bar graph redesign AN-CR-001 was
deployed in Sprint 8 — this report measures whether it changed
user behaviour. Analysis engagement is the metric that connects
logging behaviour to retention.

**Acceptance Criteria:**
- Report covers percentage of active users who view analysis weekly
- Average time spent on analysis screen documented
- Engagement before and after AN-CR-001 redesign compared
- Most viewed micronutrients in analysis identified
- Whether analysis viewing predicts Day 7 retention documented

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, May 28): Pulls analysis screen engagement data. 67% of active users view analysis at least once weekly — exactly matching the Q2 OKR target. Average time on analysis screen: 2.1 minutes per visit. Micronutrients most viewed: protein (highest), iron, vitamin D, calcium. Indian food users spend 40% longer on analysis than non-Indian-food users.
- Comment 2 (Shristi, May 29): The Indian food user analysis engagement finding is interesting. Asks Arjun to check if this is because Indian food users have more custom micronutrient goals set or if there is another driver.
- Comment 3 (Arjun, May 30): Before AN-CR-001 deployment (pre-April 26): 52% weekly analysis engagement. After AN-CR-001: 67% weekly. The redesign increased analysis engagement by 29%. This is a significant behaviour change from a single UX improvement. Confirms the bar graph redesign was worth the investment.
- Comment 4 (Shristi, June 2): The 29% engagement increase from one UX fix is the strongest data argument for user testing before implementation. Documents in report: every critical data visualisation must be user tested before implementation. The process change we made in Sprint 6 paid off measurably.

**Cross-references:** AN-CR-001, Sprint 8 retrospective

---

## TICKET 3

**Ticket ID:** RES-004
**Title:** Goal setting funnel analysis — 38% drop-off confirmed
**Type:** Research Task
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 11
**Story Points:** 5
**Tier:** Tier 1 (8 comments)

**Description:**
Run a comprehensive funnel analysis of the onboarding and goal
setting flow to identify exactly where users are dropping off and
why. The NPS open text from NPS-001 identified "goal setup too
complex" as the top complaint. This analysis confirms the hypothesis
with data and quantifies the exact drop-off rate at each onboarding
step. This directly justifies the Q3 simplified onboarding priority.

**Acceptance Criteria:**
- Funnel documents conversion at each onboarding step:
  account creation → profile setup → calorie goal start →
  calorie goal complete → first food log
- Drop-off percentage at each step calculated
- The 38% drop-off hypothesis confirmed or corrected with data
- Average time spent at the calorie goal setup step measured
- Difference between completers and abandoners documented
- Recommendations for simplification with specific changes proposed

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Arjun, May 27): Builds the funnel query. Each onboarding step has a timestamp in the relevant database table — account creation in users table, profile completion in user_profiles, goal creation in daily_goals. Tracks progression by comparing timestamps and checking which steps each user completed.
- Comment 2 (Arjun, May 29): Funnel data ready. Account creation → profile setup complete: 94% conversion. Profile setup → calorie goal start: 87% conversion. Calorie goal start → calorie goal complete: 62% conversion. Calorie goal complete → first food log: 89% conversion. The calorie goal setup step is the single biggest drop in the entire funnel.
- Comment 3 (Shristi, May 29): 38% of users who start calorie goal setup do not complete it. Asks the critical follow-up — what happens to those 38% after they abandon? Do they return to complete it? Do they churn? Do they use the app without goals?
- Comment 4 (Arjun, May 30): Of the 38% who abandon calorie goal setup: 12% return and complete it within 7 days. 8% use the app without any goals (just browse USDA foods occasionally). 80% churn within 3 days of abandoning. The EER formula setup is a hard churn driver — not a delay, a departure.
- Comment 5 (Shristi, May 30): 80% of the 38% churning within 3 days means calorie goal setup abandonment is responsible for approximately 30% of all user churn. This is not a nice-to-have improvement. This is the single highest-impact change we can make in Q3.
- Comment 6 (Arjun, June 2): Average time analysis. Users who complete calorie goal setup: average 4.2 minutes on the EER form. Users who abandon: average 1.8 minutes. The abandoners are not trying hard and giving up — they see the EER formula, make a quick decision that it is too complex, and leave. The solution is not clearer instructions. The solution is removing the formula from the visible interface entirely.
- Comment 7 (Kabir, June 2): Reviews his simplified onboarding sketch from Sprint 10. The 3-question approach (health goal, activity level in plain language, current weight) bypasses the EER formula complexity entirely. The formula runs behind the scenes. The user never needs to understand it to benefit from it. This is the correct direction.
- Comment 8 (Shristi, June 4): Funnel analysis report complete and approved. Headline finding documented formally: 38% of users who begin goal setting do not complete it. 80% of those churn within 3 days. Calorie goal setup abandonment accounts for approximately 30% of total user churn. Simplified onboarding is confirmed as Sprint 12 top priority — not a nice-to-have but a revenue-critical intervention.

**Cross-references:** NPS-001, V2-PLAN-001, Q2 OKR Objective 1

---

## TICKET 4

**Ticket ID:** RES-005
**Title:** Customer interview notes — 8 beta users March cohort
**Type:** Research Task
**Status:** Done
**Priority:** P2
**Assignee:** Ananya Iyer
**Sprint:** Sprint 11
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Document and structure the customer interview notes from the 8
beta user interviews conducted in March 2025. These notes existed
informally and need to be organised into a proper research document.
This matters for PrismAI — when the system is asked "what did
users say before launch" it needs to retrieve structured interview
data, not informal notes scattered across Slack and personal files.

**Acceptance Criteria:**
- All 8 interview notes documented with user profile, key quotes,
  pain points, and feature requests
- Common themes across 8 interviews identified
- Cross-references to product decisions made from this research
- Document structured for RAG retrieval — clear headings per user,
  clear sections per theme

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Ananya, May 28): Organises March interview notes. 8 interviews: 5 health-conscious Indians aged 24-35, 1 fitness trainer, 1 nutritionist student, 1 software engineer. Common themes across all 8: Indian food gap (8/8 mentioned), multiple app frustration (6/8), micronutrient interest (5/8), goal setting confusion (4/8) — this last theme foreshadowed the NPS finding.
- Comment 2 (Shristi, May 30): Asks Ananya to specifically map each interview finding to the product decision it influenced. The data story is more compelling when it shows the direct line from user voice to product choice.
- Comment 3 (Ananya, June 2): Decision mapping documented. Indian food gap → Custom Food fast-track Sprint 2. Tabs discovery issue → GOAL-009 tabs-to-scroll Sprint 3. Supplement tracking interest → NUTR-014 Option C Sprint 5. Goal setup confusion → foreshadowed NPS finding and Sprint 12 simplified onboarding priority.
- Comment 4 (Shristi, June 3): Document approved. The goal setup confusion finding from March interviews is particularly important in retrospect — 4 of 8 users mentioned it before launch and we did not act on it fast enough. It is now confirmed by NPS and funnel data as the biggest retention blocker. User research predicted this 3 months before the data confirmed it.

**Cross-references:** Meeting Notes 2, 3, 5, NPS-001, RES-004

---

## TICKET 5

**Ticket ID:** RES-006
**Title:** Competitive analysis update — post-launch
**Type:** Research Task
**Status:** Done
**Priority:** P2
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 11
**Story Points:** 2
**Tier:** Tier 3 (2 comments)

**Description:**
Update the competitive analysis originally completed in March to
reflect the post-launch competitive landscape. Key questions: have
MFP or HealthifyMe made any improvements to Indian food coverage
or micronutrient tracking since March? Any new Indian nutrition
apps launched? Has anything changed that affects Nutrivana's
differentiation story?

**Acceptance Criteria:**
- All 4 competitors checked for product updates since March
- Indian food coverage comparison updated
- Micronutrient tracking comparison updated
- Any new competitive threats identified
- Nutrivana's differentiation status confirmed or updated

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Shristi, May 28): Runs competitive update. MFP: no changes to Indian food coverage or micronutrient tracking. HealthifyMe: added approximately 200 new Indian restaurant food entries but still no micronutrient tracking depth. Cronometer: no changes. No new Indian nutrition app competitors identified in App Store searches.
- Comment 2 (Shristi, June 2): Analysis updated. Nutrivana's differentiation remains intact. HealthifyMe's restaurant food additions do not address the home-cooking gap that the Custom Food Creator solves. Our pregnant women segment discovery gives us a new defensible niche that none of the competitors are even aware of yet.

**Cross-references:** Round 1 competitive analysis

---

## TICKET 6

**Ticket ID:** MET-001
**Title:** Weekly metrics sheet — May complete
**Type:** Technical Task
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 11
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Complete the May metrics tracking sheet with all weekly data for
the full month of May. This is the formal record for Q2 OKR review
and investor communications. All May numbers must be verified
against Supabase raw data before the sheet is finalised.

**Acceptance Criteria:**
- Weekly metrics documented for all 4 weeks of May
- Metrics include: MAU, DAU, Day 7 retention by cohort, custom foods
  created, App Store rating, session length
- End of May headline numbers locked: MAU 1247, Day 7 retention 45%,
  App Store 4.0, NPS 34
- Numbers verified against Supabase raw data
- Sheet formatted for sharing with Ravi in investor update

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, June 2): Builds the May metrics sheet. Week 1 (May 1-7): MAU 847, Day 7 retention 43%, custom foods 250. Week 2 (May 8-14): MAU 1,023, retention 44%, custom foods 312. Week 3 (May 15-21): MAU 1,134, retention 44%, custom foods 356. Week 4 (May 22-28): MAU 1,247, retention 45%, custom foods 389.
- Comment 2 (Shristi, June 3): Validates all numbers against Supabase raw data. MAU 1,247 confirmed. Growth from 847 to 1,247 in one month is 47% — entirely organic. No paid acquisition. Dr. Kavitha Rao partnership drove approximately 89 of those installs.
- Comment 3 (Ananya, June 3): Adds NPS context to the sheet. May 20 NPS survey: 34 score, 187 responses, 23% response rate. Top open text themes documented alongside the quantitative metrics.
- Comment 4 (Arjun, June 4): Metrics sheet finalised and locked. Will begin June tracking in the same format starting June 1 data.

**Cross-references:** Q2 OKR, MON-001

---

## TICKET 7

**Ticket ID:** RET-001
**Title:** Retention cohort analysis — May cohort
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 11
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Build the May retention cohort analysis showing Day 1, Day 7,
Day 14 retention for the May public launch cohort. This is the
first full retention cohort data for public launch users and the
key comparison for understanding whether beta improvements carried
forward. Segmentation by custom food usage reveals the retention
gap that drives the onboarding recommendation.

**Acceptance Criteria:**
- Cohort covers Day 1, Day 7, Day 14 retention for May cohort
- Comparison between April beta cohort and May public launch cohort
- Segmentation by: custom food users vs non-custom-food users
- Segmentation by: users who completed goal setup vs did not
- Custom food retention gap documented — widening at Day 14 noted

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, May 28): Builds cohort query. April beta cohort (200 users): Day 7 41%, Day 14 35%. May public launch cohort (847 users): Day 7 43%, Day 14 37% estimated.
- Comment 2 (Shristi, May 29): Asks for custom food segmentation. This is the most important cut of the retention data.
- Comment 3 (Arjun, May 30): Custom food segmentation. Users with custom food: Day 7 58%, Day 14 51%. Users without custom food: Day 7 34%, Day 14 27%. The gap is widening over time — 24 percentage points at Day 7, growing to 24 points at Day 14. Custom food creates compounding retention not just a one-time lift.
- Comment 4 (Shristi, June 2): The widening gap at Day 14 is the key insight. This means custom food does not just help users survive the first week — it makes the app increasingly sticky over time. Every new entry the user creates makes leaving harder. The first 3 sessions onboarding push is even more strongly justified.

**Cross-references:** RES-002, CF-EPIC-001

---

## TICKET 8

**Ticket ID:** BUG-012
**Title:** Trend chart double-counting supplement logs
**Type:** Backend Bug
**Status:** Done
**Priority:** P2
**Assignee:** Arjun Mehta
**Sprint:** Sprint 11
**Story Points:** 2
**Tier:** Tier 3 (2 comments)

**Description:**
Users who log supplements are seeing inflated micronutrient
percentages in the 7-day trend chart for nutrients covered by
both food and supplements. The supplement nutrient contribution
is being counted twice — once from the supplement log and once
from an incorrect inclusion in the food log nutrient snapshot.
The bug affects users who track supplements — currently a small
but growing percentage of users.

**Acceptance Criteria:**
- Supplement nutrient contributions counted exactly once in totals
- Trend chart shows correct percentage for users with supplements
- Food logs and supplement logs queried separately and summed correctly
- Fix verified with test cases covering users with both sources

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Arjun, June 2): Root cause found. The nutrient_snapshot in food_logs was incorrectly including supplement data during a batch process that runs nightly. The fix is adding a source_type filter to the daily total calculation — food_logs and supplement_logs queried separately and summed correctly after.
- Comment 2 (Arjun, June 4): Fix deployed. Added explicit source_type filter. Added regression test specifically for users who log both food and supplements on the same day. Cannot double-count with the new query structure.

**Cross-references:** NUTR-TASK-004, supplement implementation Sprint 5

---

## TICKET 9

**Ticket ID:** FUN-001
**Title:** Funnel analysis report — March and June cohorts
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 11
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Create two formal funnel analysis reports — one for the March
pre-launch testing cohort and one for the June post-launch cohort.
The June funnel formally documents the 38% drop-off confirmed in
RES-004. Having both reports allows comparison between internal
testing behaviour and real user behaviour — showing where real users
diverged from what the team expected.

**Acceptance Criteria:**
- March funnel documents internal team and 5 user tester conversion
- June funnel documents full onboarding conversion with all step
  percentages and the 38% drop-off finding
- Comparison section shows where real users diverged from internal testing
- Recommendations for Q3 based on both funnels documented

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Shristi, May 28): March funnel is mostly for baseline reference. The internal team and 5 user testers all completed goal setup — 100% completion in internal testing. This is why the 38% real-world drop-off was invisible until post-launch. The team never experienced the complexity because they were motivated to complete the setup.
- Comment 2 (Arjun, May 30): June funnel data formalised from RES-004 analysis. Adds one new data point: the average time at the calorie goal setup step for completers vs abandoners. Completers: 4.2 minutes. Abandoners: 1.8 minutes. The abandoners see the EER formula and leave quickly — they do not struggle through it, they decide it is not for them within 2 minutes.
- Comment 3 (Shristi, June 2): The 1.8 minute abandon time is the most psychologically important data point in this report. Users are not trying and failing. They are making a quick decision that this is too complicated. The solution is not making the form clearer or adding a help tooltip. It is making the form shorter. Three questions instead of eight.
- Comment 4 (Shristi, June 4): Both funnel reports complete. The March vs June comparison is valuable for a different reason — it shows that internal testing is not a substitute for real user testing. The team completing 100% of goal setup gave false confidence. Real users showed 62% completion. This validates the user testing process changes we made after the bar graph incident.

**Cross-references:** RES-004, NPS-001

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 11

Generate one Excel file: sprint11_jira.xlsx
Save in generated/jira/

Sheet 1 — Tickets:
Columns: Ticket ID, Title, Type, Status, Priority, Assignee,
Sprint, Story Points, Description, Acceptance Criteria

Sheet 2 — Comments:
Columns: Ticket ID, Comment Number, Author, Date, Comment Text
One row per comment.

Use the same CRISPE system prompt from Sprints 4-9.

Comment counts must match tier:
RES-002: 8 comments (Tier 1)
RES-003: 4 comments (Tier 2)
RES-004: 8 comments (Tier 1)
RES-005: 4 comments (Tier 2)
RES-006: 2 comments (Tier 3)
MET-001: 4 comments (Tier 2)
RET-001: 4 comments (Tier 2)
BUG-012: 2 comments (Tier 3)
FUN-001: 4 comments (Tier 2)

Critical consistency:
NPS result May 20: 34
MAU end of May: 1,247
Day 7 retention end of May: 45%
Custom foods end of May: approximately 300-400
App Store rating end of May: 4.0
Custom food 2.3x Day 30 retention: confirmed in RES-002
38% goal setting drop-off: confirmed in RES-004
First 3 sessions custom food insight: confirmed in RES-002
Analysis engagement before AN-CR-001: 52%
Analysis engagement after AN-CR-001: 67%