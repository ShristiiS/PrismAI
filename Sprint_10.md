# Sprint 10 Ticket Definitions
## May 13 to May 26, 2025

---

## SPRINT 10 CONTEXT

**Sprint dates:** May 13 to May 26, 2025
**Sprint goal:** Monitor post-launch metrics closely, fix all
remaining P1 and P2 bugs from public launch week, and begin
formal investigation of the pregnant women segment.
**Total tickets:** 9
**Focus:** Post-launch monitoring, bug fixing, research initiation

**Metrics at Sprint 10 start (May 13):**
- MAU: approximately 1,000 (growing from 847 week 1)
- Day 7 retention: 43%
- App Store rating: 4.1
- Custom foods: 250 cumulative

**Metrics at Sprint 10 end (May 26):**
- MAU: approximately 1,100
- Day 7 retention: 44%
- NPS survey launched May 20 — result: 34
- Custom foods: approximately 280

**Key events this sprint:**
- NPS survey May 20 — first formal NPS, result 34
- Pregnant women cohort analysis run by Arjun
- Dr. Kavitha Rao second nutritionist partnership activated
- V2 roadmap prioritisation begins

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
| MON-001 | Post-launch metrics dashboard setup | Tier 2 | 4 |
| MON-002 | Pregnant women cohort analysis | Tier 1 | 8 |
| BUG-010 | Search results not resetting on diary date change | Tier 2 | 4 |
| AN-CR-003 | Analysis screen performance on low-end Android | Tier 2 | 4 |
| NPS-001 | NPS survey implementation and launch | Tier 2 | 4 |
| RES-001 | Pregnant women user interviews — 5 interviews | Tier 2 | 4 |
| MKT-001 | Dr. Kavitha Rao nutritionist partnership activation | Tier 3 | 2 |
| BUG-011 | Custom food serving unit not saving on iOS Safari | Tier 2 | 4 |
| V2-PLAN-001 | Q3 roadmap planning and V2 feature prioritisation | Tier 2 | 4 |

**Total comments:** 38

---

## TICKET 1

**Ticket ID:** MON-001
**Title:** Post-launch metrics dashboard setup
**Type:** Technical Task
**Status:** Done
**Priority:** P0
**Assignee:** Arjun Mehta
**Sprint:** Sprint 10
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Set up a real-time metrics monitoring dashboard for the team to
track MAU, DAU, Day 7 retention, session length, and feature usage
post-launch. The team was manually pulling metrics from Supabase
before launch. With real users now the team needs a proper dashboard
that updates daily without manual queries. Without this Shristi is
running ad-hoc Supabase queries every morning to check numbers.

**Acceptance Criteria:**
- Dashboard shows MAU, DAU, and Day 7 retention updated daily
- Feature usage breakdown shows percentage of users using each
  core feature (food diary, goal setting, custom food, analysis)
- Retention cohort chart shows Day 7 and Day 30 by weekly cohort
- Dashboard accessible to all team members via read-only link
- Custom foods created per day metric included as a key signal
- Data refreshes automatically without manual Supabase queries

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Shristi, May 13): Raises the problem. Every morning she is running 6 separate Supabase queries to check overnight numbers. Not scalable. Asks Arjun to build a simple dashboard — not a full analytics platform, just the 6 most important metrics visible without SQL.
- Comment 2 (Arjun, May 13): Recommends building custom SQL views in Supabase and a lightweight internal dashboard page in the Next.js app. Faster than setting up Metabase or Mixpanel. Can be ready in 2 days. Notes he will add a custom foods created per day metric — this is the most interesting signal for Indian food gap resolution.
- Comment 3 (Arjun, May 15): Dashboard live. One early finding worth flagging — users who create custom foods in their first 3 sessions have significantly higher session frequency the following week compared to users who do not. Will quantify properly in Sprint 11 feature adoption report.
- Comment 4 (Shristi, May 15): Approved. The early custom food retention signal is exactly what we hypothesised. Document this observation formally in Sprint 11 research work.

**Cross-references:** CF-EPIC-001, Sprint 9 retrospective

---

## TICKET 2

**Ticket ID:** MON-002
**Title:** Pregnant women cohort analysis
**Type:** Story — Backend
**Status:** Done
**Priority:** P1
**Assignee:** Arjun Mehta
**Sprint:** Sprint 10
**Story Points:** 5
**Tier:** Tier 1 (8 comments)

