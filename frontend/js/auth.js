const API_BASE_URL = 'http://localhost:5000/api';

// Show alert message
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

// Handle login form
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const button = loginForm.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = 'Signing in...';
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        // Validation
        if (!email || !password) {
            showAlert('Please fill in all fields', 'error');
            button.disabled = false;
            button.textContent = 'Sign In';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    email,
                    password,
                    remember
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('user', JSON.stringify(data.user));
                showAlert('Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = '/index.html';
                }, 1500);
            } else {
                showAlert(data.error || 'Login failed', 'error');
                button.disabled = false;
                button.textContent = 'Sign In';
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Connection error. Please try again.', 'error');
            button.disabled = false;
            button.textContent = 'Sign In';
        }
    });
}

// Handle registration form
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const button = registerForm.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = 'Creating Account...';
        
        const formData = {
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value,
            first_name: document.getElementById('first-name').value.trim(),
            last_name: document.getElementById('last-name').value.trim()
        };
        
        // Validation
        if (!formData.username || !formData.email || !formData.password) {
            showAlert('Please fill in all required fields', 'error');
            button.disabled = false;
            button.textContent = 'Create Account';
            return;
        }
        
        if (formData.password.length < 8) {
            showAlert('Password must be at least 8 characters', 'error');
            button.disabled = false;
            button.textContent = 'Create Account';
            return;
        }
        
        const confirmPassword = document.getElementById('confirm-password').value;
        if (formData.password !== confirmPassword) {
            showAlert('Passwords do not match', 'error');
            button.disabled = false;
            button.textContent = 'Create Account';
            return;
        }
        
        if (!document.getElementById('terms').checked) {
            showAlert('You must agree to the Terms of Service', 'error');
            button.disabled = false;
            button.textContent = 'Create Account';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                localStorage.setItem('user', JSON.stringify(data.user));
                showAlert('Registration successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = '/index.html';
                }, 1500);
            } else {
                showAlert(data.error || 'Registration failed', 'error');
                button.disabled = false;
                button.textContent = 'Create Account';
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Connection error. Please try again.', 'error');
            button.disabled = false;
            button.textContent = 'Create Account';
        }
    });
}

// Google login handler
const googleLoginBtn = document.getElementById('google-login');
if (googleLoginBtn) {
    googleLoginBtn.addEventListener('click', () => {
        window.location.href = `${API_BASE_URL}/auth/google`;
    });
}

// Google signup handler
const googleSignupBtn = document.getElementById('google-signup');
if (googleSignupBtn) {
    googleSignupBtn.addEventListener('click', () => {
        window.location.href = `${API_BASE_URL}/auth/google`;
    });
}
            }
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred. Please try again.');
        }
    });
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.classList.add('visible');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.display = 'none';
            errorDiv.classList.remove('visible');
        }, 5000);
    }
}

// Show success message
function showSuccess(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.className = 'success-message visible';
    }
}

// Check if user is already logged in
window.addEventListener('load', () => {
    const user = localStorage.getItem('user');
    if (user && (window.location.pathname.includes('login') || window.location.pathname.includes('register'))) {
        window.location.href = '/dashboard.html';
    }
});
