# Round 2 — Sprint Planning and Retrospective Definitions
## All 9 Sprints — January 1 to May 12, 2025

---

## GLOBAL RULES FOR ALL SPRINT DOCUMENTS

**Sprint Planning format:** Word document (.docx)
**Sprint Retrospective format:** Excel document (.xlsx)
**Author of all planning documents:** Shristi Sharmistha
**Author of all retrospectives:** Shristi Sharmistha (with team input)

**Retrospective Excel structure (Format B):**
Sheet 1: Sprint Summary
- Sprint goal, dates, team capacity, delivery vs commitment table
Sheet 2: Retrospective Narrative
- What went well, what did not, key learnings, decisions made,
  action items with owners and due dates, team health note
Sheet 3: Metrics This Sprint
- Any measurable outcomes from this sprint

---

---

# SPRINT 1

## SPRINT 1 PLANNING DOCUMENT

**Document name:** Sprint 1 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** January 1, 2025
**Sprint dates:** January 1 to January 14, 2025
**Sprint goal:** Establish the complete technical foundation before
any feature development begins. No feature code ships this sprint.
Only infrastructure, research, and architecture.

---

**Team Capacity:**
- Arjun Mehta: 10 days (full sprint)
- Priya Nair: 5 days (joining mid-sprint January 7, 
  setting up development environment first 6 days)
- Kabir Sharma: 10 days (working on design system and 
  initial wireframes in parallel)
- Ananya Iyer: 10 days (beginning waitlist collection)
- Shristi Sharmistha: 10 days (PRD finalisation, team coordination)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Story Points | Priority |
|---|---|---|---|---|
| TECH-001 | Database schema design | Arjun | 3 | P0 |
| TECH-003 | Authentication and user session management | Arjun | 5 | P0 |
| NUTR-TASK-003 | Date-stamped diary data model design | Arjun | 5 | P0 |
| GOAL-SPIKE-001 | Research EER formulas by age gender activity level | Arjun | 2 | P0 |
| GOAL-SPIKE-002 | Research RDA values for all micronutrients | Arjun | 2 | P1 |
| NUTR-EPIC-001 | Create Food Diary Core epic | Shristi | 1 | P0 |
| GOAL-EPIC-001 | Create Calorie Goal Setting epic | Shristi | 1 | P0 |
| GOAL-EPIC-002 | Create Macro and Micro Goal Setting epic | Shristi | 1 | P0 |

**Total story points committed: 20**

---

**Sprint Goal Success Criteria:**
- Supabase database schema designed with all tables, columns,
  and RLS policies defined
- JWT authentication with refresh token strategy implemented
  and tested
- EER formula research completed — all 15 variants documented
  with sources
- RDA micronutrient research completed for all tracked nutrients
- All 3 epics created in Jira with child tickets listed
- Technical spec draft begun (to be completed by January 10)

---

**Dependencies:**
- Supabase account created and configured before TECH-001 begins
- Google Cloud project created for future Drive and Gmail APIs
  (not Sprint 1 scope but account setup needed now)
- Priya onboarding completed by January 7 so she can review
  schema design and raise frontend concerns early

---

**Risks:**
- GOAL-SPIKE-001 may reveal complexity in EER formula variants
  that pushes GOAL-001 (calorie goal implementation) timeline.
  Mitigation: spike starts January 2, Arjun shares findings with
  Shristi by January 7 to assess impact.
- Priya starting mid-sprint means first feature implementation
  sprint (Sprint 2) depends on her being fully onboarded.
  Mitigation: Kabir shares design system with Priya on day 1.

---

**Definition of Done for Sprint 1:**
All tickets moved to Done in Jira. Database schema reviewed and
approved by Shristi. Authentication tested with 2 test user accounts.
Both spike research documents shared in team Slack and acknowledged
by Shristi. Technical spec Section 1-4 written by Arjun.

---

## SPRINT 1 RETROSPECTIVE

**Document name:** Sprint 1 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** January 14, 2025
**Facilitated by:** Shristi Sharmistha

---

**SHEET 1: SPRINT SUMMARY**

Sprint goal: Establish complete technical foundation before feature
development begins.

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| TECH-001 | Yes | Yes | Delivered Jan 8 — 2 days ahead of estimate |
| TECH-003 | Yes | Yes | Delivered Jan 10 — JWT + refresh token implemented |
| NUTR-TASK-003 | Yes | Yes | Delivered Jan 11 — goal_snapshots pattern agreed |
| GOAL-SPIKE-001 | Yes | Yes | Delivered Jan 7 — 15 formula variants documented |
| GOAL-SPIKE-002 | Yes | Yes | Delivered Jan 9 — RDA table completed |
| NUTR-EPIC-001 | Yes | Yes | Epic created with all child tickets listed |
| GOAL-EPIC-001 | Yes | Yes | Epic created |
| GOAL-EPIC-002 | Yes | Yes | Epic created |

Delivery rate: 8 out of 8 tickets. 100%. All story points delivered.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 1 was the most important sprint in the project even though
no user-facing feature was built. The architectural decisions made
this sprint — Supabase RLS policies, JWT refresh token strategy,
goal_snapshots data model, dual date storage (date_string + UTC) —
shaped every subsequent sprint. Getting these right now prevented
significant rework later.

**What went well:**

1. Arjun's spike-first approach worked perfectly. By completing
   GOAL-SPIKE-001 and GOAL-SPIKE-002 before any implementation,
   the team had complete EER formula and RDA data before a single
   line of goal setting code was written. This prevented the
   rework that would have happened if implementation started
   without complete data.

2. The NUTR-TASK-003 debate about empty diary representation
   (goal_snapshots pattern) was the most valuable architectural
   conversation of the entire project. Shristi caught the empty
   diary problem by reading the PRD requirement carefully —
   "when a previous date is selected and FD is not filled, an
   empty food diary with target nutrient columns must be displayed."
   This requirement implied that columns are derived from goals,
   not from food logs. The goal_snapshots solution ensures past
   diary entries always show the correct goal structure for that
   date even if goals change later.

3. TECH-003 auth debate about session persistence vs JWT expiry
   was resolved well — 1-hour access token + 30-day refresh token
   gives users a seamless experience without compromising security.

**What did not go well:**

1. Priya's mid-sprint start (January 7) meant she had no input
   on TECH-001 database schema or TECH-003 auth before they were
   implemented. She raised two frontend concerns on January 8 that
   required minor schema adjustments. In future, frontend engineer
   should review backend schema before it is finalised even if
   implementation has not started.

2. Technical spec was not completed by January 10 as planned.
   Arjun completed Sections 1-4 but Sections 5-10 (search
   architecture, performance targets, deployment) were not written
   until after Sprint 2 when the full picture was clearer.
   The spec was approved January 10 but was incomplete.

**Key learnings:**

1. Architecture decisions need to be made before feature
   implementation, not alongside it. Sprint 1 proved that
   2 weeks of architecture work prevents months of rework.

2. Spike research should always happen one sprint before
   the implementation sprint. GOAL-SPIKE-001 results directly
   unblocked GOAL-001 and GOAL-002 in Sprint 2.

3. Full team review of database schema before implementation
   is non-negotiable even if some team members are onboarding.

**Decisions made this sprint:**

1. Dual date storage approach — local date_string for queries,
   UTC timestamp for audit (from NUTR-TASK-003 discussion).
   This decision prevents midnight boundary bugs for IST users.

2. JWT + 30-day refresh token strategy (from TECH-003 discussion).
   Users never see the login screen if they open the app within
   30 days.

3. goal_snapshots pattern for date-accurate diary rendering
   (from NUTR-TASK-003 discussion). This is the most important
   architectural decision of Sprint 1.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Complete Technical Spec Sections 5-10 | Arjun | Jan 28 |
| Priya to review TECH-001 schema and raise any frontend concerns | Priya | Jan 15 |
| Shristi to finalise PRDs for Food Logging and Goal Setting before Sprint 3 | Shristi | Jan 28 |
| Ananya to share waitlist signup page with team for review | Ananya | Jan 15 |

**Team health:** 4/5
Strong start. Team aligned on architecture. Priya's late start created
minor friction but resolved quickly. Arjun carried Sprint 1 almost
entirely — team capacity will balance in Sprint 2 when Priya is
fully onboarded and Kabir shares design system.

