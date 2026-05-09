sprint 5
# Sprint 5 Ticket Definitions — Complete Brief for GPT-4o
## February 26 to March 11, 2025

---

## IMPORTANT NOTE FOR GPT-4o
Use the same GLOBAL CONTEXT from Sprint 1 definitions. Sprint 5 completes all
remaining food logging flows — custom recipe, custom food, custom meal, supplement
logging, edit, delete, recalculation, date-wise diary, and auto-save. By end of
Sprint 5 the entire food logging feature is functionally complete. Custom food
creation also begins in this sprint (CF-001, CF-002).

---

## SPRINT 5 TICKETS

---

### Ticket 1: NUTR-011
**Title:** Select custom recipe source and search saved recipes
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 26, 2025
**Resolved:** March 3, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User must be able to select Custom Recipe as source from available food sources
- After selecting Custom Recipe user redirected to recipe menu page with all saved recipes
- Search field present to search and select recipe
- User can also scroll page to find recipe
- Search results include recipe name — partial and full matches
- Only one item selected at a time
- Once selected user redirected instantly to adjust portion page
- Recipe menu page loads instantly
- Search results returned within 1 second
- If no matching recipe found show clear "no results" message
- If user changes source or navigates away mid-process, previous input cleared
- Going back redirects to food diary page

**Conversation Blueprint:**
1. Shristi creates story — custom recipe source works exactly like USDA food database
   source from NUTR-007 but pulls from user's saved custom recipes instead of USDA.
   Same search, same redirect to adjust portion page. Asks Priya to reuse the search
   component pattern from NUTR-007 rather than building a new one from scratch.
2. Priya confirms — will abstract the search component into a reusable component
   that accepts a data source prop. Custom recipe, custom food, and USDA can all
   use the same component with different data sources. Cleaner architecture. Notes
   one difference — custom recipe database is user-specific (only their recipes)
   while USDA is shared. The API endpoint for custom recipes includes user_id filter.
3. Priya marks complete — notes that custom recipes are not yet creatable in this
   sprint (no recipe creation feature in scope). The recipe menu page will show
   empty state with message "No custom recipes created yet" for now. Recipe creation
   is a V2 feature.
4. Shristi verifies — confirms empty state shows correctly. Source switch clears
   search. No results message correct. Redirect to adjust portion instant.
   Closing ticket.

**Unique Detail:** Reusable search component abstraction — one component handles
USDA, custom recipe, and custom food sources. This architecture decision reduces
code duplication and ensures consistent behaviour across all source types.

**Cross References:** Reuses architecture from NUTR-007 (USDA source). Same pattern
applied in NUTR-012 (custom food source)

---

### Ticket 2: NUTR-012
**Title:** Select custom food source and search saved custom foods
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 26, 2025
**Resolved:** March 3, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- Custom food as source can be added in two ways — Add Food in diary OR Custom Food tab
- After selecting Custom Food user redirected to custom food main page
- Search field and scroll both available to find custom food
- All custom food matching partial or full search term should appear
- Once selected redirected instantly to adjust portion page
- Only one item selected at a time
- User can add new custom food through add button on custom food main page
- User cannot edit custom food while adding food via food diary
- If no matching food found show clear "no results" message
- If user changes source or navigates away, previous input cleared
- Going back redirects to food diary page

**Conversation Blueprint:**
1. Shristi creates story — same pattern as NUTR-011 (custom recipe) but for custom
   food. Two entry points: diary Add Food button and Custom Food tab. Asks Priya
   to note one important difference from custom recipe — on the custom food main
   page there is an Add button to create a new custom food. Custom recipe page does
   not have this. The Add button in custom food page links to CF-001 (create custom
   food — also being built this sprint).
2. Priya confirms the Add button linking to CF-001 create flow. Notes another
   difference — the custom food main page shows both food name AND calorie value
   in a two-column list per PRD, unlike custom recipe which shows name only.
   Asks Shristi to confirm the calorie display format — should it be just the
   number or number with unit like "250 kcal"?
3. Shristi confirms display format — "250 kcal" with unit for clarity. Also confirms
   the edit restriction — user cannot edit custom food while in the add-to-diary flow.
   Edit is only accessible from the Custom Food tab directly, not from the diary flow.
4. Shristi verifies — two entry points both work. Two-column list with name and
   calorie correct. Add button present and links to CF-001 create page. Edit blocked
   during diary add flow. Source switch clears search. Closing ticket.

**Unique Detail:** The two-column display (name + calorie) differentiates custom food
list from custom recipe list (name only). The edit restriction during diary flow
prevents users from accidentally modifying a food while trying to log it.

**Cross References:** Reuses architecture from NUTR-011 (reusable search component).
The Add button connects to CF-001 (create custom food). Referenced in NUTR-BUG-002
(duplicate warning not showing for custom food source — Sprint 8)

---

