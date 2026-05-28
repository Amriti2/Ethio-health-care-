import { initializeApp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-app.js";
import { getDatabase, ref, push, onValue, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.23.0/firebase-database.js";
import { firebaseConfig } from "./firebase-config.js";

const firebaseApp = initializeApp(firebaseConfig);
const database = getDatabase(firebaseApp);

function showToast(message, isError = false) {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.right = '24px';
    toast.style.top = '24px';
    toast.style.padding = '16px 22px';
    toast.style.borderRadius = '18px';
    toast.style.background = isError ? '#ffeef0' : '#ddf3e8';
    toast.style.color = isError ? '#8a1f2f' : '#0d5b4f';
    toast.style.boxShadow = '0 18px 40px rgba(15, 47, 72, 0.12)';
    toast.style.zIndex = '999';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4200);
}

async function saveApplicationToFirebase(data) {
    const applicationsRef = ref(database, 'applications');
    await push(applicationsRef, {
        ...data,
        submittedAt: serverTimestamp()
    });
}

function createApplicationCard(item) {
    const card = document.createElement('article');
    card.className = 'application-card';
    card.innerHTML = `
        <h3>${item.name} — ${item.role}</h3>
        <p>${item.message || 'No additional message provided.'}</p>
        <div class="meta">
            <div><strong>Email:</strong> ${item.email}</div>
            <div><strong>Phone:</strong> ${item.phone}</div>
            <div><strong>Experience:</strong> ${item.experience || 'Not specified'}</div>
            <div><strong>Submitted:</strong> ${item.submittedAt || 'Now'}</div>
        </div>
    `;
    return card;
}

function initApplicationForm() {
    const form = document.querySelector('#application-form');
    if (!form) {
        return;
    }
    // word count for about textarea
    const about = form.querySelector('#about');
    const wordCountEl = document.querySelector('#word-count');
    function updateWordCount(){
        if(!about) return;
        const words = about.value.trim().split(/\s+/).filter(Boolean).length;
        wordCountEl.textContent = Math.min(words, 500);
    }
    about?.addEventListener('input', updateWordCount);
}

function initDashboard() {
    const list = document.querySelector('#dashboard-applications');
    const totalValue = document.querySelector('#application-count');
    const nurseValue = document.querySelector('#nurse-count');
    const doctorValue = document.querySelector('#doctor-count');
    const midwifeValue = document.querySelector('#midwife-count');
    const caregiverValue = document.querySelector('#caregiver-count');
    const otherValue = document.querySelector('#other-count');
    const searchInput = document.querySelector('#dashboard-search');
    const roleFilter = document.querySelector('#dashboard-role-filter');

    if (!list) {
        return;
    }

    const applicationsRef = ref(database, 'applications');
    let allRows = [];

    const renderDashboard = () => {
        const searchText = searchInput?.value.trim().toLowerCase() || '';
        const selectedRole = roleFilter?.value || 'all';

        list.innerHTML = '';

        const filteredRows = allRows.filter((entry) => {
            const matchesRole = selectedRole === 'all' || entry.role === selectedRole;
            const searchContent = `${entry.name} ${entry.role} ${entry.email}`.toLowerCase();
            const matchesSearch = !searchText || searchContent.includes(searchText);
            return matchesRole && matchesSearch;
        });

        filteredRows.forEach((entry) => list.appendChild(createApplicationCard(entry)));

        totalValue.textContent = allRows.length;
        nurseValue.textContent = allRows.filter((entry) => entry.role === 'Nurse').length;
        doctorValue.textContent = allRows.filter((entry) => entry.role === 'Doctor').length;
        midwifeValue.textContent = allRows.filter((entry) => entry.role === 'Midwife').length;
        caregiverValue.textContent = allRows.filter((entry) => entry.role === 'Care Giver').length;
        otherValue.textContent = allRows.filter((entry) => entry.role === 'Other').length;
    };

    onValue(applicationsRef, (snapshot) => {
        const applications = snapshot.val() || {};
        allRows = Object.values(applications).map((entry) => ({
            ...entry,
            submittedAt: typeof entry.submittedAt === 'number'
                ? new Date(entry.submittedAt).toLocaleString()
                : 'Now'
        }));
        allRows.sort((a, b) => (a.submittedAt < b.submittedAt ? 1 : -1));
        renderDashboard();
    });

    searchInput?.addEventListener('input', renderDashboard);
    roleFilter?.addEventListener('change', renderDashboard);
}
}

function initDashboard() {
    const list = document.querySelector('#dashboard-applications');
    const totalValue = document.querySelector('#application-count');
    const nurseValue = document.querySelector('#nurse-count');
    const doctorValue = document.querySelector('#doctor-count');
    const midwifeValue = document.querySelector('#midwife-count');
    const caregiverValue = document.querySelector('#caregiver-count');
    const otherValue = document.querySelector('#other-count');
    const searchInput = document.querySelector('#dashboard-search');
    const roleFilter = document.querySelector('#dashboard-role-filter');

    if (!list) {
        return;
    }

    const applicationsRef = ref(database, 'applications');
    let allRows = [];

    const renderDashboard = () => {
        const searchText = searchInput?.value.trim().toLowerCase() || '';
        const selectedRole = roleFilter?.value || 'all';

        list.innerHTML = '';

        const filteredRows = allRows.filter((entry) => {
            const matchesRole = selectedRole === 'all' || entry.role === selectedRole;
            const searchContent = `${entry.name} ${entry.role} ${entry.email}`.toLowerCase();
            const matchesSearch = !searchText || searchContent.includes(searchText);
            return matchesRole && matchesSearch;
        });

        filteredRows.forEach((entry) => list.appendChild(createApplicationCard(entry)));

        totalValue.textContent = allRows.length;
        nurseValue.textContent = allRows.filter((entry) => entry.role === 'Nurse').length;
        doctorValue.textContent = allRows.filter((entry) => entry.role === 'Doctor').length;
        midwifeValue.textContent = allRows.filter((entry) => entry.role === 'Midwife').length;
        caregiverValue.textContent = allRows.filter((entry) => entry.role === 'Care Giver').length;
        otherValue.textContent = allRows.filter((entry) => entry.role === 'Other').length;
    };

    onValue(applicationsRef, (snapshot) => {
        const applications = snapshot.val() || {};
        allRows = Object.values(applications).map((entry) => ({
            ...entry,
            submittedAt: typeof entry.submittedAt === 'number'
                ? new Date(entry.submittedAt).toLocaleString()
                : 'Now'
        }));
        allRows.sort((a, b) => (a.submittedAt < b.submittedAt ? 1 : -1));
        renderDashboard();
    });

    searchInput?.addEventListener('input', renderDashboard);
    roleFilter?.addEventListener('change', renderDashboard);
}

window.addEventListener('DOMContentLoaded', () => {
    initApplicationForm();
    initDashboard();
});
