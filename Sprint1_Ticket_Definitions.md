# Sprint 1 Ticket Definitions — Complete Brief for GPT-4o
## January 1 to January 14, 2025

---

## GLOBAL CONTEXT — Include in every API call

### Product
Nutrivana is a nutrition tracking web app. Users log food from the USDA database, set
calorie and macro/micro nutrient goals using the EER formula, and analyse their intake
through bar graphs and 7-day trend charts. The app targets health-conscious individuals,
fitness enthusiasts, pregnant women, biohackers, and weight watchers.

### Technical Stack
- Frontend: React (web app)
- Backend: Node.js / Python API
- Database: Supabase (PostgreSQL)
- Food data: USDA food database

### Team Profiles
- **Shristi Sharmistha** (shristi@nutrivana.in) — CEO and PM. Focused on user
  experience and PRD compliance. Direct, decisive, raises product concerns immediately.
  Always verifies on staging before closing tickets.

- **Arjun Mehta** (arjun@nutrivana.in) — CTO and Lead Engineer. Methodical, raises
  technical complexity early, proposes architecture solutions, thinks about performance
  and scalability. Reviews all PRs before merge.

- **Priya Nair** (priya@nutrivana.in) — Frontend Engineer. Practical and solution
  focused. Finds most UI bugs during implementation. Pairs with Arjun on complex issues.

- **Kabir Sharma** (kabir@nutrivana.in) — UI/UX Designer. Design-first thinking, raises
  discoverability and usability concerns. Shares Figma links in comments.

- **Ananya Iyer** (ananya@nutrivana.in) — Marketing Manager. Brings beta user feedback,
  thinks about feature discoverability and first-time user experience.

### Comment Style Rules
- Every comment starts with: **Person Name — Date, Time**
  Example: `Arjun Mehta — January 3, 2025, 10:14 AM`
- Comments must be written in natural conversational tone — not formal reports
- Technical comments must use specific Nutrivana terminology — EER, DV%, food diary,
  USDA, macro/micro etc. Never generic terms like "the system" or "the app"
- Each person sounds different:
  - Shristi: decisive, product-focused, references PRD requirements directly
  - Arjun: technical depth, raises architecture concerns, mentions specific technologies
  - Priya: practical, implementation-focused, mentions specific React components
  - Kabir: design-focused, references Figma, user experience first
  - Ananya: user-focused, brings real user feedback, marketing perspective
- Final comment always closes the ticket with a status update

---

## SPRINT 1 TICKETS

---

### Ticket 1: TECH-001
**Title:** Database schema design for users, food logs, goals and nutrients
**Tier:** 2 (4 comments)
**Type:** Technical task
**Sprint:** 1
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 2, 2025
**Resolved:** January 8, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Food diary must maintain a separate log for each calendar date
- Only the current user's logged items should be displayed (data isolation)
- Nutrient values must use standardised units — kcal, g, mg, µg
- The system must store user profile variables: age, height, current weight, sex, goal
  weight, target date, activity level
- EER formula depends on age, gender, activity level — these must be stored per user
- Macro goals stored as percentage AND gram AND kcal equivalents
- Micronutrient goals stored with RDA and MAX values per age and gender
- Custom food linked to specific user — not accessible by other users

**Conversation Blueprint:**
1. Arjun creates ticket and shares initial schema design covering users, food_logs,
   goals, and nutrients tables
2. Shristi reviews schema and raises concern — the PRD requires data isolation between
   users. Asks how RLS (Row Level Security) will be enforced in Supabase
3. Arjun explains Supabase RLS policies — every table will have user_id foreign key
   with RLS policy enforcing user can only read/write their own rows
4. Shristi approves schema with RLS approach. Asks Arjun to also account for the
   date-stamped diary requirement — each food log needs exact date

**Unique Detail:** Supabase RLS policy design for user data isolation. Schema must handle
date-stamped food logs, EER formula variables per user, macro goals in three formats
(%, kcal, gram), and micronutrient RDA/MAX values by age and gender.

**Cross References:** Referenced in NUTR-TASK-003 (diary data model), TECH-005
(data isolation testing)

---

### Ticket 2: TECH-003
**Title:** Authentication and user session management
**Tier:** 1 (8 comments)
**Type:** Technical task
**Sprint:** 1
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 3, 2025
**Resolved:** January 10, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Once the nutrient is set, same nutrient remains in the diary even if the user logs
  off, refreshes the page or moves to some other page
- Food diary data must persist across logout and re-login
- The food once saved can only be accessed by the logged-in user who created it
- Even if user goes back or to some other page, refreshes or re-logs in, the same value
  should be present
- Macro goal: system should automatically save macros as user inputs the value
- If user is below 18 years for either gender then no goal should be allowed to be set

