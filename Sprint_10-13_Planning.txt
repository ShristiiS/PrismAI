# Sprint 10-13 Planning and Retrospective Definition

---

## GLOBAL RULES

**Sprint Planning format:** Word document (.docx)
**Sprint Retrospective format:** Excel document (.xlsx)
**Author of all planning documents:** Shristi Sharmistha
**Author of all retrospectives:** Shristi Sharmistha with team input

**Retrospective Excel structure (Format B):**
Sheet 1: Sprint Summary — delivery vs commitment table
Sheet 2: Retrospective Narrative — all sections in full
Sheet 3: Metrics This Sprint — metric name and value both filled

---

---

# SPRINT 10 PLANNING DOCUMENT

**Document name:** Sprint 10 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** May 13, 2025
**Sprint dates:** May 13 to May 26, 2025
**Sprint goal:** Monitor post-launch metrics closely, fix all
remaining bugs from public launch week, and begin formal
investigation of the pregnant women segment discovered in
the first week of launch.

---

**Context note:**
Sprint 10 is the first post-launch sprint. The team shifts from
building mode to learning mode. No new features are planned.
The priority is watching what real users do with the product,
fixing anything that breaks, and investigating the most
interesting signal from launch week — the 11 pregnant women
users who are engaging at 2-3x the rate of everyone else.

---

**Team Capacity:**
- Arjun Mehta: 10 days (metrics dashboard, cohort analysis, bug fixes)
- Priya Nair: 10 days (bug fixes, iOS Safari custom food issue)
- Kabir Sharma: 10 days (App Store screenshot update, V2 design thinking)
- Ananya Iyer: 10 days (NPS survey, pregnant women interviews, partnership)
- Shristi Sharmistha: 10 days (research coordination, V2 planning, investor update)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| MON-001 | Post-launch metrics dashboard setup | Arjun | 3 | P0 |
| MON-002 | Pregnant women cohort analysis | Arjun | 5 | P1 |
| BUG-010 | Search results not resetting on diary date change | Priya | 2 | P2 |
| AN-CR-003 | Analysis screen performance on low-end Android | Arjun | 3 | P2 |
| NPS-001 | NPS survey implementation and launch | Ananya | 3 | P1 |
| RES-001 | Pregnant women user interviews — 5 interviews | Ananya | 2 | P1 |
| MKT-001 | Dr. Kavitha Rao nutritionist partnership activation | Ananya | 2 | P2 |
| BUG-011 | Custom food serving unit not saving on iOS Safari | Priya | 3 | P1 |
| V2-PLAN-001 | Q3 roadmap planning and V2 feature prioritisation | Shristi | 2 | P1 |

**Total story points committed: 25**

---

**Sprint Goal Success Criteria:**
- Metrics dashboard live and accessible to all team members
- Pregnant women cohort analysis complete with formal numbers
- NPS survey launched May 20 and results shared with team
- All P1 bugs fixed and deployed
- Dr. Kavitha Rao partnership post live
- Q3 priorities documented based on NPS and cohort data
- 5 pregnant women user interviews completed

---

**Dependencies:**
- MON-002 depends on MON-001 being complete first
- RES-001 depends on the 11 user identification from Ananya's
  manual review being confirmed before interviews begin
- NPS-001 requires Arjun to build the in-app banner before
  Ananya can launch the survey on May 20

---

**Risks:**
- Pregnant women cohort analysis: sample size is only 11 users.
  Results may not be statistically significant. Mitigation: Arjun
  runs bias checks before any numbers are shared externally.
- NPS response rate: if fewer than 100 users respond the NPS
  score will not be reliable. Mitigation: survey only sent to
  users who have logged food at least 3 times — a quality filter
  that excludes non-engaged users from dragging down the score.
- BUG-011 iOS Safari: affects approximately 15% of iOS users.
  P1 priority — must be fixed before end of sprint or it will
  suppress custom food creation in our highest-value user segment.

---

**Definition of Done for Sprint 10:**
All 9 tickets moved to Done in Jira. Metrics dashboard verified
by Shristi showing correct numbers. Cohort analysis shared in
team Slack with full methodology documented. NPS survey live and
results available May 21. iOS Safari bug confirmed fixed on
physical iOS device. Q3 priorities documented and shared with Ravi.

---

---

# SPRINT 10 RETROSPECTIVE

**Document name:** Sprint 10 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** May 26, 2025
**Facilitated by:** Shristi Sharmistha

---

**SHEET 1: SPRINT SUMMARY**

Sprint goal: Monitor metrics, fix launch bugs, investigate
pregnant women segment.

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| MON-001 | Yes | Yes | May 15 — custom foods per day metric added after Arjun's early retention observation |
| MON-002 | Yes | Yes | May 18 — 3.1x engagement confirmed, survivorship bias ruled out, iodine finding noted |
| BUG-010 | Yes | Yes | May 15 — same clearSearchState pattern, fix applied to 2 additional places proactively |
| AN-CR-003 | Yes | Yes | May 19 — analysis load time 1.8s → 0.7s on mid-range Android |
| NPS-001 | Yes | Yes | May 21 — NPS 34, 187 responses, goal setup complexity as top complaint |
| RES-001 | Yes | Yes | May 22 — 5 interviews, WhatsApp group referral behaviour discovered |
| MKT-001 | Yes | Yes | May 22 — Kavitha Rao post live, 89 installs in 48 hours |
| BUG-011 | Yes | Yes | May 16 — iOS Safari onBlur fix applied to all 6 free-text fields |
| V2-PLAN-001 | Yes | Yes | May 25 — Q3 priorities documented, shared with Ravi |

