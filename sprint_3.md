sprint 3

# Sprint 3 Ticket Definitions — Complete Brief for GPT-4o
## January 29 to February 11, 2025

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions — same product description,
same team profiles, same comment style rules. Sprint 3 builds on Sprint 2 work —
calorie goal setting is now complete. Sprint 3 completes macro and micro goal setting
and begins the first food diary UI components.

---

## SPRINT 3 TICKETS

---

### Ticket 1: GOAL-005
**Title:** Default macro distribution 40:30:30 of target calorie
**Tier:** 2 (4 comments)
**Type:** Story — backend
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 29, 2025
**Resolved:** February 3, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- By default carb:fat:protein should be 40:30:30 of target calorie
- Default macro goal should be displayed instantly as user navigates to set macros step
- Macro breakdown must be shown in both kcal and grams
- For same macro distribution % if user changes target calorie the gram equivalent
  should auto-update based on new calorie
- The macro in gram becomes the main goal of the user
- Conversion rules: Carb in gram = Carb in kcal/4, Fat in gram = Fat in kcal/9,
  Protein in gram = Protein in kcal/4
- If no calorie goal is set macro values should remain hidden
- System should automatically save macros % out of calorie budget, gram and kcal

**Conversation Blueprint:**
1. Shristi creates story — default 40:30:30 must auto-populate when user reaches macro
   step. Asks Arjun to confirm the gram conversion formulas — 4/4/9 kcal per gram for
   carb/protein/fat respectively. Notes the macro in gram is the PRIMARY goal that food
   diary will compare against.
2. Arjun confirms 4/4/9 conversion rules are standard nutritional science. Implements
   default distribution endpoint — when calorie goal exists and user reaches macro step,
   system auto-calculates and saves 40:30:30 split in kcal and grams. No user action
   needed for default. Tests with 2000 kcal calorie goal: Carb = 800 kcal = 200g,
   Fat = 600 kcal = 66.7g, Protein = 600 kcal = 150g.
3. Arjun marks complete — asks Shristi to verify one important behaviour. If user
   already has a custom macro split saved from a previous session and comes back to
   the goal setting page, should the 40:30:30 default override their custom split?
4. Shristi confirms — NO. 40:30:30 default is only applied when user has never set
   macros before. If custom macros exist, those are shown. Default is a first-time
   experience only. Arjun adds first-time check to implementation. Closing ticket.

**Unique Detail:** The critical distinction — default 40:30:30 applies only for
first-time users, not returning users. The macro in gram is the primary goal (not %
or kcal). This distinction drives food diary comparison logic.

**Cross References:** Referenced in GOAL-006 (custom macro input), GOAL-007
(validation), GOAL-BUG-003 (macro gram values not updating when calorie changes)

---

### Ticket 2: GOAL-006
**Title:** Custom macro percentage input with real-time gram and kcal recalculation
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** January 29, 2025
**Resolved:** February 4, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User should be allowed to set custom % kcal manually for any macro
- System must recalculate macro distribution in Kcal and gram accordingly
- New values must immediately replace the default 40:30:30 distributions
- As user changes any one macro the equivalent gram and kcal value should be
  instantly calculated
- As user changes calorie goal the macros value should be instantly changed
- Each macro must have editable percentage input field
- At each field system should dynamically display corresponding calorie and gram value
- Only numeric input between 0 and 100 should be allowed
- System should automatically save macro % of calorie and corresponding gram and
  kcal values as user inputs

**Conversation Blueprint:**
1. Shristi creates story — three editable percentage input fields for carb, fat,
   protein. Each field shows live kcal and gram equivalent. Real-time calculation on
   every keystroke. Auto-save as user types. Asks Priya to confirm the component
   architecture — will this be a controlled React component with local state?
2. Priya confirms controlled component approach — each input field managed by React
   state, onChange triggers recalculation. Notes potential performance issue — if user
   types quickly the recalculation fires on every single keystroke including partial
   inputs like "3" while typing "30". Asks whether to debounce the calculation or
   calculate on every change.
