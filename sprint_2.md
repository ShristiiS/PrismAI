sprint 2:

# Sprint 2 Ticket Definitions — Complete Brief for GPT-4o
## January 15 to January 28, 2025

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions — same product description,
same team profiles, same comment style rules. Do not repeat them here but apply them
to every comment generated.

---

## SPRINT 2 TICKETS

---

### Ticket 1: NUTR-TASK-001
**Title:** USDA database integration and API setup
**Tier:** 1 (8 comments)
**Type:** Technical task
**Sprint:** 2
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 15, 2025
**Resolved:** January 24, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- The user must be able to select the Food Database as a source when adding a food item
- Search results must be displayed within 1 second of user input
- The system must support fuzzy or partial matching to accommodate spelling errors or
  variations (e.g., "chiken" should suggest "chicken")
- The food database should instantly appear as the user adds food in food diary
- As the user selects a food source from food database they should be redirected to
  adjust portion page instantly
- All nutrients related to food or recipe should be displayed in nutrient breakdown
- Default unit associated with nutrient should be displayed
- The DV% should be calculated in terms of 2000 calorie diet
- Nutrient data: Calcium (mg), Fiber total dietary (g), Folate DFE (mcg), Iron (mg),
  Magnesium (mg), Niacin (mg), Phosphorus (mg), Potassium (mg), Energy (kcal),
  Carbohydrate (g), Fatty acids (g), Cholesterol (mg)

**Conversation Blueprint:**
1. Arjun creates ticket — begins USDA FoodData Central API integration. Plans to call
   the API in real time for every search query.
2. Arjun discovers critical problem — USDA FoodData Central API has rate limits of
   1000 requests per hour per API key. With multiple users searching simultaneously,
   this limit will be hit within minutes during peak usage. Real-time API calls are
   not viable for production.
3. Shristi asks — how does this affect the 1 second search performance requirement in
   the PRD? If we are rate limited searches will fail or be delayed.
4. Arjun proposes solution — bulk download the entire USDA FoodData Central dataset
   (Foundation Foods and SR Legacy) and import it into our Supabase database. This way
   all searches hit our own database, not USDA API. No rate limits. Sub-100ms search
   response. One-time import of approximately 300,000 food items.
5. Shristi raises concern — the USDA dataset is large. What about Indian foods like
   idli, dosa, chapati, dal? Are they in the USDA database? If users cannot find Indian
   foods the app is useless for our target market.
6. Arjun checks USDA dataset — confirms major gap. Indian foods are largely absent.
   USDA Foundation Foods has only generic entries. Chapati shows as "Bread, whole wheat"
   with wrong nutrient values. This is a significant product risk. Recommends adding
   Custom Food feature to backlog immediately so users can add missing Indian foods.
7. Shristi acknowledges the Indian food gap — notes this is a known risk. Decides to
   proceed with USDA import as the primary database and fast-track Custom Food feature
   to Sprint 5. Documents the gap as a known issue for beta testing feedback.
8. Arjun completes USDA bulk import into Supabase — 300,000+ food items imported with
   all nutrient columns mapped. Search index created on food name column. Shristi
   verifies — searches for "chicken", "apple", "oats" return results within 200ms.
   Closing ticket. Indian food gap documented in backlog.

**Unique Detail:** USDA API rate limit discovery forces a fundamental architecture
change — from real-time API calls to bulk import into Supabase. The Indian food gap
is discovered here and directly leads to Custom Food feature being fast-tracked. This
is the seed of one of the biggest product problems in the story.

**Cross References:** Indian food gap referenced in NUTR-BUG-002, leads to Custom Food
epic CF-EPIC-001. Search performance referenced in NUTR-TASK-002 (fuzzy search),
TECH-004 (performance testing)

---

### Ticket 2: NUTR-TASK-002
**Title:** Fuzzy search implementation for USDA food database
**Tier:** 1 (8 comments)
**Type:** Technical task
**Sprint:** 2
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta, Priya Nair
**Created:** January 16, 2025
**Resolved:** January 27, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Search results must be displayed within 1 second of user input
- The system must support fuzzy or partial matching to accommodate spelling errors
  or variations — "chiken" should suggest "chicken"