Delivery rate: 9 out of 9. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 10 was the most intellectually interesting sprint of the
project. For the first time in 10 sprints the team was not building
new features — we were learning from real users. Two discoveries
defined the sprint. First: the NPS survey confirmed what we feared —
38% of users who start goal setup do not complete it, and the top
open text complaint is goal setup complexity. Second: the pregnant
women cohort analysis revealed a segment we did not build for with
3.1x engagement and 81.8% Day 7 retention. These two findings will
shape Q3 completely.

**What went well:**

1. The pregnant women cohort analysis methodology was rigorous.
Arjun ran two bias checks before sharing any numbers — survivorship
bias check and secondary identification method (folate + iron
combination). The 3.1x engagement and 81.8% Day 7 retention are
confirmed by multiple verification methods. We can share these
numbers with Ravi with confidence.

2. BUG-011 iOS Safari fix was the most impactful bug fix of the
post-launch period. Custom food creation was silently failing for
15% of iOS users. These are exactly the users most likely to create
custom Indian food entries — and therefore our highest-retention
users. Fixing this unblocked retention improvement we did not
even know was being suppressed.

3. The NPS survey question design was better than expected. Shristi
added a second question — what one feature would make you most
likely to recommend Nutrivana — which generated more actionable
data than the standard NPS score. Custom recipe builder, barcode
scanner, and simplified goal setup as the top three requests give
us a clear Q3 feature priority ranking.

4. The pregnant women user interviews produced a finding that data
alone could not: the WhatsApp group referral behaviour. 2 of 5
users had already recommended Nutrivana in their pregnancy WhatsApp
groups unprompted. This is organic viral potential in a tightly
networked community. No amount of cohort analysis would have
revealed this — it required talking to users.

**What did not go well:**

1. MON-002 took longer than estimated because Arjun ran the full
bias verification suite before sharing results. This was the right
call — the numbers are too important to share without verification.
But it means the cohort analysis was not available until May 18,
later than the sprint plan expected. Research tasks need longer
time estimates than engineering tasks.

2. The NPS score of 34 is below our Q2 target of 35. The gap is
small (1 point) but it is a miss. The more important finding is
the open text — goal setup complexity is the single most mentioned
improvement. We knew about this from the March user interviews.
We should have acted faster. This pattern — knowing about a problem
from user research but not acting until data confirms it — is the
recurring failure mode. We need to break it.

**Key learnings:**

1. Small samples can be significant signals. 11 pregnant women
users out of 850 total is 1.3%. In most analytics frameworks this
would be noise. But 11 users with 81.8% Day 7 retention in a
product where overall retention is 43% is not noise. It is a
directional signal strong enough to change Q3 strategy.

2. Research tasks take longer than engineering tasks because quality
requires iteration. An engineering ticket has a clear definition
of done (code works, tests pass). A research ticket's definition
of done is fuzzier (findings are credible, methodology is sound).
Build this into sprint planning time estimates.

3. User interviews reveal things data cannot. The WhatsApp referral
behaviour would never appear in a dashboard. Qualitative research
is not optional for a product at this stage.

**Decisions made this sprint:**

1. Pregnant women segment confirmed as Q3 priority 2 (after
   simplified onboarding). Data is credible, user interviews
   validated, referral potential is significant.

2. Q3 priorities locked: simplified onboarding (38% drop-off),
   prenatal presets (3.1x engagement), custom recipe builder
   (top NPS request).

3. App Store screenshots to be updated with Chapati search result
   image — Ananya's recommendation approved.

4. Tests-first standard extended: any feature touching both mg
   and mcg micronutrient displays must have explicit unit display
   test cases.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Share pregnant women cohort analysis with Ravi in investor update | Shristi | May 28 |
| Update App Store screenshots with Chapati search result | Kabir/Ananya | June 5 |
| Begin Sprint 11 research planning — funnel analysis and feature adoption reports | Shristi | May 27 |
| Document Q3 priorities formally in roadmap document | Shristi | May 30 |
| Ananya schedule remaining pregnant women interviews for June | Ananya | May 28 |

**Team health: 4/5**
The shift from building to learning is energising and slightly
anxiety-inducing simultaneously. The team spent 9 sprints shipping
features. Sprint 10 was the first sprint where the work was
understanding what users actually do. It feels different — less
tangible progress but more genuine insight. The pregnant women
discovery lifted morale significantly. Finding something you did
not expect that changes your strategy is the best feeling in product.

---

**SHEET 3: METRICS THIS SPRINT**

| Metric | Value |
|---|---|
| MAU end of sprint (May 26) | approximately 1,100 |
| MAU end of May | 1,247 |
| Day 7 retention end of May | 45% |
| NPS score May 20 | 34 |
| NPS response count | 187 |
| NPS response rate | 23% |
| Custom foods cumulative end of sprint | approximately 280 |
| App Store rating end of sprint | 4.1 |
| Pregnant women Day 7 retention | 81.8% (9 of 11 users) |
| Pregnant women sessions per day | 4.2 vs 1.8 overall average |
| Pregnant women session length | 6.3 min vs 2.8 min overall |
| Pregnant women engagement multiple | 3.1x |
| Dr. Kavitha Rao partnership installs | 89 in 48 hours |
| Analysis screen load time after optimisation | 0.7 seconds |
| iOS Safari bug: affected users | approximately 15% of iOS users |
| Bugs fixed this sprint | 2 (BUG-010, BUG-011) |

---

---

# SPRINT 11 PLANNING DOCUMENT

**Document name:** Sprint 11 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** May 27, 2025
**Sprint dates:** May 27 to June 9, 2025
**Sprint goal:** Complete all research and analysis documents that
provide the data foundation for Q3 decisions. By end of sprint
the team has confirmed data on custom food 2.3x retention, 38%
goal setting drop-off, and May cohort retention patterns. No new
features this sprint.

---