**Description:**
Following Ananya's discovery of 11 users who mentioned pregnancy
in their free-text profile health goals field, run a formal cohort
analysis comparing pregnant women users vs all other users across
all key engagement metrics. This is the most important analytical
task of Sprint 10. The results will determine whether pregnant women
become a Q3 product priority. The initial signals Ananya noticed
informally — 4.2 sessions per day vs 1.8 average — need to be
formally verified with complete data before any strategic decision.

**Acceptance Criteria:**
- Cohort analysis compares pregnant women vs all other users on:
  sessions per day, session length, Day 7 retention, feature usage
- Specific micronutrients tracked most by pregnant women identified
- Analysis confirms whether engagement difference is statistically
  meaningful given small sample size (11 users)
- Iodine tracking behaviour specifically noted — unexpected signal
- Results documented in shareable format for investor communication
- Methodology documented so analysis can be repeated as user base grows

**Conversation Blueprint (Tier 1 — 8 comments):**
- Comment 1 (Ananya, May 13): Provides the list of 11 users she identified from free-text health goals field. Notes the identification method is imperfect — some pregnant users may not have mentioned it in free text. Asks Arjun to also check users who have folate AND iron goals set simultaneously as a secondary identification method.
- Comment 2 (Arjun, May 14): Confirms he can run both identification methods. Secondary method (folate + iron combination) identifies 4 additional users beyond the 11 already identified. Total potential pregnant users: 15. Will run analysis on both groups and compare.
- Comment 3 (Arjun, May 15): Preliminary results on the 11 explicitly identified users. Sessions per day: 4.2 vs 1.8 overall average. Session length: 6.3 minutes vs 2.8 minutes. Day 7 retention: 9 of 11 returned on day 7 (81.8%) vs 41.9% overall. These numbers are extraordinary. Needs methodology verification before sharing externally.
- Comment 4 (Shristi, May 15): 81.8% Day 7 retention is the highest she has seen in any health app benchmark she has read. Asks Arjun to triple check the cohort definition and make sure there is no survivorship bias — are these 11 users typical or are they self-selected super-users regardless of pregnancy?
- Comment 5 (Arjun, May 16): Bias check complete. The 11 users were registered at different times (some beta, some launch week). Their first-week behaviour before the high engagement period was similar to other users. The high engagement developed over time as they used the micronutrient tracking more deeply. Not survivorship bias — genuine behavioural difference.
- Comment 6 (Arjun, May 17): Notable additional finding: iodine is tracked by 54% of pregnant users vs under 5% of all other users. This was not expected. Iodine deficiency in pregnancy is a serious risk for fetal brain development. The fact that more than half of pregnant users are specifically tracking iodine suggests these are medically informed, highly engaged users — not casual health trackers.
- Comment 7 (Ananya, May 17): Confirms from user interview context (first interview started today): first interviewee confirmed her OB-GYN specifically told her to monitor iodine alongside folate and iron. This validates the data pattern — these users have doctor-prescribed tracking targets that our micronutrient feature supports better than any competitor.
- Comment 8 (Shristi, May 18): Analysis approved for sharing with Ravi in the next investor update. The headline number is 3.1x engagement (combining session frequency and session length multipliers). Pregnant women become Q3 priority 2 immediately. Confirms this to full team in the Sprint 10 meeting.

**Cross-references:** Meeting Note 9, Q2 OKR Objective 3, Sprint 9 retrospective

---

## TICKET 3

**Ticket ID:** BUG-010
**Title:** Search results not resetting on diary date change
**Type:** Frontend Bug
**Status:** Done
**Priority:** P2
**Assignee:** Priya Nair
**Sprint:** Sprint 10
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Post-launch users reported that when navigating to a different
diary date while the food search panel is open, the search results
from the previous date session remain visible. Users think they are
searching in the new date's context but they are seeing results
from their previous search. This creates confusion about which
diary date food is being added to.

**Acceptance Criteria:**
- Navigating to a different diary date clears search state completely
- Search input field is empty when arriving on a new date
- No previous search results visible when date changes
- Fix uses the shared clearSearchState() utility created in Sprint 8
- Fix does not affect search state within the same date session

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Priya, May 13): Root cause identified immediately. The diary date navigation handler was written before the Sprint 8 codebase audit and does not call clearSearchState(). Same pattern as NUTR-BUG-008 — one more place the utility was not applied. One line fix.
- Comment 2 (Arjun, May 14): Notes this is exactly the kind of bug the shared utility approach was supposed to prevent but the audit could only fix existing code — new code written post-audit needs discipline to use the utility. Proposes adding a linting rule that flags direct search state manipulation that bypasses clearSearchState().
- Comment 3 (Priya, May 15): Fix deployed. Also found the analysis screen carousel navigation had the same issue — switching between nutrients in the analysis screen did not clear any active search state. Fixed both in the same PR.
- Comment 4 (Shristi, May 15): Approved. Arjun's linting rule idea is good — add it to the Sprint 10 action items. Prevention is better than finding the same bug class repeatedly.