**Conversation Blueprint:**
1. Arjun creates ticket — proposes basic JWT authentication with 24-hour token expiry
2. Shristi raises PRD conflict — the PRD explicitly says food diary data must persist
   even if the user logs off and logs back in. If JWT expires after 24 hours and user
   logs in again, will their food diary data still be there? Asks Arjun to clarify.
3. Arjun explains — JWT expiry is about the authentication token, not the data. Data
   is stored in Supabase database permanently. The issue is the SESSION — if JWT expires
   mid-session the user gets logged out and loses unsaved state. Proposes refresh token
   strategy with 7-day refresh token.
4. Shristi asks — what happens to a user who opens the app after 7 days without logging
   in? Will they lose their session and have to re-login?
5. Arjun explains tradeoff — security requires short expiry, UX requires long sessions.
   Proposes: access token 1 hour expiry, refresh token 30-day expiry, silent refresh
   in background. User only sees login screen if they have not opened the app in 30 days.
6. Shristi approves the 30-day refresh token approach. Adds requirement — user must
   never be logged out mid-session. Silent refresh must work without any interruption.
7. Arjun implements JWT + refresh token with Supabase Auth. Updates schema with
   refresh_tokens table. Tests silent refresh works on token expiry.
8. Shristi verifies — tested logging in, waiting, coming back. Session persists. Food
   diary data intact after re-login. Closing ticket.

**Unique Detail:** JWT access token (1 hour) + refresh token (30 days) strategy.
Silent refresh in background. Debate about security vs UX tradeoff. Supabase Auth
implementation. PRD requirement that data persists across logout is the trigger.

**Cross References:** Referenced in TECH-001 (database schema), TECH-005 (data
isolation testing)

---

### Ticket 3: NUTR-TASK-003
**Title:** Date-stamped diary data model design
**Tier:** 1 (8 comments)
**Type:** Technical task
**Sprint:** 1
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 4, 2025
**Resolved:** January 11, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- The food diary must maintain a separate log for each calendar date
- When a previous date is selected — if FD is not filled, an empty food diary with all
  target nutrients as columns must be displayed
- When a future date is selected — if FD is not filled, an empty food diary with all
  target nutrients as columns must be displayed
- Switching between dates must load the corresponding food diary within 2 seconds
- Logged food items must be associated with the exact date and meal section when saved
- User can log meal for past, current, and future dates
- The food diary must calculate cumulative total for each target nutrient for the
  selected date

**Conversation Blueprint:**
1. Arjun shares initial data model — one food_logs table with columns: id, user_id,
   food_id, meal_type, portion_size, date, created_at. Simple and clean.
2. Shristi reads the PRD requirement carefully and raises a problem — the PRD says an
   empty food diary with all target nutrient columns must show for any date, even dates
   with no logs. How does the model handle showing an empty diary for January 15 if the
   user has never logged anything on that date? There are no rows in food_logs for that
   date. How will the frontend know what columns to show?
3. Arjun realises the gap — his schema only stores rows when food is logged. An empty
   date has no rows. The empty diary structure (which columns to show, which nutrients
   are tracked) is determined by the user's goal settings, not by the food_logs table.
   The frontend cannot derive empty diary structure from an empty food_logs query.
4. Arjun proposes two solutions — Option A: create a diary_dates table that records
   every date the user has visited the diary, even if empty. Option B: compute the empty
   diary on the fly — frontend fetches user's goal settings and builds the empty
   structure dynamically without any food_logs rows needed.
5. Shristi asks — Option B sounds simpler but is it reliable? What if goal settings
   change mid-day? The PRD says if a user adds a new nutrient goal on April 24, the new
   goal must reflect from April 24 onwards. Past diary entries must not change.
6. Arjun explains — Option B handles this correctly because each diary view fetches the
   goal settings that were active on THAT date, not today's settings. This requires
   storing goal_history with effective_date. More complex but correct.
7. Arjun proposes final design — food_logs table for actual logged items + goal_snapshots
   table storing a snapshot of user goals with effective_date. Diary for any date fetches
   goal_snapshot for that date to build column structure, then fetches food_logs for that
   date to populate rows. Empty dates show columns from goal_snapshot with no rows.
8. Shristi approves the goal_snapshots approach. Notes this also solves future PRD
   requirement about goal changes not affecting past diary entries. Closing ticket.

**Unique Detail:** The core problem is representing an empty food diary in the database.
The solution is goal_snapshots table with effective_date. This is a non-obvious
architectural decision that Shristi triggers by reading the PRD carefully. The debate
between Option A (diary_dates table) and Option B (compute on the fly with
goal_snapshots) is the heart of this ticket.