**Context note:**
Sprint 11 is a pure research and analysis sprint. This is unusual
— two consecutive sprints without shipping new features. The reason
is deliberate. Before spending Sprint 12-13 building new features
we need to be certain we are building the right things. The Sprint
10 discoveries (pregnant women, NPS open text about goal setup)
need formal data backing before they drive Q3 investment decisions.
A week spent on research now prevents months of building the wrong thing.

---

**Team Capacity:**
- Arjun Mehta: 10 days (retention cohort, funnel analysis, metrics)
- Priya Nair: 10 days (bug fix BUG-012, technical support for research queries)
- Kabir Sharma: 10 days (competitive analysis, V2 design sketches)
- Ananya Iyer: 10 days (customer interview documentation, competitive update)
- Shristi Sharmistha: 10 days (feature adoption reports, funnel report, analysis)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| RES-002 | Feature adoption report — Custom Food Creator | Shristi | 3 | P1 |
| RES-003 | Feature adoption report — Nutrient Analysis | Shristi | 3 | P1 |
| RES-004 | Goal setting funnel analysis — 38% drop-off | Arjun | 5 | P0 |
| RES-005 | Customer interview notes — 8 beta users March | Ananya | 2 | P2 |
| RES-006 | Competitive analysis update — post-launch | Shristi | 2 | P2 |
| MET-001 | Weekly metrics sheet — May complete | Arjun | 2 | P1 |
| RET-001 | Retention cohort analysis — May cohort | Arjun | 3 | P1 |
| BUG-012 | Trend chart double-counting supplement logs | Arjun | 2 | P2 |
| FUN-001 | Funnel analysis report — March and June cohorts | Shristi | 3 | P1 |

**Total story points committed: 25**

---

**Sprint Goal Success Criteria:**
- Custom food 2.3x Day 30 retention formally confirmed with
  sample sizes documented
- First-3-sessions custom food insight confirmed with data
- 38% goal setting drop-off confirmed with exact funnel data
- May metrics sheet complete with all 4 weeks of May documented
- May retention cohort analysis complete with custom food
  segmentation
- All 8 March beta user interviews formally documented
- Funnel analysis report complete with both March and June funnels

---

**Dependencies:**
- RES-002 depends on MET-001 being complete — need May metrics
  to provide context for feature adoption numbers
- RES-004 depends on Arjun having built the funnel query — he
  starts this on May 27 before any other Sprint 11 ticket
- FUN-001 depends on RES-004 being complete — the funnel report
  synthesises the raw funnel analysis data into a full document

---

**Risks:**
- RES-004 funnel analysis: the query spans 3 different database
  tables with timestamps. If timestamp data is incomplete for
  some users the drop-off percentages will be inaccurate.
  Mitigation: Arjun validates the query against a sample of
  known users before running the full analysis.
- RES-002 retention correlation: the custom food cohort (287
  users) and non-custom-food cohort (413 users) must be well
  defined before the 2.3x number is stated. Sample size
  validation is required.

---

**Definition of Done for Sprint 11:**
All 9 research documents completed and shared in team Slack.
Every number in RES-002 and RES-004 verified against Supabase
raw data. Funnel analysis 38% drop-off confirmed with sample
size documented. May metrics sheet validated by Shristi against
Supabase. No research document contains unverified claims.

---

---

# SPRINT 11 RETROSPECTIVE

**Document name:** Sprint 11 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** June 9, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| RES-002 | Yes | Yes | June 3 — 2.3x confirmed, first-3-sessions insight discovered, 312 unique foods vs 847 entries distinction documented |
| RES-003 | Yes | Yes | June 2 — 67% weekly analysis engagement confirmed, 29% lift from AN-CR-001 redesign |
| RES-004 | Yes | Yes | June 4 — 38% drop-off confirmed, 80% of abandoners churn within 3 days, 1.8 min abandon time documented |
| RES-005 | Yes | Yes | June 3 — goal setup confusion in March interviews mapped to funnel finding |
| RES-006 | Yes | Yes | June 2 — no competitive threats identified, Nutrivana differentiation intact |
| MET-001 | Yes | Yes | June 4 — all 4 weeks of May locked, MAU 1,247 verified |
| RET-001 | Yes | Yes | June 2 — custom food users Day 30 retention 34% vs 15%, gap widening at Day 14 |
| BUG-012 | Yes | Yes | June 4 — source_type filter added, regression test added |
| FUN-001 | Yes | Yes | June 4 — both funnels complete, 100% internal vs 62% real-world completion documented |

Delivery rate: 9 out of 9. 100%.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 11 produced the most important product insights of the
entire project. The custom food 2.3x retention correlation is now
formally confirmed. The 38% goal setting drop-off is confirmed with
exact data. The first-3-sessions custom food window is confirmed.
Together these findings answer the two most important Q3 product
questions: why are users churning (goal setup complexity) and what
makes users stay (early personalisation through custom food). Two
sprints of research have given us more confidence in Q3 priorities
than we had after 9 sprints of building.

**What went well:**

1. The first-3-sessions custom food insight in RES-002 was not
in the original research plan — Arjun discovered it while running
the retention correlation analysis. Users who create their first
custom food within sessions 1-3 have Day 30 retention of 41%
vs 15% for users who never create one. This changes the onboarding
design — custom food creation should be part of the first session
experience, not a feature users discover later.

2. The March user interview to funnel data connection in RES-005
validated the entire research methodology. In March 4 of 8 users
mentioned goal setup confusion. In May the NPS open text showed
23 mentions. In May the funnel confirmed 38% abandonment. Three
separate research methods, three months apart, all pointing to
the same problem. This kind of methodological consistency gives
us high confidence in the simplified onboarding decision.

3. The competitive analysis update in RES-006 confirmed that
Nutrivana's differentiation is intact. HealthifyMe added restaurant
Indian foods but no micronutrient tracking. No new competitors.
The pregnant women segment is uncontested territory.

**What did not go well:**

