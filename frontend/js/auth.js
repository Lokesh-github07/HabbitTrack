const API_BASE_URL = '/api';
const REDIRECT_PATH = '/';

function getElementValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

function showAlert(message, type = 'error') {
    const container = document.getElementById('alert-container');
    if (!container) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    container.innerHTML = '';
    container.appendChild(alertDiv);

    if (type === 'success') {
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

function setButtonState(button, isLoading, loadingText, idleText) {
    if (!button) return;
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingText : idleText;
}

async function authenticate(endpoint, payload, button, loadingText, idleText) {
    setButtonState(button, true, loadingText, idleText);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            localStorage.setItem('user', JSON.stringify(data.user));
            showAlert(endpoint === 'login' ? 'Login successful! Redirecting...' : 'Registration successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = REDIRECT_PATH;
            }, 900);
            return;
        }

        showAlert(data.error || `${endpoint === 'login' ? 'Login' : 'Registration'} failed`, 'error');
    } catch (error) {
        console.error('Auth error:', error);
        showAlert('Connection error. Please try again.', 'error');
    } finally {
        setButtonState(button, false, loadingText, idleText);
    }
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const button = loginForm.querySelector('button[type="submit"]');
        const email = getElementValue('email').trim();
        const password = getElementValue('password');
        const remember = document.getElementById('remember')?.checked || false;

        if (!email || !password) {
            showAlert('Please fill in all fields', 'error');
            return;
        }

        await authenticate('login', { email, password, remember }, button, 'Signing in...', 'Sign In');
    });
}

const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const button = registerForm.querySelector('button[type="submit"]');
        const formData = {
            username: getElementValue('username').trim(),
            email: getElementValue('email').trim(),
            password: getElementValue('password'),
            first_name: getElementValue('first-name').trim(),
            last_name: getElementValue('last-name').trim()
        };

        if (!formData.username || !formData.email || !formData.password) {
            showAlert('Please fill in all required fields', 'error');
            return;
        }

        if (formData.password.length < 8) {
            showAlert('Password must be at least 8 characters', 'error');
            return;
        }

        const confirmPassword = getElementValue('confirm-password');
        if (formData.password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            return;
        }

        if (!document.getElementById('terms')?.checked) {
            showAlert('You must agree to the Terms of Service', 'error');
            return;
        }

        await authenticate('register', formData, button, 'Creating account...', 'Create Account');
    });
}

const googleLoginBtn = document.getElementById('google-login');
if (googleLoginBtn) {
    googleLoginBtn.addEventListener('click', () => {
        window.location.href = `${API_BASE_URL}/auth/google`;
    });
}

const googleSignupBtn = document.getElementById('google-signup');
if (googleSignupBtn) {
    googleSignupBtn.addEventListener('click', () => {
        window.location.href = `${API_BASE_URL}/auth/google`;
    });
}

window.addEventListener('load', () => {
    const user = localStorage.getItem('user');
    if (user && (window.location.pathname.includes('login') || window.location.pathname.includes('register'))) {
        window.location.href = REDIRECT_PATH;
    }
});
