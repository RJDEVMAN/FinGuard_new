/**
 * API Wrapper for FinGuard Frontend
 * Handles all communication with FastAPI backend with robust error handling
 */

const API = {
    // Base URLs
    BASE_URL: 'http://localhost:8000',
    GATEWAY_URL: 'http://localhost:8001',
    
    // Configuration
    TIMEOUT: 30000, // 30 seconds
    RETRY_COUNT: 2,
    RETRY_DELAY: 500, // 500ms

    /**
     * Generic fetch wrapper with comprehensive error handling
     * @param {string} url - URL to fetch
     * @param {object} options - Fetch options
     * @returns {Promise<object>} Response JSON
     */
    _fetch: async function(url, options = {}) {
        if (!url) {
            throw new Error('URL is required');
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.TIMEOUT);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMsg = errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
                throw new Error(errorMsg);
            }

            const data = await response.json();
            return data || {};
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - service may be offline');
            }
            
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Network error - cannot reach server. Check if backend is running.');
            }
            
            throw error;
        }
    },

    /**
     * Fetch with automatic retry logic for transient failures
     * @param {string} url - URL to fetch
     * @param {object} options - Fetch options
     * @param {number} attempt - Current attempt number
     * @returns {Promise<object>} Response JSON
     */
    _fetchWithRetry: async function(url, options = {}, attempt = 1) {
        try {
            return await this._fetch(url, options);
        } catch (error) {
            const isTransient = error.message.includes('timeout') || 
                                error.message.includes('Network error');
            
            if (attempt < this.RETRY_COUNT && isTransient) {
                const delay = this.RETRY_DELAY * Math.pow(2, attempt - 1); // exponential backoff
                await new Promise(resolve => setTimeout(resolve, delay));
                return this._fetchWithRetry(url, options, attempt + 1);
            }
            throw error;
        }
    },

    /**
     * Check if API is online
     * @returns {Promise<boolean>} API health status
     */
    checkHealth: async function() {
        try {
            const response = await this._fetch(`${this.BASE_URL}/health`);
            return response.status === 'ok' || response.status === 'healthy';
        } catch (error) {
            console.debug('Health check failed:', error.message);
            return false;
        }
    },

    /**
     * Check if Gateway is online
     * @returns {Promise<boolean>} Gateway health status
     */
    checkGatewayHealth: async function() {
        try {
            const response = await this._fetch(`${this.GATEWAY_URL}/health`);
            return response.status === 'ok' || response.status === 'healthy';
        } catch (error) {
            console.debug('Gateway health check failed:', error.message);
            return false;
        }
    },

    /**
     * Get system information
     * @returns {Promise<object>} System info
     */
    getSystemInfo: async function() {
        try {
            const response = await this._fetch(`${this.BASE_URL}/health`);
            return response || {};
        } catch (error) {
            console.debug('System info fetch failed:', error.message);
            return {};
        }
    },

    /**
     * Analyze text content
     * @param {object} data - Analysis data {text_content, mode, metadata}
     * @returns {Promise<object>} Analysis result
     */
    analyzeText: async function(data) {
        if (!data || !data.text_content) {
            throw new Error('Text content is required');
        }

        if (typeof data.text_content !== 'string' || data.text_content.trim() === '') {
            throw new Error('Text content cannot be empty');
        }

        const payload = {
            text_content: data.text_content.trim(),
            mode: data.mode || 'COMMAND',
            metadata: data.metadata || {}
        };

        try {
            return await this._fetchWithRetry(
                `${this.BASE_URL}/analyze/text`,
                {
                    method: 'POST',
                    body: JSON.stringify(payload)
                }
            );
        } catch (error) {
            throw new Error(`Text analysis failed: ${error.message}`);
        }
    },

    /**
     * Analyze image file
     * @param {object} data - Analysis data {file, mode, metadata}
     * @returns {Promise<object>} Analysis result
     */
    analyzeImage: async function(data) {
        if (!data.file_content && !data.file_data) {
            throw new Error('Image file is required');
        }

        const payload = {
            file_content: data.file_content || data.file_data,
            file_name: data.file_name || 'image.jpg',
            mode: data.mode || 'COMMAND',
            metadata: data.metadata || {}
        };

        return await this._fetchWithRetry(
            `${this.BASE_URL}/analyze/image`,
            {
                method: 'POST',
                body: JSON.stringify(payload)
            }
        );
    },

    /**
     * Analyze video file
     * @param {object} data - Analysis data {file, mode, metadata}
     * @returns {Promise<object>} Analysis result
     */
    analyzeVideo: async function(data) {
        if (!data.file_content && !data.file_data) {
            throw new Error('Video file is required');
        }

        const payload = {
            file_content: data.file_content || data.file_data,
            file_name: data.file_name || 'video.mp4',
            mode: data.mode || 'COMMAND',
            metadata: data.metadata || {}
        };

        return await this._fetchWithRetry(
            `${this.BASE_URL}/analyze/video`,
            {
                method: 'POST',
                body: JSON.stringify(payload)
            }
        );
    },

    /**
     * Analyze audio file
     * @param {object} data - Analysis data {file, mode, metadata}
     * @returns {Promise<object>} Analysis result
     */
    analyzeAudio: async function(data) {
        if (!data.file_content && !data.file_data) {
            throw new Error('Audio file is required');
        }

        const payload = {
            file_content: data.file_content || data.file_data,
            file_name: data.file_name || 'audio.mp3',
            mode: data.mode || 'COMMAND',
            metadata: data.metadata || {}
        };

        return await this._fetchWithRetry(
            `${this.BASE_URL}/analyze/audio`,
            {
                method: 'POST',
                body: JSON.stringify(payload)
            }
        );
    },

    /**
     * Analyze document file
     * @param {object} data - Analysis data {file, mode, metadata}
     * @returns {Promise<object>} Analysis result
     */
    analyzeDocument: async function(data) {
        if (!data.file_content && !data.file_data) {
            throw new Error('Document file is required');
        }

        const payload = {
            file_content: data.file_content || data.file_data,
            file_name: data.file_name || 'document.pdf',
            mode: data.mode || 'COMMAND',
            metadata: data.metadata || {}
        };

        return await this._fetchWithRetry(
            `${this.BASE_URL}/analyze/document`,
            {
                method: 'POST',
                body: JSON.stringify(payload)
            }
        );
    },

    /**
     * Analyze batch of items
     * @param {object} data - Batch data {items, mode, metadata}
     * @returns {Promise<array>} Array of analysis results
     */
    analyzeBatch: async function(data) {
        if (!data || !data.items ) {
            throw new Error('Items array is required');
        }

        if (!Array.isArray(data.items) || data.items.length === 0) {
            throw new Error('At least one item is required for batch analysis');
        }

        // Validate all items are strings
        const validItems = data.items.filter(item => typeof item === 'string' && item.trim() !== '');
        if (validItems.length === 0) {
            throw new Error('All items are empty or invalid');
        }

        if (validItems.length < data.items.length) {
            console.warn(`${data.items.length - validItems.length} empty items will be skipped`);
        }

        // Process items with controlled concurrency to avoid overwhelming server
        const results = [];
        const concurrency = 3; // Process 3 at a time
        
        for (let i = 0; i < validItems.length; i += concurrency) {
            const batch = validItems.slice(i, i + concurrency);
            const batchPromises = batch.map((item, index) =>
                this.analyzeText({
                    text_content: item,
                    mode: data.mode || 'COMMAND',
                    metadata: data.metadata || {}
                }).then(result => ({
                    success: true,
                    result,
                    item_index: i + index
                })).catch(error => ({
                    success: false,
                    error: error.message,
                    item_index: i + index,
                    text_content: item
                }))
            );

            try {
                const batchResults = await Promise.all(batchPromises);
                results.push(...batchResults);
            } catch (error) {
                console.error('Batch processing error:', error);
                // Continue processing other batches even if one fails
            }

            // Small delay between batches
            if (i + concurrency < validItems.length) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }

        if (results.length === 0) {
            throw new Error('Batch analysis produced no results');
        }

        return results;
    },

    /**
     * Get status of all backend services
     * @returns {Promise<object>} Status of all services
     */
    getServicesStatus: async function() {
        const status = {
            api: await this.checkHealth(),
            gateway: await this.checkGatewayHealth(),
            timestamp: new Date().toISOString()
        };
        return status;
    },

    /**
     * Validate connection to all services
     * @returns {Promise<object>} Connection validation result
     */
    validateConnection: async function() {
        const status = await this.getServicesStatus();
        
        return {
            connected: status.api && status.gateway,
            details: status,
            message: status.api && status.gateway 
                ? 'All services are connected'
                : 'Some services are offline'
        };
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}