1. RES-004 took the full sprint instead of the first 5 days as
planned. The funnel query required validating timestamp data
integrity across 3 tables before Arjun was confident the drop-off
percentages were accurate. Research that depends on data quality
validation is harder to time-box than feature work.

2. The March interview notes in RES-005 revealed that goal setup
confusion was documented 3 months before the funnel confirmed it.
We had the user signal in March. The funnel data in May is just
the statistical confirmation of what users told us directly. We
should have moved faster. This is the second time this observation
has been made (first was in the Sprint 10 retrospective). The
pattern of waiting for data confirmation before acting on clear
user signals is now a documented team failure mode.

**Key learnings:**

1. User signals from qualitative research should trigger action
faster than we have been comfortable with. The goal setup confusion
was signalled in March. We did not act until June. 3 months of
unnecessary churn happened in between.

2. The first-3-sessions window insight changes how we think about
onboarding permanently. Onboarding is not just about explaining
the app. It is about getting users to personalise it within the
first 3 sessions because personalisation is what makes them stay.

3. 100% internal testing completion vs 62% real-world completion
(FUN-001 finding) is the most important process insight of the
project. Internal testing is not a proxy for real user behaviour.
Teams are motivated to complete the flows they built. Real users
are not.

**Decisions made this sprint:**

1. Simplified onboarding confirmed as Sprint 12 top priority
   with formal data justification (38% drop-off, 80% of abandoners
   churn within 3 days).

2. Custom food creation nudge to be added to simplified onboarding
   flow — the first-3-sessions data justifies making it part of
   core setup not a secondary discovery.

3. Internal testing must always include users who were not involved
   in building the feature — the 100% vs 62% completion gap proves
   that builder testing is systematically biased toward completion.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Start simplified onboarding Figma designs | Kabir | June 10 |
| Share 38% funnel data with Ravi as part of Q3 rationale | Shristi | June 12 |
| Add custom food nudge to simplified onboarding brief | Shristi | June 12 |
| Arjun builds the A/B test infrastructure for Sprint 12 | Arjun | June 13 |
| Ananya identifies users who abandoned goal setup for simplified onboarding user testing | Ananya | June 12 |

**Team health: 5/5**
Two sprints of research after 9 sprints of building was the right
call. The team needed to understand what they built before deciding
what to build next. The data confirmed the intuitions we had but
could not act on. The pregnant women segment gives the team a
genuine sense of discovery — we built something that serves a
user group we never planned for. That is a good feeling.

---

**SHEET 3: METRICS THIS SPRINT**

| Metric | Value |
|---|---|
| Custom food 2.3x retention correlation | Confirmed — 34% vs 15% Day 30 |
| Custom food first-3-sessions retention | 41% Day 30 vs 15% never |
| Goal setting abandonment rate | 38% of users who start |
| Abandoners who churn within 3 days | 80% |
| Average time on EER form — abandoners | 1.8 minutes |
| Average time on EER form — completers | 4.2 minutes |
| Analysis engagement weekly | 67% of active users |
| Analysis engagement before AN-CR-001 | 52% |
| Analysis engagement after AN-CR-001 | 67% (29% improvement) |
| MAU end of May confirmed | 1,247 |
| Day 7 retention end of May | 45% |
| Custom foods cumulative end of May | approximately 300 |
| Unique custom food names | 312 |
| March user interviews — goal setup confusion mentions | 4 of 8 users |
| Internal testing goal setup completion | 100% |
| Real user goal setup completion | 62% |

---

---

# SPRINT 12 PLANNING DOCUMENT

**Document name:** Sprint 12 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** June 10, 2025
**Sprint dates:** June 10 to June 23, 2025
**Sprint goal:** Ship simplified onboarding to 50% of users via
A/B test and begin prenatal micronutrient presets design and
backend. By end of sprint the team has A/B test data confirming
simplified onboarding works before full rollout in Sprint 13.

---

**Context note:**
Sprint 12 is the return to building after two research sprints.
The research was not optional — without the 38% funnel data and
the 3.1x pregnant women engagement data the team would not have
had the confidence to deprioritise other features in favour of
these two. Every decision in Sprint 12 is grounded in specific
data from Sprints 10 and 11.

Sprint 12 is ambitious — 11 tickets including two significant
feature builds. The risk is scope. PRE-003 (prenatal frontend)
is explicitly planned to carry over to Sprint 13. This is a
deliberate scope decision not a failure to estimate.

---

**Team Capacity:**
- Arjun Mehta: 10 days (ONBD-002 backend, PRE-002 backend, A/B test, metrics)
- Priya Nair: 10 days (ONBD-003 frontend, PRE-003 frontend start)
- Kabir Sharma: 10 days (ONBD-001 design, PRE-001 design)
- Ananya Iyer: 10 days (NPS-002 setup, MKT-002, user testing for designs)
- Shristi Sharmistha: 10 days (BUG-013, coordination, PRE-001 research review)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| ONBD-001 | Simplified onboarding — 3 question flow design | Kabir | 5 | P0 |
| ONBD-002 | Simplified onboarding — backend implementation | Arjun | 5 | P0 |
| ONBD-003 | Simplified onboarding — frontend implementation | Priya | 5 | P0 |
| PRE-001 | Prenatal presets — research and design | Kabir | 5 | P1 |
| PRE-002 | Prenatal presets — trimester auto-update logic | Arjun | 3 | P1 |
| MET-002 | Weekly metrics — June week 1 and 2 | Arjun | 1 | P1 |
| ONBD-004 | Simplified onboarding A/B test setup | Arjun | 3 | P1 |
| BUG-013 | Retention numbers inconsistent between reports | Arjun | 2 | P2 |
| MKT-002 | Press outreach — building the data story | Ananya | 2 | P2 |
| NPS-002 | NPS survey round 2 — June 30 setup | Ananya | 2 | P1 |
| PRE-003 | Prenatal presets — frontend implementation (partial) | Priya | 5 | P1 |

