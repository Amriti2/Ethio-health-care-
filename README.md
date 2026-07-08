# Ethio Health Care Recruitment Site

## Local Run

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open `http://localhost:5002`

## Deployment on Render

1. Initialize git and commit the project:
   ```bash
   git init
   git add .
   git commit -m "Prepare Render deployment"
   ```
2. Push to GitHub and connect the repo in Render.
3. In Render service settings, set environment variables for SMTP if you want email sending:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `ADMIN_PASSWORD`
4. If SMTP is not configured, email actions will still log to the server console.

## Deployment on Railway

This project is now database-first and is ready to use Railway with Postgres.

1. Create a new Railway project from this GitHub repo.
2. Add a Railway Postgres service.
3. In the web service variables, set:
   - `DATABASE_URL` to the Railway Postgres connection string
   - `DISABLE_FIREBASE=true`
   - `BASE_URL` to your Railway public URL
   - `SECRET_KEY` to a strong random value
   - `CEO_PASSWORD` to your real admin password
4. Railway will use the `Procfile` start command automatically.
5. Submit one test application, then redeploy once to confirm the applicant still appears in `/dashboard`.

Notes:
- If `DATABASE_URL` is not set, the app falls back to a local SQLite database file.
- Jobs and applications are stored in the primary database first, with JSON files kept only as a backup/migration layer.
