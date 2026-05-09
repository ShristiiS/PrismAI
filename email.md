# SPRINT 1 THREADS

---

## THREAD — Database schema review

**Subject:** Schema review — few things I want to flag
**Sprint:** 1
**Date range:** January 7, 2025
**Participants:** Priya → Arjun → Priya → Arjun → Shristi
**Email count:** 5

---

**Email 1**
Date: January 7, 2025 — 11:43 AM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Just finished going through the schema. Overall it looks solid.
Two things I want to flag before you go further.

First — meal_type column in food_diary_entries. You have it as
VARCHAR. That means someone could store "Breakfast", "breakfast",
"BREAKFAST", "brkfast" — all four as different values. The diary
filtering logic on the frontend will break silently if this
happens because I will be doing exact string matching. Can we
make this an ENUM? My suggested values: breakfast, lunch, dinner,
snacks. These match what is in the PRD.

Second — display_order in nutrient_targets. The column exists
but there is nothing documenting who controls the ordering —
frontend or database? If frontend controls it I need to write
sorting logic in every component that renders nutrients. If
database controls it I just render in the order I receive.
The database owning it is cleaner. Can you confirm?

One more small thing — I noticed food_diary_entries does not
have an index on (user_id, date_string). Every diary query is
going to filter on both of these. Without a composite index
this will get slow as diary data grows.

Priya

---

**Email 2**
Date: January 7, 2025 — 12:21 PM
From: arjun@nutrivana.in
To: priya@nutrivana.in

Priya,

All three are good catches. Making the changes now.

meal_type: switching to ENUM with values breakfast, lunch,
dinner, snacks. Agreed on the string matching problem —
I should have caught this myself. ENUM is the right call.

display_order: database owns it. I will set display_order at
RDA data import time. Nutrients will come out of the database
in consistent order — you just render what you receive.
No sorting logic needed on your side.

Composite index: good catch. Adding a composite index on
(user_id, date_string) to food_diary_entries. I should also
add (user_id, created_at) to custom_foods — any query that
loads a user's custom food list will need this.

One thing I want to flag back to you: the nutrient_targets
table stores targets per user per nutrient. But what happens
if a user has NO targets set yet and opens the diary for the
first time? The frontend is going to get an empty array.
How do you want to handle that state?

Arjun

---

**Email 3**
Date: January 7, 2025 — 12:48 PM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

For the empty targets state — I will render a prompt:
"Set your nutrition goals to start tracking" with a button
that goes to the goal setting flow. Empty array from the
database, empty state UI on the frontend. Simple.

But your question made me think of a related problem. What
happens if a user HAS set goals, logs food for 2 weeks, then
changes their goals in week 3? When they navigate back to
their week 1 diary, should the nutrient columns reflect their
week 1 goals or their current week 3 goals?

If it is current goals, their historical diary is being
evaluated against targets that did not exist when they logged
that food. That feels wrong.

Is there a way to snapshot goals per date so the diary always
shows the goals that were active on that specific date?

Priya

---

**Email 4**
Date: January 7, 2025 — 1:15 PM
From: arjun@nutrivana.in
To: priya@nutrivana.in, shristi@nutrivana.in

Priya, Shristi,

Priya has identified something important. Looping in Shristi
because this is a product decision, not just a technical one.

The problem: if a user changes their goals after using the app
for a while, should their historical diary show their old goals
or their new goals?

Current schema has no way to answer this — daily_goals only
stores the current state.

Priya is right that showing current goals against historical
data is wrong. If I was tracking protein at 120g per day in
January then changed my goal to 150g in March, my January
diary should show 120g target, not 150g.

Three options:
Option A — store a copy of active goals inside every diary entry.
Accurate but expensive — duplicates goal data across every entry.

Option B — store goal change history with timestamps, query
which goal was active on each diary date.
Accurate but complex query logic, edge cases at goal change boundaries.

Option C — goal_snapshots table. Once per day, when the user
first opens the diary, take a snapshot of their current goals
and store it with today's date. Diary always reads from the
snapshot for that date. If no snapshot exists for a past date
(user did not open the app that day) fall back to the nearest
previous snapshot.

I recommend Option C. It is accurate, performant, and handles
the edge case of days the user did not open the app.

Shristi — your call on which direction we go.

Arjun

---

**Email 5**
Date: January 7, 2025 — 2:03 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

Option C. The goal_snapshots approach is correct.

One addition to the fallback logic: if no snapshot exists for
a past date AND no previous snapshot exists at all (user is
brand new and never had a snapshot), show the diary with empty
nutrient columns and a prompt to set goals.

Arjun — implement goal_snapshots as part of NUTR-TASK-003.
Add it to the technical spec as a core architectural decision.