3. Priya decides no debounce — PRD says instant calculation. Even partial inputs like
   "3" should show live calculation (3% of 2000 kcal = 60 kcal = 15g carb). This
   gives users live feedback as they type which is the intended UX. Implements with
   onChange calculation, marks complete.
4. Shristi verifies — tests changing carb from 40 to 50, confirms fat and protein
   grams and kcal update correctly even though their % did not change (because calorie
   equivalents are relative to target calorie). Confirms auto-save working. Closing
   ticket.

**Unique Detail:** The decision NOT to debounce — PRD says instant, so partial inputs
like "3" while typing "30" must still show live calculation. This is intentional UX
that requires controlled components without debounce on calculation.

**Cross References:** Depends on GOAL-005 (default macros). Referenced in GOAL-007
(validation of sum to 100%), GOAL-BUG-003 (macro gram values not updating)

---

### Ticket 3: GOAL-007
**Title:** Validate macros sum to 100% with real-time error display
**Tier:** 1 (8 comments)
**Type:** Story — frontend technical
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** January 30, 2025
**Resolved:** February 8, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- Total of custom macro percentages (carbs + protein + fat) must equal exactly 100%
- All 3 macros % kcal fields are mandatory to be filled
- If sum is not 100% — display value of total % in red, show message
  "% sum of macros not 100%"
- If any field empty — display borders of input fields in red, show message
  "All macros should have goal value"
- If both conditions met — show total 100% in green, enable track macro checkboxes
- Validation and error messaging must occur in real time (≤1 second) after user input
- Do not allow setting macro goal if validation fails
- If user refreshes the page even if macros not validated the same value should persist

**Conversation Blueprint:**
1. Shristi creates story — real-time sum validation. Total must be exactly 100%.
   Green when valid, red when invalid. Checkboxes to track macros only enabled when
   valid. Asks Priya to implement.
2. Priya implements validation — uses JavaScript to sum three percentage inputs and
   compare to 100. During testing discovers a floating point arithmetic problem.
   User enters 33.33 + 33.33 + 33.34. JavaScript calculates 99.99999999999999 instead
   of 100.00. Validation fails even though the input is correct. Reports to Arjun.
3. Arjun explains — this is a classic JavaScript floating point precision issue.
   IEEE 754 double precision floating point cannot represent 33.33 exactly in binary.
   The accumulated rounding error over three additions causes 99.99999...
   Proposes fix: round each input to 2 decimal places before summing, then compare
   sum rounded to 2 decimal places against 100.
4. Priya asks — should the rounding happen on display only or on the actual stored
   value? If we store 33.33333... internally but display 33.33, the stored gram
   calculations will be more accurate but the displayed validation sum might show
   100.00 even when stored sum is 99.99999.
5. Arjun proposes clean solution — store rounded values to 2 decimal places at input
   time. Use parseFloat(value.toFixed(2)) on every user input before storing. This
   ensures stored values, displayed values, and validation sum are all consistent at
   2 decimal precision. Minor precision loss is acceptable for nutrition tracking.
6. Shristi confirms — 2 decimal precision is more than sufficient for macro tracking.
   Users entering 33.33 expect to see 33.33, not 33.3300000001. Priya to implement
   parseFloat(toFixed(2)) rounding at input.
7. Priya reimplements with rounding fix — tests all edge cases: 33.33/33.33/33.34
   sums to 100.00 and shows green. 40/30/29 sums to 99 and shows 99 in red with error
   message. 40/30/30 sums to 100 and enables checkboxes. Also tests persistence —
   refreshes page with invalid state (40/30/29) and confirms values persist with
   error still showing.
8. Shristi verifies all cases — valid sum green, invalid sum red, empty fields red
   borders, checkboxes enabled only on valid. Persistence after refresh confirmed.
   Closing ticket.

