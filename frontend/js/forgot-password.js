const API_BASE_URL = '/api';
const OTP_LENGTH = 6;
const OTP_DURATION_SECONDS = 10 * 60;

let currentEmail = '';
let resetToken = '';
let otpTimerInterval = null;
let otpSecondsLeft = OTP_DURATION_SECONDS;

// ---------- helpers ----------

function showAlert(message, type = 'error') {
    const container = document.getElementById('alert-container');
    if (!container) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    container.innerHTML = '';
    container.appendChild(alertDiv);

    if (type === 'success') {
        setTimeout(() => alertDiv.remove(), 4000);
    }
}

function clearAlert() {
    const container = document.getElementById('alert-container');
    if (container) container.innerHTML = '';
}

function setButtonState(button, isLoading, loadingText, idleText) {
    if (!button) return;
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingText : idleText;
}

async function postJSON(endpoint, payload) {
    const response = await fetch(`${API_BASE_URL}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, status: response.status, data };
}

function goToStep(stepNumber) {
    document.querySelectorAll('.auth-step').forEach((el) => el.classList.remove('active'));
    document.getElementById(`step-${stepNumber}`).classList.add('active');

    // Update the 1-2-3 indicator (steps 1-3 only; step 4 is the success screen).
    const indicator = document.getElementById('step-indicator');
    if (stepNumber <= 3) {
        indicator.style.display = 'flex';
        document.querySelectorAll('.step-dot').forEach((dot) => {
            const dotStep = Number(dot.dataset.step);
            dot.classList.toggle('active', dotStep === stepNumber);
            dot.classList.toggle('done', dotStep < stepNumber);
            dot.textContent = dotStep < stepNumber ? '✓' : dotStep;
        });
        document.querySelectorAll('.step-line').forEach((line) => {
            line.classList.toggle('done', Number(line.dataset.line) < stepNumber);
        });
    } else {
        indicator.style.display = 'none';
        document.getElementById('auth-footer').style.display = 'none';
    }

    clearAlert();
}

// ---------- Step 1: request OTP ----------

const requestOtpForm = document.getElementById('request-otp-form');
requestOtpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const button = requestOtpForm.querySelector('button[type="submit"]');
    const email = document.getElementById('email').value.trim();

    if (!email) {
        showAlert('Please enter your email address');
        return;
    }

    setButtonState(button, true, 'Sending code...', 'Send Verification Code');
    try {
        const { ok, data } = await postJSON('forgot-password', { email });
        if (!ok) {
            showAlert(data.error || 'Something went wrong. Please try again.');
            return;
        }

        currentEmail = email;
        document.getElementById('otp-email-display').textContent = email;
        showAlert(data.message || 'A verification code has been sent.', 'success');

        // Dev convenience: backend echoes the OTP when running on localhost
        // since no email provider is wired up yet.
        if (data.otp) {
            console.info(`[dev only] Your verification code is: ${data.otp}`);
            showAlert(`Dev mode — your code is ${data.otp} (an email provider isn't configured yet).`, 'success');
        }

        goToStep(2);
        startOtpTimer();
        clearOtpBoxes();
        focusOtpBox(0);
    } catch (error) {
        console.error('Forgot password error:', error);
        showAlert('Connection error. Please try again.');
    } finally {
        setButtonState(button, false, 'Sending code...', 'Send Verification Code');
    }
});

document.getElementById('back-to-step-1').addEventListener('click', () => {
    stopOtpTimer();
    goToStep(1);
});

// ---------- Step 2: OTP input boxes ----------

const otpBoxes = Array.from(document.querySelectorAll('.otp-box'));

function clearOtpBoxes() {
    otpBoxes.forEach((box) => (box.value = ''));
}

function focusOtpBox(index) {
    if (otpBoxes[index]) otpBoxes[index].focus();
}

function getOtpValue() {
    return otpBoxes.map((box) => box.value).join('');
}

otpBoxes.forEach((box, index) => {
    box.addEventListener('input', () => {
        box.value = box.value.replace(/[^0-9]/g, '').slice(0, 1);
        if (box.value && index < otpBoxes.length - 1) {
            focusOtpBox(index + 1);
        }
    });

    box.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !box.value && index > 0) {
            focusOtpBox(index - 1);
        }
    });

    box.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData.getData('text') || '').replace(/[^0-9]/g, '').slice(0, OTP_LENGTH);
        pasted.split('').forEach((digit, i) => {
            if (otpBoxes[i]) otpBoxes[i].value = digit;
        });
        focusOtpBox(Math.min(pasted.length, OTP_LENGTH - 1));
    });
});

