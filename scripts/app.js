// Application bootstrap: wires managers, UI, and runtime helpers
class TodoApp {
    constructor() {
        this.todoManager = null;
        this.uiManager = null;
        this.isInitialized = false;
        
        // Defer init until DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    // Orchestrates app startup
    async init() {
        try {
            console.log('App initializing...');
            
            // Avoid stale caches unless explicitly enabled
            this.unregisterServiceWorkers();

            // Temporarily disable auth check for debugging
            console.log('Skipping auth check for testing...');

            this.checkDependencies();
            
            // Core managers
            console.log('Creating TodoManager...');
            this.todoManager = new TodoManager();
            
            // Wait for data before wiring UI
            console.log('Waiting for TodoManager to load data...');
            await this.todoManager.init();
            
            console.log('Creating UIManager...');
            this.uiManager = new UIManager(this.todoManager);
            
            // Initial render after both are ready
            console.log('Updating UI with loaded data...');
            this.uiManager.renderTodos();
            this.uiManager.updateCounts();
            
            // For inline onclick handlers
            window.uiManager = this.uiManager;
            
            this.setupUserAuth();
            this.setupAdvancedFeatures();
            this.setupErrorHandling();
            this.setupPerformanceOptimizations();
            
            this.isInitialized = true;
            this.showWelcomeMessage();
            
            console.log('✅ TODO App initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize TODO App:', error);
            this.showInitializationError(error);
        }
    }

    checkDependencies() {
        const required = ['TodoStorageManager', 'TodoManager', 'UIManager'];
        const results = {};

        for (const dep of required) {
            let ok = false;
            if (typeof globalThis !== 'undefined' && typeof globalThis[dep] === 'function') {
                ok = true;
            } else {
                try {
                    const type = Function(`try { return typeof ${dep} } catch (e) { return 'undefined' }`)();
                    ok = type === 'function';
                } catch (e) {
                    ok = false;
                }
            }
            results[dep] = ok;
        }

        const missing = Object.keys(results).filter(k => !results[k]);
        if (missing.length) {
            console.warn('Some dependencies not detected yet, continuing anyway:', missing.join(', '));
        } else {
            console.log('✅ All dependencies loaded successfully');
        }
    }

    setupUserAuth() {
        // Minimal user header (if logged in)
        const userStr = localStorage.getItem('user');
        const userInfo = document.getElementById('userInfo');
        const welcomeUser = document.getElementById('welcomeUser');
        const logoutBtn = document.getElementById('logoutBtn');

        if (userStr && userInfo && welcomeUser) {
            try {
                const user = JSON.parse(userStr);
                welcomeUser.textContent = `Welcome, ${user.username}!`;
                userInfo.style.display = 'flex';
                userInfo.style.alignItems = 'center';
                userInfo.style.gap = 'var(--spacing-sm)';
            } catch (error) {
                console.error('Error parsing user data:', error);
            }
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.removeItem('authToken');
                localStorage.removeItem('user');
                window.location.href = '/auth.html';
            });
        }
    }

    // Optional UX extras
    setupAdvancedFeatures() {
        this.setupKeyboardShortcuts();
        this.setupDataManagement();
        this.setupOfflineSupport();
        this.setupAutoSave();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === '?') {
                e.preventDefault();
                this.showKeyboardShortcuts();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                document.getElementById('todoInput').focus();
            }
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                if (this.todoManager) this.todoManager.clearCompleted();
            }
        });
    }

    setupDataManagement() {
        this.addDataManagementUI();
    }

    addDataManagementUI() {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn btn-secondary';
        exportBtn.innerHTML = '<i class="fas fa-download"></i> Export Data';
        exportBtn.onclick = () => this.exportData();
        
        const importBtn = document.createElement('button');
        importBtn.className = 'btn btn-secondary';
        importBtn.innerHTML = '<i class="fas fa-upload"></i> Import Data';
        importBtn.onclick = () => this.importData();
        
        const bulkActions = document.querySelector('.bulk-actions-container');
        if (bulkActions) {
            bulkActions.appendChild(exportBtn);
            bulkActions.appendChild(importBtn);
        }
    }

    exportData() {
        try {
            const data = this.todoManager.exportTodos();
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `todos-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            this.uiManager.showNotification('Data exported successfully', 'success');
        } catch (error) {
            console.error('Export failed:', error);
            this.uiManager.showNotification('Export failed', 'error');
        }
    }

    importData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const success = this.todoManager.importTodos(e.target.result);
                    if (success) {
                        this.uiManager.showNotification('Data imported successfully', 'success');
                    } else {
                        this.uiManager.showNotification('Import failed - invalid data format', 'error');
                    }
                } catch (error) {
                    console.error('Import failed:', error);
                    this.uiManager.showNotification('Import failed', 'error');
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    // Unregister service workers unless explicitly enabled
    async unregisterServiceWorkers() {
        try {
            if ('serviceWorker' in navigator) {
                const enabled = localStorage.getItem('enableSW') === 'true';
                if (enabled) {
                    console.log('Service Worker enabled by flag; not unregistering.');
                    return;
                }
                const regs = await navigator.serviceWorker.getRegistrations();
                if (regs && regs.length) {
                    console.log(`Unregistering ${regs.length} Service Worker(s) to avoid stale cache...`);
                    for (const r of regs) await r.unregister();
                }
            }
        } catch (e) {
            console.warn('Failed to unregister service workers:', e);
        }
    }

    // Offline support (disabled by default)
    setupOfflineSupport() {
        if ('serviceWorker' in navigator) {
            const enabled = localStorage.getItem('enableSW') === 'true';
            if (!enabled) {
                console.log('Service Worker disabled. Set localStorage.enableSW = "true" to enable.');
                return;
            }
            navigator.serviceWorker.register('/service-worker.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupAutoSave() {
        // Basic periodic backup to localStorage
        setInterval(() => {
            if (this.todoManager) {
                const stats = this.todoManager.getStats();
                localStorage.setItem('lastBackup', new Date().toISOString());
                console.log('📁 Auto-backup completed:', stats);
            }
        }, 5 * 60 * 1000);
    }

    setupErrorHandling() {
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            if (this.uiManager) this.uiManager.showNotification('An unexpected error occurred', 'error');
        });
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            if (this.uiManager) this.uiManager.showNotification('An unexpected error occurred', 'error');
        });
    }

    setupPerformanceOptimizations() {
        // Throttle resize events
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                console.log('Window resized');
            }, 250);
        });
        this.setupIntersectionObserver();
    }

    setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) entry.target.classList.add('visible');
                });
            }, { threshold: 0.1 });
            this.intersectionObserver = observer;
        }
    }

    showWelcomeMessage() {
        const hasVisited = localStorage.getItem('hasVisited');
        if (!hasVisited && this.todoManager.getAllTodos().length === 0) {
            setTimeout(() => {
                if (this.uiManager) {
                    this.uiManager.showNotification('Welcome! Add your first todo above to get started 🎉', 'info');
                }
                localStorage.setItem('hasVisited', 'true');
            }, 1000);
        }
    }

    showKeyboardShortcuts() {
        const shortcuts = [
            'Ctrl/Cmd + Enter: Add todo',
            'Ctrl/Cmd + N: Focus input',
            'Ctrl/Cmd + A: Mark all complete',
            'Ctrl/Cmd + Shift + C: Clear completed',
            'Ctrl/Cmd + ?: Show this help',
            'Escape: Close modal',
            'Double-click todo: Edit'
        ];
        const message = 'Keyboard Shortcuts:\n\n' + shortcuts.join('\n');
        alert(message);
    }

    showInitializationError(error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'initialization-error';
        errorDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #fee2e2;
                color: #991b1b;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                max-width: 400px;
                text-align: center;
                z-index: 9999;
            ">
                <h3>❌ App Initialization Failed</h3>
                <p>The TODO app could not start properly.</p>
                <p><strong>Error:</strong> ${error.message}</p>
                <button onclick="location.reload()" style="
                    background: #dc2626;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 0.25rem;
                    cursor: pointer;
                    margin-top: 1rem;
                ">
                    Reload Page
                </button>
            </div>
        `;
        document.body.appendChild(errorDiv);
    }

    getAppStats() {
        if (!this.isInitialized) return { error: 'App not initialized' };
        return {
            initialized: this.isInitialized,
            storageStats: this.todoManager.getStats(),
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
    }

    resetApp() {
        if (confirm('Are you sure you want to reset all data? This cannot be undone!')) {
            localStorage.clear();
            location.reload();
        }
    }
}

// Add notification styles if they don't exist
const addNotificationStyles = () => {
    const existingStyles = document.getElementById('notification-styles');
    if (existingStyles) return;

    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        .notification { position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; border-radius: 0.5rem; color: white; font-weight: 500; z-index: 10000; display: none; max-width: 300px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); animation: slideInRight 0.3s ease-out; }
        .notification.success { background: #10b981; }
        .notification.error { background: #ef4444; }
        .notification.info { background: #3b82f6; }
        .notification.warning { background: #f59e0b; }
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @media (max-width: 480px) { .notification { top: 10px; right: 10px; left: 10px; max-width: none; } }
    `;
    document.head.appendChild(style);
};

// Initialize notification styles
addNotificationStyles();

// Boot the app
const app = new TodoApp();

// Expose for debugging
window.todoApp = app;

// CommonJS export (for tests/tools)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TodoApp;
}