**Unique Detail:** The JavaScript floating point precision problem with 33.33 + 33.33
+ 33.34 = 99.99999999. The debate about where to apply rounding — at input time vs
display time vs storage time. The final decision to use parseFloat(toFixed(2)) at
input is a non-obvious but correct solution. This is a real engineering problem that
catches many junior developers.

**Cross References:** Depends on GOAL-006 (custom macro input). The rounding approach
also referenced in GOAL-BUG-003 (macro gram values not updating when calorie changes)

---

### Ticket 4: GOAL-008
**Title:** Select macros to track after validation
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** January 30, 2025
**Resolved:** February 5, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- System must allow user to select/deselect one, two, or all three macros to track
- User can skip tracking any of the macros
- User can track macros only after macros are validated (sum = 100%)
- Macro selection should be applied and reflected in UI within 1 second
- Each macro should have checkbox beside its name
- Title must be clearly displayed as "Track Nutrient" and "Primary goal"
- Checkbox displayed only after macros are validated
- Default state for calorie tracking is enabled (checked by default)
- Disabling a macro does not erase the macro goal value — only removes from tracking
- Once user moves forward or backward the set data must persist
- Only tracked nutrients will be shown in food diary columns

**Conversation Blueprint:**
1. Shristi creates story — checkboxes only visible after GOAL-007 validation passes.
   User can select any combination of carb, fat, protein to track. Only selected
   macros appear in food diary columns. Asks Priya to confirm behaviour when user
   deselects a macro — does it hide from food diary immediately?
2. Priya confirms — deselecting a macro removes it from food diary columns immediately
   per PRD. But the macro goal value is NOT deleted — user can re-select later and the
   goal value reappears. Implements checkbox visibility tied to validation state from
   GOAL-007. Implements macro selection persistence in database.
3. Priya marks complete — asks Shristi to clarify one edge case. If user selects carb
   and protein but not fat, and then sets a new calorie goal that changes macro gram
   values, should the untracked fat macro goal still recalculate even though it is
   not being tracked?
4. Shristi confirms — yes. All macro goals recalculate when calorie changes, even
   untracked ones. If user later re-enables fat tracking, the correct gram value
   should be there. Priya updates implementation. Closing ticket.

**Unique Detail:** Untracked macros still recalculate in background — they are just
hidden from food diary. This is an important data integrity behaviour that prevents
stale values if user re-enables tracking.

**Cross References:** Depends on GOAL-007 (validation). Selected macros feed directly
into NUTR-005 (food diary columns). Referenced in GOAL-BUG-003 (macro grams not
updating when calorie changes)

---

### Ticket 5: GOAL-009
**Title:** View micronutrient list by category with tabs
**Tier:** 1 (8 comments)
**Type:** Story — frontend design
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair
**Created:** January 29, 2025
**Resolved:** February 10, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Ananya Iyer, Priya Nair

**PRD Requirements:**
- All micronutrients placed in different buckets — vitamins, minerals, carbohydrates etc
- Each category in different tabs accessible by switching between tabs
- Micronutrient detail shown only after calorie budget is set by user
- If calorie not set — show message "Please navigate to the Calorie & Goal section,
  and fill in the full detail"
- For each nutrient display: checkbox to select, nutrient name, RDA value
  (system set), MAX value (system set), unit, is custom checkbox
- RDA and MAX values as per age and gender
- From nutrient list Excel: tracked nutrients include Calcium (mg), Fiber total
  dietary (g), Folate DFE (mcg), Iron (mg), Magnesium (mg), Niacin (mg),
  Phosphorus (mg), Potassium (mg), and others
- User can select max 20 nutrients at a time as goal in food diary

**Conversation Blueprint:**
1. Shristi creates story — micronutrient list organised by tabs: vitamins, minerals,
   carbohydrates, fats. Each tab shows list with checkbox, name, RDA, MAX, unit.
   Asks Kabir to design the tab layout.
