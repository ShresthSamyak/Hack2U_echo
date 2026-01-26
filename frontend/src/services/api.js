// API Service for Product Intelligence Agent
const API_BASE = 'http://localhost:8000';

export const api = {
    // Get all products
    async getProducts() {
        const response = await fetch(`${API_BASE}/products`);
        if (!response.ok) throw new Error('Failed to fetch products');
        return response.json();
    },

    // Get single product by model_id
    async getProduct(modelId) {
        const response = await fetch(`${API_BASE}/model/${modelId}`);
        if (!response.ok) throw new Error('Failed to fetch product');
        return response.json();
    },

    // Send chat message (with optional multiple images and session ID)
    async sendMessage(message, modelId, mode = 'PRE_PURCHASE', imageFiles = [], sessionId = null) {
        // Handle both array and single file for backwards compatibility
        const images = Array.isArray(imageFiles) ? imageFiles : (imageFiles ? [imageFiles] : []);

        if (images.length > 0) {
            // Use FormData for multipart request (with images)
            const formData = new FormData();
            formData.append('message', message || '');
            formData.append('model_id', modelId);
            formData.append('mode', mode);
            if (sessionId) formData.append('session_id', sessionId);

            // Append multiple images
            images.forEach((file) => {
                formData.append('images', file);  // Same field name for all images
            });

            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                body: formData  // NO Content-Type header - browser sets it
            });
            if (!response.ok) throw new Error('Failed to send message');
            return response.json();
        } else {
            // Use FormData even for text-only messages (backend expects Form data)
            const formData = new FormData();
            formData.append('message', message || '');
            formData.append('model_id', modelId);
            formData.append('mode', mode);
            if (sessionId) formData.append('conversation_id', sessionId);

            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error('Failed to send message');
            return response.json();
        }
    },

    // Switch mode
    async switchMode(mode) {
        const response = await fetch(`${API_BASE}/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        if (!response.ok) throw new Error('Failed to switch mode');
        return response.json();
    },

    // Analyze room image
    async analyzeRoom(imageFile, modelId) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('model_id', modelId);

        const response = await fetch(`${API_BASE}/analyze-room`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Failed to analyze room');
        return response.json();
    },

    // Get conversation history by session ID
    async getConversationHistory(sessionId) {
        const response = await fetch(`${API_BASE}/history/${sessionId}`);
        if (!response.ok) {
            // If endpoint doesn't exist yet or fails, return empty
            return { session_id: sessionId, messages: [] };
        }
        return response.json();
    }
};

export default api;