**Cross-references:** NUTR-BUG-008, Sprint 8 codebase audit, clearSearchState utility

---

## TICKET 4

**Ticket ID:** AN-CR-003
**Title:** Analysis screen performance on low-end Android devices
**Type:** Change Request
**Status:** Done
**Priority:** P2
**Assignee:** Arjun Mehta
**Sprint:** Sprint 10
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Post-launch user feedback via App Store reviews mentions the
nutrient analysis screen loads slowly on low-end Android devices
(2GB RAM). One review specifically says "app is slow when checking
nutrition". The analysis page triggers multiple FoodDiaryContext
re-renders when the user navigates to it even when the data has not
changed. Target is analysis screen under 1 second on mid-range
Android (3GB RAM).

**Acceptance Criteria:**
- Analysis screen loads in under 1 second on mid-range Android
- FoodDiaryContext reads are memoized to prevent unnecessary re-renders
- React.memo applied to analysis bar graph component
- useCallback applied to data transformation functions
- Performance tested on simulated low-end Android device profile
- No regressions on iOS or desktop

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Arjun, May 14): Root cause found. FoodDiaryContext triggers re-renders in all subscribed components whenever any diary data changes — even if the analysis screen data did not change. The analysis bar graph component is re-rendering on every food log action even when the user is not on the analysis screen.
- Comment 2 (Priya, May 15): Suggests React.memo on the analysis bar graph component as the highest-impact fix. The bar graph is the most complex component and it is re-rendering unnecessarily on every diary update.
- Comment 3 (Arjun, May 19): Optimisation complete. React.memo applied to analysis bar graph, 7-day trend chart, and per-nutrient analysis components. useCallback applied to the nutrient aggregation function. Analysis screen load time on mid-range Android simulation: 1.8 seconds → 0.7 seconds.
- Comment 4 (Shristi, May 20): Approved. The 0.7 second load time is well within the 1 second target. Notes for future: performance testing on low-end devices should be part of the definition of done for any new screen component.

**Cross-references:** TECH-004, FoodDiaryContext Sprint 7

---

## TICKET 5

**Ticket ID:** NPS-001
**Title:** NPS survey implementation and launch
**Type:** Story — Full Stack
**Status:** Done
**Priority:** P1
**Assignee:** Ananya Iyer
**Sprint:** Sprint 10
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
Launch the first formal NPS survey to all active users on May 20.
The survey asks the standard NPS question (likelihood to recommend,
0-10 scale) plus one open text question about the most important
improvement. This is the first formal measurement of user satisfaction
post-launch and directly tracks Q2 OKR Objective 2 KR for NPS 35+
by end of May.

**Acceptance Criteria:**
- Survey sent only to users who have logged food at least 3 times
- In-app survey as dismissible banner — not a blocking modal
- NPS score calculated from responses using standard formula
- Open text responses exported to CSV for qualitative analysis
- Survey does not appear more than once per user per quarter
- Results available for team review by May 21

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Ananya, May 14): Proposes NPS survey for May 20. Shares draft question wording and timing. Asks Shristi to add the open text question and Arjun to build the in-app banner.
- Comment 2 (Shristi, May 15): Approves question wording. Adds second question: "What one feature would make you most likely to recommend Nutrivana to a friend?" — specifically for Q3 roadmap prioritisation. This question will tell us what users think is missing more directly than generic NPS feedback.
- Comment 3 (Arjun, May 18): In-app banner built. Technical note: the 3-food-log minimum filter correctly excludes users who registered but never really used the app. These users would have dragged NPS down with negative scores that do not reflect the actual product experience.
- Comment 4 (Ananya, May 21): Results. 187 responses from approximately 800 eligible users (23% response rate). NPS: 34. Promoters (9-10): 41%. Passives (7-8): 52%. Detractors (0-6): 7%. Top open text responses: custom recipe builder (most mentioned), barcode scanner, simplified goal setup. Goal setup complexity is the top complaint — directly aligns with the funnel analysis to be run in Sprint 11.

**Cross-references:** Q2 OKR Objective 2, V2-PLAN-001

---

## TICKET 6