2. Kabir shares Figma design — tab navigation at top with category names. Each tab
   contains scrollable list of micronutrients with all required columns. Design looks
   clean on desktop. But Kabir raises a concern — on mobile the tab navigation with
   4-5 categories is usable, but he ran a quick test on iPhone screen size. With 40+
   micronutrients across tabs, users are constantly switching tabs looking for specific
   nutrients. The tab paradigm makes navigation feel fragmented.
3. Ananya weighs in — she has been onboarding beta users for testing. Most users are
   confused by tabs. They want to scroll through all nutrients at once to discover what
   they can track. The tab structure hides nutrients and creates friction for first-time
   setup. Recommends a single scrollable list with category labels as section headers.
4. Shristi asks Kabir to propose 3 options with tradeoffs — tabs (current PRD design),
   accordion (collapsed by category, expand to see nutrients), single scroll with
   sticky category headers.
5. Kabir presents 3 options with quick mockups. Tabs — PRD specified but poor mobile
   experience. Accordion — compact but requires extra tap to expand each category.
   Single scroll with sticky headers — most discoverable, easiest to browse, PRD
   compliant if categories are clearly visible. Recommends single scroll.
6. Shristi makes decision — single scroll with sticky category headers. Overrides
   the tab design specified in PRD. Notes this is a better UX decision for a mobile
   first app. Updates PRD note. Kabir to update Figma.
7. Kabir updates Figma with single scroll layout — sticky category headers (Vitamins,
   Minerals, Carbohydrates, Fats), each nutrient row has checkbox, name, RDA, MAX,
   unit clearly laid out. Priya implements the component.
8. Shristi verifies on mobile and desktop — single scroll works perfectly. Nutrients
   discoverable, categories clearly visible, checkbox selection smooth. 20 nutrient
   limit enforced correctly — 21st selection shows message "Maximum 20 nutrients can
   be tracked at once". Closing ticket.

**Unique Detail:** The PRD specified tabs but this is overridden by the team during
implementation based on real mobile usability feedback from Ananya. This is a genuine
design decision that improves the product. The 3-option debate (tabs vs accordion vs
single scroll) with real reasoning for each is what makes this conversation unique.
Also the 20 nutrient limit enforcement edge case.

**Cross References:** Depends on GOAL-SPIKE-002 (RDA research) and GOAL-004 (calorie
budget gate). Referenced in GOAL-010 (select micros to track), GOAL-BUG-004
(micro goals disappearing after refresh)

---

### Ticket 6: GOAL-010
**Title:** Select micronutrients to track with RDA as daily target
**Tier:** 2 (4 comments)
**Type:** Story — backend
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 30, 2025
**Resolved:** February 6, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- User should be allowed to select/deselect micros
- For selected nutrient RDA value should be set and saved as daily target
- RDA value different per age and sex
- Selected micros must persist even after logout/refresh/page change
- Only micros selected here appear in food diary columns
- Max 20 nutrients can be tracked at a time across macro and micro combined
- Deselecting a micro removes it from food diary but does not delete the RDA goal value

**Conversation Blueprint:**
1. Shristi creates story — when user selects a micronutrient checkbox the RDA value
   for their age and gender is automatically set as their daily target. No manual input
   needed. Asks Arjun to confirm the data source — RDA values from GOAL-SPIKE-002
   research table.
2. Arjun confirms RDA values from GOAL-SPIKE-002 research will be used. Notes an
   important question — what happens to the selected micro goals when user updates
   their age or gender in profile? The RDA values are age and gender specific. If a
   30-year-old female becomes 31, Vitamin A RDA remains 700mcg (same age group).
   But if gender changes from female to male, Vitamin A RDA jumps from 700mcg to
   900mcg. Should the selected micro goals auto-update on profile change?
3. Arjun proposes solution — yes, auto-update. When user changes age that crosses an
   age group boundary OR changes gender, all selected micronutrient RDA goals
   recalculate. This is consistent with how EER recalculates on the same triggers.
   Implements auto-recalculation with cascade from profile changes.
4. Shristi approves auto-recalculation approach — confirms persistence requirements
   tested: selected micros survive logout, page refresh, browser close and reopen.
   Closing ticket.

