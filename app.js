// =====================
// AUTHENTICATION
// =====================

const API_BASE_URL = 'http://localhost:5000/api';

// Check if user is authenticated
function checkAuth() {
    const user = localStorage.getItem('user');
    if (!user) {
        window.location.href = '/frontend/login.html';
        return false;
    }
    return JSON.parse(user);
}

// Initialize user profile
function initializeUserProfile() {
    const user = checkAuth();
    if (user) {
        document.getElementById('user-name').textContent = user.username || 'User';
        document.getElementById('user-email').textContent = user.email || 'user@email.com';
        
        // Set avatar with first letter
        const firstLetter = (user.first_name || user.username || 'U')[0].toUpperCase();
        document.getElementById('user-avatar').textContent = firstLetter;
    }
}

// Logout handler
document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    localStorage.removeItem('user');
    window.location.href = '/frontend/login.html';
});

// =====================
// DATA MANAGEMENT
// =====================

const STORAGE_KEY = 'habitTracker_data';
const HABITS_KEY = 'habitTracker_habits';

class HabitTracker {
    constructor() {
        this.habits = this.loadHabits();
        this.currentWeekStart = this.getWeekStart(new Date());
        this.chartInstances = {};
        this.daysInView = 14; // Show 2 weeks
    }

    // Load habits from localStorage
    loadHabits() {
        const saved = localStorage.getItem(HABITS_KEY);
        return saved ? JSON.parse(saved) : [];
    }

    // Save habits to localStorage
    saveHabits() {
        localStorage.setItem(HABITS_KEY, JSON.stringify(this.habits));
    }