**Total story points committed: 38**
**Note:** PRE-003 is deliberately planned to carry over to Sprint 13.
Sprint 12 scope for PRE-003 is pregnancy option in onboarding and
trimester selection. Sprint 13 scope is notification UI, edge cases,
user testing, and deployment.

---

**Sprint Goal Success Criteria:**
- Simplified onboarding 3-question flow designed, built, and
  in A/B test by June 20
- A/B test showing preliminary completion rate data by June 18
- ICMR prenatal research complete and design approved by June 16
- Prenatal trimester auto-update backend logic complete
- NPS survey set up and ready to launch June 30
- BUG-013 retention metric definition standardised
- PRE-003 Sprint 12 scope complete (pregnancy option and trimester screen)

---

**Dependencies:**
- ONBD-003 depends on ONBD-001 Figma designs being approved
  before Priya starts implementation
- ONBD-004 A/B test depends on ONBD-002 and ONBD-003 being
  complete — cannot test what is not built
- PRE-002 depends on PRE-001 research being complete — Arjun
  needs the ICMR target values before building the auto-update logic
- PRE-003 depends on PRE-001 Figma designs — Priya starts
  implementation once Kabir confirms designs are approved

---

**Hard deadline:** Simplified onboarding must be in A/B test
by June 20 to have 10 days of data before Sprint 13 rollout
decision on June 28.

---

**Risks:**
- ONBD-001 user testing: the design must be tested with users
  who previously abandoned the original EER onboarding. If we
  cannot identify enough of these users the user testing will
  not provide the most meaningful validation.
  Mitigation: Ananya identifies abandoned users from funnel
  data for Kabir's testing pool.
- PRE-001 ICMR vs WHO debate: the ICMR iron value (35mg) differs
  significantly from WHO (27mg). If the team does not reach
  consensus quickly this delays the design and backend work.
  Mitigation: Arjun and Ananya provide supporting evidence for
  ICMR before the decision is required.
- Sprint scope: 38 story points is the highest in the project
  history. PRE-003 is explicitly planned to carry over but
  other tickets must not slip.

---

**Definition of Done for Sprint 12:**
Simplified onboarding live in A/B test with 50/50 split confirmed.
ICMR prenatal values confirmed and documented in tech spec.
PRE-002 backend tested with simulated trimester transitions.
BUG-013 metric definition documented and standardised.
NPS-002 survey configured and ready for June 30 launch.
PRE-003 Sprint 12 scope complete — pregnancy option and trimester
selection screen working in staging.

---

---

# SPRINT 12 RETROSPECTIVE

**Document name:** Sprint 12 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** June 23, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| ONBD-001 | Yes | Yes | June 16 — user tested with 3 previous abandoners, all 3 completed in under 2 minutes |
| ONBD-002 | Yes | Yes | June 18 — neutral defaults within 200 calories of full EER, profile completion trigger working |
| ONBD-003 | Yes | Yes | June 19 — Shristi completed in 1 min 47 sec from fresh account |
| PRE-001 | Yes | Yes | June 16 — ICMR values confirmed, Pregnant added as fourth goal option |
| PRE-002 | Yes | Yes | June 17 — trimester calculation and notification system complete |
| MET-002 | Yes | Yes | June 16 — June week 1 MAU 1,456, week 2 MAU 1,847 |
| ONBD-004 | Yes | Yes | June 18 — A/B test live, preliminary 84% vs 61% after first week |
| BUG-013 | Yes | Yes | June 16 — Day 7 retention definition standardised across all reports |
| MKT-002 | Yes | In Progress | Pitch document ready, outreach begins Sprint 13 |
| NPS-002 | Yes | Yes | June 14 — survey configured, ready for June 30 launch |
| PRE-003 | Yes | Partial | June 20 — Sprint 12 scope complete, Sprint 13 scope carries over as planned |

Delivery rate: 10 of 11 fully delivered. MKT-002 in progress
as planned (outreach was always Sprint 13 scope). PRE-003 partial
delivery was planned from the start — Sprint 12 scope fully complete.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 12 was the most productive sprint since Sprint 6 (MVP).
The team returned to building after two research sprints with
complete clarity on what to build and why. Every ticket had a
specific data justification. The simplified onboarding A/B test
preliminary result (84% vs 61% completion) is the clearest
product success signal since the custom food 2.3x retention
discovery. The ICMR vs WHO decision for prenatal values was the
most intellectually rigorous product decision of the project —
choosing Indian clinical guidelines over international standards
because our user base demands it.

**What went well:**

1. The ONBD-001 user testing result was extraordinary. Kabir
tested the Figma prototype with 3 users who had previously
abandoned the original EER onboarding (identified from funnel
data by Ananya). All 3 completed the simplified flow in under
2 minutes. One said: this is much simpler than the other app
I tried. It just asked me what I need to know. This is the best
possible validation — getting the users who failed to complete
the original flow to successfully complete the replacement.

2. The ICMR prenatal research was thorough and clinically grounded.
Using ICMR values over WHO values because Indian pregnant women
have higher baseline iron and B12 deficiency rates is a product
decision that shows genuine care for our specific users. Ananya's
real-world validation (a user's OB-GYN prescribed ICMR-aligned
values) gave us the confidence to commit.

3. The A/B test infrastructure Arjun built is clean and reusable.
The onboarding_variant column in user_profiles is the pattern
we should use for all future A/B tests. Simple, auditable,
tied to the user record permanently for post-test analysis.

4. PRE-003 planned carry-over worked as intended. By explicitly
acknowledging in sprint planning that PRE-003 would carry over
to Sprint 13 the team did not feel pressure to rush the prenatal
implementation. The quality of the Sprint 12 PRE-003 work
(pregnancy option, trimester selection) is better because we
did not rush the remaining work into an already full sprint.

