# Job Application Tracker (API)

A full-stack job application tracker backend — built to help job seekers log applications, track their status over time, and see their history in one place, rather than losing track across spreadsheets and email threads.

**Live API docs:** `(https://job-application-tracker-production-1cb4.up.railway.app/)/docs`

## Tech Stack

- **FastAPI** — Python web framework for the REST API
- **PostgreSQL** (hosted on [Neon](https://neon.tech)) — relational database
- **SQLAlchemy** — ORM for models, relationships, and queries
- **Pydantic** — request/response validation and schema contracts
- **JWT** (via `python-jose`) — stateless authentication
- **Passlib / bcrypt** — password hashing
- **Deployed on [Railway](https://railway.app)**

## Features

- User signup and login with hashed passwords and JWT-based authentication
- Protected routes — every request to a user's own data requires a valid token
- Log a new job application, with automatic company creation if the company doesn't already exist
- List all applications belonging to the logged-in user (strictly scoped — no user can see another user's data)
- Update an application's status, with every change automatically logged to a status history table

## API Endpoints

| Method | Path | Description | Auth required |
|---|---|---|---|
| POST | `/signup` | Create a new user account | No |
| POST | `/login` | Log in and receive a JWT access token | No |
| GET | `/me` | Get the currently authenticated user | Yes |
| POST | `/applications` | Log a new job application (creates the company if it doesn't exist) | Yes |
| GET | `/applications` | List all applications for the current user | Yes |
| PATCH | `/applications/{id}/status` | Update an application's status and log the change | Yes |

Full interactive documentation (Swagger UI) is available at `/docs` on the live deployment, where each endpoint can be tested directly in the browser.

## Architecture Notes

**Authentication flow:** On signup, passwords are hashed with bcrypt before being stored — plaintext passwords are never saved. On login, the submitted password is verified against the stored hash, and if it matches, a signed JWT is issued. Protected routes use a shared `get_current_user` dependency that decodes and verifies the token on every request, then looks up the real user from the database — no session state is stored server-side.

**Data model:** Four related tables — `User`, `Company`, `Application`, and `StatusHistory` — connected via foreign keys. Each `Application` belongs to exactly one `User` and one `Company`; each `StatusHistory` row is a timestamped record of a status change for a specific application, so the full history of an application (not just its current state) is preserved.

**Schema separation:** Database models (`models.py`) and API schemas (`schemas.py`) are kept deliberately separate. `Create` schemas define exactly what a client is allowed to send (e.g., a plain company name string, never a database ID), while `Out` schemas define exactly what's returned (e.g., never exposing a password hash). This keeps the API's public contract independent from the internal database structure.

## Running Locally

```bash
# Clone the repo
git clone <repo-url>
cd job-application-tracker

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Create a .env file with:
# DATABASE_URL=<your postgres connection string>
# SECRET_KEY=<a random secret, e.g. via `python -c "import secrets; print(secrets.token_hex(32))"`>

# Create the database tables
python create_tables.py

# Run the server
uvicorn main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` to interact with the API.

## Known Limitations & Next Steps

- **Case sensitivity in company names:** Company name matching is now normalized with `.title()` on write and lookup, but this was fixed partway through development — a small number of earlier test records may still contain duplicate companies with inconsistent casing. In a production system, this would require a one-time data migration to merge and clean up existing rows.
- **No frontend yet:** The API is currently only usable via the interactive `/docs` interface. A React frontend is planned as the next phase of this project.
- **No route to view status history directly:** `StatusHistory` rows are created automatically on every status update, but there's currently no `GET` endpoint to retrieve that history — planned for a future update.