---

**SHEET 3: METRICS THIS SPRINT**
No user metrics available (pre-launch sprint).
Technical foundation metrics:
- Database tables designed: 12 tables
- RLS policies implemented: 12 (one per table)
- EER formula variants documented: 15
- Micronutrients with RDA values documented: 40+
- Authentication: JWT + refresh token implemented and tested

---

---

# SPRINT 2

## SPRINT 2 PLANNING DOCUMENT

**Document name:** Sprint 2 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** January 15, 2025
**Sprint dates:** January 15 to January 28, 2025
**Sprint goal:** Complete USDA database integration with search
working under 1 second, and begin goal setting implementation
with EER formula fully working for all user profiles.

---

**Team Capacity:**
- Arjun Mehta: 10 days (full sprint)
- Priya Nair: 10 days (fully onboarded, first full sprint)
- Kabir Sharma: 10 days (designing goal setting screens)
- Ananya Iyer: 10 days (waitlist building, user interview scheduling)
- Shristi Sharmistha: 10 days (PRD review, sprint coordination)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| NUTR-TASK-001 | USDA database integration and API setup | Arjun | 8 | P0 |
| NUTR-TASK-002 | Fuzzy search implementation | Arjun/Priya | 8 | P0 |
| GOAL-001 | Set calorie goal with EER calculation | Arjun | 5 | P0 |
| GOAL-002 | EER formula implementation all variants | Arjun | 8 | P0 |
| GOAL-003 | Required deficit surplus calculation | Arjun | 3 | P1 |
| GOAL-004 | BMR validation with warning message | Arjun | 3 | P1 |

**Total story points committed: 35**

---

**Sprint Goal Success Criteria:**
- 300,000+ USDA foods importable into Supabase and searchable
- Search returns results under 1 second for all query types
- "chiken" returns "chicken" (fuzzy matching working)
- User can set calorie goal — EER calculated correctly for
  at least 5 different user profiles (male/female, ages 19-65)
- BMR validation blocks below-BMR calorie goals with correct
  error message

---

**Dependencies:**
- GOAL-SPIKE-001 (Sprint 1) must be complete — EER formula
  research needed before GOAL-001 and GOAL-002 can start
- Supabase database schema (TECH-001) must be finalised
  before USDA import begins

---

**Risks:**
- USDA API may have rate limits that prevent real-time search.
  Mitigation: Arjun investigates API limits on Day 1. If rate
  limits are a problem, switch to bulk import approach.
  Decision needed by January 17.
- EER formula complexity (15 variants) may make GOAL-002 spill
  into Sprint 3. Mitigation: GOAL-002 is the highest priority
  implementation ticket — Arjun starts it January 15 alongside
  NUTR-TASK-001.

---

## SPRINT 2 RETROSPECTIVE

**Document name:** Sprint 2 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** January 28, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| NUTR-TASK-001 | Yes | Yes | Delivered Jan 24. USDA rate limit discovery → bulk import |
| NUTR-TASK-002 | Yes | Yes | Delivered Jan 27. Hybrid ILIKE + trigram solution |
| GOAL-001 | Yes | Yes | Delivered Jan 25. PRD activity level mismatch resolved |
| GOAL-002 | Yes | Yes | Delivered Jan 27. All 15 EER variants with unit tests |
| GOAL-003 | Yes | Yes | Delivered Jan 25 |
| GOAL-004 | Yes | Yes | Delivered Jan 26 |

Delivery rate: 6 out of 6 tickets. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 2 was where reality first collided with the plan. Two
significant discoveries changed our approach: (1) USDA API has
rate limits that make real-time search impossible at scale —
we switched to bulk import. (2) The USDA database has almost
no Indian foods — chapati, dal, paneer, idli are missing.
Both discoveries were made early enough in the sprint to pivot.
The team handled both well.

**What went well:**

1. Arjun discovered the USDA rate limit problem on Day 1
   (January 15) and immediately proposed the bulk import
   solution. The decision was made within 48 hours. This is
   exactly the right response to an unexpected technical blocker.

2. The hybrid ILIKE + trigram search solution from NUTR-TASK-002
   is technically elegant. The 3-character minimum problem with
   trigrams (where "dal" returns 0 results) was caught by Priya
   during testing and solved with the hybrid approach. Search
   now returns results under 200ms for all query types.

3. The PRD activity level mismatch (5 levels in PRD vs 4 in USDA)
   discovered in GOAL-001 was handled correctly — Shristi made
   a clear product decision to use 4 USDA levels and updated
   the PRD immediately. No ambiguity left for future sprints.

**What did not go well:**

1. The Indian food gap was a known risk that should have been
   investigated before Sprint 2 began. We were surprised by
   the extent of the gap — not just a few missing foods but
   almost all common Indian foods absent from the USDA database.
   This should have been in the Sprint 1 risk register.

2. Arjun carried the entire sprint again — all 6 tickets were
   primarily his work. Priya contributed to NUTR-TASK-002 but
   most of Sprint 2 was backend heavy. Sprint 3 and 4 will
   start balancing this with frontend work.

**Key learnings:**

1. Never assume external data sources have the coverage you need.
   Validate data quality before building on it. The Indian food
   gap should have been investigated in Sprint 1.

2. Architecture pivots (real-time API → bulk import) are much
   cheaper in Sprint 2 than Sprint 6. The early discovery
   of the rate limit saved significant rework.

**Decisions made this sprint:**

1. USDA bulk import instead of real-time API (NUTR-TASK-001).
   Performance: 200ms average search response time.

2. Custom Food feature fast-tracked to Sprint 5 (not originally
   planned) to address Indian food gap. This adds scope to Q1/Q2
   but is the right product decision.

3. PRD updated — 4 activity levels (USDA standard) not 5 (GOAL-001).

4. EER age-group auto-transition (birthday formula switch) deferred
   to V2 — too complex for V1, documented as known limitation.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Add Custom Food to roadmap and create epic NUTR-CF-EPIC-001 | Shristi | Feb 3 |
| Document Indian food gap — top 20 missing foods with user priority | Shristi/Ananya | Feb 10 |
| Arjun to write unit tests for all 15 EER formula variants | Arjun | Feb 3 |
| Priya to begin reviewing GOAL-001 through GOAL-004 frontend requirements | Priya | Jan 29 |

**Team health:** 4/5
Good sprint despite surprises. The team's ability to pivot quickly
on the USDA rate limit issue was impressive. The Indian food gap
discovery created anxiety — is the product viable for Indian users?
Decision to fast-track Custom Food resolved that anxiety. Team
morale good but Arjun is carrying a heavy load. Sprints 3-5 will
distribute work more evenly.

---

---

# SPRINT 3

## SPRINT 3 PLANNING DOCUMENT

**Document name:** Sprint 3 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** January 29, 2025
**Sprint dates:** January 29 to February 11, 2025
**Sprint goal:** Complete all macro and micro goal setting so users
can set comprehensive nutrition targets. Begin the first food diary
UI components.

---

**Team Capacity:**
- Arjun Mehta: 10 days
- Priya Nair: 10 days (first sprint with significant frontend work)
- Kabir Sharma: 10 days (goal setting UI designs ready for Priya)
- Ananya Iyer: 10 days
- Shristi Sharmistha: 10 days

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| GOAL-005 | Default macro distribution 40:30:30 | Arjun | 2 | P1 |
| GOAL-006 | Custom macro percentage input | Priya | 3 | P1 |
| GOAL-007 | Validate macros sum to 100% | Priya | 3 | P1 |
| GOAL-008 | Select macros to track | Priya | 2 | P1 |
| GOAL-009 | View micronutrient list by category | Kabir/Priya | 5 | P1 |
| GOAL-010 | Select micronutrients to track | Arjun | 3 | P1 |
| GOAL-011 | Edit custom micronutrient goal values | Arjun | 2 | P2 |
| GOAL-012 | RDA values by age and gender loaded | Arjun | 2 | P1 |
| NUTR-005 | Food diary view with goal nutrient columns | Priya | 3 | P0 |
| NUTR-006 | Select meal type | Priya | 2 | P0 |

**Total story points committed: 27**

---