**What did not go well:**

1. Sprint 12 was the most ambitious sprint by story points (38).
While everything was delivered the team felt stretched in the
final week with ONBD-003, PRE-003, and ONBD-004 all in flight
simultaneously. Arjun, Priya, and Kabir were each carrying 2-3
active tickets in the last 5 days. This is acceptable for one
sprint but should not be the regular pace.

2. MKT-002 press pitch is ready but no outreach happened this
sprint. Ananya built the pitch document but the actual outreach
to publications requires a dedicated sprint focus that was not
available with the simplified onboarding and prenatal work also
in progress. Press outreach gets its own focus in Sprint 13.

**Key learnings:**

1. Data-justified sprints move faster than intuition-justified
sprints. Every Sprint 12 decision had a data source. ONBD-001
was justified by 38% drop-off and 1.8 minute abandon time.
PRE-001 was justified by 3.1x engagement and user interview
quotes. When the team knows WHY they are building something they
spend less time debating scope and more time building.

2. Using previous abandoners as the user testing pool for
ONBD-001 was the correct approach. Testing a redesign with users
who succeeded with the original tells you if the redesign is
as good as the original. Testing with users who failed tells
you if the redesign solves the actual problem.

3. ICMR vs WHO is not just a data choice — it is a positioning
choice. Using ICMR values communicates that we serve Indian users
specifically, not Indian users as a subset of global users.

**Decisions made this sprint:**

1. Simplified onboarding ships to 100% of users in Sprint 13
   pending A/B test final results (preliminary 84% vs 61% — decision
   is clear, formal rollout waits for 10-day data).

2. ICMR values used for all prenatal presets. Documented in
   technical spec under Data Sources.

3. Day 7 retention standard definition locked: user who opens
   app AND logs at least one food item on exactly day 7 from
   registration date. Applied everywhere.

4. Prenatal preset attribution line: Targets based on ICMR
   dietary guidelines for Indian pregnant women. Appears on
   result screen.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Complete PRE-003 — notification UI, edge cases, user testing | Priya | June 26 |
| Ship simplified onboarding to 100% once A/B test final results available | Arjun | June 28 |
| Launch NPS-002 survey June 30 | Ananya | June 30 |
| Begin press outreach with pregnant women story angle | Ananya | June 25 |
| Complete Q2 OKR review | Shristi | June 30 |

**Team health: 5/5**
The combination of clear data-driven priorities, significant
product wins (A/B test preliminary result), and the ICMR decision
giving the team a genuine sense of purpose — building specifically
for Indian users not generic users — created the highest team
energy since the MVP launch. The stretched final week was taxing
but the team is proud of what they shipped.

---

**SHEET 3: METRICS THIS SPRINT**

| Metric | Value |
|---|---|
| Simplified onboarding A/B test — simplified completion | 84% (preliminary after 1 week) |
| Simplified onboarding A/B test — control completion | 61% |
| Simplified onboarding average time — simplified | 1.9 minutes |
| Simplified onboarding average time — control | 4.1 minutes |
| MAU June week 1 (June 1-7) | 1,456 |
| MAU June week 2 (June 8-14) | 1,847 |
| Day 7 retention June week 2 | 46% |
| Custom foods cumulative June 23 | approximately 634 |
| App Store rating | 4.1 |
| ONBD-001 user test: previous abandoners who completed simplified flow | 3 of 3 |
| PRE-001 user validation: OB-GYN prescribed values matching ICMR | confirmed by 1 user |
| A/B test users in simplified group | 50% of new registrations from June 19 |

---

---

# SPRINT 13 PLANNING DOCUMENT

**Document name:** Sprint 13 Planning — Nutrivana
**Format:** Word (.docx)
**Date:** June 24, 2025
**Sprint dates:** June 24 to June 30, 2025
**Sprint goal:** Close Q2 completely. Ship prenatal presets to
production. Roll out simplified onboarding to 100% of users.
Verify and lock all Q2 closing metrics. Complete Q2 OKR review.

---

**Context note:**
Sprint 13 is a 7-day sprint — the shortest in the project. It is
also the most deadline-driven. June 30 is the end of Q2. Every
ticket must be completed by June 30. The team has only one new
build to complete (PRE-003 carry-over) and everything else is
closure work — shipping, reviewing, documenting, and communicating.

The tone of Sprint 13 is different from all previous sprints.
This is not a building sprint or a research sprint. It is a
closing sprint. The work is completing things that are already
started, verifying numbers that need to be accurate, and
communicating what Q2 meant to the team and to investors.

---

**Team Capacity:**
- Arjun Mehta: 7 days (ONBD-005 rollout, MET-003, MET-004, RET-002)
- Priya Nair: 7 days (PRE-003-COMPLETE, BUG-014 if discovered)
- Kabir Sharma: 7 days (design review PRE-003, design support)
- Ananya Iyer: 7 days (NPS-002 launch, MKT-002 press outreach)
- Shristi Sharmistha: 7 days (Q2-REVIEW-001, INVEST-001, overall coordination)

---

**Sprint Backlog:**

| Ticket | Title | Assignee | Points | Priority |
|---|---|---|---|---|
| PRE-003-COMPLETE | Prenatal presets — complete and ship | Priya | 3 | P0 |
| ONBD-005 | Simplified onboarding — ship to 100% | Arjun | 2 | P0 |
| MET-003 | Weekly metrics — June complete and Q2 final | Arjun | 2 | P0 |
| Q2-REVIEW-001 | Q2 OKR review — all objectives assessed | Shristi | 3 | P0 |
| RET-002 | Retention cohort analysis — June cohort | Arjun | 3 | P1 |
| BUG-014 | Prenatal goal values wrong units (if discovered) | Priya | 2 | P1 |
| INVEST-001 | Q2 investor update to Ravi | Shristi | 1 | P1 |
| MET-004 | June metrics sheet finalised | Arjun | 1 | P0 |