Priya — this is a great catch. The kind of problem that would
have been reported by confused users in beta ("my old diary
shows the wrong targets") is now prevented entirely because
you read the schema carefully on day 1.

Going forward — frontend engineer reviews backend schema
before any implementation starts. This is now a rule.

Shristi

---

---

## THREAD — January investor update

**Subject:** Nutrivana — January kickoff update
**Sprint:** 1
**Date range:** January 2-5, 2025
**Participants:** Shristi → Ravi → Shristi
**Email count:** 3

---

**Email 1**
Date: January 2, 2025 — 9:15 AM
From: shristi@nutrivana.in
To: ravi.kapoor@seedfund.in

Hi Ravi,

Happy New Year. Sprint 1 kicked off yesterday.

Quick update on where things stand:

Team is in place. Arjun leading infrastructure, Priya joining
January 7, Kabir and Ananya full time from today.

This sprint is entirely architecture and research — no feature
code until Sprint 2. The decisions we make this sprint (database
schema, authentication strategy, EER formula implementation)
will be the foundation everything else builds on. Spending 2
weeks here saves weeks of rework later.

Specific Sprint 1 deliverables:
Database schema with RLS policies for user data isolation.
JWT authentication with 30-day refresh token so users never
see the login screen unnecessarily.
EER formula research — 15 variants across age, gender, activity
level. This is the calorie science behind every goal we set.
RDA micronutrient targets for all 40+ nutrients we plan to track.

MVP target: March 31. Beta: April 1. Public launch: May 1.
These dates are fixed. The team knows it.

Waitlist: 23 users from Instagram bio link. Slow but quality
is good — Ananya screened several and they are exactly our
target (health-conscious, Indian, frustrated with existing apps).

One thing I want to flag early: USDA food database integration
starts next sprint. I have a hypothesis that Indian foods are
poorly covered in the USDA database. If that hypothesis is
correct it changes our product approach. I will have a clear
answer for you by end of January.

Shristi

---

**Email 2**
Date: January 3, 2025 — 11:30 AM
From: ravi.kapoor@seedfund.in
To: shristi@nutrivana.in

Shristi,

Good to hear the team is in motion.

Two questions:

First — the USDA database hypothesis you mentioned. If Indian
foods ARE poorly covered, what is your contingency? A nutrition
app for Indian users that cannot find Indian food is not a
nutrition app for Indian users.

Second — you mentioned EER formula has 15 variants. What happens
if a user enters incorrect information about themselves (wrong
age, wrong activity level) to get a higher calorie budget?
Is there a safeguard or do you trust the user's inputs?

Ravi

---

**Email 3**
Date: January 4, 2025 — 8:45 AM
From: shristi@nutrivana.in
To: ravi.kapoor@seedfund.in

Ravi,

Both good questions.

On the USDA coverage: if Indian foods are poorly covered we
build a Custom Food Creator that lets users add their own entries
with accurate nutrient data. This is actually a better long-term
solution than us manually maintaining an Indian food database —
users build it themselves and every entry makes the database
more valuable for every future Indian user. The contingency is
already designed. I just need to confirm whether we need to
fast-track it to Q1 or can leave it for Q2.

On users gaming the EER formula: we have a BMR safety floor.
No calorie goal can be set below the user's Basal Metabolic Rate
— the minimum calories needed to maintain basic organ function
at complete rest. If a user tries to set a goal below their BMR
(which would be medically dangerous) the app shows a warning
and requires active confirmation. We cannot stop users from
making bad decisions but we make sure they are informed ones.

The 15 EER variants are not something users choose — the formula
selects the appropriate variant automatically based on age and
gender. The only user inputs are age, gender, height, weight,
and activity level. We show users what each activity level means
in plain language so they do not accidentally choose wrong.

Shristi

---

---

# SPRINT 2 THREADS

---

## THREAD — USDA rate limit and Indian food gap

**Subject:** USDA API — blocker on day 1
**Sprint:** 2
**Date range:** January 15-22, 2025
**Participants:** Arjun → Shristi → Arjun → Shristi → Arjun →
full team
**Email count:** 6

---

**Email 1**
Date: January 15, 2025 — 9:47 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Blocker on day 1. The USDA FoodData Central API has a hard rate
limit of 1,000 requests per hour per API key. I discovered this
at 9 AM when I started testing the integration.

1,000 requests per hour sounds like a lot until you think about
what our app does. A user who searches for food 10 times in a
session and then views their diary which makes nutrient lookup
calls — that is already 15-20 API requests for one user in one
session. At 50 concurrent users we hit the rate limit in minutes.

Real-time API is not viable. We need to switch to bulk import —
download the entire USDA dataset locally into Supabase and run
all searches against our own database.

What this means practically:
The bulk download is approximately 2.1GB of JSON.
Import will take 1-2 days to process and index.
After that, search runs entirely against our Supabase instance —
no external API calls, no rate limits, better performance.

One significant upside: without the API latency, search response
time will be faster. Real-time API calls average 300-500ms.
Our own Supabase query will average 100-200ms.

Downside: we are now responsible for keeping the data fresh.
USDA updates their database periodically. We will need a process
to re-import updates. I suggest quarterly re-import. For V1 this
is fine — the nutrient values for chicken breast do not change.

Need your decision today. If you approve bulk import I start the
download immediately. If you want to explore other options we
lose 2-3 days.

Arjun

---

**Email 2**
Date: January 15, 2025 — 10:12 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Bulk import approved. Start the download now.

One question: does this affect any other Sprint 2 tickets?
NUTR-TASK-002 (fuzzy search) was designed assuming real-time
API. Does the bulk import change the search architecture?

Also — how does our search compare to what HealthifyMe or
MyFitnessPal users experience? If our search is noticeably
faster that is a genuine product advantage worth knowing.

Shristi

---

**Email 3**
Date: January 15, 2025 — 10:31 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Download started. Approximately 6 hours to complete at current
speed, then 4-6 hours to process and index. Should be fully
searchable by tomorrow morning.

On NUTR-TASK-002: the fuzzy search implementation does not
change significantly. Instead of querying the USDA API endpoint
we query our own Supabase table. The fuzzy matching logic
(handling misspellings like "chiken" returning "chicken") is
all on our side regardless.

One thing I need to figure out: the USDA search API supports
trigram similarity natively. Our Supabase Postgres instance also
supports trigrams via the pg_trgm extension. But trigram matching
requires a minimum 3-character input to return results. "Dal" is
3 characters — that should work. But "D" or "Da" returns nothing.
Most users probably type at least 3 characters before stopping
but I want to confirm the minimum character behaviour works
correctly before marking NUTR-TASK-002 done.

On competitor speed: I used MFP this morning. Their food search
results appeared in approximately 600-800ms. HealthifyMe was
similar. Our target is under 200ms average. We will be
significantly faster if we hit that.

One more thing — I started testing the database with Indian
foods while the bulk import runs. Preliminary results are not
good. Will send separately when I have the full picture.

Arjun

---

**Email 4**
Date: January 17, 2025 — 8:22 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Bulk import complete. 300,847 foods in Supabase.
Search indexes built. Average search response time: 180ms.

But I need to show you the Indian food results.

I spent yesterday evening testing every common Indian food I
could think of. Here is what the database returns:

Chapati — 0 results
Roti — 4 results (all are "Roti canai" — Malaysian flatbread,
completely different food, different macros)
Dal (any variety — dal tadka, dal makhani, moong dal) — 0 results
Paneer — 3 results (all labelled as "Paneer, Indian cheese from
US restaurant", macros are for restaurant-prepared paneer with
oil and spices, not homemade paneer which is what users actually eat)
Idli — 0 results
Dosa — 0 results
Poha — 0 results
Upma — 0 results
Rajma — 0 results
Chole — 0 results
Sabzi (any variety) — 0 results
Biryani — 2 results (both are "Indian restaurant biryani"
from US nutritional databases, completely wrong macros for
homemade biryani)
Khichdi — 0 results
Paratha — 0 results

The USDA database was built for American dietary patterns.
It has 47 varieties of American cheese and 23 varieties of
corn dogs. It has zero varieties of dal and zero varieties
of roti.

This is not a minor gap. This is a fundamental problem for
our target users. I wanted you to have the full picture
before we discuss in today's meeting.

Arjun

---

**Email 5**
Date: January 17, 2025 — 9:05 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Thank you for the full picture. This is exactly the kind of
thing I needed to know before the meeting.

Sending a team email now. We are going to talk through options
together.

Shristi

---

**Email 6**
Date: January 22, 2025 — 4:45 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in,
kabir@nutrivana.in, ananya@nutrivana.in

Team,

Following today's meeting — decision made. Custom Food Creator
is fast-tracked to Sprints 5-6.

The Indian food gap is not a nice-to-have fix. It is the core
problem our users have with every existing app. Ananya has been
collecting waitlist feedback for 3 weeks. 61% of users named
this exact problem without being prompted.

What changes:
CF-EPIC-001 created in Jira today.
I will personally research and add the top 30 Indian foods before
beta launch using IFCT (Indian Food Composition Tables) data.
Arjun — please flag what backend work CF-EPIC-001 needs and
when it should start relative to the other sprint work.

One thing I want to be clear about: the custom food feature is
not a workaround for a database problem. It is a genuine product
feature. Users who create their own food entries are making the
app personal to them. That personalisation will drive retention.
I believe this more strongly than almost anything else about
the product right now.

Shristi

---

---

## THREAD — Sprint 2 investor update

**Subject:** Nutrivana — end of January update
**Sprint:** 2
**Date range:** January 28-30, 2025
**Participants:** Shristi → Ravi → Shristi
**Email count:** 3

---

**Email 1**
Date: January 28, 2025 — 7:30 PM
From: shristi@nutrivana.in
To: ravi.kapoor@seedfund.in

Ravi,

Sprint 2 complete.

USDA integrated — 300,847 foods, search averaging 180ms.
EER formula implemented — all 15 variants verified against
USDA reference values. Arjun wrote unit tests for every variant
including the edge cases (BMR floor, activity level multiplier
boundaries). The calorie science is solid.

The Indian food gap you asked about in your last email — it was
worse than I expected. Chapati: 0 results. Dal: 0 results. Paneer:
3 results, all wrong. We fast-tracked Custom Food Creator to
Sprints 5-6. I am personally researching and adding the top 30
Indian foods before beta using IFCT data.

One thing I learned this sprint that I want to share: the USDA
database gap is actually an opportunity. MyFitnessPal has the
same problem and has had it for 15 years. They are too large to
fix it — their database is crowdsourced and inconsistent.
We are small enough to seed it correctly and build a feature
(Custom Food) that makes users active contributors to solving it.

Waitlist at 67. Targeting 150 by March 31.
Next sprint: complete goal setting (macro + micronutrient).
Sprint 4: food diary becomes demoable for the first time.

Shristi

---

**Email 2**
Date: January 29, 2025 — 10:15 AM
From: ravi.kapoor@seedfund.in
To: shristi@nutrivana.in

Shristi,

The USDA gap framing is interesting. You are right that MFP
has never solved it — their crowdsourced data for Indian foods
is notoriously inaccurate.

One concern: if users create custom foods and those entries
are private per user, you have 1000 users each creating their
own "Chapati" entry with slightly different macros. You end up
with 1000 versions of the same food. How do you prevent that
from becoming a quality problem?

Ravi

---

**Email 3**
Date: January 30, 2025 — 9:00 AM
From: shristi@nutrivana.in
To: ravi.kapoor@seedfund.in

Ravi,

You have identified the exact V2 product decision we need to
make — when do custom foods become community foods?

For V1 the custom foods are private per user. This is the safe
choice — we cannot verify user-submitted nutrition data for
accuracy, and incorrect macros for a food someone eats every
day is a meaningful health problem.

The V2 solution we are planning: a "suggest to community" flag
that users can set on their custom food entries. We review
suggested foods against IFCT reference data before making them
available to all users. Quality-gated crowdsourcing rather than
open crowdsourcing.

For beta we seed the top 30 Indian foods ourselves using verified
IFCT data. These become the quality anchor — if a user searches
"chapati" they find our verified entry first, and can add their
own variant if their homemade recipe has different macros.

I expect by the time we get to the community foods decision
we will have data on how many users are creating duplicate
entries for the same food. That data will tell us exactly when
and how to build the community layer.

Shristi

---

---

# SPRINT 3 THREADS

---

## THREAD — Floating point bug and USDA data quality

**Subject:** Floating point issue in macro validation — and something else
**Sprint:** 3
**Date range:** February 3-5, 2025
**Participants:** Priya → Arjun → Priya → Arjun → Shristi
**Email count:** 5

---

**Email 1**
Date: February 3, 2025 — 3:22 PM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Found a bug in GOAL-007 (macro validation) that I need your
input on.

When a user enters 33.33 / 33.33 / 33.34 for protein / carb /
fat split, JavaScript evaluates the sum as 99.99999999997 rather
than 100. My validation checks sum === 100 and rejects it.
The user did nothing wrong — this is a valid equal split.
But the app tells them it is invalid.

The fix for this specific case: parseFloat(sum.toFixed(2))
rounds the sum to 2 decimal places before validation.
99.99999999997 becomes 100.00. Validation passes.

My question is whether we apply this fix everywhere we display
or validate nutrient values, not just in macro validation.
If we do not, the same floating point problem will appear in
other places — calorie totals, individual nutrient tracking,
percentage-of-goal calculations.

My recommendation: yes, apply universally. Any number that
comes from a mathematical operation (not a raw database value)
gets rounded to 2 decimal places before display or validation.

Can you confirm before I proceed?

Priya

---

**Email 2**
Date: February 3, 2025 — 4:05 PM
From: arjun@nutrivana.in
To: priya@nutrivana.in

Priya,

Yes to the universal standard. parseFloat(toFixed(2)) for all
calculated values. This is the right call.

But I want to add something you may not have considered.

The floating point issue you found is about our JavaScript
calculations. There is a separate but related problem with the
USDA data itself.

I noticed this while building the search indexes. The USDA
database is inconsistent in how it stores nutrient values:

Some nutrients are stored as integers (e.g., Sodium: 142)
Some are stored to 1 decimal place (e.g., Protein: 25.4)
Some are stored to 3 decimal places (e.g., Riboflavin: 0.124)
Some are stored to 4 decimal places (e.g., Folate: 0.0241)

When we display these values in the diary and analysis screens
we will show different decimal precision for different nutrients
which looks inconsistent and confusing.

Example: a user sees "Protein: 25.4g" and "Folate: 0.0241mg"
side by side. The folate value looks like a rounding error.

I think we need a display precision rule per nutrient unit:
- Values in grams (protein, carbs, fat, fibre): 1 decimal place
- Values in milligrams (iron, calcium, sodium): 0 decimal places
- Values in micrograms (folate, B12, D): 1 decimal place
- Values as percentages (DV%): 0 decimal places

This is not in the PRD. Should I add it to the technical spec?

Arjun

---

**Email 3**
Date: February 3, 2025 — 4:47 PM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Yes — please add the display precision rule to the technical spec.
This is exactly the kind of thing that is invisible when you design
the feature but looks terrible when a real user sees it.

One addition to your rules: what about serving sizes? USDA stores
serving weights to 2 decimal places for some foods (e.g., "1 cup
(156.00g)" for oats). Showing two decimal places on serving weight
is unnecessary. Suggest: serving weight always displayed as integer
grams. "156g" not "156.00g."

Also — what do we show when a nutrient value is 0? Some foods
have genuinely 0 values for certain nutrients (e.g., plain water
has 0mg of everything). We should show "0" not "0.0" or "—".
The dash symbol (—) should only be used when a nutrient value
is null in the database (data not available), not when it is
actually zero.

Priya

---

**Email 4**
Date: February 4, 2025 — 9:15 AM
From: arjun@nutrivana.in
To: priya@nutrivana.in, shristi@nutrivana.in

Priya, Shristi,

Looping in Shristi because this has become a broader product
decision.

Summary of what Priya and I have been discussing: we need a
formal display precision standard for all nutrient values across
the entire app. This is not in the PRD.

Proposed rules:
1. Grams (protein, carbs, fat, fibre, sugar): 1 decimal place
2. Milligrams (iron, calcium, sodium, potassium): 0 decimal places
3. Micrograms (folate, B12, vitamin D): 1 decimal place
4. Percentages (DV%): 0 decimal places
5. Serving weights: integer grams only
6. Zero values: show "0" not "0.0" or "—"
7. Null values (data not available): show "—" not "0"

The distinction between 0 and null is important. If we show
"—" for both genuine zero values and missing data, users cannot
tell if folate is 0mcg (this food genuinely has no folate) or
if folate data is simply not in the USDA database.

Shristi — does this need to go in the PRD? Or is technical spec
sufficient?

Arjun

---

**Email 5**
Date: February 4, 2025 — 11:30 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

The zero vs null distinction is a genuine product decision —
add it to the PRD and technical spec both.

For users tracking micronutrients for health reasons (which is
our differentiating feature), seeing "—" when they expect a
number will create confusion and support tickets. The distinction
between "this food has no folate" and "folate data is unavailable"
is meaningful for a pregnant user tracking folate intake.

Full display precision rules approved. Arjun add to technical
spec. I will add the zero/null distinction to the PRD under
Data Display Standards.

One addition: for the diary totals row (the cumulative daily
total at the bottom) — always show 1 decimal place regardless
of unit. The daily total is where users make decisions about
their remaining intake. "47.3g protein remaining" is more
useful than "47g" when someone is deciding whether to add a
protein source.

Shristi

---

---

## THREAD — GOAL-009 micronutrient list design

**Subject:** Micronutrient list — tabs vs scroll, user feedback
**Sprint:** 3
**Date range:** February 5-8, 2025
**Participants:** Ananya → Kabir → Priya → Shristi → Kabir
**Email count:** 5

---

**Email 1**
Date: February 5, 2025 — 10:15 AM
From: ananya@nutrivana.in
To: kabir@nutrivana.in

Kabir,

I showed the tabbed micronutrient list prototype to 3 waitlist
users yesterday evening (informal — just screen shares over
Google Meet, no script).

The results are not good. 2 out of 3 users completed the task
of selecting their micronutrients to track but both missed
entire categories. One user (Meera, 28, software engineer
Bangalore) selected only Vitamins and clicked done without
noticing the Minerals and Electrolytes tabs existed. She would
have set up tracking for vitamins only.

The third user (Rohan, 24) found the tabs fine but said
"I almost missed the other tabs — I had to look carefully to
see them."

Only one user found the tabs intuitive. 2 out of 3 is not
good enough for a setup screen users only see once.

What would a scroll-based layout look like for this screen?

Ananya

---

**Email 2**
Date: February 5, 2025 — 11:30 AM
From: kabir@nutrivana.in
To: ananya@nutrivana.in, priya@nutrivana.in

Ananya, Priya,

The tabs are a problem I suspected but hoped users would
not notice. They clearly do notice.

Quick sketch of the scroll alternative: instead of tabs,
all 40+ micronutrients in a single scrollable list grouped
by category. Category names (Vitamins, Minerals, Electrolytes,
Other) become sticky headers that stay visible as you scroll
within a section. A "Select all in this category" checkbox
next to each sticky header lets users quickly select or
deselect an entire category.

The key difference in discoverability: with tabs you have to
know the tabs exist and click each one. With scroll you can
see everything from the first screen — you just scroll down.
Users who only want to track vitamins can stop scrolling when
they finish vitamins. Users who want everything see it all.

Priya — technically, which is simpler to implement?

Kabir

---

**Email 3**
Date: February 5, 2025 — 12:20 PM
From: priya@nutrivana.in
To: kabir@nutrivana.in, ananya@nutrivana.in

Kabir, Ananya,

Scroll is actually simpler to implement than tabs.

Tabs require: active tab state management, conditional rendering
of active tab content, tab switching animations, making sure
scroll position within a tab is preserved when switching back.

Scroll requires: render the full list once, implement sticky
headers (straightforward with CSS position: sticky), add
"select all" checkbox logic per category.

The one complexity with scroll: on mobile, 40+ nutrients is
a long list. We need a search bar at the top so users can
jump directly to a specific nutrient (e.g., someone who knows
they need to track folate specifically can search "folate"
rather than scrolling through the entire list).

I had already started implementing tabs and will need to restart.
I estimate 2 extra days. But scroll is the right choice.

Priya

---

**Email 4**
Date: February 5, 2025 — 2:45 PM
From: shristi@nutrivana.in
To: kabir@nutrivana.in, priya@nutrivana.in, ananya@nutrivana.in

Team,

Single scroll approved. PRD updated.

This is a PRD override. The original PRD specified tabs based
on my assumption that grouping into categories would reduce
cognitive load. Ananya's user testing shows the opposite —
tabs hide options rather than organising them.

Kabir — please update the Figma design by February 7 with:
Single scroll layout, sticky category headers, search bar
at top, "select all in category" checkboxes.

Priya — restart implementation once Kabir confirms designs.
2 extra days is worth it.

One note for the future: this is the second design decision
in 5 weeks where informal user testing caught a problem that
we would not have found ourselves (the first was the meal_type
enum). Ananya should be in every design review from this point
forward, not brought in after designs are finalised.

Shristi

---

**Email 5**
Date: February 7, 2025 — 4:30 PM
From: kabir@nutrivana.in
To: priya@nutrivana.in, ananya@nutrivana.in, shristi@nutrivana.in

Team,

Figma updated. Single scroll with sticky headers, search bar,
select all per category.

One design detail worth noting: the search bar filters the list
in real time as the user types. I implemented this as a filter
(hides non-matching nutrients) rather than a jump-to (scrolls
to the first match). The difference: filter shows only matching
nutrients which is useful if a user types "B" and wants to see
all B vitamins together. Jump-to shows everything and just moves
the viewport which is less useful on a long list.

Also added a "selected" counter in the top right that shows
"X of 40 selected" and updates as users tap nutrients. This
gives users a sense of how many they have selected and makes
it obvious when they have accidentally deselected something.

Priya — link to updated Figma in Notion. Let me know if anything
looks off when you start implementing.

Kabir

---

---

# SPRINT 4 THREADS

---

## THREAD — Serving units and portion size

**Subject:** USDA serving units — not what we expected
**Sprint:** 4
**Date range:** February 16-18, 2025
**Participants:** Arjun → Kabir, Priya, Shristi → Priya → Arjun → Shristi
**Email count:** 5

---

**Email 1**
Date: February 16, 2025 — 11:15 AM
From: arjun@nutrivana.in
To: kabir@nutrivana.in, priya@nutrivana.in, shristi@nutrivana.in

Team,

Discovery during NUTR-009 that changes the portion size UI.

The USDA database does not use generic serving units. Every food
has its own specific serving unit based on how that food is
conventionally measured. Some examples:

Oats, rolled, dry: 1 cup = 156g
Spinach, raw: 1 cup = 30g
Chicken breast, roasted: 1 serving = 85g
Olive oil: 1 tablespoon = 13.5g
Almonds, raw: 1 oz = 28.35g
Milk, whole: 1 cup = 244g
Honey: 1 tablespoon = 21g
Banana, raw: 1 medium (7" to 7-7/8") = 118g

These are actual USDA entries. The database is very precise about
how each food is conventionally measured.

The PRD assumed I would present a generic dropdown: cup,
tablespoon, gram, ounce. This assumption was wrong and the
food-specific units are actually better UX.

Proposed new approach: the portion input shows the food's own
USDA serving unit as the default. As the user adjusts the
quantity slider or input, the gram equivalent updates in real
time. Users can toggle to "enter grams directly" if they prefer.

Kabir — can you look at the Figma and tell me if this needs
a design update? The portion input component will need to
show the food-specific unit name dynamically rather than
a static dropdown.

Arjun

---

**Email 2**
Date: February 16, 2025 — 2:30 PM
From: kabir@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in, shristi@nutrivana.in

Arjun,

I like this more than the generic dropdown. The food-specific
units are how people actually think about food.

Nobody measures their oat intake in grams in the kitchen.
They scoop a cup. Nobody measures chicken in tablespoons.
They eat a serving. The USDA units match real kitchen behaviour.

One design question: what do we do when the USDA unit is
something very specific like "1 medium (7" to 7-7/8") banana"?
That string is too long to display cleanly in the UI.
Do we truncate to "1 medium" or do we show the full string?

Also — what about foods that have multiple valid serving options
in the USDA database? Milk has entries for both "1 cup" and
"100g" as base serving units. Do we pick one or let users choose?

Kabir

---

**Email 3**
Date: February 16, 2025 — 3:45 PM
From: priya@nutrivana.in
To: arjun@nutrivana.in, kabir@nutrivana.in, shristi@nutrivana.in

Arjun, Kabir,

On the long unit strings like "1 medium (7" to 7-7/8") banana":
I suggest we display just the first part before the parenthesis
for UI purposes — "1 medium banana." The gram equivalent shows
in real time so users can see exactly what they are logging
regardless of how we truncate the label.

On multiple serving options per food: this is actually common.
Looking at USDA data, many foods have a "household measure"
unit and a "100g" unit both defined. I think we should default
to the household measure (the one with a real-world unit like
cup or oz or serving) and give users a toggle to switch to 100g
input if they prefer. Some users — particularly people with
kitchen scales — prefer to weigh everything in grams. We should
support both without making one feel secondary.

Implementation note: I will need Arjun to add a household_serving_unit,
household_serving_size_g, and has_gram_option boolean to the
food search API response. This is a small schema addition but
I cannot build the UI without it.

Priya

---

**Email 4**
Date: February 17, 2025 — 9:00 AM
From: arjun@nutrivana.in
To: priya@nutrivana.in, kabir@nutrivana.in, shristi@nutrivana.in

Priya, Kabir, Shristi,

Schema updated. Adding household_serving_unit, household_serving_size_g,
and has_gram_option to the usda_foods table. Search API response
updated to include these fields.

Also discovered something during the update: 23 foods in the
USDA database have their micronutrient data stored in reversed
column order — the import script maps column positions and 23
records have calcium where sodium should be and vice versa.
These are all foods in a specific USDA dataset (FNDDS — Food
and Nutrient Database for Dietary Studies) that uses a different
column schema from the main SR Legacy dataset.

The practical impact: for those 23 foods, users who log them
would see calcium contributing to their sodium goal and sodium
contributing to their calcium goal. For a pregnant user tracking
calcium for fetal bone development this could be a real problem.

I have fixed the 23 records in our Supabase database. But I
want to run a full audit of all FNDDS entries — there may be
more. Will do this tonight.

Arjun

---

**Email 5**
Date: February 17, 2025 — 10:30 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in, kabir@nutrivana.in

Team,

Arjun — fix the 23 records and do the full FNDDS audit.
Document the fix in the technical spec under Data Quality.

This is the kind of problem that would have been catastrophic
if it reached beta users. Someone logging salmon and seeing
their sodium spike instead of their calcium is going to think
our data is wrong — and they would be right. Thank you for
catching it.

General principle: any time we are importing data from an
external source that uses a different schema, we write an
explicit data quality validation that checks the import results
against known reference values before we mark the import done.

For the serving units approach: food-specific units as default
with gram toggle approved. Priya proceed with implementation.
Kabir please update Figma to show the household unit as the
default display with the gram toggle as a secondary option.

Shristi

---

---

## THREAD — FoodDiaryContext deferral

**Subject:** FoodDiaryContext — I need to say something
**Sprint:** 4
**Date range:** February 19-20, 2025
**Participants:** Shristi → Arjun → Shristi → Arjun
**Email count:** 4

---

**Email 1**
Date: February 19, 2025 — 6:15 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Sending this separately from the team thread because I want
to be direct with you without it becoming a group discussion.

FoodDiaryContext has been identified as needed in Sprint 4.
It is being deferred to Sprint 5 because NUTR-009 took longer
than expected. I understand why. NUTR-009 was genuinely more
complex than estimated.

But I want you to understand the risk I am worried about.

Every sprint we build more components that will eventually need
FoodDiaryContext to work correctly together. The diary totals
component. The per-meal breakdown component. The analysis screen
we are building in Sprint 6. Each component we build without
FoodDiaryContext is a component that will need to be retrofitted
or refactored when FoodDiaryContext eventually goes in.

The later we implement it the more components have been built
assuming it does not exist. That is technical debt that compounds.

I also want to be honest that this is the second time we have
deferred architectural work in favour of feature work (the first
was the offline data handling note in Sprint 3). I see a pattern
forming and I want to name it before it becomes a Sprint 6 problem.

What would it take to implement FoodDiaryContext as the very
first task in Sprint 5? Not alongside other Sprint 5 work —
first, before anything else.

Shristi

---

**Email 2**
Date: February 19, 2025 — 7:30 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

You are right and I know you are right.

The honest reason FoodDiaryContext keeps getting deprioritised:
it is unglamorous architectural work that does not show up in
the demo. When Priya asks "should I implement FoodDiaryContext
or should I implement the date picker feature that users will
actually see" the date picker feels more urgent. It should not
feel more urgent but it does.

The technical risk you described is real. Every component
currently reads diary state from its own local state. When
food is added to the diary, the diary totals component updates
because it is the one making the POST request. But the analysis
screen does not update because it has its own separate state
object. The 7-day trend graph has its own separate state object.
Right now this only shows up as "you need to refresh the page
to see updated analysis" — an annoyance. But in beta it will
show up as a confusing bug where the diary and analysis show
different numbers for the same data.

Sprint 5: FoodDiaryContext is the first task Priya and I start
on day 1. Before any other Sprint 5 ticket. I am putting this
in writing so you have it.

One question: should we create a specific Jira ticket for
FoodDiaryContext so it is tracked formally and cannot be
quietly deprioritised without it showing up in the sprint
health metrics?

Arjun

---

**Email 3**
Date: February 19, 2025 — 8:00 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Yes. Create a Jira ticket for FoodDiaryContext today.
Add it to the Sprint 5 backlog as P0. I want to see it in
the sprint health report from day 1 of Sprint 5.

The pattern you described — feature work feels more urgent
than architectural work because it shows up in the demo —
is a product management failure, not an engineering failure.
I should have caught it earlier and made the prioritisation
explicit. I did not. That is on me.

Going forward: every sprint retrospective will explicitly ask
"what architectural work did we defer this sprint?" If the
answer is anything other than "nothing" I want to understand
why and whether it was the right call.

Shristi

---

**Email 4**
Date: February 20, 2025 — 9:30 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Jira ticket created. NUTR-TASK-005: Implement FoodDiaryContext.
Added to Sprint 5 backlog as P0.

Description I wrote in the ticket: "Shared React context for
food diary state. All components that read diary data (diary
totals row, per-meal breakdown, analysis bar graph, 7-day trend
graph) must read from this shared context rather than maintaining
independent local state. Without this, adding, editing, or
deleting a food entry updates the component that initiated the
action but not other components showing the same data."

Acceptance criteria: adding a food entry in the diary updates
the totals row, the per-meal breakdown, AND the analysis screen
simultaneously without page refresh.

I have also documented in the ticket: this was deferred from
Sprint 4. If it is deferred again from Sprint 5 without explicit
written approval from Shristi, it should be treated as a sprint
failure, not a scope adjustment.

Arjun

---

---

# SPRINT 5 THREADS

---

## THREAD — Supplement toggle decision

**Subject:** Supplement section — three options, need a decision
**Sprint:** 5
**Date range:** March 1-4, 2025
**Participants:** Kabir → Ananya, Priya → Shristi → Arjun → Shristi
**Email count:** 5

---

**Email 1**
Date: March 1, 2025 — 3:00 PM
From: kabir@nutrivana.in
To: ananya@nutrivana.in, priya@nutrivana.in

Ananya, Priya,

Need your input on the supplement section design before I
escalate to Shristi. NUTR-014 in Jira.

The PRD says the supplement section should be always visible
in the food diary. But I have been prototyping this and it does
not feel right. The supplement section takes up real estate
at the bottom of the diary for every user including the majority
who probably do not take supplements.

Three options I am considering:

Option A: Always visible (what PRD says). Pro: discoverable.
Con: visual noise for 60-70% of users who never use it.

Option B: Hidden in settings. Pro: clean diary for everyone.
Con: very hard to discover — users who SHOULD use it probably
never find it.

Option C: Dismissible prompt on first diary visit. A subtle
overlay appears once asking "Do you take supplements? Track
them here." User can enable (goes to supplement setup) or
dismiss (prompt never shows again, but toggle available in
diary settings). This is the pattern some apps use for
optional feature discovery.

Ananya — from a user perspective, how do you think Indian
health-conscious users think about supplements? Are they
common enough that discoverability matters significantly?

Priya — which is most implementable cleanly?

Kabir

---

**Email 2**
Date: March 1, 2025 — 4:30 PM
From: ananya@nutrivana.in
To: kabir@nutrivana.in, priya@nutrivana.in

Kabir, Priya,

From user interviews and the waitlist survey, supplements are
more common in our target demographic than I expected. Not just
protein powder — we are talking vitamin D, omega-3, iron
supplements, B12, multivitamins. A significant number of our
waitlist users are already taking supplements and tracking them
manually alongside their food.

Three specific user segments who will care about supplement
tracking:
1. Fitness users tracking protein intake (whey protein is
   very common in this group)
2. Women tracking iron and vitamin D (many Indian women are
   deficient in both)
3. Pregnant women — I have seen several waitlist users mention
   taking prenatal vitamins and wanting to track against their
   doctor's micronutrient recommendations

For these users discoverability matters. If the supplement
section is buried in settings they will not find it.

I recommend Option C. One-time prompt is the least intrusive
way to ensure users who need the feature find it, while not
cluttering the diary for users who do not use supplements.

Ananya

---

**Email 3**
Date: March 2, 2025 — 10:15 AM
From: priya@nutrivana.in
To: kabir@nutrivana.in, ananya@nutrivana.in

Kabir, Ananya,

Option C from a technical perspective:

I need to add a has_seen_supplement_prompt boolean column to
user_profiles table. When the user first opens the diary after
completing goal setup, if has_seen_supplement_prompt is false
I show the overlay. When they dismiss or enable, I set it to true.
The prompt never shows again.

If they enable supplements: redirect to a supplement setup screen
where they add their supplements (supplement name, dose, unit).
These get saved to a supplements table and show in the diary.

If they dismiss: the supplement section is available in diary
settings as a toggle. Easy to find if they change their mind.

One nuance: should the prompt appear after goal setup is complete
or on the very first diary visit regardless of goals? I think
after goal setup is complete — a user who has not set any goals
yet does not need to see the supplement prompt.

Option C is implementable. Cleaner than I initially thought.
I vote Option C.

Priya

---

**Email 4**
Date: March 3, 2025 — 9:00 AM
From: shristi@nutrivana.in
To: kabir@nutrivana.in, priya@nutrivana.in, ananya@nutrivana.in,
arjun@nutrivana.in

Team,

Option C approved. PRD override from Option A.

Arjun — please add has_seen_supplement_prompt to user_profiles.
Also confirm: does the supplement data need its own table or
can supplement entries live in food_diary_entries with a type flag?

Kabir — update Figma for the dismissible prompt design.
Design principle: the prompt should be subtle enough that
dismissing it feels easy and guilt-free, but specific enough
that users who want supplement tracking understand immediately
what they are choosing.

One thing Ananya flagged worth noting: pregnant women were
mentioned as a segment who track supplements carefully.
This is the second time they have come up in product discussions
(the first was Ananya's waitlist feedback about iron and folate).
Keep this segment in the back of our minds.

Shristi

---

**Email 5**
Date: March 3, 2025 — 11:45 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, kabir@nutrivana.in, priya@nutrivana.in

Shristi, Kabir, Priya,

Supplements need their own table, not a type flag in
food_diary_entries.

Reason: supplement entries have different required fields than
food entries. Food entries need usda_food_id or custom_food_id,
serving size, meal_type, timestamp. Supplement entries need
supplement_name, dose_amount, dose_unit (mg, mcg, IU, g),
and optionally a link to a micronutrient target if the user
wants the supplement to count toward their daily micronutrient goal.

The most important part: supplements should count toward
micronutrient totals, not calorie totals. If a user takes a
vitamin D supplement of 1000 IU, that should add to their
vitamin D daily total in the analysis screen. It should not
add any calories to the diary. This is a fundamentally different
data flow from food logging.

Creating a supplements table with: user_id, supplement_name,
dose_amount, dose_unit, micronutrient_id (nullable — links to
the micronutrient target if user wants it to count), date_string,
logged_at timestamp.

has_seen_supplement_prompt added to user_profiles.

Arjun

---

---

## THREAD — IST timezone midnight problem

**Subject:** NUTR-022 timezone issue — need your call on this
**Sprint:** 5
**Date range:** March 1-3, 2025
**Participants:** Priya → Arjun → Priya → Arjun → Shristi
**Email count:** 5

---

**Email 1**
Date: March 1, 2025 — 11:00 AM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Hit a real problem in NUTR-022 (date-wise diary). Need your
architectural input before I go further.

The problem: Indian users are in IST (UTC+5:30). If a user
logs food at 11:55 PM IST the UTC timestamp is 6:25 PM the
same day — same calendar date, no problem. But if they log
food at 12:05 AM IST on March 6, the UTC timestamp is 6:35 PM
March 5 — the previous calendar day.

If the diary uses the UTC timestamp to determine which date
an entry belongs to, a meal logged just after midnight IST
appears in yesterday's diary. This will be very confusing
for users who have a late-night snack at 12:15 AM and find
it logged under the previous day.

Two options:

Option A: Store everything in UTC, convert to IST for display.
The risk: any query that filters diary entries by date needs
to know the user's timezone offset at query time. If the server
does the conversion it is manageable. But if we ever process
queries on a server in a different timezone this breaks.

Option B: Store a date_string in IST ("2025-03-06") alongside
the UTC timestamp. The date_string is generated client-side
at the moment of logging using the user's device timezone.
All diary queries filter on date_string. UTC is only used
for ordering (showing entries in time order within a day)
and for audit purposes.

I think Option B is correct. But it changes the data model
from TECH-001. Your call.

Priya

---

**Email 2**
Date: March 1, 2025 — 12:30 PM
From: arjun@nutrivana.in
To: priya@nutrivana.in

Priya,

Option B is correct. The date_string approach is the standard
pattern for apps that have date-centric features in non-UTC
timezones. Generating date_string client-side at logging time
is the key insight — the server never needs to know the user's
timezone for date-based queries.

One critical constraint: date_string must be generated on the
client using the device's local timezone at the MOMENT the user
taps "add food." Not when the request reaches the server. Not
using a stored timezone preference. The device timezone at
logging time.

This matters because users who travel internationally and log
food in different timezones should have entries appear on the
date that matches wherever they were when they logged. A user
in Singapore who travels to London for 2 days and logs dinner
at 7 PM London time should see that dinner under the London
date (the date they ate it), not under a different date because
the server is in India.

Updating TECH-001 and the technical spec now. I will add a
note: for V2 we should consider showing a soft notice if a user's
device timezone changes significantly from their account creation
timezone. Something like "We noticed you may be in a different
timezone. Your diary entries will be logged in your current
timezone (UK)." But that is V2 scope.

Arjun

---

**Email 3**
Date: March 1, 2025 — 1:15 PM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Starting Option B implementation now.

One follow-up edge case: what happens if the user's device
clock is wrong? Some older Android phones have clock sync
issues and the device clock can be off by hours. If the device
clock is 3 hours ahead, date_string would be generated as
the next calendar day even at 9 PM.

Should we do any server-side sanity check on the date_string?
Like if the date_string from the client differs from the server
UTC date by more than 24 hours, flag it?

Priya

---

**Email 4**
Date: March 1, 2025 — 2:00 PM
From: arjun@nutrivana.in
To: priya@nutrivana.in, shristi@nutrivana.in

Priya, Shristi,

Wrong device clock is a real edge case but I recommend we do
not try to fix it in V1.

Reason: if we do a server-side sanity check and reject date_strings
that differ from server time by more than 24 hours, we break
the intentional case of users in significantly different timezones
(IST user travelling to US West Coast — 13.5 hour difference
means their local date can differ from IST server date by 1 day).

The wrong-clock problem affects a small percentage of older
Android devices. Trying to distinguish "intentional timezone
difference" from "wrong device clock" server-side is complex
and error-prone.

V1 approach: trust the device clock. Document this as a known
limitation in the technical spec. If wrong-clock diary entries
become a support ticket issue in beta, we address it in V2 with
a specific fix.

Shristi — flagging this so you are aware. Not requesting a
decision — just documenting a known V1 limitation.

Arjun

---

**Email 5**
Date: March 2, 2025 — 10:00 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

Agreed. Trust device clock for V1. Document as known limitation.

The percentage of users with significantly wrong device clocks
is small enough that it does not warrant V1 scope. If it becomes
a support issue in beta we revisit.

One thing I want in the technical spec: a clear description of
what the correct user experience should be for the timezone
edge cases we are intentionally not solving in V1. This way
when we get a support ticket saying "my dinner showed up on
the wrong date" we have a documented explanation for why it
happened and what the V2 fix looks like.

Shristi

---

---

# SPRINT 6 THREADS

---

## THREAD — Bar graph user test failure

**Subject:** Bar graph test results — we need to talk
**Sprint:** 6
**Date range:** March 20-22, 2025
**Participants:** Ananya → Kabir → Shristi → Priya → Kabir → Ananya
**Email count:** 6

---

**Email 1**
Date: March 20, 2025 — 9:30 AM
From: ananya@nutrivana.in
To: kabir@nutrivana.in

Kabir,

Bar graph test results. I tested with 5 users (ages 24-38,
mix of fitness backgrounds, all health-conscious Indians).

4 out of 5 could not read the bar graph correctly on first view.

Specific confusions:

Riya (26, teacher, Delhi): "I see bars of different lengths.
Does the longer bar mean I ate more of that nutrient or that
I have less remaining? I cannot tell which direction is good."

Deepak (32, accountant, Mumbai): "What does it mean when the
bar is completely full? Did I hit my target exactly, or did
I use up all the available space on the chart?"

Sneha (28, dietitian student, Hyderabad): "The bar fills up
from left to right. OK. But what happens when I go OVER my
target? Does it overflow or stop at the edge? Because if it
stops at the edge I cannot see that I went over."

Rahul (35, fitness trainer, Chennai): Understood after I
explained the metaphor to him. Said: "Oh OK I get it now.
But I would not have understood that from just looking at it."

Anjali (24, data analyst, Bangalore): Understood immediately
without explanation.

I spoke to Anjali separately after the test. She uses a
running app that shows pace improvement over time as a filled
bar. She had a prior mental model for filled bars representing
progress toward a target. The other 4 users had no such
prior experience.

This is important: our target users are NOT data visualisation
experts. They are regular people who want to eat healthier.
Designing for Anjali's mental model means designing for 1 in 5
of our users.

What can we do? We have 11 days before launch.

Ananya

---

**Email 2**
Date: March 20, 2025 — 11:00 AM
From: kabir@nutrivana.in
To: ananya@nutrivana.in, shristi@nutrivana.in, priya@nutrivana.in

Ananya, Shristi, Priya,

4 out of 5 is a clear failure. I am not going to defend the design.

The root problem: a bar chart uses length to encode magnitude.
The user has to know what the maximum length represents before
they can interpret the bar. In most bar charts the y-axis tells
you this. In our design the maximum length represents "100% of
goal" but there is nothing in the visual that communicates this
clearly.

Three options for the remaining 11 days:

Option A: Add text labels to each bar showing "Xg / Xg target."
For example "47g / 120g protein." Users do not need to interpret
the bar length because the numbers tell the truth.
Risk: very cluttered with 20+ nutrients. Mobile will be hard to read.

Option B: Replace bars with a circular ring progress design
(like Apple Watch activity rings). Full ring = 100% of goal.
More intuitive metaphor for progress.
Risk: same ambiguity problem — what does a full ring mean?
And significant implementation time — 11 days.

Option C: Keep the bar but add explicit text below each bar.
"42g remaining" when under target. "12g over target" when over.
Bar is visual scanning aid. Text is the truth. You do not need
to interpret the bar to understand your status.
Risk: adds implementation time but less than Option B.

I recommend Option C for MVP with a full design rethink for
Sprint 8. The current metaphor (bar = amount of goal space used)
is fundamentally confusing. After launch I want to redesign this
from scratch — probably a progress bar that visually fills toward
a target and overflows with a colour change when exceeded.

Priya — is Option C implementable in 11 days alongside your
other Sprint 6 tickets? Honest answer please.

Kabir

---

**Email 3**
Date: March 20, 2025 — 12:30 PM
From: shristi@nutrivana.in
To: kabir@nutrivana.in, ananya@nutrivana.in, priya@nutrivana.in

Team,

Option C for MVP. Full redesign in Sprint 8 under AN-CR-001.

I want to say something about how we got here. The bar graph
should have been user tested in Sprint 4 or Sprint 5 when we
first designed it, not 11 days before launch. This is the second
time a critical user-facing element has been tested dangerously
late (the first was the micronutrient list tabs in Sprint 3).

New rule: any screen that visualises data in a non-standard way
(not a plain list, not a simple form) must be user tested with
at least 3 users before implementation begins. Not after. Before.

Kabir — you design the Option C patch. Ananya's observation about
Anjali's prior mental model is useful — design the text labels
to make the meaning explicit for users with NO prior experience
of progress bars or data charts.

Priya — please reply with honest answer on implementation time.

Shristi

---

**Email 4**
Date: March 20, 2025 — 1:45 PM
From: priya@nutrivana.in
To: shristi@nutrivana.in, kabir@nutrivana.in, ananya@nutrivana.in

Shristi, Kabir, Ananya,

Option C is implementable. Honest estimate: 2 days if Kabir
gives me the updated Figma today.

The text labels below each bar require:
- A calculation: (target - actual) for remaining, (actual - target)
  for over target
- A conditional display: show "Xg remaining" in green when under
  target, "Xg over target" in orange/red when over
- The colour logic must use the weight_goal_type variable (which
  we implemented in NUTR-017) — for a weight gain user, being
  over protein is green, not orange

I will need the weight_goal_type available in the analysis
component's props. I do not think it is currently passed through.
Arjun — can you confirm the analysis component has access to
weight_goal_type? If not, this could add half a day.

Starting tomorrow once Kabir has the designs ready.

Priya

---

**Email 5**
Date: March 21, 2025 — 9:00 AM
From: kabir@nutrivana.in
To: priya@nutrivana.in, ananya@nutrivana.in, shristi@nutrivana.in

Priya, Ananya, Shristi,

Figma updated for Option C. Sending the link now.

Design decisions I made:

For the text labels: I am using plain language rather than
abbreviations. "42 grams remaining" not "42g rem" — the extra
2 characters are worth it for clarity on first read.

For the over-target state: the text says "12 grams over target"
not "−12 grams" — negative numbers require understanding a
sign convention, plain language does not.

For zero state (no food logged today): text says "Goal: 120g"
rather than "120g remaining" — "remaining" implies you started
and have some left. If you have not started, "Goal" is more accurate.

One thing I want to flag about the full redesign for Sprint 8:
I think the new metaphor should be a thermometer or a tank that
fills up. The bar filling from left to right with an overflow
for over-target is more intuitive than what we have now — the
overflow section visually extends beyond the "full" marker,
making it obvious you have gone over. I will design this properly
for Sprint 8 with user testing before implementation.

Kabir

---

**Email 6**
Date: March 22, 2025 — 2:00 PM
From: ananya@nutrivana.in
To: kabir@nutrivana.in, priya@nutrivana.in, shristi@nutrivana.in

Kabir, Priya, Shristi,

Tested the Option C patch with 3 of the original 5 users
(the ones who were available for a quick follow-up).

3 out of 3 understood the labels immediately.

Deepak specifically said: "Oh this makes much more sense.
I can see '12 grams over target' and I know exactly what
that means. I do not have to think about the bar at all."

The bar chart is now a visual accent that helps scanning.
The text is the actual information. This is how it should work.

Riya asked: "Will you always show grams or can I see it as
percentage of goal?" Interesting question — she wants to see
"25% over target" not "12 grams over target." This is probably
a user preference we should add to V2 settings.

MVP patch works. Sprint 8 redesign still needed for the
underlying bar metaphor. But we can launch.

Ananya

---

---

## THREAD — AN-004 spec gap and zero calorie decision

**Subject:** Two PRD gaps I need resolved before I can continue
**Sprint:** 6
**Date range:** March 19-21, 2025
**Participants:** Arjun → Shristi → Arjun → Priya
**Email count:** 4

---

**Email 1**
Date: March 19, 2025 — 2:00 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Two specification gaps I discovered today that I cannot
proceed without decisions on.

Gap 1 — AN-004 (7-day trend graph): The PRD section for this
feature literally says "The exact design of the trend graph
should be discussed with the developer and then the
specification should be written." That discussion never happened
and the specification was never written. I need answers to:

a) What happens on days where the user logged no food?
   Options: show 0%, show a gap/break in the line, skip the day.

b) What does the Y-axis represent?
   Options: percentage of goal (0-100%+), actual gram amounts,
   both with dual axis.

c) Does the graph show one nutrient at a time (user swipes
   between nutrients) or multiple nutrients on the same chart?

