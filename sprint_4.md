sprint 4 

# Sprint 4 Ticket Definitions — Complete Brief for GPT-4o
## February 12 to February 25, 2025

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions. Sprint 4 is the core food
logging sprint. By end of Sprint 4, users can search the USDA database, select a
food, adjust portion size, add to diary, and see nutrient totals with goal comparison.
This is the first sprint where the full end-to-end logging flow becomes testable.

---

## SPRINT 4 TICKETS

---

### Ticket 1: NUTR-007
**Title:** Select USDA food database as source when adding food to diary
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 12, 2025
**Resolved:** February 17, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- User must be able to select Food Database as a source when adding food
- Food from food database can be selected in two ways — Add Food in diary OR Food
  Database tab
- Search input field available after selecting source
- Only one item can be selected at a time
- Food database selection and search interface must be clearly distinguishable from
  other sources (custom food, recipe etc)
- Search results in scrollable list with clear food name labels
- If user changes source or navigates away mid-process, previous input must be cleared
  and user must re-search and re-select
- Food database should appear instantly as user adds food in diary
- As user selects food source they should be redirected to adjust portion page instantly

**Conversation Blueprint:**
1. Shristi creates story — USDA food database source selection. Two entry points:
   Add Food button in diary and Food Database tab. Interface must be clearly
   distinguishable from custom food and recipe sources. Asks Priya to confirm the
   state clearing behaviour — if user selects USDA, searches "chicken", then switches
   to custom food source, the "chicken" search must clear completely.
2. Priya confirms state clearing on source switch — will implement using React
   useEffect cleanup that fires when source changes. Also asks Arjun to confirm the
   API endpoint — when user selects a food from USDA search results, what data is
   returned to populate the adjust portion page instantly?
3. Arjun confirms — the search endpoint returns food_id, food_name, and default
   serving size. The adjust portion page then makes a second call with food_id to
   fetch full nutrient breakdown. This two-step approach keeps search results fast
   (no heavy nutrient data in search response) while loading full detail only when
   needed. Priya implements accordingly.
4. Shristi verifies — tests USDA source selection from diary Add Food button and from
   Food Database tab. Confirms both entry points work. Source switch clears search.
   Redirect to adjust portion instant after food selection. Closing ticket.

**Unique Detail:** Two-step API design — lightweight search response for fast results,
full nutrient detail loaded only when food is selected. State clearing on source switch
via React useEffect cleanup.

**Cross References:** Depends on NUTR-TASK-001 (USDA data), NUTR-TASK-002 (fuzzy
search). Referenced in NUTR-009 (adjust portion page), NUTR-BUG-008 (search results
not clearing on source change — Sprint 8)

---

### Ticket 2: NUTR-008
**Title:** Search food with fuzzy matching in USDA database
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 12, 2025
**Resolved:** February 17, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- Search results displayed within 1 second of user input
- System must support fuzzy or partial matching — "chiken" should suggest "chicken"
- All search results partially or fully matching item name should appear
- Users allowed to go back from food database
- If user changes source or navigates away, previous input cleared
- Search results in scrollable list with clear food name labels

**Conversation Blueprint:**
1. Shristi creates story — frontend search component using the fuzzy search backend
   from NUTR-TASK-002. 300ms debounce already decided in NUTR-TASK-002. Asks Priya
   to confirm the minimum character count before search fires — should single character
   trigger a search?
2. Priya proposes minimum 2 characters before search triggers — single character
   searches like "a" would return thousands of results and cause performance issues.
   2 characters narrows results meaningfully. Asks Arjun to confirm backend handles
   2-character minimum correctly with the ILIKE/trigram hybrid approach from
   NUTR-TASK-002.
3. Arjun confirms — the ILIKE path handles 2-3 character queries fine (prefix match).
   Trigram kicks in for longer queries. Minimum 2 characters on frontend is correct.
   Priya implements search component with 2-character minimum, 300ms debounce,
   scrollable results list.