**Total story points committed: 17**
**Note:** BUG-014 is in the backlog as a contingency — it was
not known at sprint planning time, it was discovered post-deployment
of PRE-003. Story points are reserved.

---

**Sprint Goal Success Criteria:**
- Prenatal presets live in production by June 26
- Simplified onboarding shipped to 100% of users by June 28
- Q2 OKR review complete and shared by June 30
- All Q2 closing numbers verified: MAU 3512, retention 47%,
  NPS 41, App Store 4.2, custom foods 847
- Investor update sent to Ravi by June 30
- Zero P1 bugs in production at Q2 close

---

**Hard deadlines:**
- PRE-003-COMPLETE: June 26 (must ship before NPS survey June 30
  so prenatal users can give satisfaction feedback)
- ONBD-005: June 28 (must ship before Q2 close to affect closing
  retention metrics)
- Q2-REVIEW-001: June 30 (Q2 closes June 30)
- MET-003 and MET-004: June 30 (needed for Q2 OKR review)
- INVEST-001: June 30 (Ravi expects Q2 update on the last day
  of Q2)

---

**Risks:**
- PRE-003-COMPLETE: health-critical feature. If a bug is found
  post-deployment (like BUG-014 unit display) the team must
  stop everything and fix within 24 hours.
  Mitigation: Priya tests the complete user journey including
  the analysis screen — not just the onboarding flow — before
  deployment.
- Q2 closing metrics: MAU fluctuates daily. The June 30 MAU
  number must be from Supabase at the close of business June 30
  not an earlier snapshot.
  Mitigation: Arjun pulls the final MAU number on June 30 after
  5 PM IST.
- INVEST-001: Ravi's response to the Q2 update may require a
  follow-up before Q3 planning begins. Build time for follow-up
  correspondence into June 30 schedule.

---

**Definition of Done for Sprint 13:**
Prenatal presets live with zero P1 bugs. Simplified onboarding
at 100% rollout. All Q2 closing numbers verified against Supabase
raw data. Q2 OKR review shared with team and Ravi. Investor
update sent and acknowledged. June metrics sheet complete.

---

---

# SPRINT 13 RETROSPECTIVE

**Document name:** Sprint 13 Retrospective — Nutrivana
**Format:** Excel (.xlsx)
**Date:** June 30, 2025

---

**SHEET 1: SPRINT SUMMARY**

| Ticket | Committed | Delivered | Notes |
|---|---|---|---|
| PRE-003-COMPLETE | Yes | Yes | June 26 — 87 second average setup, all 11 pregnant users updated within 24 hours |
| ONBD-005 | Yes | Yes | June 28 — 84.7% vs 61.3% final A/B result, Day 7 retention 47.3% vs 43.1% |
| MET-003 | Yes | Yes | June 30 — all Q2 closing numbers verified: MAU 3512, retention 47%, NPS 41 |
| Q2-REVIEW-001 | Yes | Yes | June 30 — shared with team and Ravi, all 4 objectives assessed honestly |
| RET-002 | Yes | Yes | June 30 — simplified onboarding users 51.2% Day 7 retention |
| BUG-014 | Not in plan | Yes | June 26 — discovered and fixed within 4 hours post-deployment |
| INVEST-001 | Yes | Yes | June 30 — Ravi responded same evening |
| MET-004 | Yes | Yes | June 30 — top 10 custom foods list locked, all 847 entries verified |

Delivery rate: 8 of 8. 100%.
Additionally fixed BUG-014 which was not in the sprint plan.

---

**SHEET 2: RETROSPECTIVE NARRATIVE**

**Sprint summary:**
Sprint 13 closed Q2 on time and on quality. Prenatal presets
shipped June 26 with the fastest feature adoption in project
history — 87 seconds average setup time and all 11 identified
pregnant users updated within 24 hours. Simplified onboarding
shipped to 100% of users June 28 with final A/B results confirming
84.7% vs 61.3% completion. BUG-014 (prenatal unit display error)
was discovered and fixed within 4 hours — the health-critical
response standard established after GOAL-BUG-002 worked. Q2
closed with MAU 3,512, NPS 41, Day 7 retention 47%. The team
shipped everything it committed to. Q2 is done.

**What went well:**

1. PRE-003-COMPLETE user adoption speed is the project highlight
of Q2. 87 seconds average setup time for prenatal presets.
All 11 identified pregnant users updated within 24 hours of the
prompt going live. One user quote captures the moment: finally
an app that knows I am in my second trimester and needs 600mcg
folate not just 400mcg. That sentence is worth the entire Sprint 12
research investment.

2. BUG-014 response time was 4 hours from discovery to fix.
The health-critical response standard we established after
GOAL-BUG-002 worked exactly as designed. Priya had the root
cause identified within 1 hour and the fix deployed within 4.
The post-fix process (regression tests added, definition of done
updated, retrospective note) also worked.

3. The Q2 OKR review is the most honest retrospective document
of the project. The retention miss (47% vs 50%) is acknowledged
with the exact cause (38% drop-off) and the exact fix timeline
(simplified onboarding shipped June 28, A/B test shows 51.2%
retention for simplified users). Investors and future team
members reading this document will understand exactly what happened
and why.

4. Ravi's response to the investor update confirmed strategic
alignment on the pregnant women segment. His question about
defensibility prompted Shristi to articulate the core argument:
ICMR prenatal presets on top of deep micronutrient tracking
infrastructure is the combination that is hard to replicate.
The value is not in the ICMR data (publicly available) but in
the tracking infrastructure that makes the presets useful.

**What did not go well:**