    // Get week start date (Monday)
    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }

    // Get week end date
    getWeekEnd(date) {
        const end = new Date(this.getWeekStart(date));
        end.setDate(end.getDate() + this.daysInView - 1);
        return end;
    }

    // Add a new habit
    addHabit(name) {
        if (!name.trim()) return false;
        
        const habit = {
            id: Date.now(),
            name: name.trim(),
            createdAt: new Date().toISOString(),
            completions: {} // Format: { 'YYYY-MM-DD': true }
        };
        
        this.habits.push(habit);
        this.saveHabits();
        return true;
    }

    // Delete a habit
    deleteHabit(habitId) {
        this.habits = this.habits.filter(h => h.id !== habitId);
        this.saveHabits();
    }

    // Toggle habit completion for a specific date
    toggleCompletion(habitId, date) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return;
        
        const dateStr = date.toISOString().split('T')[0];
        if (habit.completions[dateStr]) {
            delete habit.completions[dateStr];
        } else {
            habit.completions[dateStr] = true;
        }
        
        this.saveHabits();
    }

    // Check if a habit is completed on a specific date
    isCompletedOnDate(habitId, date) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return false;
        
        const dateStr = date.toISOString().split('T')[0];
        return !!habit.completions[dateStr];
    }

    // Get completion count for a habit in current period
    getWeeklyCompletions(habitId) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return 0;
        
        let count = 0;
        for (let i = 0; i < this.daysInView; i++) {
            const date = new Date(this.currentWeekStart);
            date.setDate(date.getDate() + i);
            if (this.isCompletedOnDate(habitId, date)) count++;
        }
        return count;
    }

    // Get all completions for a habit
    getTotalCompletions(habitId) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return 0;
        return Object.keys(habit.completions).length;
    }

    // Get completion rate for a habit
    getCompletionRate(habitId) {
        if (this.habits.length === 0) return 0;
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return 0;
        
        const createdAt = new Date(habit.createdAt);
        const today = new Date();
        const daysAvailable = Math.ceil((today - createdAt) / (1000 * 60 * 60 * 24)) + 1;
        const completions = this.getTotalCompletions(habitId);
        
        return Math.round((completions / daysAvailable) * 100);
    }

    // Get completion data for last N days
    getCompletionTrend(habitId, days = 7) {
        const habit = this.habits.find(h => h.id === habitId);
        if (!habit) return [];
        
        const trend = [];
        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            trend.push(this.isCompletedOnDate(habitId, date) ? 1 : 0);
        }
        return trend;
    }

    // Get statistics
    getStatistics() {
        if (this.habits.length === 0) {
            return {
                totalCompletions: 0,
                averageRate: 0,
                bestHabit: null,
                currentStreak: 0
            };
        }

        const totalCompletions = this.habits.reduce((sum, habit) => 
            sum + this.getTotalCompletions(habit.id), 0);
        
        const averageRate = Math.round(
            this.habits.reduce((sum, habit) => 
                sum + this.getCompletionRate(habit.id), 0) / this.habits.length
        );

        const bestHabit = this.habits.reduce((best, habit) => {
            const rate = this.getCompletionRate(habit.id);
            return !best || rate > this.getCompletionRate(best.id) ? habit : best;
        });

        const currentStreak = this.calculateStreak();

        return {
            totalCompletions,
            averageRate,
            bestHabit: bestHabit ? bestHabit.name : null,
            currentStreak
        };
    }

    // Calculate current streak
    calculateStreak() {
        if (this.habits.length === 0) return 0;

        let streak = 0;
        const today = new Date();
        
        for (let i = 0; i < 365; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            const allCompleted = this.habits.every(habit => 
                this.isCompletedOnDate(habit.id, date)
            );
            
            if (allCompleted) {
                streak++;
            } else {
                break;
            }
        }
        
        return streak;
    }

    // Get contribution data for last 12 weeks
    getContributionData() {
        const weeks = [];
        const today = new Date();
        
        for (let week = 11; week >= 0; week--) {
            const weekData = [];
            for (let day = 0; day < 7; day++) {
                const date = new Date(today);
                date.setDate(date.getDate() - (week * 7 + day));
                
                const completedCount = this.habits.filter(habit => 
                    this.isCompletedOnDate(habit.id, date)
                ).length;
                
                const completionRate = this.habits.length > 0 
                    ? Math.round((completedCount / this.habits.length) * 100)
                    : 0;
                
                weekData.push({
                    date: date.toISOString().split('T')[0],
                    completions: completedCount,
                    rate: completionRate
                });
            }
            weeks.push(weekData);
        }
        
        return weeks;
    }

    // Get chart data
    getChartData() {
        const habits = this.habits.slice(0, 10); // Limit to 10 habits for charts

        // Pie chart data (completion rates)
        const pieData = {
            labels: habits.map(h => h.name),
            datasets: [{
                data: habits.map(h => this.getCompletionRate(h.id)),
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
                    '#f97316', '#eab308', '#84cc16', '#22c55e',
                    '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9'
                ],
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        };

        // Line chart data (weekly trends)
        const lineData = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: habits.map((habit, index) => ({
                label: habit.name,
                data: this.getCompletionTrend(habit.id, 7),
                borderColor: pieData.datasets[0].backgroundColor[index],
                backgroundColor: pieData.datasets[0].backgroundColor[index] + '20',
                tension: 0.4,
                fill: true
            }))
        };

        // Bar chart data (total completions)
        const barData = {
            labels: habits.map(h => h.name),
            datasets: [{
                label: 'Total Completions',
                data: habits.map(h => this.getTotalCompletions(h.id)),
                backgroundColor: habits.map((_, i) => pieData.datasets[0].backgroundColor[i]),
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        };

        return { pieData, lineData, barData };
    }
}

// =====================
// UI MANAGEMENT
// =====================

const tracker = new HabitTracker();

// Initialize charts on page load
window.addEventListener('load', () => {
    initializeUserProfile();
    renderHabits();
    updateWeekDisplay();
    renderCharts();
    loadSocialPlatforms();
});

// Render habits calendar
function renderHabits() {
    // Render day headers
    const headerContainer = document.getElementById('calendar-days-header');
    headerContainer.innerHTML = '';
    
    for (let i = 0; i < tracker.daysInView; i++) {
        const date = new Date(tracker.currentWeekStart);
        date.setDate(date.getDate() + i);
        
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayDate = date.getDate();
        
        const headerCell = document.createElement('div');
        headerCell.className = 'day-header-cell';
        headerCell.innerHTML = `
            <div class="day-name">${dayName}</div>
            <div class="day-date">${dayDate}</div>
        `;
        headerContainer.appendChild(headerCell);
    }
    
    // Render habit rows
    const bodyContainer = document.getElementById('calendar-body');
    bodyContainer.innerHTML = '';
    
    if (tracker.habits.length === 0) {
        const emptyRow = document.createElement('div');
        emptyRow.style.padding = '2rem';
        emptyRow.style.textAlign = 'center';
        emptyRow.style.color = '#999';
        emptyRow.textContent = 'No habits yet. Add one to get started!';
        bodyContainer.appendChild(emptyRow);
        return;
    }
    
    tracker.habits.forEach(habit => {
        const row = document.createElement('div');
        row.className = 'habit-row';
        
        // Habit label (left side)
        const label = document.createElement('div');
        label.className = 'habit-row-label';
        label.title = `Click to edit: ${habit.name}`;
        label.onclick = () => editHabit(habit.id);
        label.innerHTML = `
            <span class="habit-name">${habit.name}</span>
        `;
        
        // Habit cells (checkboxes)
        const cellsContainer = document.createElement('div');
        cellsContainer.className = 'habit-row-cells';
        
        for (let i = 0; i < tracker.daysInView; i++) {
            const date = new Date(tracker.currentWeekStart);
            date.setDate(date.getDate() + i);
            const dateStr = date.toISOString().split('T')[0];
            const isCompleted = tracker.isCompletedOnDate(habit.id, date);
            
            const cell = document.createElement('div');
            cell.className = 'habit-cell';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.dataset.habitId = habit.id;
            checkbox.dataset.date = dateStr;
            checkbox.checked = isCompleted;
            
            checkbox.addEventListener('change', (e) => {
                const habitId = parseInt(e.target.dataset.habitId);
                const date = new Date(e.target.dataset.date);
                tracker.toggleCompletion(habitId, date);
                renderHabits();
            });
            
            cell.appendChild(checkbox);
            cellsContainer.appendChild(cell);
        }
        
        // Action buttons (right side)
        const actions = document.createElement('div');
        actions.className = 'habit-row-actions';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'habit-action-btn';
        editBtn.textContent = '✎';
        editBtn.title = 'Edit';
        editBtn.onclick = () => editHabit(habit.id);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'habit-action-btn delete';
        deleteBtn.textContent = '✕';
        deleteBtn.title = 'Delete';
        deleteBtn.onclick = () => {
            if (confirm(`Delete "${habit.name}"?`)) {
                tracker.deleteHabit(habit.id);
                renderHabits();
            }
        };
        
        actions.appendChild(editBtn);
        actions.appendChild(deleteBtn);
        
        row.appendChild(label);
        row.appendChild(cellsContainer);
        row.appendChild(actions);
        bodyContainer.appendChild(row);
    });
}

// Update week display
function updateWeekDisplay() {
    const start = tracker.currentWeekStart;
    const end = tracker.getWeekEnd(start);
    
    const options = { month: 'short', day: 'numeric' };
    const startStr = start.toLocaleDateString('en-US', options);
    const endStr = end.toLocaleDateString('en-US', options);
    
    document.getElementById('week-display').textContent = `${startStr} - ${endStr}`;
}

// Add habit
document.getElementById('add-habit-btn').addEventListener('click', () => {
    const input = document.getElementById('habit-input');
    if (tracker.addHabit(input.value)) {
        input.value = '';
        renderHabits();
    }
});

document.getElementById('habit-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('add-habit-btn').click();
    }
});