**Sprint Goal Success Criteria:**
- User can complete entire macro goal setup end to end
- Macro validation catches floating point edge cases
  (33.33 + 33.33 + 33.34 = 100.00 shown as valid)
- Micronutrient list shows all 40+ nutrients in categories
- User can select up to 20 micronutrients to track
- Food diary skeleton visible with dynamic nutrient columns
  based on user's goal selections

---

**Context note for this sprint:**
Sprint 3 is the first sprint where Priya has significant ownership.
Goal setting frontend is Priya's work. Kabir has completed Figma
designs for all goal setting screens. The PRD override on
micronutrient list design (tabs vs single scroll) may happen
during implementation — team empowered to make this call
without escalating to Shristi if the reasoning is clear.

---

## SPRINT 3 RETROSPECTIVE

**Document name:** Sprint 3 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** February 11, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| GOAL-005 | Yes | Yes | Feb 3 — first-time check for default correctly implemented |
| GOAL-006 | Yes | Yes | Feb 4 — no debounce decision made |
| GOAL-007 | Yes | Yes | Feb 8 — floating point fix parseFloat(toFixed(2)) |
| GOAL-008 | Yes | Yes | Feb 5 — untracked macros still recalculate |
| GOAL-009 | Yes | Yes | Feb 10 — PRD override: tabs → single scroll |
| GOAL-010 | Yes | Yes | Feb 6 — auto-recalculate on age/gender change |
| GOAL-011 | Yes | Yes | Feb 7 — custom override never touched by system |
| GOAL-012 | Yes | Yes | Feb 3 — Potassium unit discrepancy handled |
| NUTR-005 | Yes | Yes | Feb 10 — horizontal scroll confirmed intentional |
| NUTR-006 | Yes | Yes | Feb 10 — supplement toggle confirmed persistent |

Delivery rate: 10 out of 10. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 3 completed the entire goal setting feature. By end of this
sprint, a user can set calorie, macro, and micronutrient goals
completely. Two notable things happened: (1) Priya discovered a
real JavaScript floating point precision bug in GOAL-007 that would
have caused validation failures for users entering 33.33/33.33/33.34.
The fix (parseFloat(toFixed(2))) is now applied consistently.
(2) The team made their first PRD override — changing the
micronutrient list from tabs to single scroll based on Ananya's
user feedback about discoverability.

**What went well:**

1. The floating point discovery in GOAL-007 shows the value of
   Priya testing edge cases. 33.33 + 33.33 + 33.34 = 99.99999999
   in JavaScript. This would have frustrated users trying to set
   equal macro splits. Caught and fixed before any user saw it.

2. The PRD override on GOAL-009 (tabs to single scroll) was the
   team's first independent product decision. Kabir proposed it,
   Ananya validated it with user perspective, Shristi approved.
   The decision was made and documented in 48 hours.

3. Priya fully ramped up this sprint — she owned 5 of 10 tickets
   and delivered all on time. Team capacity balance much better.

**What did not go well:**

1. GOAL-009 took the longest of any Sprint 3 ticket (11 days vs
   3-day estimate) because the PRD override required new Figma
   designs from Kabir, implementation changes from Priya, and
   final design review. PRD overrides need to be flagged as
   scope-change risks in sprint planning.

2. The Potassium unit discrepancy in GOAL-012 (target in grams,
   data in mg) was caught late — on the day of implementation.
   Data quality checks on reference data should happen before
   the implementation sprint, not during.

**Key learnings:**

1. PRD overrides add scope — flag them explicitly in sprint
   planning as a risk. GOAL-009 took 4x estimated time because
   of the unplanned redesign.

2. Floating point arithmetic is a recurring source of bugs in
   nutrition calculations. The parseFloat(toFixed(2)) approach
   is now a team standard for all nutrient value displays.

3. Ananya's user perspective was critical in the GOAL-009
   decision. She should be more involved in design reviews
   earlier, not just as a late-stage validator.

**Decisions made this sprint:**

1. Micronutrient list: single scroll with sticky category headers
   instead of tabs (GOAL-009). PRD updated.

2. parseFloat(toFixed(2)) rounding standard for all numeric
   nutrient displays (from GOAL-007 fix).

3. Untracked macros still recalculate in background — they are
   hidden from diary but values remain accurate if re-enabled
   (GOAL-008).

4. Supplement toggle is a persistent global setting, not a
   per-day toggle (NUTR-006).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Add PRD override documentation process to team norms | Shristi | Feb 15 |
| Apply parseFloat(toFixed(2)) audit across all existing calculation code | Priya/Arjun | Feb 20 |
| Ananya to join all design reviews from Sprint 4 onwards | Shristi | Ongoing |
| Schedule data quality pre-check for USDA nutrient data before Sprint 4 | Arjun | Feb 14 |

**Team health:** 5/5
Best sprint energy so far. Priya fully in flow. Kabir producing
great designs. The floating point find and the PRD override both
gave the team confidence in their own judgement. No escalations
needed this sprint. Team working well together.

---

---

# SPRINT 4

## SPRINT 4 PLANNING DOCUMENT

**Document name:** Sprint 4 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** February 12, 2025
**Sprint dates:** February 12 to February 25, 2025
**Sprint goal:** Build the core food logging flow end to end —
user can search food, adjust portion, add to diary, and see
nutrient totals with goal comparison. First time the product
feels real.

---

**Team Capacity:**
- Arjun Mehta: 10 days
- Priya Nair: 10 days
- Kabir Sharma: 10 days
- Ananya Iyer: 10 days
- Shristi Sharmistha: 10 days

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| NUTR-007 | Select USDA food database as source | Priya | 2 | P0 |
| NUTR-008 | Search food with fuzzy matching | Priya | 2 | P0 |
| NUTR-009 | Adjust portion size with recalculation | Arjun/Priya/Kabir | 8 | P0 |
| NUTR-010 | Add food to diary and redirect | Priya | 3 | P0 |
| NUTR-015 | View only goal nutrients as columns | Priya | 2 | P0 |
| NUTR-016 | View cumulative nutrient totals | Priya | 2 | P0 |
| NUTR-017 | Compare actual vs goal with color coding | Kabir/Priya | 3 | P0 |
| NUTR-018 | Per meal nutrient breakdown | Priya | 2 | P1 |
| NUTR-TASK-004 | Real-time nutrient calculation engine | Arjun/Priya | 5 | P0 |

**Total story points committed: 29**

---

**Sprint Goal Success Criteria:**
- User can complete full logging flow: search → select →
  adjust portion → add → see in diary
- Nutrient totals update within 1 second of adding food
- Color coding correct for all three weight goal types
  (loss/gain/maintain)
- Serving units are food-specific (oats cup ≠ spinach cup)
- Diary columns show only tracked nutrients

---

**Context note for this sprint:**
Sprint 4 is the most important sprint in the build phase.
The product first becomes demoable this sprint. Shristi will
do a full end-to-end demo walkthrough on February 24 as a
dry run for the MVP demo. Any blocker discovered in the dry
run will be escalated immediately.

---

## SPRINT 4 RETROSPECTIVE

**Document name:** Sprint 4 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** February 25, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| NUTR-007 | Yes | Yes | Feb 17 — two-step API design |
| NUTR-008 | Yes | Yes | Feb 17 — 2-char minimum added |
| NUTR-009 | Yes | Yes | Feb 24 — food-specific serving units discovered |
| NUTR-010 | Yes | Yes | Feb 19 — optimistic update pattern |
| NUTR-015 | Yes | Yes | Feb 20 — dash for zero and missing confirmed |
| NUTR-016 | Yes | Yes | Feb 22 — sticky total row |
| NUTR-017 | Yes | Yes | Feb 23 — weight maintain yellow not red |
| NUTR-018 | Yes | Yes | Feb 22 — always show even single food |
| NUTR-TASK-004 | Yes | Yes | Feb 24 — client-side calculation engine |

Delivery rate: 9 out of 9. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 4 was the most exciting sprint yet — the product became
real and demoable for the first time. The February 24 dry run
with Shristi went cleanly. Two major architectural discoveries
shaped this sprint: (1) USDA foods have food-specific serving
units — a cup of oats is 156g but a cup of spinach is 30g.
The PRD never mentioned this. (2) The FoodDiaryContext was
planned but not implemented this sprint — this will come back
as NUTR-BUG-001 in Sprint 7.