**Cross References:** Referenced in NUTR-BUG-006 (future date diary showing wrong data),
GOAL-BUG-004 (micro goals disappearing after page refresh), TECH-001 (database schema)

---

### Ticket 4: GOAL-SPIKE-001
**Title:** Research all EER formulas by age group gender and activity level
**Tier:** 3 (2 comments)
**Type:** Spike
**Sprint:** 1
**Priority:** P1
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 2, 2025
**Resolved:** January 7, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- EER formula is different for people with different age group having different gender
  and different activity level
- Example EER formula for female age 19+ with low physical activity:
  EER = –297.54 – (22.25 × age) + (12.77 × height) + (14.73 × current weight) + 20
- Example EER formula for female age 19+ sedentary:
  EER = 55.59 – (22.25 × age) + (8.43 × height) + (17.07 × current weight) + 20
- Activity level selection through popup — only one level can be selected
- If a person changes gender or activity level then automatically new formula of EER
  must be selected depending on the category

**Conversation Blueprint:**
1. Arjun completes EER formula research — documents all 15+ formula variants categorised
   by gender (male/female), age group (children, adolescent, adult 19+, older adult),
   and activity level (sedentary, low active, active, very active). Notes discrepancy —
   PRD mentions 5 activity levels but USDA EER documentation uses 4. Shares full formula
   table as attachment. Asks Shristi to confirm which activity level mapping to use.
2. Shristi reviews formula table — decides to use USDA's 4 activity levels (sedentary,
   low active, active, very active) and map PRD's 5th level into the closest USDA
   category. Approves formula table. Asks Arjun to start GOAL-001 implementation using
   this research.

**Unique Detail:** 15+ EER formula variants. Discrepancy between PRD activity levels
(5) and USDA EER documentation (4). Shristi must make a product decision on mapping.

**Cross References:** Directly referenced in GOAL-001 (set calorie goal with EER
calculation), GOAL-002 (EER formula implementation), GOAL-BUG-002 (EER formula not
switching on gender change)

---

### Ticket 5: GOAL-SPIKE-002
**Title:** Research RDA and MAX values for all micronutrients by age and gender
**Tier:** 3 (2 comments)
**Type:** Spike
**Sprint:** 1
**Priority:** P1
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 2, 2025
**Resolved:** January 9, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- RDA and MAX value should be as per age and gender
- Example: RDA of vitamin A for male 31-50 age is 900 microgram/day while for women
  31-50 is 700 microgram/day
- Micronutrient detail should be displayed only after the calorie budget is set by user
- All micronutrients will be placed in different buckets — vitamins, minerals,
  carbohydrates etc.

**Conversation Blueprint:**
1. Arjun completes micronutrient RDA/MAX research from USDA and NIH databases —
   documents RDA and MAX values for all tracked nutrients categorised by age group and
   gender. Notes that some nutrients (like vitamin K) have AI (Adequate Intake) values
   instead of formal RDA. Shares complete reference table. Asks Shristi if AI values
   should be treated as RDA for display purposes.
2. Shristi approves treating AI as RDA for display — users do not need to know the
   distinction. Confirms research is sufficient to start GOAL-012 implementation.
   Closing ticket.

**Unique Detail:** Distinction between RDA (Recommended Dietary Allowance) and AI
(Adequate Intake) values for some nutrients like vitamin K. Shristi makes product
decision to treat AI as RDA for simplicity.

**Cross References:** Directly referenced in GOAL-009 (view micronutrient list),
GOAL-010 (select micronutrients to track), GOAL-011 (edit custom micronutrient
goal values), GOAL-012 (RDA values by age and gender)

---

### Ticket 6: NUTR-EPIC-001
**Title:** Epic: Food Diary Core
**Tier:** 3 (2 comments)
**Type:** Epic
**Sprint:** 1
**Priority:** P0
**Status:** In Progress (open throughout development)
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 1, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- Food diary is the core feature of Nutrivana
- Allows users to record all food, recipes and supplements across different meals
- Provides foundation for calculating actual nutrient intake vs user-defined goals
- Covers: food logging, goal comparison, meal breakdown, cumulative totals,
  date-wise diary, edit/delete

**Conversation Blueprint:**
1. Shristi creates epic — defines scope covering all food diary user stories from PRD.
   Lists child tickets: NUTR-005 through NUTR-026 plus NUTR-TASK-001 through
   NUTR-TASK-004. Sets priority P0 as food diary is the core differentiator.
2. Arjun confirms scope is feasible within Sprint 3 to Sprint 5 timeline. Notes
   dependency — food diary cannot be built before USDA database integration (NUTR-TASK-001)
   and goal setting (GOAL-001 to GOAL-012) are complete. Confirms this epic starts
   Sprint 3 after goal setting is done.

