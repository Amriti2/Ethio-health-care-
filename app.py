from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
import os
import time
import json
import uuid
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

CEO_PASSWORD = os.environ.get("CEO_PASSWORD", "password1212")

ROLE_MAP = {
    "nurse": "Nurse",
    "doctor": "Doctor",
    "caregiver": "Care Giver",
    "midwife": "Midwife",
    "other": "Other"
}

DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
DATA_FOLDER = os.path.join(DATA_DIR, "data")
APPLICATIONS_FILE = os.path.join(DATA_FOLDER, "applications.json")
JOBS_FILE = os.path.join(DATA_FOLDER, "jobs.json")

ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
LOGO_FOLDER = os.path.join(os.path.dirname(__file__), "static", "logos")
os.makedirs(LOGO_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.environ.get("SMTP_USE_SSL", "false").lower() == "true"

EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER or "no-reply@ethiohealthcare.com")
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


def format_datetime(value):
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(int(value)))
    except Exception:
        return "Unknown"


app.jinja_env.filters["datetimeformat"] = format_datetime


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


# --------------------------
# JOBS MANAGEMENT
# --------------------------

def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return []
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_jobs(jobs):
    with open(JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(jobs, file, indent=2)


def find_job(job_id):
    jobs = load_jobs()
    for job in jobs:
        if job.get("id") == job_id:
            return job
    return None


def update_job(updated_job):
    jobs = load_jobs()
    for index, item in enumerate(jobs):
        if item.get("id") == updated_job.get("id"):
            jobs[index] = updated_job
            save_jobs(jobs)
            return
    

def delete_job(job_id):
    jobs = load_jobs()
    jobs = [job for job in jobs if job.get("id") != job_id]
    save_jobs(jobs)


def send_email(to_address, subject, body):
    """Send email via SMTP or log to console"""
    if SMTP_HOST and SMTP_USER and SMTP_PASS:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = EMAIL_FROM
            message["To"] = to_address
            message.set_content(body)

            if SMTP_USE_SSL:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                    smtp.login(SMTP_USER, SMTP_PASS)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
                    if SMTP_USE_TLS:
                        smtp.starttls()
                    smtp.login(SMTP_USER, SMTP_PASS)
                    smtp.send_message(message)

            print(f"✓ EMAIL SENT: {subject} → {to_address}")
            return True, "Email sent successfully."
        except Exception as exc:
            print(f"✗ EMAIL FAILED: {str(exc)}")
            return False, f"Email error: {str(exc)}"
    else:
        print("\n" + "="*70)
        print("📧 EMAIL CONSOLE FALLBACK (SMTP not configured on this server)")
        print("="*70)
        print(f"TO: {to_address}")
        print(f"SUBJECT: {subject}")
        print("-"*70)
        print(body)
        print("="*70 + "\n")
        return False, "SMTP not configured on server."


# --------------------------
# ANALYTICS & DASHBOARD HELPERS
# --------------------------

def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    applications = load_applications()
    
    stats = {
        "total": len(applications),
        "pending": len([a for a in applications if a.get("status") == "pending"]),
        "approved": len([a for a in applications if a.get("status") == "approved"]),
        "verified": len([a for a in applications if a.get("status") == "verified"]),
        "rejected": len([a for a in applications if a.get("status") == "rejected"]),
        "verification_sent": len([a for a in applications if a.get("status") == "verification_sent"]),
    }
    
    # Calculate conversion rates
    if stats["total"] > 0:
        stats["approval_rate"] = round((stats["approved"] / stats["total"]) * 100, 1)
        stats["verification_rate"] = round((stats["verified"] / stats["total"]) * 100, 1)
    else:
        stats["approval_rate"] = 0
        stats["verification_rate"] = 0
    
    # Role breakdown
    role_count = Counter([a.get("role", "Unknown") for a in applications])
    stats["roles"] = dict(role_count)
    
    # Experience distribution
    exp_levels = {"0-2": 0, "2-5": 0, "5-10": 0, "10+": 0}
    for app in applications:
        try:
            years = int(app.get("experience_years", 0))
            if years <= 2:
                exp_levels["0-2"] += 1
            elif years <= 5:
                exp_levels["2-5"] += 1
            elif years <= 10:
                exp_levels["5-10"] += 1
            else:
                exp_levels["10+"] += 1
        except:
            pass
    stats["experience_levels"] = exp_levels
    
    # Recent applications (last 7 days)
    now = int(time.time())
    week_ago = now - (7 * 24 * 60 * 60)
    stats["recent_applications"] = len([
        a for a in applications 
        if a.get("submitted_at", 0) >= week_ago
    ])
    
    return stats


def get_chart_data():
    """Get data for dashboard charts"""
    applications = load_applications()
    
    # Status distribution for pie chart
    status_data = {}
    for status in ["pending", "approved", "verified", "rejected", "verification_sent"]:
        count = len([a for a in applications if a.get("status") == status])
        if count > 0:
            status_data[status.replace("_", " ").title()] = count
    
    # Application timeline (last 30 days)
    now = int(time.time())
    timeline = {}
    for i in range(29, -1, -1):
        date = now - (i * 24 * 60 * 60)
        date_str = datetime.fromtimestamp(date).strftime("%Y-%m-%d")
        timeline[date_str] = 0
    
    for app in applications:
        app_date = datetime.fromtimestamp(app.get("submitted_at", 0)).strftime("%Y-%m-%d")
        if app_date in timeline:
            timeline[app_date] += 1
    
    return {
        "status_distribution": status_data,
        "timeline": timeline
    }


def add_rating_to_application(app_id, rating, notes=""):
    """Add or update rating for an application"""
    application = find_application(app_id)
    if application:
        application["rating"] = rating
        application["rating_notes"] = notes
        application["rating_date"] = int(time.time())
        update_application(application)
        return True
    return False


def schedule_interview(app_id, interview_date, interview_time, interviewer_email=""):
    """Schedule an interview for an application"""
    application = find_application(app_id)
    if application:
        application.setdefault("interview", {})
        application["interview"]["scheduled_date"] = interview_date
        application["interview"]["scheduled_time"] = interview_time
        application["interview"]["interviewer"] = interviewer_email
        application["interview"]["status"] = "scheduled"
        update_application(application)
        return True
    return False


# --------------------------
# HOME PAGE
# --------------------------

@app.route("/")
def home():
    return render_template("index-enhanced.html")


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
    
    # Filter by status
    status_filter = request.args.get("status", "").strip()
    role_filter = request.args.get("role", "").strip()
    sort_by = request.args.get("sort", "recent").strip()

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
    
    # Status filter
    if status_filter:
        applications = [a for a in applications if a.get("status") == status_filter]
    
    # Role filter
    if role_filter:
        applications = [a for a in applications if a.get("role") == role_filter]
    
    # Sorting
    if sort_by == "recent":
        applications.sort(key=lambda x: x.get("submitted_at", 0), reverse=True)
    elif sort_by == "rating":
        applications.sort(key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "name":
        applications.sort(key=lambda x: x.get("name", "").lower())
    elif sort_by == "experience":
        applications.sort(key=lambda x: int(x.get("experience_years", 0)), reverse=True)

    smtp_configured = bool(
        SMTP_HOST and SMTP_USER and SMTP_PASS
    )
    
    # Get statistics
    stats = get_dashboard_stats()
    chart_data = get_chart_data()

    return render_template(
        "dashboard-enhanced.html",
        applications=applications,
        search_query=search_query,
        status_filter=status_filter,
        role_filter=role_filter,
        sort_by=sort_by,
        smtp_configured=smtp_configured,
        stats=stats,
        chart_data=chart_data
    )


# --------------------------
# DOWNLOAD CV
# --------------------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    if not session.get("admin"):
        return redirect(url_for("login"))

    download = request.args.get("download", "1")
    as_attachment = download == "1"

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=as_attachment
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

        verification_link = url_for("verify_email", token=application["verification_token"], _external=True)
        subject = "🔒 Verify Your Ethio Health Care Application"
        
        body = f"""
Hello {application['name']},

Thank you for applying to Ethio Health Care!

To complete your registration and verify your application, please click the link below:

VERIFICATION LINK:
{verification_link}

This link will confirm your email address and move your application forward in our review process.

Important: This link will expire in 30 days. If it has expired, please contact us at support@ethiohealthcare.com

After verification, you can expect to hear from us within 3-5 business days.

---

Position Applied For: {application['role']}
Application Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(application['submitted_at']))}

If you have any questions, please don't hesitate to reach out.

Best Regards,
The Ethio Health Care Team
support@ethiohealthcare.com
"""
        
        recipient = application.get("account_email") or application.get("email")
        success, msg = send_email(recipient, subject, body)
        
        if success:
            flash(f"✓ Verification email sent to {recipient}")
        else:
            flash(f"⚠ Verification link generated (Email: {msg})")
            # Log the verification link for admin to copy/share if email fails
            print(f"\n🔗 VERIFICATION LINK FOR {application['name']}: {verification_link}\n")

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
    
    # RATING
    elif action == "rate":
        rating = request.form.get("rating", 0)
        notes = request.form.get("rating_notes", "").strip()
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                add_rating_to_application(app_id, rating, notes)
                flash(f"Rating updated: {rating} stars")
            else:
                flash("Rating must be between 1 and 5")
        except:
            flash("Invalid rating")
    
    # SCHEDULE INTERVIEW
    elif action == "schedule_interview":
        interview_date = request.form.get("interview_date", "").strip()
        interview_time = request.form.get("interview_time", "").strip()
        interviewer_email = request.form.get("interviewer_email", "").strip()
        
        if interview_date and interview_time:
            schedule_interview(app_id, interview_date, interview_time, interviewer_email)
            
            # Send email notification
            subject = "Interview Invitation - Ethio Health Care"
            body = f"""
Hello {application['name']},

We are pleased to invite you to an interview with Ethio Health Care.

Date: {interview_date}
Time: {interview_time}
Position: {application.get('role', 'Healthcare Position')}

{f'Interviewer: {interviewer_email}' if interviewer_email else 'More details will be provided soon.'}

Please confirm your availability by replying to this email.

Company Website: {BASE_URL}

If you have any questions before the interview, feel free to reply to this email.

Regards,
Ethio Health Care
"""
            recipient = application.get("email") or application.get("account_email")
            success, message = send_email(recipient, subject, body)
            if success:
                flash(f"Interview scheduled and email sent to {recipient}.")
            else:
                flash(f"Interview scheduled, but email was not sent: {message}")
        else:
            flash("Please provide interview date and time")

    return redirect(url_for("dashboard"))


# --------------------------
# API ENDPOINTS
# --------------------------

@app.route("/api/dashboard-stats")
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    stats = get_dashboard_stats()
    chart_data = get_chart_data()
    
    return jsonify({
        "stats": stats,
        "charts": chart_data
    })


@app.route("/api/export-csv")
def export_csv():
    """Export applications as CSV"""
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    applications = load_applications()
    
    # Filter by status if provided
    status = request.args.get("status", "").strip()
    if status:
        applications = [a for a in applications if a.get("status") == status]
    
    csv_content = "ID,Name,Email,Phone,Role,Experience (Years),Experience,Qualifications,Shift,Status,Verified,Rating,Submitted Date\n"
    
    for app in applications:
        submitted_date = datetime.fromtimestamp(app.get("submitted_at", 0)).strftime("%Y-%m-%d %H:%M")
        csv_content += f'{app.get("id", "")},{app.get("name", "")},{app.get("email", "")},{app.get("phone", "")},{app.get("role", "")},{app.get("experience_years", "")},{app.get("experience", "")},"{app.get("qualifications", "")}",{app.get("shift_preference", "")},{app.get("status", "")},{app.get("verified", False)},{app.get("rating", "N/A")},{submitted_date}\n'
    
    from flask import Response
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"}
    )


@app.route("/api/bulk-action", methods=["POST"])
def bulk_action():
    """Perform bulk actions on multiple applications"""
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    app_ids = data.get("ids", [])
    action = data.get("action", "")
    
    count = 0
    for app_id in app_ids:
        application = find_application(app_id)
        if not application:
            continue
        
        if action == "approve":
            application["status"] = "approved"
            update_application(application)
            count += 1
        elif action == "reject":
            application["status"] = "rejected"
            update_application(application)
            count += 1
        elif action == "delete":
            delete_application(app_id)
            count += 1
    
    return jsonify({"success": True, "count": count})


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
# JOBS POSTING & MANAGEMENT
# --------------------------

@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    """Public job listing page"""
    jobs_list = load_jobs()
    
    search_query = request.args.get("search", "").strip()
    if search_query:
        query = search_query.lower()
        jobs_list = [
            job for job in jobs_list 
            if query in job.get("title", "").lower() 
            or query in job.get("description", "").lower()
            or query in job.get("role", "").lower()
        ]
    
    # Sort by newest first
    jobs_list.sort(key=lambda x: x.get("posted_at", 0), reverse=True)
    
    return render_template(
        "jobs.html",
        jobs=jobs_list,
        search_query=search_query
    )


@app.route("/job/<job_id>", methods=["GET"])
def view_job(job_id):
    """View single job posting"""
    job = find_job(job_id)
    if not job:
        return redirect(url_for("jobs"))
    
    return render_template("job-detail.html", job=job)


@app.route("/dashboard/jobs", methods=["GET", "POST"])
def manage_jobs():
    """CEO job management"""
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "post":
            title = request.form.get("title", "").strip()
            role = request.form.get("role", "").strip()
            salary = request.form.get("salary", "").strip()
            location = request.form.get("location", "").strip()
            company = request.form.get("company", "").strip()
            summary = request.form.get("summary", "").strip()
            responsibilities = request.form.get("responsibilities", "").strip()
            qualifications = request.form.get("qualifications", "").strip()
            competencies = request.form.get("competencies", "").strip()
            posted_date_str = request.form.get("posted_date", "")
            
            # Convert date string to timestamp
            posted_timestamp = int(time.time())
            if posted_date_str:
                try:
                    from datetime import datetime
                    posted_dt = datetime.strptime(posted_date_str, "%Y-%m-%d")
                    posted_timestamp = int(posted_dt.timestamp())
                except:
                    posted_timestamp = int(time.time())

            company_logo_filename = ""
            logo_file = request.files.get("company_logo")
            if logo_file and logo_file.filename:
                ext = logo_file.filename.rsplit(".", 1)[-1].lower()
                if ext in ALLOWED_LOGO_EXTENSIONS:
                    safe_logo = secure_filename(logo_file.filename)
                    company_logo_filename = f"{int(time.time())}_{safe_logo}"
                    logo_file.save(os.path.join(LOGO_FOLDER, company_logo_filename))

            if title and role and company:
                job = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "role": role,
                    "salary": salary,
                    "location": location,
                    "company": company,
                    "company_logo": company_logo_filename,
                    "summary": summary,
                    "responsibilities": responsibilities,
                    "qualifications": qualifications,
                    "competencies": competencies,
                    "posted_at": posted_timestamp,
                    "applications": []
                }
                jobs_list = load_jobs()
                jobs_list.append(job)
                save_jobs(jobs_list)
                flash("Job posted successfully!")
            else:
                flash("Please fill in all required fields")
            
            return redirect(url_for("manage_jobs"))
        
        elif action == "delete":
            job_id = request.form.get("job_id", "")
            delete_job(job_id)
            flash("Job deleted successfully!")
            return redirect(url_for("manage_jobs"))
    
    jobs_list = load_jobs()
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("dashboard-jobs.html", jobs=jobs_list, today=today)


