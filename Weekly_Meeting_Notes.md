# Round 3 — Weekly Meeting Notes Definitions
## All 9 Sprints — January 7 to May 7, 2025

---

## GLOBAL RULES FOR ALL MEETING NOTES

**Format:** Word document (.docx)
**Meeting cadence:** One weekly sync per sprint (mid-sprint)
**Facilitator:** Shristi Sharmistha
**Note taker:** Shristi Sharmistha
**Attendees (all meetings):** Shristi, Arjun, Priya, Kabir, Ananya
**Meeting duration:** 45-60 minutes
**Meeting time:** Wednesdays 11:00 AM IST

**Standard document structure:**
1. Meeting header (date, attendees, sprint number)
2. Sprint health check
3. Key product discussions (2-3 topics with real debate captured)
4. User and market updates
5. Metrics review (post-launch only — Sprint 7 onwards)
6. Decisions made this meeting
7. Action items with owners and due dates
8. Next week focus

---

---

# MEETING NOTE 1 — SPRINT 1

**Document name:** Nutrivana Weekly Sync — Sprint 1
**Date:** January 7, 2025
**Sprint:** Sprint 1 (January 1-14)

---

**Sprint Health Check:**
Sprint 1 on track. TECH-001 database schema completed January 6
— 2 days ahead of schedule. GOAL-SPIKE-001 EER formula research
findings shared in Slack this morning. Priya joined today and
has spent the morning on dev environment setup with Arjun.
TECH-003 authentication in progress — expected completion January 10.
NUTR-TASK-003 date model design begins today.

---

**Key Discussion 1 — Database schema review (TECH-001):**
Arjun walked the team through the 12-table schema. Priya reviewed
it immediately and raised two frontend concerns.

First: meal_type column stored as free-text string. Priya said
this creates inconsistent values — "Breakfast" vs "breakfast" vs
"BREAKFAST" would all be different values, breaking diary filtering.
Arjun agreed immediately. Schema updated to enum type with four
values: breakfast, lunch, dinner, snacks. Shristi confirmed
these 4 meal types match the PRD.

Second: display_order column in nutrient_targets has no defined
logic for who controls ordering. Priya asked: frontend or database?
Arjun said: database should own it for consistency across all
screens. display_order set at RDA data import time. Priya confirmed
this works.

Both changes incorporated before end of day.

Shristi noted: this is exactly why Priya needed to review the
schema before implementation. Frontend concerns caught at design
time cost 30 minutes. Caught after implementation they cost days.
Full team schema review is now non-negotiable before any
implementation begins.

---

**Key Discussion 2 — goal_snapshots architectural decision
(NUTR-TASK-003):**
Shristi raised a PRD requirement she wanted carefully considered
before NUTR-TASK-003 began. The requirement: "When a previous date
is selected and the food diary is not filled, an empty food diary
with the target nutrient columns must be displayed."

She asked: if a user changes their goal in March then navigates to
their January diary — which nutrient columns appear? January goals
or March goals?

Arjun said: with the current schema, March goals would show.
daily_goals is a live table with current goals only. The diary
has no way to know what goals were active on a past date.

Shristi said: that is wrong. January diary must show January goals.
A person who reduced their protein goal in March should not see
January entries re-evaluated against March targets.

Three options considered. Option A: store goals inside every diary
entry (duplicates data — rejected). Option B: goal change history
with timestamps, query which goal was active on each date (complex,
V2). Option C: goal_snapshots table — daily snapshot of user's
goal state that the diary reads from. If no snapshot exists for a
date, show empty diary. If snapshot exists, show that date's goals
regardless of current goals.

Team agreed Option C is the correct V1 solution. Arjun implements
goal_snapshots as part of NUTR-TASK-003. PRD updated.

---

**Key Discussion 3 — EER formula activity level mismatch
(GOAL-SPIKE-001 findings):**
Arjun shared research findings. PRD specifies 5 activity levels.
USDA Harris-Benedict formula uses 4 (sedentary, lightly active,
moderately active, very active).

Shristi asked: do we use 5 or 4?
Arjun: USDA uses 4. Adding a 5th requires defining it ourselves —
accuracy risk.
Shristi decided: 4 USDA standard activity levels. Consistency with
USDA data is more important than the extra granularity. PRD updated.

---

**User and Market Updates (Ananya):**
Waitlist signup page live. 23 signups in first week from Instagram
bio link. Several signup form responses mention "can't find Indian
foods in other apps." First real-world validation of the Indian
food gap hypothesis. Noted for team awareness.

---

**Decisions Made:**
1. meal_type uses enum (breakfast, lunch, dinner, snacks)
2. goal_snapshots table — daily snapshot for date-accurate diary
3. 4 USDA activity levels not 5 — PRD updated

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Update TECH-001 with enum meal_type and display_order logic | Arjun | Jan 7 EOD |
| Begin NUTR-TASK-003 with goal_snapshots approach | Arjun | Jan 8 |
| PRD updated with 4 activity levels and goal_snapshots decision | Shristi | Jan 8 |
| Priya to review full schema and raise any remaining concerns | Priya | Jan 10 |
| Ananya to share waitlist growth update next week | Ananya | Jan 14 |

---

**Next Week Focus:**
Complete TECH-003, NUTR-TASK-003, GOAL-SPIKE-002. Begin Technical
Spec Sections 1-4.

---

---

# MEETING NOTE 2 — SPRINT 2

**Document name:** Nutrivana Weekly Sync — Sprint 2
**Date:** January 22, 2025
**Sprint:** Sprint 2 (January 15-28)