**Unique Detail:** Dependency mapping — food diary epics cannot start until USDA
integration and goal setting are complete. This drives the sprint ordering decision.

**Cross References:** Parent of NUTR-005 through NUTR-026, NUTR-TASK-001 through
NUTR-TASK-004

---

### Ticket 7: GOAL-EPIC-001
**Title:** Epic: Calorie Goal Setting
**Tier:** 3 (2 comments)
**Type:** Epic
**Sprint:** 1
**Priority:** P0
**Status:** In Progress
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 1, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- After account setup user can set calorie goal in Nutrivana
- Getting calorie calculated is compulsory — only then user will be allowed to use
  food diary
- Variables: target calorie, age, height, current weight, sex, goal weight, target date,
  activity level
- EER method used for weight maintenance calorie calculation
- BMR validation — error shown if calorie budget below BMR

**Conversation Blueprint:**
1. Shristi creates epic — defines scope covering GOAL-001 through GOAL-004 plus
   GOAL-SPIKE-001. Notes critical dependency — food diary cannot be used without calorie
   goal being set first. This makes calorie goal setting the highest priority epic.
2. Arjun confirms scope. Flags that GOAL-SPIKE-001 must complete before GOAL-001 and
   GOAL-002 can start — EER formula research is the prerequisite. Confirms both spikes
   start in Sprint 1 before any implementation begins.

**Unique Detail:** Calorie goal is a gate for the entire food diary. No other feature
can be properly tested without this. GOAL-SPIKE-001 is a hard prerequisite.

**Cross References:** Parent of GOAL-001 through GOAL-004. Prerequisite for
NUTR-EPIC-001 (food diary)

---

### Ticket 8: GOAL-EPIC-002
**Title:** Epic: Macro and Micro Goal Setting
**Tier:** 3 (2 comments)
**Type:** Epic
**Sprint:** 1
**Priority:** P1
**Status:** In Progress
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 1, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- Macro goal comprises carb, fat and protein as % of target calorie
- Macros measured in both kcal and grams
- Default distribution 40:30:30
- Total macro % must equal exactly 100%
- Micronutrient goals per age and gender using RDA values
- User can select/deselect up to 20 nutrients to track at a time
- Micronutrient list organised into category buckets — vitamins, minerals,
  carbohydrates, fats

**Conversation Blueprint:**
1. Shristi creates epic — defines scope covering GOAL-005 through GOAL-012 plus
   GOAL-SPIKE-002. Notes macro goal depends on calorie goal being set first. Micro goal
   depends on RDA research from GOAL-SPIKE-002 completing first.
2. Arjun confirms scope and dependency chain — GOAL-SPIKE-002 in Sprint 1, macro goal
   stories in Sprint 3 after calorie goal is done, micro goal stories in Sprint 3
   alongside macro. Notes 20 nutrient limit in food diary columns will need careful UI
   work from Kabir.

**Unique Detail:** 20 nutrient maximum tracked at once. This drives UI complexity
for both goal setting and food diary display. Kabir needs to be involved early.

**Cross References:** Parent of GOAL-005 through GOAL-012. Depends on GOAL-EPIC-001
(calorie goal) completing first.

---

## SUMMARY OF SPRINT 1

| Ticket | Tier | Comments | Status |
|---|---|---|---|
| TECH-001 | T2 | 4 | Closed Jan 8 |
| TECH-003 | T1 | 8 | Closed Jan 10 |
| NUTR-TASK-003 | T1 | 8 | Closed Jan 11 |
| GOAL-SPIKE-001 | T3 | 2 | Closed Jan 7 |
| GOAL-SPIKE-002 | T3 | 2 | Closed Jan 9 |
| NUTR-EPIC-001 | T3 | 2 | In Progress |
| GOAL-EPIC-001 | T3 | 2 | In Progress |
| GOAL-EPIC-002 | T3 | 2 | In Progress |

**Total comments Sprint 1: 30**

---

## GPT-4o GENERATION INSTRUCTIONS

When generating comments for each ticket:

1. Use the exact dates specified in each ticket definition
2. Use the exact email addresses for each person
3. Follow the conversation blueprint in exact order
4. Make technical details specific to Nutrivana — mention EER formula, USDA database,
   Supabase RLS, React components, food diary columns, DV%, macros/micros
5. Each person's voice must be distinct — see Team Profiles above
6. For Tier 1 tickets — 8 comments, rich technical debate, unexpected problem drives
   unique conversation
7. For Tier 2 tickets — 4 comments, clean implementation flow, one clarifying question
8. For Tier 3 tickets — 2 comments, simple acknowledgement and completion
9. Reference the PRD requirement text when characters quote requirements
10. Cross references must be mentioned naturally in conversation where indicated