### Ticket 3: NUTR-013
**Title:** Log custom meal directly without portion adjust step
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 26, 2025
**Resolved:** March 4, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User must be able to connect to custom meal database
- User shown list of all custom meals created
- User can search or scroll to find required custom meal
- Search by meal name using partial or full keywords
- Only one custom meal selected at a time
- Once selected meal directly added to food diary under selected meal — NO adjust
  portion step
- Default nutrient values calculated by combining individual items in meal at
  time of selection added to food diary
- Nutrient data for selected meal adds up to other food in diary
- No limit to number of food or recipe added
- Custom meal database loads instantly once user selects custom meal
- Search results appear within 1 second
- Selected custom meal logged to diary within 1 second of selection
- In food diary meal name shown with total nutrient — not individual components
- Entire process (select source → search → log) requires no more than 3 interactions
- Nutrient data must match values saved during custom meal creation

**Conversation Blueprint:**
1. Shristi creates story — custom meal is unique because it skips the adjust portion
   step entirely. Meal is logged with default nutrient values in one tap after selection.
   This is the fastest logging path for regular meals users eat frequently. Asks Priya
   to confirm — if user selects custom meal from diary breakfast section, does the
   meal get logged to breakfast automatically or does user still select meal type?
2. Priya confirms — meal type is inherited from where user initiates the add. If user
   taps Add in breakfast section and selects custom meal, it logs to breakfast. No
   separate meal type step. However if user navigates from food database tab directly,
   they need to select meal type before logging. Same two-path behaviour as other
   sources.
3. Priya marks complete — notes that in diary view the custom meal shows as one row
   with meal name and combined nutrient totals. Individual ingredients of the meal
   are not visible in the diary. This is per PRD. If user wants to see ingredients
   they would need to go to custom meal management (V2 feature).
4. Shristi verifies — custom meal logs instantly with correct nutrient totals. Shows
   as single row in diary with meal name. Nutrient values match values set at meal
   creation. 3-interaction maximum confirmed. Closing ticket.

**Unique Detail:** Skip adjust portion step — custom meal is the only food source
that logs directly without portion adjustment. This is intentional for quick logging
of regularly eaten meals. The single-row display hiding individual ingredients is
a deliberate design choice.

**Cross References:** Same source selection pattern as NUTR-011 and NUTR-012.
Meal logging connects to NUTR-TASK-004 (calculation engine) and NUTR-016
(cumulative totals)

---

### Ticket 4: NUTR-014
**Title:** Supplement section toggle — persistent setting with discoverability
**Tier:** 1 (8 comments)
**Type:** Story — frontend design
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Kabir Sharma, Priya Nair
**Created:** February 26, 2025
**Resolved:** March 9, 2025
**Participants:** Shristi Sharmistha, Kabir Sharma, Ananya Iyer, Priya Nair

**PRD Requirements:**
- Supplement section appears ONLY if enabled by user
- A user can add food under breakfast, lunch, dinner, snacks — if supplement section
  enabled then user can enter supplement under that section
- Supplement section is a persistent global setting — once enabled it stays enabled
  across all diary dates unless explicitly disabled
- The selection should be intuitive — no more than 1-2 taps to enable
- Food diary clearly bifurcated into 3 or 4 parts (4 when supplement enabled)
- Supplement-Heavy User persona: Dev takes multiple supplements daily and uses
  Nutrient Tracking to prevent overdosing and balance nutrients like iron and calcium
- Pregnant Woman persona: Ayesha tracks supplements alongside food to stay within
  doctor-recommended targets for folate, iron, calcium

**Conversation Blueprint:**
1. Shristi creates story — supplement section hidden by default, enabled via toggle
   in user settings or diary preferences. Once enabled shows as 4th section in diary.
   Persistent across all dates. Asks Kabir to design the toggle placement and the
   visual treatment of the supplement section when enabled.
2. Kabir shares initial Figma — supplement toggle in diary settings, completely
   hidden when off. Clean minimal design. But Kabir immediately raises a concern —
   if supplement is completely hidden and the toggle is buried in settings, users
   who actually need it (pregnant women tracking folate and iron supplements,
   biohackers tracking vitamin stacks) will never discover the feature exists.
   For these user personas supplements are critical, not optional. Hidden by default
   means the feature is invisible to exactly the users who need it most.
3. Ananya agrees strongly — she has been talking to potential users and supplements
   are a major reason people choose Nutrivana over simpler calorie counters. The
   ability to track supplements and see how they combine with food nutrients is a
   key differentiator. If users cannot discover this feature the marketing message
   about supplement tracking falls apart. Recommends making it more visible even
   when off.
4. Shristi asks Kabir to design 3 options with tradeoffs — Option A: completely
   hidden, discovered only via settings (current design). Option B: always visible
   in diary as a collapsed/greyed-out section with "Enable supplement tracking"
   text. Option C: persistent subtle prompt in diary — small banner or link that
   says "Track supplements? Enable here" that appears until user makes a choice
   to enable or permanently dismiss.
5. Kabir presents 3 options with quick mockups. Option A — clean but zero
   discoverability. Option B — always visible greyed section adds clutter for users
   who do not need supplements. Option C — dismissible prompt is discoverable without
   permanent clutter. Once user enables or dismisses the prompt it disappears
   permanently. Recommends Option C.
6. Shristi makes decision — Option C with dismissible prompt. Users who need
   supplements will see the prompt and enable. Users who do not need supplements can
   dismiss permanently and never see it again. This balances clean UI with
   discoverability. Updates PRD note. Kabir to update Figma.
7. Kabir updates Figma — dismissible prompt appears below snacks section with
   clear "Enable supplement tracking" CTA and small X to dismiss permanently.
   When enabled, supplement section appears as 4th section. When dismissed, diary
   shows clean 3-section view forever. Priya implements toggle logic with persistent
   preference storage per user.
8. Shristi verifies — new user sees prompt. Enables supplement section — 4th section
   appears. Tests dismiss — prompt gone permanently. Tests supplement logging — works
   identically to other meal sections. Persistent across diary dates. Closing ticket.
   Notes the PRD will be updated to reflect Option C implementation.

**Unique Detail:** The PRD specified hidden by default with settings toggle. The team
discovers this creates a discoverability problem for the exact user personas who need
supplements most (pregnant women, biohackers). The three-option design debate with
Ananya bringing real user perspective drives the decision to Option C (dismissible
prompt). This is the second PRD override this team has made based on real UX thinking
(first was GOAL-009 tabs to single scroll). NUTR-BUG-004 (supplement section showing
without toggle enabled — Sprint 7) is caused by the conditional rendering logic
implemented here for the toggle.

**Cross References:** Connects to NUTR-006 (meal section layout). NUTR-BUG-004
(Sprint 7) — supplement section showing without toggle enabled — is a direct
consequence of the conditional rendering logic implemented here

---

### Ticket 5: NUTR-019
**Title:** Edit logged item portion size with pre-filled values
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 28, 2025
**Resolved:** March 5, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User must be able to click any logged food item in diary to edit portion size
- Previously logged portion size must be pre-filled and visible
- User can edit amount of serving, serving unit, or both
- Updated nutrient values must automatically reflect in food diary after save
- Portion adjustment and nutrient recalculation within 1 second of saving
- Updated values reflected instantly without page reload
- On clicking food item the adjust portion page must re-open with previously
  inputted value
- Add button enabled to re-update values in diary
- Back button present in adjust portion page
- If user navigates back or refreshes without saving — original value must be
  restored in both adjust portion page and diary
- Changes must apply only to the specific date and meal section where item logged

**Conversation Blueprint:**
1. Shristi creates story — clicking a logged food item reopens the adjust portion
   page from NUTR-009 but with all fields pre-filled with the currently logged values.
   User edits and taps Add to update. Cancel or back navigation restores original.
   Asks Priya to confirm state management — how will the pre-filled original values
   be preserved so they can be restored on cancel?
2. Priya explains — will store the original logged values in a separate React state
   variable (editingOriginalValues) when user enters edit mode. The adjust portion
   form fields are updated as user edits but editingOriginalValues never changes.
   On cancel or back navigation, the form state is reset from editingOriginalValues.
   On confirm, the food_log record is updated with new values via PATCH API call.
3. Priya marks complete — asks about one specific case. User edits portion size on
   January 15. Does this change affect the food log entry on January 15 only, or
   does it propagate to other dates if the same food appears on other dates?
4. Shristi confirms — edit applies ONLY to the specific food log entry on that
   specific date and meal section. Each logged entry is independent. Changing
   chicken breast portion on January 15 breakfast does not affect chicken breast
   on January 16. Priya confirms this is how PATCH /food-logs/{id} works —
   it updates one specific record by ID. Closing ticket.

**Unique Detail:** editingOriginalValues pattern for cancel/restore. The important
clarification that edits apply to one specific food log record (by ID) not all
instances of that food across dates.

**Cross References:** Reuses NUTR-009 (adjust portion page) in edit mode. Edit
triggers NUTR-TASK-004 (recalculation engine). Changes logged as new
goal_snapshot in NUTR-TASK-003 data model.

---