---

**Sprint Health Check:**
Sprint 2 has one critical blocker resolved and one discovery that
changes product direction. NUTR-TASK-001 USDA integration hit a
rate limit problem on Day 1. Bulk import now complete — 300,000+
foods in Supabase, search performance 180-200ms. NUTR-TASK-002
fuzzy search in progress. GOAL-001 and GOAL-002 both in progress.

---

**Key Discussion 1 — Indian food gap crisis:**
Arjun raised the most significant product concern so far.
During USDA bulk import testing he searched the most common
Indian foods.

Chapati: 0 results. Dal (any variety): 0 results. Paneer:
3 results (all American restaurant varieties, wrong macros).
Idli: 0 results. Dosa: 0 results. Poha: 0 results. Rajma: 0 results.

Arjun said: "We are building a nutrition app for Indian users
and they cannot find their staple foods. This is the gap we said
we would solve but we have no solution built."

Silence for a moment.

Shristi asked: what are our options?

Option A — do nothing in V1, tell users to use custom food.
Problem: Custom Food was not planned until Sprint 7.

Option B — manually add top 50 Indian foods using IFCT data.
Problem: IFCT licensing takes time and we do not have the data.

Option C — fast-track Custom Food Creator to Sprints 5-6. Seed
the database with top 30 Indian foods ourselves before beta.

Ananya said: Option A is not acceptable. 7 of 10 waitlist users
mentioned Indian food as a pain point. If we launch without Indian
food support we are building the same broken product they already
hate.

Kabir: "Our value proposition is being the nutrition app that
understands Indian users. If we cannot find chapati on day one
we have failed."

Shristi decided: Option C. Custom Food fast-tracked to Sprints 5-6.
Shristi will personally research and add top 30 Indian foods before
beta using IFCT data. Significant scope addition but the right call.

---

**Key Discussion 2 — PRD activity level definition mismatch
(GOAL-001):**
Arjun found a second mismatch beyond the 5-vs-4 levels resolved
in Sprint 1. The PRD describes activity level 3 as "moderately
active (3-5 days exercise per week)" but the USDA formula defines
it as "moderately active (walking 1.5-3 miles per day)." Different
definitions for the same level.

Team discussed: which definition is more useful for users
self-assessing their activity?

Arjun: USDA miles-per-day definition is precise but users struggle
to know if they walk 2 miles daily.
Priya: the exercise-frequency definition (3-5 days) is how
fitness apps universally describe activity levels. Users know this.
Shristi decided: use exercise-frequency for UI labels. Map
internally to USDA calorie multiplier. Easy user self-assessment
with accurate EER formula. PRD updated.

---

**User and Market Updates (Ananya):**
Waitlist at 67. Ananya spoke informally with 3 waitlist users.
All 3: "I stopped using MyFitnessPal because I could not find
my food." Direct validation of Indian food gap.

One quote from a Bangalore-based engineer: "I have a spreadsheet
where I manually look up nutrient values for every Indian food
I eat. I have been doing this for 2 years." Shristi asked Ananya
to save this quote for marketing.

---

**Decisions Made:**
1. Custom Food Creator fast-tracked to Sprints 5-6
2. Activity level UI: exercise frequency. Internal: USDA multiplier
3. Shristi seeds top 30 Indian foods before beta using IFCT data
4. IFCT as reference for Indian food nutrient values

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Add Custom Food to roadmap, create CF-EPIC-001 in Jira | Shristi | Jan 25 |
| Research top 30 missing Indian foods with IFCT values | Shristi | Feb 15 |
| Document Indian food gap — list with user priority ranking | Shristi/Ananya | Feb 15 |
| PRD update — activity level definitions | Shristi | Jan 23 |
| Ananya to plan Instagram Reel for February | Ananya | Feb 1 |

---

**Next Week Focus:**
Complete Sprint 2 — all 6 tickets by January 28. Begin Sprint 3
planning.

---

---

# MEETING NOTE 3 — SPRINT 3

**Document name:** Nutrivana Weekly Sync — Sprint 3
**Date:** February 5, 2025
**Sprint:** Sprint 3 (January 29 - February 11)

---

**Sprint Health Check:**
Sprint 3 tracking well. GOAL-005 through GOAL-008 (macro goal
setting) in progress or complete. Priya has full ownership of
macro goal setting frontend — her first sprint as primary
implementer on multiple tickets.

Flag: GOAL-009 (micronutrient list) taking longer than estimated.
PRD specifies tabbed interface but a discoverability problem has
emerged. Discussed below.

---

**Key Discussion 1 — Micronutrient list design (GOAL-009):**
Kabir presented the problem. PRD specifies micronutrients in tabs
(Vitamins, Minerals, Electrolytes, Other). In Figma it looks clean.
But Ananya showed the prototype to 3 waitlist users informally —
2 of them missed nutrients in non-active tabs entirely.

Kabir proposed: single scrollable list with sticky category
headers. Every nutrient visible without interaction.

Arjun: technically easier — no tab state management.
Priya: she had started implementing tabs and would need to restart.
Estimated 2 extra days.
Ananya: discoverability on first visit is critical. Users setting
up micronutrient goals for the first time need to see all options.
Tabs hide options. Scroll reveals them.

Shristi: the right design is worth 2 days. Proceed with single
scroll. PRD override documented. Kabir updates Figma by February 7.

---

