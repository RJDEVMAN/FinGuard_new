/**
 * Utility Functions for FinGuard Frontend
 * Handles common operations: file processing, metadata parsing, storage, etc.
 */

const Utils = {
    /**
     * Parse metadata string in format "key=value, key=value"
     * @param {string} metadataStr - Metadata string to parse
     * @returns {object} Parsed metadata object or empty object
     */
    parseMetadata: function(metadataStr) {
        if (!metadataStr || typeof metadataStr !== 'string') {
            return {};
        }

        const metadata = {};
        try {
            const pairs = metadataStr.split(',').map(pair => pair.trim());
            for (const pair of pairs) {
                if (!pair) continue;
                const [key, value] = pair.split('=').map(s => s.trim());
                if (key && value) {
                    metadata[key] = value;
                }
            }
        } catch (e) {
            console.error('Error parsing metadata:', e);
        }

        return metadata;
    },

    /**
     * Convert File object to Base64 string
     * @param {File} file - File object to convert
     * @returns {Promise<string>} Base64 encoded file content
     */
    fileToBase64: async function(file) {
        return new Promise((resolve, reject) => {
            if (!file) {
                reject(new Error('No file provided'));
                return;
            }

            const reader = new FileReader();
            reader.onload = () => {
                try {
                    resolve(reader.result.split(',')[1]); // Remove data URL prefix
                } catch (e) {
                    reject(e);
                }
            };
            reader.onerror = () => reject(reader.error);
            reader.readAsDataURL(file);
        });
    },

    /**
     * Format bytes to human-readable format
     * @param {number} bytes - Number of bytes
     * @returns {string} Formatted size (e.g., "2.5MB")
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    },

    /**
     * Save analysis session to localStorage
     * @param {object} sessionData - Session data to save
     * @returns {boolean} Success status
     */
    saveSession: function(sessionData) {
        try {
            if (!sessionData.id) {
                sessionData.id = 'session_' + Date.now();
            }
            if (!sessionData.timestamp) {
                sessionData.timestamp = new Date().toISOString();
            }

            const sessions = this.getRecentSessions(1000) || [];
            sessions.unshift(sessionData); // Add to beginning
            
            // Keep only last 50 sessions
            const truncated = sessions.slice(0, 50);
            
            localStorage.setItem('analysis_sessions', JSON.stringify(truncated));
            return true;
        } catch (e) {
            console.error('Error saving session:', e);
            if (e.name === 'QuotaExceededError') {
                console.warn('LocalStorage quota exceeded');
            }
            return false;
        }
    },

    /**
     * Retrieve recent sessions from localStorage
     * @param {number} limit - Maximum number of sessions to retrieve
     * @returns {array} Array of session objects
     */
    getRecentSessions: function(limit = 50) {
        try {
            const stored = localStorage.getItem('analysis_sessions');
            if (!stored) return [];
            
            const sessions = JSON.parse(stored);
            return Array.isArray(sessions) ? sessions.slice(0, limit) : [];
        } catch (e) {
            console.error('Error retrieving sessions:', e);
            return [];
        }
    },

    /**
     * Get file accept types for media input
     * @param {string} mediaType - Type of media (image, video, audio, document)
     * @returns {string} File accept attribute value
     */
    getFileAccept: function(mediaType) {
        const accepts = {
            image: 'image/jpeg,image/png,image/gif,image/webp',
            video: 'video/mp4,video/mpeg,video/quicktime,video/x-msvideo',
            audio: 'audio/mpeg,audio/wav,audio/ogg,audio/aac',
            document: '.pdf,.doc,.docx,.txt,.xlsx'
        };
        return accepts[mediaType] || '*/*';
    },

    /**
     * Validate file size
     * @param {File} file - File object to validate
     * @param {number} maxSizeMB - Maximum size in megabytes
     * @returns {object} Validation result {valid: boolean, message: string}
     */
    validateFileSize: function(file, maxSizeMB = 100) {
        const maxBytes = maxSizeMB * 1024 * 1024;
        if (file.size > maxBytes) {
            return {
                valid: false,
                message: `File size exceeds ${maxSizeMB}MB limit. Current size: ${this.formatFileSize(file.size)}`
            };
        }
        return {
            valid: true,
            message: ''
        };
    },

    /**
     * Validate file type
     * @param {File} file - File object to validate
     * @param {string} mediaType - Expected media type
     * @returns {object} Validation result {valid: boolean, message: string}
     */
    validateFileType: function(file, mediaType) {
        const mimeTypes = {
            image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            video: ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo'],
            audio: ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/aac'],
            document: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/vnd.ms-excel']
        };

        const allowed = mimeTypes[mediaType] || [];
        if (allowed.length > 0 && !allowed.includes(file.type)) {
            return {
                valid: false,
                message: `Invalid file type. Expected ${mediaType} files.`
            };
        }
        return {
            valid: true,
            message: ''
        };
    },

    /**
     * Clear all sessions from localStorage
     * @returns {boolean} Success status
     */
    clearSessions: function() {
        try {
            localStorage.removeItem('analysis_sessions');
            return true;
        } catch (e) {
            console.error('Error clearing sessions:', e);
            return false;
        }
    },

    /**
     * Export sessions as JSON file
     * @returns {void}
     */
    exportSessions: function() {
        try {
            const sessions = this.getRecentSessions(1000);
            const json = JSON.stringify(sessions, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `finguard_sessions_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
        } catch (e) {
            console.error('Error exporting sessions:', e);
        }
    },

    /**
     * Format date/time for display
     * @param {string|Date} dateInput - Date to format
     * @returns {string} Formatted date string
     */
    formatDateTime: function(dateInput) {
        try {
            const date = new Date(dateInput);
            return date.toLocaleString();
        } catch (e) {
            return 'Invalid date';
        }
    },

    /**
     * Create unique session ID
     * @returns {string} Session ID
     */
    generateSessionId: function() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },

    /**
     * Deep clone an object
     * @param {object} obj - Object to clone
     * @returns {object} Cloned object
     */
    deepClone: function(obj) {
        try {
            return JSON.parse(JSON.stringify(obj));
        } catch (e) {
            console.error('Error cloning object:', e);
            return {};
        }
    },

    /**
     * Debounce function execution
     * @param {function} func - Function to debounce
     * @param {number} timeout - Debounce timeout in ms
     * @returns {function} Debounced function
     */
    debounce: function(func, timeout = 300) {
        let timer;
        return function(...args) {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), timeout);
        };
    },

    /**
     * Throttle function execution
     * @param {function} func - Function to throttle
     * @param {number} limit - Time limit in ms
     * @returns {function} Throttled function
     */
    throttle: function(func, limit = 300) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Check if string contains any fraud indicators
     * @param {string} text - Text to check
     * @returns {array} Array of found indicators
     */
    findFraudIndicators: function(text) {
        const indicators = {
            urgency: ['immediately', 'urgent', 'asap', 'hurry', 'quickly', 'right now'],
            crypto: ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'wallet', 'mining'],
            transfer: ['transfer', 'wire', 'send', 'payment', 'deposit', 'transaction'],
            verify: ['verify', 'confirm', 'validate', 'update', 'authenticate', 'authorization'],
            social_engineering: ['click link', 'download attachment', 'verify account', 'claim reward', 'congratulations']
        };

        const found = [];
        const lowerText = text.toLowerCase();

        for (const [category, keywords] of Object.entries(indicators)) {
            for (const keyword of keywords) {
                if (lowerText.includes(keyword)) {
                    found.push({
                        category,
                        keyword,
                        type: 'fraud_indicator'
                    });
                }
            }
        }

        return found;
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
