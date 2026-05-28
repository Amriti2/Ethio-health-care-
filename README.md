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