### Ticket 6: NUTR-020
**Title:** Delete logged item with confirmation popup
**Tier:** 2 (4 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 28, 2025
**Resolved:** March 4, 2025
**Participants:** Shristi Sharmistha, Priya Nair

**PRD Requirements:**
- User must be able to select any logged food or recipe item in diary and delete it
- Upon deletion item permanently removed from diary for that specific date and meal
- System must ask for confirmation prompt before finalising deletion:
  "Are you sure you want to delete this item?"
- Deletion must complete within 1 second after confirmation
- Food diary list must update instantly without page reload
- Delete icon must be available next to each logged item
- Confirmation popup must appear before deletion finalised
- If user cancels the confirmation, item must remain unchanged
- Deletions must only affect current user's food diary and selected date

**Conversation Blueprint:**
1. Shristi creates story — delete icon next to each food item. Tap shows confirmation
   popup. Confirm deletes permanently and updates diary instantly. Cancel leaves
   item unchanged. Asks Priya to confirm — after deletion does the diary optimistically
   remove the item from UI before API response, or wait for API confirmation?
2. Priya recommends optimistic deletion — remove from UI immediately on confirm,
   then send DELETE API call. If API fails, re-add item to UI and show error toast.
   This makes deletion feel instant per PRD requirement. Matches the optimistic
   update pattern from NUTR-010 (add food).
3. Priya marks complete — confirms deletion only affects the specific food_log record
   by ID. User data isolation enforced at Supabase RLS level (from TECH-001). Other
   users cannot delete each other's entries.
4. Shristi verifies — delete icon visible on each item. Popup appears. Confirm removes
   instantly from UI, totals update. Cancel leaves item intact. Tests rapid delete
   of multiple items — all update correctly. Closing ticket.

**Unique Detail:** Optimistic deletion pattern consistent with optimistic add from
NUTR-010. If API fails, item is re-added — this is a rollback mechanism that ensures
UI consistency.

**Cross References:** Deletion triggers NUTR-TASK-004 (recalculation). Data isolation
from TECH-001 (Supabase RLS). Pattern matches NUTR-010 (optimistic updates)

---

### Ticket 7: NUTR-021
**Title:** Recalculate totals instantly on add edit delete with debounce on slow devices
**Tier:** 1 (8 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Arjun Mehta
**Created:** February 26, 2025
**Resolved:** March 10, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- Cumulative total recalculates when user adds food, deletes food, updates portion size
- Food added: target nutrient cumulative total increases
- Food deleted: target nutrient cumulative total decreases
- Portion size changed: cumulative totals for all target nutrients update accordingly
- Recalculated totals must reflect: cumulative nutrient intake for the day,
  updated goal comparison (actual vs target)
- Nutrient recalculation must happen within 1 second after any action
- No manual refresh needed
- Changes to totals must be clearly reflected without disrupting user workflow
- Users must not have to manually save or confirm for recalculations to occur
- All recalculated values must maintain unit consistency

**Conversation Blueprint:**
1. Shristi creates story — recalculation fires on every add, edit, delete. No manual
   refresh. Within 1 second. Asks Priya to test on a low-end device to confirm
   performance before marking done.
2. Priya implements recalculation using the client-side calculation engine from
   NUTR-TASK-004 — fires on every food log array state change. Tests on a mid-range
   Android device. Single food additions are instant. But discovers a performance
   issue: when user rapidly adds multiple foods in quick succession (tapping Add 5
   times in 3 seconds), each addition triggers a recalculation. On the mid-range
   device with 15 tracked nutrients this causes visible lag — each calculation takes
   150ms and they stack, causing 750ms total lag before UI settles.
3. Priya reports to Arjun — 5 rapid additions on mid-range device causes 750ms lag,
   approaching the 1 second limit. For users with 20 tracked nutrients and fast
   hands this could exceed 1 second. Asks Arjun whether debouncing the calculation
   would help and whether PRD allows it.
4. Arjun explains — debouncing means the calculation only fires after user stops
   interacting for X milliseconds. A 200ms debounce would batch 5 rapid additions
   into one calculation run instead of 5 separate runs. But the PRD says instant
   recalculation. Does debouncing violate the PRD?
5. Shristi reads the PRD requirement — "nutrient recalculation must happen within
   1 second after an add, edit, or delete action." Key phrase: "after an action."
   A 200ms debounce means calculation fires 200ms after the last action, not
   200ms after each action. The final state is reached within 1 second of the last
   action. This is PRD compliant. Approves debounce approach.
6. Arjun and Priya debate debounce timing — too short (50ms) and rapid additions
   still trigger multiple calculations. Too long (500ms) and single actions feel
   sluggish. Settles on 100ms debounce — this batches additions made within 100ms
   of each other (fast tapping) while making single deliberate actions feel nearly
   instant.
7. Priya implements 100ms debounce on calculation engine. Re-tests rapid additions
   on mid-range device — 5 additions in 3 seconds now triggers 2-3 calculations
   instead of 5. UI settles within 300ms of the last addition. Well within 1 second.
   Single food addition still feels instant (calculation at 100ms).
8. Shristi verifies on both fast and slow interaction patterns. Single food addition:
   instant. 5 rapid additions: diary settles within 300ms of last addition. Edit
   portion: recalculates within 200ms of save. Delete: recalculates within 200ms.
   All within 1 second. Closing ticket.

**Unique Detail:** The performance issue discovery on mid-range Android devices is
a real problem in nutrition tracking apps. The debate about whether debouncing
violates the "within 1 second" PRD requirement is resolved by careful PRD reading —
"after an action" means after the last action, not each individual action. The 100ms
debounce is the product of an engineering debate about batching vs responsiveness.

**Cross References:** Uses NUTR-TASK-004 (calculation engine). Debounce referenced
in NUTR-BUG-001 (Sprint 7) context — the React Context fix there also helps
performance by ensuring calculation only runs when state actually changes

---

### Ticket 8: NUTR-022
**Title:** Separate diary per date with date picker and timezone handling
**Tier:** 1 (8 comments)
**Type:** Story — full stack
**Sprint:** 5
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta, Priya Nair
**Created:** February 26, 2025
**Resolved:** March 10, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Food diary must maintain a separate log for each calendar date
- When previous date selected: if filled shows all logged food, if empty shows
  empty diary with target nutrient columns
- When today's date selected: current day's diary with latest updates
- When future date selected: same as previous date logic
- Switching between dates must load corresponding diary within 2 seconds
- Logged food items must be associated with exact date and meal section when saved
- User can log meals for past, current, and future dates
- The date picker and analysis section must use the same calendar picker (synced)

**Conversation Blueprint:**
1. Shristi creates story — date picker in food diary header. Switching dates loads
   the corresponding food diary. Same date picker synced with analysis section.
   Asks Arjun about the data model — the goal_snapshots approach from NUTR-TASK-003
   means each diary date fetches the goal settings active on that date. Confirms
   this is how it will work.
2. Arjun begins implementation and immediately raises a critical timezone issue.
   Nutrivana targets Indian users. A user in Mumbai logging food at 11:30pm IST
   (Indian Standard Time) — that is 6:00pm UTC (Coordinated Universal Time).
   If the server stores the log date in UTC, this food gets stored as "February 26"
   in the database. But the user's local date in Mumbai is still "February 26" — so
   that is fine. The problem occurs at midnight: at midnight IST it becomes
   February 27 for the user. But UTC midnight is 12:00am UTC = 5:30am IST. So from
   midnight IST until 5:30am IST, the user's local date says "February 27" but UTC
   still says "February 26". Food logged at 1:00am IST by the user would be stored
   as "February 26" UTC — one day behind the user's perspective.
3. Priya asks — this is the same problem flagged in NUTR-TASK-003 earlier. What
   is the correct solution? Store dates in UTC and calculate offset on display?
   Or store dates in user's local timezone?
4. Arjun explains two approaches. Option A: store in UTC, add timezone offset to
   every query. This requires storing user's timezone (IST, UTC+5:30) in their
   profile and applying offset for every date calculation. Complex but clean.
   Option B: store date as the user's local date string (YYYY-MM-DD in their timezone)
   not as a UTC timestamp. Simpler — no offset calculations needed. The date_string
   "2025-02-26" means February 26 in the user's local time regardless of UTC.
5. Shristi asks — what if Nutrivana expands internationally? Users in different
   timezones would have inconsistent date representations in the database. Is
   Option B future-proof?
6. Arjun recommends Option B for V1 with a migration path — store both the local
   date_string AND UTC timestamp. For V1 all queries use date_string. In V2 if
   international expansion happens the UTC timestamp is already there for migration.
   This avoids over-engineering for V1 while not closing the door for the future.
7. Shristi approves dual storage approach — local date_string for queries, UTC
   timestamp for audit and future migration. Arjun updates food_logs table schema
   to include both columns. Priya implements date picker using user's local date.
   Tests midnight edge case: logs food at 11:55pm on February 26 (local) and
   12:05am on February 27 (local) — both appear on the correct diary dates.
8. Shristi verifies date switching — past dates show correct history, future dates
   show empty diary correctly, today shows current day. Midnight edge case verified.
   Date picker synced with analysis section confirmed. Switching dates loads within
   2 seconds. Closing ticket.

**Unique Detail:** The IST midnight vs UTC midnight timezone problem is a real and
subtle engineering challenge. The dual storage approach (local date_string + UTC
timestamp) is a pragmatic V1 solution that does not close the door on future
internationalisation. The specific example of food logged at 11:55pm IST vs 12:05am
IST appearing on different diary dates makes this conversation concrete and unique.

**Cross References:** Depends on NUTR-TASK-003 (date-stamped data model with
goal_snapshots). NUTR-BUG-006 (Sprint 7 — future date diary showing wrong data)
is caused by a date comparison logic error that this ticket was supposed to prevent
but a regression occurs later. TECH-007 (date-timezone handling) implements the
IST offset decision made here.

---

### Ticket 9: NUTR-023
**Title:** Fresh empty diary on new day
**Tier:** 3 (2 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 28, 2025
**Resolved:** March 3, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- When today's date is selected: current day's food diary with all latest updates
- When a new day begins: fresh empty diary with all target nutrient columns
- No food items from yesterday should bleed into today's diary
- Empty diary still shows all selected nutrient columns
- Switching to new date within 2 seconds

**Conversation Blueprint:**
1. Priya implements new-day reset logic — diary component reads current local date
   from NUTR-022 date system. Each diary page load fetches food_logs for the
   current date_string. Since new day = new date_string = empty food_logs query
   result, diary shows clean columns with no food items. No special reset logic
   needed — the date-based query handles it automatically.
2. Shristi verifies — tested by manually setting device date forward to next day.
   Diary shows clean empty state with all nutrient columns from current goals.
   Previous day's food visible when switching back to yesterday. Closing ticket.

**Unique Detail:** No special reset logic needed — the date_string architecture
from NUTR-022 automatically provides clean diary per day. The verification method
(manually advancing device date) is noted for future regression testing.

**Cross References:** Depends on NUTR-022 (date picker and timezone). Connects to
NUTR-TASK-003 (goal_snapshots for column display on empty dates)

---

### Ticket 10: NUTR-024
**Title:** Auto-save all diary actions
**Tier:** 3 (2 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P0
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 28, 2025
**Resolved:** March 3, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Food diary entries must persist even if user logs off, refreshes, or navigates away
- Food should be auto-saved as user adds to diary — no manual save button
- Once the nutrient is set, same nutrient remains in diary even if user logs off,
  refreshes, or moves to another page
- System should automatically save macros % as user inputs value

**Conversation Blueprint:**
1. Priya implements auto-save — every add/edit/delete action immediately calls the
   API and persists to Supabase. No local-only state that could be lost. The
   optimistic update pattern from NUTR-010 means UI updates instantly while save
   happens in background. Verifies that refreshing the page mid-session restores
   the exact state from database.
2. Shristi verifies — adds 3 foods, refreshes page, all 3 foods still present.
   Logs out, logs back in, diary intact. Closing ticket.

**Unique Detail:** Auto-save is achieved by the optimistic update architecture from
NUTR-010 — every action persists immediately. No separate auto-save mechanism needed.

**Cross References:** Auto-save architecture from NUTR-010. Session persistence
from TECH-003 (JWT + refresh tokens)

---

### Ticket 11: NUTR-025
**Title:** Edit food logs for past and future dates
**Tier:** 3 (2 comments)
**Type:** Story — full stack
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Arjun Mehta, Priya Nair
**Created:** February 28, 2025
**Resolved:** March 4, 2025
**Participants:** Arjun Mehta, Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- User can log and edit meals for past, current, and future dates
- Past date diary: shows all logged food with correct nutrient values, portion sizes,
  goal comparisons for that date
- Future date diary: same as past date — can pre-log planned meals
- Goal comparison uses goal settings active on THAT date (from goal_snapshots)
- Switching between dates must load within 2 seconds

**Conversation Blueprint:**
1. Arjun confirms backend supports any date editing — food_logs queries always filter
   by user_id AND date_string. Past and future dates use the exact same API endpoints
   as today. The goal_snapshots architecture from NUTR-TASK-003 ensures goal
   comparison uses the correct goals for that date. Priya confirms frontend date
   picker already handles this from NUTR-022.
2. Shristi verifies — logs food on a past date (manually set), logs food on a future
   date. Both persist correctly. Goal comparison uses goals active on those dates.
   Closing ticket.

**Unique Detail:** No special implementation needed — the date_string architecture
and goal_snapshots from NUTR-TASK-003 and NUTR-022 already handle this correctly.
The verification confirms the architecture works end-to-end for non-today dates.

**Cross References:** Depends on NUTR-022 (date picker), NUTR-TASK-003
(goal_snapshots for correct column display per date)

---

### Ticket 12: NUTR-026
**Title:** Duplicate food warning for same meal same date
**Tier:** 3 (2 comments)
**Type:** Story — frontend technical
**Sprint:** 5
**Priority:** P2
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair
**Created:** February 28, 2025
**Resolved:** March 5, 2025
**Participants:** Priya Nair, Shristi Sharmistha

**PRD Requirements:**
- Same food or recipe can be part of multiple meals but CANNOT be part of same meal
  again on the same date
- Warning must be shown in red when duplicate detected
- Warning disappears after 3 seconds
- Only prevents duplicates within same meal on same date — not across meals or dates

**Conversation Blueprint:**
1. Priya implements duplicate check — before confirming add on adjust portion page,
   checks food_logs for same food_id + meal_type + date_string combination. If
   duplicate found, shows red warning below Add button: "This food is already in
   your breakfast. Add again anyway?" with Yes/No options — or block entirely?
   Asks Shristi which approach.
2. Shristi confirms PRD says "cannot be part of same meal again" — block with
   warning, no option to override. Shows red warning message that disappears
   after 3 seconds. User must choose a different food or different meal. Priya
   implements accordingly. Shristi verifies warning shows for duplicate, disappears
   after 3 seconds, allows same food in different meal. Closing ticket.
   Notes NUTR-BUG-002 (Sprint 8) will find that this warning does not trigger
   for custom food source — only USDA source.

**Unique Detail:** Block not warn-and-allow. Warning auto-dismisses after 3 seconds.
NUTR-BUG-002 (Sprint 8) is seeded here — the duplicate check only works for USDA
food_id, not for custom food which uses a different ID namespace.

**Cross References:** NUTR-BUG-002 (Sprint 8 — duplicate warning not showing for
custom food source) is directly caused by the food_id check implemented here not
covering custom food IDs

---

### Ticket 13: CF-001
**Title:** Create custom food with name serving value and serving unit
**Tier:** 2 (4 comments)
**Type:** Story — full stack
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Arjun Mehta
**Created:** February 28, 2025
**Resolved:** March 7, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- 3 mandatory input fields: Food Name (alphanumeric, max 30 chars), Serving Value
  (integer > 0), Serving Unit (text — cup, glass, bowl, gram etc)
- Food name, serving value, and serving unit are all mandatory
- Mandatory fields marked with asterisk
- If food name not in correct format — border highlighted red
- Food can only be accessed by the logged-in user who created it
- Custom food database is user-specific

**Conversation Blueprint:**
1. Shristi creates story — three mandatory fields for custom food creation. Alphanumeric
   food name, numeric serving value, text serving unit. All required before moving to
   nutrient entry (CF-002). Asks Arjun to confirm the data model — custom_foods table
   in Supabase with user_id foreign key so each user only sees their own foods.
2. Arjun confirms custom_foods table design — user_id foreign key, Supabase RLS policy
   restricts each user to their own foods only. Food name max 30 characters enforced
   at database level too (VARCHAR(30)). Serving value stored as DECIMAL(10,2) to
   handle values like 2.5 cups.
3. Priya implements the create form — three input fields with real-time validation.
   Red border on incorrect format. Asterisk on all three. Character counter on food
   name showing remaining characters (30 - current length). Asks Shristi about the
   serving unit input — is it a free-text field or a dropdown with predefined units?
4. Shristi confirms free-text — PRD says "cup, glass, bowl, gram etc" suggesting
   it is examples not a fixed list. Users can enter any unit they want for their
   custom foods. This is the key difference from USDA foods which have predefined
   serving units from NUTR-009. Priya implements as free-text with placeholder
   text "e.g. cup, glass, gram". Closing ticket.

**Unique Detail:** Serving unit as free-text vs dropdown — opposite of USDA foods
(NUTR-009) where serving units are food-specific from USDA data. Custom foods let
users define their own units freely. The character counter on food name (30 max)
is a UX detail from the PRD.

**Cross References:** Directly enables NUTR-012 (custom food source in diary).
CF-002 (nutrient values) follows this ticket. CF-BUG-003 (calorie not marked
mandatory — Sprint 8) is a display error in this form.

---

### Ticket 14: CF-002
**Title:** Add macro and micronutrient values when creating custom food
**Tier:** 2 (4 comments)
**Type:** Story — full stack
**Sprint:** 5
**Priority:** P1
**Status:** Closed
**Reporter:** Shristi Sharmistha
**Assignee:** Priya Nair, Arjun Mehta
**Created:** February 28, 2025
**Resolved:** March 8, 2025
**Participants:** Shristi Sharmistha, Priya Nair, Arjun Mehta

**PRD Requirements:**
- Three columns in nutrient entry: Nutrient Category, Nutrient Name, Nutrient Value
  (input field), Default Unit
- List of all tracked nutrients with corresponding units
- Input field beside every nutrient: integer format like 20.0 or 0.5, > 0
- Calorie value is mandatory to be filled
- Calorie should have asterisk to show mandatory
- If nutrient value not in correct format — border outline highlighted red
- Nutrient category, name, and unit are system-defined — non-editable
- Values persist even if user refreshes, re-logins, or navigates away

**Conversation Blueprint:**
1. Shristi creates story — nutrient entry step after CF-001. Full list of all tracked
   nutrients with input fields. Only calorie is mandatory. All other nutrients optional.
   Asks Arjun to confirm the nutrient list source — same list from GOAL-SPIKE-002
   research or a different set?
2. Arjun confirms — same nutrient list from GOAL-SPIKE-002 and the nutrient_list
   Excel file. All nutrients that Nutrivana tracks are displayed here so user can
   fill in whichever ones they know for their custom food. The unit column is
   system-defined from the same nutrient reference data.
3. Priya implements nutrient entry form — generates input fields dynamically from
   nutrient reference list. Calorie has asterisk and mandatory validation. All other
   fields optional with decimal number validation. Notes a UX concern — the full list
   includes 30+ nutrients. Showing all at once is overwhelming. Should they be
   grouped by category (calorie, macros, vitamins, minerals) with the same accordion
   pattern used in GOAL-009?
4. Shristi approves accordion grouping — consistent with GOAL-009 micro selection
   pattern. Users can expand the category they know values for and leave others
   collapsed. Priya updates implementation. Arjun confirms values saved incrementally
   as user enters each field (auto-save per nutrient). Closing ticket.

**Unique Detail:** Consistent UX with GOAL-009 accordion pattern — grouping nutrients
by category (calorie, macros, vitamins, minerals) reduces overwhelm on a 30+ nutrient
form. Auto-save per nutrient field means partial entry is never lost.

**Cross References:** Nutrient list from GOAL-SPIKE-002. CF-BUG-004 (add button not
appearing after save — Sprint 8) is caused by the save state not propagating from
this form correctly. Connects to CF-003 (save custom food — Sprint 6)

---

## SUMMARY OF SPRINT 5

| Ticket | Tier | Comments | Reporter | Assignee | Closed |
|---|---|---|---|---|---|
| NUTR-011 | T2 | 4 | Shristi | Priya | Mar 3 |
| NUTR-012 | T2 | 4 | Shristi | Priya | Mar 3 |
| NUTR-013 | T2 | 4 | Shristi | Priya | Mar 4 |
| NUTR-014 | T1 | 8 | Shristi | Kabir/Priya | Mar 9 |
| NUTR-019 | T2 | 4 | Shristi | Priya | Mar 5 |
| NUTR-020 | T2 | 4 | Shristi | Priya | Mar 4 |
| NUTR-021 | T1 | 8 | Shristi | Priya/Arjun | Mar 10 |
| NUTR-022 | T1 | 8 | Shristi | Arjun/Priya | Mar 10 |
| NUTR-023 | T3 | 2 | Shristi | Priya | Mar 3 |
| NUTR-024 | T3 | 2 | Shristi | Priya | Mar 3 |
| NUTR-025 | T3 | 2 | Shristi | Arjun/Priya | Mar 4 |
| NUTR-026 | T3 | 2 | Shristi | Priya | Mar 5 |
| CF-001 | T2 | 4 | Shristi | Priya/Arjun | Mar 7 |
| CF-002 | T2 | 4 | Shristi | Priya/Arjun | Mar 8 |

**Total comments Sprint 5: 60**

---

## KEY STORY THREADS IN SPRINT 5

**Thread 1 — Second PRD Override: Supplement Discoverability**
NUTR-014 is the second time the team overrides a PRD design decision based on
real UX insight. First was GOAL-009 (tabs to single scroll). Here Kabir and Ananya
together push back on hidden-by-default for supplements. The dismissible prompt
solution is elegant. NUTR-BUG-004 (Sprint 7) breaks the conditional rendering
for this toggle.

**Thread 2 — Debounce vs Instant Recalculation**
NUTR-021 discovers performance lag on mid-range devices with rapid additions.
The 100ms debounce debate and PRD interpretation ("after an action" = after last
action) is a genuine engineering problem with a clever solution.

**Thread 3 — IST Timezone Architecture**
NUTR-022 establishes the dual storage approach (local date_string + UTC timestamp).
This is a V1 vs V2 pragmatic decision. NUTR-BUG-006 (Sprint 7) is caused by a
regression in date comparison logic despite this careful architecture.

**Thread 4 — Custom Food ID Namespace Gap**
NUTR-026 implements duplicate check using USDA food_id. Custom foods use a different
ID from custom_foods table. NUTR-BUG-002 (Sprint 8) occurs when duplicate check
is not extended to custom food IDs.

**Thread 5 — Reusable Search Component**
NUTR-011 introduces the abstracted search component pattern used across USDA,
custom recipe, and custom food sources. This architecture reduces code but also
means a bug in the shared component affects all three sources — as seen in
NUTR-BUG-008 (Sprint 8 — search not clearing on source change).

---

## GPT-4o GENERATION INSTRUCTIONS FOR SPRINT 5

1. Sprint 5 dates: February 26 to March 11, 2025
2. Sprint 5 is the longest sprint in the build phase — 14 tickets. Comments should
   reflect a busy, productive team working at pace to complete the full food diary.
3. NUTR-014 supplement toggle — Kabir and Ananya must sound like they genuinely care
   about the user personas. Kabir references the pregnant women and biohacker personas
   from the PRD by name. Ananya speaks from the perspective of someone who has been
   talking to potential users about what matters to them.
4. NUTR-021 debounce discussion — Arjun and Priya's conversation about 100ms vs 200ms
   vs 50ms debounce must sound like two engineers who understand both the technical
   constraints and the UX implications. Reference specific device types and test results.
5. NUTR-022 timezone issue — Arjun's comment 2 explaining the IST midnight vs UTC
   midnight problem must be technically precise. Use the specific example: 11:55pm
   IST = 6:25pm UTC → same UTC date as earlier that day. 12:05am IST = 6:35pm UTC
   (next UTC day). The dual storage solution is pragmatic — acknowledge the technical
   debt explicitly.
6. Tier 3 tickets (NUTR-023 through NUTR-026) should be brief and factual. They
   confirm existing architecture works as designed or catch one small edge case.
7. CF-001 and CF-002 should feel like the beginning of a new feature area after weeks
   of food diary work. The team is now building the custom food creator that will
   solve the Indian food gap discovered in Sprint 2 (NUTR-TASK-001 comment 5).
   Reference this connection explicitly — "this is the solution to the Indian food
   gap we found in Sprint 2."