**Key Discussion 2 — Floating point bug in macro validation
(GOAL-007):**
Priya found a bug during testing. When users enter 33.33 / 33.33 /
33.34 (equal macro splits) the JavaScript sum is 99.99999999.
Validation incorrectly flags this as invalid.

Arjun: classic JavaScript floating point precision issue. Fix:
parseFloat(sum.toFixed(2)) before validation.

Priya asked: should we apply this rounding everywhere we display
nutrient values?
Shristi: yes. Any number from a calculation (not a raw database
value) uses this rounding pattern. Team coding standard from now.

Arjun to audit all existing calculation code for floating point
handling.

---

**Key Discussion 3 — Ananya joining design reviews:**
Shristi raised that in the GOAL-009 discussion, Ananya's
discoverability concern was the most important input but she
gave it informally — after designs were nearly finalised.

Going forward Ananya joins all design reviews as a standing
attendee. Kabir shares Figma links with Ananya before all
design review meetings.

Ananya: "I want to be involved earlier. I keep hearing about
design decisions after they are made."

---

**User and Market Updates (Ananya):**
Waitlist at 94. Instagram Reel about Indian food gap in production
(Kabir helping with graphics). Targeting 150 users by March 31.

Notable user feedback from a Bangalore engineer (same one from
last week): "If your app has my foods I will never go back to
my spreadsheet." Shristi: save this quote — it is the clearest
articulation of our value proposition.

---

**Decisions Made:**
1. GOAL-009: single scroll with sticky headers replaces tabs. PRD updated.
2. parseFloat(toFixed(2)) standard for all calculated nutrient values.
3. Ananya joins all design reviews from Sprint 4 as standing attendee.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Kabir updates Figma for GOAL-009 single scroll design | Kabir | Feb 7 |
| Arjun audits existing code for floating point handling | Arjun | Feb 10 |
| PRD updated with GOAL-009 override | Shristi | Feb 6 |
| Ananya added to all design review calendar invites | Shristi | Feb 6 |

---

**Next Week Focus:**
Complete Sprint 3 by February 11. Priya presents GOAL-009
implementation for team review February 10.

---

---

# MEETING NOTE 4 — SPRINT 4

**Document name:** Nutrivana Weekly Sync — Sprint 4
**Date:** February 19, 2025
**Sprint:** Sprint 4 (February 12-25)

---

**Sprint Health Check:**
Sprint 4 mostly on track but NUTR-009 (portion size adjustment)
is taking significantly longer than estimated — full sprint
instead of 5 days. Arjun and Priya pairing on it. NUTR-007,
NUTR-008, NUTR-010 all completed ahead of schedule.
NUTR-015 through NUTR-018 in progress with Priya.
NUTR-TASK-004 calculation engine in progress with Arjun.

---

**Key Discussion 1 — Food-specific serving units discovery
(NUTR-009):**
Arjun raised a discovery from February 16. USDA database does
not use generic serving units — each food has its own specific
serving unit.

Oats, rolled, dry: 1 cup = 156 grams.
Spinach, raw: 1 cup = 30 grams.
Chicken breast, roasted: 1 serving = 85 grams.

The PRD assumed a generic dropdown (cup, tablespoon, gram, ounce).
This assumption was wrong.

Kabir: what does the UI look like with food-specific units?
Arjun showed a mockup: portion input shows the food's own units
with gram equivalent updating in real time. Users can switch to
grams directly.

Priya: this is actually better UX. Users think in "cups of oats"
not "156 grams of oats."
Ananya: strong marketing point — "we show portions the way you
actually measure your food."
Shristi: food-specific serving units is the correct implementation.
PRD updated. Better product than originally specified.

---

**Key Discussion 2 — FoodDiaryContext deferred:**
Priya raised that FoodDiaryContext was identified as needed this
sprint but has not been implemented due to NUTR-009 taking the
full sprint.

Arjun: FoodDiaryContext is needed for diary totals to update
correctly without a full page refresh. Without it the analysis
screen will not update when food is added to diary — core
experience issue.

Shristi: if this is a core experience issue it cannot be deferred.
Arjun: we are out of time this sprint with NUTR-009 taking
everything. Sprint 5 with P0 priority.
Shristi accepted the deferral reluctantly. Noted explicitly:
this is the second time architectural work has been identified
and deferred. This pattern creates risk. Every deferral
makes it harder to address later. Sprint 5 is the hard deadline.

---

**Key Discussion 3 — Color coding for weight goals (NUTR-017):**
Kabir raised a design question. PRD specifies green/yellow/red
for calorie tracking. But what is "over" for someone maintaining
weight vs losing weight?

Priya: going 200 calories over for a maintenance user is not
a crisis — should not be red.
Arjun: red implies danger. Maintenance users over by 200 is yellow.
Shristi: clinical decision. Being over for weight loss = bad (red).
Being over for maintenance = less bad (yellow). Being over for
weight gain = positive (green in some cases).

Decision: color logic is weight_goal_type dependent.
Loss: over calorie = red, under = green.
Gain: over calorie = green, under = yellow.
Maintain: over or under = yellow, on target = green.
Kabir updates design system. Arjun implements as shared variable.

---

**User and Market Updates (Ananya):**
Waitlist at 134. Instagram Reel about Indian food gap posted
February 15 — 1,247 views, 89 new follows. Best performing
content so far. Indian food pain point resonates strongly.

3 user interviews completed. Key finding: all 3 users currently
use 2-3 apps simultaneously (MFP for database, Cronometer for
micronutrients, spreadsheet for Indian foods). Nutrivana's value
prop is consolidation.

---

**Decisions Made:**
1. Food-specific serving units from USDA data (NUTR-009). PRD updated.
2. FoodDiaryContext deferred to Sprint 5 as P0 — cannot be deferred again.
3. Color coding is weight_goal_type dependent — 3 color schemes.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Kabir updates design system with weight-goal-type color logic | Kabir | Feb 22 |
| FoodDiaryContext added as P0 to Sprint 5 backlog | Shristi | Feb 26 |
| Arjun documents food-specific serving unit approach in tech spec | Arjun | Feb 25 |
| Ananya conducts 2 more user interviews before March 15 | Ananya | Mar 15 |

---

**Next Week Focus:**
Complete Sprint 4 by February 25. Demo walkthrough February 24.
Sprint 5 planning with FoodDiaryContext as first P0 item.

---

---

# MEETING NOTE 5 — SPRINT 5

**Document name:** Nutrivana Weekly Sync — Sprint 5
**Date:** March 5, 2025
**Sprint:** Sprint 5 (February 26 - March 11)

---

**Sprint Health Check:**
Sprint 5 on track. 14 tickets this sprint. 9 completed as of
March 5. Remaining 5 in progress.

Concern: FoodDiaryContext was P0 for Sprint 5 and has been
deprioritised again. Full discussion below.

---

**Key Discussion 1 — FoodDiaryContext deferred again:**
Priya raised that FoodDiaryContext was started but set aside
when NUTR-022 (date-wise diary with date picker) turned out more
complex than expected due to an IST timezone midnight problem.

Priya explained: Indian users are UTC+5:30. A user logging food
at 11:55 PM IST — UTC timestamp is same date. But 12:05 AM IST
— UTC timestamp is the previous day. Without careful handling
diary entries appear on the wrong date.

Fix: store both date_string ("2025-03-06") in IST AND a UTC
timestamp. All diary queries use date_string for filtering. UTC
only for ordering and audit. Correct solution but time-consuming.
FoodDiaryContext deprioritised as a result.

Shristi said: FoodDiaryContext has been deferred from Sprint 4
to Sprint 5 to now Sprint 6. This is the third deferral. I want
a clear commitment — will it be in Sprint 6?

Arjun said: Sprint 6 is the MVP sprint. FoodDiaryContext must be
in Sprint 6 — without it the analysis screen will not update when
food is added. This is a guarantee.

Shristi accepted reluctantly. Documented as a risk — if
FoodDiaryContext is not in Sprint 6 it will create bugs in beta.

---

**Key Discussion 2 — Supplement toggle design (NUTR-014):**
Kabir presented 3 options.

Option A: always visible supplement section. Clean but takes
space for users who do not take supplements.
Option B: hidden behind settings menu. Clean but hard to discover.
Option C: first-time dismissible prompt — appears once when user
opens diary post-goal-setup. User enables or dismisses. Toggle
available in diary settings if dismissed.

Ananya: about 30-40% of health-conscious Indian users take
supplements regularly. For them discoverability matters. For
the 60-70% who do not, a permanent supplement section is noise.
Option C balances both.
Priya: technically manageable — first_supplement_prompt_shown
boolean in user_profiles table.
Shristi: Option C. PRD override — PRD had specified Option A.
New approach is better for users.

---

**Key Discussion 3 — Bar graph user testing concern:**
Ananya raised a concern about AN-002 (analysis bar graph) planned
for Sprint 6. She sketched what the bar graph would look like from
Kabir's designs and showed it to 2 waitlist users informally.

Both users were confused.
User 1: "So the bar shows how much I ate? Or how much is left?"
User 2: "Does the bar going to the edge mean I hit my goal
or I went over?"

Ananya recommended: bar graph needs real user testing with a
prototype before implementation. If users cannot understand it
intuitively the entire analysis feature fails.

Kabir agreed. Will create interactive Figma prototype for testing
before implementation begins.

Shristi: needs to be tested in the first week of Sprint 6
(before March 15) so there is time to change design if needed.
Action: Kabir prototype by March 13. Ananya tests 5 users by March 20.

---

**User and Market Updates (Ananya):**
Waitlist at 156 — exceeded 150 target ahead of schedule.
5 user interviews completed (Q1 OKR target met).
Key findings: all 5 frustrated with Indian food gap. 4 of 5
track 2+ apps simultaneously. 3 of 5 interested in micronutrients
but find existing apps too complex.

Shristi: Q1 OKR user research KR is achieved. Will document.

---

**Decisions Made:**
1. FoodDiaryContext guaranteed Sprint 6 — Arjun commits explicitly. Not deferrable again.
2. Supplement toggle: Option C dismissible prompt. PRD updated.
3. Bar graph Figma prototype user-tested before Sprint 6 implementation.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Kabir creates interactive Figma prototype for AN-002 | Kabir | Mar 13 |
| Ananya tests bar graph prototype with 5 users | Ananya | Mar 20 |
| FoodDiaryContext added as Sprint 6 P0 — cannot be deferred | Shristi | Mar 12 |
| Shristi writes Q1 OKR user research KR as achieved | Shristi | Mar 15 |

---

**Next Week Focus:**
Sprint 5 complete March 11. Sprint 6 planning March 12.
MVP countdown: 19 days.

---

---

# MEETING NOTE 6 — SPRINT 6

**Document name:** Nutrivana Weekly Sync — Sprint 6
**Date:** March 19, 2025
**Sprint:** Sprint 6 (March 12-31)

---

