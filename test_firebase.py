import time
import json
from datetime import datetime
from app import app, save_jobs, load_jobs

with app.app_context():
    # Create test job
    test_job = {
        'id': 'test-job-' + str(int(time.time())),
        'title': '🏥 Senior Registered Nurse',
        'company': 'Ethio Health Care',
        'company_logo': '',
        'role': 'Nursing',
        'salary': '35,000 - 50,000 ETB/month',
        'location': 'Addis Ababa',
        'summary': 'We are seeking an experienced Senior Registered Nurse to lead our nursing team.',
        'responsibilities': 'Oversee patient care, manage nursing staff, ensure compliance with healthcare standards',
        'qualifications': 'BSc in Nursing, 5+ years experience, valid license',
        'competencies': 'Leadership, Patient Care, Clinical Skills, Team Management',
        'posted_at': int(time.time())
    }
    
    # Save to Firebase
    jobs = load_jobs()
    jobs.append(test_job)
    save_jobs(jobs)
    
    # Verify it's saved
    loaded = load_jobs()
    print(f'✅ Test job saved to Firebase')
    print(f'✅ Total jobs in Firebase: {len(loaded)}')
    if loaded:
        latest = loaded[-1]
        print(f'✅ Latest job: {latest.get("title")} at {latest.get("company")}')
