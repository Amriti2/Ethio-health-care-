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
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@ethiohealthcare.com")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5002")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)


# --------------------------
# HELPERS
# --------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_applications():
    if not os.path.exists(APPLICATIONS_FILE):
        return []

    try:
        with open(APPLICATIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_applications(applications):
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(applications, file, indent=2)


def find_application(app_id):
    applications = load_applications()

    for application in applications:
        if application.get("id") == app_id:
            return application

    return None


def update_application(updated_application):
    applications = load_applications()

    for index, item in enumerate(applications):
        if item.get("id") == updated_application.get("id"):
            applications[index] = updated_application
            save_applications(applications)
            return


def delete_application(app_id):
    applications = load_applications()

    applications = [
        app for app in applications
        if app.get("id") != app_id
    ]

    save_applications(applications)


def send_email(to_address, subject, body):

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

            return True, "Email sent successfully."

        except Exception as exc:
            return False, f"Email error: {str(exc)}"

    else:
        print("\n===== EMAIL LOG =====")
        print("TO:", to_address)
        print("SUBJECT:", subject)
        print(body)
        print("=====================\n")

        return True, "Email logged to console."


# --------------------------
# HOME PAGE
# --------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------
# APPLY PAGE
# --------------------------

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

        qualifications = request.form.get("qualifications", "").strip()

        experience_years = request.form.get("experience_years", "").strip()

        shift_preference = request.form.get("shift_preference", "").strip()

        message = request.form.get("message", "").strip()

        about = request.form.get("about", "").strip()

        if not name or not email or not phone:
            error = "Please complete all required fields."

        elif not role or not experience:
            error = "Please select role and experience."

        elif not qualifications or not experience_years:
            error = "Please complete qualifications section."

        elif not shift_preference:
            error = "Please choose shift preference."

        else:

            cv_file = request.files.get("cv")

            if not cv_file or not cv_file.filename:
                error = "Please upload your CV."

            elif not allowed_file(cv_file.filename):
                error = "Only PDF files are allowed."

            else:

                safe_name = secure_filename(cv_file.filename)

                unique_filename = f"{int(time.time())}_{safe_name}"

                save_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    unique_filename
                )

                try:
                    cv_file.save(save_path)

                except Exception as exc:
                    print(exc)
                    error = "Could not save CV."

                if not error:

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
                        "cv": unique_filename,
                        "submitted_at": int(time.time()),
                        "status": "pending",
                        "verified": False,
                        "verification_token": "",
                        "account_email": "",
                        "messages": []
                    }

                    applications = load_applications()

                    applications.append(application)

                    save_applications(applications)

                    success = f"Thank you {name}! Your application has been submitted."

    return render_template(
        "apply.html",
        role=role,
        success=success,
        error=error
    )


@app.route("/apply/<role_key>")
def apply_role(role_key):

    role = ROLE_MAP.get(role_key.lower())

    if role:
        return redirect(
            url_for(
                "apply_form",
                role=role_key.lower()
            )
        )

    return redirect(url_for("apply_form"))


# --------------------------
# LOGIN
# --------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        password = request.form.get("password")

        if password == CEO_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))

        error = "Incorrect password."

    return render_template(
        "login.html",
        error=error
    )


@app.route("/logout")
def logout():

    session.pop("admin", None)

    flash("Logged out successfully.")

    return redirect(url_for("login"))


# --------------------------
# DASHBOARD
# --------------------------

@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect(url_for("login"))

    applications = load_applications()

    search_query = request.args.get("search", "").strip()

    if search_query:

        query = search_query.lower()

        applications = [
            app for app in applications
            if query in app.get("name", "").lower()
            or query in app.get("email", "").lower()
            or query in app.get("phone", "").lower()
            or query in app.get("role", "").lower()
            or query in app.get("status", "").lower()
        ]

    smtp_configured = bool(
        SMTP_HOST and SMTP_USER and SMTP_PASS
    )

    return render_template(
        "dashboard.html",
        applications=applications,
        search_query=search_query,
        smtp_configured=smtp_configured
    )