**What went well:**

1. The food-specific serving unit discovery in NUTR-009 was
   handled excellently. Arjun investigated the USDA data,
   found the problem, and the three-way discussion between
   Arjun (technical), Kabir (UX), and Shristi (product)
   resolved the right solution in one day.

2. The client-side calculation engine (NUTR-TASK-004) is the
   right architecture — calculating client-side instead of
   server-side guarantees 1-second performance even on slow
   connections. This decision prevents a class of latency
   bugs that would have appeared in beta.

3. The weight maintain color coding decision in NUTR-017
   (yellow not red for over-calorie) was correctly implemented
   and clearly documented. The weight_goal_type variable is
   now the single source of truth for color logic across
   the entire app.

**What did not go well:**

1. FoodDiaryContext was identified as needed but not
   implemented this sprint. We knew it was required but
   deferred it. This created NUTR-BUG-001 and AN-BUG-003
   in Sprint 7. Technical debt always comes back.

2. NUTR-009 took 12 days (entire sprint) vs 5-day estimate.
   The food-specific serving unit discovery was unforeseeable
   but added significant scope. When an architectural discovery
   happens mid-sprint it needs to be flagged as a sprint risk
   immediately.

**Key learnings:**

1. Deferred architectural work (FoodDiaryContext) creates
   future bugs. If you know something is needed, build it
   now, not later.

2. USDA data structure assumptions should be validated before
   planning the implementation sprint. Serving units were a
   surprise. What else in the USDA data structure are we
   not checking?

3. The optimistic update pattern (POST returns full entry,
   no refetch needed) should be the standard for all diary
   operations. Document this as a team pattern.

**Decisions made this sprint:**

1. Food-specific serving units from USDA data, not generic
   dropdown list (NUTR-009).

2. Client-side calculation engine on food log array state
   changes (NUTR-TASK-004).

3. Weight maintain calorie: yellow for both over and under,
   never red — clinical decision (NUTR-017).

4. Optimistic update as standard pattern for all diary
   API operations (NUTR-010).

5. Sticky total row always visible while scrolling (NUTR-016).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Implement FoodDiaryContext in Sprint 5 before it is needed | Priya/Arjun | Mar 3 |
| Audit USDA data structure for any other unexpected formats | Arjun | Mar 1 |
| Document optimistic update pattern in technical spec | Arjun | Mar 7 |
| Schedule full February 24 demo recording for Ananya to share with waitlist | Ananya | Feb 28 |

**Team health:** 5/5
The moment the food diary worked end to end on February 24 was
genuinely exciting. Team morale at highest point. Product is real.
Priya and Arjun paired effectively on NUTR-009. Kabir's design
system is making implementation faster each sprint. Ananya starting
to build waitlist momentum.

---

---

# SPRINT 5

## SPRINT 5 PLANNING DOCUMENT

**Document name:** Sprint 5 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** February 26, 2025
**Sprint dates:** February 26 to March 11, 2025
**Sprint goal:** Complete all remaining food logging flows
(supplement, edit, delete, date-wise diary, all custom sources)
and begin custom food creation. By end of this sprint the food
diary is functionally complete for V1.

---

**Team Capacity:**
- Arjun Mehta: 10 days
- Priya Nair: 10 days
- Kabir Sharma: 10 days
- Ananya Iyer: 10 days (scheduling user interviews for March)
- Shristi Sharmistha: 10 days

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| NUTR-011 | Select custom recipe source | Priya | 2 | P1 |
| NUTR-012 | Select custom food source | Priya | 2 | P1 |
| NUTR-013 | Log custom meal without portion adjust | Priya | 2 | P1 |
| NUTR-014 | Supplement section toggle | Kabir/Priya | 5 | P1 |
| NUTR-019 | Edit logged item portion size | Priya | 3 | P1 |
| NUTR-020 | Delete logged item with confirmation | Priya | 2 | P1 |
| NUTR-021 | Recalculate totals on add edit delete | Priya/Arjun | 5 | P0 |
| NUTR-022 | Separate diary per date with date picker | Arjun/Priya | 8 | P0 |
| NUTR-023 | Fresh empty diary on new day | Priya | 1 | P1 |
| NUTR-024 | Auto-save all diary actions | Priya | 1 | P0 |
| NUTR-025 | Edit food logs for past and future dates | Arjun/Priya | 2 | P1 |
| NUTR-026 | Duplicate food warning | Priya | 1 | P2 |
| CF-001 | Create custom food with name serving value unit | Priya/Arjun | 3 | P1 |
| CF-002 | Add nutrient values to custom food | Priya/Arjun | 3 | P1 |

**Total story points committed: 40**

**Note:** Sprint 5 is the largest sprint in the project (14 tickets,
40 points). This is intentional — most of these tickets are small
completions of the food diary feature. Priya is fully in flow on
food diary work and the patterns are established.

---

## SPRINT 5 RETROSPECTIVE

**Document name:** Sprint 5 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** March 11, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| NUTR-011 | Yes | Yes | Mar 3 — reusable search component |
| NUTR-012 | Yes | Yes | Mar 3 — two-column list with calorie |
| NUTR-013 | Yes | Yes | Mar 4 — skip portion adjust for custom meal |
| NUTR-014 | Yes | Yes | Mar 9 — PRD override: dismissible prompt |
| NUTR-019 | Yes | Yes | Mar 5 — editingOriginalValues restore pattern |
| NUTR-020 | Yes | Yes | Mar 4 — optimistic deletion |
| NUTR-021 | Yes | Yes | Mar 10 — 100ms debounce for performance |
| NUTR-022 | Yes | Yes | Mar 10 — dual date storage IST + UTC |
| NUTR-023 | Yes | Yes | Mar 3 — no special logic needed |
| NUTR-024 | Yes | Yes | Mar 3 — auto-save via optimistic updates |
| NUTR-025 | Yes | Yes | Mar 4 — date_string architecture handles this |
| NUTR-026 | Yes | Yes | Mar 5 — USDA only bug seeded here |
| CF-001 | Yes | Yes | Mar 7 — serving unit free-text |
| CF-002 | Yes | Yes | Mar 8 — accordion grouping |

Delivery rate: 14 out of 14. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 5 completed the food diary feature entirely and began
custom food. The team delivered 14 tickets — the most in any
sprint — without missing a single one. Three things stand out:
(1) The IST timezone midnight problem discovered in NUTR-022
was architecturally complex but resolved correctly. (2) The
supplement toggle PRD override (Option C — dismissible prompt)
was the team's best product decision so far. (3) The duplicate
check only covers USDA food IDs — a gap that will become
NUTR-BUG-002 in Sprint 8.

**What went well:**

1. The reusable search component from NUTR-011 is a genuine
   engineering win — one component handles USDA, custom food,
   and custom recipe sources. Reduced implementation time for
   NUTR-011, NUTR-012, and will reduce future search features.

2. The 100ms debounce solution in NUTR-021 is an example of
   the team solving a problem that was not in the PRD. Priya
   found the performance lag on mid-range Android during testing.
   The PRD interpretation ("within 1 second after an action"
   = after the last action) was clever and correct.

3. The supplement toggle Option C decision (dismissible prompt)
   was the right balance between clean UI and discoverability.
   Kabir and Ananya's combined perspective — design and user
   research — produced a better solution than either alone.

**What did not go well:**

1. NUTR-026 duplicate check was implemented for USDA food IDs
   only. The custom food ID namespace gap was noted during
   implementation but not fixed. This will become NUTR-BUG-002
   in Sprint 8. Known gaps should be fixed in the same sprint,
   not deferred.

2. The offline data loss risk was identified in NUTR-024 but
   deferred to V2 without a temporary mitigation. A network
   status indicator was added later in Sprint 6. Should have
   been added in Sprint 5 when the risk was identified.

**Key learnings:**

1. When you identify a known gap (NUTR-026 custom food IDs),
   fix it in the same sprint. Known gaps always cost more to
   fix later than to address now.

2. The reusable component pattern works. Invest in abstraction
   early — it pays off across multiple tickets.

3. Product decisions (supplement toggle Option C) are better
   when multiple perspectives (design, user research, product)
   are involved simultaneously.

**Decisions made this sprint:**

1. Supplement toggle: dismissible prompt (Option C) — not
   hidden, not always visible (NUTR-014).

2. Duplicate storage: local date_string + UTC timestamp
   (NUTR-022). V1 for Indian users, migration path preserved.

3. Custom food serving unit: free-text, not dropdown
   (CF-001). Opposite of USDA which uses food-specific units.

4. 100ms debounce on recalculation (NUTR-021). PRD compliant
   ("after the action" = after the last action).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Extend duplicate check to custom food IDs in Sprint 8 | Priya | Sprint 8 |
| Add network status indicator in Sprint 6 | Arjun | Sprint 6 |
| Ananya to schedule 5 user interviews for March research | Ananya | Mar 20 |
| Shristi to complete user research report by Mar 31 | Shristi | Mar 31 |

**Team health:** 5/5
Best sprint of the project. 14 tickets, 100% delivery. Team
confidence high. The food diary feature being complete feels like
a genuine milestone. Custom food beginning shows the team can
execute at speed without cutting corners. MVP is 3 weeks away.

---

---

# SPRINT 6

## SPRINT 6 PLANNING DOCUMENT

**Document name:** Sprint 6 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** March 12, 2025
**Sprint dates:** March 12 to March 31, 2025
**Sprint goal:** Complete custom food management and build the
entire analysis feature. Ship MVP on March 31. No scope additions
this sprint — focus is completion and quality.

---

**Team Capacity:**
- Arjun Mehta: 14 days (sprint extended to March 31 for MVP)
- Priya Nair: 14 days
- Kabir Sharma: 14 days
- Ananya Iyer: 14 days (App Store listing, waitlist communications)
- Shristi Sharmistha: 14 days

**Note:** Sprint 6 is a 3-week sprint (14 working days) to ensure
MVP ships on March 31 without rushing. All Sprint 6 tickets
are scope-locked — no new tickets can be added after March 15.

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| CF-003 | Save custom food with validation | Priya/Arjun | 5 | P0 |
| CF-004 | Search and select custom food | Priya | 2 | P1 |
| CF-005 | Edit custom food | Priya/Arjun | 3 | P1 |
| CF-006 | Delete custom food | Priya | 1 | P2 |
| CF-007 | Retroactive change reflects from edit date | Arjun | 5 | P1 |
| AN-001 | Per nutrient analysis screen | Kabir/Priya | 3 | P1 |
| AN-002 | Daily bar graph actual vs target | Kabir/Priya/Ananya | 8 | P0 |
| AN-003 | Color coding yellow green red | Kabir/Priya | 3 | P0 |
| AN-004 | 7-day trend graph | Arjun/Priya | 5 | P1 |
| AN-005 | Date picker synced diary and analysis | Priya | 2 | P1 |
| TECH-004 | Performance testing all operations | Arjun | 3 | P0 |
| TECH-006 | Auto-save verification | Arjun/Priya | 2 | P0 |
| TECH-007 | Date timezone handling verification | Arjun | 2 | P0 |

**Total story points committed: 44**

---

**Sprint Goal Success Criteria:**
- Full end-to-end demo clean by March 25
- All PRD performance requirements verified via TECH-004
- Bar graph tested with real users (Ananya to test with 5 users)
  before March 28
- MVP ships March 31 — all P0 and P1 tickets complete

---

**Hard deadline:** March 31 is non-negotiable. Beta invites go
out April 1. Any ticket not completed by March 29 must be scoped
down or deferred, not delayed.

---

## SPRINT 6 RETROSPECTIVE

**Document name:** Sprint 6 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** April 1, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| CF-003 | Yes | Yes | Mar 22 — zero calorie decision made |
| CF-004 | Yes | Yes | Mar 17 |
| CF-005 | Yes | Yes | Mar 19 |
| CF-006 | Yes | Yes | Mar 17 — soft delete + PRD cancel behaviour fixed |
| CF-007 | Yes | Yes | Mar 20 — effective_date versioning |
| AN-001 | Yes | Yes | Mar 19 — carousel swipe navigation |
| AN-002 | Yes | Yes | Mar 28 — emergency redesign 3 days before launch |
| AN-003 | Yes | Yes | Mar 21 — shared color function |
| AN-004 | Yes | Yes | Mar 24 — 0% for skipped days agreed |
| AN-005 | Yes | Yes | Mar 22 |
| TECH-004 | Yes | Yes | Mar 26 — 20 query → 1 query optimisation |
| TECH-006 | Yes | Yes | Mar 24 — offline limitation documented |
| TECH-007 | Yes | Yes | Mar 26 |

Delivery rate: 13 out of 13. 100%.
MVP shipped: March 31, 2025. On time.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
MVP shipped on time. This is a significant achievement for a 5-person
team building a complex health tracking product from scratch in 3
months. However Sprint 6 had the most stressful moment of the
entire project: Ananya's user testing of the analysis bar graph
(AN-002) on March 24 — 7 days before launch — revealed that 4 out
of 5 users completely misread the bar graph. The team spent 2 days
implementing an emergency patch (Option C: explicit numbers) while
preparing for launch simultaneously.

**What went well:**

1. MVP shipped on time. Every ticket completed. No deferred scope.
   This is a testament to the team's execution over 6 sprints.

2. The TECH-004 optimisation — batching 20 sequential analysis
   queries into 1 — was found and fixed before launch. Without
   this the analysis page would have exceeded the 2-second limit
   for users tracking 20 nutrients.

3. The zero calorie decision in CF-003 (allow ≥ 0, not > 0)
   shows the team making correct product decisions under time
   pressure. Black coffee and plain water are zero calorie foods —
   blocking zero was the wrong call regardless of what the PRD said.

**What did not go well:**

1. AN-002 bar graph user confusion discovered 7 days before
   launch. This should have been caught in Sprint 4 or 5
   during design review. Critical visualisations need user
   testing at least 2 sprints before they are needed in
   production, not 1 week before launch.

2. The AN-004 specification was literally incomplete in the PRD
   ("discuss with developer and then write"). This meant Arjun
   and Shristi had to define the spec during implementation.
   Incomplete PRD requirements should be flagged during sprint
   planning, not discovered during implementation.

3. The offline data loss risk (identified in Sprint 5) was only
   addressed in Sprint 6 with a network status indicator.
   Should have been done in Sprint 5 when first identified.

**Key learnings:**

1. Critical visualisations (bar graphs, trend charts) need real
   user testing 2 sprints before the feature ships. Not 1 week.
   This is now a team standard.

2. Incomplete PRD sections must be flagged in sprint planning
   and completed before the sprint begins, not during.

3. Known risks identified in sprint retrospectives must have
   action items with due dates in the NEXT sprint, not "future sprint."

**Decisions made this sprint:**

1. Zero calorie allowed (≥ 0 not > 0) for all nutrient inputs
   in custom food (CF-003). PRD corrected.

2. Bar graph: Option C patch (explicit numbers) for MVP.
   AN-CR-001 created for proper redesign in Sprint 8.

3. 7-day trend: 0% for days with no logs, not null/gap (AN-004).
   Note: this will be incorrectly implemented and become
   AN-BUG-001 in Sprint 9.

4. Analysis: carousel swipe navigation, not URL routing (AN-001).

5. Custom food: soft delete preserves diary history (CF-006).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| AN-CR-001 bar graph full redesign — Sprint 8 | Kabir/Priya | Sprint 8 |
| Shristi to send beta invites April 1 | Shristi | Apr 1 |
| Ananya to prepare beta feedback form | Ananya | Apr 1 |
| Team celebration dinner — MVP shipped | Shristi | Apr 2 |
| Sprint 7 planning — focus entirely on beta bugs | Shristi | Apr 1 |

**Team health:** 5/5 (with exhaustion)
The team is proud but tired. 3 months of intense building.
MVP shipped on time and on quality. The AN-002 scare was stressful
but the team handled it well under pressure. The celebration dinner
is deserved. Sprint 7 will be different — reactive bug fixing
instead of building. Team needs to mentally shift gears.

---

**SHEET 3: METRICS THIS SPRINT**
Pre-launch metrics:
- Features shipped: 5 (food diary, goal setting, custom food,
  analysis, authentication)
