Round 1 Document Definitions — Foundation Documents
Technical Spec, Roadmap, OKR Q1, OKR Q2

GLOBAL CONTEXT FOR ALL DOCUMENTS
Company: Nutrivana
Product: Nutrition tracking web app
Team:

Shristi Sharmistha — CEO and PM (shristi@nutrivana.in)
Arjun Mehta — CTO and Lead Engineer (arjun@nutrivana.in)
Priya Nair — Frontend Engineer (priya@nutrivana.in)
Kabir Sharma — UI/UX Designer (kabir@nutrivana.in)
Ananya Iyer — Marketing Manager (ananya@nutrivana.in)

Timeline: January 2025 to June 2025
MVP shipped: March 31, 2025
Beta launched: April 1, 2025
Public launched: May 1, 2025

DOCUMENT 1: TECHNICAL SPECIFICATION
Document name: Nutrivana Technical Architecture Specification v1.0
Format: Word (.docx)
Date: January 10, 2025
Author: Arjun Mehta
Reviewed by: Shristi Sharmistha
Status: Approved

Content Sections
Section 1 — Executive Summary
High level overview of Nutrivana technical architecture. Single-page web application
with React frontend, Node.js/Python API backend, Supabase PostgreSQL database with
pgvector extension for future search capabilities, USDA FoodData Central database
imported into Supabase. Built for initial target of Indian health-conscious users
with support for custom food creation to address Indian food database gaps.
Section 2 — System Architecture Diagram
Three-tier architecture:

Frontend: React web application hosted on Vercel
Backend: FastAPI Python REST API hosted on Render
Database: Supabase PostgreSQL with Row Level Security

Data flow:
User → React Frontend → FastAPI Backend → Supabase DB
→ USDA Food Data (Supabase)
→ Auth (Supabase Auth)
Section 3 — Technology Stack
Frontend:

React 18 with hooks
React Context API for shared state (FoodDiaryContext, AuthContext)
CSS Modules for component styling
Charting library for nutrient analysis bar graphs and trend charts
Deployed on Vercel

Backend:

FastAPI (Python)
Supabase Python client
JWT authentication with refresh token strategy
(Access token: 1 hour, Refresh token: 30 days)
Deployed on Render

Database:

Supabase PostgreSQL
Row Level Security (RLS) policies on all tables
GIN index on food name column for trigram search
B-tree index for ILIKE prefix search
pgvector extension (future use)

Section 4 — Database Schema
Tables with columns and relationships:
users (managed by Supabase Auth):

id, email, created_at

user_profiles:

user_id (FK users), age, gender, height_cm, current_weight_kg,
goal_weight_kg, activity_level, created_at, updated_at

calorie_goals:

user_id (FK), calorie_budget_kcal, eer_kcal, weight_goal_type
(loss/gain/maintain), required_deficit_surplus_kcal,
target_date, days_left, bmr_kcal, created_at, updated_at,
profile_changed_flag

macro_goals:

user_id (FK), carb_percent, fat_percent, protein_percent,
carb_kcal, fat_kcal, protein_kcal, carb_gram, fat_gram,
protein_gram, track_carb, track_fat, track_protein,
created_at, updated_at

user_micronutrient_goals:

user_id (FK), nutrient_id (FK), is_tracked, rda_value,
max_value, is_custom, custom_value, created_at, updated_at

nutrients (reference table):

id, name, category (vitamin/mineral/carbohydrate/fat/other),
default_unit, is_mandatory, dv_2000kcal

usda_foods:

id, fdc_id, food_name, food_category, created_at

usda_food_nutrients:

food_id (FK usda_foods), nutrient_id (FK nutrients),
value_per_100g

usda_food_serving_units:

food_id (FK usda_foods), unit_name, gram_weight, is_default

food_logs:

id, user_id (FK), date_string (YYYY-MM-DD local date),
logged_at_utc, meal_type (breakfast/lunch/dinner/snacks/supplement),
source_type (usda/custom_food/custom_recipe/custom_meal),
food_id (FK usda_foods nullable),
custom_food_id (FK custom_foods nullable),
custom_recipe_id (FK custom_recipes nullable),
custom_meal_id (FK custom_meals nullable),
food_name_snapshot, nutrient_snapshot (JSONB),
quantity, serving_unit, created_at, updated_at

goal_snapshots:

user_id (FK), effective_date (date_string), snapshot_data (JSONB),
created_at
Note: stores complete user goals at any given date for
date-accurate historical diary rendering

custom_foods:

