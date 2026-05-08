sprint 7

# Sprint 7 Ticket Definitions — Complete Brief for GPT-4o
## April 1 to April 14, 2025 — Beta Launch

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions. Sprint 7 is the beta launch
sprint. MVP shipped March 31. Beta invites sent to 200 users on April 1. Bugs start
appearing immediately. All 10 tickets are Tier 1 bugs with 8 comments each. The tone
in this sprint shifts from building to firefighting. Shristi is managing beta users
while the team fixes bugs rapidly. Every bug discovered by a beta user should feel
like real user feedback — frustrated, confused, or reporting specific reproduction steps.

---

## SPRINT 7 TICKETS — ALL TIER 1 BUGS

---

### Ticket 1: NUTR-BUG-001
**Title:** Nutrient totals not updating instantly after food addition — React state issue
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair
**Created:** April 3, 2025
**Resolved:** April 8, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Nutrient recalculation must happen within 1 second after any add, edit, or delete
- No manual refresh needed by the user
- Cumulative totals must update accurately on every diary action

**Bug Context:**
Found by Priya during internal beta testing on April 3. Three beta users also
reported it on April 3 and April 4 via feedback form saying "the totals don't
change when I add food — I have to refresh to see them update."

**Conversation Blueprint:**
1. Priya reports bug — after adding a food item from any source (USDA, custom food,
   custom recipe), the cumulative nutrient totals at the bottom of the food diary
   do not update until the user manually refreshes the page. Steps to reproduce:
   open food diary for today, add any food item from USDA database, observe
   cumulative total row at bottom — total remains unchanged. Manually refresh page —
   totals update correctly. The bug is consistent across all food sources and all
   meal types.
2. Shristi marks P1 — this breaks the core value proposition of Nutrivana. Real-time
   tracking is the primary reason users choose this app over paper tracking. If totals
   only update on refresh the app is unusable. Assigns to Priya and asks Arjun to
   help diagnose root cause immediately.
3. Priya diagnoses the issue — the food diary component that displays cumulative totals
   is NOT subscribed to the food log state changes. When a food is added via the
   adjust portion page (NUTR-010 flow), the POST API call succeeds and the new food
   appears in the diary list. But the cumulative total component reads from its own
   local component state, not from the shared food log array. The calculation engine
   from NUTR-TASK-004 fires correctly but the total display component never re-renders
   because it does not know the food log array changed.
4. Arjun identifies the root cause at the architecture level — when NUTR-010 and
   NUTR-TASK-004 were built in Sprint 4, the optimistic update pattern stores the
   new food log in a local component state inside the FoodDiaryList component. The
   cumulative total component is a sibling component, not a child. Sibling components
   cannot share state directly — they need a shared parent state or a Context. The
   FoodDiaryContext that was planned but not yet implemented is the missing piece.
   Proposes implementing FoodDiaryContext now to lift the food log array state up to
   a shared level.
5. Priya and Arjun pair to implement FoodDiaryContext — a React Context that holds
   the food log array for the current diary date. All diary components (food list,
   cumulative totals, meal subtotals, goal comparison) subscribe to this Context.
   When any component adds, edits, or deletes a food, it updates the Context. All
   subscribed components re-render automatically.
6. Priya implements FoodDiaryContext and updates all diary components to subscribe
   to it. The implementation takes 3 hours of pairing. Tests the fix internally —
   adds food, totals update within 200ms. Deletes food, totals update. Edits portion,
   totals update.
7. Arjun reviews the PR — the Context implementation is clean. Notes that this same
   fix resolves AN-BUG-003 (analysis not updating after food deletion) which has the
   same root cause. Links AN-BUG-003 to this ticket as related. Approves and merges.
8. Shristi verifies on staging — adds 5 different foods in rapid succession. Totals
   update after each addition within 200ms. Tests delete and edit — both update
   totals correctly. Deploys fix to beta. Sends apology message to the 3 beta users
   who reported it. Closing ticket. Notes AN-BUG-003 will be closed as part of this
   same fix.

**Unique Detail:** The FoodDiaryContext is the architectural fix that was planned
but not implemented in Sprint 4. This bug forces the team to implement it now. The
discovery that sibling components cannot share state without Context is a real React
architecture lesson. The same root cause affecting NUTR-BUG-001 and AN-BUG-003
simultaneously is discovered during the PR review.

**Cross References:** Same root cause as AN-BUG-003. FoodDiaryContext connects to
NUTR-TASK-004 (calculation engine), NUTR-010 (optimistic updates), NUTR-016
(cumulative totals display). Referenced in Sprint retrospective.

---

### Ticket 2: NUTR-BUG-003
**Title:** Serving unit dropdown not resetting when user navigates back from adjust portion
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 7
**Priority:** P2
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair
**Created:** April 4, 2025
**Resolved:** April 10, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- If user navigates back from adjust portion page they should be redirected to
  food database page and the previous search input should be cleared and search
  field reset to default state
- If user changes source or navigates away, previous input should be cleared

**Bug Context:**
Found by Priya during internal beta testing. Reproduction: search for "chicken",
select it, reach adjust portion page, select serving unit "1 breast (172g)", tap
Back, search for "oats", select it, reach adjust portion page — the serving unit
dropdown still shows "1 breast" instead of the default oats serving units.