- Performance: search 200ms, analysis load 0.8s, diary date
  switch 0.8s, recalculation <200ms
- End-to-end demo: passed clean March 25
- Beta waitlist: 187 users ready for April 1 invites
- Known bugs at launch: 0 P0, 2 P1 (AN-002 patched, GOAL-BUG-004
  will be discovered in Sprint 7)

---

---

# SPRINT 7

## SPRINT 7 PLANNING DOCUMENT

**Document name:** Sprint 7 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** April 1, 2025
**Sprint dates:** April 1 to April 14, 2025
**Sprint goal:** Fix all critical bugs discovered during beta
launch within 14 days. Maintain beta user trust through rapid
response and transparent communication.

---

**Team Capacity:**
- Arjun Mehta: 10 days (bug fixing focus)
- Priya Nair: 10 days (bug fixing focus)
- Kabir Sharma: 10 days (design QA and bug fixes)
- Ananya Iyer: 10 days (managing beta user communication)
- Shristi Sharmistha: 10 days (bug triage, user communication,
  sprint coordination)

---

**Sprint Mode:** REACTIVE. This sprint has no planned feature work.
All capacity is reserved for beta bugs. Tickets will be created
as bugs are reported and triaged in real time. Sprint backlog is
intentionally left open at planning time.

**Bug triage priority:**
- P0: Data integrity, health-critical (BMR/EER errors), data loss
- P1: Core feature broken for majority of users
- P2: Feature degraded but workaround exists
- P3: Minor UX issue, not blocking

**Response SLA for beta users:**
- P0: Acknowledge within 2 hours, fix within 24 hours
- P1: Acknowledge within 4 hours, fix within 48 hours
- P2: Fix within sprint
- P3: Log and defer

---

**Bugs committed at sprint start (known from Sprint 6):**
AN-CR-001 bar graph redesign (P1 — scheduled) and any bugs
reported by beta users from April 1 onwards.

---

## SPRINT 7 RETROSPECTIVE

**Document name:** Sprint 7 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** April 14, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Bug | Priority | Found By | Fixed | Days to Fix |
|---|---|---|---|---|
| NUTR-BUG-001 | P1 | Priya + 3 beta users | Apr 8 | 5 days |
| NUTR-BUG-003 | P2 | Priya | Apr 10 | 6 days |
| NUTR-BUG-004 | P2 | Priya + 5 beta users | Apr 11 | 6 days |
| NUTR-BUG-005 | P1 | Kabir | Apr 9 | 5 days |
| NUTR-BUG-006 | P1 | Beta user BT-047 | Apr 12 | 6 days |
| GOAL-BUG-002 | P1 | Beta user BT-023 | Apr 11 | 6 days |
| GOAL-BUG-003 | P2 | Priya | Apr 12 | 5 days |
| GOAL-BUG-004 | P1 | 4 beta users | Apr 12 | 6 days |
| AN-BUG-002 | P2 | Kabir | Apr 13 | 5 days |
| AN-BUG-003 | P1 | Priya | Apr 8 | 4 days |

All 10 bugs fixed within sprint. 0 P0 bugs this sprint.
No health-critical issues (GOAL-BUG-002 closest but resolved).

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
The first beta sprint was brutal but necessary. 10 bugs in 14 days.
The most important insight: NUTR-BUG-001 and AN-BUG-003 had the
same root cause (FoodDiaryContext not implemented) — architectural
debt from Sprint 4 came back as two P1 bugs simultaneously. The
most alarming bug was GOAL-BUG-004 — micronutrient selections
were never saved to the database. They worked within a session
but reset on every refresh. This was a fundamental implementation
oversight that 4 beta users discovered within 24 hours.

**What went well:**

1. Team response time was excellent. All P1 bugs fixed within
   6 days. Beta users who received direct responses from Shristi
   became advocates — several left positive App Store reviews
   after their bugs were fixed.

2. AN-BUG-003 (analysis not updating after food deletion) was
   fixed as a direct extension of NUTR-BUG-001 — recognising
   shared root causes saved significant time.

3. Ananya's beta user communication was excellent. Personal
   messages to affected users with fix confirmations built
   trust instead of eroding it.

**What did not go well:**

1. GOAL-BUG-004 — micronutrient selections never saved to
   database — is the most embarrassing bug of the project.
   The selections worked in the session because React state
   survived intra-session navigation. Across sessions the
   state was destroyed. This should have been caught by a
   cross-session persistence test before MVP launch.

