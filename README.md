

## What did I build?

I built two separate Django backends that talk to each other:

**1. Auth Service** (port 8000) - It stores all user passwords (hashed), handles login, and generates JWT tokens. No other service is allowed to store passwords.

**2. Independent Site** (port 8001) - This is a regular website that completely depends on the auth service for login. It never stores passwords or generates tokens on its own. It just asks the auth service for verification

**3. Frontend** (port 3000) - A simple HTML page with register, login and dashboard.

I also set up two separate PostgreSQL databases, one for each service.


## How does it work?

**Registration:**
- User fills the form on the frontend
- Independent site receives the data
- Independent site forwards it to auth service (it never touches the password itself)
- Auth service hashes the password and saves the user
- Independent site saves a local profile without the password

**Login:**
- User logs in via auth service
- Auth service checks the password and returns a JWT token
- Frontend saves this token

**Accessing protected pages:**
- Frontend sends the JWT token with every request
- Independent site asks auth service to verify the token
- If valid, user gets access

## How to run it

### Using Docker (easiest way)
Make sure Docker Desktop is running, then just run:
docker-compose up --build

- Auth Service: http://localhost:8000
- Independent Site: http://localhost:8001
- Frontend: http://localhost:3000

### Without Docker

**Start auth service:**
cd auth-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

**Start independent site (new terminal):**
cd independent-site
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001

**Start frontend (new terminal):**
cd frontend
python -m http.server 3000

## API Endpoints

### Auth Service (port 8000)
| Method | URL | What it does |
|--------|-----|--------------|
| POST | /api/auth/register/ | Register a new user |
| POST | /api/auth/login/ | Login and get JWT token |
| GET | /api/auth/verify/ | Check if a token is valid |

### Independent Site (port 8001)
| Method | URL | What it does |
|--------|-----|--------------|
| POST | /api/register/ | Register via independent site |
| GET | /api/dashboard/ | View dashboard (needs token) |

## Summary
- Passwords are ONLY stored in the auth service database
- Independent site NEVER stores or generates passwords or tokens
- Every protected request must include Authorization: Bearer token
- Both services have completely separate PostgreSQL databases

## Tech Stack
- Backend: Django + Django REST Framework
- Auth: JWT tokens via djangorestframework-simplejwt
- Database: PostgreSQL with one database per service
- Containerization: Docker + Docker Compose
