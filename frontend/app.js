// =====================
// CONFIGURATION
// =====================

const API_BASE_URL = '/api';

// =====================
// AUTHENTICATION MODAL MANAGEMENT
// =====================

function showLoginModal() {
    document.getElementById('login-modal').classList.add('active');
    document.getElementById('register-modal').classList.remove('active');
}

function showRegisterModal() {
    document.getElementById('login-modal').classList.remove('active');
    document.getElementById('register-modal').classList.add('active');
}

function hideAuthModals() {
    document.getElementById('login-modal').classList.remove('active');
    document.getElementById('register-modal').classList.remove('active');
}

function showAlert(containerId, message, type) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user) {
        showLoginModal();
        return null;
    }
    
    hideAuthModals();
    return JSON.parse(user);
}

function initializeUserProfile() {
    const user = localStorage.getItem('user');
    if (!user) return;
    
    const userData = JSON.parse(user);
    const nameEl = document.getElementById('user-name');
    const emailEl = document.getElementById('user-email');
    const avatarEl = document.getElementById('user-avatar');
    
    if (nameEl) nameEl.textContent = userData.first_name || userData.username || 'User';
    if (emailEl) emailEl.textContent = userData.email || 'user@email.com';
    
    if (avatarEl) {
        const firstLetter = ((userData.first_name || userData.username || 'U')[0]).toUpperCase();
        avatarEl.textContent = firstLetter;
    }

    populateProfileForm(userData);
}

function getPreferences() {
    try {
        return JSON.parse(localStorage.getItem('habittrack_preferences') || '{}');
    } catch {
        return {};
    }
}

function savePreferences(preferences) {
    localStorage.setItem('habittrack_preferences', JSON.stringify(preferences));
    applyPreferences();
}

function applyPreferences() {
    const prefs = getPreferences();
    const neonToggle = document.getElementById('pref-neon');
    if (neonToggle) neonToggle.checked = prefs.neon !== false;
    const remindersToggle = document.getElementById('pref-reminders');
    if (remindersToggle) remindersToggle.checked = prefs.reminders !== false;
    const insightsToggle = document.getElementById('pref-insights');
    if (insightsToggle) insightsToggle.checked = prefs.insights !== false;
}

function populateProfileForm(userData) {
    if (!userData) return;
    const fields = {
        'profile-username': userData.username || '',
        'profile-email': userData.email || '',
        'profile-first-name': userData.first_name || '',
        'profile-last-name': userData.last_name || ''
    };

    Object.entries(fields).forEach(([id, value]) => {
        const field = document.getElementById(id);
        if (field) field.value = value;
    });
}

// =====================
// AUTHENTICATION HANDLERS
// =====================