**Sprint Health Check:**
Sprint 6 on track. Custom food (CF-001 through CF-007) progressing
well — CF-003, CF-004, CF-005, CF-006 completed. CF-007 in progress.
Analysis (AN-001 through AN-005) in progress. AN-001 complete.
AN-002 bar graph has a significant update — discussed below.
AN-004 has a specification gap — discussed below.
TECH-004 performance testing planned March 24-26.

---

**Key Discussion 1 — Bar graph user test results (AN-002):**
Ananya presented results. 5 users tested. 4 out of 5 could not
correctly read the bar graph on first view without explanation.

Most common confusion: "Does the bar reaching the edge mean I
hit my goal or I ran out of space?"
Second confusion: no indication of whether being over target
shows as the bar overflowing or stopping at the edge.

Kabir acknowledged the design failed. Three options:

Option A: text labels showing actual/target numbers on each bar.
Cluttered on mobile with 20 nutrients.
Option B: circular progress rings. Same ambiguity problem.
Option C: explicit "Xg remaining" or "Xg over target" label
beneath each bar. Bar is visual cue, text is the truth.

Ananya: Option C is best — bar gives quick visual scanning,
text gives exact information for users who want it.
Priya: implementable in Sprint 6 — 2 days to add text labels.
Shristi: 12 days before launch. Implement Option C as MVP patch
now. Create AN-CR-001 for proper redesign in Sprint 8 — the
current bar metaphor is fundamentally confusing and needs a
rethink after launch.

---

**Key Discussion 2 — AN-004 specification gap:**
Arjun raised that AN-004 (7-day trend graph) has an incomplete
specification. The PRD literally says: "The exact design of the
trend graph should be discussed with the developer and then the
specification should be written."

The specification was never written.

Shristi acknowledged this as a PRD error. She asked Arjun what
he needed to know to implement it.

Arjun's 3 questions:
1. Days with no food logged — show 0%, gap, or skip?
2. Y-axis — percentage of goal, actual grams, or both?
3. Multiple nutrients on one chart or one nutrient at a time?

Shristi's answers:
1. Show 0% for days with no logs — gaps are confusing, 0%
   accurately represents no tracking.
2. Y-axis: percentage of goal (0-120%+) — comparable across
   all nutrients regardless of gram amounts.
3. One nutrient at a time — carousel navigation consistent
   with AN-001 per-nutrient screen.

Arjun confirmed he can now implement. Shristi noted for the
record: PRD sections marked "discuss with developer" must be
completed in sprint planning, not discovered during implementation.

---

**Key Discussion 3 — Zero calorie edge case (CF-003):**
Priya raised a validation question. Current CF-003 validation
blocks saving a custom food with 0 calories. But plain black
coffee and water are legitimately zero calorie.

Kabir: black coffee and water are real foods users will log.
Blocking zero calories prevents this.
Arjun: the concern about zero is probably preventing empty
entries. But validate on empty name and serving fields, not
zero calorie value.
Shristi: allow zero calorie (≥ 0 not > 0). Validation for zero
calories is wrong. PRD corrected. Case where implementation
surfaced a PRD error.

---

**User and Market Updates (Ananya):**
Beta invites go out April 1 — 12 days. 187 confirmed waitlist
users. Ananya preparing personal invite emails for all 187.
App Store listing submitted to Apple March 18. Expected approval
March 25-27.

---

**Decisions Made:**
1. AN-002: Option C patch (explicit numbers) for MVP. AN-CR-001 for Sprint 8 redesign.
2. AN-004 spec: 0% for no-log days, % of goal Y-axis, one nutrient carousel. PRD updated.
3. CF-003: allow zero calorie (≥ 0). PRD corrected.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Priya implements Option C bar graph patch | Priya | Mar 22 |
| AN-CR-001 created in Jira for Sprint 8 | Shristi | Mar 20 |
| Arjun begins AN-004 with agreed spec | Arjun | Mar 19 |
| PRD updated with zero calorie decision and AN-004 spec | Shristi | Mar 20 |
| TECH-004 performance testing | Arjun | Mar 24-26 |
| End-to-end demo — all hands | All | Mar 25 |
| Ananya sends beta invite emails | Ananya | Apr 1 |

---

**Next Week Focus:**
Sprint 6 final push. Performance testing March 24-26.
Demo March 25. MVP ships March 31. Beta begins April 1.

---

---

# MEETING NOTE 7 — SPRINT 7

**Document name:** Nutrivana Weekly Sync — Sprint 7
**Date:** April 7, 2025
**Sprint:** Sprint 7 (April 1-14)

---

**Sprint Health Check:**
First beta sprint. 200 users active since April 1.
6 bugs reported by users in first 7 days. 4 found internally.
Total: 10 bugs this sprint.

Status April 7:
NUTR-BUG-001 (nutrients not updating after food add): Arjun
fixing, expected April 8.
AN-BUG-003 (analysis not updating after delete): same root cause
as NUTR-BUG-001, being fixed simultaneously.
GOAL-BUG-002 (gender change not triggering EER recalculation):
CRITICAL — discussed below.
GOAL-BUG-004 (micronutrient selections not saved across sessions):
CRITICAL — discussed below.
All other bugs P2 — in progress.

---

**Key Discussion 1 — GOAL-BUG-002 health escalation:**
Shristi opened with GOAL-BUG-002 as a health risk requiring
immediate escalation.

Beta user BT-023 reported: "I changed my gender from male to female
in my profile but my calorie goal did not change. I think I am
eating on the wrong budget."