# --------------------------
# DOWNLOAD CV
# --------------------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    if not session.get("admin"):
        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# --------------------------
# DASHBOARD ACTIONS
# --------------------------

@app.route("/dashboard/app/<app_id>", methods=["POST"])
def dashboard_action(app_id):

    if not session.get("admin"):
        return redirect(url_for("login"))

    application = find_application(app_id)

    if not application:
        flash("Application not found.")
        return redirect(url_for("dashboard"))

    action = request.form.get("action")

    # ASSIGN EMAIL
    if action == "assign_email":

        new_email = request.form.get("account_email", "").strip()

        if new_email:
            application["account_email"] = new_email
            update_application(application)
            flash("Employee email saved successfully.")
        else:
            flash("Please enter a valid email address.")

    # SEND MESSAGE
    elif action == "send_message":

        ceo_message = request.form.get("ceo_message", "").strip()

        if not ceo_message:
            flash("Please enter a message before sending.")
        else:
            application.setdefault("messages", []).append({
                "from": "CEO",
                "message": ceo_message,
                "sent_at": int(time.time())
            })
            update_application(application)

            subject = "Message from Ethio Health Care"
            body = f"""
Hello {application['name']},

A message from the Ethio Health Care team:

{ceo_message}

Regards,
Ethio Health Care
"""
            recipient = application.get("account_email") or application.get("email")
            send_email(recipient, subject, body)
            flash("Message sent to applicant.")

    # VERIFICATION EMAIL
    elif action == "send_verification":

        if not application.get("verification_token"):
            application["verification_token"] = str(uuid.uuid4())

        application["status"] = "verification_sent"
        update_application(application)

        verification_link = f"{BASE_URL}/verify/{application['verification_token']}"
        subject = "Verify Your Ethio Health Care Application"
        body = f"""
Hello {application['name']},

Please verify your application by clicking the link below:
{verification_link}

Thank you,
Ethio Health Care
"""
        recipient = application.get("account_email") or application.get("email")
        send_email(recipient, subject, body)
        flash("Verification email sent.")

    # ACCEPT
    elif action == "accept":

        application["status"] = "approved"
        update_application(application)

        subject = "Congratulations! You Have Been Approved"
        body = f"""
Hello {application['name']},

Congratulations!

We are pleased to inform you that your application for the role of
{application['role']} has been approved.

Further onboarding details will be sent soon.

Regards,
Ethio Health Care
"""
        recipient = application.get("account_email") or application.get("email")
        send_email(recipient, subject, body)
        flash("Applicant approved successfully.")

    # REJECT
    elif action == "reject":

        application["status"] = "rejected"
        update_application(application)

        subject = "Ethio Health Care Application"
        body = f"""
Hello {application['name']},

Thank you for applying to Ethio Health Care.

After careful consideration, we will not be moving forward
with your application at this time.

We appreciate your interest and encourage you to apply again
in the future.

Regards,
Ethio Health Care
"""
        recipient = application.get("account_email") or application.get("email")
        send_email(recipient, subject, body)
        flash("Applicant rejected.")

    # DELETE
    elif action == "delete":

        cv_file = application.get("cv")
        if cv_file:
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], cv_file))
            except:
                pass

        delete_application(app_id)
        flash("Applicant deleted.")

    return redirect(url_for("dashboard"))


# --------------------------
# VERIFY EMAIL
# --------------------------

@app.route("/verify/<token>")
def verify_email(token):

    applications = load_applications()

    for application in applications:

        if application.get("verification_token") == token:

            application["verified"] = True

            application["status"] = "verified"

            update_application(application)

            return render_template(
                "verify.html",
                success=True,
                application=application
            )

    return render_template(
        "verify.html",
        success=False
    )


# --------------------------
# START APP
# --------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5002))

    debug_mode = (
        os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )