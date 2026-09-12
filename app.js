const API = '/api';
const $ = id => document.getElementById(id);
const monday = date => {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    return d;
};
let habits = [], tasks = [], weekStart = monday(new Date()), chart;
const iso = date => new Date(date).toISOString().slice(0,10);
const esc = text => { const e = document.createElement('span'); e.textContent = text; return e.innerHTML; };
async function api(path, options = {}) {
    const res = await fetch(API + path, {
        credentials: 'include',
        ...options,
        headers: {
            ...(options.body ? {'Content-Type': 'application/json'} : {}),
            ...(options.headers || {})
        }
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || data.message || 'Something went wrong.');
    return data;
}
function alertBox(id, text, type='error') { const el=$(id); el.innerHTML=`<div class="alert alert-${type}">${esc(text)}</div>`; setTimeout(()=>el.innerHTML='',4500); }
function setUser(user) { localStorage.setItem('user',JSON.stringify(user)); $('user-name').textContent=user.first_name||user.username||'User'; $('user-email').textContent=user.email||''; $('user-avatar').textContent=(user.first_name||user.username||'U')[0].toUpperCase(); [['username','username'],['email','email'],['first-name','first_name'],['last-name','last_name']].forEach(([id,key])=>{if($('profile-'+id)) $('profile-'+id).value=user[key]||'';}); }
function auth(mode) { $('login-modal').classList.toggle('active',mode==='login'); $('register-modal').classList.toggle('active',mode==='register'); }
function page(name) { document.querySelectorAll('.page-section').forEach(el=>el.classList.toggle('active',el.id===name+'-section')); document.querySelectorAll('.nav-link').forEach(el=>el.classList.toggle('active',el.id===name+'-link')); renderAll(); }
async function refresh() { [habits,tasks]=await Promise.all([api('/habits'),api('/tasks')]); renderAll(); }
const completed = (habit,date) => (habit.completions||[]).some(x=>x.date===date&&x.completed);
function streak(habit) { let count=0; for(let i=0;i<366;i++){const d=new Date();d.setDate(d.getDate()-i);if(!completed(habit,iso(d)))break;count++;}return count; }
function weekDates() { return Array.from({length:7},(_,i)=>{const d=new Date(weekStart);d.setDate(d.getDate()+i);return d;}); }
function renderHabits() { const dates=weekDates(), body=$('calendar-body'); $('calendar-days-header').innerHTML=dates.map(d=>`<div class="calendar-day-header"><span>${d.toLocaleDateString('en-US',{weekday:'short'})}</span><span>${d.getDate()}</span></div>`).join(''); $('week-display').textContent=`Week of ${weekStart.toLocaleDateString('en-US',{month:'short',day:'numeric'})} – ${dates[6].toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}`; if(!habits.length){body.innerHTML='<div class="empty-state">No habits yet. Add one to get started!</div>';return;} body.innerHTML=habits.map(h=>`<div class="habit-row"><div class="habit-label"><span class="habit-name">${esc(h.name)}</span><div class="habit-stats"><span class="stat">🔥 ${streak(h)}</span></div><button class="btn-delete" data-delete-habit="${h.id}">×</button></div><div class="habit-checkboxes">${dates.map(d=>`<label class="checkbox-label"><input class="habit-checkbox" data-habit="${h.id}" data-date="${iso(d)}" type="checkbox" ${completed(h,iso(d))?'checked':''}></label>`).join('')}</div></div>`).join(''); }
function due(date) { if(!date)return 'No due date';if(date===iso(new Date()))return 'Today';return new Date(date+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'}); }
function renderTasks() { const target=$('tasks-list'); if(!tasks.length){target.innerHTML='<div class="empty-state">No tasks yet. Add one to get started!</div>';return;} target.innerHTML=tasks.map(t=>`<div class="task-row ${t.completed?'done':''}"><input type="checkbox" data-task="${t.id}" ${t.completed?'checked':''}><span class="task-text">${esc(t.title)}</span><span class="task-due">${due(t.due_date)}</span><button class="btn-delete" data-delete-task="${t.id}">×</button></div>`).join(''); }
function dashRows(items,kind,today) { if(!items.length)return `<div class="dash-empty"><div class="dash-empty-title">${kind==='task'?'No tasks for today 🎉':'No habits scheduled'}</div><div class="dash-empty-sub">${kind==='task'?'Plan one small thing — momentum starts there.':'Create one habit you can repeat daily.'}</div></div>`;return items.map(x=>`<div class="dash-list-row"><label><input type="checkbox" ${kind==='task'?`data-task="${x.id}" ${x.completed?'checked':''}`:`data-habit="${x.id}" data-date="${today}" ${completed(x,today)?'checked':''}`}> ${esc(kind==='task'?x.title:x.name)}</label><span>${kind==='task'?due(x.due_date):streak(x)+' day streak'}</span></div>`).join(''); }
function renderDashboard() { const today=iso(new Date()), todayTasks=tasks.filter(t=>t.due_date===today), finishedTasks=todayTasks.filter(t=>t.completed).length, finishedHabits=habits.filter(h=>completed(h,today)).length,total=todayTasks.length+habits.length,done=finishedTasks+finishedHabits,pct=total?Math.round(done/total*100):0,overdue=tasks.filter(t=>!t.completed&&t.due_date&&t.due_date<today).length; $('progress-ring').style.setProperty('--pct',pct); $('progress-pct').textContent=pct+'%';$('progress-pct-sub').textContent=`${done}/${total} done`;$('progress-tasks').textContent=`${finishedTasks}/${todayTasks.length}`;$('progress-habits').textContent=`${finishedHabits}/${habits.length}`;$('progress-overdue').textContent=overdue;$('stat-overdue-tasks').textContent=overdue;$('stat-overdue-sub').textContent=overdue?'A small next step can clear the list.':'Nothing overdue. Nice work.';$('stat-progress-score').textContent=pct;const scores=habits.map(streak);$('stat-current-streak').innerHTML=`${scores.length?Math.min(...scores):0} <span class="unit">days</span>`;$('stat-best-streak').innerHTML=`${scores.length?Math.max(...scores):0} <span class="unit">days</span>`;$('today-tasks-body').innerHTML=dashRows(todayTasks,'task',today);$('today-habits-body').innerHTML=dashRows(habits,'habit',today);const next=tasks.filter(t=>!t.completed&&t.due_date&&t.due_date>today).slice(0,5);$('upcoming-body').innerHTML=next.length?next.map(t=>`<div class="dash-list-row"><span>${esc(t.title)}</span><span>${due(t.due_date)}</span></div>`).join(''):'<div class="dash-empty"><div class="dash-empty-title">Nothing scheduled ahead</div><div class="dash-empty-sub">Plan your week when you’re ready.</div></div>'; renderChart(); }
function renderChart(){if(!window.Chart)return;const dates=weekDates(),values=dates.map(d=>{const day=iso(d),total=habits.length+tasks.filter(t=>t.due_date===day).length,done=habits.filter(h=>completed(h,day)).length+tasks.filter(t=>t.due_date===day&&t.completed).length;return total?Math.round(done/total*100):0;});if(chart)chart.destroy();chart=new Chart($('weekly-productivity-chart'),{type:'bar',data:{labels:dates.map(d=>d.toLocaleDateString('en-US',{weekday:'short'})),datasets:[{data:values,backgroundColor:'#6658e8',borderRadius:7}]},options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100,ticks:{callback:v=>v+'%'}},x:{grid:{display:false}}}}});}
function renderAll(){renderHabits();renderTasks();renderDashboard();}
async function addHabit(){const name=$('habit-input').value.trim();if(!name)return $('habit-input').focus();try{const data=await api('/habits',{method:'POST',body:JSON.stringify({name})});habits.push(data.habit);$('habit-input').value='';renderAll();}catch(e){alert(e.message);}}
async function addTask(){const title=$('task-input').value.trim();if(!title)return $('task-input').focus();try{const data=await api('/tasks',{method:'POST',body:JSON.stringify({title,due_date:$('task-date-input').value||null})});tasks.push(data.task);$('task-input').value='';$('task-date-input').value='';renderAll();}catch(e){alert(e.message);}}
async function toggleHabit(id,date){try{const data=await api('/habits/'+id+'/toggle',{method:'POST',body:JSON.stringify({date})}),h=habits.find(h=>h.id===id),i=(h.completions||[]).findIndex(c=>c.date===date);if(i>=0)h.completions.splice(i,1);if(data.completion.completed)h.completions.push(data.completion);renderAll();}catch(e){alert(e.message);refresh();}}
async function toggleTask(id,checked){try{const data=await api('/tasks/'+id,{method:'PUT',body:JSON.stringify({completed:checked})}),i=tasks.findIndex(t=>t.id===id);tasks[i]=data.task;renderAll();}catch(e){alert(e.message);refresh();}}
async function deleteItem(type,id){if(!confirm('Delete this '+type+'?'))return;try{await api('/'+type+'s/'+id,{method:'DELETE'});if(type==='habit')habits=habits.filter(h=>h.id!==id);else tasks=tasks.filter(t=>t.id!==id);renderAll();}catch(e){alert(e.message);}}
function bind() {
    const safeOn = (id, event, handler) => {
        const el = $(id);
        if (el) el.addEventListener(event, handler);
    };

    safeOn('signup-link', 'click', e => {
        e.preventDefault();
        auth('register');
    });

    safeOn('signin-link', 'click', e => {
        e.preventDefault();
        auth('login');
    });

    safeOn('forgot-password-link', 'click', async e => {
        e.preventDefault();
        const email = prompt('Enter your account email address:');
        if (!email) return;

        try {
            const data = await api('/auth/forgot-password', {
                method: 'POST',
                body: JSON.stringify({email: email.trim()})
            });

            // In development the API returns a reset token so the flow can be
            // tested without an email provider. Production should email it.
            if (data.reset_token) {
                const password = prompt('Enter your new password (minimum 8 characters):');
                if (!password) return;
                const confirmPassword = prompt('Confirm your new password:');
                if (password !== confirmPassword) {
                    alert('Passwords do not match.');
                    return;
                }
                await api('/auth/reset-password', {
                    method: 'POST',
                    body: JSON.stringify({token: data.reset_token, password})
                });
                alert('Password reset successfully. You can now sign in.');
            } else {
                alert(data.message || 'If the account exists, a reset link has been sent.');
            }
        } catch (error) {
            alert(error.message);
        }
    });

    const loginForm = $('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async e => {
            e.preventDefault();
            const email = $('login-email').value.trim();
            const password = $('login-password').value;
            const remember = $('login-remember').checked;
            if (!email || !password) {
                alertBox('login-alert-container', 'Please enter your email and password.');
                return;
            }
            const button = loginForm.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            try {
                button.disabled = true;
                button.textContent = 'Signing in...';
                const data = await api('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify({email, password, remember})
                });
                setUser(data.user);
                auth();
                await refresh();
            } catch (error) {
                console.error('Login error:', error);
                alertBox('login-alert-container', error.message || 'Unable to sign in.');
            } finally {
                button.disabled = false;
                button.textContent = originalText;
            }
        });
    }

    const registerForm = $('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async e => {
            e.preventDefault();
            const firstName = $('first-name').value.trim();
            const lastName = $('last-name').value.trim();
            const username = $('username').value.trim();
            const email = $('register-email').value.trim();
            const password = $('register-password').value;
            const confirmPassword = $('confirm-password').value;

            if (password.length < 8) {
                alertBox('register-alert-container', 'Password must be at least 8 characters.');
                return;
            }
            if (password !== confirmPassword) {
                alertBox('register-alert-container', 'Passwords do not match.');
                return;
            }
            if (!$('terms').checked) {
                alertBox('register-alert-container', 'Please accept the Terms of Service.');
                return;
            }

            const button = registerForm.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            try {
                button.disabled = true;
                button.textContent = 'Creating account...';
                const data = await api('/auth/register', {
                    method: 'POST',
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        username,
                        email,
                        password
                    })
                });
                setUser(data.user);
                auth();
                await refresh();
            } catch (error) {
                console.error('Registration error:', error);
                alertBox('register-alert-container', error.message || 'Unable to create account.');
            } finally {
                button.disabled = false;
                button.textContent = originalText;
            }
        });
    }

    ['google-login', 'google-signup'].forEach(id => {
        safeOn(id, 'click', () => {
            window.location.href = API + '/auth/google';
        });
    });

    ['dashboard', 'tasks', 'habits'].forEach(name => {
        safeOn(name + '-link', 'click', () => page(name));
    });

    safeOn('account-footer-btn', 'click', e => {
        if (!e.target.closest('#logout-btn')) page('profile');
    });

    safeOn('logout-btn', 'click', async e => {
        e.stopPropagation();
        try {
            await api('/auth/logout', {method: 'POST'});
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('user');
            auth('login');
        }
    });

    safeOn('add-habit-btn', 'click', addHabit);
    safeOn('add-task-btn', 'click', addTask);
    safeOn('habit-input', 'keydown', e => { if (e.key === 'Enter') addHabit(); });
    safeOn('task-input', 'keydown', e => { if (e.key === 'Enter') addTask(); });
    safeOn('quick-add-btn', 'click', () => { page('tasks'); $('task-input').focus(); });
    safeOn('dash-add-task-btn', 'click', () => { page('tasks'); $('task-input').focus(); });
    safeOn('dash-add-habit-btn', 'click', () => { page('habits'); $('habit-input').focus(); });
    safeOn('upcoming-view-all', 'click', () => page('tasks'));
    safeOn('prev-week', 'click', () => { weekStart.setDate(weekStart.getDate() - 7); renderAll(); });
    safeOn('next-week', 'click', () => { weekStart.setDate(weekStart.getDate() + 7); renderAll(); });

    document.addEventListener('change', e => {
        if (e.target.dataset.habit) toggleHabit(e.target.dataset.habit, e.target.dataset.date);
        if (e.target.dataset.task) toggleTask(e.target.dataset.task, e.target.checked);
    });

    document.addEventListener('click', e => {
        if (e.target.dataset.deleteHabit) deleteItem('habit', e.target.dataset.deleteHabit);
        if (e.target.dataset.deleteTask) deleteItem('task', e.target.dataset.deleteTask);
    });

    document.querySelectorAll('.theme-toggle').forEach(button => {
        button.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('habittrack_dark', document.body.classList.contains('dark-mode'));
        });
    });

    safeOn('back-to-dashboard-btn', 'click', () => page('dashboard'));

    safeOn('profile-form', 'submit', async e => {
        e.preventDefault();
        try {
            const data = await api('/auth/profile', {
                method: 'PUT',
                body: JSON.stringify({
                    username: $('profile-username').value.trim(),
                    email: $('profile-email').value.trim(),
                    first_name: $('profile-first-name').value.trim(),
                    last_name: $('profile-last-name').value.trim(),
                    password: $('profile-password').value
                })
            });
            $('profile-password').value = '';
            setUser(data.user);
            $('profile-status').textContent = 'Profile updated successfully.';
            $('profile-status').className = 'status-message success';
        } catch (error) {
            $('profile-status').textContent = error.message;
            $('profile-status').className = 'status-message error';
        }
    });
}

document.addEventListener('DOMContentLoaded',async()=>{bind();if(localStorage.getItem('habittrack_dark')==='true')document.documentElement.dataset.theme='dark';try{const user=await api('/auth/current-user');setUser(user);auth();await refresh();}catch{localStorage.removeItem('user');auth('login');}});