Arjun confirmed: real bug. When user changes gender in profile,
EER formula recalculation is not triggered. Calorie goal stays
at old male EER value.

Shristi: a female user eating on a male calorie budget is a
meaningful health risk. Male EER is typically 400-600 calories
higher than female EER for same age and activity level. A female
user eating 2400 when her goal should be 1900 is getting
materially wrong health guidance.

Arjun: fix requires that whenever gender, age, or activity level
changes in user profile, EER formula automatically recalculates
and calorie goal updates immediately with user notification.

Shristi: this is Arjun's only priority until fixed. All other
Sprint 7 work paused for him. Target: fix and deploy by April 11.

Shristi also: she will personally message beta user BT-023 today
with an explanation and apology before the fix is deployed.
The user should not have to wait to be told what happened.

---

**Key Discussion 2 — GOAL-BUG-004 session persistence failure:**
Priya raised GOAL-BUG-004. 4 beta users reported micronutrient
selections reset on every browser refresh.

Priya explained: micronutrient selections stored in React state
only — never persisted to Supabase nutrient_targets table. Within
a session state survived. On refresh, React state destroyed and
database had no record. Bug not caught in internal testing because
team always tested within a single session. Nobody tested the
refresh scenario.

Shristi: this is the most embarrassing bug of the project.
A core feature — micronutrient goal setting — never actually saved.
Users who spent time selecting their micronutrients thought those
selections were saved. They were not.

Priya: fix is clear — persist to nutrient_targets on every change.
3 days estimated.
Arjun: second priority immediately after GOAL-BUG-002.

Team agreed: cross-session persistence testing (log out, clear
browser, log back in, verify state persists) is now in the
definition of done for any feature involving user selections.

---

**Key Discussion 3 — Root cause pattern (NUTR-BUG-001 + AN-BUG-003):**
Arjun shared that while fixing NUTR-BUG-001 he found the same
root cause behind AN-BUG-003. Both are caused by FoodDiaryContext
not being implemented — diary and analysis components reading
state independently instead of from shared context.

Implementing FoodDiaryContext correctly fixes both bugs simultaneously.

Shristi: this is the FoodDiaryContext deferred three times.
The bugs in beta are the direct consequence of those deferrals.
This pattern — defer architectural work, face bugs later — stops.

Going forward: when architectural work is identified in a
retrospective it gets a Jira ticket and a specific sprint
assignment. It cannot be deferred without a documented risk note
approved by Shristi.

---

**Metrics — First Week Beta:**
DAU: 67 (33.5% of 200 beta users).
Day 7 retention: 34%.
Custom foods created: 23 — all Indian foods. Chapati, Dal Tadka,
Paneer the top 3.
App Store early reviews: 3.8 average from 12 reviews.

Ananya's feedback themes: top complaint — totals not updating
(fixing). Second complaint — micronutrient selections resetting
(fixing). Positive: "Finally an app that lets me add chapati"
(3 separate users, unprompted). Positive: "I can finally track
my iron levels" (2 users).

Ananya: the positive feedback validates the core product direction.
The bugs are fixable. The product direction is right.

---

**Decisions Made:**
1. GOAL-BUG-002: Arjun's only priority until fixed April 11.
   Shristi personally messages user BT-023 today.
2. Cross-session persistence test added to definition of done.
3. Deferred architectural work requires Jira ticket + sprint assignment.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Fix GOAL-BUG-002 — EER recalculation on profile changes | Arjun | Apr 11 |
| Personal message to beta user BT-023 | Shristi | Apr 7 EOD |
| Fix GOAL-BUG-004 — persist micronutrient selections | Arjun/Priya | Apr 12 |
| Implement FoodDiaryContext (NUTR-BUG-001 fix) | Priya/Arjun | Apr 8 |
| Add cross-session persistence test to DoD | Shristi | Apr 8 |
| Ananya compiles full beta feedback theme report | Ananya | Apr 14 |

---

**Next Week Focus:**
Fix all P1 bugs by April 12. No new features. Stability and
user trust are the only priorities.

---

---

# MEETING NOTE 8 — SPRINT 8

**Document name:** Nutrivana Weekly Sync — Sprint 8
**Date:** April 21, 2025
**Sprint:** Sprint 8 (April 15-28)

---

**Sprint Health Check:**
Sprint 8 on track. 7 of 11 tickets completed April 21. Remaining
4 (GOAL-BUG-005, AN-CR-001, NUTR-BUG-007, NUTR-BUG-010)
in progress. All P1 bugs from Sprint 7 fixed and deployed.

---

**Key Discussion 1 — GOAL-BUG-005 tests-first approach:**
Arjun raised GOAL-BUG-005 (BMR warning shown but goal saved
incorrectly) and proposed a process change for health-critical
bugs.

The bug: when a user sets calorie goal below BMR and clicks
through the warning, the goal is saved at an incorrect value
(sometimes BMR floor, sometimes 0). Calculation path unclear.

Arjun: this is health-critical. If we fix it without understanding
the full failure mode we risk creating a worse regression.
Proposal: write tests first. Define every scenario the fixed
code must handle. Run tests against broken code to confirm they
catch the bug. Then fix until tests pass.

Shristi: this is the right approach for health-critical features.
Tests-first for BMR, EER, and calorie calculations is now a
team standard. Non-negotiable for all health-critical features
going forward.

---