1. BUG-014 should not have reached production. The prenatal
presets user testing covered the onboarding flow but not the
analysis screen. The bug was in the analysis screen. Testing
coverage gap. The definition of done update (any new micronutrient
feature must be verified on analysis screen AND onboarding flow)
addresses this for future sprints.

2. MKT-002 press outreach did not land any coverage in Sprint 13.
Ananya sent pitches to 4 publications. Zero responses by June 30.
This is not surprising — press cycles are slow and publications
receive many pitches. But the Q2 OKR review correctly calls out
earned media as a complete failure for Q2. Q3 will require a
different approach — building relationships with journalists before
pitching rather than cold pitching with data.

**Key learnings:**

1. The fastest feature adoption in project history (prenatal presets,
87 second average setup) came from a feature that was designed
for a specific user group with specific clinical needs. Generic
features have average adoption. Features that solve specific
real problems for specific users have extraordinary adoption.

2. The BUG-014 lesson — testing coverage must include every screen
the feature affects not just the new screens — applies to all
future feature work. New features change the product context.
All affected screens must be tested not just the new ones.

3. The Q2 OKR review pattern from Arjun — retention improvement
came from fixing things not adding things — should shape Q3
planning. At least one sprint in Q3 should be explicitly dedicated
to fixing, optimising, and cleaning up rather than adding new features.

4. The research-before-building approach of Sprints 10-11 paid
off completely in Sprints 12-13. Every build decision was data-backed.
The team moved faster and with more confidence because the why
was established before the how began.

**Decisions made this sprint:**

1. Simplified onboarding is now standard for all new users.
   A/B test code removed. EER form in Advanced goal settings.

2. Prenatal presets shipped. ICMR values as standard.
   BUG-014 fix applied. Regression tests in place.

3. Unit display test standard: any feature touching micronutrient
   display must verify correct units on all screens where
   micronutrients appear — not just the new screens.

4. Q3 will include at least one dedicated improvement sprint
   (no new features, only fixes and optimisations) as a standing
   commitment.

**Action items:**

| Action | Owner | Due |
|---|---|---|
| Q3 OKR planning session | Shristi | July 7 |
| Press outreach strategy revision — relationship-first not cold pitch | Ananya | July 7 |
| Q3 sprint planning with simplified onboarding as standard baseline | All | July 7 |
| Custom recipe builder technical design begins | Arjun | July 8 |
| Prenatal marketing to OB-GYN offices and maternal health communities | Ananya | July 10 |

**Team health: 5/5**
Q2 is closed and Q2 was good. 315% MAU growth in 2 months with
zero paid acquisition. 3,512 users. 847 Indian food entries. 41
NPS. 47% Day 7 retention. Prenatal presets shipped. Simplified
onboarding shipped and working. The pregnant women discovery is
the most exciting product finding in the project. The team goes
into Q3 with clear priorities, strong data foundation, and
genuine momentum.

---

**SHEET 3: METRICS THIS SPRINT**

| Metric | Value |
|---|---|
| MAU June 30 (Q2 final) | 3,512 |
| Day 7 retention June 30 (Q2 final) | 47% |
| App Store rating June 30 | 4.2 |
| NPS June 30 | 41 |
| Custom foods June 30 | 847 total entries, 312 unique food names |
| Top custom food | Chapati — 234 entries |
| Simplified onboarding completion (simplified group) | 84.7% |
| Simplified onboarding completion (control group) | 61.3% |
| Simplified onboarding Day 7 retention (simplified) | 47.3% |
| Simplified onboarding Day 7 retention (control) | 43.1% |
| Prenatal presets average setup time | 87 seconds |
| Pregnant users updated to prenatal presets within 24hr | 11 of 11 |
| BUG-014 time from discovery to fix | 4 hours |
| MAU growth since launch (May 1 to June 30) | 847 → 3,512 (315%) |
| Paid acquisition contribution to growth | Zero |
| Partnership-driven organic installs | 412 (Nambiar 267, Kavitha 145) |
| Instagram followers | 623 at 5.2% engagement rate |
| Q2 OKR objectives achieved or partially achieved | 4 of 4 |
| Q2 OKR KRs fully achieved | 13 of 17 |

---

## GPT-4o GENERATION INSTRUCTIONS

**For Sprint Planning documents (Word):**
Generate 4 Word documents:
- sprint10_planning.docx
- sprint11_planning.docx
- sprint12_planning.docx
- sprint13_planning.docx

Each document should have professional formatting with:
- Bold sprint goal at the top
- Team capacity as a table
- Sprint backlog as a table
- All other sections with clear headings

Tone: Direct startup PM voice. Every section adds information
the team actually needs. No filler language.

Sprint 13 planning document should feel shorter and more urgent
than the others — it is a 7-day sprint with hard June 30 deadlines.

**For Sprint Retrospective documents (Excel):**
Generate 4 Excel files:
- sprint10_retro.xlsx
- sprint11_retro.xlsx
- sprint12_retro.xlsx
- sprint13_retro.xlsx

Each file has 3 sheets exactly as specified in the content above.

Sheet 2 Retrospective Narrative: write in full paragraphs.
What went well and what did not go well must reference specific
ticket IDs and specific data points. Not generic statements.

Sheet 3 Metrics: both columns filled — metric name and value.
Never leave the value column empty.

**Critical consistency — all numbers must be exact:**
Sprint 10 end: MAU approximately 1,100, NPS 34, retention 45%
Sprint 11 end: MAU approximately 1,456, custom foods approximately 300
Sprint 12 end: MAU approximately 2,234, A/B test 84% vs 61%
Sprint 13 end: MAU 3,512, retention 47%, NPS 41, custom foods 847
Prenatal presets shipped: June 26
Simplified onboarding 100% rollout: June 28
BUG-014 fix time: 4 hours
Pregnant women engagement: 3.1x confirmed
All 11 pregnant users updated: within 24 hours of June 26 prompt