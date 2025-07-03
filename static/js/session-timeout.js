/**
 * Session Timeout Management
 * Provides automatic session timeout with user warnings
 */

class SessionTimeout {
    constructor(options = {}) {
        this.sessionDuration = options.sessionDuration || 30 * 60 * 1000; // 30 minutes in milliseconds
        this.warningTime = options.warningTime || 5 * 60 * 1000; // 5 minutes warning
        this.checkInterval = options.checkInterval || 60 * 1000; // Check every minute
        this.serverCheckUrl = options.serverCheckUrl || '/auth/session-check';
        this.extendUrl = options.extendUrl || '/auth/extend-session';
        this.logoutUrl = options.logoutUrl || '/logout';
        
        this.sessionTimer = null;
        this.warningTimer = null;
        this.checkTimer = null;
        this.warningShown = false;
        this.isActive = false;
        
        this.init();
    }

    init() {
        // Only initialize if user is logged in
        if (document.body.getAttribute('data-user-id')) {
            this.isActive = true;
            this.startSession();
            this.setupActivityListeners();
            this.startPeriodicCheck();
        }
    }

    startSession() {
        this.clearTimers();
        this.warningShown = false;
        
        // Set warning timer
        this.warningTimer = setTimeout(() => {
            this.showWarning();
        }, this.sessionDuration - this.warningTime);
        
        // Set session expiry timer
        this.sessionTimer = setTimeout(() => {
            this.expireSession();
        }, this.sessionDuration);
    }

    showWarning() {
        if (this.warningShown) return;
        
        this.warningShown = true;
        const remainingTime = Math.ceil(this.warningTime / 1000 / 60); // Minutes
        
        // Create warning modal
        const modalHtml = `
            <div class="modal fade" id="sessionWarningModal" tabindex="-1" aria-labelledby="sessionWarningModalLabel" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-warning">
                            <h5 class="modal-title text-dark" id="sessionWarningModalLabel">
                                <i class="fas fa-exclamation-triangle me-2"></i>Session Timeout Warning
                            </h5>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <strong>Your session will expire in <span id="countdown">${remainingTime}</span> minute(s).</strong>
                            </div>
                            <p>You will be automatically logged out unless you choose to stay logged in.</p>
                            <div class="d-flex justify-content-between">
                                <button type="button" class="btn btn-primary" id="stayLoggedInBtn">
                                    <i class="fas fa-clock me-2"></i>Stay Logged In
                                </button>
                                <button type="button" class="btn btn-outline-secondary" id="logoutNowBtn">
                                    <i class="fas fa-sign-out-alt me-2"></i>Logout Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('sessionWarningModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('sessionWarningModal'));
        modal.show();
        
        // Setup button handlers
        document.getElementById('stayLoggedInBtn').addEventListener('click', () => {
            this.extendSession();
            modal.hide();
        });
        
        document.getElementById('logoutNowBtn').addEventListener('click', () => {
            this.logout();
        });
        
        // Start countdown
        this.startCountdown();
    }

    startCountdown() {
        const countdownElement = document.getElementById('countdown');
        if (!countdownElement) return;
        
        let timeLeft = Math.ceil(this.warningTime / 1000 / 60);
        
        const countdownInterval = setInterval(() => {
            timeLeft--;
            if (countdownElement) {
                countdownElement.textContent = timeLeft;
            }
            
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
            }
        }, 60000); // Update every minute
    }

    extendSession() {
        fetch(this.extendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.startSession(); // Restart session timer
                this.showNotification('Session extended successfully', 'success');
            } else {
                this.showNotification('Failed to extend session', 'danger');
            }
        })
        .catch(error => {
            console.error('Error extending session:', error);
            this.showNotification('Error extending session', 'danger');
        });
    }

    expireSession() {
        // Hide warning modal if visible
        const modal = document.getElementById('sessionWarningModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
        
        // Redirect to logout
        window.location.href = this.logoutUrl;
    }

    logout() {
        window.location.href = this.logoutUrl;
    }

    resetSession() {
        if (this.isActive) {
            this.startSession();
        }
    }

    setupActivityListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        let activityTimeout;
        
        const activityHandler = () => {
            clearTimeout(activityTimeout);
            // Debounce activity to avoid too frequent resets
            activityTimeout = setTimeout(() => {
                if (this.isActive && !this.warningShown) {
                    this.resetSession();
                }
            }, 1000);
        };
        
        events.forEach(event => {
            document.addEventListener(event, activityHandler, true);
        });
    }

    startPeriodicCheck() {
        // Check session status with server periodically
        this.checkTimer = setInterval(() => {
            if (this.isActive) {
                this.checkSessionStatus();
            }
        }, this.checkInterval);
    }

    checkSessionStatus() {
        fetch(this.serverCheckUrl, {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (!data.valid) {
                // Session is invalid on server side
                this.expireSession();
            }
        })
        .catch(error => {
            console.error('Error checking session:', error);
        });
    }

    clearTimers() {
        if (this.sessionTimer) {
            clearTimeout(this.sessionTimer);
            this.sessionTimer = null;
        }
        if (this.warningTimer) {
            clearTimeout(this.warningTimer);
            this.warningTimer = null;
        }
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
            this.checkTimer = null;
        }
    }

    showNotification(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert" style="position: fixed; top: 100px; right: 20px; z-index: 1060;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert:last-child');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    destroy() {
        this.clearTimers();
        this.isActive = false;
        
        // Remove modal if exists
        const modal = document.getElementById('sessionWarningModal');
        if (modal) {
            modal.remove();
        }
    }
}

// Initialize session timeout when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize session timeout with custom configuration
    window.sessionTimeout = new SessionTimeout({
        sessionDuration: 30 * 60 * 1000, // 30 minutes
        warningTime: 5 * 60 * 1000,      // 5 minutes warning
        checkInterval: 60 * 1000,        // Check every minute
        serverCheckUrl: '/auth/session-check',
        extendUrl: '/auth/extend-session',
        logoutUrl: '/logout'
    });
});