function setupAuthHandlers() {
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const statusEl = document.getElementById('profile-status');
            const formData = {
                username: document.getElementById('profile-username').value.trim(),
                email: document.getElementById('profile-email').value.trim(),
                first_name: document.getElementById('profile-first-name').value.trim(),
                last_name: document.getElementById('profile-last-name').value.trim(),
                password: document.getElementById('profile-password').value
            };

            if (statusEl) {
                statusEl.textContent = 'Saving...';
                statusEl.className = 'status-message';
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/profile`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(formData)
                });
                const data = await response.json().catch(() => ({}));

                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    initializeUserProfile();
                    if (statusEl) {
                        statusEl.textContent = 'Profile updated successfully.';
                        statusEl.className = 'status-message success';
                    }
                } else {
                    if (statusEl) {
                        statusEl.textContent = data.error || 'Unable to update profile.';
                        statusEl.className = 'status-message error';
                    }
                }
            } catch (error) {
                if (statusEl) {
                    statusEl.textContent = 'Connection error. Please try again.';
                    statusEl.className = 'status-message error';
                }
            }
        });
    }

    // Login form handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json().catch(() => ({}));
                
                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    hideAuthModals();
                    initializeUserProfile();
                    initializeApp();
                } else {
                    showAlert('login-alert-container', data.error || data.message || 'Login failed', 'error');
                }
            } catch (error) {
                showAlert('login-alert-container', 'An error occurred', 'error');
            }
        });
    }
    
    // Register form handler
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('register-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (password !== confirmPassword) {
                showAlert('register-alert-container', 'Passwords do not match', 'error');
                return;
            }
            
            if (password.length < 8) {
                showAlert('register-alert-container', 'Password must be at least 8 characters', 'error');
                return;
            }
            
            const formData = {
                first_name: document.getElementById('first-name').value,
                last_name: document.getElementById('last-name').value,
                username: document.getElementById('username').value,
                email: document.getElementById('register-email').value,
                password: password
            };
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json().catch(() => ({}));
                
                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    hideAuthModals();
                    initializeUserProfile();
                    initializeApp();
                } else {
                    showAlert('register-alert-container', data.error || data.message || 'Registration failed', 'error');
                }
            } catch (error) {
                showAlert('register-alert-container', 'An error occurred', 'error');
            }
        });
    }
    
    // Modal switching links
    const signupLink = document.getElementById('signup-link');
    if (signupLink) {
        signupLink.addEventListener('click', (e) => {
            e.preventDefault();
            showRegisterModal();
        });
    }
    
    const signinLink = document.getElementById('signin-link');
    if (signinLink) {
        signinLink.addEventListener('click', (e) => {
            e.preventDefault();
            showLoginModal();
        });
    }
}

// Logout handler
function setupPreferencesHandlers() {
    const prefNeon = document.getElementById('pref-neon');
    const prefReminders = document.getElementById('pref-reminders');
    const prefInsights = document.getElementById('pref-insights');

    const persistPreferences = () => {
        const preferences = {
            neon: prefNeon ? prefNeon.checked : true,
            reminders: prefReminders ? prefReminders.checked : true,
            insights: prefInsights ? prefInsights.checked : true
        };
        savePreferences(preferences);
    };

    [prefNeon, prefReminders, prefInsights].forEach((toggle) => {
        toggle?.addEventListener('change', persistPreferences);
    });
}

function setupLogoutHandler() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    credentials: 'include'
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
            
            localStorage.removeItem('user');
            showLoginModal();
            document.querySelector('.tracker-section').innerHTML = '';
            document.querySelector('.analytics-section').innerHTML = '';
        });
    }
}

// =====================
// DATA MANAGEMENT
// =====================

const STORAGE_KEY = 'habitTracker_data';
const HABITS_KEY = 'habitTracker_habits';

class HabitTracker {
    constructor() {
        this.habits = [];
        this.currentWeekStart = this.getWeekStart(new Date());
        this.chartInstances = {};
        this.daysInView = 14;
    }

    async loadHabits() {
        try {
            const response = await fetch(`${API_BASE_URL}/habits`, { credentials: 'include' });
            const data = await response.json().catch(() => []);
            if (Array.isArray(data)) {
                this.habits = data;
                localStorage.setItem(HABITS_KEY, JSON.stringify(this.habits));
            }
        } catch (error) {
            const saved = localStorage.getItem(HABITS_KEY);
            this.habits = saved ? JSON.parse(saved) : [];
        }
    }

    saveHabits() {
        localStorage.setItem(HABITS_KEY, JSON.stringify(this.habits));
    }

    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }

    getWeekEnd(date) {
        const end = new Date(this.getWeekStart(date));
        end.setDate(end.getDate() + this.daysInView - 1);
        return end;
    }

    async addHabit(name) {
        if (!name.trim()) return false;
        
        const response = await fetch(`${API_BASE_URL}/habits`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: name.trim() })
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok && data.habit) {
            this.habits.push(data.habit);
            this.saveHabits();
            return data.habit;
        }
        return false;
    }

    async deleteHabit(habitId) {
        const response = await fetch(`${API_BASE_URL}/habits/${habitId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if (response.ok) {
            this.habits = this.habits.filter(h => h.id !== habitId);
            this.saveHabits();
        }
    }

    async toggleCompletion(habitId, dateStr) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return false;
        
        const response = await fetch(`${API_BASE_URL}/habits/${habitId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ date: `${dateStr}` })
        });
        const data = await response.json().catch(() => ({}));
        if (response.ok) {
            const completion = data.completion || {};
            const exists = habit.completions.some(item => item.date === completion.date);
            if (exists) {
                habit.completions = habit.completions.filter(item => item.date !== completion.date);
            }
            if (completion.completed !== false) {
                habit.completions.push(completion);
            }
            this.saveHabits();
            return completion.completed;
        }
        return false;
    }

    getStreak(habitId) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return 0;
        
        let streak = 0;
        const today = new Date();
        
        for (let i = 0; i < 365; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            if (habit.completions[dateStr]) {
                streak++;
            } else if (i > 0) {
                break;
            }
        }
        
        return streak;
    }

    getCompletionRate(habitId) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return 0;
        
        const today = new Date();
        const createdDate = new Date(habit.created_at || habit.createdAt || new Date());
        const daysPassed = Math.floor((today - createdDate) / (1000 * 60 * 60 * 24)) + 1;
        const completedDays = (habit.completions || []).filter(item => item.completed).length;
        
        return Math.round((completedDays / daysPassed) * 100);
    }
}

// =====================
// UI INITIALIZATION
// =====================

let tracker;

async function initializeApp() {
    const user = checkAuth();
    if (!user) return;
    
    initializeUserProfile();
    
    tracker = new HabitTracker();
    await tracker.loadHabits();
    
    renderCalendarHeader();
    renderHabits();
    renderCharts();
    setupEventListeners();
}

function renderCalendarHeader() {
    const header = document.getElementById('calendar-days-header');
    if (!header || !tracker) return;
    
    header.innerHTML = '';
    const weekStart = tracker.getWeekStart(tracker.currentWeekStart || new Date());
    
    for (let i = 0; i < tracker.daysInView; i++) {
        const date = new Date(weekStart);
        date.setDate(date.getDate() + i);
        
        const dateStr = date.toISOString().split('T')[0];
        const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayOfMonth = date.getDate();
        
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day-header';
        dayDiv.innerHTML = `<span>${dayOfWeek}</span><span>${dayOfMonth}</span>`;
        header.appendChild(dayDiv);
    }
    
    updateWeekDisplay();
}

function updateWeekDisplay() {
    const display = document.getElementById('week-display');
    if (!display || !tracker) return;
    
    const weekStart = tracker.getWeekStart(tracker.currentWeekStart || new Date());
    const weekEnd = tracker.getWeekEnd(tracker.currentWeekStart || new Date());
    
    const startStr = weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const endStr = weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    
    display.textContent = `Week of ${startStr} - ${endStr}`;
}

function renderHabits() {
    const body = document.getElementById('calendar-body');
    if (!body) return;
    
    body.innerHTML = '';
    
    if (tracker.habits.length === 0) {
        body.innerHTML = '<div class="empty-state">No habits yet. Add one to get started!</div>';
        return;
    }
    
    tracker.habits.forEach(habit => {
        const habitRow = document.createElement('div');
        habitRow.className = 'habit-row';
        
        const habitLabel = document.createElement('div');
        habitLabel.className = 'habit-label';
        
        const habitName = document.createElement('span');
        habitName.className = 'habit-name';
        habitName.textContent = habit.name;
        
        const habitStats = document.createElement('div');
        habitStats.className = 'habit-stats';
        
        const streak = tracker.getStreak(habit.id);
        const rate = tracker.getCompletionRate(habit.id);
        
        habitStats.innerHTML = `
            <span class="stat">🔥 ${streak}</span>
            <span class="stat">${rate}%</span>
        `;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn-delete';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = () => {
            if (confirm('Delete this habit?')) {
                tracker.deleteHabit(habit.id).then(() => {
                    renderHabits();
                    renderCharts();
                });
            }
        };
        
        habitLabel.appendChild(habitName);
        habitLabel.appendChild(habitStats);
        habitLabel.appendChild(deleteBtn);
        
        const habitsCheckboxes = document.createElement('div');
        habitsCheckboxes.className = 'habit-checkboxes';
        
        const weekStart = tracker.getWeekStart(tracker.currentWeekStart || new Date());
        
        for (let i = 0; i < tracker.daysInView; i++) {
            const date = new Date(weekStart);
            date.setDate(date.getDate() + i);
            const dateStr = date.toISOString().split('T')[0];
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'habit-checkbox';
            const completed = (habit.completions || []).some(item => item.date === dateStr && item.completed);
            checkbox.checked = completed;

            // Optimistic toggle handler: update UI immediately, then sync with server
            checkbox.addEventListener('change', async (e) => {
                const checked = e.target.checked;
                if (!habit.completions) habit.completions = [];

                // apply optimistic change locally
                if (checked) {
                    if (!habit.completions.some(item => item.date === dateStr)) {
                        habit.completions.push({ date: dateStr, completed: true });
                    }
                } else {
                    habit.completions = habit.completions.filter(item => item.date !== dateStr);
                }
                tracker.saveHabits();

                // disable while syncing
                checkbox.disabled = true;
                try {
                    const ok = await tracker.toggleCompletion(habit.id, dateStr);
                    if (ok === false) {
                        // server returned failure; revert optimistic
                        if (checked) {
                            habit.completions = habit.completions.filter(item => item.date !== dateStr);
                        } else {
                            habit.completions.push({ date: dateStr, completed: true });
                        }
                        tracker.saveHabits();
                    }
                } catch (err) {
                    // revert on error
                    if (checked) {
                        habit.completions = habit.completions.filter(item => item.date !== dateStr);
                    } else {
                        habit.completions.push({ date: dateStr, completed: true });
                    }
                    tracker.saveHabits();
                } finally {
                    checkbox.disabled = false;
                    renderHabits();
                    renderCharts();
                }
            });

            const label = document.createElement('label');
            label.className = 'checkbox-label';
            label.appendChild(checkbox);
            habitsCheckboxes.appendChild(label);
        }
        
        habitRow.appendChild(habitLabel);
        habitRow.appendChild(habitsCheckboxes);
        body.appendChild(habitRow);
    });
}

function renderCharts() {
    if (tracker.habits.length === 0) return;
    
    renderPieChart();
    renderLineChart();
    renderBarChart();
}

function renderPieChart() {
    const ctx = document.getElementById('pie-chart');
    if (!ctx) return;
    
    const completed = tracker.habits.map(h => tracker.getCompletionRate(h.id));
    const avg = completed.reduce((a, b) => a + b, 0) / completed.length;
    
    if (tracker.chartInstances.pie) {
        tracker.chartInstances.pie.destroy();
    }
    
    tracker.chartInstances.pie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending'],
            datasets: [{
                data: [Math.round(avg), 100 - Math.round(avg)],
                backgroundColor: ['#00D084', '#E0E0E0'],
                borderColor: ['#00D084', '#E0E0E0']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function renderLineChart() {
    const ctx = document.getElementById('line-chart');
    if (!ctx) return;
    
    const labels = [];
    const datasets = [];
    
    for (let i = 13; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    tracker.habits.slice(0, 3).forEach((habit, idx) => {
        const colors = ['#00D084', '#667eea', '#FF6B6B'];
        const data = [];
        
        for (let i = 13; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            data.push(habit.completions[dateStr] ? 1 : 0);
        }
        
        datasets.push({
            label: habit.name,
            data: data,
            borderColor: colors[idx],
            backgroundColor: colors[idx] + '20',
            tension: 0.4,
            fill: true
        });
    });
    
    if (tracker.chartInstances.line) {
        tracker.chartInstances.line.destroy();
    }
    
    tracker.chartInstances.line = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            }
        }
    });
}

function renderBarChart() {
    const ctx = document.getElementById('bar-chart');
    if (!ctx) return;
    
    const labels = tracker.habits.map(h => h.name);
    const data = tracker.habits.map(h => tracker.getCompletionRate(h.id));
    
    if (tracker.chartInstances.bar) {
        tracker.chartInstances.bar.destroy();
    }
    
    tracker.chartInstances.bar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Completion Rate (%)',
                data,
                backgroundColor: '#00D084',
                borderColor: '#00A366',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// =====================
// EVENT LISTENERS
// =====================

function setupEventListeners() {
    const addBtn = document.getElementById('add-habit-btn');
    const habitInput = document.getElementById('habit-input');
    
    if (addBtn && habitInput) {
        addBtn.addEventListener('click', async () => {
            const name = habitInput.value.trim();
            if (name) {
                await tracker.addHabit(name);
                habitInput.value = '';
                renderCalendarHeader();
                renderHabits();
                renderCharts();
            }
        });
        
        habitInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addBtn.click();
            }
        });
    }
    
    const prevWeekBtn = document.getElementById('prev-week');
    const nextWeekBtn = document.getElementById('next-week');
    
    if (prevWeekBtn) {
        prevWeekBtn.addEventListener('click', () => {
            tracker.currentWeekStart = new Date(tracker.currentWeekStart || new Date());
            tracker.currentWeekStart.setDate(tracker.currentWeekStart.getDate() - 7);
            renderCalendarHeader();
            renderHabits();
        });
    }
    
    if (nextWeekBtn) {
        nextWeekBtn.addEventListener('click', () => {
            tracker.currentWeekStart = new Date(tracker.currentWeekStart || new Date());
            tracker.currentWeekStart.setDate(tracker.currentWeekStart.getDate() + 7);
            renderCalendarHeader();
            renderHabits();
        });
    }
    
    const trackerLink = document.getElementById('tracker-link');
    const analyticsLink = document.getElementById('analytics-link');
    const profileLink = document.getElementById('profile-link');
    const trackerSection = document.querySelector('.tracker-section');
    const analyticsSection = document.querySelector('.analytics-section');
    const profileSection = document.querySelector('.profile-section');

    const setActiveSection = (activeLink) => {
        [trackerLink, analyticsLink, profileLink].forEach((link) => {
            link?.classList.toggle('active', link === activeLink);
        });

        if (trackerSection) trackerSection.style.display = activeLink === trackerLink ? 'flex' : 'none';
        if (analyticsSection) analyticsSection.style.display = activeLink === analyticsLink ? 'flex' : 'none';
        if (profileSection) profileSection.style.display = activeLink === profileLink ? 'flex' : 'none';
    };
    
    if (trackerLink) {
        trackerLink.addEventListener('click', () => setActiveSection(trackerLink));
    }
    
    if (analyticsLink) {
        analyticsLink.addEventListener('click', () => setActiveSection(analyticsLink));
    }

    if (profileLink) {
        profileLink.addEventListener('click', () => setActiveSection(profileLink));
    }
}

// =====================
// INITIALIZATION
// =====================

document.addEventListener('DOMContentLoaded', () => {
    setupAuthHandlers();
    setupPreferencesHandlers();
    setupLogoutHandler();
    applyPreferences();
    checkAuth();
    initializeApp();
});
