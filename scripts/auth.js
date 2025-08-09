/**
 * Authentication Manager for TODO List Application
 * Handles login, register, and session management
 */

class AuthManager {
    constructor() {
        this.apiBase = '/api/auth';
        this.token = localStorage.getItem('authToken');
        this.user = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        
        // Check if user is already logged in
        if (this.token) {
            this.validateToken();
        }
    }

    setupEventListeners() {
        // Form switching
        const showRegisterBtn = document.getElementById('showRegister');
        const showLoginBtn = document.getElementById('showLogin');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (showRegisterBtn) {
            showRegisterBtn.addEventListener('click', () => {
                loginForm.classList.add('hidden');
                registerForm.classList.remove('hidden');
            });
        }

        if (showLoginBtn) {
            showLoginBtn.addEventListener('click', () => {
                registerForm.classList.add('hidden');
                loginForm.classList.remove('hidden');
            });
        }

        // Form submissions
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister();
            });
        }

        // Password confirmation validation
        const confirmPassword = document.getElementById('confirmPassword');
        const registerPassword = document.getElementById('registerPassword');
        
        if (confirmPassword && registerPassword) {
            confirmPassword.addEventListener('input', () => {
                if (confirmPassword.value !== registerPassword.value) {
                    confirmPassword.setCustomValidity('Passwords do not match');
                } else {
                    confirmPassword.setCustomValidity('');
                }
            });
        }
    }

    async handleLogin() {
        const login = document.getElementById('loginInput').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!login || !password) {
            this.showError('Please fill in all fields');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ login, password })
            });

            const data = await response.json();

            if (data.success) {
                this.setAuthData(data.token, data.user);
                this.showSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                this.showError(data.message || 'Login failed');
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showError('Connection error. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async handleRegister() {
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!username || !email || !password || !confirmPassword) {
            this.showError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            this.showError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            this.showError('Password must be at least 6 characters long');
            return;
        }

        if (!/^[a-zA-Z0-9_-]{3,20}$/.test(username)) {
            this.showError('Username must be 3-20 characters and contain only letters, numbers, hyphens, and underscores');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBase}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (data.success) {
                this.setAuthData(data.token, data.user);
                this.showSuccess('Registration successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                if (data.errors && data.errors.length > 0) {
                    this.showError(data.errors[0].msg);
                } else {
                    this.showError(data.message || 'Registration failed');
                }
            }

        } catch (error) {
            console.error('Registration error:', error);
            this.showError('Connection error. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    async validateToken() {
        if (!this.token) return false;

        try {
            const response = await fetch(`${this.apiBase}/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (data.success) {
                this.user = data.user;
                return true;
            } else {
                this.clearAuthData();
                return false;
            }

        } catch (error) {
            console.error('Token validation error:', error);
            this.clearAuthData();
            return false;
        }
    }

    setAuthData(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    clearAuthData() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
    }

    logout() {
        this.clearAuthData();
        window.location.href = '/auth.html';
    }

    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorDiv && errorText) {
            errorText.textContent = message;
            errorDiv.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 5000);
        }
    }

    showSuccess(message) {
        // Create a success message similar to error
        let successDiv = document.getElementById('successMessage');
        
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.id = 'successMessage';
            successDiv.className = 'success-message';
            successDiv.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span id="successText"></span>
            `;
            
            // Add success message styles
            successDiv.style.cssText = `
                background: var(--pixel-sage);
                color: var(--pixel-dark);
                border: 3px solid var(--pixel-dark);
                padding: var(--spacing-md);
                margin-top: var(--spacing-md);
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            `;
            
            const errorDiv = document.getElementById('errorMessage');
            if (errorDiv) {
                errorDiv.parentNode.insertBefore(successDiv, errorDiv.nextSibling);
            }
        }
        
        const successText = document.getElementById('successText');
        if (successText) {
            successText.textContent = message;
            successDiv.classList.remove('hidden');
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                successDiv.classList.add('hidden');
            }, 3000);
        }
    }
}

// Initialize auth manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
    
    // Redirect to main app if already logged in
    if (window.authManager.isAuthenticated()) {
        window.location.href = '/';
    }
});

// Export for use in other modules
window.AuthManager = AuthManager;