Gap 2 — CF-003 (custom food validation): The PRD specifies
that the calorie field must be greater than 0. But black coffee
and water are zero calorie foods. Users will want to log these.
The current validation would block them from creating a custom
food entry for black coffee.

I need both gaps resolved before I start implementation.
The trend graph is on the critical path for MVP.

Arjun

---

**Email 2**
Date: March 19, 2025 — 3:30 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Answering both.

AN-004 trend graph:
a) Show 0% for days with no logs. A gap or break in the line
   is visually confusing — users will think the app lost their
   data. 0% is accurate (they tracked 0% of their goal that day)
   and visually clean (unbroken line with a valley on no-log days).

b) Y-axis shows percentage of goal (0 to 120%+). Gram amounts
   are not comparable across nutrients — 2g of sodium looks
   identical to 2g of protein on a gram scale but one is
   dramatically over target and one is normal. Percentage of
   goal normalises everything and makes the chart useful across
   all nutrients.

c) One nutrient at a time. Carousel/swipe navigation between
   nutrients consistent with AN-001 per-nutrient screen. If we
   show multiple nutrients on one chart with 20 tracked nutrients
   the chart becomes unreadable.

CF-003 zero calorie:
PRD was wrong. Allow >= 0. Black coffee, plain water, sparkling
water, herbal tea — all real foods with legitimate zero calorie
values. The validation was meant to prevent empty entries. Fix
the validation to catch empty name and serving fields instead.