4. Shristi verifies — tests with partial names ("chic" returns chicken), misspellings
   ("chiken" returns chicken), short queries ("da" returns dal items from custom food
   if added, USDA items with "da" prefix). No results message shown correctly for
   completely unrecognised inputs. Closing ticket.

**Unique Detail:** Minimum 2 character threshold decision — single character would
return thousands of rows. The 2-character minimum is a UX and performance decision
that connects back to the ILIKE/trigram architecture from NUTR-TASK-002.

**Cross References:** Directly builds on NUTR-TASK-002 (fuzzy search backend) and
NUTR-007 (source selection). Referenced in NUTR-BUG-008 (search results not clearing)

---

### Ticket 3: NUTR-009
**Title:** Adjust portion size with food-specific serving units and instant recalculation
**Tier:** 1 (8 comments)
**Type:** Story — full stack
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta, Priya Nair, Kabir Sharma
**Created:** February 12, 2025
**Resolved:** February 24, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta, Priya Nair, Kabir Sharma

**PRD Requirements:**
- Adjust portion page is a compulsory step — user cannot add food without it
- Two input fields: amount of serving (editable number) and serving unit (dropdown)
- Initially full nutrient breakdown shown based on default serving size
- Nutrient breakdown recalculates instantly as user re-edits portion size
- Nutrient breakdown table columns: nutrient name, actual value, default unit, DV%
- Calorie, macros (carb, fat, protein) and micros clearly separated in table
- If nutrient value is zero — show blank for amount and DV%. Unit still shown.
- If nutrient DV% is less than 1 — show '-' instead of decimal value
- DV% calculated based on 2000 calorie diet
- All nutrient values displayed at once — no "see more" or expansion needed
- All 4 components clearly distinguishable: food name, serving size inputs, nutrient
  table, Add button
- If navigates back — redirected to food database page, search cleared

**Conversation Blueprint:**
1. Shristi creates story — adjust portion page. Two editable fields: amount (number
   input) and serving unit (dropdown). Full nutrient table loads instantly on page
   load. Recalculates instantly on portion change. Asks Arjun what serving unit
   options will be in the dropdown — is it a fixed list like gram/cup/tablespoon
   or is it food-specific?
2. Arjun investigates USDA data structure and discovers a critical problem not
   accounted for in the PRD. USDA foods have food-specific serving units with
   food-specific gram weights. A "cup" of oats weighs 156 grams. A "cup" of spinach
   weighs only 30 grams. A "cup" of oil weighs 218 grams. The serving unit dropdown
   cannot be a generic fixed list — it must show the actual serving units stored
   for each specific food in the USDA database, each with their correct gram weights.
   If we use a generic list, nutrient calculations will be completely wrong.
3. Shristi asks — how many serving unit options does a typical USDA food have? And
   does the PRD need to be updated to reflect food-specific serving units? This was
   not explicitly mentioned in the PRD.
4. Arjun checks USDA data — most foods have 2-5 serving unit options. For example
   "Chicken, broiled" has: 100g (100g), 1 cup chopped (140g), 1 oz (28g), 1 breast
   (172g). The PRD says "serving unit dropdown" without specifying generic vs
   food-specific. Shristi and Arjun debate: hardcode a generic unit list and
   approximate, or pull food-specific units from USDA data.
5. Kabir joins the discussion — raises a UX concern. If the dropdown shows
   food-specific units like "1 breast (172g)" for chicken and "1 cup (156g)" for
   oats, users will immediately understand the serving sizes they are entering.
   A generic list of gram/cup/tablespoon would confuse users — a cup of oats and a
   cup of chicken are vastly different amounts. Food-specific units are essential
   for accurate logging and good UX.
6. Shristi makes the decision — food-specific serving units from USDA data. This
   is the correct approach both technically and from UX perspective. Notes this
   requires updating the USDA import from NUTR-TASK-001 to also import serving
   unit data per food. Arjun to update the import and add serving_units table.
