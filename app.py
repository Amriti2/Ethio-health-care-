from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import time
import json
import uuid
import smtplib
from email.message import EmailMessage
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
CEO_PASSWORD = os.environ.get("CEO_PASSWORD", "password1212")
ROLE_MAP = {
    "nurse": "Nurse",
    "doctor": "Doctor",
    "caregiver": "Care Giver",
    "midwife": "Midwife",
    "other": "Other"
}

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")
APPLICATIONS_FILE = os.path.join(DATA_FOLDER, "applications.json")
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@ethiohealthcare.com")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5002")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_applications():
    if not os.path.exists(APPLICATIONS_FILE):
        return []
    try:
        with open(APPLICATIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []

def save_applications(applications):
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(applications, file, indent=2)

def find_application(app_id):
    for application in load_applications():
        if application.get("id") == app_id:
            return application
    return None

def update_application(updated):
    applications = load_applications()
    for index, item in enumerate(applications):
        if item.get("id") == updated.get("id"):
            applications[index] = updated
            save_applications(applications)
            return

def send_email(to_address, subject, body):
    # If SMTP is configured, use real email
    if SMTP_HOST and SMTP_USER and SMTP_PASS:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = EMAIL_FROM
            message["To"] = to_address
            message.set_content(body)

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(SMTP_USER, SMTP_PASS)
                smtp.send_message(message)
            return True, f"✓ Email sent to {to_address}"
        except Exception as exc:
            return False, f"Email error: {str(exc)}"
    else:
        # Fallback: log to console when SMTP not configured
        print(f"\n[EMAIL LOG] TO: {to_address}")
        print(f"[EMAIL LOG] SUBJECT: {subject}")
        print(f"[EMAIL LOG] BODY:\n{body}\n")
        return True, f"✓ Email prepared for {to_address} (check console/logs)"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/apply", methods=["GET", "POST"])
def apply_form():
    role_key = request.args.get("role", "").lower()
    role = ROLE_MAP.get(role_key)
    success = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        role = request.form.get("role", "").strip()
        experience = request.form.get("experience", "").strip()
        message = request.form.get("message", "").strip()
        about = request.form.get("about", "").strip()

        if not name or not email or not phone or not role or not experience:
            error = "Please complete your full name, email, phone, role, and experience."
        else:
            qualifications = request.form.get("qualifications", "").strip()
            experience_years = request.form.get("experience_years", "").strip()
            shift_preference = request.form.get("shift_preference", "").strip()
            
            if not qualifications or not experience_years or not shift_preference:
                error = "Please complete all qualification and preference fields."
            else:
                cv_filename = None
                cv_file = request.files.get("cv")
                if not cv_file or not cv_file.filename:
                    error = "Please upload your CV in PDF format."
                elif not allowed_file(cv_file.filename):
                    error = "PDF only. Please upload a CV file with a .pdf extension."
                else:
                    safe_name = secure_filename(cv_file.filename)
                    unique_name = f"{int(time.time())}_{safe_name}"
                    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                    try:
                        cv_file.save(save_path)
                        cv_filename = unique_name
                    except Exception as e:
                        print("Failed to save CV:", e)
                        error = "Unable to save your CV. Please try again."

                if not error:
                    applications = load_applications()
                    application = {
                        "id": str(uuid.uuid4()),
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "role": role,
                        "experience": experience,
                        "qualifications": qualifications,
                        "experience_years": experience_years,
                        "shift_preference": shift_preference,
                        "message": message,
                        "about": about,
                        "cv": cv_filename,
                        "submitted_at": int(time.time()),
                        "status": "pending",
                        "account_email": "",
                        "verification_token": "",
                        "verified": False,
                        "messages": []
                    }
                    applications.append(application)
                    save_applications(applications)
                    success = f"Thanks, {name}! Your application for {role} has been received."

    return render_template("apply.html", role=role, success=success, error=error)

@app.route("/apply/<role_key>")
def apply_role(role_key):
    role = ROLE_MAP.get(role_key.lower())
    if role:
        return redirect(url_for("apply_form", role=role_key.lower()))
    return redirect(url_for("apply_form"))

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))
    search_query = request.args.get("search", "").strip()
    applications = load_applications()
    if search_query:
        query = search_query.lower()
        applications = [
            app for app in applications
            if query in app.get("name", "").lower()
            or query in app.get("email", "").lower()
            or query in app.get("phone", "").lower()
            or query in app.get("role", "").lower()
            or query in app.get("status", "").lower()
            or query in app.get("experience_years", "").lower()
            or query in app.get("shift_preference", "").lower()
        ]
    smtp_configured = bool(SMTP_HOST and SMTP_USER and SMTP_PASS)
    return render_template("dashboard.html", applications=applications, search_query=search_query, smtp_configured=smtp_configured)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if not session.get('admin'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/dashboard/app/<app_id>", methods=["POST"])
def dashboard_action(app_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    application = find_application(app_id)
    if not application:
        flash("Application not found.")
        return redirect(url_for("dashboard"))

    action = request.form.get("action")
    if action == "assign_email":
        account_email = request.form.get("account_email", "").strip()
        if account_email:
            application["account_email"] = account_email
            application["status"] = "approved"
            application["verification_token"] = str(uuid.uuid4())
            application["verified"] = False
            update_application(application)
            flash("Applicant account email saved. You can now send verification.")
        else:
            flash("Please enter an email address to assign.")
    elif action == "send_verification":
        if not application.get("account_email"):
            flash("❌ Assign an account email before sending verification.")
        else:
            token = application.get("verification_token") or str(uuid.uuid4())
            application["verification_token"] = token
            application["status"] = "verification_sent"
            update_application(application)
            verify_url = f"{BASE_URL}/verify/{token}"
            subject = "🎉 Verify Your Ethio Health Care Account"
            body = f"Hello {application['name']},\n\nYour application has been approved! Please verify your email by visiting:\n\n{verify_url}\n\nOnce verified, you'll gain access to your account.\n\nBest regards,\nEthio Health Care Team"
            sent, info = send_email(application["account_email"], subject, body)
            flash(info)
    elif action == "send_message":
        message_text = request.form.get("ceo_message", "").strip()
        if message_text:
            application["messages"].append({
                "timestamp": int(time.time()),
                "from": "CEO",
                "message": message_text
            })
            update_application(application)
            recipient = application.get("account_email") or application.get("email")
            subject = "💬 Message from Ethio Health Care CEO"
            body = f"Hello {application['name']},\n\n{message_text}\n\nRegards,\nEthio Health Care Team"
            sent, info = send_email(recipient, subject, body)
            flash(info)
        else:
            flash("❌ Enter a message before sending.")
    elif action == "accept":
        application["status"] = "accepted"
        recipient = application.get("account_email") or application.get("email")
        subject = "🎉 Congratulations! You're Accepted at Ethio Health Care"
        body = f"Hello {application['name']},\n\n🎉 Great news! We are thrilled to inform you that your application has been ACCEPTED!\n\nYour qualifications and experience impressed our team. We would like to welcome you to Ethio Health Care as a {application['role']}.\n\nYou will receive further details about onboarding and next steps via email shortly.\n\nCongratulations on this exciting opportunity!\n\nBest regards,\nEthio Health Care Team"
        update_application(application)
        sent, info = send_email(recipient, subject, body)
        flash(f"✅ Application accepted. {info}")
    elif action == "reject":
        application["status"] = "rejected"
        recipient = application.get("account_email") or application.get("email")
        subject = "Re: Your Ethio Health Care Application"
        body = f"Hello {application['name']},\n\nThank you for your interest in Ethio Health Care and for taking the time to apply.\n\nAfter careful review of your application, we regret to inform you that we will not be moving forward at this time. This decision does not reflect your qualifications, but rather our current staffing needs.\n\nWe encourage you to apply again in the future. We appreciate your interest in joining our team.\n\nBest regards,\nEthio Health Care Team"
        update_application(application)
        sent, info = send_email(recipient, subject, body)
        flash(f"❌ Application rejected. {info}")
    elif action == "delete":
        cv_file = application.get("cv")
        if cv_file:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], cv_file))
            except Exception:
                pass
        delete_application(app_id)
        flash("🗑️ Applicant deleted successfully.")
        return redirect(url_for("dashboard"))
    return redirect(url_for("dashboard"))

@app.route("/verify/<token>")
def verify_email(token):
    applications = load_applications()
    for application in applications:
        if application.get("verification_token") == token:
            application["verified"] = True
            application["status"] = "verified"
            update_application(application)
            return render_template("verify.html", success=True, application=application)
    return render_template("verify.html", success=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == CEO_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        error = "Password is incorrect. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