**Unique Detail:** Auto-recalculation of RDA goals when user changes age group or
gender — consistent with EER cascade logic from GOAL-002. This is a subtle but
important product behaviour.

**Cross References:** Depends on GOAL-009 (micro list UI), GOAL-SPIKE-002 (RDA data).
Selected micros feed into NUTR-005 (food diary columns). Referenced in GOAL-BUG-004
(micro goals disappearing after refresh)

---

### Ticket 7: GOAL-011
**Title:** Edit custom micronutrient goal values
**Tier:** 2 (4 comments)
**Type:** Story — backend
**Sprint:** 3
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** January 30, 2025
**Resolved:** February 7, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta

**PRD Requirements:**
- User can edit custom values for micronutrient goals
- Saving and input field validation criteria is same as creation
- Custom value overrides the system-set RDA value
- The is_custom checkbox should be checked when user has set a custom value
- Even if user goes back or to some other page, refreshes or re-logs in,
  same custom value should be present
- User can revert back to RDA value by unchecking is_custom

**Conversation Blueprint:**
1. Shristi creates story — users can override RDA values with custom micronutrient
   goals. For example a doctor-prescribed iron intake of 30mg instead of RDA 18mg.
   Custom value marked with is_custom flag. Asks Arjun to confirm — if user unchecks
   is_custom, does it revert to RDA or clear the value?
2. Arjun confirms revert to RDA on uncheck — the RDA value is always stored in the
   background. Custom value is an override. Removing override reveals the underlying
   RDA. Implements custom value storage with is_custom flag per nutrient per user.
3. Arjun marks complete — asks Shristi to clarify what happens when user changes age
   or gender after setting a custom micro goal. Does the custom value get overridden
   by the new RDA or does the custom value take precedence?
4. Shristi confirms — custom value always takes precedence over RDA, even after profile
   changes. The RDA in background updates for non-custom nutrients but custom values
   are never touched by the system. User owns their custom values completely. Arjun
   updates implementation. Closing ticket.

**Unique Detail:** The layered override system — RDA as base, custom as override.
Profile changes (age/gender) update RDA for non-custom nutrients but never touch
custom values. This is a clean data ownership model.

**Cross References:** Depends on GOAL-010 (select micros), GOAL-SPIKE-002 (RDA data).
The is_custom flag is referenced in GOAL-BUG-004 (micro goals disappearing)

---

### Ticket 8: GOAL-012
**Title:** RDA values by age and gender loaded from research data
**Tier:** 3 (2 comments)
**Type:** Story — backend
**Sprint:** 3
**Priority:** P1
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** January 29, 2025
**Resolved:** February 3, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- RDA and MAX value as per age and gender
- Example: Vitamin A — male 31-50: 900 mcg/day, female 31-50: 700 mcg/day
- Calcium (mg), Fiber total dietary (g), Folate DFE (mcg), Iron (mg),
  Magnesium (mg), Niacin (mg), Phosphorus (mg), Potassium (mg) and others
- Note from nutrient list: Potassium target is in grams but captured in mg

**Conversation Blueprint:**
1. Arjun seeds the RDA and MAX lookup table in Supabase using GOAL-SPIKE-002 research
   data. All micronutrients seeded with values by age group and gender. Notes the
   Potassium unit discrepancy from the nutrient list Excel — target is in grams but
   USDA data is in mg. Has stored in mg and will handle unit conversion in display
   layer. Asks Shristi to confirm this approach.
2. Shristi confirms mg storage with display conversion is correct — avoids precision
   loss from premature conversion. Verifies Vitamin A values for male 31-50 (900 mcg)
   and female 31-50 (700 mcg) match expected values. RDA table seeded correctly.
   Closing ticket.

**Unique Detail:** Potassium unit discrepancy — target in grams but data in mg.
Storage in mg with display layer conversion is the correct approach.

**Cross References:** Directly uses GOAL-SPIKE-002 research data. Powers GOAL-009
(micro list display), GOAL-010 (RDA as daily target), GOAL-011 (custom override)