**Conversation Blueprint:**
1. Priya reports bug — serving unit dropdown retains the previous food's serving
   unit selection when navigating back and selecting a new food. Reproduction steps:
   select chicken, choose "1 breast (172g)" serving unit, navigate back, select
   oats — adjust portion page for oats shows "1 breast" selected in serving unit
   dropdown instead of the default oats serving unit. The serving amount field
   resets correctly but serving unit does not.
2. Arjun reviews the serving unit implementation from NUTR-009 — the food-specific
   serving units are fetched from the database when a food is selected. The dropdown
   options change correctly (oats shows oats-specific units). But the SELECTED value
   in the dropdown is maintained in component state that persists across navigation.
   When the component re-renders for oats, it loads the correct options but the
   selected index still points to position 2 ("1 breast") even though position 2
   for oats is a completely different unit.
3. Priya traces the bug — the serving unit selected value is stored as an array
   index (0, 1, 2) in component state. The index persists even when the dropdown
   options change. For chicken, index 2 = "1 breast (172g)". For oats, index 2 =
   "1 oz (28g)". The index maps to a different unit without the user choosing it.
   The fix is to reset the selected index to 0 (default serving unit) whenever the
   food_id changes.
4. Arjun and Priya debate whether to store serving unit selection as index or as
   the actual unit name string. Index is simpler but has this cross-food contamination
   problem. Storing the unit name string is safer — if the food changes, the old
   unit name simply does not exist in the new food's unit list and defaults to
   the first unit automatically.
5. Shristi asks — is there a scenario where user WANTS to keep the same serving
   unit across foods? For example someone who always thinks in "100g" units might
   want to stay on "100g" when switching foods. Should we preserve the selection
   if the new food also has the same unit name?
6. Arjun recommends always reset to default on food change — the default serving
   unit for each food is the most common way people eat that food. Keeping a
   previous unit across foods is more likely to confuse than help. The 100g use
   case is edge case vs the common case of users not noticing the wrong unit.
7. Priya implements the fix — stores serving unit selection as unit_name string
   instead of index. On food_id change, resets to null which causes the component
   to select the first (default) unit. Tests fix with multiple food selections in
   sequence.
8. Shristi verifies — selects chicken with "1 breast", navigates back, selects
   oats — oats default unit shows correctly. Tests 5 different food switches —
   each shows correct default unit. Closing ticket.

**Unique Detail:** The serving unit stored as array index vs unit name string debate
is a real engineering decision about data representation. The index approach is the
root cause — it cross-contaminates between different foods because the same index
maps to different units. The string approach is defensive programming.

**Cross References:** Caused by serving unit implementation in NUTR-009 (food-specific
serving units). The useEffect cleanup mentioned in the mapping table is part of the
navigation reset — when user navigates away the component unmounts and serving unit
state should clear via useEffect cleanup.

---

### Ticket 3: NUTR-BUG-004
**Title:** Supplement section showing in diary without toggle being enabled
**Tier:** 1 (8 comments)
**Type:** Frontend design bug
**Sprint:** 7
**Priority:** P2
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair, Kabir Sharma
**Created:** April 5, 2025
**Resolved:** April 11, 2025
**Participants:** Priya Nair, Kabir Sharma, Shristi Sharmistha

**PRD Requirements:**
- Supplement section ONLY appears if enabled by user
- The supplement toggle is a persistent global setting
- Food diary should show 3 sections by default (breakfast, lunch, dinner, snacks)
- 4th section (supplement) only shows when toggle is ON

**Bug Context:**
Found by Priya during beta testing on April 5. New users who have never enabled
supplement tracking are seeing the supplement section in their diary. Five beta users
also reported it — "I see a supplement section but I never turned it on, is it safe
to ignore?"

**Conversation Blueprint:**
1. Priya reports bug — supplement section appears in food diary for users who have
   never enabled the supplement toggle. Steps to reproduce: create a new user
   account, navigate to food diary without enabling supplement toggle — the diary
   shows all 4 sections including supplement. The supplement section should only
   appear if the user has explicitly enabled it.
2. Kabir checks the Figma — the supplement section should be completely hidden when
   toggle is off. The dismissible prompt from NUTR-014 should show instead. Asks
   Priya to check the conditional rendering logic in the diary component.
3. Priya traces the bug — in the diary component the conditional rendering is:
   `if (supplementEnabled || supplementEnabled === undefined)` — the `undefined`
   case was added as a default to handle users who have never set the toggle.
   The intent was "if we don't know the toggle state yet, show supplement by default."
   But this is backwards — it should be hidden by default, not shown. The correct
   logic is `if (supplementEnabled === true)`. The `undefined` case should show
   the dismissible prompt from NUTR-014, not the supplement section itself.
4. Kabir confirms the expected behaviour from design — new users (toggle state =
   undefined/null) should see the dismissible prompt ("Enable supplement tracking?")
   not the supplement section itself. Existing users with toggle OFF should see
   nothing (prompt already dismissed). Existing users with toggle ON should see
   the supplement section.
5. Shristi asks — how many beta users have already been affected? If they have been
   logging data in the supplement section thinking it was supposed to be there, what
   happens to that data when we fix the bug and hide the section?
6. Arjun checks the database — none of the affected beta users have actually logged
   any supplement entries. They just saw the section but didn't use it. Safe to
   fix without data migration concern. If any user had logged supplement entries
   with toggle OFF, those entries would remain in the database but be hidden from
   view — they are not deleted by the fix.
