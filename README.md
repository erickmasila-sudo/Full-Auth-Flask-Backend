# Notes API — Session-Auth Flask Backend

A secure Flask REST API for a personal notes-tracking productivity app.
Users register and log in with a bcrypt-hashed password and a server-side
session cookie. Once logged in, they can create, read, update, and delete
their own notes — every note is scoped to its owner, no user can view or
modify another user's data, and the notes index endpoint is paginated.

Built to pair with the JWT/Sessions frontend client repo — use the
**sessions** client, since this API uses cookie-based sessions rather than
JWTs.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Security Notes](#security-notes)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Tech Stack
- Flask 2.2.2 + Flask-RESTful (routing)
- Flask-SQLAlchemy 3.0.3 + Flask-Migrate 4.0.0 (models + migrations)
- Flask-Bcrypt 1.0.1 (password hashing)
- Marshmallow 3.20.1 (request validation)
- Faker 15.3.2 (database seeding)
- SQLite (default local database)

## Project Structure
```
server/
├── app.py            # Routes / Flask-RESTful resources (auth + notes)
├── config.py          # Flask app, db, bcrypt, migrate, api instances
├── models.py          # User and Note SQLAlchemy models
├── schemas.py          # Marshmallow request-validation schemas
├── seed.py            # Seeds demo users + notes
├── Pipfile
├── migrations/         # Flask-Migrate / Alembic migration history
└── README.md
```

## Installation

1. Clone the repository and enter the server folder:
```bash
   git clone https://github.com/yourusername/notes-api.git
   cd notes-api/server
```

2. Install dependencies with Pipenv:
```bash
   pipenv install
   pipenv shell
```
   (If you'd rather use plain `pip` in a virtualenv, install the packages
   listed in `Pipfile` instead.)

3. Set the Flask app entry point:
```bash
   export FLASK_APP=app.py       # macOS/Linux
   set FLASK_APP=app.py          # Windows (cmd)
```

4. Create and apply the database migrations:
```bash
   flask db init      # only needed if migrations/ doesn't already exist
   flask db upgrade
```

5. Seed the database with sample data:
```bash
   python seed.py
```
   This creates a demo account (`username: demo`, `password: password123`)
   plus four more random users, each with several notes.

## Usage

Start the server:
```bash
flask run --port 5555
```
The API will be available at `http://127.0.0.1:5555`.

### Connecting the frontend

By default the API allows cross-origin requests (with cookies) from
`http://localhost:4000`. If your frontend client runs on a different port,
set `FRONTEND_ORIGIN` before starting the server:

```bash
export FRONTEND_ORIGIN=http://localhost:3000
flask run --port 5555
```

### Example request

```bash
curl -c cookies.txt -X POST http://127.0.0.1:5555/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "password123"}'

curl -b cookies.txt "http://127.0.0.1:5555/notes?page=1&per_page=5"
```

### Environment Variables (optional)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-me` | Signs the session cookie — set a real secret in production. |
| `DATABASE_URI` | `sqlite:///app.db` | SQLAlchemy database URL. |
| `FRONTEND_ORIGIN` | `http://localhost:4000` | Allowed CORS origin for the frontend client. |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Set to `None` (with `SESSION_COOKIE_SECURE=True` and HTTPS) if frontend/backend are on different registrable domains. |

## API Endpoints

### Auth

| Method | Route | Description | Auth required |
|---|---|---|---|
| `POST` | `/signup` | Create an account. Body: `{ "username", "password" }` (password min. 6 chars). Logs the user in and returns the user. | No |
| `POST` | `/login` | Log in. Body: `{ "username", "password" }`. Starts a session and returns the user. | No |
| `DELETE` | `/logout` | Clears the session. | Yes |
| `GET` | `/check_session` | Returns the currently logged-in user, or 401 if none. | No |

### Notes (all require an active session — 401 otherwise)

| Method | Route | Description |
|---|---|---|
| `GET` | `/notes?page=1&per_page=10` | Paginated list of **the current user's** notes, newest first. Returns `notes`, `page`, `per_page`, `total`, `total_pages`, `has_next`, `has_prev`. |
| `POST` | `/notes` | Create a note owned by the current user. Body: `{ "title", "content" }`. |
| `GET` | `/notes/<id>` | Fetch a single note. 404 if it doesn't exist or belongs to another user. |
| `PATCH` | `/notes/<id>` | Update `title` and/or `content` of one of the current user's notes. 404 if not found/owned. |
| `DELETE` | `/notes/<id>` | Delete one of the current user's notes. 404 if not found/owned. |

### Status codes used
- `200` success (read/update)
- `201` resource created
- `204` success, no content (logout, delete)
- `400` malformed query params
- `401` not authenticated / bad credentials
- `404` resource not found or not owned by the current user
- `422` validation error (e.g. missing field, duplicate username, password too short)

## Security Notes
- Passwords are never stored in plain text — `User.password_hash` is a
  write-only property that hashes on assignment via Flask-Bcrypt, and the
  raw hash column is never included in `to_dict()`.
- Every notes route uses the `user_id` stored in the server-side session
  (never a client-supplied value) to scope queries, so a user can't view or
  modify another user's data by guessing IDs. Requests for another user's
  note return `404` rather than `403`, so callers can't use the API to probe
  which note IDs exist.

## Testing
Manual testing was done with `curl` and the sessions frontend client,
covering: signup/login/logout, `check_session`, full note CRUD, pagination,
cross-user access attempts (expect `404`), duplicate signup (`422`), and
invalid login (`401`). A `pytest` suite can be added under a `tests/`
directory if desired (not required for this lab).

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes.
4. Push your branch: `git push origin feature-name`.
5. Open a pull request.

## License
This project was built as a course lab and is provided for educational use.