---

### Ticket 9: NUTR-005
**Title:** Food diary view displaying only tracked nutrients as columns
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 3
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 3, 2025
**Resolved:** February 10, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Only nutrients checked to track should be shown in food diary
- Display message if user has not set goals:
  "To start tracking nutrients in your Food Diary, please set your goals and select
  the nutrients you want to track in the Goal Setting section. Please note setting
  calorie goal is must."
- Food diary in tabular format — food items as rows, nutrients as columns
- Column order: Calorie (if selected), Macros alphabetical (if selected),
  Micros alphabetical (only those selected)
- Max 20 nutrient columns displayed at once
- User can scroll left to right to view all nutrient columns
- Nutrient values in food diary must be non-editable
- Same nutrient columns remain in diary even if user logs off, refreshes or moves
  to another page

**Conversation Blueprint:**
1. Shristi creates story — food diary table structure. Columns determined by nutrients
   selected in goal setting. Column order strictly defined: Calorie first, then macros
   alphabetically, then micros alphabetically. Asks Priya to confirm the component
   design — will nutrient columns be dynamic based on user's goal selections?
2. Priya confirms dynamic columns — the diary component fetches user's tracked nutrients
   from goal settings and builds column headers dynamically. Asks about max 20 column
   horizontal scroll — on mobile with 20 columns the table will require significant
   horizontal scrolling. Is this acceptable UX?
3. Shristi confirms — PRD explicitly allows left to right scroll for nutrients. This
   is a deliberate design decision — Nutrivana tracks more nutrients than other apps
   and the table format is the differentiator. Horizontal scroll is acceptable.
   Priya implements dynamic column generation with horizontal scroll.
4. Shristi verifies — tests with 3 tracked nutrients (calorie, protein, iron) and
   with 20 tracked nutrients. Column order correct. Horizontal scroll smooth. Empty
   diary shows message correctly when no goals set. Values read-only confirmed.
   Closing ticket.

**Unique Detail:** The horizontal scroll with 20 columns is a deliberate product
decision that differentiates Nutrivana from simpler calorie counters. Shristi
explicitly confirms this is intentional UX despite mobile challenge.

**Cross References:** Depends on GOAL-008 (tracked macros) and GOAL-010 (tracked
micros). This is the visual output of all goal setting work. Referenced in
NUTR-BUG-001 (nutrient totals not updating), data model from NUTR-TASK-003

---

### Ticket 10: NUTR-006
**Title:** Select meal type — breakfast lunch dinner snacks supplement
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 3
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 3, 2025
**Resolved:** February 10, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User must be able to select from predefined meal types: Breakfast, Lunch, Snacks,
  Dinner, Supplement
- Food items added must be saved under the selected meal section in food diary
- Supplement section appears ONLY if enabled by user
- Same food or recipe can be part of multiple meals but CANNOT be part of same meal
  again (duplicate prevention)
- Meal type selection must respond instantly without page reload
- All meal type options should be clearly visible
- Food diary should be clearly bifurcated into 3 or 4 parts (4 if supplement enabled)
- Selection should be intuitive and require no more than 1-2 taps/clicks
- User must be able to switch between meal types seamlessly during logging process
- Once user adds food in selected meal all databases should appear instantly

**Conversation Blueprint:**
1. Shristi creates story — meal type selection is the first step before logging food.
   Four always-visible sections (breakfast, lunch, dinner, snacks). Supplement section
   conditional on user enabling it. Asks Priya about the supplement toggle — is it
   a global setting in goal/profile or a per-day toggle in the diary?
2. Priya checks PRD — the supplement section toggle is a persistent setting in user
   preferences. Once enabled it stays enabled across all diary dates unless user
   explicitly disables it. Not a per-day toggle. Confirms with Shristi.
3. Shristi confirms persistent toggle — once a user enables supplements it should
   show on all diary days. Makes sense for users who take supplements daily.
   Priya implements meal section layout with conditional supplement section.
   Notes the supplement implementation connects to NUTR-014 (supplement toggle story)
   which will flesh out the full supplement logging flow.