**Ticket ID:** RES-001
**Title:** Pregnant women user interviews — 5 interviews
**Type:** Research Task
**Status:** Done
**Priority:** P1
**Assignee:** Ananya Iyer
**Sprint:** Sprint 10
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Conduct 5 structured user interviews with pregnant women users
identified from the MON-002 cohort analysis. Goal is to understand
their specific micronutrient tracking needs, what doctor-recommended
targets they follow, what the current product does not support, and
whether they have referred other pregnant women to Nutrivana.

**Acceptance Criteria:**
- 5 interviews completed with pregnant women users by May 22
- Each interview covers: how they found Nutrivana, what they track,
  their doctor's specific recommendations, what the app cannot do,
  referral behaviour
- Interview notes documented and shared with full team
- Top 3 feature gaps identified and prioritised
- At least one direct quote captured for investor communication

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Ananya, May 13): Reaches out to 8 of the 11 identified users explaining they are doing research interviews and offering 3 months Nutrivana Pro free when premium launches. 6 respond positively. Schedules 5 for May 15-22.
- Comment 2 (Shristi, May 15): Provides interview script. Non-negotiable questions: what does your doctor tell you to track, what trimester are you in, what does Nutrivana do that other apps do not, what does it not do that you wish it did, have you told any other pregnant women about it.
- Comment 3 (Ananya, May 22): Interviews complete. Most important findings: all 5 users have trimester-specific targets from their OB-GYN. The current app does not support trimester — users are manually editing their micronutrient goals every time they transition. Two users have already shared Nutrivana in their pregnancy WhatsApp groups — unprompted referrals.
- Comment 4 (Shristi, May 23): The WhatsApp group referral is the most strategically important finding. Pregnant women communities are tightly networked and highly trusting of recommendations from other pregnant women. If the product serves them well the segment is genuinely self-propagating. Prenatal presets confirmed as Q3 priority 2.

**Cross-references:** MON-002, Q2 OKR Objective 3

---

## TICKET 7

**Ticket ID:** MKT-001
**Title:** Dr. Kavitha Rao nutritionist partnership activation
**Type:** Marketing Task
**Status:** Done
**Priority:** P2
**Assignee:** Ananya Iyer
**Sprint:** Sprint 10
**Story Points:** 2
**Tier:** Tier 3 (2 comments)

**Description:**
Activate the second nutritionist partnership with Dt. Kavitha Rao
(Bangalore-based dietitian, 18k Instagram followers). Partnership
agreed in April but first post not yet scheduled. Coordinate the
briefing document, tracking link, and post timing.

**Acceptance Criteria:**
- Partnership briefing document sent to Kavitha
- Custom UTM tracking link created for attribution
- Post scheduled for week of May 19
- Install attribution monitored via tracking link

**Conversation Blueprint (Tier 3 — 2 comments):**
- Comment 1 (Ananya, May 14): Briefing document sent to Kavitha. Highlights Nutrivana's Indian food coverage and micronutrient tracking depth as the key differentiators to mention. Post scheduled for May 21.
- Comment 2 (Ananya, May 22): Kavitha's post live May 21. 89 installs in 48 hours from her tracking link. Smaller than Dr. Nambiar's 156 (smaller audience) but 4.8% click rate on her followers — higher engagement rate than Nambiar's post. Both partnerships active now.

**Cross-references:** Q2 OKR Objective 4, Sprint 9 launch

---

## TICKET 8

**Ticket ID:** BUG-011
**Title:** Custom food serving unit not saving on iOS Safari
**Type:** Frontend Bug
**Status:** Done
**Priority:** P1
**Assignee:** Priya Nair
**Sprint:** Sprint 10
**Story Points:** 3
**Tier:** Tier 2 (4 comments)

**Description:**
iOS Safari users report that the serving unit free-text field in
custom food creation sometimes saves as empty even when a value
was typed. This is a critical bug — serving unit is required for
accurate nutrient calculation. If serving unit is empty the custom
food cannot be logged correctly. Approximately 15% of iOS users
based on bug report volume.

