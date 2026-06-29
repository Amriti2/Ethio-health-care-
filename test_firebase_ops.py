import json
from app import app, FIREBASE_ENABLED, load_jobs, save_jobs

with app.app_context():
    print(f"Firebase Enabled: {FIREBASE_ENABLED}")
    print("Testing Firebase operations...")
    
    # Test loading
    try:
        jobs = load_jobs()
        print(f"✅ Load successful: {len(jobs)} jobs")
    except Exception as e:
        print(f"❌ Load error: {e}")
    
    # Test saving with a test job
    try:
        test_job = {
            "id": "test-job",
            "title": "Test Job",
            "company": "Test Co",
            "role": "Test Role",
            "posted_at": 1234567890
        }
        test_jobs = [test_job]
        result = save_jobs(test_jobs)
        print(f"✅ Save result: {result}")
    except Exception as e:
        print(f"❌ Save error: {e}")
        import traceback
        traceback.print_exc()