7. Priya implements fix — three explicit states: `undefined/null` → show dismissible
   prompt. `false` → show nothing (prompt already dismissed). `true` → show
   supplement section. Tests all three states with fresh accounts and existing
   accounts.
8. Kabir verifies the design matches Figma — new user sees prompt correctly, dismiss
   works, enable toggle shows section, disable toggle hides section. Shristi
   verifies on staging. Deploys to beta. Closing ticket.

**Unique Detail:** The `undefined` fallback logic being backwards is a real
conditional rendering mistake. The three-state model (undefined/null = prompt,
false = hidden, true = visible) is the correct mental model for a feature that
has three distinct user states: never interacted, explicitly dismissed, explicitly
enabled.

**Cross References:** Caused by conditional rendering in NUTR-014 (supplement toggle
implementation). The three-state model is important for how NUTR-BUG-004 is fixed.

---

### Ticket 4: NUTR-BUG-005
**Title:** Goal comparison colors incorrect for weight maintain calorie case
**Tier:** 1 (8 comments)
**Type:** Frontend design bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Kabir Sharma
**Assignee:** Priya Nair, Kabir Sharma
**Created:** April 4, 2025
**Resolved:** April 9, 2025
**Participants:** Kabir Sharma, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- For calorie in weight MAINTAIN goal: yellow if under, yellow if over, green if exact
- For calorie in weight LOSS/GAIN goal: yellow if under, green if exact, red if over
- Color coding must be consistent between food diary comparison and analysis bar graph
- Comparison must update within 1 second of any add/edit/delete

**Bug Context:**
Kabir spots the bug during a design review on April 4. He is testing the color
coding using a weight maintain goal account and notices that overeating calories
shows red instead of the required yellow.

**Conversation Blueprint:**
1. Kabir spots bug during design QA — creates a test account with weight maintain
   goal, logs food that exceeds the calorie target. The difference cell turns red.
   PRD explicitly specifies that for weight maintain goal, over-calorie should be
   yellow not red. The distinction is clinically meaningful — over-eating during
   weight maintenance is less concerning than over-eating during active weight loss.
   Reports to Priya with screenshot showing red where yellow is expected.
2. Priya reviews the color logic implementation from NUTR-017 — the code has three
   branches: weight_loss, weight_gain, and weight_maintain. The weight_maintain
   branch was implemented but Priya finds a logic error. The code is:
   `if (goalType === 'maintain' && percentage > 100) return 'yellow'` — this is
   correct. But the condition is only checked AFTER a general condition that checks
   `if (percentage > 100) return 'red'` which runs first and catches all over-100%
   cases before reaching the maintain-specific branch.
3. Kabir asks — are all three cases broken or just the over-100% maintain case? Priya
   checks all three weight goal types against all three percentage conditions (under,
   exact, over). The under and exact cases are correct for all goal types. Only the
   over case for weight maintain is wrong because of the early return in the general
   condition.
4. Arjun reviews the code — confirms the early return bug. The fix is to check
   goal_type FIRST before applying the general percentage rules. Proposed logic:
   ```
   if goalType === 'maintain':
     if percentage === 100: return green
     else: return yellow  // both under and over are yellow
   else (loss or gain):
     if percentage < 100: return yellow
     if percentage === 100: return green
     if percentage > 100: return red
   ```
5. Shristi confirms this fix is correct per PRD and per clinical reasoning. She
   references the original discussion in NUTR-017 where this distinction was
   explicitly designed. The fact that it broke shows the early return pattern
   is dangerous for case-specific logic — goal_type should always be evaluated first.
6. Priya implements the restructured condition — goal_type evaluated first, then
   percentage conditions within each goal_type branch. Also fixes the same logic
   in the AN-003 color function since both food diary and analysis share the same
   function.
7. Priya tests all combinations — weight loss under/exact/over correct. Weight gain
   under/exact/over correct. Weight maintain under/exact/over all correct (under=yellow,
   exact=green, over=yellow). Also tests with a few micronutrients to ensure the
   other-nutrients color logic was not accidentally broken.
8. Kabir verifies design matches expected colors in all scenarios. Shristi verifies
   on staging. Closing ticket. Notes AN-BUG-004 (Sprint 9) will find the same issue
   in a slightly different code path in the analysis page — this fix catches the diary
   but misses the analysis-specific branch.

**Unique Detail:** The early return bug — a general condition catches all over-100%
cases before the maintain-specific branch can run. The fix requires restructuring
the condition order (goal_type first, then percentage). The clinical reasoning for
why maintain-over should be yellow not red is referenced from the original NUTR-017
discussion. AN-BUG-004 (Sprint 9) finds the same issue in a different code path —
showing the early return pattern was used in multiple places.

**Cross References:** Caused by color logic in NUTR-017 (food diary) and AN-003
(analysis). The shared color function means this fix applies to both places.
AN-BUG-004 (Sprint 9) finds a similar bug in a different analysis code path
not caught by this fix.

---

### Ticket 5: NUTR-BUG-006
**Title:** Future date diary showing previous day data instead of empty diary
**Tier:** 1 (8 comments)
**Type:** Full stack bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Beta user (reported to Shristi)
**Assignee:** Arjun Mehta, Priya Nair
**Created:** April 6, 2025
**Resolved:** April 12, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- When future date selected: if FD not filled show empty diary with target
  nutrient columns
