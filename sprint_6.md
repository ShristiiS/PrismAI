sprint 6:

# Sprint 6 Ticket Definitions — Complete Brief for GPT-4o
## March 12 to March 31, 2025 — MVP Ships March 31

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions. Sprint 6 is the final build
sprint before MVP ships. It completes custom food management (CF-003 through CF-007)
and builds the entire Analysis feature (AN-001 through AN-005). Sprint 6 ends with
the MVP shipping on March 31. Comments in this sprint should reflect the pressure
and excitement of approaching the first major milestone.

---

## SPRINT 6 TICKETS

---

### Ticket 1: CF-003
**Title:** Save custom food with mandatory field validation and zero calorie edge case
**Tier:** 1 (8 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Arjun Mehta
**Created:** March 12, 2025
**Resolved:** March 22, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- Save button must be present to confirm food is saved
- Once saved Add button appears to directly add from create page
- Once saved no field can be edited
- Food saved only if all mandatory fields filled — food name, serving size, AND calorie
- Food once saved can only be accessed by the logged-in user who created it
- If mandatory field not filled — show message "please enter mandatory field" with
  field highlighted
- If input not in correct format — do not allow save
- Once saved: if user goes back or navigates away, refreshes or re-logs in, same
  value should be present
- If NOT saved and user navigates away — input value is discarded
- On going back after saving — navigate to custom food menu page
- Once saved user stays on create custom food page (does not redirect away)
- The input field should be a number format like 20.0 or 0.5 and > 0
- Calorie value is mandatory to be filled

**Conversation Blueprint:**
1. Shristi creates story — Save button validates all mandatory fields (food name,
   serving size, calorie) before saving. After successful save, Add button appears
   on the same page. All fields become read-only after save. Asks Priya to implement
   and run through the validation scenarios carefully.
2. Priya implements save validation — food name required, serving value required
   and must be > 0, calorie required. Tests all scenarios and they pass. But during
   internal testing Shristi discovers an edge case the PRD does not explicitly address.
   She tries to enter 0 in the calorie field for black coffee. The PRD says calorie
   is mandatory (must be filled) and the input field description says "> 0". But
   black coffee genuinely has 0 calories. Plain water has 0 calories. Both are foods
   users would legitimately want to log in their diary. If we block zero the app is
   less accurate. If we allow zero we technically violate the "> 0" input spec.
3. Shristi raises the issue formally in the ticket — "the PRD says input field format
   is > 0 but zero calorie foods are real. Black coffee, plain water, diet soda,
   plain lettuce. If a user creates a custom food for black coffee and cannot enter
   0 calories, the app is factually inaccurate. This is a health app — accuracy
   matters more than strict adherence to the "> 0" spec that was probably written
   without thinking about zero calorie foods."
4. Arjun joins the discussion — from a technical standpoint 0 is valid as a stored
   value. The database column is DECIMAL(10,2) which accepts 0.00. The "> 0"
   requirement in the PRD was likely meant to prevent negative values and empty
   submissions, not to prevent genuinely zero-calorie foods. Proposes allowing 0
   as a valid calorie input.
5. Priya asks — if we allow 0 calories, what about other nutrient fields? The PRD
   says all nutrient input fields should be "> 0" format. Should we allow 0 for
   all nutrients too? For example a food could have 0mg cholesterol (common in
   plant foods). Or 0g fat.
6. Shristi makes a product decision — allow 0 for all nutrient fields including
   calorie. The "> 0" in the PRD was poorly worded and meant to prevent empty
   fields and negative values. Zero is a valid nutritional value for any nutrient.
   Updates the PRD note to "≥ 0 (empty is not valid, negative is not valid,
   zero is valid)." Asks Arjun to confirm this does not break any downstream
   calculation logic.
7. Arjun confirms — calculation engine handles 0 nutrient values correctly (treats
   as 0 in sum, as expected). The USDA database itself has many foods with 0 values
   for certain nutrients. Allowing 0 in custom food is consistent with how USDA
   data is handled. Updates validation logic to allow ≥ 0. Priya updates frontend
   validation to match.
8. Shristi verifies — saves custom food "Black Coffee" with 0 calories, 0g fat,
   0g carbs, 0mg sodium. Saves successfully. Add button appears. Fields become
   read-only. Navigates away and returns — values persist. Logs out, logs back in
   — custom food still there. Going back from create page navigates to menu page.
   Closing ticket.

**Unique Detail:** The zero calorie edge case is a genuine product decision that
reveals a PRD error. The "> 0" specification was meant to prevent empty/negative
values but accidentally blocks legitimate zero-calorie foods like black coffee and
plain water. The decision to allow ≥ 0 is a health-accuracy argument that overrides
the literal PRD spec. This is a thoughtful product conversation unique to this ticket.
CF-BUG-003 (Sprint 8) is also related to this ticket — calorie not marked mandatory
in the create flow (the asterisk was missed in implementation).

