function initGoogleAuth() {
    // Wait for the Google API to load
    window.onload = function () {
        if (!window.google) return;
        
        // This Client ID should be loaded dynamically, but for now we'll assume it's set in the environment or passed via config.
        // In a real app, you would expose the public client ID via an API endpoint or inject it.
        // We'll fetch it from the backend for security.
        fetch(`${API_BASE}/api/auth/client-id`)
            .then(res => res.json())
            .then(data => {
                if (!data.client_id) return;
                
                google.accounts.id.initialize({
                    client_id: data.client_id,
                    callback: handleGoogleCallback
                });
                
                if ($('#googleLoginBtn')) {
                    google.accounts.id.renderButton(
                        $('#googleLoginBtn'),
                        { theme: "outline", size: "large", text: "signin_with", shape: "pill" }
                    );
                }
                
                if ($('#googleSignupBtn')) {
                    google.accounts.id.renderButton(
                        $('#googleSignupBtn'),
                        { theme: "outline", size: "large", text: "signup_with", shape: "pill" }
                    );
                }
            })
            .catch(err => console.error('Failed to load Google Client ID', err));
    }
}

async function handleGoogleCallback(response) {
    try {
        const res = await fetch(`${API_BASE}/api/auth/google-login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: response.credential })
        });
        const data = await res.json();
        
        if (res.ok) {
            // token is now in HttpOnly cookie
            showToast('Logged in with Google!', 'success');
            checkAuthStatus();
        } else {
            showToast(data.detail || 'Google Login failed', 'error');
        }
    } catch (err) {
        showToast('Google Login error', 'error');
    }
}

async function checkAuthStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/auth/me`);
        if (res.ok) {
            const user = await res.json();
            window.appState.user = user; // Set global state
            if ($('#authContainerWrapper')) $('#authContainerWrapper').style.display = 'none';
            else $('#authView').style.display = 'none'; // Fallback
            
            $('#mainApp').style.display = 'block';
            switchView('generateView');
            loadAccountProfile();
            
            if (user.is_admin) {
                if ($('#navAdmin')) $('#navAdmin').style.display = 'inline-block';
                if ($('#mobileNavAdmin')) $('#mobileNavAdmin').style.display = 'block';
            } else {
                if ($('#navAdmin')) $('#navAdmin').style.display = 'none';
                if ($('#mobileNavAdmin')) $('#mobileNavAdmin').style.display = 'none';
            }
        } else {
            throw new Error('Not auth');
        }
    } catch(err) {
        if ($('#authContainerWrapper')) $('#authContainerWrapper').style.display = 'block';
        else $('#authView').style.display = 'block'; // Fallback
        
        $('#mainApp').style.display = 'none';
        if ($('#navAdmin')) $('#navAdmin').style.display = 'none';
        if ($('#mobileNavAdmin')) $('#mobileNavAdmin').style.display = 'none';
    }
}

function getToken() {
    // Deprecated with HttpOnly cookies
    return null;
}

function getAuthHeaders() {
    return {}; // Credentials automatically sent via cookies
}

function handleLogout() {
    // backend will clear the cookie
    fetch(`${API_BASE}/api/auth/logout`, {method: 'POST'});
    window.appState.user = null;
    showToast('Logged out successfully', 'info');
    checkAuthStatus();
}

async function handleLogin() {
    const username = $('#authUsername').value.trim();
    const password = $('#authPassword').value;
    if (!username || !password) return showToast('Please enter username and password', 'error');

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            // token is now in HttpOnly cookie
            showToast('Logged in successfully!', 'success');
            checkAuthStatus();
        } else if (res.status === 403 && data.detail.includes('not verified')) {
            showToast(data.detail, 'warning');
            pendingSignupEmail = username; // Note: they might have typed email
            showOTPView(username);
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (err) {
        showToast('Login error', 'error');
    }
}

async function handleSignup() {
    const username = $('#signupUsername').value.trim();
    const email = $('#signupEmail').value.trim();
    const password = $('#signupPassword').value;
    if (!username || !email || !password) return showToast('Please enter username, email and password', 'error');

    try {
        const res = await fetch(`${API_BASE}/api/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            showToast('OTP sent to your email!', 'info');
            pendingSignupEmail = email;
            showOTPView(email);
        } else {
            showToast(data.detail || 'Signup failed', 'error');
        }
    } catch (err) {
        showToast('Signup error', 'error');
    }
}

function showOTPView(email) {
    $('#otpEmailDisplay').textContent = email;
    $('#otpInput').value = '';
    
    const flipper = $('#authFlipper');
    if (flipper) {
        flipper.className = 'auth-flipper otp-view';
    }
}

async function handleOTPVerify() {
    const otp = $('#otpInput').value.trim();
    if (otp.length !== 6) return showToast('Please enter a 6-digit OTP', 'error');
    if (!pendingSignupEmail) return showToast('Session expired, please try again', 'error');

    try {
        const res = await fetch(`${API_BASE}/api/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: pendingSignupEmail, otp })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            // token is now in HttpOnly cookie
            showToast('Email verified and logged in successfully!', 'success');
            checkAuthStatus();
        } else {
            showToast(data.detail || 'Invalid OTP', 'error');
        }
    } catch (err) {
        showToast('Verification error', 'error');
    }
}

async function handleResendOTP() {
    if (!pendingSignupEmail) return;
    
    // We can resend OTP simply by calling a login with dummy password if it's the easiest route without an explicit resend endpoint.
    // However, it's better to add an endpoint, or we can just ask them to login again which triggers a new OTP.
    showToast('To resend, please click Back to Login and try logging in again.', 'info');
}

function toggleAuthFlip() {
    const flipper = $('#authFlipper');
    if (flipper) {
        flipper.className = flipper.classList.contains('flipped') ? 'auth-flipper' : 'auth-flipper flipped';
    }
}

