# Firebase Integration Setup Guide

## Overview
This application supports Firebase Realtime Database for storing jobs and applications. You can use it for real-time sync across all users, or keep using the current JSON-based storage.

## Option 1: Keep Using Current Storage (No Setup Needed) ✅
Jobs and applications are automatically saved to:
- `data/jobs.json` 
- `data/applications.json`

**Status:** Already working on localhost and Render!

---

## Option 2: Add Firebase (Real-time Sync)

### Step 1: Get Firebase Credentials
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing one
3. Go to **⚙️ Settings → Service Accounts**
4. Click **Generate New Private Key** 
5. Copy the entire JSON file contents

### Step 2: Add to Render Environment Variables

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your **ethio-health-care** service
3. Go to **Environment** tab
4. Add these variables:

```
FIREBASE_CREDENTIALS = {"type": "service_account", "project_id": "your-project", ...}
FIREBASE_DATABASE_URL = https://your-project-default-rtdb.firebaseio.com
```

**Note:** For `FIREBASE_CREDENTIALS`, paste the entire JSON in one line (Render will format it)

### Step 3: Add to Local `.env` (for development)

Create `.env` file in project root:
```
FIREBASE_CREDENTIALS={"type": "service_account", "project_id": "your-project", ...}
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com
```

### Step 4: Update Frontend Config

Edit `static/js/firebase-config.js`:
```javascript
export const firebaseConfig = {
    apiKey: "YOUR_ACTUAL_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    databaseURL: "https://your-project-default-rtdb.firebaseio.com",
    projectId: "your-project",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "YOUR_ACTUAL_ID",
    appId: "YOUR_ACTUAL_APP_ID"
};
```

---

## How It Works

### Backend (app.py)
- Tries to load/save jobs and applications to Firebase first
- Falls back to JSON files automatically if Firebase is disabled
- Both storage methods work simultaneously (redundancy)

### Frontend (firebase-jobs.js)
- Listens for real-time job updates
- Publishes new jobs to Firebase
- Tracks job applications in real-time
- Works even if Firebase is not configured (degrades gracefully)

---

## Testing

### Local Testing
```bash
python app.py
# Access http://127.0.0.1:5002
# Jobs save to both JSON and (optionally) Firebase
```

### Check Firebase Status
Open browser DevTools Console → Look for:
- ✅ "Firebase initialized for real-time job sync" = Firebase enabled
- ⚠️ "Firebase not configured, using server-side storage" = Using JSON only

---

## Features

✅ **Jobs synced in real-time** - All users see new postings instantly  
✅ **Applications tracked** - CEO dashboard updates live  
✅ **Automatic fallback** - Works perfectly without Firebase  
✅ **Backup storage** - JSON files keep local copy always  
✅ **Zero downtime** - Switch between storage methods anytime  

---

## No Credentials Yet?

The app works perfectly without Firebase! Jobs and applications are stored in:
- `data/jobs.json`
- `data/applications.json`

**This is sufficient for production use on Render.** Add Firebase later whenever you're ready for real-time sync.

---

## Support

If Firebase credentials are wrong or incomplete:
1. App automatically falls back to JSON storage
2. Check logs in Render dashboard for errors
3. Delete FIREBASE_CREDENTIALS variable to disable Firebase temporarily