2. GOAL-BUG-002 (gender change not triggering EER recalculation)
   is a health-critical bug. A female user eating on male calorie
   budget is a product liability issue. This was a PRD requirement
   ("if person changes gender, automatically new EER formula must
   be selected") that was never implemented. PRD requirements
   must be cross-checked against implementation before shipping.

3. The pattern of "fix not applied to related components" appeared
   for the first time this sprint — NUTR-BUG-001 fixed diary
   totals but AN-BUG-003 was the same root cause not fixed
   simultaneously. Arjun caught this in PR review. In future,
   when a root cause is identified, audit ALL components that
   could share that root cause before closing the ticket.

**Key learnings:**

1. Cross-session persistence testing must be part of the definition
   of done for any feature that stores user selections. Log out,
   clear browser, log back in, verify state persists. Non-negotiable.

2. PRD requirements that trigger on profile changes (gender, age,
   activity level) must have explicit test cases for the trigger
   scenario, not just the initial setup scenario.

3. Root cause audits: when a bug is found, ask "what else in the
   codebase uses the same pattern that caused this bug?"

4. Health-critical bugs (anything touching EER formula, BMR,
   calorie calculations) need dedicated regression tests before
   each release.

**Decisions made this sprint:**

1. FoodDiaryContext implemented as the shared state solution
   for all diary components (NUTR-BUG-001).

2. "Apply fix to all related components" becomes a standard
   PR review checklist item.

3. Cross-session persistence test added to definition of done
   for all features with user selections.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Add cross-session persistence test to DoD checklist | Shristi | Apr 15 |
| PR review checklist: always ask "what other components share this root cause" | Arjun | Apr 15 |
| Regression test suite for all EER and BMR calculations | Arjun | Apr 28 |
| Ananya to compile beta user feedback themes by Apr 20 | Ananya | Apr 20 |
| Shristi to triage remaining known issues for Sprint 8 | Shristi | Apr 15 |

**Team health:** 3/5
Tired. Bug fixing is demoralising after 6 sprints of building.
The team knew bugs were coming but 10 in 14 days was more than
expected. Three things maintain morale: (1) beta users are
responding well to the rapid fixes, (2) no P0 bugs, (3) the
underlying product is solid — these are implementation bugs,
not architectural failures. Sprint 8 should see the bug count
decline significantly.

---

**SHEET 3: METRICS THIS SPRINT**

Beta metrics (April 1-14):
- Beta users active: 200
- Bugs reported by users: 6 (NUTR-BUG-001, 004, 006, GOAL-BUG-002, 004, and one false positive)
- Bugs found internally: 4 (NUTR-BUG-003, 005, GOAL-BUG-003, AN-BUG-003)
- Day 7 retention (first cohort): 34%
- Average daily food logs per user: 2.3 meals
- Custom foods created: 23 (all Indian foods — chapati, dal, paneer top 3)
- User NPS informal: too early for formal survey
- App Store early reviews: 3.8 average from 12 reviews

---

---

# SPRINT 8

## SPRINT 8 PLANNING DOCUMENT

**Document name:** Sprint 8 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** April 15, 2025
**Sprint dates:** April 15 to April 28, 2025
**Sprint goal:** Fix all remaining beta bugs, complete the bar
graph redesign, and reach product stability for public launch
on May 1. Zero P1 bugs in production by April 28.

---

**Team Capacity:**
- Arjun Mehta: 10 days
- Priya Nair: 10 days
- Kabir Sharma: 10 days (bar graph redesign priority)
- Ananya Iyer: 10 days (user testing for bar graph redesign,
  App Store listing preparation)
- Shristi Sharmistha: 10 days

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| NUTR-BUG-002 | Duplicate warning not showing for custom food | Priya | 3 | P2 |
| NUTR-BUG-007 | Custom meal nutrients not matching creation | Arjun/Priya | 5 | P1 |
| NUTR-BUG-008 | Search not clearing on source change | Priya | 3 | P2 |
| NUTR-BUG-009 | DV% showing decimal instead of dash | Priya | 3 | P2 |
| NUTR-BUG-010 | Per-meal total appearing after wrong food | Priya | 3 | P2 |
| GOAL-BUG-001 | Target date not updating on calorie change | Arjun | 3 | P2 |
| GOAL-BUG-005 | BMR warning shown but goal saved incorrectly | Arjun | 5 | P1 |
| CF-BUG-003 | Calorie not marked mandatory in create form | Kabir/Priya | 1 | P2 |
| CF-BUG-004 | Add button not appearing after save | Priya | 2 | P2 |
| AN-CR-001 | Bar graph full redesign | Kabir/Priya/Ananya | 8 | P1 |
| AN-CR-002 | Add remaining vs over label | Kabir/Priya | 2 | P2 |

**Total story points committed: 38**

---

**Sprint Goal Success Criteria:**
- Zero P1 bugs in production by April 28
- Bar graph redesign tested with 8 users — all 8 understand
  it without explanation
- Product stable enough for public launch May 1
- GOAL-BUG-005 (BMR health-critical) has tests written before
  fix implemented

---

## SPRINT 8 RETROSPECTIVE

**Document name:** Sprint 8 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** April 28, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| NUTR-BUG-002 | Yes | Yes | Apr 20 — source-type aware duplicate check |
| NUTR-BUG-007 | Yes | Yes | Apr 22 — frozen snapshot approach |
| NUTR-BUG-008 | Yes | Yes | Apr 21 — synchronous clear on source change |
| NUTR-BUG-009 | Yes | Yes | Apr 20 — two bugs found, both fixed |
| NUTR-BUG-010 | Yes | Yes | Apr 22 — in-place array update + alphabetical sort |
| GOAL-BUG-001 | Yes | Yes | Apr 21 — full cascade function refactor |
| GOAL-BUG-005 | Yes | Yes | Apr 22 — tests first, then fix |
| CF-BUG-003 | Yes | Yes | Apr 21 — is_mandatory flag in renderer |
| CF-BUG-004 | Yes | Yes | Apr 21 — ID extraction from API response |
| AN-CR-001 | Yes | Yes | Apr 26 — progress bar with thermometer overflow |
| AN-CR-002 | Yes | Yes | Apr 24 — remaining/over target copy |

Delivery rate: 11 out of 11. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 8 was the stabilisation sprint. All 11 tickets delivered.
By April 28 there are zero P1 bugs in production. The product is
ready for public launch on May 1. Three moments stand out:
(1) Shristi identified the "fix not applied to related components"
pattern for the third time (NUTR-BUG-008) and requested a
codebase audit — a systematic response that prevented future
bugs. (2) GOAL-BUG-005 became the first ticket where tests were
written before the fix was implemented — a new team standard for
health-critical features. (3) The AN-CR-001 bar graph redesign
went through real user testing and emerged significantly better
than the original design.

**What went well:**

1. The codebase audit triggered by Shristi (NUTR-BUG-008)
   found and fixed 2 additional instances of the same pattern
   proactively. This is mature engineering practice — fix the
   root cause, not just the symptom.

2. Tests-first for GOAL-BUG-005 (BMR regression) is the right
   approach for health-critical features. Writing the tests
   first revealed the full scope of the regression before
   the fix was attempted.

3. AN-CR-001 progress bar design is genuinely better than
   what the PRD specified. Real user testing (Ananya, 8 users)
   informed the design. The thermometer overflow metaphor
   (full green bar + red extension for over-target) elegantly
   shows both achievement and excess simultaneously.

4. CF-BUG-004 fix using Masala Oats as the test case was
   a genuine product moment — custom food feature now works
   for the Indian food gap that motivated its creation.

**What did not go well:**

1. The "fix not applied to related components" pattern appeared
   for the third time this sprint. Despite identifying it in
   Sprint 7 and adding it to the PR review checklist, it
   still happened. The root cause is two separate functions
   implementing the same logic. The fix is shared utility
   functions — not better checklists.

2. NUTR-BUG-009 revealed a USDA data normalisation issue
   (23 micronutrients with reversed column order in the import)
   that was in the data since Sprint 2 but not caught until
   beta testing. Data quality validation on external data
   sources needs to be systematic, not ad hoc.

**Key learnings:**

1. Checklists do not prevent duplicate-function bugs.
   Shared utility functions do. Every repeated logic pattern
   must be a shared function.

2. External data quality issues (USDA column order) are
   only found by testing edge cases with real data. More
   edge case coverage needed for external data sources.

3. Tests-first for health-critical features is now a
   non-negotiable team standard.

**Decisions made this sprint:**

1. Tests-first for all health-critical features (GOAL-BUG-005).
2. Codebase audit as standard response when a pattern is
   found more than twice (NUTR-BUG-008).
3. Custom meal values frozen at creation time snapshot,
   not live-calculated (NUTR-BUG-007).
4. Progress bar design with thermometer overflow for over-target
   (AN-CR-001). Replaces original bar = target metaphor.
5. Remaining/over target as standard label copy across
   diary and analysis (AN-CR-002).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Create shared formatNutrient utility function | Priya/Arjun | Sprint 9 |
| Create shared color utility function | Priya/Arjun | Sprint 9 |
| USDA data quality audit — all 40+ micronutrient columns | Arjun | Sprint 9 |
| Shristi to draft public launch announcement email | Shristi | Apr 29 |
| Ananya to prepare launch day social media posts | Ananya | Apr 30 |

**Team health:** 4/5
Tired but proud. The product is genuinely ready for public launch.
Bug count has dropped significantly from Sprint 7 (10 bugs) to
Sprint 8 (11 but mostly P2). The bar graph redesign energised
the team — shipping a real improvement based on user feedback
is more satisfying than bug fixing.

---

**SHEET 3: METRICS THIS SPRINT**

Beta metrics (April 15-28):
- Beta DAU: 67 (out of 200 users — 33.5% daily active)
- Day 7 retention improvement: 34% → 41% (driven by bug fixes)
- Custom foods created: 47 (up from 23 at Sprint 7 end)
- App Store rating: 3.8 → 4.0 (after bug fixes and AN-CR-001)
- Beta user NPS informal survey (Ananya): estimated 28-32
- Bug reports from users this sprint: 3 (all P2, all fixed)

---

---

# SPRINT 9

## SPRINT 9 PLANNING DOCUMENT

**Document name:** Sprint 9 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** April 29, 2025
**Sprint dates:** April 29 to May 12, 2025
**Sprint goal:** Fix all pre-launch critical bugs, verify data
security for public launch, and successfully launch Nutrivana
to the public on May 1. Achieve stable product with zero P0
bugs by May 5.

---

**Team Capacity:**
- Arjun Mehta: 10 days
- Priya Nair: 10 days
- Kabir Sharma: 8 days (launch visuals April 30-May 2)
- Ananya Iyer: 10 days (launch campaign full focus May 1-5)
- Shristi Sharmistha: 10 days

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| CF-BUG-001 | Custom food edits reflecting in all dates | Arjun/Priya | 8 | P1 |
| CF-BUG-002 | Deleted custom food in past diary entries | Arjun | 5 | P2 |
| AN-BUG-001 | 7-day trend missing days with no logs | Arjun/Priya | 5 | P0 |
| AN-BUG-004 | Wrong color weight maintain in analysis | Arjun/Priya | 3 | P1 |
| AN-BUG-005 | DV% rounding in analysis | Priya/Arjun | 3 | P2 |
| TECH-005 | Data isolation testing | Arjun | 3 | P0 |
| CF-EPIC-001 | Close Custom Food epic | Shristi | 1 | P0 |

**Total story points committed: 28**

---

**Launch day plan (May 1):**
- 9:00 AM: App Store listing goes live
- 10:00 AM: Instagram launch post (Ananya)
- 10:30 AM: Email to beta users announcing public launch
- 11:00 AM: Nutritionist partners post (Dr. Priya Nambiar)
- 12:00 PM: Team monitors for P0 bugs (all hands)
- 6:00 PM: First day metrics review call

**Launch P0 criteria:** If AN-BUG-001 is not fixed by April 30,
public launch may be delayed. 12 beta user reports make this
the highest-risk launch blocker.

---

## SPRINT 9 RETROSPECTIVE

**Document name:** Sprint 9 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** May 12, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| CF-BUG-001 | Yes | Yes | May 7 — one-line fix, massive impact |
| CF-BUG-002 | Yes | Yes | May 6 — snapshot approach, migration needed |
| AN-BUG-001 | Yes | Yes | May 8 — zero fill in application code |
| AN-BUG-004 | Yes | Yes | May 6 — shared color function created |
| AN-BUG-005 | Yes | Yes | May 5 — formatNutrient shared utility |
| TECH-005 | Yes | Yes | May 5 — all isolation tests pass |
| CF-EPIC-001 | Yes | Yes | May 10 — 47 Indian foods at beta, 847 target by June |

Delivery rate: 7 out of 7. 100%.
Public launch: May 1, 2025. On time.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 9 marked the end of the build and stabilisation phase.
Public launch happened on May 1 as planned. AN-BUG-001 was the
most critical pre-launch bug — 12 reports in 3 days, fixed by
May 8. The most satisfying moment was closing CF-EPIC-001 —
beta users had already created 47 custom Indian food entries
(chapati, dal, paneer leading). The Indian food gap first
discovered in Sprint 2 is now being solved by real users.

**What went well:**

1. AN-BUG-004 and AN-BUG-005 each triggered a shared utility
   function (shared color function, formatNutrient function).
   The "fix the root cause, not the symptom" approach from
   Sprint 8 retrospective action items was implemented.
   This sprint created the most maintainable codebase state
   of the entire project.

2. CF-BUG-001 one-line fix (NOW() → $diary_date) with massive
   impact shows the value of careful SQL query review. The old
   custom food versions were preserved — the versioning system
   worked. Only the query had the wrong parameter.

3. TECH-005 security analysis was thorough and proactive —
   Arjun identified a theoretical vulnerability in the
   CF-BUG-002 snapshot approach and confirmed it was not
   exploitable. Appropriate security thinking for a health
   data application.

4. The public launch went smoothly. Ananya's coordinated
   campaign (App Store + Instagram + nutritionist partners)
   drove strong Day 1 installs.

**What did not go well:**

1. AN-BUG-001 (7-day trend missing skipped days) was P0 at
   launch with 12 reports in 3 days. This was specified
   correctly in AN-004 ("0% for days with no logs") but
   not implemented. The implementation gap between
   specification and code is the recurring theme of our
   bug patterns.

2. CF-BUG-001 retroactively changed historical data for
   8 beta users without their knowledge. This is the
   most serious data integrity failure of the project.
   The NOW() vs $diary_date distinction is subtle but
   consequential. Date-parameterised queries must be
   reviewed with the specific question: "does this query
   use the right date for the historical context it serves?"

**Key learnings:**

1. The biggest source of bugs in Nutrivana is the gap between
   specification and implementation. The code does something
   slightly different from what was specified. The fix:
   test cases that mirror the specification exactly, run
   before merging.

2. Date-parameterised queries (anything querying historical
   data) must always be reviewed with the question:
   "am I using the date of the data being viewed or today's
   date?" NOW() should almost never appear in a query that
   serves historical data.

3. Shared utility functions (color, formatNutrient) are the
   right solution to the duplicate-function bug class.
   By end of Sprint 9 the codebase has 3 shared utilities
   that prevent entire categories of future bugs.

**Decisions made this sprint:**

1. Shared color utility function — single source of truth
   for all nutrient color logic (AN-BUG-004).

2. Shared formatNutrient utility — single source of truth
   for all numeric nutrient display rounding (AN-BUG-005).

3. Nutrient snapshot in food_logs — all diary entries store
   nutrient values at logging time. Past data is immutable
   even if food definitions change (CF-BUG-002).

4. Zero-fill for skipped days in 7-day trend — always return
   exactly 7 data points (AN-BUG-001).

**Action items:**

| Action | Owner | Due |
|---|---|---|
| One-time migration to backfill food_log nutrient snapshots | Arjun | May 20 |
| Date-parameterised query review — all historical queries | Arjun | May 20 |
| Specification-to-implementation test pairing process | Shristi | May 15 |
| Shristi to begin user research with beta users | Shristi | May 15 |
| Ananya to launch NPS survey May 20 | Ananya | May 20 |
| Team retrospective on full Jan-May journey | All | May 12 |

**Team health:** 4/5
Public launch is a genuine achievement. The team built a complex
health product from scratch in 4 months. 89 Jira tickets across
9 sprints. The journey from Sprint 1 (database schema) to Sprint 9
(public launch) required 486 individual conversations and decisions.
Every team member grew significantly. Arjun became a more systematic
engineer. Priya became a confident frontend owner. Kabir learned
to validate designs with users before assuming they work. Ananya
became the bridge between users and product. Sprint 10 onwards
is a different mode — growth, retention, and V2 planning.

---

**SHEET 3: METRICS THIS SPRINT (LAUNCH WEEK)**

Launch metrics (May 1-12):
- Day 1 installs: 312
- Week 1 MAU: 847
- Day 7 retention (May cohort, early read): 43%
- App Store rating: 4.1 (May 12)
- Custom foods created since launch: 203 (total including beta: 847 on track)
- AN-BUG-001 reports resolved: 12 users notified
- Launch NPS: too early
- Ananya Instagram followers: 287 (from 0 at launch)

---

## SUMMARY OF ALL SPRINT DOCUMENTS

| Sprint | Planning Date | Retro Date | Tickets | Delivery Rate | Key Milestone |
|---|---|---|---|---|---|
| Sprint 1 | Jan 1 | Jan 14 | 8 | 100% | Foundation complete |
| Sprint 2 | Jan 15 | Jan 28 | 6 | 100% | USDA integrated, Indian food gap found |
| Sprint 3 | Jan 29 | Feb 11 | 10 | 100% | Goal setting complete |
| Sprint 4 | Feb 12 | Feb 25 | 9 | 100% | Food diary demoable |
| Sprint 5 | Feb 26 | Mar 11 | 14 | 100% | Food diary complete |
| Sprint 6 | Mar 12 | Apr 1 | 13 | 100% | MVP shipped Mar 31 |
| Sprint 7 | Apr 1 | Apr 14 | 10 | 100% | Beta bugs fixed |
| Sprint 8 | Apr 15 | Apr 28 | 11 | 100% | Product stable |
| Sprint 9 | Apr 29 | May 12 | 7 | 100% | Public launch May 1 |

---

## GPT-4o GENERATION INSTRUCTIONS FOR ALL SPRINT DOCUMENTS

**For Sprint Planning documents (Word):**
Generate professional sprint planning documents that look like
real agile sprint planning artifacts. Each document should have:
- A header with company name, sprint number, dates
- Sprint goal in bold as the first section
- Team capacity table
- Sprint backlog table with story points
- Success criteria as bullet points
- Dependencies and risks as separate sections
- Definition of done

Tone: Practical, direct, action-oriented. Written by a PM who
runs lean agile sprints. Not corporate — startup velocity.

**For Sprint Retrospective documents (Excel):**
Each retrospective has 3 sheets:
- Sheet 1: Sprint Summary — delivery table, metrics
- Sheet 2: Retrospective Narrative — Format B with all sections
- Sheet 3: Sprint Metrics — quantitative data for this sprint

Tone for retrospective narratives: Honest and reflective.
The what-went-well sections celebrate real wins. The what-did-not-
go-well sections name problems directly without blame. The key
learnings sections are actionable. The team health rating is
genuine — not always 5/5.

**Critical accuracy requirements:**
All ticket numbers, dates, and team member names must match
exactly with the sprint ticket definitions in sprint1 through
sprint9 definition files. Every cross-reference to a specific
ticket (e.g. "NUTR-BUG-001 and AN-BUG-003 share the same root
cause") must match the conversation blueprint in the ticket
definition files.

The metrics in Sheet 3 must be consistent with:
- Weekly metrics sheets (separate document)
- OKR Q1 and Q2 review sections
- NPS survey documents
- Retention cohort sheets
All numbers are locked in the OKR document definitions file


Meeting note sprint 1-9

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