7. Arjun updates USDA import — adds food_serving_units table with food_id,
   unit_name, gram_weight. Updates adjust portion API to return serving units for
   selected food. Priya updates dropdown to populate from API response. Recalculation
   logic: new_nutrient_value = (base_nutrient_per_100g × gram_weight × quantity) / 100.
8. Shristi verifies with multiple food types — oats cup (156g) vs spinach cup (30g)
   show different nutrient values for same "1 cup" selection. Chicken breast (172g)
   calculates correctly. DV% shows '-' for nutrients below 1%. Zero nutrients show
   blank. All nutrients visible at once without scrolling vertically. Closing ticket.

**Unique Detail:** The food-specific serving unit discovery is the core of this ticket.
USDA stores gram weights per serving unit per food — a "cup" is not a universal
measurement. This was completely missed in the PRD. The three-way debate between
Arjun (technical accuracy), Kabir (UX clarity), and Shristi (product decision) makes
this conversation unique. The recalculation formula
(base_nutrient_per_100g × gram_weight × quantity / 100) is the mathematical heart
of the entire food logging feature.

**Cross References:** Requires update to NUTR-TASK-001 (USDA import now includes
serving units). NUTR-BUG-003 (serving unit dropdown not resetting — Sprint 7) is
directly caused by the serving unit state management implemented here.

---

### Ticket 4: NUTR-010
**Title:** Add food to diary and redirect to food diary page instantly
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 14, 2025
**Resolved:** February 19, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- As soon as user adds food they are redirected to food diary page
- Nutrient data for selected meal should add up to nutrient data of other food
  present in food diary
- Addition of food to food diary should happen instantly
- Adding item to diary must update day's nutrient totals without delay
- There should be no limit to number of food or recipe added
- Food or recipe cannot be added without meal type selection — warning message
  "Food or recipe cannot be logged without meal type selection" shown on adjust
  portion page

**Conversation Blueprint:**
1. Shristi creates story — Add button on adjust portion page submits the food log
   and redirects to diary. Warns that the meal type validation is critical — if user
   reached adjust portion from food database tab (not from within a meal section),
   they must explicitly select meal type before Add button works. Asks Priya how
   the meal type warning will be displayed.
2. Priya proposes — Add button disabled until meal type is selected when coming
   from food database tab. Warning message shown inline below the meal type dropdown.
   When coming from diary Add Food button within a meal section, meal type is pre-filled
   and Add button is immediately active. Implements both entry point behaviours.
3. Priya marks complete — notes one important detail: after redirect to diary, the
   newly added food must appear in the correct meal section immediately without page
   reload. This connects to the React Context from NUTR-BUG-001 fix (not yet built
   at this point, but the architecture must support it). Asks Arjun to confirm the
   POST endpoint returns the saved food log entry in the response so frontend can
   optimistically update the diary without a second GET request.
4. Arjun confirms — POST /food-logs returns the complete saved entry including all
   nutrient values. Frontend can immediately append to diary state without refetching.
   Priya implements optimistic update. Shristi verifies: adds 5 foods rapidly, all
   appear in diary instantly, totals update correctly. Closing ticket.

**Unique Detail:** Optimistic update architecture — POST returns complete entry so
frontend updates diary state without refetching. Two different meal type behaviours
depending on entry point (diary vs food database tab). These implementation decisions
directly affect NUTR-BUG-001 in Sprint 7.

**Cross References:** Connects to NUTR-BUG-001 (nutrient totals not updating —
the optimistic update here is the precursor to the React Context bug discovered
in Sprint 7). Depends on NUTR-009 (adjust portion page), NUTR-007 (source selection)

---

### Ticket 5: NUTR-015
**Title:** Display only goal nutrients as columns with logged food values
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 14, 2025
**Resolved:** February 20, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Only nutrients checked to track should be shown as columns in food diary
- Column order: Calorie (if selected) → Macros alphabetical → Micros alphabetical
- Max 20 nutrient columns displayed at once
- Each logged food item shows its nutrient value under each target nutrient column
- If food does not contain a target nutrient the value field should display '-'
- Nutrient values in food diary are non-editable
- User can scroll left to right to view all nutrient columns
- If food has nutrient value of zero the value field shows '-'

