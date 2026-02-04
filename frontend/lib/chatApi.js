/**
 * API service for chatbot backend
 * Connects to localhost:8000
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Send a chat message to the backend
 * @param {Object} params - Chat parameters
 * @returns {Promise<Object>} Response from backend
 */
export async function sendChatMessage({
    productId,
    message,
    sessionId,
    language = 'en',
    mode = 'PRE_PURCHASE',
    images = []
}) {
    try {
        const formData = new FormData();

        // Add text data - match backend parameter names
        formData.append('model_id', productId);
        formData.append('message', message);
        formData.append('conversation_id', sessionId); // Changed from session_id to conversation_id
        formData.append('mode', mode);
        formData.append('language', language);

        // Add images if any
        images.forEach((image, index) => {
            formData.append('images', image);
        });

        const response = await fetch(`${BACKEND_URL}/chat`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend error:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Chat API error:', error);
        throw error;
    }
}

/**
 * Generate a new session ID
 */
export function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get or create session ID from localStorage
 */
export function getSessionId(productId) {
    if (typeof window !== 'undefined') {
        const key = `chat_session_${productId}`;
        let sessionId = localStorage.getItem(key);

        if (!sessionId) {
            sessionId = generateSessionId();
            localStorage.setItem(key, sessionId);
        }

        return sessionId;
    }
    return generateSessionId();
}