**Acceptance Criteria:**
- Serving unit field saves correctly on iOS Safari 16 and 17
- Root cause identified and fixed
- Fix uses onChange handler not onBlur for all free-text fields
- Applied to all 6 free-text fields in the custom food form
- No regression on Android Chrome or desktop browsers
- Tested on physical iOS device not just simulator

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Priya, May 14): Root cause found. iOS Safari has a known issue with input event handling — onBlur fires before the value is committed in some scroll and tap scenarios. The serving unit field was using onBlur to capture the value. When the bug triggers the field saves an empty string.
- Comment 2 (Arjun, May 15): Confirms this is a well-documented iOS Safari and React interaction issue. The fix (onChange instead of onBlur) is correct. Suggests applying it to all free-text fields in the custom food form proactively — not just the serving unit field.
- Comment 3 (Priya, May 16): Fix deployed. onChange applied to all 6 free-text fields in the custom food form. Tested on iOS 16 and 17 physical device (Priya's iPhone). Bug not reproducible after fix.
- Comment 4 (Shristi, May 16): Approved. Important fix. Indian users disproportionately use iPhones — this bug was silently blocking custom food creation for a significant portion of our most valuable users (those who create custom foods retain 2.3x better). Should have been caught in pre-launch iOS testing.

**Cross-references:** CF-001, CF-002, Sprint 9 CF-EPIC-001 closure

---

## TICKET 9

**Ticket ID:** V2-PLAN-001
**Title:** Q3 roadmap planning and V2 feature prioritisation
**Type:** Product Task
**Status:** Done
**Priority:** P1
**Assignee:** Shristi Sharmistha
**Sprint:** Sprint 10
**Story Points:** 2
**Tier:** Tier 2 (4 comments)

**Description:**
Based on NPS survey results, cohort analysis findings, and pregnant
women user interviews, create the initial Q3 roadmap prioritisation.
This ticket formalises what was discussed in the Sprint 10 weekly
meeting. Three confirmed Q3 priorities: simplified onboarding
(38% goal setting drop-off from NPS open text), prenatal
micronutrient presets (3.1x engagement), custom recipe builder
(top NPS open text feature request).

**Acceptance Criteria:**
- Q3 roadmap document updated with confirmed priorities and rationale
- Each Q3 feature has clear data-based justification
- Priority order confirmed and documented
- Technical complexity estimates from Arjun included
- Roadmap shared with Ravi for investor alignment
- Q3 OKR draft started based on roadmap priorities

**Conversation Blueprint (Tier 2 — 4 comments):**
- Comment 1 (Shristi, May 23): Documents Q3 priorities based on Sprint 10 findings. Priority 1 — simplified onboarding: NPS open text shows goal setup complexity as top complaint. 34 respondents mentioned it. This is a retention blocker not a feature gap. Priority 2 — prenatal presets: 3.1x engagement from an unserved segment. Priority 3 — custom recipe builder: top NPS feature request.
- Comment 2 (Arjun, May 24): Technical complexity estimates. Simplified onboarding: 2 sprints (new 3-question flow replacing EER setup, backend mapping, A/B testing). Prenatal presets: 1.5 sprints (ICMR research, trimester targets, auto-update logic, frontend). Custom recipe builder: 2 sprints (multi-ingredient recipe model, nutrient calculation, frontend). All three fit in Sprint 12-13 if simplified onboarding starts Sprint 12.
- Comment 3 (Kabir, May 24): Shares initial sketch for simplified onboarding — 3 questions: health goal, activity level in plain language, current weight. From these 3 the EER calculates invisibly. User sees only "Your personalised calorie goal: 1847 kcal."
- Comment 4 (Shristi, May 25): Q3 roadmap updated. Sharing with Ravi in the next investor update. Sprint 12 will begin simplified onboarding design and implementation. Sprints 12-13 will begin prenatal presets design and first implementation.

**Cross-references:** NPS-001, MON-002, RES-001, Roadmap document

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 10

Generate one Excel file: sprint10_jira.xlsx
Save in generated/jira/

Sheet 1 — Tickets:
Columns: Ticket ID, Title, Type, Status, Priority, Assignee,
Sprint, Story Points, Description, Acceptance Criteria

Sheet 2 — Comments:
Columns: Ticket ID, Comment Number, Author, Date, Comment Text
One row per comment.

Use the same CRISPE system prompt from Sprints 4-9.

Comment counts must match tier:
MON-001: 4 comments (Tier 2)
MON-002: 8 comments (Tier 1)
BUG-010: 4 comments (Tier 2)
AN-CR-003: 4 comments (Tier 2)
NPS-001: 4 comments (Tier 2)
RES-001: 4 comments (Tier 2)
MKT-001: 2 comments (Tier 3)
BUG-011: 4 comments (Tier 2)
V2-PLAN-001: 4 comments (Tier 2)

Critical consistency:
All metrics must match locked numbers exactly.
NPS survey result May 20: 34
MAU by end of May: 1,247
Pregnant women: 3.1x engagement, 11 identified users
Day 7 retention: 43% at sprint start, 44-45% by sprint end
Custom foods cumulative: approximately 280 by May 26
Dr. Kavitha Rao post: 89 installs in 48 hours