PRD updated on both. I will also note in the PRD update: any
future specification section that says "discuss with developer
and write later" must be completed before the sprint that
implements the feature begins. This gap should have been caught
at sprint planning.

Shristi

---

**Email 3**
Date: March 19, 2025 — 4:15 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

Starting AN-004 implementation now with the agreed spec.

One technical note on the 0% for no-log days: the database
query for 7-day trend data returns rows only for days where
the user logged food. There is no row for days with no logs.

Two ways to handle this in code:

Option A: Handle in the database query. Use a generate_series
function to create all 7 dates, left join with actual diary data,
default to 0 where no join match exists. Database does the work.

Option B: Handle in application code. The frontend receives
whatever rows exist (might be 4 days instead of 7), generates
all 7 dates client-side, merges the database results, and
defaults missing dates to 0.

I recommend Option B for a specific reason: generate_series
in Supabase Postgres works but it requires a specific query
structure that makes the query harder to read and maintain.
Application-side zero-fill is more explicit and easier to
debug if something goes wrong.

Going with Option B unless you have a strong preference
otherwise Priya.

Arjun

---

**Email 4**
Date: March 20, 2025 — 9:15 AM
From: priya@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Option B agreed. Application-side zero-fill.

One implementation note: the zero-fill logic should return
exactly 7 data points in the response regardless of how many
the database returned. If the database returns 3 days of data
the application fills in the remaining 4 with zeroes and returns
all 7. The frontend should never have to handle variable-length
arrays for the trend data — always exactly 7 points.