// Week navigation
document.getElementById('prev-week').addEventListener('click', () => {
    tracker.currentWeekStart.setDate(tracker.currentWeekStart.getDate() - tracker.daysInView);
    updateWeekDisplay();
    renderHabits();
});

document.getElementById('next-week').addEventListener('click', () => {
    tracker.currentWeekStart.setDate(tracker.currentWeekStart.getDate() + tracker.daysInView);
    updateWeekDisplay();
    renderHabits();
});

// Modal management
let editingHabitId = null;
const modal = document.getElementById('edit-modal');
const closeBtn = document.querySelector('.close');

function editHabit(habitId) {
    editingHabitId = habitId;
    const habit = tracker.habits.find(h => h.id === habitId);
    if (habit) {
        document.getElementById('edit-habit-input').value = habit.name;
        modal.classList.add('active');
    }
}

closeBtn.addEventListener('click', () => {
    modal.classList.remove('active');
});

document.getElementById('cancel-habit-btn').addEventListener('click', () => {
    modal.classList.remove('active');
});

document.getElementById('save-habit-btn').addEventListener('click', () => {
    const newName = document.getElementById('edit-habit-input').value;
    if (newName.trim()) {
        const habit = tracker.habits.find(h => h.id === editingHabitId);
        if (habit) {
            habit.name = newName.trim();
            tracker.saveHabits();
            renderHabits();
            modal.classList.remove('active');
        }
    }
});

document.getElementById('delete-habit-btn').addEventListener('click', () => {
    if (confirm('Are you sure you want to delete this habit?')) {
        tracker.deleteHabit(editingHabitId);
        renderHabits();
        modal.classList.remove('active');
    }
});