**Conversation Blueprint:**
1. Shristi creates story — builds on NUTR-005 (diary structure from Sprint 3). Now
   that food can actually be logged (NUTR-010), need to display the nutrient values
   per food item in the correct columns. Each food row shows its tracked nutrient
   values. Non-tracked nutrients not shown at all. Asks Priya to confirm the dash
   vs blank rule — when does a column show '-' vs empty?
2. Priya clarifies with Shristi — two different '-' cases in PRD. Case 1: food has
   the nutrient but value is zero (e.g. chicken has 0mg Vitamin C). Case 2: food
   simply does not have data for that nutrient in USDA database. Both show '-' in
   the column. The unit column should still show even when value is '-' so user knows
   what units they are looking at. Implements accordingly.
3. Priya marks column rendering complete — asks about a specific edge case. User has
   20 tracked nutrients. They add a food that has values for only 5 of those nutrients.
   The other 15 columns show '-'. Should the '-' columns still be rendered (correct
   per PRD) or should they be hidden to reduce visual clutter?
4. Shristi confirms — all 20 columns must always be visible even if '-'. This is
   intentional — users need to see that a food has no vitamin C even if the column
   looks empty. The '-' is information, not absence of information. Priya finalises
   implementation. Shristi verifies column order correct, values accurate, '-' shows
   for zero and missing values. Closing ticket.

**Unique Detail:** The '-' vs blank distinction — two different zero conditions that
both display '-'. The philosophical decision that '-' columns must always show because
absence of a nutrient is itself information. This connects to NUTR-BUG-009 (DV%
showing value instead of dash for less than 1) in Sprint 8.

**Cross References:** Builds on NUTR-005 (diary column structure). Connects to
NUTR-BUG-009 (DV% dash rule). The '-' rule also referenced in adjust portion page
NUTR-009

---

### Ticket 6: NUTR-016
**Title:** View cumulative nutrient totals at bottom of food diary
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 17, 2025
**Resolved:** February 22, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Cumulative total for each target nutrient displayed at bottom of each nutrient column
- Cumulative total = sum of each target nutrient consumed in a day across all meals
- Totals calculated from first food logged to last food logged regardless of meal
  or food source
- If food does not contain a target nutrient its value treated as 0 in cumulative total
- Updates in real time as food is added
- Total must be accurate even with multiple rapid changes or many foods added
- User should not be allowed to edit any value in food diary
- User can scroll up to down to view all nutrient values and total

**Conversation Blueprint:**
1. Shristi creates story — cumulative totals pinned at the bottom of each nutrient
   column. Sum of all logged foods for the selected date across all meals. Real-time
   update. Asks Priya to confirm the visual design — is the total row always visible
   (sticky) or does it scroll with the content?
2. Priya proposes — total row should be sticky at bottom of diary viewport. As user
   scrolls through long list of logged foods, they can always see their running totals.
   This is especially important for users tracking 15-20 nutrients across many meals.
   Asks Kabir to confirm this was in the design.
3. Priya checks with Kabir offline (not in this ticket) — confirms sticky total row
   is the intended design. Implements sticky total row using CSS position: sticky.
   Notes the total row calculation sums across ALL meals for the date — breakfast +
   lunch + dinner + snacks + supplement all contribute to the same running total.
4. Shristi verifies — adds foods to breakfast, lunch, dinner. Confirms total row
   sums all three meals. Scroll test: diary with 20 foods across meals, total row
   stays visible at bottom while scrolling. Real-time update confirmed on adding
   and deleting foods. Closing ticket.

**Unique Detail:** Sticky total row design decision — always visible while scrolling
through long food lists. This is critical UX for users tracking many nutrients.
The cross-meal aggregation confirms all meals contribute to one daily total.