This simplifies the chart rendering logic significantly. Chart
always has exactly 7 data points mapped to the last 7 dates.
No conditional logic needed for empty arrays or partial arrays.

Priya

---

---

# SPRINT 7 THREADS

---

## THREAD — GOAL-BUG-002 health escalation and user response

**Subject:** Health risk — beta user BT-023 — drop everything
**Sprint:** 7
**Date range:** April 3-14, 2025
**Participants:** Shristi → Arjun, Priya → Priya → Arjun →
Shristi (to Roopa) → Roopa → Ananya → full team
**Email count:** 8

---

**Email 1**
Date: April 3, 2025 — 11:30 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

Beta user BT-023 sent us a message this morning. She changed
her gender from male to female in her profile 3 days ago.
Her calorie goal did not change. She noticed the number "felt
off" and did the maths herself.

She has been eating approximately 500 calories per day MORE
than her correct goal because we failed to trigger a recalculation
when her profile changed.

Male EER for her profile (age 28, moderately active): 2,447 calories
Correct female EER for her profile: 1,923 calories
Difference: 524 calories per day over 3 days = 1,572 calories

She has been on the wrong budget for 3 days.

Arjun: I need you to stop everything else and fix this.
Not NUTR-BUG-001. Not GOAL-BUG-004. Not anything else.
When a user changes gender, age, or activity level, EER must
recalculate immediately. I need this deployed by April 11.

Priya: please audit the code and tell me whether the same
non-recalculation problem exists for age changes and activity
level changes. I suspect it does. Report back within 2 hours.

I am messaging user BT-023 personally right now.

Shristi

---

**Email 2**
Date: April 3, 2025 — 12:15 PM
From: priya@nutrivana.in
To: shristi@nutrivana.in, arjun@nutrivana.in

Shristi, Arjun,

Audit complete. 2 hours was generous — took 20 minutes because
the problem is obvious once you look for it.

The profile update handler in the backend only calls the EER
recalculation function on initial account creation. There is
a comment in the code that says "// TODO: trigger recalculation
on profile updates" that was never implemented.

The same non-recalculation problem exists for:
- Age change: changing from 25 to 40 does not update EER
- Activity level change: changing from sedentary to very active
  does not update EER (this is the one most likely to cause
  users to dramatically undereat or overeat)
- Height change: changing from 160cm to 165cm does not update
  EER (smaller impact but still inaccurate)

So user BT-023 is not the only person this could affect.
Any user who has ever changed any profile field that feeds
into the EER formula is on a potentially incorrect calorie budget.

Arjun — this is a wider fix than just gender. Every profile
change that affects EER inputs must trigger a recalculation.

Shristi — how do you want to handle the potentially affected
users? If we can identify users who changed any EER-relevant
profile field after their initial setup, we should proactively
recalculate their goals rather than waiting for them to notice.

Priya

---

**Email 3**
Date: April 3, 2025 — 1:00 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

I found the TODO comment Priya is referring to. It is in
profile_update_handler.py, line 47. It was there when I wrote
the initial implementation in Sprint 2. I intended to come back
to it. I did not.

The fix is straightforward but needs to be careful. When any
of (gender, age, activity_level, height, weight, weight_goal)
changes in user_profiles:

1. Recalculate EER using the new profile values
2. Update the user's calorie target in daily_goals
3. If the new EER is below the current calorie target AND below
   the BMR safety floor, set the calorie target to BMR floor
   and trigger the BMR warning notification
4. Send the user an in-app notification: "Your calorie goal has
   been updated to [X] calories based on your updated profile"

On Priya's question about proactively fixing affected users:
Yes. I can query user_profiles for all users who have an
updated_at timestamp that is later than their daily_goals
created_at timestamp. These are users who changed their profile
after initial goal setup. I will recalculate EER for all of
them as part of the fix deployment.

Estimate: 2 days for implementation and testing.
Target deployment: April 5.

Arjun

---

**Email 4**
Date: April 3, 2025 — 1:30 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

Proceed with the full fix including the proactive recalculation
for all affected users.

One thing before you deploy: when the recalculation runs for
existing users, send each affected user an in-app notification
AND an email. The in-app notification might not be seen if they
have not opened the app recently. Use this email template:

Subject: Your Nutrivana calorie goal has been updated

"Hi [Name],

We fixed a bug today that was affecting users who changed their
profile information after initial setup. Your calorie goal has
been automatically recalculated to [X] calories to accurately
reflect your current profile.

If this number surprises you or does not seem right, you can
adjust it manually in your profile settings.

We are sorry for the inconvenience. We take accuracy seriously —
a calorie goal that does not match your actual body is worse
than no calorie goal at all.

The Nutrivana team"

I am sending a personal message to BT-023 now separately.

Shristi

---

**Email 5**
Date: April 3, 2025 — 2:15 PM
From: shristi@nutrivana.in
To: roopa.v@gmail.com

Hi Roopa,

I am Shristi, one of the founders of Nutrivana.

Thank you for reaching out. You found a real bug. When you updated
your gender in your profile, your calorie goal should have
automatically recalculated to your new EER value. It did not.
This is a failure in our implementation and I am sorry.

Based on your profile your correct calorie goal as a female user
with your age and activity level is approximately 1,923 calories
per day. The value currently showing in your profile is approximately
2,447 calories — the EER value calculated for male users.

While we fix the bug properly — which will be deployed by April 5
— you can manually update your calorie goal to 1,923 calories
in your profile settings. The manual update will override the
incorrect stored value immediately.

When we deploy the fix it will automatically recalculate your
goal to the correct value and you will receive an in-app notification.

I also want to explain WHY this happened, because you deserve
a real answer not a PR-managed apology: we had a placeholder
comment in our code from Sprint 2 that said "TODO: trigger
recalculation on profile updates." That placeholder was never
implemented. Your bug report is the reason it will be implemented
by Friday.

I would like to offer you 3 months of Nutrivana Pro free when
we launch our premium tier. You helped make the product better
for every future user who changes their profile.

Shristi Sharmistha
Co-founder, Nutrivana

---

**Email 6**
Date: April 5, 2025 — 9:30 AM
From: roopa.v@gmail.com
To: shristi@nutrivana.in

Hi Shristi,

I did not expect a personal reply from the founder. And I
definitely did not expect you to explain exactly what went wrong
in your code. That level of transparency is remarkable.

I updated my goal manually as you suggested. The numbers make
much more sense now and I can see the difference it makes to
my daily tracking.

I know you are in beta and bugs are expected. What matters is
how a company responds to them. You responded the same day,
you explained clearly what happened, you gave me a workaround,
you told me exactly when the fix would be ready, and you offered
me something in return even though I did not ask for anything.

I left a review on the App Store this morning. I hope it helps.
Keep building.

Roopa

---

**Email 7**
Date: April 5, 2025 — 10:15 AM
From: ananya@nutrivana.in
To: shristi@nutrivana.in, arjun@nutrivana.in,
priya@nutrivana.in, kabir@nutrivana.in

Team,

Roopa left a 5-star App Store review this morning. Title:
"Finally an app that treats users like adults."

She reviewed the experience, not the features. She specifically
mentioned that Shristi explained "exactly what went wrong in
the code" — the transparency mattered to her as much as the fix.

I want to suggest this becomes a documented communication
standard for us, not just Shristi's instinct:

When a user reports a P0 or P1 bug that affects their health
or data:
1. The founder (Shristi or Arjun) responds personally within
   24 hours — not marketing, not a support template
2. The response includes: what happened technically (in plain
   language), the impact on their specific data, a manual
   workaround if available, an exact deployment date for the fix
3. We offer something tangible for their trouble

A frustrated user who gets a personal, transparent, honest
response from the founder becomes an advocate. We have evidence
of this now.

Ananya

---

**Email 8**
Date: April 5, 2025 — 11:00 AM
From: shristi@nutrivana.in
To: ananya@nutrivana.in, arjun@nutrivana.in,
priya@nutrivana.in, kabir@nutrivana.in

Team,

Ananya — yes. Document this as our bug communication standard.
Add it to the team norms document in Notion.

One addition to your framework: we should notify users proactively
when we know a bug affected them, rather than waiting for them
to report it. For GOAL-BUG-002 we are already doing this —
Arjun is running a query to find all affected users and we are
sending them all the recalculation email.

But the broader principle: when we discover a bug that silently
affected user data, we tell affected users before they notice.
Do not wait for the support ticket. Find the users and tell them.

This feels obvious but most companies do not do it because it
means admitting the mistake proactively. We are doing it anyway.

Shristi

---

---

## THREAD — FoodDiaryContext root cause and technical debt reflection

**Subject:** Root cause found — NUTR-BUG-001 and AN-BUG-003 are the same bug
**Sprint:** 7
**Date range:** April 8-9, 2025
**Participants:** Arjun → Shristi → Priya → Arjun
**Email count:** 4

---

**Email 1**
Date: April 8, 2025 — 9:45 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

Root cause confirmed for both NUTR-BUG-001 and AN-BUG-003.

They are the same bug. Both caused by FoodDiaryContext not
being implemented.

Here is the technical picture:

Currently, the food diary page has three separate components
that each maintain their own local state about the diary entries:

1. DiaryTotalsRow — maintains a local copy of the entry array
   to calculate and display the cumulative nutrient totals
2. MealSection (×4 — breakfast, lunch, dinner, snacks) — each
   maintains a local copy of its own entries
3. AnalysisScreen — fetches diary entries independently when
   it mounts

When a user adds a food entry, the POST request is made by
the MealSection component. The POST response updates
MealSection's local state. DiaryTotalsRow does not know a
new entry was added — it still shows the old totals until
page refresh. AnalysisScreen does not know — same problem.

FoodDiaryContext would give all three components a single
shared state. When MealSection adds an entry, it updates
the context. DiaryTotalsRow and AnalysisScreen both subscribe
to the context and re-render automatically.

The fix is implementing FoodDiaryContext correctly. Both bugs
close when this is done.

Implementation time: 1 day for the context implementation,
1 day to migrate all three components to read from context
instead of local state, half a day for testing. Targeting
April 10 deployment.

Arjun

---

**Email 2**
Date: April 8, 2025 — 10:30 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

I need to say something before we close this thread.

FoodDiaryContext was first identified as needed in Sprint 4.
It was deferred with the note "Sprint 5, P0."
In Sprint 5 it was deferred again with the note "Sprint 6, guaranteed."
In Sprint 6 Arjun gave an explicit written commitment that it
would be implemented.
It was not implemented in Sprint 6.

We are now fixing two P1 beta bugs that exist solely because
this architectural work was deferred three times across three sprints.

I am not saying this to assign blame. I am saying it because
I want us to have an honest conversation about why it happened
so it does not happen again.

My read: FoodDiaryContext is not glamorous. It does not add a
visible feature. It does not improve the demo. It just makes
the invisible plumbing work correctly. And in a sprint-by-sprint
environment where the pressure is always to show visible progress,
invisible plumbing gets deprioritised.

Going forward: when Jira tickets are tagged as architectural work
they cannot be deprioritised without an explicit written note
from me explaining the risk we are accepting. Not "we will do
it next sprint." A written acceptance that we are knowingly
taking on technical debt with a specific risk consequence.

Shristi

---

**Email 3**
Date: April 8, 2025 — 11:15 AM
From: priya@nutrivana.in
To: shristi@nutrivana.in, arjun@nutrivana.in

Shristi, Arjun,

I want to add something honest to this conversation.

In Sprint 6 when FoodDiaryContext came up again, I made a
judgment call to deprioritise it. I had 13 tickets to deliver
in a 3-week sprint with a hard March 31 MVP deadline. I looked
at the list and FoodDiaryContext felt like the ticket with the
most invisible benefit.

I was wrong. The benefit was invisible until beta users hit
NUTR-BUG-001 and GOAL-BUG-004. Then it became very visible.

The lesson I am taking: "invisible until it breaks" is not the
same as "low value." Infrastructure work is exactly this type.
It is invisible when it works and catastrophically visible
when it does not.

I am starting FoodDiaryContext implementation today. Expect
a PR by tomorrow evening.

Priya

---

**Email 4**
Date: April 10, 2025 — 3:30 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

FoodDiaryContext implementation complete. PR merged and deployed.

Testing confirmed: adding a food entry now simultaneously
updates DiaryTotalsRow, MealSection, and AnalysisScreen.
No page refresh needed. NUTR-BUG-001 and AN-BUG-003 both closed.

One thing I found during implementation that is worth noting:
the AnalysisScreen was fetching diary data independently on
every mount — meaning every time a user navigated away from
analysis and back, it made a fresh database call even if the
data had not changed. With FoodDiaryContext the analysis screen
reads from the shared context. Database calls now happen only
when diary data actually changes, not on every navigation.

This is a performance improvement we would not have had without
FoodDiaryContext. The architectural work that felt "invisible"
actually reduces database load by approximately 30% for active
users who navigate between diary and analysis frequently.

Arjun

---

---

# SPRINT 8 THREADS

---

## THREAD — Tests first for health-critical bugs

**Subject:** GOAL-BUG-005 — I want to change how we approach this
**Sprint:** 8
**Date range:** April 18-22, 2025
**Participants:** Arjun → Shristi → Arjun → Shristi
**Email count:** 4

---

**Email 1**
Date: April 18, 2025 — 10:00 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Starting GOAL-BUG-005 today (BMR warning shown but goal saved
incorrectly). Before I begin I want to change how we approach
health-critical bug fixes.

The bug: when a user sets a calorie goal below their BMR,
clicks through the warning, and confirms they understand the
risk — the goal is saved at an incorrect value. In some cases
it saves at 0. In some cases it saves at the BMR floor instead
of the user's specified value. In some cases it saves correctly.
The inconsistency suggests there are multiple code paths and
I do not fully understand which path triggers which outcome.

My proposal: write tests first.

Step 1: Define every scenario that the fixed code must handle
(user sets goal above BMR — no warning, saves correctly;
user sets goal 5% below BMR — warning shown, user clicks through,
saves at specified value; user sets goal 30% below BMR — warning
shown, user closes warning without confirming, goal not saved, etc.)

Step 2: Write test cases for all scenarios. Run them against
the broken code to confirm the tests catch the bug correctly.

Step 3: Implement the fix until all tests pass.

The reason I want to do this: if I just fix what I can see is
broken, I risk fixing the symptom without understanding the
full failure mode. For a health-critical feature where the bug
involves incorrect calorie goals, I would rather take an extra
day to understand it fully than ship a fix that works for 80%
of scenarios.

Request permission to take an extra day for test-writing before
implementation.

Arjun

---

**Email 2**
Date: April 18, 2025 — 10:45 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Not just permission — instruction. Write the tests first.

And more than that: tests-first is now a team standard for
all health-critical features. Not just this bug. Any feature
or fix that touches BMR, EER, calorie goals, or micronutrient
targets gets tests written before implementation begins.

The reason: health features have a failure mode that is worse
than "the app crashes." If the app crashes users know something
is wrong. If the calorie calculation is silently incorrect for
a subset of scenarios, users do not know — they just eat the
wrong amount and wonder why they are not making progress.

Silent failure in health data is the worst kind of failure.
Tests-first is how we prevent it.

Shristi

---

**Email 3**
Date: April 21, 2025 — 9:30 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Tests written. 23 test cases covering every combination of:
- Goal value relative to BMR (above, equal, 1-10% below, 10-30% below, 30%+ below)
- User action (click through warning, close warning, close and re-enter same value, close and enter different value)
- Existing goal state (first time setting goal, updating existing goal, goal already below BMR from a previous bug)

Running against broken code: 11 of 23 tests fail. Tests are
catching the bug. This is correct.

Three failure modes I found through test-writing that I would
not have caught by just fixing the obvious symptom:

Failure mode 1: Goal saves at 0 when user clicks through warning
if they have never set a goal before. This only happens on
first-time goal setup — on subsequent edits it saves at the
specified value. The code path is different for initial setup
vs update.

Failure mode 2: BMR warning does not show when user sets goal
equal to EXACTLY their BMR. The check is goal < BMR not goal <= BMR.
Setting a goal equal to BMR is also risky but does not trigger
a warning.

Failure mode 3: Warning state is not reset if user closes the
warning and immediately re-submits the same value. The warning
should appear again on re-submit. It does not because the
warning_acknowledged flag is set when the user clicks "I understand"
but never cleared when they close without confirming.

Starting the fix now. Will have all 23 tests passing by April 22.

Arjun

---

**Email 4**
Date: April 22, 2025 — 4:00 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

The three failure modes you found through test-writing — 
particularly failure mode 1 (first-time vs update code path
divergence) — are exactly the kind of thing that would have
slipped through a conventional "fix what I can see" approach.

Please add the 23 test cases to the permanent codebase regression
suite. Every future change to BMR or EER logic should run against
these tests before merging. Not just now — permanently.

Also: failure mode 2 (goal equal to BMR not triggering warning)
is technically a PRD issue. The PRD says "below BMR" but
setting a goal at exactly BMR is nutritionally equivalent to
fasting — essentially zero metabolic headroom for any physical
activity. Should the warning trigger at exactly BMR or only
strictly below?

My view: warning should trigger at BMR and below (goal <= BMR).
Eating at exactly BMR is not advisable for any active person.
Please update the PRD and fix accordingly.

Shristi

---

---

## THREAD — Codebase audit and shared utilities

**Subject:** The duplicate logic problem — I want to fix this properly
**Sprint:** 8
**Date range:** April 20-26, 2025
**Participants:** Priya → Shristi → Arjun → Arjun (update) → Priya
**Email count:** 5