id, user_id (FK), food_name, serving_value, serving_unit,
created_at, updated_at, deleted_at (soft delete)

custom_food_versions:

custom_food_id (FK), effective_date, nutrient_values (JSONB),
created_at
Note: versioning for date-aware nutrient changes per CF-007

custom_recipes:

id, user_id (FK), recipe_name, created_at, updated_at, deleted_at

custom_meals:

id, user_id (FK), meal_name, nutrient_snapshot (JSONB),
created_at, updated_at, deleted_at

rda_values (reference table):

nutrient_id (FK), age_group, gender, rda_value, max_value, unit

Section 5 — Authentication and Security
Auth strategy:

Supabase Auth for user management
JWT access tokens (1 hour expiry)
Refresh tokens (30 day expiry)
Silent refresh in background — user never sees login screen
if opened within 30 days
All tables protected by RLS policies keyed on auth.uid()

RLS policy pattern:

SELECT: WHERE user_id = auth.uid()
INSERT: WITH CHECK (user_id = auth.uid())
UPDATE: USING (user_id = auth.uid())
DELETE: USING (user_id = auth.uid())

Reference tickets: TECH-003 (auth implementation),
TECH-005 (data isolation testing)
Section 6 — Search Architecture
USDA food search uses hybrid approach:

Short queries (< 4 characters): PostgreSQL ILIKE with B-tree index
Response time: ~45ms for 300,000 rows
Long queries (≥ 4 characters): PostgreSQL trigram similarity
with GIN index (pg_trgm extension)
Response time: ~120ms for 300,000 rows
Frontend: 300ms debounce, 2-character minimum before search fires
All searches return results under 1 second per PRD requirement

Known limitation: Indian foods significantly underrepresented in USDA
database. Custom Food feature (CF-001 through CF-007) addresses this gap.
Reference tickets: NUTR-TASK-001, NUTR-TASK-002, TECH-004
Section 7 — Date and Timezone Handling
All diary dates stored as:

date_string: YYYY-MM-DD in user's local timezone (IST for India)
Used for all diary queries and date comparisons
logged_at_utc: UTC timestamp
Used for audit trail and future international expansion

Decision rationale: Prevents midnight boundary bugs where IST date
differs from UTC date. V2 migration path preserved via UTC timestamp.
Reference tickets: NUTR-022, TECH-007
Section 8 — Performance Targets and Achieved Metrics
OperationPRD RequirementAchievedUSDA search< 1 second120ms (avg)Diary date switch< 2 seconds0.8 secondsAnalysis load< 2 seconds0.8 secondsNutrient recalculation< 1 second< 200msFood add/delete< 1 second< 200ms
Optimisation: Analysis with 20 nutrients batched into single DB query
instead of 20 sequential queries (identified in TECH-004).
Section 9 — Known Technical Limitations (V1)

Offline support: No offline capability. Network status indicator
shows warning when offline. Data loss if user logs food offline.
Planned for V2 with service worker implementation.
International timezone: Date handling optimised for IST.
International users in other timezones may see midnight boundary
issues. UTC timestamp stored for future migration.
Age group auto-transition: EER formula does not auto-switch on
user's birthday. User must manually update age in profile.
Planned for V2.
Custom recipe creation: Recipe creation UI not implemented in V1.
Users can create custom foods but not multi-ingredient recipes.
Planned for V2.

Section 10 — Deployment Architecture
Frontend: Vercel (automatic deployment on GitHub main branch push)
Backend: Render (manual deployment, Docker container)
Database: Supabase hosted PostgreSQL (Singapore region — closest
to India for lowest latency)
Domain: nutrivana.app

Document Cross-References
References: NUTR-TASK-001, NUTR-TASK-002, NUTR-TASK-003, TECH-001,
TECH-003, TECH-004, TECH-005, TECH-006, TECH-007, GOAL-002, CF-007

GPT-4o Generation Brief
Generate a professional technical architecture specification document
for Nutrivana. Write in formal technical documentation style. Include
all sections above with full detail. The document should read like
a real architecture spec written by a CTO for a seed-stage startup —
detailed but not over-engineered. All table schemas must be accurate
and consistent with the data model decisions made across Sprint 1
(TECH-001), Sprint 5 (NUTR-022 timezone), Sprint 6 (CF-007 versioning)
and Sprint 9 (CF-BUG-001 and CF-BUG-002 snapshot additions).
Include the known limitations section honestly — a good technical spec
acknowledges what was descoped rather than hiding it.
Format: Word document with proper headings, a table of contents,
and tables for database schema and performance metrics.