**Cross References:** This is the display layer for NUTR-TASK-004 (calculation engine).
NUTR-BUG-001 (totals not updating) in Sprint 7 is caused by this component not
subscribing to React Context state changes correctly.

---

### Ticket 7: NUTR-017
**Title:** Compare actual vs goal with color coding — red yellow green
**Tier:** 2 (4 comments)
**Type:** Story — frontend design
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair
**Created:** February 17, 2025
**Resolved:** February 23, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Priya Nair

**PRD Requirements:**
- System must compare cumulative actual intake against user's daily goal for each nutrient
- Display for each nutrient: goal value, actual value consumed, difference (actual-goal)
- Color coding for CALORIE in weight loss or weight gain goal:
  Yellow if actual/target % < 100 (under target)
  Green if actual/target % = 100 (exactly on target)
  Red if actual/target % > 100 (over target)
- Color coding for CALORIE in weight MAINTAIN goal:
  Yellow if actual/target % < 100 (under)
  Yellow if actual/target % > 100 (over — NOT red, because over-eating to maintain
  weight is less concerning than over-eating during weight loss)
  Green if actual/target % = 100 (exactly on target)
- Color coding for ALL OTHER NUTRIENTS:
  Yellow if actual < daily target
  Green if actual = daily target OR actual <= daily max target
  Red if actual > daily max target
- Remark shown using color in the difference section
- Comparison must update within 1 second of any add/edit/delete

**Conversation Blueprint:**
1. Shristi creates story — color coding logic has three distinct cases. Most critical
   and easy to miss: calorie in weight MAINTAIN goal shows yellow for both over and
   under, never red. This is different from weight loss/gain where over calorie is red.
   Asks Kabir to design the difference display and Priya to implement the three-case
   logic.
2. Kabir shares Figma — difference row shows actual, goal, and difference value.
   Color applied to the difference value text. Notes the maintain weight case where
   over-calories shows yellow not red — this is subtle and important for the maintain
   weight user persona. Has added a note in Figma to flag this case to Priya.
3. Priya implements color logic — uses weight_goal_type from GOAL-001 backend to
   determine which color rule to apply for calories. For all other nutrients uses
   the simpler under/on-track/over rule based on RDA and MAX values. Asks Shristi
   to confirm one edge case: what if user has no MAX value set for a micronutrient
   (because RDA exists but no defined MAX)? Should the nutrient ever turn red?
4. Shristi clarifies — if no MAX value exists for a micronutrient, it can only be
   yellow (under) or green (on track). Never red because we have no threshold to
   define "over". Priya updates implementation. Kabir verifies color rendering.
   Shristi tests all three weight goal types. Closing ticket. Notes this is the
   exact logic that NUTR-BUG-005 (Sprint 7) will break for weight maintain case.

**Unique Detail:** The weight maintain calorie case showing yellow instead of red
for over-consumption is a deliberate clinical decision — overeating to maintain weight
is less risky than overeating during active weight loss. The micro MAX value edge case
(no MAX = no red) is a product decision that needs explicit implementation. The
weight_goal_type from GOAL-001 is the critical system-wide variable driving this.

**Cross References:** Depends on weight_goal_type from GOAL-001 backend. NUTR-BUG-005
(goal comparison colors wrong for weight maintain case — Sprint 7) is directly caused
by this logic being implemented incorrectly for the maintain case. Also referenced in
AN-BUG-004 (wrong color for weight maintain in analysis page)

---

### Ticket 8: NUTR-018
**Title:** Per meal nutrient breakdown — bold total at end of each meal section
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 4
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 17, 2025
**Resolved:** February 22, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Nutrients of each food item within a meal must be added up and displayed as a meal
  total at the end of the last food item in that meal
- Total nutrient consumed per meal should be bold
- No color coding for meal totals (unlike daily cumulative total)
- Design same as nutrient view — just without color coding and bold values
- If food does not have a target nutrient its value treated as 0 in meal total
- Meal total is separate from daily cumulative total — it shows per-meal not per-day