**Key Discussion 2 — AN-CR-001 bar graph redesign user testing:**
Kabir presented the redesign. Progress bar fills left to right.
When on target: green and full. When over target: bar overflows —
green fills to 100%, red extension shows overflow. Text beneath
each bar: "Xg remaining" or "Xg over target."

Ananya tested with 8 beta users over 3 days (April 18-20):
8 out of 8 understood the design without explanation.
7 out of 8 said "much clearer than before."
Top comment (3 users): "I can see exactly how much more I need
to eat for each nutrient."

Shristi: 8 out of 8 without explanation is the gold standard.
Ship it. Priya confirms implementation complete by April 26.

---

**Key Discussion 3 — Codebase audit for repeated pattern:**
Shristi raised a pattern observed across Sprint 7 and Sprint 8.
The "fix applied to one component but not related components
with the same logic" problem had appeared three times:

1. NUTR-BUG-001 and AN-BUG-003 — same FoodDiaryContext root cause
2. NUTR-BUG-005 — fix applied to diary but not analysis
3. NUTR-BUG-008 — fix applied to USDA source but not custom source

Shristi: this pattern means duplicate logic across components.
Checklists do not fix duplicate logic. Shared utility functions do.

Arjun to lead codebase audit this sprint: find all duplicated
nutrient formatting logic, color logic, and search state management.
Replace with shared utility functions. Complete before Sprint 9.

---

**Metrics:**
Day 7 retention: 41% (up from 34%). Sprint 7 bug fixes directly
drove improvement.
Custom foods created: 47 (up from 23). Top 3: Chapati, Dal Tadka,
Homemade Paneer.
App Store rating: 4.0 (up from 3.8). Users who received personal
responses from Shristi left 4.5 and 5.0 star reviews.

---

**Decisions Made:**
1. Tests-first for all health-critical features — team standard.
2. AN-CR-001 progress bar redesign approved. Ship by April 26.
3. Codebase audit for shared utility functions — Arjun leads, Sprint 9 start.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Write tests for GOAL-BUG-005 before fix | Arjun | Apr 21 EOD |
| Codebase audit — shared utilities | Arjun | Apr 28 |
| AN-CR-001 implementation complete | Priya/Kabir | Apr 26 |
| Shristi drafts public launch email for beta users | Shristi | Apr 25 |
| Ananya finalises launch day social media plan | Ananya | Apr 25 |

---

**Next Week Focus:**
Complete all Sprint 8 tickets by April 28. Zero P1 bugs in
production. Product stable for May 1 public launch.

---

---

# MEETING NOTE 9 — SPRINT 9

**Document name:** Nutrivana Weekly Sync — Sprint 9
**Date:** May 7, 2025
**Sprint:** Sprint 9 (April 29 - May 12)

---

**Sprint Health Check:**
Public launch happened May 1 as planned.
Week 1 metrics: 312 Day 1 installs. 847 MAU. Day 7 retention
early read: 43%. App Store rating: 4.1.

Sprint 9 status:
AN-BUG-001 (7-day trend missing days): P0 — 12 user reports in
3 days. Arjun fixing. Expected May 8.
CF-BUG-001 (custom food edits reflecting all historical dates):
P1 — Arjun/Priya fixing, expected today.
CF-BUG-002, AN-BUG-004, AN-BUG-005: P2 — in progress.
TECH-005 data isolation testing: complete, all pass.

---

**Key Discussion 1 — CF-EPIC-001 closure and Indian food milestone:**
Shristi announced CF-EPIC-001 (Custom Food Creator epic) is being
closed this sprint. The epic was created in Sprint 2 when the
Indian food gap was discovered — 15 weeks ago.

Beta users created 47 custom Indian food entries in 4 weeks.
Top foods: Chapati (18), Dal Tadka (12), Homemade Paneer (9),
Masala Oats (7), Poha (6) — all Indian foods missing from USDA.

Shristi: 47 entries with 200 users in 4 weeks. With 3000+ users
we are on track for 800-900 entries by June 30. Well above Q2
OKR target of 200.

Kabir: this is the feature that makes Nutrivana different. Users
are building the Indian food database themselves. More valuable
every day.

Arjun: users with at least 1 custom food have 2.3x higher Day 30
retention vs users with no custom food (34% vs 15%). Custom food
is not just a feature — it is the mechanism by which Nutrivana
becomes personal to the user. Personalisation drives retention.

Shristi asked Arjun to document this finding in the Custom Food
feature adoption report formally.

---

**Key Discussion 2 — AN-BUG-001 and specification-implementation gap:**
Arjun explained. The 7-day trend graph shows gaps on days with no
food logged instead of 0%. The Sprint 6 meeting specification was
clear: "show 0% for days with no logs." Implementation returned
null for dates with no database entries. Frontend showed a gap.

12 reports in 3 days — highest volume for any single bug.
Users thought the app had lost their data.

Priya: fix is zero-fill missing days in application code. Generate
all 7 dates client-side, merge with database results, fill missing
dates with 0.

Shristi: this is the specification-implementation gap again. Spec
said 0%, code did something different. New process going forward:
for every PRD requirement, a corresponding test case that tests
exactly what the PRD says. Not what the developer assumed.

---

**Key Discussion 3 — Pregnant women engagement signal:**
Ananya shared an unexpected finding from the first week of
public launch.

She had been reviewing anonymised user profile data and noticed
a cluster of users with unusually high engagement — more sessions
per day, longer sessions, more micronutrient tracking. She
investigated their profile data.

A disproportionate number had written "pregnant" or "expecting"
in the health goals free-text field (not a structured field —
they wrote it themselves). She counted 11 such users.

