sprint 8

# Sprint 8 Ticket Definitions — Complete Brief for GPT-4o
## April 15 to April 28, 2025

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions. Sprint 8 continues beta
bug fixes. MVP is live, beta has 200+ users. The team is stabilising the product
while Ananya runs the first marketing campaign. Sprint 8 has 9 bugs and 2 change
requests. By end of Sprint 8 the product is significantly more stable. Public
launch is scheduled for May 1.

---

## SPRINT 8 TICKETS

---

### Ticket 1: NUTR-BUG-002
**Title:** Duplicate food warning not showing when same food added from custom food source
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair
**Created:** April 15, 2025
**Resolved:** April 20, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Same food or recipe CANNOT be part of same meal again on the same date
- Warning must be shown in red when duplicate detected
- Warning disappears after 3 seconds

**Bug Context:**
Found by Priya during systematic beta testing on April 15. The duplicate warning
from NUTR-026 works correctly for USDA foods but silently allows the same custom
food to be added twice to the same meal.

**Conversation Blueprint:**
1. Priya reports bug — the duplicate detection from NUTR-026 only triggers for
   USDA database foods. Custom food, custom recipe, and custom meal sources all
   bypass the duplicate check. Steps to reproduce: create custom food "Homemade
   Daal", add it to breakfast, attempt to add it to breakfast again — no warning
   appears, food gets added twice creating incorrect nutrient totals.
2. Shristi asks — how many beta users have actually double-logged a custom food?
   Priya checks the database — finds 7 users with duplicate custom food entries
   in the same meal. Most appear to be accidental double-taps. Shristi marks P2
   (not P1 because users can manually delete the duplicate entry).
3. Priya traces the duplicate check code from NUTR-026 — the check queries
   food_logs table for existing entries matching food_id + meal_type + date_string.
   The food_id column stores the USDA food database ID for USDA foods. For custom
   foods, the food_logs table stores custom_food_id in a separate column, not in
   food_id. The duplicate check only checks food_id — it never looks at
   custom_food_id, custom_recipe_id, or custom_meal_id.
4. Priya asks Arjun — should the food_logs table schema be refactored to use a
   single food_id with a food_source_type column? Or should the duplicate check
   be extended to check the appropriate ID based on source_type?
5. Arjun recommends extending the duplicate check rather than schema refactoring —
   schema refactoring would require a migration on existing beta user data and
   is risky with 200+ active users. The duplicate check extension is safe and
   targeted. Proposes: check for duplicate based on
   (source_type + appropriate_id + meal_type + date_string) where source_type
   determines which ID column to check.
6. Priya implements extended duplicate check — adds source_type-aware query:
   if source_type is 'usda', check food_id. If 'custom_food', check custom_food_id.
   If 'custom_recipe', check custom_recipe_id. If 'custom_meal', check
   custom_meal_id. All four sources now trigger the red warning on duplicate.
7. Priya also cleans up the 7 users with existing duplicates — removes the
   second entry from each affected user's diary and sends a brief notification
   explaining the fix. Tests all four source types for duplicate detection.
8. Shristi verifies — adds same USDA food twice to breakfast (warning shows),
   adds same custom food twice to breakfast (warning shows), adds same custom
   recipe twice to lunch (warning shows). Tests cross-meal behaviour — same food
   in breakfast AND lunch is still allowed (only same meal is blocked). Closing ticket.

**Unique Detail:** The food_id namespace separation between USDA and custom sources
is the root cause — a design decision from NUTR-009 (USDA serves units) that created
separate ID columns. The source_type-aware duplicate check is cleaner than schema
refactoring. The real user data cleanup (7 affected users) and notification is a
product maturity moment.