4. Shristi verifies — four meal sections visible, supplement hidden by default.
   Switching between meal sections instant. Closing ticket. Notes NUTR-014 will
   complete the supplement enable/disable toggle UI.

**Unique Detail:** The supplement toggle is a persistent global setting, not a per-day
toggle. This is a subtle product decision that affects all diary dates. The connection
to NUTR-014 for the full toggle implementation is noted explicitly.

**Cross References:** Referenced in NUTR-014 (supplement toggle and logging),
NUTR-BUG-004 (supplement section showing without toggle enabled — discovered in
Sprint 7 beta)

---

## SUMMARY OF SPRINT 3

| Ticket | Tier | Comments | Reporter | Assignee | Closed |
|---|---|---|---|---|---|
| GOAL-005 | T2 | 4 | Shristi | Arjun | Feb 3 |
| GOAL-006 | T2 | 4 | Shristi | Priya | Feb 4 |
| GOAL-007 | T1 | 8 | Shristi | Priya | Feb 8 |
| GOAL-008 | T2 | 4 | Shristi | Priya | Feb 5 |
| GOAL-009 | T1 | 8 | Shristi | Kabir/Priya | Feb 10 |
| GOAL-010 | T2 | 4 | Shristi | Arjun | Feb 6 |
| GOAL-011 | T2 | 4 | Shristi | Arjun | Feb 7 |
| GOAL-012 | T3 | 2 | Arjun | Arjun | Feb 3 |
| NUTR-005 | T2 | 4 | Shristi | Priya | Feb 10 |
| NUTR-006 | T2 | 4 | Shristi | Priya | Feb 10 |

**Total comments Sprint 3: 46**

---

## KEY STORY THREADS IN SPRINT 3

**Thread 1 — PRD Override: Tabs to Single Scroll**
In GOAL-009 the team overrides the PRD tab design for micronutrient list.
This is the first time in the project where implementation reveals a better UX
than what was specified. Referenced in design retrospective discussions.

**Thread 2 — Floating Point Precision**
GOAL-007 discovers JavaScript floating point with 33.33 + 33.33 + 33.34.
The parseFloat(toFixed(2)) fix is referenced in GOAL-BUG-003 (Sprint 7) where
a similar floating point issue causes macro gram values to not update correctly.

**Thread 3 — Supplement Toggle as Persistent Setting**
NUTR-006 establishes supplement toggle as persistent global setting.
NUTR-014 (Sprint 5) builds the full toggle UI. NUTR-BUG-004 (Sprint 7) is
directly caused by a conditional rendering error in the toggle implementation.

**Thread 4 — 20 Nutrient Maximum**
Established in GOAL-009 and NUTR-005. This limit drives both the goal setting
UI design and the food diary column count. Referenced in usability testing results.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 3

1. Sprint 3 dates: January 29 to February 11, 2025
2. Sprint 3 completes the entire goal setting feature — by end of Sprint 3 users can
   set calorie, macro, and micro goals. This is a major milestone.
3. Comments should reference Sprint 2 work — "now that calorie goal is working
   from GOAL-001..." and "the EER formula is in place so macro calculations will
   use that calorie budget..."
4. GOAL-007 floating point conversation must be technically precise — JavaScript
   IEEE 754, 33.33 in binary is a repeating fraction, accumulated rounding error.
   Arjun must sound like he understands this deeply.
5. GOAL-009 is the richest story in Sprint 3 — four people involved, genuine UX
   debate with real mobile usability concerns, PRD override decision. Make Ananya's
   comment sound like genuine user empathy from someone talking to beta users daily.
6. NUTR-005 and NUTR-006 are the first food diary UI tickets — Priya should sound
   excited about starting the core feature after weeks of goal setting backend work.
7. The Potassium unit discrepancy in GOAL-012 should be mentioned casually —
   a small practical detail that shows attention to real data quality issues.