**Cross References:** CF-BUG-003 (Sprint 8 — calorie not marked mandatory) is caused
by Priya missing the asterisk on the calorie field in this implementation.
CF-BUG-004 (Sprint 8 — Add button not appearing after save) is caused by state
management in this save flow.

---

### Ticket 2: CF-004
**Title:** Search and select custom food from list on menu page
**Tier:** 2 (4 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** March 12, 2025
**Resolved:** March 17, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Custom food menu page shows: list of saved custom food names, calorie value,
  create button, add icon next to each food
- Two columns: Custom Food (name) and Calorie
- Create button bold and distinguishable
- Add icon present beside each custom food
- Search field with placeholder "enter custom food name"
- Custom food searched through name — partial and full matches returned
- User can select only one custom food at a time
- Redirect to adjust portion page on: clicking add icon OR selecting from search
- Clicking Create redirects to create custom food page

**Conversation Blueprint:**
1. Shristi creates story — custom food menu page. Two column layout (name + calorie).
   Search by name. Add icon on each row. Create button. Asks Priya to confirm the
   search uses the same reusable component from NUTR-011 (custom recipe search) with
   the custom_foods table as data source.
2. Priya confirms — reuses the search component from NUTR-011. Custom food search
   queries custom_foods table filtered by user_id (Supabase RLS). Notes one
   difference from recipe menu — shows calorie in second column. Standard search
   result list pattern. Also adds the Create button linking to CF-001 create flow.
3. Priya marks complete — notes the add icon on each row is a second way to initiate
   logging besides selecting from search. Both paths lead to adjust portion page.
   The list is sorted alphabetically by food name by default for easy browsing.
4. Shristi verifies — list shows name and calorie correctly. Search works with
   partial names. Add icon redirects to adjust portion. Create button opens create
   page. Alphabetical sort confirmed. Closing ticket.

**Unique Detail:** Alphabetical sort by default — makes large custom food lists
browseable without searching. Two paths to adjust portion (add icon vs search
selection) ensure flexibility for power users.

**Cross References:** Reuses search component from NUTR-011. Feeds into NUTR-012
(custom food source in diary). CF-BUG-004 (Sprint 8 — add button not appearing after
save on CREATE page) is different from the add icon here on MENU page

---

### Ticket 3: CF-005
**Title:** Edit custom food — name serving size nutrients with retroactive date logic
**Tier:** 2 (4 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Arjun Mehta
**Created:** March 12, 2025
**Resolved:** March 19, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- User can edit any custom food by clicking its name in custom food main menu
- Editable fields: custom food name, serving size (value + unit), nutrient values
- Saving and input field validation criteria same as creation (CF-003)
- On saving — Add button should be enabled
- SAVE and ADD buttons clearly distinguishable
- All fields in edit mode — clearly indicated as editable
- When page in edit mode: if user refreshes, re-logs, or navigates away — previous
  filled value (the unsaved edit) should persist
- New value stored only on saving
- In case user has already logged the custom food and makes changes later — the new
  change should reflect from the DAY CHANGE WAS MADE — not retroactively to past logs

**Conversation Blueprint:**
1. Shristi creates story — edit works like create but with pre-filled values. Most
   important requirement is the date-aware change logic: changes reflect from the
   day of edit, not retroactively. Asks Arjun to explain how CF-007 (retroactive
   change story) connects to this ticket since both deal with the same behaviour.
2. Arjun explains the data model — CF-005 is the user-facing edit flow. CF-007 is
   the backend logic that ensures changes only affect diary entries from the edit
   date onwards. They are separate stories because the UI (CF-005) can be tested
   independently of the retroactive logic (CF-007). The retroactive logic requires
   the goal_snapshots style approach: when a custom food is edited, a new version
   is created with an effective_date. Food diary queries use the version active on
   each log's date_string.
3. Priya implements edit form — pre-fills all fields from current custom food record.
   All fields editable. Save validates same as CF-003. Asks Arjun — should unsaved
   edits persist if user navigates away (per PRD)? This is different from CF-003
   where unsaved create was discarded on navigation.
4. Shristi confirms — yes, PRD explicitly says unsaved edits persist (edit mode
   preserves unsaved state). This is different from create flow where unsaved
   input is discarded. Edit flow is forgiving because user has already invested
   effort creating the food. Priya implements auto-save of draft edit state.
   Closing ticket.

**Unique Detail:** Contrast between create flow (unsaved = discarded on navigation)
and edit flow (unsaved = preserved on navigation). The PRD intentionally treats them
differently. The effective_date versioning connects to CF-007 backend logic.

**Cross References:** CF-007 implements the backend effective_date logic that this
ticket depends on. CF-BUG-001 (Sprint 9 — edit changes reflecting for past dates)
is caused by a bug in the effective_date logic from CF-007.

---

### Ticket 4: CF-006
**Title:** Delete custom food with confirmation popup
**Tier:** 3 (2 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** March 14, 2025
**Resolved:** March 17, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- On deleting: entire custom food record removed from user account
- Delete icon present beside each custom food on menu page
- Confirmation popup: "do you want to delete custom food?" with delete and cancel options
- Confirmation message is a popup
- If user cancels: redirect to create custom food page
- Delete operation cancelled if user refreshes, clicks cancel, or moves to new page

**Conversation Blueprint:**
1. Priya implements delete with confirmation popup matching the pattern from
   NUTR-020 (delete logged food item). Delete icon on each row of custom food menu.
   Confirmation popup appears. On confirm — DELETE API call removes the custom_food
   record. On cancel — stays on menu page (note: PRD says redirect to create page
   on cancel which seems like a PRD error — Priya asks Shristi to confirm).
2. Shristi reviews PRD — confirms the "redirect to create custom page on cancel" in
   PRD is indeed unusual. Decides it should stay on menu page on cancel (consistent
   with NUTR-020 behaviour). Documents as intentional deviation from PRD. Priya
   implements stay-on-menu-page on cancel. Also asks Arjun — when a custom food is
   deleted, what happens to past diary entries that logged this food? They should
   remain intact (soft delete pattern from CF-BUG-002 discussion). Arjun confirms
   soft delete — deleted_at timestamp set, food hidden from menu but diary entries
   preserved. Closing ticket.

**Unique Detail:** PRD says cancel redirects to create page — this is caught as
a PRD error and corrected to stay on menu page. Soft delete pattern ensures past
diary entries are preserved when custom food is deleted. CF-BUG-002 (Sprint 9)
is the bug where deleted custom food still appears in past dates despite the soft
delete — caused by query not filtering deleted_at correctly.

**Cross References:** CF-BUG-002 (Sprint 9 — deleted custom food appearing in past
diary) is caused by a gap in the soft delete implementation here

---

### Ticket 5: CF-007
**Title:** Retroactive change reflects from edit date only — effective date versioning
**Tier:** 3 (2 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** March 14, 2025
**Resolved:** March 20, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- In case user has already logged custom food and makes changes later — new change
  should reflect from the day change was made
- Example: if user changes serving size on April 11 then change in nutrient
  calculation of custom food should reflect from April 11 onwards
- Past diary entries (before April 11) should remain with old nutrient values

**Conversation Blueprint:**
1. Arjun implements effective_date versioning for custom foods — creates
   custom_food_versions table with custom_food_id, effective_date, and all
   nutrient values. When user edits a custom food, a new version row is inserted
   with effective_date = today. Diary queries for any given date_string use the
   custom food version whose effective_date is latest but not later than the
   diary date_string. This ensures April 10 diary uses pre-edit values and
   April 11 diary uses post-edit values.
2. Shristi verifies — creates custom food "Homemade Daal", logs it on March 15.
   Edits the protein value on March 20. Checks March 15 diary — shows original
   protein value. Checks March 20 diary — shows new protein value. Checks March
   19 diary — shows original value. Edge case passes. Closing ticket. Notes this
   is the most architecturally complex backend feature in the custom food system.

**Unique Detail:** custom_food_versions table with effective_date is the same pattern
as goal_snapshots from NUTR-TASK-003. The versioning pattern recurs throughout
Nutrivana architecture. CF-BUG-001 (Sprint 9 — edit changes reflecting for past
dates) is a bug where this logic is applied incorrectly during certain edge cases.

**Cross References:** Same pattern as goal_snapshots (NUTR-TASK-003). CF-BUG-001
(Sprint 9) is a regression in this exact logic under specific edit conditions.

---

### Ticket 6: AN-001
**Title:** Per nutrient analysis screen with ordered categories and separate screens
**Tier:** 2 (4 comments)
**Type:** Story — frontend design
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair
**Created:** March 12, 2025
**Resolved:** March 19, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Priya Nair

**PRD Requirements:**
- Every tracked nutrient should be analysed graphically
- Every nutrient analysis has a separate screen
- Order: Calorie (if tracked) → Macros alphabetical (if tracked) →
  Micros alphabetical (if tracked)
- Labels for calorie, macros, micros clearly visible
- All sub-nutrients under each category displayed below parent nutrient
- Analysis shows nutrient consumed only for current or selected date
- Analysis cannot be changed manually — only changes when user adds, deletes,
  or edits in food diary
- Bar graph loads within 2 seconds of navigating to analysis section
- Updates to graph after logging or removing food render within 1 second

**Conversation Blueprint:**
1. Shristi creates story — analysis section structure. One screen per nutrient.
   Ordered by calorie → macros alphabetical → micros alphabetical. Asks Kabir
   to design the navigation between nutrient screens — horizontal swipe or
   vertical scroll or tab navigation?
2. Kabir shares Figma — proposes horizontal swipe navigation between nutrient
   screens with a nutrient name indicator at the top showing position (like
   story dots). This feels natural for mobile — swipe left/right to browse
   nutrients. The category labels (Calorie, Macros, Micros) appear as section
   headers in the navigation. Priya asks if this is a single scrollable component
   or separate routes for each nutrient.
3. Kabir recommends a single component with swipe gestures — routing to a new
   URL for each nutrient would create slow transitions and break the swipe
   animation. A carousel-style component with all nutrients pre-rendered (but
   only the current one visible) gives instant swipe response.
4. Shristi approves carousel approach. Priya implements swipe navigation with
   category section headers. Shristi verifies — calorie screen first, then
   macros alphabetically (carbohydrate before fat before protein), then micros
   alphabetically. Category labels visible. Analysis reads from food diary data
   for selected date. Closing ticket.

**Unique Detail:** Carousel-style navigation with pre-rendered screens vs URL routing
— a frontend architecture decision driven by animation performance requirements.
Horizontal swipe pattern feels natural for mobile nutrient browsing.

**Cross References:** Powers AN-002 (bar graph) and AN-003 (color coding) which
render within each nutrient screen. Date selection synced via AN-005 (shared
date picker with food diary)

---

### Ticket 7: AN-002
**Title:** Daily bar graph actual vs target — user testing reveals fundamental label confusion
**Tier:** 1 (8 comments)
**Type:** Story — frontend design
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair, Ananya Iyer
**Created:** March 12, 2025
**Resolved:** March 28, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Ananya Iyer, Priya Nair

**PRD Requirements:**
- Length of colored part of bar graph represents actual consumption as % of target
- Whole bar graph represents the target goal
- Colored portion = % of target — e.g. 25mg consumed of 100mg target = ¼ colored
- Display: actual nutrient consumed, target nutrient, (actual/target)% rounded to
  2 decimal points, amount left/over |target-actual|
- If actual > target: label says "over"
- If actual = target OR actual < target: label says "left"
- Bar graph loads within 2 seconds
- Updates within 1 second after food add/remove
- Same calendar picker used for both food diary and analysis
- Color coding: weight loss/gain calorie → yellow under, green exact, red over
- Color coding: weight maintain calorie → yellow under, yellow over, green exact
- Color coding: other nutrients → yellow under, green on track/under max, red over max

**Conversation Blueprint:**
1. Shristi creates story — bar graph with colored portion representing actual intake
   as proportion of target. The visual metaphor: bar is the target, how much you fill
   it is your actual. Asks Kabir to design the bar with all required display elements
   (actual, target, %, remaining/over).
2. Kabir implements the bar graph design in Figma and then Priya builds it. Kabir
   shares the implementation with Ananya for feedback before beta launch. Ananya
   takes the prototype to 5 test users for feedback sessions.
3. Ananya reports back with alarming findings. 4 out of 5 test users completely
   misread the bar graph. They think the FULL bar represents what they have eaten,
   and the unfilled grey portion represents how much more they can eat. The opposite
   of the actual design. One user said "I've eaten 100% of the bar, that means I'm
   done for the day" — but they had only eaten 75% of their target. The bar label
   design is fundamentally confusing.
4. Kabir reviews the feedback seriously — realises the problem is that his bar design
   followed the PRD literally (whole bar = target, colored = actual) but the visual
   language people expect is "fill bar = progress towards goal." Users are used to
   progress bars that fill up as you achieve the goal. Nutrivana's bar fills in the
   opposite direction to what users expect when they are under target.
5. Shristi calls an emergency design review — the MVP ships in 3 days. They need
   to fix the bar graph label confusion before launch or beta users will immediately
   think the app is broken. Asks Kabir to propose 3 options quickly.
6. Kabir presents 3 options within 2 hours. Option A — add clearer labels "Your
   intake" and "Your target" with arrows pointing to colored and full bar respectively.
   Option B — invert the visual: bar fills from target down, showing what remains
   rather than what you consumed. Option C — keep the current visual but add a
   percentage number in the bar and bold text labels below showing "XXg consumed /
   XXg target" so the numbers tell the story even if the visual confuses. Kabir
   recommends Option C as lowest implementation risk given 3-day window.
7. Shristi and Ananya evaluate together — Option A adds labels but may still confuse
   because the bar direction is counter-intuitive. Option B requires significant
   redesign and retest. Option C acknowledges the visual ambiguity and compensates
   with explicit numbers. Decides on Option C as an interim fix for MVP. Commits to
   redesigning Option A or B properly post-launch in a change request ticket.
   AN-CR-001 (Sprint 8) is created as a follow-up for the proper redesign.
8. Priya implements Option C changes — percentage number displayed inside the bar,
   bold text below showing "Xg consumed / Xg target, Xg remaining." Ananya
   re-tests with 3 users — all 3 now understand the graph correctly with the
   explicit number labels. Shristi approves. Closing ticket. AN-CR-001 created
   for the full redesign post-beta.

**Unique Detail:** This is the most important ticket in the entire Analysis sprint.
Real user testing before MVP reveals that the PRD-specified bar graph design is
fundamentally confusing. The entire bar metaphor (bar = target) conflicts with users'
mental model of progress bars (fill up = achieving goal). The 3-day-to-launch
timeline creates real pressure. The decision to patch with explicit numbers (Option C)
rather than proper redesign is a pragmatic MVP trade-off with a documented follow-up
(AN-CR-001). Ananya's role as the user research voice is central to this story.

**Cross References:** AN-CR-001 (Sprint 8 — bar graph colors confusing, full redesign)
and AN-CR-002 (Sprint 8 — remaining vs over label) are both direct follow-ups from
the findings documented in this ticket. AN-BUG-002 (Sprint 7 — bar exceeding container
when over 100%) is discovered during beta and is also related to bar graph rendering.

---

### Ticket 8: AN-003
**Title:** Color coding yellow green red for all nutrients with weight goal type logic
**Tier:** 2 (4 comments)
**Type:** Story — frontend design
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair
**Created:** March 14, 2025
**Resolved:** March 21, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Priya Nair

**PRD Requirements:**
- For calorie in weight loss/gain goal:
  Yellow if actual/target % < 100, Green if = 100, Red if > 100
- For calorie in weight MAINTAIN goal:
  Yellow if < 100, Yellow if > 100 (NOT red), Green if = 100
- For all other nutrients:
  Yellow if actual < daily target
  Green if actual = daily target OR actual ≤ daily max target
  Red if actual > daily max target
- Color applied to the colored portion of the bar graph
- Same color logic used in food diary comparison (NUTR-017)

**Conversation Blueprint:**
1. Shristi creates story — same 3-case color logic as NUTR-017 (food diary color
   coding). Asks Kabir to confirm the analysis bar uses identical color rules to
   food diary for consistency. Users should see the same colors in both places for
   the same nutrient status.
2. Kabir confirms consistency with NUTR-017 — same color rules. Notes one important
   implementation detail: the color of the bar segment is dynamic and changes as
   user logs food throughout the day. When protein starts at 0 (yellow) and user
   logs food, it transitions to yellow at 50%, then green at 100%, then red above
   MAX. Priya must ensure the color recalculates correctly on every diary update.
3. Priya implements color logic — reuses the color calculation function from
   NUTR-017 (good architecture — single source of truth for color rules). The
   analysis component subscribes to the same food log state changes that power
   NUTR-TASK-004 recalculation. Color updates automatically when diary changes.
4. Shristi verifies all color cases — calorie under target (yellow), calorie at
   target (green), calorie over target weight loss user (red), calorie over target
   weight maintain user (yellow not red). Vitamin C under RDA (yellow), at RDA
   (green), over MAX (red). Closing ticket.

**Unique Detail:** Reusing the color calculation function from NUTR-017 — single
source of truth for color rules ensures food diary and analysis are always in sync.
AN-BUG-004 (Sprint 9 — wrong color for weight maintain) is a bug that breaks both
food diary and analysis simultaneously because they share this function.

**Cross References:** Reuses color function from NUTR-017. AN-BUG-004 (Sprint 9)
breaks both places because they share the same function. AN-CR-001 (Sprint 8) will
change the color design — this shared function makes that change easier.

---

### Ticket 9: AN-004
**Title:** 7-day trend graph showing adherence over last 7 days
**Tier:** 2 (4 comments)
**Type:** Story — full stack
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta, Priya Nair
**Created:** March 14, 2025
**Resolved:** March 24, 2025
**Participants:** Shristi Sharmistha, Arjun Mehta, Priya Nair

**PRD Requirements:**
- Trend shown for selected date and 6 days BEFORE selected date
- Example: selected date May 31 → includes May 30, 29, 28, 27, 26, 25
- PRD note says "discuss with developer and then write" — incomplete specification
  This means Arjun and Shristi must define the trend chart behaviour together

**Conversation Blueprint:**
1. Shristi creates story — 7-day trend but PRD is explicitly incomplete ("discuss
   with developer and then write"). Asks Arjun what data the trend should show and
   what chart type makes most sense technically and visually.
2. Arjun proposes the trend specification — line chart showing actual/target % for
   each of the 7 days. X-axis: dates (last 7 days from selected date). Y-axis:
   0% to 150%+ (to accommodate over-target days). Each nutrient has its own trend
   line. Days where no food was logged show as 0% (gap in the line). Shristi approves
   this specification — fills in the blank PRD with this agreed approach.
3. Arjun implements backend trend endpoint — queries food_logs for user_id +
   7-day date range, aggregates nutrient totals per date_string, returns array of
   {date, actual, target, percentage} for each day. Priya implements the line chart
   using the charting library.
4. Shristi verifies — trend shows correct 7-day window. Days with no logs show as
   0% (not as null gaps). Switching selected date shifts the 7-day window correctly
   — selecting March 31 shows March 25-31, selecting March 28 shows March 22-28.
   Updates correctly when food diary changes. Closing ticket. Notes AN-BUG-001
   (Sprint 9) will break the 0% handling for skipped days.

**Unique Detail:** The PRD is explicitly incomplete — "discuss with developer and
then write" is an actual PRD note. Arjun and Shristi collaborate to define the
specification themselves. The decision to show 0% for days with no logs (rather
than null/gap) is important — AN-BUG-001 breaks exactly this case.

**Cross References:** AN-BUG-001 (Sprint 9 — 7-day trend not calculating correctly
for days with no logs) is directly caused by the 0% handling implemented here
being applied incorrectly.

---

### Ticket 10: AN-005
**Title:** Date picker synced between food diary and analysis section
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 6
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** March 17, 2025
**Resolved:** March 22, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Same calendar picker used for both food diary and analysis
- The analysis shows nutrient consumed for the selected date
- 7-day trend shows selected date and 6 days before it
- Changing date in food diary updates analysis view
- Changing date in analysis updates food diary view

**Conversation Blueprint:**
1. Shristi creates story — shared date picker between food diary and analysis. Changing
   date in one section updates the other. Asks Priya how to implement this — shared
   React Context state for the selected date?
2. Priya confirms — will lift selected_date state up to the app-level Context (same
   pattern as FoodDiaryContext from NUTR-BUG-001 fix, not yet built but planned).
   Both food diary and analysis subscribe to the same selected_date from Context.
   When either component changes the date, the Context updates and both components
   re-render with the new date.
3. Priya marks complete — same date picker component used in both sections. Date
   changes propagate via Context instantly. 7-day trend window shifts automatically
   when date changes.
4. Shristi verifies — changes date in food diary, analysis shows same date. Changes
   date in analysis, food diary shows same date. 7-day trend shifts correctly with
   date change. Closing ticket.

**Unique Detail:** Shared selected_date Context is architecturally consistent with
the FoodDiaryContext approach. Both the date sync and the nutrient totals use the
same React Context pattern — important for maintaining consistency.

**Cross References:** The shared date Context connects to NUTR-BUG-001 (Sprint 7)
where the FoodDiaryContext pattern is discussed. AN-BUG-001 (Sprint 9 — 7-day trend
for skipped days) depends on this date sync working correctly.

---

### Ticket 11: TECH-004
**Title:** Performance testing — all search and load operations under 1 second
**Tier:** 2 (4 comments)
**Type:** Technical task
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** March 17, 2025
**Resolved:** March 26, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Search results displayed within 1 second of user input
- Food database appears instantly when user adds food in diary
- Redirect to adjust portion page happens instantly after food selection
- Bar graph loads within 2 seconds of navigating to analysis
- Updates to analysis after food add/remove render within 1 second
- Nutrient recalculation within 1 second
- Meal type selection responds instantly
- Switching diary dates loads within 2 seconds
- Deletion completes within 1 second

**Conversation Blueprint:**
1. Arjun creates performance test suite — covers all PRD-specified timing requirements.
   Uses browser performance API to measure actual response times for each operation.
   Tests against: USDA search with 300,000 rows, analysis bar graph with 20 nutrients,
   diary with 30 logged foods, date switching.
2. Arjun runs tests on production-equivalent Supabase instance — most operations
   pass. One concern: analysis bar graph with 20 nutrients takes 2.1 seconds to load
   on first navigation — just over the 2-second limit. The issue is 20 separate
   database queries (one per nutrient) firing in sequence. Proposes batching all 20
   nutrient queries into one call.
3. Arjun optimises analysis endpoint — single query returns all nutrient totals for
   the selected date across all tracked nutrients. One database round trip instead of
   20. Re-tests: analysis loads in 0.8 seconds. All other operations well under limits.
4. Shristi reviews test results — all operations pass performance requirements.
   Arjun documents the test suite for regression testing after each sprint. Notes
   the 20-query-to-1-query optimisation is significant — without it analysis would
   fail performance requirements for users tracking the maximum 20 nutrients.
   Closing ticket.

**Unique Detail:** The sequential 20-query problem for analysis — one query per
nutrient exceeds the 2-second limit. Batching to a single query is a meaningful
performance optimisation that is only discovered through proper testing. The test
suite itself is valuable as a regression testing artifact.

**Cross References:** Performance requirements connect to NUTR-TASK-002 (fuzzy search
indexes), NUTR-TASK-004 (calculation engine), AN-002 (bar graph load time)

---

### Ticket 12: TECH-006
**Title:** Auto-save implementation verification across all diary actions
**Tier:** 2 (4 comments)
**Type:** Technical task
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta, Priya Nair
**Created:** March 17, 2025
**Resolved:** March 24, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Food diary entries must persist across logout, refresh, navigate away
- No manual save button — all diary actions auto-save
- Food added from any source should log instantly
- Cumulative total calculated and updated instantly without loading or refreshing
- The system should automatically save macros as user inputs value
- Once nutrient set same nutrient remains even after logout/refresh

**Conversation Blueprint:**
1. Arjun creates ticket — comprehensive verification that auto-save works correctly
   across all diary actions before MVP launch. Wants to ensure no silent failures
   where API save call fails but UI shows success. Asks Priya to review all places
   where API calls happen and confirm error handling is in place.
2. Priya audits all diary API calls — add food (POST), edit portion (PATCH), delete
   food (DELETE), add custom food (POST). All use optimistic updates from NUTR-010
   pattern. All have error handlers that revert UI state if API call fails. The one
   gap: if the network is offline when user adds food, the optimistic update shows
   success in UI but the food is lost when page refreshes because it was never saved
   to Supabase. Asks Arjun how to handle offline scenario.
3. Arjun evaluates — offline support is a V2 feature (requires service workers and
   local-first architecture). For V1 MVP the assumption is online usage. Documents
   offline as a known limitation. Adds a network status indicator to the app header
   — shows "offline" warning when network is unavailable, preventing user from
   logging food while offline (better than silent data loss).
4. Shristi approves offline warning approach — better to show clear "you're offline"
   than to silently lose data. Tests: adds food, refreshes, food persists. Logs out,
   logs back in, diary intact. Closes browser tab, reopens, diary intact. All pass.
   Closing ticket. Offline support added to V2 backlog.

**Unique Detail:** The offline data loss scenario is a genuine edge case discovered
during systematic testing. The decision to show an offline warning rather than silently
lose data is a product maturity decision. Documents a known V1 limitation explicitly.

**Cross References:** Auto-save architecture from NUTR-010 (optimistic updates) and
NUTR-024 (auto-save story). The offline limitation documented here is referenced in
launch documentation.

---

### Ticket 13: TECH-007
**Title:** Date-timezone handling — IST offset storage verification
**Tier:** 2 (4 comments)
**Type:** Technical task
**Sprint:** 6
**Priority:** P0
**Status:** Closed
**Reporter:** Arjun Mehta
**Assignee:** Arjun Mehta
**Created:** March 19, 2025
**Resolved:** March 26, 2025
**Participants:** Arjun Mehta, Shristi Sharmistha

**PRD Requirements:**
- Food diary must maintain separate log for each calendar date
- Food items must be associated with exact date when saved
- Switching between dates loads within 2 seconds
- Same date picker must be used for food diary and analysis

**Conversation Blueprint:**
1. Arjun creates ticket — final verification that the IST timezone handling from
   NUTR-022 is correctly implemented across all date-sensitive operations before
   MVP launch. Tests the midnight edge case explicitly: food logged at 11:55pm IST
   should be on the same date as food logged at 1:00am the next calendar day (because
   11:55pm IST is still before midnight UTC).
2. Arjun runs edge case tests — logs food at simulated 11:55pm IST, confirms it
   appears on the correct local date. Logs food at simulated 12:05am IST (next
   calendar day), confirms it appears on the next local date. The dual storage
   (date_string + UTC timestamp) from NUTR-022 handles both correctly.
3. Arjun tests date switching for analysis section — selected date changes the
   7-day trend window correctly using local date_string arithmetic. No UTC offset
   errors in trend date calculation.
4. Shristi verifies using an actual device set to IST timezone — all date operations
   correct. Midnight edge case passes. Date switching in both diary and analysis
   works correctly. Closing ticket. Notes NUTR-BUG-006 (Sprint 7) will later find
   a regression in future date handling despite these tests passing — the bug is
   in a specific code path not covered by these test cases.

**Unique Detail:** The IST midnight edge case is a real test scenario that most
apps miss. The dual storage approach from NUTR-022 is verified to work correctly.
The note about NUTR-BUG-006 being in an uncovered code path is important —
good testing does not prevent all bugs, only the scenarios you think to test.

**Cross References:** Implements the timezone decision from NUTR-022. NUTR-BUG-006
(Sprint 7 — future date showing wrong data) is a regression in a code path not
covered by these tests.

---

## SUMMARY OF SPRINT 6

| Ticket | Tier | Comments | Reporter | Assignee | Closed |
|---|---|---|---|---|---|
| CF-003 | T1 | 8 | Shristi | Priya/Arjun | Mar 22 |
| CF-004 | T2 | 4 | Shristi | Priya | Mar 17 |
| CF-005 | T2 | 4 | Shristi | Priya/Arjun | Mar 19 |
| CF-006 | T3 | 2 | Shristi | Priya | Mar 17 |
| CF-007 | T3 | 2 | Arjun | Arjun | Mar 20 |
| AN-001 | T2 | 4 | Shristi | Kabir/Priya | Mar 19 |
| AN-002 | T1 | 8 | Shristi | Kabir/Priya/Ananya | Mar 28 |
| AN-003 | T2 | 4 | Shristi | Kabir/Priya | Mar 21 |
| AN-004 | T2 | 4 | Shristi | Arjun/Priya | Mar 24 |
| AN-005 | T2 | 4 | Shristi | Priya | Mar 22 |
| TECH-004 | T2 | 4 | Arjun | Arjun | Mar 26 |
| TECH-006 | T2 | 4 | Arjun | Arjun/Priya | Mar 24 |
| TECH-007 | T2 | 4 | Arjun | Arjun | Mar 26 |

**Total comments Sprint 6: 56**
**MVP ships: March 31, 2025**

---

## KEY STORY THREADS IN SPRINT 6

**Thread 1 — Zero Calorie Product Decision**
CF-003 establishes the ≥ 0 rule for all nutrient values after discovering the PRD
"> 0" spec blocks legitimate zero-calorie foods. This is documented as a PRD
correction. CF-BUG-003 (Sprint 8) is Priya missing the calorie asterisk in this
same form — a small oversight in the same ticket.

**Thread 2 — Bar Graph User Testing Failure**
AN-002 is the most important discovery in Sprint 6. Real user testing reveals
the PRD-specified bar design is fundamentally confusing. The team patches with
explicit numbers (Option C) as an MVP compromise. AN-CR-001 and AN-CR-002 (Sprint 8)
are the planned proper fixes. AN-BUG-002 (Sprint 7) is an additional rendering
bug in the same bar graph.

**Thread 3 — Incomplete PRD in AN-004**
The 7-day trend PRD is literally incomplete — "discuss with developer and then write."
Arjun and Shristi define the specification themselves. This is a realistic scenario
in early-stage product development.

**Thread 4 — 20-Query Performance Issue**
TECH-004 finds that analysis with 20 nutrients fires 20 sequential queries — just
over the 2-second limit. Batching to 1 query is a significant optimisation only
caught through systematic performance testing before launch.

**Thread 5 — Offline Data Loss Risk**
TECH-006 discovers the offline scenario where optimistic updates succeed in UI but
data is lost. The network status indicator solution is pragmatic. Offline support
added to V2 backlog — an honest acknowledgement of a V1 limitation.

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 6

1. Sprint 6 dates: March 12 to March 31, 2025. MVP ships March 31.
2. Sprint 6 is the most pressure-filled sprint — team is racing to finish before
   the MVP launch date. Comments in later tickets (especially AN-002 and TECH-004)
   should reflect this pressure. "We have 3 days to launch" creates urgency.
3. AN-002 is the emotional centre of Sprint 6. Ananya's user testing report (comment 3)
   should feel like delivering difficult news the team does not want to hear right
   before launch. Kabir's response (comment 4) should show genuine self-reflection
   rather than defensiveness — a designer acknowledging their design failed real users.
4. CF-003 zero calorie debate should feel like a genuine discovery moment. Shristi
   trying to enter "0" for black coffee and finding it blocked — simple action, big
   implication. The PRD correction is handled maturely: acknowledge the error,
   make the right product decision, document it.
5. AN-004 incomplete PRD should be acknowledged explicitly in the conversation —
   Arjun or Shristi should quote the "discuss with developer and then write" PRD note
   and treat it as a collaborative specification session rather than a gap to fill
   silently.
6. TECH-007 should reference NUTR-022 explicitly — "verifying the IST timezone
   implementation from NUTR-022 before we go live." This shows systematic
   engineering practice before MVP launch.
7. The final comment on any Sprint 6 ticket closed after March 28 should mention
   MVP launching in days — giving the dataset a real sense of timeline and stakes.