**Conversation Blueprint:**
1. Shristi creates story — meal subtotal row after the last food in each meal section.
   Bold values. No color coding. Different from the daily total which has color coding
   and is pinned at the bottom. Asks Priya to confirm how this interacts with the
   sticky total row from NUTR-016 — will there be two total rows visible?
2. Priya explains the distinction — meal subtotal appears inline between meal sections
   (after last food of breakfast, before first food of lunch). Daily cumulative total
   is sticky at the very bottom of the entire diary. They are in different positions
   and serve different purposes. No conflict.
3. Priya marks implementation complete — notes one edge case. When user has only one
   food item in a meal, the meal total is identical to that single food's values.
   Should the meal total row still show? Or only show when there are 2+ foods?
4. Shristi confirms — always show meal total even with single food. Consistent UX —
   user should always see the meal subtotal row at the same position regardless of
   how many foods are in the meal. Priya finalises. Shristi verifies meal totals
   correct for single-food meals and multi-food meals. Bold confirmed. No color.
   Closing ticket.

**Unique Detail:** The architectural distinction between meal subtotal (inline, no
color, bold) and daily total (sticky, with color, from NUTR-017). Both exist in the
same diary view but serve different purposes. The always-show-even-single-food
decision ensures consistent UX.

**Cross References:** Companion to NUTR-016 (cumulative total) and NUTR-017 (color
coding). NUTR-BUG-010 (per-meal total appearing after wrong food — Sprint 8) is
caused by the meal grouping logic implemented here

---

### Ticket 9: NUTR-TASK-004
**Title:** Real-time nutrient calculation engine
**Tier:** 2 (4 comments)
**Type:** Technical task
**Sprint:** 4
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta, Priya Nair
**Created:** February 12, 2025
**Resolved:** February 24, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Nutrient recalculation must happen within 1 second after any add, edit, or delete
- No manual refresh needed by the user
- Cumulative totals must be accurate with multiple rapid changes
- Meal subtotals and daily totals must both update instantly
- After recalculation: updated nutrient totals shown in same format as original
- Over/under/on-track indicators must update accordingly
- Users must not have to manually save or confirm for recalculations to occur
- All recalculated values must maintain unit consistency (kcal, g, mg, µg)

**Conversation Blueprint:**
1. Arjun creates ticket — designs the calculation engine. Two options: server-side
   calculation (every add/edit/delete triggers API call that returns recalculated
   totals) vs client-side calculation (frontend recalculates totals using stored
   food data without API call). Asks Priya which approach fits the React architecture
   better.
2. Priya recommends client-side calculation — server-side approach adds network
   latency that makes hitting 1 second requirement risky on slow connections. With
   client-side, the calculation is instant because all food data is already in React
   state. The formula is simple: sum each nutrient value across all logged foods for
   the date. No complex logic needed. Arjun agrees.
3. Arjun implements the calculation engine as a pure JavaScript function — takes
   array of food log entries, returns calculated totals per nutrient. Priya integrates
   it into React state — calculation runs automatically whenever the food log array
   changes (add, edit, delete). The result feeds into both NUTR-016 (daily totals)
   and NUTR-018 (meal subtotals) components.
4. Shristi tests with rapid additions — adds 10 foods quickly in succession. All
   totals update correctly after each addition without any lag. Tests deletion and
   portion edit — both trigger recalculation correctly. Confirms no manual save needed.
   Closing ticket. Notes this architecture (client-side calculation on food log array
   changes) is what NUTR-BUG-001 in Sprint 7 will break when React Context is not
   properly set up.

**Unique Detail:** Client-side calculation chosen over server-side to guarantee
1-second performance on slow connections. Pure JavaScript function operating on
React state array. This architecture decision is what makes NUTR-BUG-001 (Sprint 7)
so easy to fix once the root cause (missing React Context subscription) is identified.