- All search results partially or fully matching based on item name should appear
- The food database search interface must be clearly distinguishable from other sources
- Search results must be displayed in a scrollable list with clear labels for food name
- If the user changes the source or navigates away mid-process, previous input should
  be cleared and the user must re-search and re-select the item

**Conversation Blueprint:**
1. Arjun creates ticket — now that USDA data is in Supabase, needs to implement fuzzy
   search. Proposes using PostgreSQL trigram similarity extension (pg_trgm) which is
   natively supported in Supabase. No external service needed.
2. Priya asks — what is trigram similarity? How does it handle "chiken" matching
   "chicken"? Also asks about the frontend debounce — should search trigger on every
   keystroke or wait for user to pause typing?
3. Arjun explains trigram — breaks words into 3-character sequences and compares
   overlap. "chiken" and "chicken" share enough trigrams to score high similarity.
   Recommends 300ms debounce on frontend — fast enough to feel instant, reduces
   unnecessary DB calls.
4. Priya tests trigram approach — finds a problem. Search for "dal" returns 0 results
   because "dal" is only 3 characters. Trigram similarity needs minimum 3 characters
   to work but single trigram for a 3-letter word has poor matching. "daal" also
   returns 0 results.
5. Arjun proposes hybrid approach — use ILIKE pattern matching for short queries
   under 4 characters (faster, exact prefix match), switch to trigram similarity for
   longer queries. This handles "dal" → ILIKE '%dal%' returns results. "chiken" →
   trigram similarity returns "chicken".
6. Shristi asks — the PRD says search results must appear within 1 second. Has anyone
   tested performance with 300,000 rows? A full table scan with ILIKE could be slow.
7. Arjun runs performance tests — without index, ILIKE on 300,000 rows takes 800ms.
   Too slow. Creates GIN index on food name column for trigram, and separate B-tree
   index for ILIKE prefix matching. Re-tests — ILIKE with index: 45ms. Trigram with
   GIN index: 120ms. Both well under 1 second requirement.
8. Priya implements frontend search component with 300ms debounce, hybrid
   short/long query routing, scrollable results list. Shristi verifies — searches
   "dal" (short), "chicken" (exact), "chiken" (misspelled), "broc" (partial). All
   return relevant results within 200ms. Closing ticket.

**Unique Detail:** The 3-character minimum problem with trigrams is a real technical
edge case. The hybrid ILIKE + trigram solution is non-obvious. Performance testing
reveals the need for two different index types. This is a genuinely unique technical
conversation that cannot be confused with any other ticket.

**Cross References:** Depends on NUTR-TASK-001 (USDA data in Supabase). Performance
requirement referenced in TECH-004. Search component referenced in NUTR-007 (select
USDA food source), NUTR-008 (search food with fuzzy matching)

---

### Ticket 3: GOAL-001
**Title:** Set calorie goal with EER calculation
**Tier:** 1 (8 comments)
**Type:** Story — backend
**Sprint:** 2
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 15, 2025
**Resolved:** January 25, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- Variables user can change: target calorie, age, height, current weight, sex,
  goal weight, target date, activity level
- Variables system calculates (non-editable): weight maintenance goal (EER), required
  deficit/surplus, number of days left
- Getting calorie calculated is compulsory — only then user allowed to use food diary
- All fields are mandatory and should be marked with asterisk
- A checkbox should be provided if user wants to track calorie — checked by default
- Target goal = Weight Maintenance goal – Required deficit (for weight loss)
- Target goal = Weight Maintenance goal + Required surplus (for weight gain)
- Target goal = Weight Maintenance goal (for same weight)
- If goal weight = current weight then maintain weight
- If current weight > goal weight then weight loss
- If goal weight > current weight then weight gain

**Conversation Blueprint:**
1. Shristi creates story — defines acceptance criteria for calorie goal setting page.
   All mandatory fields marked with asterisk. EER calculation on form completion.
   Calorie goal is gate for food diary access.
2. Arjun starts implementation — immediately hits a problem. The PRD lists 5 activity
   levels in the UI design requirement but GOAL-SPIKE-001 research showed USDA EER
   documentation uses 4 activity levels (sedentary, low active, active, very active).
   Which 5 activity levels does Shristi intend in the PRD?
