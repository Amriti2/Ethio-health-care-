import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
import { getDatabase, ref, push, onValue, serverTimestamp, set } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-database.js";
import { firebaseConfig } from "./firebase-config.js";

let firebaseApp;
let database;
let FIREBASE_ENABLED = false;

try {
    if (firebaseConfig.apiKey && !firebaseConfig.apiKey.includes("YOUR_")) {
        firebaseApp = initializeApp(firebaseConfig);
        database = getDatabase(firebaseApp);
        FIREBASE_ENABLED = true;
        console.log("✅ Firebase initialized for real-time job sync");
    }
} catch (error) {
    console.log("⚠️ Firebase not configured, using server-side storage");
}

/**
 * Listen for real-time job updates from Firebase
 */
export function listenToJobs(callback) {
    if (!FIREBASE_ENABLED) {
        console.log("Firebase not enabled, using server updates");
        return;
    }

    try {
        const jobsRef = ref(database, 'jobs');
        onValue(jobsRef, (snapshot) => {
            const data = snapshot.val();
            const jobs = data ? Object.values(data) : [];
            callback(jobs);
        }, (error) => {
            console.error("Error listening to jobs:", error);
        });
    } catch (error) {
        console.error("Error setting up jobs listener:", error);
    }
}

/**
 * Publish a new job to Firebase
 */
export async function publishJobToFirebase(jobData) {
    if (!FIREBASE_ENABLED) {
        console.log("Firebase not enabled, job saved server-side");
        return false;
    }

    try {
        const jobsRef = ref(database, 'jobs');
        const newJobRef = push(jobsRef);
        
        const fullJobData = {
            ...jobData,
            id: newJobRef.key,
            posted_at: serverTimestamp(),
            applications: []
        };
        
        await set(newJobRef, fullJobData);
        console.log("✅ Job published to Firebase:", fullJobData.id);
        return true;
    } catch (error) {
        console.error("Error publishing job to Firebase:", error);
        return false;
    }
}

/**
 * Add application to Firebase
 */
export async function submitApplicationToFirebase(jobId, applicationData) {
    if (!FIREBASE_ENABLED) {
        console.log("Firebase not enabled, application saved server-side");
        return false;
    }

    try {
        const appRef = ref(database, `applications/${jobId}`);
        const newAppRef = push(appRef);
        
        const fullAppData = {
            ...applicationData,
            jobId: jobId,
            submittedAt: serverTimestamp()
        };
        
        await set(newAppRef, fullAppData);
        console.log("✅ Application submitted to Firebase");
        return true;
    } catch (error) {
        console.error("Error submitting application to Firebase:", error);
        return false;
    }
}

/**
 * Get current Firebase status
 */
export function getFirebaseStatus() {
    return {
        enabled: FIREBASE_ENABLED,
        message: FIREBASE_ENABLED ? "Real-time sync active" : "Server-side storage"
    };
}

// Auto-sync status on page load
document.addEventListener('DOMContentLoaded', () => {
    const status = getFirebaseStatus();
    console.log(`🔄 Job Storage: ${status.message}`);
});