---

**Email 1**
Date: April 20, 2025 — 3:15 PM
From: priya@nutrivana.in
To: shristi@nutrivana.in, arjun@nutrivana.in

Shristi, Arjun,

Fixed NUTR-BUG-008 (search not clearing on source change).
Straightforward — clear search state synchronously when source
dropdown changes.

But I need to flag something while fixing it. I noticed the
same bug I just fixed exists in at least 2 other places:
switching from USDA to custom food source does not clear search
state. Switching between custom recipe and custom meal does not
clear search state either.

This is the third occurrence in Sprint 7 and Sprint 8 of the
same pattern: fix applied in one place, same fix needed in
3 other places with the same underlying logic.

The root cause is not "developers are not careful enough."
The root cause is that we have the same logic written in 4
different places. When the logic in one place is wrong, the
other 3 places have the same bug. When we fix one place without
the others, we have 1 fixed and 3 still broken.

The real fix is shared utility functions. One function for
search state management. One function for nutrient value display.
One function for colour logic. Any change to the logic changes
it everywhere simultaneously.

Arjun — can you lead a codebase audit to find all the duplicated
logic patterns? I can identify the frontend duplications but
you have visibility into both frontend and backend.

Priya

---

**Email 2**
Date: April 20, 2025 — 4:30 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, priya@nutrivana.in

Arjun, Priya,

Arjun — lead the codebase audit. Complete before Sprint 9 begins.