3. Shristi checks PRD — realises the PRD was written referencing a different source
   that used 5 levels. After reviewing GOAL-SPIKE-001 research, confirms USDA 4
   activity levels are more scientifically accurate. Decides to use 4 levels and
   update the PRD accordingly.
4. Arjun asks second clarifying question — the PRD says "if user changes gender or
   activity level then automatically new EER formula must be selected." Should the
   EER recalculate automatically in real time as the user changes the dropdown, or
   only on form submission?
5. Shristi confirms real-time recalculation — as user changes any variable the EER
   and calorie budget must update immediately. No submit button needed for calculation.
   User only saves the goal explicitly.
6. Arjun implements calorie goal backend — EER formula selection logic based on gender
   and activity level from GOAL-SPIKE-001 research, real-time calculation endpoints,
   weight goal type detection (loss/gain/maintain), required deficit/surplus calculation.
7. Arjun marks backend complete — asks Shristi to review the API response structure
   before Priya builds the frontend. Shares sample API response with all calculated
   fields including EER, required deficit, calorie budget, weight goal type.
8. Shristi reviews API response — confirms all required fields present. Notes the
   weight_goal_type field is critical — it determines which color coding and formula
   display to use throughout the app. Approves backend. Closing ticket — frontend
   implementation in GOAL-001 frontend story.

**Unique Detail:** PRD activity level mismatch (5 vs 4 levels) is discovered during
implementation. Shristi has to make a product decision to update the PRD. Real-time
vs on-submit calculation debate. The weight_goal_type field becomes a critical
system-wide variable.

**Cross References:** Depends on GOAL-SPIKE-001 (EER formula research). Referenced
in GOAL-002 (EER formula implementation), GOAL-BUG-002 (EER not switching on gender
change), AN-BUG-004 (wrong color for weight maintain calorie goal)

---

### Ticket 4: GOAL-002
**Title:** EER formula implementation per gender and activity level
**Tier:** 1 (8 comments)
**Type:** Story — backend
**Sprint:** 2
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 15, 2025
**Resolved:** January 27, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- EER formula is different for people with different age group, gender, activity level
- Example EER for female age 19+ low active:
  EER = –297.54 – (22.25 × age) + (12.77 × height) + (14.73 × current weight) + 20
- Example EER for female age 19+ sedentary:
  EER = 55.59 – (22.25 × age) + (8.43 × height) + (17.07 × current weight) + 20
- If person changes gender or activity level then automatically new EER formula selected
- If person changes age, current weight, height then same formula used but value updated
- Any change in EER or weight maintenance calorie should automatically result in change
  of target calorie — both changes must reflect in UI immediately
- If user changes current weight: EER changes, target calorie changes, required
  deficit/surplus changes. Target date should NOT change.
- BMR formula for men: 88.362 + (13.397 × weight) + (4.799 × height) – (5.677 × age)
- BMR formula for women: 447.593 + (9.247 × weight) + (3.098 × height) – (4.330 × age)

**Conversation Blueprint:**
1. Shristi creates story — references GOAL-SPIKE-001 research. Arjun to implement all
   15+ EER formula variants with correct selection logic based on gender, age group,
   and activity level.
2. Arjun begins implementation — shares formula selection matrix. Discovers complexity:
   age groups are not uniform across genders. Children, adolescents, and adults each
   have different formula structures. Also discovers that the "+20" constant at the end
   of some female formulas represents thermic effect of food and is not present in
   male formulas. Asks Shristi to confirm this is intentional.
3. Shristi confirms — the +20 thermic effect constant is correct per USDA documentation.
   Different formula structures for different age groups are correct. Arjun to implement
   all variants exactly as per GOAL-SPIKE-001 research document.
4. Arjun implements formula selection logic — creates a formula lookup table keyed by
   gender + age_group + activity_level. Each key maps to the correct EER formula
   coefficients. Tests with 12 different user profiles covering edge cases — 17-year-old
   male active, 65-year-old female sedentary, 25-year-old male very active.
5. Arjun discovers edge case — what happens when user turns 19 on their birthday and
   their age group changes from adolescent to adult? The EER formula should
   automatically switch to adult formula. Currently the system only recalculates EER
   when user manually changes a variable. Date-triggered recalculation is not
   implemented.