function startOtpTimer() {
    stopOtpTimer();
    otpSecondsLeft = OTP_DURATION_SECONDS;
    const resendBtn = document.getElementById('resend-otp-btn');
    resendBtn.disabled = true;
    updateOtpTimerDisplay();

    otpTimerInterval = setInterval(() => {
        otpSecondsLeft -= 1;
        updateOtpTimerDisplay();
        if (otpSecondsLeft <= 0) {
            stopOtpTimer();
            resendBtn.disabled = false;
            document.getElementById('otp-timer').textContent = 'expired';
        }
    }, 1000);
}

function stopOtpTimer() {
    if (otpTimerInterval) {
        clearInterval(otpTimerInterval);
        otpTimerInterval = null;
    }
}

function updateOtpTimerDisplay() {
    const minutes = Math.floor(otpSecondsLeft / 60).toString().padStart(2, '0');
    const seconds = (otpSecondsLeft % 60).toString().padStart(2, '0');
    document.getElementById('otp-timer').textContent = `${minutes}:${seconds}`;
}

document.getElementById('resend-otp-btn').addEventListener('click', async () => {
    const resendBtn = document.getElementById('resend-otp-btn');
    resendBtn.disabled = true;
    try {
        const { ok, data } = await postJSON('resend-otp', { email: currentEmail });
        if (!ok) {
            showAlert(data.error || 'Could not resend code. Please try again.');
            resendBtn.disabled = false;
            return;
        }
        showAlert(data.message || 'A new code has been sent.', 'success');
        if (data.otp) {
            console.info(`[dev only] Your new verification code is: ${data.otp}`);
            showAlert(`Dev mode — your new code is ${data.otp}.`, 'success');
        }
        clearOtpBoxes();
        focusOtpBox(0);
        startOtpTimer();
    } catch (error) {
        console.error('Resend OTP error:', error);
        showAlert('Connection error. Please try again.');
        resendBtn.disabled = false;
    }
});

const verifyOtpForm = document.getElementById('verify-otp-form');
verifyOtpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const button = verifyOtpForm.querySelector('button[type="submit"]');
    const otp = getOtpValue();

    if (otp.length !== OTP_LENGTH) {
        showAlert('Please enter the full 6-digit code');
        return;
    }

    setButtonState(button, true, 'Verifying...', 'Verify Code');
    try {
        const { ok, data } = await postJSON('verify-otp', { email: currentEmail, otp });
        if (!ok) {
            showAlert(data.error || 'Invalid or expired code.');
            clearOtpBoxes();
            focusOtpBox(0);
            return;
        }

        resetToken = data.reset_token;
        stopOtpTimer();
        showAlert('Code verified!', 'success');
        goToStep(3);
    } catch (error) {
        console.error('Verify OTP error:', error);
        showAlert('Connection error. Please try again.');
    } finally {
        setButtonState(button, false, 'Verifying...', 'Verify Code');
    }
});

// ---------- Step 3: set new password ----------

const passwordInput = document.getElementById('new-password');
const strengthBar = document.getElementById('password-strength');

passwordInput.addEventListener('input', () => {
    const value = passwordInput.value;
    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;

    strengthBar.className = 'password-strength';
    if (value.length === 0) {
        // no class - all bars neutral
    } else if (score <= 1) {
        strengthBar.classList.add('weak');
    } else if (score <= 3) {
        strengthBar.classList.add('medium');
    } else {
        strengthBar.classList.add('strong');
    }
});

const resetPasswordForm = document.getElementById('reset-password-form');
resetPasswordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const button = resetPasswordForm.querySelector('button[type="submit"]');
    const password = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-new-password').value;

    if (password.length < 8) {
        showAlert('Password must be at least 8 characters');
        return;
    }
    if (password !== confirmPassword) {
        showAlert('Passwords do not match');
        return;
    }
    if (!resetToken) {
        showAlert('Your session expired. Please start over.');
        goToStep(1);
        return;
    }

    setButtonState(button, true, 'Resetting...', 'Reset Password');
    try {
        const { ok, data } = await postJSON('reset-password', { token: resetToken, password });
        if (!ok) {
            showAlert(data.error || 'Could not reset password. Please try again.');
            return;
        }
        goToStep(4);
    } catch (error) {
        console.error('Reset password error:', error);
        showAlert('Connection error. Please try again.');
    } finally {
        setButtonState(button, false, 'Resetting...', 'Reset Password');
    }
});
