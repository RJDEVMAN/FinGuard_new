/**
 * Shared Application Initialization
 * Handles global setup, status monitoring, and common event listeners
 */

const App = {
    // Configuration
    STATUS_UPDATE_INTERVAL: 15000, // 15 seconds
    NOTIFICATION_TIMEOUT: 5000, // 5 seconds

    /**
     * Initialize application on page load
     */
    init: async function() {
        try {
            console.log('FinGuard App - Initializing...');
            
            // Set up global error handlers
            this.setupErrorHandlers();
            
            // Initialize status indicator
            await this.updateStatusIndicator();
            
            // Set up status update interval
            this.statusInterval = setInterval(
                this.updateStatusIndicator.bind(this), 
                this.STATUS_UPDATE_INTERVAL
            );

            // Add keyboard shortcuts
            this.setupKeyboardShortcuts();

            // Set up exit confirmation
            this.setupExitConfirmation();

            console.log('FinGuard App - Initialization complete');
        } catch (error) {
            console.error('App initialization error:', error);
            this.showNotification('App initialization error. Some features may not work.', 'warning');
        }
    },

    /**
     * Setup global error handlers
     */
    setupErrorHandlers: function() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showNotification(
                'An unexpected error occurred. Check console for details.',
                'error'
            );
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled rejection:', event.reason);
            const message = event.reason?.message || 'An unexpected error occurred.';
            this.showNotification(message, 'error');
        });
    },

    /**
     * Update status indicator across all pages
     */
    updateStatusIndicator: async function() {
        const indicator = document.getElementById('status-indicator');
        if (!indicator) return;

        try {
            const apiOnline = await API.checkHealth();
            const gatewayOnline = await API.checkGatewayHealth();
            const online = apiOnline && gatewayOnline;

            indicator.classList.remove('online', 'offline');
            indicator.classList.add(online ? 'online' : 'offline');
            
            const statusText = indicator.querySelector('.status-text');
            if (statusText) {
                statusText.textContent = online ? 'Online' : 'Offline';
            }

            // Update title
            document.title = (online ? '✓ ' : '✗ ') + (document.title.replace(/^[✓✗] /, '') || 'FinGuard');
        } catch (error) {
            console.debug('Status update error:', error.message);
            indicator.classList.remove('online');
            indicator.classList.add('offline');
        }
    },

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter: Submit form
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const form = document.activeElement?.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }

            // Ctrl/Cmd + S: Save/Export
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const exportBtn = document.querySelector('[data-action="export"]');
                if (exportBtn) {
                    exportBtn.click();
                }
            }

            // Escape: Close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('[role="dialog"]:not([hidden])');
                modals.forEach(modal => modal.setAttribute('hidden', ''));
            }
        });
    },

    /**
     * Set up exit confirmation for unsaved changes
     */
    setupExitConfirmation: function() {
        let hasUnsavedChanges = false;

        document.addEventListener('change', (e) => {
            if (e.target.closest('form')) {
                hasUnsavedChanges = true;
            }
        });

        document.addEventListener('input', (e) => {
            if (e.target.closest('form')) {
                hasUnsavedChanges = true;
            }
        });

        document.addEventListener('submit', () => {
            hasUnsavedChanges = false;
        });

        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    },

    /**
     * Show notification message
     * @param {string} message - Message to display
     * @param {string} type - Notification type (success, error, warning, info)
     * @param {number} duration - Display duration in milliseconds
     */
    showNotification: function(message, type = 'info', duration = this.NOTIFICATION_TIMEOUT) {
        if (!message) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');
        
        const iconClass = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${iconClass}"></i>
                <span>${message}</span>
                <button class="notification-close" aria-label="Close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
    },

    /**
     * Get icon for notification type
     */
    getNotificationIcon: function(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    },

    /**
     * Format analysis result for display
     */
    formatResult: function(result) {
        if (!result) return null;

        return {
            decision: result.decision || result.final_decision || 'UNKNOWN',
            fraud_score: parseFloat(result.fraud_score) || 0,
            timestamp: result.timestamp || new Date().toISOString(),
            agent_reports: result.agent_reports || {},
            fraud_indicators: result.fraud_indicators || [],
            confidence: parseFloat(result.confidence) || 0
        };
    },

    /**
     * Get decision color based on result
     */
    getDecisionColor: function(decision) {
        const colors = {
            'SAFE_APPROVED': '#10b981',
            'REQUIRE_MANUAL_REVIEW': '#f59e0b',
            'FRAUD_BLOCKED': '#ef4444',
            'UNKNOWN': '#6b7280'
        };
        return colors[decision] || colors['UNKNOWN'];
    },

    /**
     * Get decision icon based on result
     */
    getDecisionIcon: function(decision) {
        const icons = {
            'SAFE_APPROVED': 'check-circle',
            'REQUIRE_MANUAL_REVIEW': 'exclamation-triangle',
            'FRAUD_BLOCKED': 'times-circle',
            'UNKNOWN': 'question-circle'
        };
        return icons[decision] || icons['UNKNOWN'];
    },

    /**
     * Validate email address
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Copy text to clipboard
     */
    copyToClipboard: function(text) {
        if (!text) {
            this.showNotification('No text to copy', 'warning');
            return Promise.resolve(false);
        }

        return navigator.clipboard.writeText(text)
            .then(() => {
                this.showNotification('Copied to clipboard', 'success', 2000);
                return true;
            })
            .catch((err) => {
                console.error('Clipboard copy failed:', err);
                this.showNotification('Failed to copy to clipboard', 'error');
                return false;
            });
    },

    /**
     * Set button loading state
     */
    setButtonLoading: function(button, loading = true) {
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.setAttribute('data-original-text', button.textContent);
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.getAttribute('data-original-text') || 'Submit';
        }
    },

    /**
     * Cleanup function
     */
    destroy: function() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }
    }
};



// Add global styles for notifications
const appStyle = document.createElement('style');
appStyle.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-in-out;
        z-index: 1000;
        max-width: 400px;
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
    }

    .notification-success { border-left: 4px solid #10b981; }
    .notification-error { border-left: 4px solid #ef4444; }
    .notification-warning { border-left: 4px solid #f59e0b; }
    .notification-info { border-left: 4px solid #0ea5e9; }

    .notification i { font-size: 1.25rem; }
    .notification-success i { color: #10b981; }
    .notification-error i { color: #ef4444; }
    .notification-warning i { color: #f59e0b; }
    .notification-info i { color: #0ea5e9; }

    .notification-close {
        background: none;
        border: none;
        cursor: pointer;
        color: #9ca3af;
        padding: 0;
        font-size: 1.25rem;
        margin-left: auto;
    }

    .notification-close:hover { color: #6b7280; }

    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @media (max-width: 640px) {
        .notification {
            left: 10px;
            right: 10px;
            max-width: none;
        }
    }
`;
document.head.appendChild(appStyle);

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}