6. Shristi makes product decision — auto age-group transition is a V2 feature. For V1
   the formula updates only when user manually updates their age in profile. Documents
   this as a known limitation. The system will not auto-switch formula on birthday.
7. Arjun completes full implementation — all 15 formula variants, formula selection
   matrix, real-time recalculation on any variable change. Writes unit tests covering
   all 15 formula variants with known expected outputs.
8. Shristi tests with 5 user profiles — male age 25 active, female age 35 low active,
   male age 50 sedentary, female age 19 very active, male age 65 low active. All EER
   values match USDA reference values. Closing ticket.

**Unique Detail:** The +20 thermic effect constant in female formulas but not male
formulas is a genuine technical discovery. The age-group transition edge case (birthday
auto-switch) is a real product decision — V1 vs V2 scope. Unit tests with 15 formula
variants demonstrate engineering rigour.

**Cross References:** Directly depends on GOAL-SPIKE-001 (EER research) and GOAL-001
(calorie goal framework). Referenced in GOAL-BUG-002 (EER not switching on gender
change) which reappears during beta testing.

---

### Ticket 5: GOAL-003
**Title:** Required deficit and surplus calculation
**Tier:** 2 (4 comments)
**Type:** Story — backend
**Sprint:** 2
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 20, 2025
**Resolved:** January 25, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- Required surplus = (Goal weight – current weight) × 7700 / No of days left
- Required deficit = (Current weight – goal weight) × 7700 / No of days left
- No of days left = (target date – 1) – current date
- Required deficit/surplus can only be calculated by system — not changed by user
- The required deficit/surplus should always be positive
- If user changes goal weight, current weight, target date, age, height, gender,
  activity level, or target calorie — required deficit/surplus must recalculate
- The 7700 constant represents calories per kilogram of body weight change
- Required deficit/surplus will always be in calories

**Conversation Blueprint:**
1. Shristi creates story with formula from PRD — Required deficit =
   (current weight – goal weight) × 7700 / No of days left. Asks Arjun to confirm
   the 7700 constant is correct and what it represents physiologically.
2. Arjun confirms — 7700 kcal is the approximate energy equivalent of 1 kg of body
   fat. This is a widely used clinical estimate. Implements the formula with correct
   handling of all dependency changes — when calorie goal changes manually, deficit
   recalculates and target date updates. When target date changes, deficit recalculates
   but calorie goal does NOT change (per PRD). When current weight changes, deficit
   recalculates but target date does NOT change.
3. Arjun marks done — notes the dependency matrix is complex. Three different variables
   can change and each triggers different cascading updates. Has documented the full
   dependency matrix in code comments. Asks Shristi to review edge cases.
4. Shristi tests all edge cases — weight loss scenario, weight gain scenario, maintain
   weight scenario. Confirms required deficit/surplus always positive, correct formula
   applied per scenario. Closing ticket.

**Unique Detail:** The 7700 kcal per kg physiological constant. The complex
dependency matrix — different variables trigger different cascading updates. This is
documented thoroughly in code to prevent future bugs.

**Cross References:** Referenced in GOAL-001 (calorie goal framework), GOAL-BUG-001
(target date not updating when calorie changed)

---

### Ticket 6: GOAL-004
**Title:** BMR validation with warning message
**Tier:** 2 (4 comments)
**Type:** Story — backend
**Sprint:** 2
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 20, 2025
**Resolved:** January 26, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- BMR formula for men:
  88.362 + (13.397 × weight in kg) + (4.799 × height in cm) – (5.677 × age in years)
- BMR formula for women:
  447.593 + (9.247 × weight in kg) + (3.098 × height in cm) – (4.330 × age in years)
- If calorie budget is less than BMR then show error message:
  "Calorie budget below BMR [BMR value]. Eating less than BMR calories could cause
  excessive loss of lean body mass. Please change the value"
- Do NOT set the calorie goal when below BMR
- Only remove the goal weight and target date value — keep showing EER/WMC
- In case user-defined target calorie is less than BMR — show warning but ALLOW user
  to add value (different from system-calculated below BMR case)
- If target calorie is less than respective BMR for men and women then show error but
  allow user to add value