- When future date selected: if FD is filled show all logged food for that date
- Food diary must maintain separate log for each calendar date
- Switching between dates loads within 2 seconds

**Bug Context:**
Beta user Rahul (beta tester ID: BT-047) reports on April 6: "When I tap on
tomorrow's date in the food diary I see today's food there. I was trying to
pre-plan meals for tomorrow but it shows what I ate today."

**Conversation Blueprint:**
1. Shristi forwards beta user report to the team — user sees today's food when
   navigating to tomorrow's date. Asks Priya and Arjun to reproduce and investigate.
   This is a data integrity issue — user could be confused about what they actually
   ate vs planned.
2. Priya reproduces the bug — navigates to tomorrow's date, confirms it shows today's
   food. Checks the date picker value — date picker correctly shows tomorrow's date.
   But the diary data being displayed is today's data. The date picker value and the
   data query are out of sync.
3. Arjun investigates the diary data fetching logic — the food diary component has two
   sources of date: the URL parameter (used for initial load) and the React state
   (used for in-session date changes). When the date picker changes the date, it
   updates the React state correctly. But the data fetching useEffect has the wrong
   dependency array — it watches the URL parameter for the date, not the React state.
   So when user changes date via picker, the React state updates (changing what date
   is shown) but the useEffect for data fetching does not re-run because the URL
   parameter did not change.
4. Priya traces the specific failure — when viewing April 6 (today), the URL contains
   `?date=2025-04-06`. User clicks date picker to April 7. React state updates to
   April 7. The display component re-renders showing "April 7" in the header. But
   the data fetch useEffect watches `router.query.date` (URL parameter) which is
   still `2025-04-06`. So the fetch still returns April 6 data. The user sees April
   7 header with April 6 food data.
5. Arjun proposes two fixes — Option A: make the URL update when date changes
   (push new URL with date parameter). Option B: make the useEffect watch the React
   state date instead of URL parameter. Option A is more correct architecturally
   (URL reflects app state, supports browser back button). Option B is faster to
   implement.
6. Shristi asks — does Option A break anything with the browser back button? If user
   navigates date forward and then hits browser back, they should return to previous
   date. Option A supports this naturally. Option B does not. Recommends Option A.
7. Arjun implements Option A — date picker change pushes new URL with updated date
   parameter. The useEffect now watches the URL parameter correctly. Both URL and
   React state are in sync. Browser back button works correctly for date navigation.
8. Shristi verifies — navigates to tomorrow via date picker, sees empty diary.
   Navigates to past dates, sees historical data. Browser back button returns to
   previous date. Tests the midnight edge case from NUTR-022 — logs food at 11:55pm
   and 12:05am on test device, confirms data appears on correct dates. Closing ticket.

**Unique Detail:** URL parameter vs React state desynchronisation is a classic
Next.js routing bug. The date picker updates React state but the data fetch watches
URL parameters — these become out of sync. Option A (URL reflects state) is
architecturally correct and supports browser history. The browser back button
consideration is what drives the choice between options.

**Cross References:** Related to timezone handling in NUTR-022 and TECH-007. The
TECH-007 tests did not catch this because they tested the data integrity (correct
values per date) not the navigation synchronisation (date picker and data fetch
staying in sync).

---

### Ticket 6: GOAL-BUG-002
**Title:** EER formula not switching to correct formula when user changes gender
**Tier:** 1 (8 comments)
**Type:** Backend bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Beta user (reported to Shristi)
**Assignee:** Arjun Mehta
**Created:** April 5, 2025
**Resolved:** April 11, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- If person changes gender or activity level then automatically new EER formula
  must be selected depending on the category
- Any change in EER or weight maintenance calorie should automatically result in
  change of target calorie — both changes must reflect in UI immediately
- EER formula is different for different age group, gender, activity level

**Bug Context:**
Beta user Preethi (BT-023) reports on April 5: "I accidentally selected Male when
creating my account. I fixed it to Female but my calorie goal didn't change. I'm
Female age 28, active lifestyle, and 65kg. The app is giving me 2847 kcal which
looks like the male formula calculation."

**Conversation Blueprint:**
1. Shristi forwards Preethi's report to Arjun — user changed gender from male to
   female in profile settings but calorie goal remains at the male EER value.
   This is a health-critical bug — a female user on a male calorie budget could
   be significantly over-eating. Marks P1 and asks Arjun to investigate urgently.
2. Arjun reproduces with Preethi's exact values — female, age 28, active, 65kg,
   170cm. Expected female EER ≈ 2245 kcal. System shows 2847 kcal which matches
   male active formula for same parameters. Confirms the bug.
3. Arjun investigates the EER formula selection logic from GOAL-002 — the formula
   lookup table is keyed by gender + age_group + activity_level. The lookup
   function is called in the calorie goal recalculation endpoint. Traces what
   happens when gender changes: the profile update saves the new gender to the
   database. But the calorie goal endpoint only recalculates EER when the user
   explicitly visits the calorie goal page and saves — it does NOT automatically
   recalculate when profile fields (gender, age, height, activity level) change.
4. Arjun identifies the missing trigger — the PRD says "if person changes gender
   or activity level then automatically new EER formula must be selected." This
   requires a trigger on the user_profile table — when gender or activity_level
   changes, the EER must recalculate automatically without user visiting calorie
   goal page. This trigger was never implemented. The calorie goal page only
   recalculates when user explicitly interacts with it.