**Cross References:** Caused by NUTR-026 (duplicate check) only covering USDA food_id.
The separate custom_food_id namespace from CF-001 and CF-002. The data cleanup
connects to TECH-005 (data isolation — only user's own duplicates cleaned up).

---

### Ticket 2: NUTR-BUG-007
**Title:** Custom meal nutrient values in diary not matching values from creation
**Tier:** 1 (8 comments)
**Type:** Full stack bug
**Sprint:** 8
**Priority:** P1
**Status:** Closed
**Reporter:** Beta user (multiple reports)
**Assignee:** Arjun Mehta, Priya Nair
**Created:** April 15, 2025
**Resolved:** April 22, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Nutrient data added to food diary must match the values saved during custom meal
  creation
- Only meals created by the logged-in user should be accessible

**Bug Context:**
Three beta users report: "The protein in my custom meal 'Post-Workout Shake' shows
differently in my diary than when I created it. I created it with 35g protein but
my diary shows 32g." Shristi verifies — the discrepancy varies between users and
changes over time.

**Conversation Blueprint:**
1. Shristi forwards reports to Arjun — custom meal nutrient values in diary do not
   match values at creation time. Discrepancy varies: some users see 3g protein
   difference, others see no difference, some see it sometimes but not always.
   The inconsistency suggests the values are being recalculated at some point
   rather than using stored values.
2. Arjun investigates the custom meal data model — custom meals are stored as a
   list of ingredients (each being a custom food or USDA food with a quantity).
   When a custom meal is CREATED, the total nutrient values are calculated by
   summing ingredient nutrients. When a custom meal is LOGGED to diary, the
   total nutrient values are recalculated again from current ingredient data.
   This recalculation at logging time is the problem.
3. Arjun identifies the specific failure scenario — user creates custom meal
   "Post-Workout Shake" using custom food "Protein Powder" with 35g protein per
   serving. Later, user EDITS the custom food "Protein Powder" (maybe correcting
   a typo or updating the serving size). The custom food change takes effect from
   the edit date (per CF-007 effective_date logic). But the custom meal recalculates
   at logging time using the CURRENT ingredient values, not the values at meal
   creation time. So if Protein Powder was edited after the meal was created, the
   meal nutrient values shift.
4. Priya asks — should custom meal nutrient values be FROZEN at creation time
   (snapshot) or LIVE calculated from current ingredient values? Both have valid
   arguments. Frozen: diary always shows what you intended when you created the meal.
   Live: diary shows the most accurate current values if you improve an ingredient.
5. Shristi makes the product decision — FROZEN at creation time. The PRD says
   "nutrient data added to diary must match values saved during custom meal creation."
   The word "saved during creation" is explicit. Users who create a meal for a
   specific nutritional purpose need those values to remain consistent. If ingredient
   values change, the user should update the custom meal explicitly.
6. Arjun implements the fix — when a custom meal is SAVED (created or edited), the
   total nutrient values are calculated and stored as a snapshot on the custom_meal
   record. When the meal is logged to diary, the snapshot values are used directly
   without recalculation. The live ingredient data is only used to update the
   snapshot when the meal is explicitly saved again.
7. Priya updates the food diary logging flow — POST /food-logs for custom meal now
   copies the snapshot_nutrients from custom_meals table directly, not recalculating
   from ingredients. Tests with a custom meal created with 35g protein, editing
   an ingredient, logging the meal — confirms 35g protein still appears in diary.
8. Shristi verifies with the three beta users' exact scenarios — confirms values
   now match creation time. Also tests the edge case: if user explicitly edits
   the custom meal itself (not just an ingredient) — the snapshot updates on
   save, and FUTURE diary logs use the new snapshot. Past logs are unaffected
   (they already stored the nutrient values directly from the PATCH endpoint).
   Notifies the three beta users. Closing ticket.

**Unique Detail:** The FROZEN vs LIVE debate is a genuine product philosophy question.
The PRD explicitly says "match values saved during creation" — frozen wins. The
effective_date versioning from CF-007 is what creates the inconsistency — ingredient
edits change values but the custom meal is not aware. The snapshot approach is
the correct data integrity solution.

**Cross References:** Connected to CF-007 (effective_date versioning for custom
foods). The snapshot pattern is similar to goal_snapshots from NUTR-TASK-003.
The PRD compliance argument ("values saved during creation") is the deciding factor.

---

### Ticket 3: NUTR-BUG-008
**Title:** Search results from previous food source still showing when source changed
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair
**Created:** April 16, 2025
**Resolved:** April 21, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- If user changes source or navigates away mid-process, previous input must be
  cleared and user must re-search and re-select
- Search results must be cleared when source changes

**Bug Context:**
Found by Priya on April 16. User searches "chicken" in USDA source, sees results,
then switches source to Custom Food — the search results panel still shows the
USDA chicken results briefly before clearing, sometimes staying visible for 2-3
seconds. Some users have tapped on a USDA result from the stale list while expecting
custom food results.

**Conversation Blueprint:**
1. Priya reports bug — switching food source does not immediately clear search
   results. When user switches from USDA to Custom Food, the USDA search results
   remain visible for a noticeable period (sometimes until user types in the new
   search field). Steps to reproduce: search "chicken" in USDA source, see 10
   results, switch to Custom Food source — results panel still shows USDA chicken
   results for 1-3 seconds.
2. Arjun reviews the reusable search component from NUTR-011 — the source prop
   change triggers a re-render. The search results state (results array) is cleared
   in a useEffect that watches the source prop. But the useEffect has a timing issue —
   React batches state updates and the results clearing happens after the render,
   not before. So the component briefly renders with old source but new results
   cleared state, during which the old results are still visible.
3. Priya suggests a different approach — instead of clearing in useEffect after
   render, clear the results synchronously in the source onChange handler BEFORE
   the state update. This ensures the component renders with empty results
   simultaneously with the source change.
4. Arjun explains — the issue is deeper. The NUTR-BUG-003 fix (useEffect cleanup
   for serving unit) was a different component. This bug is in the search component
   itself. The useEffect cleanup approach from NUTR-BUG-003 should be applied here
   too but the search component was not updated when NUTR-BUG-003 was fixed.
5. Shristi notes this is the third time a fix in one component was not applied to
   a related component. NUTR-BUG-001 fixed diary totals but missed analysis
   (AN-BUG-003). NUTR-BUG-003 fixed serving unit but missed search component
   (this bug). Asks team to do a comprehensive audit of all components that share
   the same patterns and ensure fixes are applied everywhere.
6. Priya implements the fix — moves results clearing to synchronous event handler
   on source change. When source dropdown value changes, results array is cleared
   immediately (synchronous state update) before any async fetch begins. Also
   applies the same fix to search input clearing on source change.
7. Arjun conducts the audit Shristi requested — reviews all useEffect cleanup
   patterns across the codebase. Finds one more instance in the date picker
   component that could have a similar timing issue under specific conditions.
   Fixes all instances proactively.
8. Shristi verifies — switches source while results are showing: results clear
   instantly (no flash of old results). Tests all 4 source types: USDA → custom
   food, custom food → custom recipe, custom recipe → USDA, custom meal → USDA.
   All clear instantly. Closing ticket.

**Unique Detail:** The pattern of fixes not being applied to related components is
identified explicitly by Shristi as a recurring issue — NUTR-BUG-001/AN-BUG-003,
NUTR-BUG-003/NUTR-BUG-008. The audit request and proactive fixing of the date
picker is a team maturity moment.

**Cross References:** Related to NUTR-BUG-003 (same useEffect cleanup pattern).
Related to NUTR-BUG-001/AN-BUG-003 (fix not applied everywhere). The reusable
search component from NUTR-011.

---

### Ticket 4: NUTR-BUG-009
**Title:** DV% showing decimal value instead of dash for nutrients less than 1%
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** April 16, 2025
**Resolved:** April 20, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- In case the nutrient DV% is less than 1 then '-' should be shown in DV%
- All nutrient values displayed in nutrient breakdown table on adjust portion page
- DV% calculated based on 2000 calorie diet

**Bug Context:**
Shristi finds during QA on April 16. On the adjust portion page, some micronutrients
are showing "0.47%" in the DV% column instead of '-'. The PRD requires that any
DV% less than 1 should show '-' instead of a decimal value.

**Conversation Blueprint:**
1. Shristi reports bug — on adjust portion page for foods with very low micronutrient
   content, the DV% column shows decimal values like "0.47%" and "0.83%" instead
   of '-'. Example: selecting 100g lettuce shows Vitamin B12 DV% as "0.00%" and
   Zinc DV% as "0.47%" — both should show '-' per PRD.
2. Priya reviews the DV% display logic from NUTR-009 — the code checks
   `if (dvPercent < 1) return '-'`. This should work. Priya investigates the
   specific case Shristi reported — Zinc DV% of 0.47%. The raw calculation is:
   0.47mg zinc in 100g lettuce / 11mg zinc daily value × 100 = 4.27% which
   is above 1 and should NOT show '-'. But Shristi sees 0.47%.
3. Priya traces further — the 0.47% is not the Zinc DV%. It IS the Zinc actual
   amount (0.47mg) being displayed in the wrong column. There are two separate bugs:
   (1) a column alignment issue where actual mg values appear in the DV% column for
   some nutrients, AND (2) the original < 1 dash rule not applying to the actual DV%
   calculation for some edge cases.
4. Arjun helps trace the column alignment bug — the nutrient table renders columns
   dynamically from an array. For most nutrients the array order is [name, amount,
   unit, dv_percent]. For some micronutrients with unusual data structure in the
   USDA database, the array comes back in a different order [name, dv_percent, unit,
   amount]. The dynamic column renderer does not validate column positions.
5. Priya asks — how many nutrients in the USDA database have this unusual data
   structure? Arjun queries and finds 23 micronutrients out of 40+ tracked have
   the reversed column order in the USDA import. This is a data normalisation
   issue from NUTR-TASK-001 (USDA import).
6. Arjun fixes the USDA import normalisation — adds explicit column mapping using
   nutrient_type_id from USDA schema instead of relying on array position. All
   23 affected nutrients now return data in the correct order. Priya also adds
   defensive column position validation in the frontend renderer.
7. Priya also fixes the < 1 dash rule — the original check `dvPercent < 1` correctly
   catches most cases. But for nutrients where DV% is calculated as a very small
   number (like 0.002%), floating point makes the value display as "0.00%" instead
   of being caught as < 1. Applies the same parseFloat(toFixed(2)) rounding from
   GOAL-007 to DV% before the < 1 check.
8. Shristi verifies across 20 different foods — all DV% values below 1% now show
   '-'. Column alignment correct for all 40+ micronutrients. Tests on foods with
   extreme micro values (oysters for zinc, liver for vitamin A) to ensure high
   values still display correctly. Closing ticket.

**Unique Detail:** Two separate bugs discovered — column alignment (array order
inconsistency from USDA import) AND dash rule (floating point rounding before
comparison). The USDA import normalisation fix affects 23 out of 40+ micronutrients.
The parseFloat(toFixed(2)) fix from GOAL-007 recurs here — the same rounding
problem appears in multiple calculation contexts.

**Cross References:** USDA import normalisation from NUTR-TASK-001. The dash rule
first established in NUTR-009 (adjust portion page). The parseFloat(toFixed(2))
pattern from GOAL-007. Related to NUTR-015 (diary column dash rule) and AN-BUG-005
(Sprint 9 — DV% rounding in analysis).

---

### Ticket 5: NUTR-BUG-010
**Title:** Per-meal nutrient total row appearing after wrong food item
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** April 17, 2025
**Resolved:** April 22, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Total nutrient consumed per meal displayed at end of last food item in that meal
- Total nutrient consumed per meal should be bold
- No color coding for meal totals

**Bug Context:**
Shristi finds during QA. When foods are added to a meal in non-sequential order
(e.g. adding a snack item, then a breakfast item, then another snack item), the
meal total row appears in the wrong position — showing after the 2nd food instead
of after the last food in that meal.

**Conversation Blueprint:**
1. Shristi reports bug — the per-meal total row from NUTR-018 appears in the wrong
   position. Steps to reproduce: add Apple to Snacks, add Egg to Breakfast, add
   Banana to Snacks. Expected: Breakfast section shows [Egg, Total]. Snacks section
   shows [Apple, Banana, Total]. Actual: Snacks section shows [Apple, Total, Banana]
   with total appearing after the 2nd Snacks item instead of the last.
2. Priya traces the meal grouping logic from NUTR-018 — the diary component renders
   food items grouped by meal_type. The grouping uses the food_logs array which is
   ordered by created_at timestamp (insertion order). When Apple is added first and
   Banana is added later with Egg in between, the array is [Apple, Egg, Banana].
   The grouping algorithm groups by meal_type but preserves insertion order within
   each group. The total row is appended after the LAST item in the array that
   belongs to that meal — which is Banana (correct). But Priya finds the bug is
   different from the report.
3. Priya reproduces more carefully — the bug occurs specifically when EDITING
   a food's portion size. When Priya edits Apple in Snacks, the PATCH API returns
   the updated Apple record and the frontend optimistically updates the diary state.
   The state update for editing moves the edited item to the END of the food_logs
   array (because the state update replaces the item by appending updated version
   and removing the original). Now the Snacks array has [Banana, Apple(updated)]
   instead of [Apple, Banana]. Total still appears after Apple but Apple is no
   longer the last Snacks item in visual order.
4. Arjun explains the optimistic update bug — the edit state update in NUTR-019
   removes the original item from its position in the array and appends the updated
   version at the end. This changes the visual order of items within a meal every
   time an edit is made. The fix is to UPDATE the item IN PLACE (preserving its
   array position) rather than remove-and-append.
5. Priya asks — will the in-place update also fix the meal total position? Yes —
   if array positions are preserved, the meal grouping renders in the original
   insertion order and the total always appears after the last item in that order.
6. Shristi asks — should food items within a meal always show in insertion order,
   or should they be sorted by name or by time of addition? The PRD does not specify.
   Suggests alphabetical sort within each meal for better UX — users can predict
   where a food will appear.
7. Priya implements both fixes — in-place array update for edits (preserves position),
   alphabetical sort by food_name within each meal group. The total row always renders
   after the last alphabetically sorted item in each meal. Tests with additions and
   edits in various orders.
8. Shristi verifies — adds foods in random order across meals, confirms each meal
   section is alphabetically sorted, total appears after the last food in each meal.
   Tests edit: edits a food's portion, confirms it stays in its alphabetical position.
   Tests delete: removes middle food, total shifts up correctly. Closing ticket.

**Unique Detail:** The bug is actually in the optimistic edit update (remove-and-append
vs in-place update) not in the meal grouping algorithm itself. The alphabetical sort
within meals is a UX improvement added proactively during the fix — turning a bug
fix into a feature improvement.

**Cross References:** Caused by optimistic edit update in NUTR-019 (edit logged
item). Connected to NUTR-018 (meal total rendering). The in-place update pattern
is a best practice that prevents future ordering bugs.

---

### Ticket 6: GOAL-BUG-001
**Title:** Target date not recalculating when user manually changes calorie budget
**Tier:** 1 (8 comments)
**Type:** Backend bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Beta user (reported to Shristi)
**Assignee:** Arjun Mehta
**Created:** April 15, 2025
**Resolved:** April 21, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- If user changes target calorie (manually): required deficit/surplus should change,
  target date should change, no of days left should change
- Weight maintenance calorie should NOT change
- For weight loss — new required deficit = WMC - new target calorie
- No of days left = (current weight - goal weight) × 7700 / new required deficit
- Current date + no of days left = target date

**Bug Context:**
Beta user BT-089 reports: "I lowered my calorie goal to lose weight faster. The
app confirmed my calorie budget changed but my target date didn't move — it still
shows the same date as before."

**Conversation Blueprint:**
1. Shristi forwards BT-089's report to Arjun — user manually lowered calorie goal
   from 1800 to 1600 kcal. Expected: target date should move closer (fewer days
   to goal because higher deficit). Actual: target date unchanged. The number of
   days left also unchanged.
2. Arjun reproduces and confirms — calorie budget updates correctly in database
   when user saves. The EER/WMC value is unchanged (correct per PRD). The required
   deficit updates correctly (new deficit = WMC 2200 - new calorie 1600 = 600 kcal).
   But the no_of_days_left and target_date columns in the database are NOT being
   updated after the deficit recalculation.
3. Arjun traces the dependency cascade from GOAL-003 — the cascade should be:
   calorie changes → deficit recalculates → days_left recalculates → target_date
   recalculates. The deficit recalculation is correct (step 2). But steps 3 and 4
   are in a separate database function that is only called when the user saves the
   calorie goal page with all fields. The manual calorie change happens via a
   separate PATCH endpoint that only updates the calorie_budget column and triggers
   the deficit recalculation but NOT the days_left/target_date recalculation.
4. Arjun identifies the missing cascade — the deficit recalculation function
   (from GOAL-003) correctly calculates the new deficit. But after calculating
   the deficit, it does NOT call the days_left and target_date recalculation
   functions. These functions are only called from the full goal-save flow, not
   from the manual calorie edit flow.
5. Shristi asks — looking at the PRD dependency matrix from GOAL-003, how many
   other cascade paths might have similar gaps? The GOAL-003 dependency matrix
   was documented in code comments. Arjun reviews it.
6. Arjun checks the dependency matrix — finds two more cascade paths with the same
   gap: (1) when goal_weight changes, target_date should update but doesn't in the
   quick-edit flow. (2) when current_weight changes, WMC should update but target
   date doesn't cascade after. Both have the same pattern — partial cascade in
   quick-edit flows.
7. Arjun implements the complete cascade — refactors the recalculation logic into
   a single comprehensive function that always runs the full cascade regardless
   of which trigger initiated it. Any change to any calorie-related variable now
   flows through this single function ensuring all dependent values update. Tests
   all three trigger paths.
8. Shristi verifies with BT-089's scenario — lowers calorie from 1800 to 1600,
   confirms target date moves correctly to an earlier date. Also tests goal weight
   change and current weight change — both cascade correctly now. Notifies BT-089.
   Closing ticket.

**Unique Detail:** The cascade gap — partial cascade in quick-edit flows vs full
cascade in the save flow. Refactoring into a single comprehensive cascade function
is the correct architectural fix. The systematic audit finding two more gaps shows
the cascade pattern was inconsistently implemented across all calorie-related
edit paths.

**Cross References:** Caused by incomplete cascade implementation in GOAL-003
(required deficit calculation). The dependency matrix documented in GOAL-003 code
comments is what enables finding the two additional gaps. Related to GOAL-BUG-002
(Sprint 7) which had a similar missing trigger pattern.

---

### Ticket 7: GOAL-BUG-005
**Title:** BMR warning shown for below-BMR calorie but goal saved incorrectly
**Tier:** 1 (8 comments)
**Type:** Backend bug
**Sprint:** 8
**Priority:** P1 (health critical)
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta
**Created:** April 16, 2025
**Resolved:** April 22, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- For system-calculated calorie below BMR: show error, DO NOT set calorie goal,
  remove goal weight and target date
- For USER-DEFINED calorie below BMR: show warning but ALLOW user to save
- Both cases show the message: "Calorie budget below BMR [value]. Eating less than
  BMR calories could cause excessive loss of lean body mass"

**Bug Context:**
Shristi finds during systematic QA on April 16. Testing the user-defined below-BMR
case (should show warning but allow save): enters a calorie value below BMR, warning
appears correctly, clicks save — goal is saved correctly. BUT she then tests going
back and re-opening the goal page — the goal weight and target date fields are BLANK
even though they should only be cleared for the SYSTEM-CALCULATED case, not the
user-defined case.

**Conversation Blueprint:**
1. Shristi reports the bug — the two-path BMR validation from GOAL-004 is partially
   broken. User-defined below-BMR case: (a) warning shows correctly (pass), (b) user
   can save the goal (pass), (c) BUT going back and reopening shows blank goal weight
   and target date fields (fail). The clearing of goal weight and target date should
   only happen for the system-calculated case, not the user-defined case.
2. Arjun reviews the BMR validation implementation from GOAL-004 — the code correctly
   implements two paths in the save handler. But during the Sprint 6 performance
   refactoring (TECH-004), the save endpoint was reorganised and a regression was
   introduced. The goal_weight and target_date clearing code was moved to a generic
   "post-save cleanup" function that runs after ALL saves, not just system-calculated
   saves. This cleanup function checks if calorie < BMR and clears the fields —
   regardless of whether it was system-calculated or user-defined.
3. Arjun traces the regression commit — finds the exact commit from Sprint 6 where
   the save endpoint was refactored for performance. The original GOAL-004 code had
   the clearing logic inside a conditional block. After refactoring, the clearing
   logic was extracted to a separate function that lost the conditional context.
4. Shristi asks — this is a regression from a refactoring in Sprint 6. Does this mean
   the GOAL-004 tests did not catch the regression? Arjun confirms — GOAL-004 tests
   verified the initial implementation but no regression tests were added for the
   refactored version.
5. Shristi asks Arjun to add regression tests for BMR validation BEFORE fixing the
   code. Tests first, then fix — to ensure the fix itself is verified. Important
   for a health-critical feature.
6. Arjun writes tests first — covers all BMR scenarios: system-calculated below BMR
   (fields cleared), user-defined below BMR (fields preserved), system-calculated
   above BMR (normal flow), user-defined above BMR (normal flow). All four tests
   fail initially confirming the regression.
7. Arjun fixes the clearing logic — moves it back inside the conditional block that
   only fires for system-calculated cases. User-defined saves never trigger field
   clearing regardless of BMR comparison. All four tests now pass.
8. Shristi verifies all four scenarios manually — system-calculated below BMR (fields
   clear, goal not saved), user-defined below BMR (warning shows, fields preserved,
   goal saved), both above BMR cases normal flow. Closing ticket. Notes this is
   the first time tests were written before the fix — a good practice that should
   be adopted for all health-critical features.

**Unique Detail:** Tests-first approach for a health-critical regression is a product
maturity moment — Shristi requires tests before the fix. The regression was introduced
by a performance refactoring in Sprint 6 that lost the conditional context. The
specific failure (goal weight/target date cleared for user-defined case) is exactly
what GOAL-004 was designed to prevent.

**Cross References:** Regression from Sprint 6 TECH-004 refactoring. Caused by
GOAL-004 (BMR validation two-path logic). The tests-first approach becomes a team
standard for health-critical features going forward.

---

### Ticket 8: CF-BUG-003
**Title:** Calorie field not marked as mandatory with asterisk in custom food create form
**Tier:** 1 (8 comments)
**Type:** Frontend design bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Kabir Sharma
**Created:** April 17, 2025
**Resolved:** April 21, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Priya Nair

**PRD Requirements:**
- Calorie value is mandatory to be filled
- Calorie should have asterisk (*) to show it is mandatory
- All mandatory fields should be marked by asterisk

**Bug Context:**
Shristi finds during systematic QA of the custom food create form. The food name
and serving size fields correctly show asterisks indicating mandatory. The calorie
field does NOT show an asterisk despite being mandatory. Users could reasonably
assume calorie is optional.

**Conversation Blueprint:**
1. Shristi reports bug — custom food create form from CF-001/CF-002: food name field
   shows asterisk (correct), serving value field shows asterisk (correct), serving
   unit field shows asterisk (correct). Calorie nutrient field in the nutrient entry
   section does NOT show asterisk despite PRD explicitly requiring it. The calorie
   field validates correctly (blocks save if empty) but gives no visual cue that it
   is mandatory.
2. Kabir checks the Figma — the calorie asterisk IS present in the design file. This
   is an implementation gap — the design had it, the code missed it. Asks Priya to
   explain why the calorie asterisk was not implemented.
3. Priya reviews her CF-002 implementation — the nutrient list is rendered
   dynamically from a list of nutrient definitions. Most nutrients are optional.
   The is_mandatory flag exists in the nutrient definition data but was not
   used in the rendering logic to add the asterisk. The calorie nutrient entry
   in the database has is_mandatory = true but the frontend renderer never checks
   this flag.
4. Shristi asks — are there any other nutrients that might be marked as mandatory
   in the database that are also not showing asterisks? Priya queries — calorie
   is the only nutrient with is_mandatory = true. All other nutrients are optional.
5. Kabir confirms the design — only calorie gets an asterisk in the nutrient entry
   section. All other nutrients are deliberately optional so users can fill in
   only what they know. The fix is simple: add a conditional asterisk render based
   on the is_mandatory flag in the nutrient definition.
6. Priya implements the fix — adds `{nutrient.is_mandatory && <span>*</span>}` to
   the nutrient row renderer. Tests that only the calorie row shows the asterisk
   and all other nutrient rows do not.
7. Priya also adds a visible mandatory label below the calorie input: "Required"
   in small red text, consistent with the mandatory style on the food name and
   serving fields. Provides visual reinforcement beyond just the asterisk.
8. Shristi verifies — calorie field shows asterisk and "Required" label. All other
   nutrients show no asterisk. Attempts to save without calorie — blocked with
   "please enter mandatory field" message highlighting calorie. Closing ticket.

**Unique Detail:** The is_mandatory flag exists in the database but was never
used in the rendering logic — a classic gap between data model and UI implementation.
The "Required" label addition is a proactive UX improvement beyond just fixing the
missing asterisk. Simple bug but important for usability clarity.

**Cross References:** Caused by CF-002 (nutrient entry implementation) not using
the is_mandatory flag. Connected to CF-003 (save validation) which correctly blocks
empty calorie but gives no visual warning about why.

---

### Ticket 9: CF-BUG-004
**Title:** Add button not appearing on create custom food page after saving
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** April 17, 2025
**Resolved:** April 21, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Once saved, Add button should be present to directly add from create page
- Once saved no field can be edited
- On going back after saving user should navigate to custom food menu page

**Bug Context:**
Shristi finds during QA. After successfully saving a custom food on the create page,
the page transitions to read-only mode correctly (all fields greyed out) but the
Add button does NOT appear. The only way to add the new food to the diary is to
navigate to the custom food menu page manually and find it there.

**Conversation Blueprint:**
1. Shristi reports bug — after saving a custom food the create page should show
   an Add button so user can immediately add the new food to their diary without
   extra navigation (per PRD). The save succeeds (food visible in menu), fields
   become read-only (correct), but no Add button appears. The save button itself
   disappears (correct) but nothing replaces it.
2. Priya reviews the save flow implementation from CF-003 — the save handler:
   (1) validates mandatory fields, (2) calls POST /custom-foods API, (3) on success
   sets is_saved = true in component state, (4) rendering logic: if is_saved show
   read-only fields. The Add button was supposed to show when is_saved is true.
   Priya checks the rendering code — the Add button conditional is
   `if (is_saved && custom_food_id)`. Both conditions should be true after save.
3. Priya debugs with console.log — is_saved is true after save. But custom_food_id
   is undefined. The POST API call returns the created custom food record including
   its new ID. But the custom_food_id state variable is never set from the API
   response. The API response data is received but not stored in component state.
4. Priya traces — the save handler: `const response = await POST(...)` — the
   response object is received. But the next line is `setIsSaved(true)` — there
   is no line saving the custom_food_id from the response. This is a simple
   omission — the API call was implemented without extracting the returned ID.
5. Shristi asks — what happens when user taps the missing Add button once it is
   fixed? It should open the adjust portion page for the new food pre-populated
   with the new food's data. Priya confirms this is the expected flow — linking
   directly to adjust portion with the new custom_food_id.
6. Priya implements the fix — after successful save, extracts custom_food_id from
   API response and stores in state. The Add button now appears correctly. Tapping
   it navigates to adjust portion page pre-populated with the new custom food data.
7. Priya also adds a subtle success animation — when save completes and the Add
   button appears, a brief green flash on the button draws user attention to the
   newly available action. This was Kabir's suggestion from a quick design review.
8. Shristi verifies — saves new custom food "Masala Oats" (testing Indian food
   use case from the NUTR-TASK-001 gap), Add button appears with green flash,
   taps Add, reaches adjust portion page with Masala Oats pre-filled. Adds to
   breakfast diary — logs correctly with custom nutrient values. Closing ticket.

**Unique Detail:** The missing ID extraction is a simple omission — API response
received but ID not stored. The Masala Oats test case explicitly references the
Indian food gap from NUTR-TASK-001 (Sprint 2), showing the custom food feature
is now fulfilling its original purpose. The success animation is a small UX
improvement added during the fix.

**Cross References:** Caused by CF-003 (save flow) not extracting returned ID.
The Masala Oats test case closes the circle from NUTR-TASK-001 Indian food gap
(Sprint 2) → Custom Food feature (Sprints 5-6) → User can now add Indian food.

---

### Ticket 10: AN-CR-001
**Title:** Bar graph colors and design confusing — full redesign following user feedback
**Tier:** 1 (8 comments)
**Type:** Change request
**Sprint:** 8
**Priority:** P1
**Status:** Closed
**Reporter:** Ananya Iyer
**Assignee:** Kabir Sharma, Priya Nair
**Created:** April 15, 2025
**Resolved:** April 26, 2025
**Participants:** Ananya Iyer, Kabir Sharma, Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Bar graph visual must clearly communicate actual vs target
- All nutrient value and unit must be clearly visible
- Bar graph loads within 2 seconds
- Updates within 1 second after food changes

**Context:**
This is the planned follow-up to the AN-002 emergency patch from Sprint 6. The
Option C patch (explicit numbers) helped but Ananya's continued user research
during beta shows the bar graph is still one of the most confusing elements
for new users.

**Conversation Blueprint:**
1. Ananya brings compiled beta feedback — 12 of 40 beta users surveyed say the
   analysis bar graph is "confusing" or "hard to understand." Direct quotes:
   "I don't know if the colored part is what I ate or what I need to eat."
   "The bar being full doesn't mean I'm done eating, right?" The Option C patch
   (explicit numbers) helped but users still struggle with the bar visual itself.
   Ananya formally requests a redesign — this is the AN-CR-001 follow-up from
   AN-002.
2. Kabir has been preparing redesign options since AN-002 was patched in Sprint 6.
   Presents two complete redesign options with Figma mockups. Option 1: Progress bar
   approach — bar fills from left as you eat towards target. 0% = empty bar, 100% =
   full green bar, 150% = full bar overflowing into red zone. Users' natural mental
   model of progress bars. Option 2: Remaining approach — bar shows what's LEFT,
   shrinks as you eat. Full bar = empty stomach, empty bar = goal complete. More
   unusual but possibly clearer for over-eating scenarios.
3. Ananya evaluates both with 5 quick user tests (30 minutes, informal). Option 1
   (progress bar) — all 5 users immediately understand "bar fills as you eat."
   Option 2 (remaining) — 3 out of 5 confused by shrinking bar concept. Option 1
   clearly wins on immediate comprehension.
4. Shristi approves Option 1 — progress bar from 0% to 100%. Notes it requires
   rethinking the over-100% case: how does Option 1 show overeating visually?
   Kabir proposes: 0-99% = yellow bar fills normally. At 100% = bar turns green and
   is full. 101%+ = red segment extends PAST the 100% marker (like a thermometer
   overflowing). This shows completion AND overage simultaneously.
5. Kabir presents the over-100% thermometer metaphor — small 100% marker line on
   the bar. Below: yellow fill. At: green full bar. Above: red extension past the
   marker. User sees both "I hit my goal" (green bar) AND "I went over" (red extension).
   Ananya immediately approves — intuitive and visually clear.
6. Priya implements the redesign — new bar component with: yellow fill from 0% to
   actual%, cap at 100% with a marker line, green colour when actual reaches 100%,
   red extension segment for amounts over 100%. Maintains the explicit number labels
   from Option C (keeping what worked). Performance: same rendering speed as before.
7. Ananya tests redesign with 8 beta users — all 8 correctly identify "the bar fills
   as you eat" without explanation. Over-eating case (thermometer overflow) understood
   by 7 of 8. The 1 user who did not understand the red extension immediately
   understood after reading the "over target" text label. Substantial improvement
   from the original 4/5 confusion rate.
8. Shristi approves — deploys to beta. Sends update to all 200+ beta users:
   "We've improved the Analysis visualisation based on your feedback." Links to
   in-app changelog. Kabir updates Figma documentation for future reference.
   Closing ticket.

**Unique Detail:** The progress bar mental model (fill up towards goal) wins over
the remaining bar (shrink as you eat) based on real user testing. The thermometer
metaphor for over-100% (green full bar + red extension) is elegant — shows both
achievement (full green bar) and excess (red overflow). The direct user testing
with specific numbers (5 users in comment 3, 8 users in comment 7) shows a
data-driven design process.

**Cross References:** Follow-up from AN-002 (Sprint 6 emergency patch) and AN-BUG-002
(Sprint 7 CSS overflow). The redesign incorporates fixes for both. Referenced in
marketing emails as "improved based on your feedback." AN-CR-002 is the companion
label copy change.

---

### Ticket 11: AN-CR-002
**Title:** Add clear remaining vs over target label below bar graph
**Tier:** 1 (8 comments)
**Type:** Change request
**Sprint:** 8
**Priority:** P2
**Status:** Closed
**Reporter:** Ananya Iyer
**Assignee:** Kabir Sharma, Priya Nair
**Created:** April 15, 2025
**Resolved:** April 24, 2025
**Participants:** Ananya Iyer, Kabir Sharma, Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Display: actual nutrient consumed, target nutrient, (actual/target)% rounded to
  2 decimal points, amount left/over |target-actual|
- If actual > target: label says "over"
- If actual < target: label says "left"

**Bug Context:**
Companion to AN-CR-001. Beta users who understand the bar graph still struggle
with interpreting the "left/over" text label. "Left" is ambiguous — does it mean
"remaining" (good: I have calories left to eat) or "leftover" (neutral: excess
calories)?

**Conversation Blueprint:**
1. Ananya reports text label confusion — the current label shows "Xg left" for
   under-target and "Xg over" for over-target. Multiple beta users ask: "When it
   says 35g protein left, does that mean I should eat more protein or that I ate
   35g as a leftover?" The word "left" has two meanings in English — remaining
   (to be consumed) and leftover (excess). In a nutrition context it is always
   "remaining" but users are confused.
2. Kabir proposes three alternative label copy options with examples:
   Option A: "35g remaining" / "35g over target" — clear but longer
   Option B: "35g to go" / "35g over target" — friendly but "to go" might feel odd
   Option C: "Need 35g more" / "35g exceeded" — most explicit but verbose
   Recommends Option A as clearest while remaining concise.
3. Ananya tests all three options with 5 users (informal 15-minute test). Option A
   (remaining/over target) — 5/5 immediately understand both states. Option B (to go)
   — 4/5 understand "to go" but 1 user thinks it means takeaway food (comic but real).
   Option C (need more/exceeded) — 5/5 understand but users say it feels "bossy."
   Option A wins unanimously on clarity and tone.
4. Shristi approves Option A — "Xg remaining" for under-target, "Xg over target"
   for over-target. Notes the label should also update consistently in the food
   diary comparison section (NUTR-017) for terminology consistency across the app.
   Same words in both places.
5. Kabir points out a subtle issue — the current PRD says `|target-actual|` for
   the displayed amount. For over-target this gives the same number whether it is
   displayed as "remaining" or "over target." But the display should always be a
   positive number regardless. Confirms implementation is already using absolute
   value — no change needed there.
6. Priya implements label copy changes — replaces "left" with "remaining", replaces
   "over" with "over target" in both analysis section AND food diary comparison
   section (NUTR-017) for consistency. Tests in both locations.
7. Ananya verifies label copy in both analysis and diary — "remaining" and "over target"
   appear consistently. Tests with nutrient at exactly 100% — shows "0g remaining"
   which correctly conveys goal met with nothing left. Tests over-target — shows
   "35g over target" clearly.
8. Shristi approves. Notes that updating both analysis and diary in the same ticket
   ensures terminology is consistent across the app — a small UX detail that matters
   for product polish. Closing ticket.

**Unique Detail:** The dual meaning of "left" in English (remaining vs leftover)
is a real copy writing trap. The informal user testing with 5 users catches the
"to go = takeaway food" misreading — a genuinely funny but valid UX concern.
The consistency update across both analysis and diary (same terminology everywhere)
is a product polish decision.

**Cross References:** Companion to AN-CR-001 (bar graph redesign). The label copy
is also updated in NUTR-017 (food diary color comparison) for consistency. The
absolute value handling in PRD (|target-actual|) is confirmed as already correct.

---

## SUMMARY OF SPRINT 8

| Ticket | Tier | Comments | Type | Priority | Closed |
|---|---|---|---|---|---|
| NUTR-BUG-002 | T1 | 8 | Bug | P2 | Apr 20 |
| NUTR-BUG-007 | T1 | 8 | Bug | P1 | Apr 22 |
| NUTR-BUG-008 | T1 | 8 | Bug | P2 | Apr 21 |
| NUTR-BUG-009 | T1 | 8 | Bug | P2 | Apr 20 |
| NUTR-BUG-010 | T1 | 8 | Bug | P2 | Apr 22 |
| GOAL-BUG-001 | T1 | 8 | Bug | P2 | Apr 21 |
| GOAL-BUG-005 | T1 | 8 | Bug | P1 | Apr 22 |
| CF-BUG-003 | T1 | 8 | Bug | P2 | Apr 21 |
| CF-BUG-004 | T1 | 8 | Bug | P2 | Apr 21 |
| AN-CR-001 | T1 | 8 | Change Request | P1 | Apr 26 |
| AN-CR-002 | T1 | 8 | Change Request | P2 | Apr 24 |

**Total comments Sprint 8: 88**
**Public launch: May 1, 2025**

---

## KEY STORY THREADS IN SPRINT 8

**Thread 1 — Pattern of Missed Related Fixes**
NUTR-BUG-008 is the third time a fix was applied to one component but not its
related components (after NUTR-BUG-001/AN-BUG-003 and NUTR-BUG-003/NUTR-BUG-008).
Shristi explicitly identifies this pattern and requests a codebase audit. This
becomes a team learning moment.

**Thread 2 — Tests-First for Health Critical**
GOAL-BUG-005 regression was not caught by existing tests. Shristi requires tests
written before the fix for health-critical features. This becomes a team standard.

**Thread 3 — FROZEN vs LIVE Custom Meal Values**
NUTR-BUG-007 resolves the fundamental question: custom meal nutrient values are
frozen at creation time (snapshot) not live-calculated from current ingredients.
PRD compliance argument wins.

**Thread 4 — Progress Bar Design Win**
AN-CR-001 completes the bar graph evolution: original design (bar = target) →
Option C patch (explicit numbers) → final progress bar design (fill towards goal).
Real user testing with data at each stage shows a rigorous design process.

**Thread 5 — Indian Food Gap Closure**
CF-BUG-004 test case uses "Masala Oats" explicitly referencing the Indian food
gap from Sprint 2. Custom food feature now fulfills its original purpose.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 8

1. Sprint 8 dates: April 15 to April 28, 2025. Public launch May 1.
2. The team is in final stabilisation mode. Comments should reflect a team that has
   learned from Sprint 7 (faster diagnosis, more systematic thinking).
3. NUTR-BUG-008 — Shristi's call for a codebase audit in comment 5 should feel like
   a PM who has noticed a pattern and is proactively preventing future bugs, not
   just fixing the current one.
4. GOAL-BUG-005 — the tests-first requirement should feel like a genuine policy
   decision from Shristi, not a suggestion. "I want tests before the fix" is firm.
   The health-critical designation is serious.
5. AN-CR-001 is the most positive ticket in Sprint 8 — the redesign process shows
   the team at its best. User testing, real data, iterative improvement. Comments
   should feel collaborative and energised despite being late in the product cycle.
6. CF-BUG-004 test case using Masala Oats is important — explicitly reference the
   Indian food gap discovery from NUTR-TASK-001 Sprint 2. "This is exactly the
   use case we said custom food would solve." This circle closing should be noted.
7. AN-CR-002 should be lighter in tone — copy writing debates are fun. The "to go
   = takeaway food" confusion is genuinely funny — write it with warmth.
8. By end of Sprint 8 the team should feel confident about the May 1 public launch.
   The last comments of late-April tickets should reference "ready for launch."