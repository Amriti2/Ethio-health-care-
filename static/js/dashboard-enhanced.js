// Enhanced Dashboard JavaScript

// Dark Mode Functionality
function initDarkMode() {
    const html = document.documentElement;
    const savedMode = localStorage.getItem('darkMode');
    
    if (savedMode === 'true') {
        document.body.classList.add('dark-mode');
    }
    
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
    }
}

// Smooth Filtering
function applyFilters() {
    const search = document.getElementById('searchInput')?.value || '';
    const status = document.getElementById('statusFilter')?.value || '';
    const role = document.getElementById('roleFilter')?.value || '';
    const sort = document.getElementById('sortFilter')?.value || 'recent';
    
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status) params.append('status', status);
    if (role) params.append('role', role);
    params.append('sort', sort);
    
    window.location.href = `/dashboard?${params.toString()}`;
}

// Batch Selection
let selectedIds = [];

function toggleSelectMode() {
    const containers = document.querySelectorAll('.app-checkbox-container');
    const isShowing = containers[0]?.style.display === 'block';
    
    containers.forEach(container => {
        container.style.display = isShowing ? 'none' : 'block';
    });
    
    if (!isShowing) {
        showBatchActions();
    } else {
        hideBatchActions();
        selectedIds = [];
    }
}

function updateBatchCount() {
    selectedIds = Array.from(document.querySelectorAll('.app-checkbox:checked')).map(cb => cb.value);
    
    if (selectedIds.length > 0) {
        showBatchActions();
    } else {
        hideBatchActions();
    }
}

function showBatchActions() {
    let batchBar = document.getElementById('batchBar');
    if (!batchBar) {
        batchBar = document.createElement('div');
        batchBar.id = 'batchBar';
        batchBar.className = 'batch-actions';
        batchBar.innerHTML = `
            <span id="batchCount">0 selected</span>
            <button onclick="batchApprove()" class="btn-small" style="background: linear-gradient(135deg, var(--primary-green) 0%, var(--secondary-teal) 100%);">✅ Approve All</button>
            <button onclick="batchReject()" class="btn-small btn-danger" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">❌ Reject All</button>
            <button onclick="batchDelete()" class="btn-small" style="background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);">🗑️ Delete All</button>
        `;
        document.body.appendChild(batchBar);
    }
    
    document.getElementById('batchCount').textContent = `${selectedIds.length} selected`;
    batchBar.style.display = 'flex';
}

function hideBatchActions() {
    const batchBar = document.getElementById('batchBar');
    if (batchBar) {
        batchBar.style.display = 'none';
    }
}

async function batchApprove() {
    await performBatchAction('approve');
}

async function batchReject() {
    await performBatchAction('reject');
}

async function batchDelete() {
    if (!confirm(`Delete ${selectedIds.length} applications?`)) return;
    await performBatchAction('delete');
}

async function performBatchAction(action) {
    try {
        const response = await fetch('/api/bulk-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ids: selectedIds,
                action: action
            })
        });
        
        const data = await response.json();
        if (data.success) {
            alert(`${action.charAt(0).toUpperCase() + action.slice(1)} ${data.count} applications`);
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error performing batch action');
    }
}

// Export CSV
function exportToCSV() {
    window.location.href = '/api/export-csv';
}

// Rating System
function setupRating() {
    const stars = document.querySelectorAll('.star');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.dataset.rating;
            document.getElementById(`rating-input-${this.dataset.id}`).value = rating;
            updateStars(this.dataset.id, rating);
        });
        
        star.addEventListener('mouseover', function() {
            const rating = this.dataset.rating;
            highlightStars(this.dataset.id, rating);
        });
    });
}

function updateStars(id, rating) {
    const stars = document.querySelectorAll(`.star[data-id="${id}"]`);
    stars.forEach(star => {
        if (star.dataset.rating <= rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function highlightStars(id, rating) {
    const stars = document.querySelectorAll(`.star[data-id="${id}"]`);
    stars.forEach(star => {
        if (star.dataset.rating <= rating) {
            star.style.filter = 'grayscale(0%)';
        } else {
            star.style.filter = 'grayscale(80%)';
        }
    });
}

// Search with debounce
let searchTimeout;
function searchApplications() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        applyFilters();
    }, 300);
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Copy verification link
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}

// Confirm delete
function confirmDelete() {
    return confirm('Are you sure you want to delete this application? This cannot be undone.');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initDarkMode();
    setupRating();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideBatchActions();
        }
    });
    
    // Add scroll-to-top button
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scrollTopBtn';
    scrollBtn.textContent = '↑';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--secondary-teal) 100%);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 1.5rem;
        cursor: pointer;
        display: none;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transition: all 0.3s ease;
    `;
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollBtn.style.display = 'flex';
            scrollBtn.style.alignItems = 'center';
            scrollBtn.style.justifyContent = 'center';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
    
    scrollBtn.addEventListener('click', scrollToTop);
    scrollBtn.addEventListener('mouseover', function() {
        this.style.transform = 'scale(1.1)';
    });
    scrollBtn.addEventListener('mouseout', function() {
        this.style.transform = 'scale(1)';
    });
});

// Live search filter (real-time)
function liveSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                applyFilters();
            }, 500);
        });
    }
}

// Initialize live search
liveSearch();

// Export functions to global scope
window.applyFilters = applyFilters;
window.toggleSelectMode = toggleSelectMode;
window.updateBatchCount = updateBatchCount;
window.batchApprove = batchApprove;
window.batchReject = batchReject;
window.batchDelete = batchDelete;
window.exportToCSV = exportToCSV;
window.confirmDelete = confirmDelete;