5. Shristi asks — should the trigger recalculate and SAVE the new EER automatically,
   or should it flag the user to visit calorie goal page and confirm? Auto-save
   could change someone's calorie goal without them being aware. A notification
   seems safer.
6. Arjun recommends auto-recalculate AND save — the PRD says "automatically new
   formula must be selected" which implies automatic recalculation. But adds a
   notification banner on the calorie goal page: "Your calorie goal was updated
   due to profile changes. Please review and confirm." This gives transparency
   without requiring manual action.
7. Arjun implements the trigger — database function fires on user_profile table
   updates for gender, age, height, weight, activity_level columns. Calls the
   EER recalculation function with updated profile values. Saves new EER and
   calorie goal to database. Sets a `profile_changed_flag` that the calorie goal
   page reads to show the notification banner.
8. Shristi verifies with Preethi's values — changes gender from male to female,
   calorie goal immediately updates to correct female value (2245 kcal). Notification
   banner shows on calorie goal page. Also tests age change — EER updates correctly.
   Also tests activity level change — formula switches correctly. Notifies Preethi
   that her account has been corrected. Closing ticket.

**Unique Detail:** The missing trigger on profile changes is a PRD requirement gap —
the trigger was specified ("automatically new formula must be selected") but never
implemented. The notification banner approach (auto-update + transparency notification)
balances automation with user awareness. The health-criticality of a female user on
a male calorie budget makes this P1 urgent.

**Cross References:** Caused by incomplete implementation of GOAL-002 (EER formula
implementation). The formula selection logic from GOAL-SPIKE-001 and GOAL-002 is
correct — the missing piece is the trigger. GOAL-BUG-001 (Sprint 8) is a related
issue where calorie changes do not cascade correctly.

---

### Ticket 7: GOAL-BUG-003
**Title:** Macro gram values not updating when user changes calorie goal
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 7
**Priority:** P2
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair, Arjun Mehta
**Created:** April 7, 2025
**Resolved:** April 12, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- For the same macro distribution % if user changes target calorie the gram equivalent
  should auto-update based on new calorie
- As user changes calorie goal the macros value should be instantly changed
- Macro in gram becomes the main goal of the user
- Carb in gram = Carb in kcal/4, Fat in gram = Fat in kcal/9,
  Protein in gram = Protein in kcal/4

**Bug Context:**
Found by Priya during beta testing on April 7. User changes their calorie goal
from 2000 to 1800 kcal. The macro percentages stay at 40:30:30. The kcal values
update correctly (carb = 720 kcal, not 800 kcal). But the gram values remain at
the old 2000 kcal calculation (carb = 200g instead of the new 180g).

**Conversation Blueprint:**
1. Priya reports bug — user reduces calorie goal from 2000 to 1800 kcal. Macro
   percentages (40:30:30) are unchanged. Macro kcal values update correctly:
   carb becomes 720 kcal (40% of 1800). But macro gram values do NOT update:
   carb still shows 200g (which was 40% of 2000/4 = 200g) instead of the new
   180g (720/4 = 180g). The gram values are frozen at the calculation from when
   macros were first set.
2. Arjun reviews the macro calculation chain from GOAL-005 and GOAL-006 — the
   chain should be: calorie changes → macro kcal values recalculate
   (percentage × new calorie) → macro gram values recalculate (kcal / conversion
   factor). The first step (kcal recalculation) is working. The second step (gram
   recalculation) is not triggering.
3. Priya traces the gram calculation — the gram values are calculated in a separate
   React useEffect that watches the macro kcal values. When calorie changes, it
   triggers the kcal calculation first. Then the kcal values update in state. Then
   the gram useEffect should fire because its dependency (kcal values) changed. But
   Priya finds the gram useEffect dependency array is wrong — it watches the
   percentage values not the kcal values. So the gram calculation only fires when
   the user manually changes a macro percentage, not when kcal changes due to
   calorie update.
4. Arjun explains the root cause clearly — there are two ways gram values can
   change: (1) user changes macro percentage → kcal changes → grams change.
   (2) user changes calorie goal → kcal changes (same percentage, new calorie base)
   → grams change. Both paths go through kcal. The gram useEffect should watch
   the kcal values, not the percentage values. Watching percentage only catches
   path 1 but misses path 2.
5. Shristi asks — this sounds similar to the GOAL-007 floating point issue from
   Sprint 3 where the calculation chain was brittle. Are there other parts of the
   macro calculation chain that might have wrong useEffect dependencies?
6. Priya does a systematic audit of all macro-related useEffects — finds two more
   with similar issues. The required deficit/surplus value also does not recalculate
   when macros change (it should — macro changes can imply calorie changes). Adds
   these to the fix.
7. Priya fixes the gram calculation useEffect dependency array — changes from
   watching percentage to watching kcal values. Also fixes the two other
   dependency array issues found in the audit. Tests the full chain: change calorie
   → kcal updates → grams update → deficit/surplus updates. All fire in sequence.
8. Shristi verifies all three paths — changes calorie goal (grams update correctly),
   changes macro percentage (grams update correctly), changes both together (grams
   update correctly). Tests the floating point edge case from GOAL-007 — rounding
   still correct. Closing ticket.