Priya has correctly diagnosed the root cause. The PR review
checklist approach we added after Sprint 7 ("did you check
all related components?") was a process fix for a code
architecture problem. Process fixes for code problems do not
scale. Code fixes do.

Shared utility functions for all repeated logic patterns is
the right solution. The audit should find every place where
we have duplicated logic and create a shared function for each.

The definition of done for this audit: no two places in the
codebase implement the same logic independently. If it needs
to be done in two places, there is a shared function that
both places call.

Shristi

---

**Email 3**
Date: April 21, 2025 — 11:00 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

Starting the audit today. Initial scan of the codebase shows
three categories of duplicated logic:

Category 1: Nutrient value formatting
Found 6 different places that format nutrient values for display.
Some round to 1 decimal, some to 2, some call toFixed(1) directly
without parseFloat wrapper (the bug we fixed in Sprint 3 for
macro validation). Inconsistent null handling — 3 places show
0, 3 places show — for null values.

Category 2: Colour logic
Diary totals row, analysis bar graph, and per-meal breakdown
each have their own colour logic implementation. The weight_goal_type
colour rules we defined in Sprint 4 are implemented slightly
differently in each. The analysis screen has a subtle bug where
weight_maintain users who are over target see yellow for some
nutrients and orange for others — the implementations diverged
at some point.

Category 3: Search state management
The exact bug Priya raised. clearSearchState() logic exists in
4 places with 4 slightly different implementations.

Additional category I found that was not in Priya's list:

Category 4: Date range queries
Three different places build date range queries for querying
diary data by date. Each builds the query slightly differently.
Two use date_string correctly. One accidentally uses the UTC
timestamp for the date boundary comparison — this is a latent
timezone bug that would surface for users logging food near
midnight IST. Has not been reported because it requires a
specific timing condition to trigger.

Creating shared functions for all four categories.

Arjun

---

**Email 4**
Date: April 25, 2025 — 5:00 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, priya@nutrivana.in

Shristi, Priya,

Codebase audit complete. Four shared utility functions created
and deployed:

formatNutrient(value, unit, displayPrecision)
Handles all nutrient value display including the zero vs null
distinction, decimal precision by unit type, and the
parseFloat(toFixed()) rounding. Every place in the codebase
that previously formatted nutrient values now calls this function.

getNutrientColor(actual, target, goalType)
Single source of truth for all nutrient colour logic. Fixed the
weight_maintain colour divergence Priya mentioned — all components
now show consistent yellow for maintain users who are over target.

clearSearchState(sourceType)
Accepts a sourceType parameter so the same function handles
clearing state for USDA, custom food, custom recipe, and custom
meal source changes. Previously each had separate logic.

buildDiaryDateQuery(dateString, userId)
Fixes the latent timezone bug I found in Category 4. All diary
date queries now use this function which consistently uses
date_string for the date comparison, never the UTC timestamp.

Found and proactively fixed 4 additional instances of duplicated
logic during migration that were not in the original four categories.

The PR touches 47 files. All changes are mechanical substitutions
(replace local logic with shared function call). No logic has
changed, only the organisation. Priya please review before I merge.

Arjun

---

**Email 5**
Date: April 26, 2025 — 10:30 AM
From: priya@nutrivana.in
To: arjun@nutrivana.in, shristi@nutrivana.in

Arjun, Shristi,

PR reviewed. Looks clean.

One observation worth sharing: the formatNutrient function
revealed 3 places where we were displaying nutrient values
incorrectly for the users who were not affected by the Sprint 3
floating point bug. For example, one component was displaying
Vitamin B12 as "2.4000000000000002 mcg" instead of "2.4 mcg"
because it was using a raw JavaScript multiplication result
without rounding. Users would have seen this as a UI glitch —
a very long decimal number — but only for B12 specifically
because of how B12's RDA value interacts with the multiplication.

This is the kind of bug that never gets reported because users
assume it is intentional or just how the app works. The audit
found and fixed it without anyone ever having to report it.

Approving the merge. Good work Arjun.

Priya

---

---

# SPRINT 9 THREADS

---

## THREAD — CF-BUG-001 historical data corruption

**Subject:** CF-BUG-001 root cause — this is serious
**Sprint:** 9
**Date range:** May 5-8, 2025
**Participants:** Arjun → Shristi → Arjun → Shristi
**Email count:** 4

---

**Email 1**
Date: May 5, 2025 — 2:30 PM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Root cause identified for CF-BUG-001. The fix is one line.
But the impact of the bug on 8 beta users is significant and
I want you to know the full picture before we deploy.

The bug: when a user edits a custom food (changes name, macros,
serving size), the edit is retroactively reflected in ALL past
diary entries for that food, not just entries from the edit
date onwards.

Concrete example: beta user Divya created "Homemade Dal" on
March 12 with values she looked up from IFCT — Protein: 8.9g,
Carbs: 23.4g, Fat: 0.8g per 100g. She logged it every day
from March 12 to May 5. On May 3 she updated "Homemade Dal"
because she realised her recipe uses more ghee — new values:
Protein: 9.1g, Carbs: 23.4g, Fat: 2.3g per 100g.

After the edit, every single diary entry from March 12 to May 5
now shows the new fat value (2.3g) instead of the original (0.8g).
Her entire historical diary has been silently recalculated with
macros she did not eat.

8 beta users have edited custom foods since March. All 8 have
altered historical data without knowing it.

Root cause: in CF-007 (retroactive change handling), the query
that joins diary entries to custom food versions uses NOW() as
the effective date parameter instead of the diary entry's own
date_string. This means every diary entry joins to the custom
food version active TODAY, not the version active on the date
the food was logged.

The fix: change NOW() to $diary_date in the versioning query.
One line. The CF-007 versioning system is architecturally correct
— the food version history is stored properly. Only the query
parameter was wrong.

But I need to also run a data restoration script for the 8
affected users. Their historical diary entries need to be
re-joined to the correct custom food versions for their
respective dates.

Deploying the fix is straightforward. The data restoration
requires careful testing — I need to confirm that re-running
the join with correct date parameters gives the right historical
values before I touch production data.

Arjun

---

**Email 2**
Date: May 5, 2025 — 3:45 PM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

Fix the bug. Run the data restoration for all 8 affected users.
Test the restoration thoroughly before touching production data —
I would rather take an extra day than restore incorrect values.

I need two things from you:

First: a list of the 8 affected users and a plain-language
description of exactly what changed in their historical data
and what it looks like after restoration. I will send each
of them a personal message explaining what happened. Same
approach as GOAL-BUG-002.

Second: after this is resolved, I want a code review standard
added to our PR checklist: any query that serves historical
diary data must be reviewed with the explicit question "am I
using the date of the data I am serving or today's date?"
NOW() in a historical diary query should be treated as a
red flag that requires justification.

This is the second time a date parameter error has caused a
silent data quality problem (the first was the FNDDS column
reversal in Sprint 4). Date-sensitive queries on health data
require extra scrutiny.

Shristi

---

**Email 3**
Date: May 7, 2025 — 11:00 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in

Shristi,

Fix deployed. Data restoration complete for all 8 users.

Technical summary of the restoration:
For each affected user I identified every diary entry that
contained a custom food edit that occurred after the entry date.
Re-ran the version join query using the correct date parameter
($diary_date). Compared the corrected nutrient values against
the currently stored values. Updated all entries where the values
differed.

The 8 affected users and the scale of their data changes:

Divya (BT-012): 54 diary entries affected, fat values corrected
across her full March-May diary. Largest impact user.

Vikram (BT-034): 12 entries affected, protein values corrected.
He edited a custom protein shake entry.

Meera (BT-019): 8 entries affected, calorie values corrected.
She edited her homemade chapati entry to correct a serving size error.

The remaining 5 users had 1-3 entries affected each.
Impact was smaller but still real data.

One thing I confirmed during the restoration that is worth
noting: the food version history in the database is complete
and accurate. Every version of every custom food is stored
with the correct timestamps. The versioning system CF-007
implemented is solid. Only the query parameter was wrong.
The fact that we can do a clean restoration confirms the
architecture is correct.

I also added a database trigger that logs a warning to our
monitoring system whenever a query on food_diary_entries
uses NOW() or CURRENT_TIMESTAMP in a date comparison context.
This will catch future instances of this error during development
rather than after deployment.

Sending you the 8 user messages now as a draft for your review.

Arjun

---

**Email 4**
Date: May 8, 2025 — 9:00 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in

Arjun,

The database trigger is a genuinely good idea. Catching this
class of error during development is much better than catching
it in production.

User messages approved. Sending today.

One more thing: the CF-007 versioning architecture being intact
is actually important to communicate to the affected users.
When I tell Divya that her historical data was altered by our
bug and has now been restored, I want her to understand that
the restoration is accurate — we were not guessing what her
old values should be. We stored every version of her custom food
with timestamps. The restoration was a deterministic re-calculation,
not an approximation.

That distinction matters to users who have been carefully tracking
health data for months. Their data is not just "approximately
restored." It is exactly restored because we designed the
architecture to preserve that history.

Shristi

---

---

## THREAD — Pregnant women discovery

**Subject:** Something I noticed in the user data — need your take
**Sprint:** 9
**Date range:** May 9-12, 2025
**Participants:** Ananya → Shristi → Arjun → Shristi →
Kabir → Shristi (to Ravi)
**Email count:** 6

---

**Email 1**
Date: May 9, 2025 — 4:00 PM
From: ananya@nutrivana.in
To: shristi@nutrivana.in

Shristi,

I want to share something I have been noticing in the user data
this week. Not sure if it is significant or just a small sample
coincidence. Wanted your read before I raise it with the team.

I have been manually going through the health goals free-text
field in new user profiles (the field where users describe what
they want to achieve). Looking for qualitative patterns.

I noticed 11 users who mentioned being pregnant or expecting.
Things like: "I am 14 weeks pregnant and want to track iron
and folate," "expecting in July, need to make sure I'm getting
enough calcium," "second trimester, doctor told me to track
vitamins."

These 11 users are not what I expected to find in our user base.
We did not market to pregnant women. We did not mention pregnancy
in any of our launch materials.

But here is the strange thing. I asked Arjun to pull their usage
data informally. These 11 users are significantly more engaged
than average. Much higher session frequency, much longer sessions,
much more time in the micronutrient tracking section.

I think I understand why. Pregnant women have doctor-prescribed
micronutrient targets in specific doses. Folate: 600 mcg. Iron:
27 mg. Calcium: 1000 mg. These are not general health guidelines —
they are specific medical targets that change by trimester.
No other nutrition app tracks micronutrients at this precision.
We accidentally serve this need better than anyone else.

Is this worth investigating properly?

Ananya

---

**Email 2**
Date: May 9, 2025 — 5:30 PM
From: shristi@nutrivana.in
To: ananya@nutrivana.in, arjun@nutrivana.in

Ananya, Arjun,

Yes. This is worth investigating properly.

Ananya — your hypothesis makes complete sense. The deep
micronutrient tracking that differentiates us from HealthifyMe
and MFP is the exact feature that serves pregnant women's
needs better than anything else available. We built it for
general health users but pregnant women have the most urgent
and specific micronutrient needs of any user group.

Two things I want immediately:

First — Arjun, please run a proper cohort analysis on the 11
pregnant women users vs the rest of the user base. I want
exact numbers: average sessions per day, average session length,
Day 7 retention, what features they use most. If the engagement
difference is as significant as Ananya suggests it will show
clearly in the data.

Second — Ananya, I want you to reach out to these 11 users and
ask if they would be willing to do a 20-minute user interview.
Compensation: 3 months of Nutrivana Pro free when we launch
premium. Questions I want answered: How did you find Nutrivana?
What are you tracking and why? What does your doctor recommend
that the app does not currently support? What would make you
refer Nutrivana to other pregnant women?

This last question matters. Pregnant women talk to other pregnant
women. If we serve this segment well, referral behaviour could
be very high.

Shristi

---

**Email 3**
Date: May 11, 2025 — 10:00 AM
From: arjun@nutrivana.in
To: shristi@nutrivana.in, ananya@nutrivana.in

Shristi, Ananya,

Cohort analysis complete. 11 pregnant women vs 836 other users
in the first 10 days post-launch.

Sessions per day:
Pregnant women: 4.2 average
All other users: 1.8 average
Ratio: 2.3x

Average session length:
Pregnant women: 6.3 minutes
All other users: 2.8 minutes
Ratio: 2.25x

Day 7 retention (preliminary):
Pregnant women: 9 of 11 returned on day 7 (81.8%)
All other users: approximately 350 of 836 returned (41.9%)
Ratio: ~2x

Feature usage — micronutrient tracking section:
Pregnant women: 100% of sessions include micronutrient tracking
All other users: 34% of sessions include micronutrient tracking

Most tracked micronutrients by pregnant women users:
Iron (100% of pregnant users track this)
Folate (100%)
Calcium (90%)
Vitamin D (82%)
Magnesium (72%)
Zinc (63%)
Iodine (54%) — interesting, this is a pregnancy-specific concern
that general health users almost never track

The iodine finding is notable. Iodine deficiency in pregnancy
is a significant risk factor for developmental issues. The fact
that over half of our pregnant users are tracking iodine suggests
these are informed, medically engaged users — not casual health
trackers.

One more finding: 6 of the 11 pregnant users are in their
second trimester. 3 are in their first trimester. 2 are in
their third. Micronutrient requirements change significantly
between trimesters and our current goal setting does not
account for this at all — pregnant users are setting generic
adult RDA targets, not trimester-specific prenatal targets.

This is a genuine product gap for this segment.

Arjun

---

**Email 4**
Date: May 11, 2025 — 11:30 AM
From: shristi@nutrivana.in
To: arjun@nutrivana.in, ananya@nutrivana.in,
priya@nutrivana.in, kabir@nutrivana.in

Full team,

The numbers Arjun found are significant. 81.8% Day 7 retention
vs 41.9% for all other users. 2.3x more sessions. 100% of
pregnant users tracking micronutrients vs 34% of others.

We accidentally built the best nutrition app for pregnant women.
And we have zero features specifically designed for them.

Things we do not have that pregnant women clearly need:
Trimester-specific micronutrient targets (folate requirements
change from 400mcg pre-conception to 600mcg in pregnancy;
iron goes from 18mg to 27mg; calcium needs are different in
each trimester)

Prenatal supplement tracking — these users take 3-5 supplements
daily (prenatal multivitamin, omega-3, iron, folic acid, vitamin D)
and the supplement tracking we built for NUTR-014 was designed
for general supplement use, not prenatal dose management

Doctor-recommended goal templates — right now a pregnant user
sets up their own micronutrient targets manually. If we built
a "Pregnancy (X weeks)" goal template that pre-fills the correct
trimester targets, onboarding for this segment would take 30
seconds instead of 10 minutes

Kabir — when you have time, I want you to sketch what a
"Pregnancy Mode" onboarding flow would look like. How many
questions do we need to ask (trimester? first child or not?
any specific deficiencies your doctor mentioned?) to give
a useful prenatal goal preset?

We are not building this in Sprint 9. But I want Q3 OKRs to
include this segment explicitly.

Shristi

---

**Email 5**
Date: May 12, 2025 — 9:00 AM
From: kabir@nutrivana.in
To: shristi@nutrivana.in, ananya@nutrivana.in,
arjun@nutrivana.in, priya@nutrivana.in

Team,

Sketched a "Pregnancy Mode" onboarding flow.

Minimum viable questions (3):
1. Are you currently pregnant? (Yes / Trying to conceive / Postpartum)
2. If yes: which trimester? (1st — weeks 1-12 / 2nd — weeks 13-26 /
   3rd — weeks 27-40)
3. Do you have any doctor-flagged deficiencies or specific targets?
   (Free text + common options: iron deficiency, low vitamin D,
   gestational diabetes considerations)

From these 3 questions we can pre-fill:
- Calorie target (pregnancy requires additional 300-500 kcal/day
  above baseline depending on trimester)
- Folate/folic acid target (600mcg for pregnancy)
- Iron target (27mg for pregnancy)
- Calcium, vitamin D, omega-3, iodine at pregnancy-specific RDAs
- A supplement prompt specifically for prenatal vitamins

The full flow including question screens and confirmation would
take a user approximately 90 seconds. Much better than the current
10+ minutes of manual micronutrient selection.

One observation: the pregnant women who found us in week 1 of
launch found us without us marketing to them. They had a specific
health need, searched for an app, and found that our micronutrient
tracking depth was better than anything else available.

If we build explicitly for them — with the right onboarding,
the right presets, the right supplement tracking — and then
market specifically to pregnant women through OB-GYN offices,
pregnancy apps, and pregnancy communities, this segment could
be significantly larger than the general health market we were
originally targeting.

That is a strategic question for Shristi and Ravi. I just wanted
to note that the product evidence supports it.

Kabir

---

**Email 6**
Date: May 12, 2025 — 11:00 AM
From: shristi@nutrivana.in
To: ravi.kapoor@seedfund.in

Hi Ravi,

I want to share a discovery from our first week of public launch
that I think is strategically important.

We found an unexpected user segment: pregnant women. 11 users
in launch week mentioned pregnancy in their profiles. We did
not market to them. They found us.

Their engagement numbers: 4.2 sessions per day vs 1.8 average.
81.8% Day 7 retention vs 41.9% for the rest of our user base.
100% of them use micronutrient tracking vs 34% of other users.

The reason makes complete sense in retrospect: pregnant women
have doctor-prescribed micronutrient targets in specific doses
that change by trimester. They need to track folate at 600mcg,
iron at 27mg, calcium at 1000mg — precision targets that no
other app supports at this level. We built deep micronutrient
tracking for general health users. Pregnant women need it
more than anyone.

We currently have zero features designed specifically for this
segment. No trimester-specific goal presets. No prenatal
supplement tracking. No pregnancy onboarding. They are using
a tool not designed for them and still retaining at 2x our
average because the core feature matches their need so well.

My question for you: does this change how you think about
the Q3 strategy?

Context: there are approximately 26 million pregnancies per year
in India. The segment is naturally self-referring — pregnant
women talk to other pregnant women. If we build explicitly for
them we move from "accidentally good for pregnant women" to
"the nutrition app designed for pregnancy in India." That is
a defensible niche that HealthifyMe, MFP, and Cronometer cannot
easily copy because none of them have deep micronutrient tracking.

We are planning user interviews with the 11 users over the next
3 weeks to understand their needs deeply before making any
product decisions.

Wanted you to have visibility on this before the June investor
call.

Shristi

---

---

## SUMMARY TABLE

| Thread Subject | Sprint | Emails | New Information Not In Jira/Retro |
|---|---|---|---|
| Database schema review | 1 | 5 | Empty targets state, goal_snapshots problem discovered by Priya, full Option A/B/C analysis |
| January investor update | 1 | 3 | BMR safety floor explanation, community foods V2 strategy |
| USDA rate limit and Indian food gap | 2 | 6 | Full list of missing Indian foods by name, 47 corn dog varieties vs 0 dal varieties |
| Sprint 2 investor update | 2 | 3 | Community vs private food strategy, V2 quality-gated crowdsourcing plan |
| Floating point and USDA data quality | 3 | 5 | USDA decimal precision inconsistency (4 different precisions), zero vs null distinction, display precision rules per unit |
| GOAL-009 micronutrient list design | 3 | 5 | "Select all in category" feature, real-time filter vs jump-to search, selected counter, specific user mental models |
| Serving units and portion size | 4 | 5 | FNDDS column reversal bug (23 foods with calcium/sodium swapped), household vs gram toggle decision, specific unit truncation rules |
| FoodDiaryContext deferral | 4 | 4 | Analysis screen makes fresh DB call on every mount, architectural explanation of why it keeps being deprioritised, 30% DB load reduction from fix |
| Supplement toggle decision | 5 | 5 | Supplement table separate from food_diary table (different data model), supplements count toward micronutrients not calories, pregnant women flagged twice as potential power users |
| IST timezone midnight problem | 5 | 5 | Wrong device clock edge case, Singapore to London travel scenario, V2 timezone change notice design |
| Bar graph user test failure | 6 | 6 | Anjali's prior mental model (running app pace charts), "remaining" vs "Goal" for zero state, V2 user preference for percentage display, thermometer/tank redesign concept |
| AN-004 spec gap and zero calorie | 6 | 4 | Option A vs B for zero-fill (generate_series vs application-side), always return exactly 7 data points rule |
| GOAL-BUG-002 health escalation | 7 | 8 | TODO comment in code from Sprint 2, proactive recalculation for all affected users, exact calorie numbers for BT-023, Roopa's full reply, bug communication standard formalised |
| FoodDiaryContext root cause | 7 | 4 | 3 separate independent state objects explained technically, 30% DB load improvement from fix, honest reflection from Priya |
| GOAL-BUG-005 tests first | 8 | 4 | 3 failure modes found only through test-writing, goal = BMR not triggering warning (PRD gap), permanent regression suite |
| Codebase audit | 8 | 5 | Category 4 (date range queries) not in original plan, latent midnight IST bug found proactively, B12 display bug found, database trigger for NOW() in historical queries |
| CF-BUG-001 historical data | 9 | 4 | Divya's specific data example (54 entries altered), all 8 users named with scale of impact, restoration is deterministic not approximate, DB trigger added |
| Pregnant women discovery | 9 | 6 | Iodine tracking (54% of pregnant users — unexpected), 3 minimum questions for Pregnancy Mode, 90-second onboarding design, strategic market sizing (26M pregnancies/year India), self-referring segment behaviour |

---

## GPT-4o GENERATION INSTRUCTIONS

Generate 18 Gmail thread files. Each thread file contains
all the emails in that thread in sequence.

**File naming:** thread_01_schema_review.txt through
thread_18_pregnant_women.txt

**Each email within a thread:**
Date: [date] [time]
From: [email]
To: [email(s)]
---
[email body]
---
[next email in thread below]

**Critical rules:**
No Thread IDs anywhere in the email content.
No "Cross-reference:" metadata blocks.
Jira ticket mentions are casual: "I looked at NUTR-BUG-001
this morning" not "Cross-reference: NUTR-BUG-001."
Meeting references are natural: "following today's standup"
not "see Meeting Note 7."

**Tone:**
Internal team emails: direct, first names only, no pleasantries,
get to the point. End when the content ends.
Investor emails: professional, warm, outcome-focused.
User emails (Roopa): personal, specific, honest.
Late-night emails (Arjun at 7:30 PM, Shristi at 8 PM):
slightly less formal — these are people working late,
not composing official communications.

**New information rule:**
Every thread must contain at least 2-3 specific details that
do not appear in any Jira ticket, sprint retrospective,
or meeting note. These are listed in the summary table above.
These details must appear naturally in the email conversation,
not as a list or summary.

**Critical numbers — exact consistency:**
Day 7 retention: 34% beta week 1, 41% Sprint 8, 43% launch week,
81.8% pregnant women cohort
Sessions per day: pregnant women 4.2, overall average 1.8
Session length: pregnant women 6.3 min, overall 2.8 min
Custom foods: 23 mid-Sprint 7, 47 end Sprint 8, 250 post-launch
App Store: 3.8 Sprint 7, 4.0 Sprint 8, 4.1 launch week
MAU: 847 week 1 post-launch
Pregnant women: 11 users identified, NOT confirmed 3.1x in emails —
that confirmation comes from June research in Sprint 10-13 period.
In these emails it is an early discovery with preliminary numbers.