@app.route("/apply-job/<job_id>", methods=["GET", "POST"])
def apply_to_job(job_id):
    """Apply to specific job posting"""
    job = find_job(job_id)
    if not job:
        return redirect(url_for("jobs"))
    
    success = None
    error = None
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        experience = request.form.get("experience", "").strip()
        message = request.form.get("message", "").strip()
        
        if not name or not email or not phone:
            error = "Please fill in all required fields"
        elif not experience:
            error = "Please tell us about your experience"
        else:
            cv_file = request.files.get("cv")
            
            if not cv_file or not cv_file.filename:
                error = "Please upload your CV"
            elif not allowed_file(cv_file.filename):
                error = "Only PDF files are allowed"
            else:
                safe_name = secure_filename(cv_file.filename)
                unique_filename = f"{int(time.time())}_{safe_name}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                
                try:
                    cv_file.save(save_path)
                    
                    application = {
                        "id": str(uuid.uuid4()),
                        "job_id": job_id,
                        "job_title": job.get("title"),
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "experience": experience,
                        "message": message,
                        "cv": unique_filename,
                        "submitted_at": int(time.time()),
                        "status": "pending"
                    }
                    
                    job["applications"].append(application.get("id"))
                    update_job(job)
                    
                    applications = load_applications()
                    applications.append(application)
                    save_applications(applications)
                    
                    success = f"Thank you {name}! Your application for {job.get('title')} has been submitted."
                    
                    subject = f"Application Received - {job.get('title')}"
                    body = f"""
Hello {name},

Thank you for applying to the {job.get('title')} position at Ethio Health Care!

We have received your application and will review it shortly. You will hear from us within 3-5 business days.

Best regards,
Ethio Health Care
"""
                    send_email(email, subject, body)
                    
                except Exception as exc:
                    error = "Could not save your application. Please try again."
                    print(exc)
    
    return render_template(
        "apply-job.html",
        job=job,
        success=success,
        error=error
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