**Unique Detail:** Wrong useEffect dependency (percentage instead of kcal) breaks
one of two paths to gram recalculation. The systematic audit of ALL macro useEffect
dependencies finds two more issues — showing that dependency array bugs tend to
cluster in feature areas. The connection to GOAL-007's floating point issue shows
the macro calculation chain has been fragile throughout development.

**Cross References:** Caused by useEffect implementation in GOAL-005 and GOAL-006.
Related to the macro calculation chain debated in GOAL-007. The systematic audit
in comment 6 prevents future macro calculation bugs.

---

### Ticket 8: GOAL-BUG-004
**Title:** Selected micronutrient goals disappearing after page refresh
**Tier:** 1 (8 comments)
**Type:** Frontend technical bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Beta user (multiple reports)
**Assignee:** Priya Nair, Arjun Mehta
**Created:** April 6, 2025
**Resolved:** April 12, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Selected micros must persist even after logout, refresh, page navigation
- Once the nutrient is set same nutrient remains even if user logs off, refreshes,
  moves to other page
- For selected nutrient RDA value should be set and saved as daily target

**Bug Context:**
Four beta users report within 24 hours: "Every time I refresh the page or close
and reopen the app, my micronutrient selections are gone and I have to re-select
them all over again. I spent 10 minutes selecting the right vitamins and they
disappeared when I reloaded." Beta user BT-012 counted — they had to reselect
12 micronutrients after every session.

**Conversation Blueprint:**
1. Shristi escalates immediately — 4 reports in 24 hours is a significant beta
   feedback signal. Micronutrient selection is a core setup step — if it resets
   every session the app is fundamentally broken for users who track micros.
   Assigns to Priya and Arjun as P1.
2. Priya reproduces the bug — selects 8 micronutrients (calcium, iron, folate,
   vitamin A, vitamin C, vitamin D, magnesium, zinc), refreshes the page, all
   8 micronutrients are unselected. The food diary also loses the micronutrient
   columns on refresh, confirming the selections are not persisting.
3. Priya reviews the micronutrient selection implementation from GOAL-010 — the
   selected_micros are stored in React state (useState hook) in the GoalSettings
   component. When user selects a micronutrient, the state updates and the checkbox
   appears checked. When user navigates away or refreshes, the component unmounts
   and the React state is destroyed. The selections were NEVER saved to the database.
   The GOAL-010 implementation only persisted which micro was selected in the UI
   but forgot to save it to Supabase.
4. Arjun checks the database — confirms there is no saved record of micronutrient
   selections for any beta user. The user_micronutrient_goals table has the schema
   but all rows are empty. The INSERT call when user selects a micro was never
   implemented — Priya only implemented the UI checkbox state but omitted the
   API call to save.
5. Shristi asks — when users see their micro selections in the food diary columns,
   how were those columns appearing if nothing was saved to the database? Priya
   explains — the columns were appearing because the food diary read from the same
   React state as goal settings. Within the same session (before refresh) everything
   worked. Across sessions (after refresh) nothing worked.
6. Arjun implements the database persistence — POST /user-micronutrient-goals
   endpoint that saves user_id + nutrient_id + is_tracked + rda_value + is_custom.
   On page load, GoalSettings fetches saved selections from database and restores
   UI state. On selection change, calls the POST endpoint to update.
7. Priya implements the load-from-database on mount — GoalSettings component fetches
   user's saved micronutrient selections on initial render. Selections restored from
   database. Food diary column generation now reads from database via API, not from
   React state. Tests persistence: selects 8 micros, refreshes, all 8 still selected.
   Logs out, logs back in, selections restored.
8. Shristi verifies — selects micronutrients, refreshes, still there. Closes browser
   completely, reopens, still there. Food diary shows correct columns. Tests with 20
   micronutrients (maximum allowed) — all 20 persist correctly. Sends apology to the
   4 reporting beta users with fix confirmation. Closing ticket.

**Unique Detail:** The selections were never saved to the database — only held in
React state. This is a classic mistake where UI state (checkbox checked/unchecked)
and persistent state (database record) are confused as the same thing. The bug worked
perfectly within a single session because React state survived intra-session navigation.
The cross-session failure was only discovered by beta users who closed and reopened
the app. The 4 reports in 24 hours is a significant beta signal.

**Cross References:** Caused by incomplete implementation of GOAL-010 (select
micronutrients to track). The missing INSERT call. The food diary column generation
also had to be fixed to read from database instead of React state.

---

### Ticket 9: AN-BUG-002
**Title:** Bar graph colored segment exceeding container boundaries when intake over 100%
**Tier:** 1 (8 comments)
**Type:** Frontend design bug
**Sprint:** 7
**Priority:** P2
**Status:** Closed
**Reporter:** Kabir Sharma
**Assignee:** Priya Nair, Kabir Sharma
**Created:** April 8, 2025
**Resolved:** April 13, 2025
**Participants:** Kabir Sharma, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Bar graph loads within 2 seconds
- The graph shall not cause noticeable lag or unresponsiveness in the application UI
- Length of colored part represents actual consumption as % of target
- Red if actual/target % > 100 (calorie weight loss/gain)

**Bug Context:**
Kabir finds during design QA on April 8. When a user has consumed more than their
target (e.g. 150% of calorie goal), the bar's colored segment extends beyond the
bar container, overlapping adjacent elements and breaking the page layout.

**Conversation Blueprint:**
1. Kabir reports bug — the bar graph colored segment uses CSS width set to the
   actual/target percentage. When percentage is 150%, the CSS width is set to 150%
   of the container, causing the colored bar to overflow outside its parent element
   and overlap nutrient name labels and other UI elements. Screenshots show the
   layout breaking visibly.
2. Priya reviews the bar implementation — uses inline style `width: ${percentage}%`
   on the colored segment. No maximum width constraint. At 150% the element is 1.5x
   wider than its container. The fix is straightforward: cap the colored segment at
   100% width and use the color (red) to communicate over-target status rather than
   bar length.
3. Kabir considers the design implication — if the bar caps at 100% width for over-target,
   how does the user visually understand they are OVER the target, not just AT the target?
   Both 100% and 150% would show a full red bar. Proposes two options: (A) cap at
   100% with red color and show the over-percentage number prominently. (B) cap at
   100% but add a small overflow indicator (like a small arrow or indicator segment)
   extending just slightly past the 100% mark to show "beyond target."
4. Shristi asks Ananya — from user testing perspective, which approach is clearer?
   AN-002 already showed users struggle with bar graph interpretation. Adding more
   visual complexity could worsen confusion.
5. Ananya recommends Option A — cap at 100%, use red + bold number. The explicit
   number ("150%") communicates over-target more clearly than any visual metaphor.
   This is consistent with the Option C fix from AN-002 (explicit numbers over
   visual metaphor). Simpler is better given the user research findings.
6. Kabir designs the cap + number approach — bar caps at 100% width (full bar), red
   color, and the percentage number shown in bold red below the bar with "over target"
   label. Consistent with the label design from AN-002 fix.
7. Priya implements CSS fix — adds `max-width: 100%` and `overflow: hidden` to the
   colored bar segment. Updates the number display to show percentage and "over target"
   label in red when percentage > 100. Layout no longer breaks at any percentage value.
8. Kabir verifies — tests at 50%, 100%, 150%, 200%, 500% — layout stable at all values.
   The 200% case (extreme overeating) still looks clean and readable. Shristi verifies.
   Closing ticket.

**Unique Detail:** The design debate between "overflow indicator" vs "cap + number"
connects directly to the AN-002 user research findings — explicit numbers beat visual
metaphors for this user base. Option A (cap + bold number) is chosen for consistency
with the AN-002 patch and based on Ananya's user research recommendation.

**Cross References:** Connected to AN-002 (bar graph design). The "explicit numbers"
approach is consistent with AN-002's Option C patch. AN-CR-001 (Sprint 8) is the
planned full redesign of the bar graph that will address both AN-002 and AN-BUG-002
more comprehensively.

---

### Ticket 10: AN-BUG-003
**Title:** Analysis section not updating after user deletes food from diary
**Tier:** 1 (8 comments)
**Type:** Full stack bug
**Sprint:** 7
**Priority:** P1
**Status:** Closed
**Reporter:** Priya Nair
**Assignee:** Priya Nair
**Created:** April 4, 2025
**Resolved:** April 8, 2025
**Participants:** Priya Nair, Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- The analysis cannot be changed manually — only changes if user adds, deletes,
  or edits item in food diary
- Updates to graph after logging or removing food render within 1 second
- Bar graph analysis reflects nutrient consumed for selected date

**Bug Context:**
Found by Priya on April 4 during beta testing. User deletes a food from the diary.
The food list in the diary updates correctly (food disappears). The cumulative totals
in the diary update correctly (NUTR-BUG-001 fix made this work). But the analysis
bar graphs do NOT update — they still show the pre-deletion nutrient values until
the user manually navigates away and back to analysis.

**Conversation Blueprint:**
1. Priya reports bug — deleting food from diary correctly removes it from the diary
   list and updates diary totals (after NUTR-BUG-001 fix). But the analysis section
   continues showing the old pre-deletion bar graph values. Steps to reproduce:
   log 200g chicken in dairy, navigate to analysis, see protein bar at 50%, navigate
   back to diary, delete chicken, navigate to analysis — protein bar still shows
   50% instead of updating to 0%.
2. Priya immediately recognises the root cause — this is the same issue as
   NUTR-BUG-001 but for the analysis section. NUTR-BUG-001 was the diary totals
   not subscribing to food log state changes. AN-BUG-003 is the analysis section
   not subscribing to the same food log state changes. Both are caused by not being
   subscribed to the FoodDiaryContext.
3. Arjun confirms — the FoodDiaryContext fix from NUTR-BUG-001 was applied to the
   diary components but the analysis section was not updated to subscribe to the same
   Context. The analysis section still reads from its own local state which only
   updates on initial mount or manual navigation.
4. Priya notes she actually mentioned this in NUTR-BUG-001 comment 7 — Arjun's PR
   review linked AN-BUG-003 as related. The fix is the same: subscribe the analysis
   components to FoodDiaryContext so they re-fetch and re-render when the food log
   array changes.
5. Shristi asks — should the analysis re-calculate from the food log array in Context
   (client-side calculation matching NUTR-TASK-004) or re-fetch from the API on every
   food log change? Client-side is faster but requires the analysis calculation logic
   to match the food log state exactly.
6. Arjun recommends client-side — the FoodDiaryContext already holds the complete
   food log array for the current date with all nutrient values. The analysis
   calculation is just summing those values per nutrient. No additional API call
   needed. Consistent with the client-side calculation engine from NUTR-TASK-004.
7. Priya implements the fix — analysis components subscribe to FoodDiaryContext.
   When food log array changes (add, edit, delete), analysis components re-calculate
   nutrient totals client-side and re-render bar graphs. Fix is simpler than
   NUTR-BUG-001 because the infrastructure is already in place.
8. Shristi verifies — adds chicken (protein bar updates in analysis), edits portion
   (analysis updates), deletes chicken (analysis updates to 0%). All analysis updates
   happen within 200ms matching the NUTR-BUG-001 fix performance. Closing ticket.
   Notes this ticket was predictable from the NUTR-BUG-001 investigation — similar
   bugs tend to cluster.

**Unique Detail:** The explicitly predicted relationship to NUTR-BUG-001 — Priya
references her own comment 7 in NUTR-BUG-001 where she linked this ticket. The
clean FoodDiaryContext extension is faster to implement than NUTR-BUG-001 because
the infrastructure already exists. This shows how fixing one architectural issue
(Context) makes fixing related issues much faster.

**Cross References:** Same root cause as NUTR-BUG-001 (FoodDiaryContext not extended
to analysis). The fix is a direct extension of NUTR-BUG-001 solution. Referenced in
Sprint 7 retrospective as an example of architectural debt creating related bugs.

---

## SUMMARY OF SPRINT 7

| Ticket | Tier | Comments | Found By | Root Cause Area | Closed |
|---|---|---|---|---|---|
| NUTR-BUG-001 | T1 | 8 | Priya + 3 beta users | React Context missing | Apr 8 |
| NUTR-BUG-003 | T1 | 8 | Priya | useEffect wrong dependency | Apr 10 |
| NUTR-BUG-004 | T1 | 8 | Priya + 5 beta users | Conditional render logic | Apr 11 |
| NUTR-BUG-005 | T1 | 8 | Kabir | Early return in color logic | Apr 9 |
| NUTR-BUG-006 | T1 | 8 | Beta user BT-047 | URL vs React state desync | Apr 12 |
| GOAL-BUG-002 | T1 | 8 | Beta user BT-023 | Missing profile change trigger | Apr 11 |
| GOAL-BUG-003 | T1 | 8 | Priya | Wrong useEffect dependency | Apr 12 |
| GOAL-BUG-004 | T1 | 8 | 4 beta users | Selections never saved to DB | Apr 12 |
| AN-BUG-002 | T1 | 8 | Kabir | CSS max-width missing | Apr 13 |
| AN-BUG-003 | T1 | 8 | Priya | React Context not extended | Apr 8 |

**Total comments Sprint 7: 80**

---

## KEY STORY THREADS IN SPRINT 7

**Thread 1 — FoodDiaryContext Architecture**
NUTR-BUG-001 and AN-BUG-003 share the same root cause and are fixed together.
The FoodDiaryContext that was planned in Sprint 4 but not implemented is finally
built under bug pressure. This is a common real-world pattern — architectural
shortcuts come back as bugs.

**Thread 2 — Database Persistence Gaps**
GOAL-BUG-004 (micro selections never saved to DB) is the most embarrassing bug
of the sprint — UI state confused with persistent state. Working within a session
but breaking across sessions.

**Thread 3 — Profile Change Triggers**
GOAL-BUG-002 (gender change not updating EER) reveals a missing database trigger
that was explicitly required by the PRD. The health-criticality of a female user
on male calorie budget makes this P1.

**Thread 4 — React State vs URL**
NUTR-BUG-006 (date picker desync) is a classic Next.js routing issue where URL
parameter and React state diverge. The Option A fix (URL reflects state) also
adds browser history support.

**Thread 5 — Bug Clustering**
GOAL-BUG-003 and NUTR-BUG-001/AN-BUG-003 both involve wrong useEffect dependencies.
When one wrong dependency is found during audit, others are typically nearby.
Sprint 7 retrospective should reference this pattern.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 7

1. Sprint 7 dates: April 1 to April 14, 2025. Beta launched April 1.
2. The tone of Sprint 7 is DIFFERENT from all previous sprints. This is firefighting
   mode, not building mode. Comments should feel urgent. Shristi is apologising to
   beta users. Team is working rapidly to fix and deploy.
3. Beta user reports should feel real — include user IDs (BT-047, BT-023, BT-012),
   quote their exact feedback language (frustrated but specific), mention the number
   of users affected.
4. NUTR-BUG-001 is the most impactful bug — Shristi's urgency in comment 2 should
   feel like a PM who is embarrassed that the core feature is broken on day 3 of beta.
5. GOAL-BUG-004 should be the most embarrassing conversation — Priya's comment 3
   realising the selections were NEVER saved to the database should convey genuine
   surprise and self-reproach. This is a fundamental implementation oversight.
6. GOAL-BUG-002 is the most health-critical — Shristi's P1 designation should
   reference the health implication explicitly: a female user eating on male calorie
   budget is a product liability issue.
7. AN-BUG-003 can reference NUTR-BUG-001 explicitly — "same root cause we just fixed
   two days ago" — showing how fixing one architectural bug reveals related ones.
8. Sprint 7 comments should mention the beta user relationship — Shristi sends
   updates to affected users, thanks them for reporting, builds goodwill.
9. The parallel threads (NUTR-BUG-001 + AN-BUG-003 being worked simultaneously,
   GOAL-BUG-002 + GOAL-BUG-004 both being P1) should create a sense of a team
   being pulled in multiple directions during a critical beta period.