// Render charts
function renderCharts() {
    const { pieData, lineData, barData } = tracker.getChartData();

    // Destroy existing charts
    Object.values(tracker.chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        }
    };

    // Pie Chart
    const pieCtx = document.getElementById('pie-chart');
    if (pieCtx) {
        tracker.chartInstances.pie = new Chart(pieCtx, {
            type: 'doughnut',
            data: pieData,
            options: chartOptions
        });
    }

    // Line Chart
    const lineCtx = document.getElementById('line-chart');
    if (lineCtx) {
        tracker.chartInstances.line = new Chart(lineCtx, {
            type: 'line',
            data: lineData,
            options: {
                ...chartOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }

    // Bar Chart
    const barCtx = document.getElementById('bar-chart');
    if (barCtx) {
        tracker.chartInstances.bar = new Chart(barCtx, {
            type: 'bar',
            data: barData,
            options: chartOptions
        });
    }

    // Contribution table
    renderContributionTable();

    // Statistics
    const stats = tracker.getStatistics();
    document.getElementById('total-completions').textContent = stats.totalCompletions;
    document.getElementById('avg-completion').textContent = stats.averageRate + '%';
    document.getElementById('best-habit').textContent = stats.bestHabit || '-';
    document.getElementById('current-streak').textContent = stats.currentStreak;
}

// Render contribution table
function renderContributionTable() {
    const container = document.getElementById('contribution-table');
    container.innerHTML = '';

    const weeks = tracker.getContributionData();
    
    // Create header with day labels
    const header = document.createElement('div');
    header.style.marginBottom = '1rem';
    header.innerHTML = '<strong>Last 12 Weeks Activity:</strong>';
    container.appendChild(header);

    // Create grid
    const grid = document.createElement('div');
    grid.className = 'contribution-grid';

    weeks.forEach((weekDays) => {
        weekDays.forEach(day => {
            const cell = document.createElement('div');
            cell.className = 'contribution-cell';
            
            // Determine level based on completion rate
            let level = 0;
            if (day.rate > 0) level = 1;
            if (day.rate > 25) level = 2;
            if (day.rate > 50) level = 3;
            if (day.rate > 75) level = 4;
            
            cell.classList.add(`level-${level}`);
            cell.textContent = '';
            cell.title = `${day.date}: ${day.completions} completions (${day.rate}%)`;
            
            grid.appendChild(cell);
        });
    });

    container.appendChild(grid);
}

// =====================
// SOCIAL SHARING
// =====================

async function loadSocialPlatforms() {
    try {
        const response = await fetch(`${API_BASE_URL}/social/platforms`);
        const platforms = await response.json();
        
        const platformsContainer = document.getElementById('social-platforms');
        platformsContainer.innerHTML = '';
        
        platforms.forEach(platform => {
            const button = document.createElement('button');
            button.className = `social-btn ${platform.id}`;
            button.innerHTML = `
                <span class="social-btn-icon">${platform.icon}</span>
                <span>${platform.name}</span>
            `;
            
            button.addEventListener('click', () => shareHabit(platform.id));
            platformsContainer.appendChild(button);
        });
    } catch (error) {
        console.error('Error loading social platforms:', error);
    }
}

function shareHabit(platform) {
    // Get best habit
    const stats = tracker.getStatistics();
    
    if (!stats.bestHabit) {
        alert('No habits to share yet. Create a habit first!');
        return;
    }
    
    // Find the best habit object
    const bestHabit = tracker.habits.find(h => h.name === stats.bestHabit);
    if (!bestHabit) return;
    
    // For now, generate share message directly
    const completionData = {
        completion_rate: tracker.getCompletionRate(bestHabit.id),
        total_completions: tracker.getTotalCompletions(bestHabit.id)
    };
    
    const messages = {
        'twitter': `I just tracked "${bestHabit.name}"! 🎯 ${completionData.completion_rate}% completion rate on #HabitTrack`,
        'facebook': `Tracking my progress on '${bestHabit.name}' using #HabitTrack! Currently at ${completionData.completion_rate}% completion rate. Building better habits! 💪`,
        'linkedin': `I'm building better habits with #HabitTrack! Currently tracking '${bestHabit.name}' with a ${completionData.completion_rate}% completion rate. Consistency is key! 📈`,
        'reddit': `Just tracked '${bestHabit.name}' using HabitTrack! ${completionData.total_completions} completions and ${completionData.completion_rate}% completion rate. Great app for habit tracking! 🎯`,
        'whatsapp': `Check out my habit tracking! '${bestHabit.name}': ${completionData.completion_rate}% completion rate 📊 #HabitTrack`,
        'telegram': `📊 Habit Update: ${bestHabit.name}\\nCompletion Rate: ${completionData.completion_rate}%\\nTotal: ${completionData.total_completions}\\n#HabitTrack`
    };
    
    const message = messages[platform] || `Tracking '${bestHabit.name}' on #HabitTrack`;
    const urls = {
        'twitter': `https://twitter.com/intent/tweet?text=${encodeURIComponent(message)}`,
        'facebook': `https://www.facebook.com/sharer/sharer.php?quote=${encodeURIComponent(message)}`,
        'linkedin': `https://www.linkedin.com/sharing/share-offsite/?url=${window.location.href}`,
        'reddit': `https://reddit.com/submit?title=${encodeURIComponent(bestHabit.name)}&text=${encodeURIComponent(message)}`,
        'whatsapp': `https://wa.me/?text=${encodeURIComponent(message)}`,
        'telegram': `https://t.me/share/url?url=${window.location.href}&text=${encodeURIComponent(message)}`
    };
    
    if (urls[platform]) {
        window.open(urls[platform], '_blank', 'width=600,height=400');
    }
}

// Initialize app
updateWeekDisplay();
renderHabits();