**Conversation Blueprint:**
1. Shristi creates story — references two different BMR scenarios in PRD. First: when
   system calculates calorie goal and result is below BMR — do not set goal, show error,
   remove goal weight and target date. Second: when user manually overrides calorie goal
   below BMR — show warning but still allow saving. Asks Arjun to confirm he understands
   the distinction.
2. Arjun confirms understanding — two different behaviours for same condition depending
   on whether it is system-calculated or user-defined. Implements both BMR formulas
   (separate for men and women using Mifflin-St Jeor equations from PRD). Implements
   two-path validation logic. Notes this is a health safety feature — most important
   PRD requirement to get exactly right.
3. Arjun marks implementation complete — both BMR formulas working, validation paths
   correct. Asks Shristi to test specifically the edge case where system calculates a
   calorie goal below BMR due to very aggressive weight loss target.
4. Shristi tests — creates test user: female, 60kg, goal 45kg, target date 30 days.
   System calculates required deficit of 3,500 kcal/day which puts calorie goal at
   negative value — far below BMR. Confirms system correctly blocks goal setting,
   shows error message with exact BMR value, removes goal weight and target date but
   preserves EER display. Also tests manual override — manually enters 900 kcal below
   BMR, confirms warning shows but save is still allowed. Closing ticket.

**Unique Detail:** Two different validation behaviours for the same below-BMR condition
depending on whether it is system-calculated or user-defined. The health safety
implications make this the most carefully implemented validation in the whole app.
The test case of negative calorie goal from aggressive weight loss target is a real
edge case Shristi must test explicitly.

**Cross References:** Referenced in GOAL-BUG-005 (BMR warning shown but goal still
saved incorrectly — reappears in Sprint 8 when beta users find the validation is
broken)

---

## SUMMARY OF SPRINT 2

| Ticket | Tier | Comments | Status |
|---|---|---|---|
| NUTR-TASK-001 | T1 | 8 | Closed Jan 24 |
| NUTR-TASK-002 | T1 | 8 | Closed Jan 27 |
| GOAL-001 | T1 | 8 | Closed Jan 25 |
| GOAL-002 | T1 | 8 | Closed Jan 27 |
| GOAL-003 | T2 | 4 | Closed Jan 25 |
| GOAL-004 | T2 | 4 | Closed Jan 26 |

**Total comments Sprint 2: 40**

---

## KEY STORY THREADS STARTING IN SPRINT 2

These are narrative threads that begin in Sprint 2 and are referenced in later sprints:

**Thread 1 — Indian Food Gap**
Discovered in NUTR-TASK-001 comment 6. Shristi documents it as known issue. This
thread continues in beta testing (Sprint 7) when users complain. Drives Custom Food
discoverability improvements in Sprint 8. Referenced in marketing emails by Ananya.

**Thread 2 — EER Activity Level Mismatch**
Discovered in GOAL-001 comment 2. Shristi updates the PRD. This decision is referenced
in GOAL-BUG-002 (Sprint 7) when beta users find the formula switches incorrectly.

**Thread 3 — Age Group Auto-Transition**
Discovered in GOAL-002 comment 5. Deferred to V2. Referenced in June V2 planning
discussions.

**Thread 4 — BMR Validation Two Paths**
Implemented in GOAL-004. The two-path logic is fragile. GOAL-BUG-005 (Sprint 8) is
directly caused by a regression in this logic during a refactor.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 2

Same rules as Sprint 1 plus:

1. Sprint 2 dates range from January 15 to January 28, 2025
2. Comments should reference Sprint 1 work naturally —
   "now that the USDA data is in Supabase from NUTR-TASK-001..."
3. The Indian food gap discovery in NUTR-TASK-001 is the most important narrative
   moment in Sprint 2 — write it with genuine concern from Shristi about product
   viability for Indian users
4. GOAL-001 and GOAL-002 are deeply connected — GOAL-002 picks up exactly where
   GOAL-001 left off. The activity level decision from GOAL-001 flows directly into
   the formula implementation in GOAL-002
5. GOAL-003 and GOAL-004 are straightforward but must reference the complex dependency
   matrix from GOAL-001 naturally — Arjun references it to explain the cascade logic
6. The +20 thermic effect constant in GOAL-002 comment 3 must be technically accurate —
   it is the dietary induced thermogenesis constant in female EER formulas per USDA