**Cross References:** Powers NUTR-016 (cumulative totals display) and NUTR-018
(meal subtotals). NUTR-BUG-001 and AN-BUG-003 (Sprint 7) are both caused by
components not subscribing to the food log state changes that trigger this engine

---

## SUMMARY OF SPRINT 4

| Ticket | Tier | Comments | Reporter | Assignee | Closed |
|---|---|---|---|---|---|
| NUTR-007 | T2 | 4 | Shristi | Priya | Feb 17 |
| NUTR-008 | T2 | 4 | Shristi | Priya | Feb 17 |
| NUTR-009 | T1 | 8 | Shristi | Arjun/Priya/Kabir | Feb 24 |
| NUTR-010 | T2 | 4 | Shristi | Priya | Feb 19 |
| NUTR-015 | T2 | 4 | Shristi | Priya | Feb 20 |
| NUTR-016 | T2 | 4 | Shristi | Priya | Feb 22 |
| NUTR-017 | T2 | 4 | Shristi | Kabir/Priya | Feb 23 |
| NUTR-018 | T2 | 4 | Shristi | Priya | Feb 22 |
| NUTR-TASK-004 | T2 | 4 | Arjun | Arjun/Priya | Feb 24 |

**Total comments Sprint 4: 40**

---

## KEY STORY THREADS IN SPRINT 4

**Thread 1 — Food-Specific Serving Units**
NUTR-009 discovers USDA foods have food-specific gram weights per serving unit.
This forces an update to NUTR-TASK-001 (USDA import must now include serving units).
NUTR-BUG-003 (Sprint 7) — serving unit dropdown not resetting on navigation — is
directly caused by serving unit state management implemented here.

**Thread 2 — React State Architecture**
NUTR-010 establishes optimistic update pattern (POST returns full entry, frontend
updates state without refetch). NUTR-TASK-004 establishes client-side calculation
engine operating on food log array. Both of these architectural decisions are what
make NUTR-BUG-001 and AN-BUG-003 (Sprint 7) happen — when the React Context is not
wired correctly, these components fail to subscribe to state changes.

**Thread 3 — Weight Maintain Color Logic**
NUTR-017 implements the three-case color logic including the weight maintain calorie
case showing yellow not red. NUTR-BUG-005 (Sprint 7) breaks exactly this case.
AN-BUG-004 (Sprint 9) breaks it again in the analysis page.

**Thread 4 — Dash Rule for Zero and Missing Nutrients**
NUTR-015 establishes the '-' rule for zero and missing nutrient values.
NUTR-BUG-009 (Sprint 8) — DV% showing decimal instead of dash for values less than
1% — is a regression of the same rule applied in the adjust portion page NUTR-009.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 4

1. Sprint 4 dates: February 12 to February 25, 2025
2. Sprint 4 is the first sprint where the full end-to-end logging flow is being built.
   By end of Sprint 4, a user can search, select, adjust, add food and see totals.
   Comments should reflect the excitement of building the core product flow.
3. NUTR-009 is the most important ticket in Sprint 4 — the food-specific serving unit
   discovery must sound like a genuine surprise. Arjun investigated the data and found
   something the PRD authors missed. Write his comment 2 with the detail and weight
   of someone who just discovered a fundamental architecture gap.
4. NUTR-017 colour logic for weight maintain case must be technically precise — yellow
   for over-calories during weight maintenance is a clinical decision. Shristi should
   reference this as a deliberate product choice rooted in health science.
5. NUTR-TASK-004 introduces the client-side calculation engine — Arjun and Priya's
   debate between server-side and client-side should feel like two engineers making
   a real architecture decision together, not just picking arbitrarily.
6. All Sprint 4 tickets should reference Sprint 3 and Sprint 2 work naturally —
   "now that USDA data is in Supabase from NUTR-TASK-001..." and "using the fuzzy
   search from NUTR-TASK-002..." and "the weight_goal_type from GOAL-001..."
7. By end of Sprint 4 comments should convey a sense of progress — the team can see
   the product taking shape for the first time.