These 11 users:
Average 4.2 sessions per day vs overall average of 1.8.
Average session length 6.3 minutes vs overall 2.8.
90% tracking iron, folate, and calcium specifically.

Ananya: this was not something we built for. But these users are
our most engaged by a significant margin.

Shristi: pregnant women have doctor-specified micronutrient
targets — specific folate, iron, calcium doses by trimester. No
other app tracks micronutrients at this precision level. Nutrivana
is accidentally the best app for pregnant women because of our
deep micronutrient tracking.

Arjun: if this signal is real it will show in the retention data.
Will run a cohort analysis on these users.

Kabir: we have not designed for pregnant women at all. No
trimester-specific targets, no prenatal supplement tracking,
no onboarding for pregnancy.

Shristi: this is the unexpected discovery we were looking for in
Q2 OKR Objective 3 — "identify at least one user segment with 3x
or more engagement than overall average." We need to investigate
properly. Ananya will conduct interviews with these 11 users over
the next 3 weeks. This will drive Q3 planning.

---

**Metrics:**
Week 1 post-launch:
Day 1 installs: 312.
Week 1 MAU: 847.
Day 7 retention: 43%.
App Store rating: 4.1.
Custom foods created since launch: 203 (total including beta: 250).
Dr. Priya Nambiar nutritionist post May 3: drove 156 installs
in 24 hours — highest single-day count.

---

**Decisions Made:**
1. CF-EPIC-001 closed. 2.3x retention correlation to be documented
   in feature adoption report.
2. Pregnant women segment formally investigated. Ananya interviews,
   Arjun cohort analysis.
3. New process: every PRD requirement gets a corresponding test
   case mirroring the specification exactly.

---

**Action Items:**

| Action | Owner | Due |
|---|---|---|
| Feature adoption report — Custom Food — 2.3x finding | Shristi/Arjun | May 31 |
| Pregnant women retention cohort analysis | Arjun | May 20 |
| Ananya schedules interviews with 11 pregnant women users | Ananya | May 15 |
| AN-BUG-001 zero-fill fix | Arjun/Priya | May 8 |
| CF-BUG-001 fix and deploy | Arjun/Priya | May 7 EOD |
| NPS survey launch | Ananya | May 20 |
| Sprint 9 retrospective — full Jan-May journey review | All | May 12 |

---

**Next Week Focus:**
Complete all Sprint 9 tickets by May 12. Begin Q2 metrics
tracking. Ananya begins pregnant women interviews.
Shristi starts Q2 OKR tracking.

---

---

## SUMMARY TABLE

| Meeting | Date | Sprint | 2-3 Key Decisions |
|---|---|---|---|
| Meeting 1 | Jan 7 | Sprint 1 | goal_snapshots, meal_type enum, 4 activity levels |
| Meeting 2 | Jan 22 | Sprint 2 | Custom Food fast-tracked, Indian food gap crisis |
| Meeting 3 | Feb 5 | Sprint 3 | GOAL-009 tabs to scroll, parseFloat standard, Ananya joins reviews |
| Meeting 4 | Feb 19 | Sprint 4 | Food-specific serving units, FoodDiaryContext deferred P0, color logic |
| Meeting 5 | Mar 5 | Sprint 5 | FoodDiaryContext deferred 3rd time, supplement Option C, bar graph user test |
| Meeting 6 | Mar 19 | Sprint 6 | Bar graph Option C patch, AN-004 spec filled, zero calorie allowed |
| Meeting 7 | Apr 7 | Sprint 7 | GOAL-BUG-002 health escalation, GOAL-BUG-004 persistence failure |
| Meeting 8 | Apr 21 | Sprint 8 | Tests-first standard, bar graph redesign approved, codebase audit |
| Meeting 9 | May 7 | Sprint 9 | CF-EPIC-001 closed, 2.3x retention finding, pregnant women discovered |

---

## GPT-4o GENERATION INSTRUCTIONS

Generate 9 Word documents — one per meeting note.

**Format:**
Professional header with company name, meeting title, date,
sprint number, attendees.
Sections separated by bold headers.
Action items as a clean table with Owner and Due Date.
Decisions as a numbered list.

**Tone:**
Meeting notes are written as live capture of real conversations.
Key discussions read like the conversation actually happened —
specific people saying specific things, disagreeing, then reaching
a decision. Not "the team discussed X." But "Arjun said... Priya
said... Shristi decided..."

This voice quality is what makes meeting notes rich for PrismAI.
"What did Arjun think about FoodDiaryContext" must be answerable.

**Story threads across all 9 documents:**
1. FoodDiaryContext: deferred Meetings 4, 5, 6 with escalating
   concern. Comes back as NUTR-BUG-001 cause in Meeting 7.
2. Indian food gap: first informally Meeting 1, crisis Meeting 2,
   resolution tracked through to triumph in Meeting 9.
3. Bar graph confusion: risk raised Meeting 5, results Meeting 6,
   redesign approved Meeting 8.
4. Pregnant women: genuine surprise discovery in Meeting 9 only.
   Not mentioned before. Treat as a real product insight moment.

**Critical numbers — must match across all documents:**
Day 7 retention: 34% Sprint 7, 41% Sprint 8, 43% Sprint 9 early read.
Custom foods: 23 mid-Sprint 7, 47 end Sprint 8, 250 post-launch.
App Store: 3.8 Sprint 7, 4.0 Sprint 8, 4.1 Sprint 9.
MAU: 847 week 1 post-launch.