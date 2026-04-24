# Travel Booking Platform (Flask)

Travel Booking Platform is a Flask web app for browsing destinations, booking trips, and managing user balances in Nepali Rupees (NRs). It includes a simple login system, booking flow, and an admin dashboard with user and booking management tools.

![Travel App Dashboard](image_url)

## Features
- User signup and login with session-based auth
- Destination listings with pricing in NRs
- Booking flow with balance deduction
- User wallet balances and booking history
- Admin dashboard for viewing users, trips, and bookings
- Admin accounts panel to add funds to users

## Tech Stack
- Flask (Python)
- SQLite
- Jinja templates
- Docker and Docker Compose support

## Project Structure
- app.py: Flask application and routes
- schema.sql: Database schema
- init_db.py: Database initialization and seed data
- templates/: HTML templates
- static/: CSS

## Local Setup
1. Create a virtual environment and install dependencies.
2. Initialize the database.
3. Start the server.

```bash
pip install -r requirements.txt
python init_db.py
python app.py
```

App runs on http://127.0.0.1:5002

## Docker Setup
```bash
docker compose up --build
```

App runs on http://127.0.0.1:5002



## Notes
- Prices are shown in NRs.
- Each new user starts with a balance of NRs 200000, deducted on booking.
- Admin accounts start with a balance of NRs 0.
- The database is stored at instance/travel.db.
- Re-run python init_db.py after schema or seed updates.
