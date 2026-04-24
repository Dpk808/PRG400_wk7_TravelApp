# Implementation Plan

## 1. Project Setup
- Use Flask for backend, SQLite for storage, and Jinja templates for server-rendered pages.
- Define folder structure (app, templates, static, instance, migrations).
- Initialize dependencies and basic README.
- Configure environment variables for secrets.

## 2. Data Model
- Define entities:
  - User (id, name, email, password_hash, role).
  - Destination (id, title, duration_days, price_nrs, description).
  - Booking (id, user_id, destination_id, status, created_at).
- Create database migrations/seed data for sample trips.

## 3. Auth (Signup/Login)
- Implement simple signup and login with Flask sessions.
- Add password hashing.
- Add role-based access for admin.

## 4. User Features
- Destinations list page with pricing (NRs) and duration.
- Destination detail view.
- Booking flow (select trip, confirm booking).
- User booking history page.

## 5. Admin Features
- Admin login.
- Admin dashboard to view all users and bookings.
- Manage destinations (add/update/remove).

## 6. UI/UX
- Build basic layout and navigation.
- Forms with validation and error states.
- Consistent styling and responsive design.

## 7. Testing and QA
- Add basic unit tests for auth and booking logic.
- Manual test checklist for flows.

## 8. Deployment
- Provide local run instructions.
- Optional hosting setup (frontend + backend).
