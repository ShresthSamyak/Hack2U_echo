import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Send, Camera, X } from 'lucide-react';
import { api } from '../services/api';
import '../styles/product.css';

export default function ProductDetailPage() {
    const { modelId } = useParams();
    const [productData, setProductData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Chat state
    const [mode, setMode] = useState('PRE_PURCHASE');
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const chatAreaRef = useRef(null);

    // Image upload state (multi-image support)
    const [selectedImages, setSelectedImages] = useState([]);
    const [imagePreviews, setImagePreviews] = useState([]);
    const [uploadError, setUploadError] = useState(null);
    const fileInputRef = useRef(null);
    const MAX_IMAGES = 3;

    // Fetch product data on mount
    useEffect(() => {
        fetchProductData();
    }, [modelId]);

    // Initialize session and load history
    useEffect(() => {
        if (!modelId) return;

        // Get or create session ID for this product
        const key = `session_${modelId}`;
        let sid = localStorage.getItem(key);

        if (!sid) {
            sid = crypto.randomUUID();
            localStorage.setItem(key, sid);
            console.log(`✅ Created new session: ${sid}`);
        } else {
            console.log(`📂 Using existing session: ${sid}`);
        }

        setSessionId(sid);
        loadConversationHistory(sid);
    }, [modelId]);

    const loadConversationHistory = async (sid) => {
        try {
            setIsLoadingHistory(true);
            const history = await api.getConversationHistory(sid);

            if (history.messages && history.messages.length > 0) {
                console.log(`📚 Loaded ${history.messages.length} messages from history`);
                setMessages(history.messages);
            } else {
                console.log(`💬 No previous conversation history`);
            }
        } catch (err) {
            console.error('Failed to load history:', err);
            // Continue without history
        } finally {
            setIsLoadingHistory(false);
        }
    };

    // Auto-scroll chat to bottom
    useEffect(() => {
        if (chatAreaRef.current) {
            chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
        }
    }, [messages]);

    const fetchProductData = async () => {
        try {
            setLoading(true);
            const data = await api.getProduct(modelId);
            setProductData(data);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSendMessage = async () => {
        // Allow sending if there's a message or images
        if ((!inputMessage.trim() && selectedImages.length === 0) || isSending) return;

        const userMessage = inputMessage.trim();
        const imagesToSend = [...selectedImages];
        const imagePreviewsToStore = [...imagePreviews];

        // Clear inputs
        setInputMessage('');
        setSelectedImages([]);
        setImagePreviews([]);
        setUploadError(null);

        // Add user message with image previews
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage || `📷 [${imagesToSend.length} image(s)]`,
            imagePreviews: imagePreviewsToStore
        }]);
        setIsSending(true);

        try {
            // Send to backend with multiple images and session ID
            const response = await api.sendMessage(userMessage, modelId, mode, imagesToSend, sessionId);

            // Add assistant response
            setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again.'
            }]);
        } finally {
            setIsSending(false);
        }
    };

    const handleImageSelect = (e) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        // Limit to MAX_IMAGES
        const remainingSlots = MAX_IMAGES - selectedImages.length;
        if (remainingSlots <= 0) {
            setUploadError(`Maximum ${MAX_IMAGES} images allowed`);
            return;
        }

        const filesToAdd = files.slice(0, remainingSlots);

        // Validate and create previews
        const validFiles = [];
        const newPreviews = [];

        for (const file of filesToAdd) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                setUploadError('Only images are allowed (PNG, JPG, JPEG, WEBP)');
                continue;
            }

            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                setUploadError('Each file must be less than 5MB');
                continue;
            }

            validFiles.push(file);
        }

        // Create previews for valid files
        Promise.all(
            validFiles.map(file => {
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(file);
                });
            })
        ).then(previews => {
            setSelectedImages(prev => [...prev, ...validFiles]);
            setImagePreviews(prev => [...prev, ...previews]);
            setUploadError(null);
        });

        // Reset file input
        e.target.value = '';
    };

    const handleRemoveImage = (index) => {
        setSelectedImages(prev => prev.filter((_, i) => i !== index));
        setImagePreviews(prev => prev.filter((_, i) => i !== index));
        setUploadError(null);
    };

    const handleModeSwitch = async (newMode) => {
        if (newMode === mode) return;
        setMode(newMode);

        try {
            await api.switchMode(newMode);
        } catch (err) {
            console.error('Failed to switch mode:', err);
        }
    };

    if (loading) {
        return (
            <div className="product-detail-page">
                <div className="container">
                    <div className="loading-placeholder">
                        <div className="spinner"></div>
                        <p>Loading product details...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="product-detail-page">
                <div className="container">
                    <div className="error-placeholder">
                        <p>❌ Error loading product: {error}</p>
                        <button onClick={fetchProductData} className="btn btn-primary">
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!productData) return null;

    const { product, model, warranty_years } = productData;

    return (
        <div className="product-detail-page">
            <div className="container">
                {/* Back button */}
                <Link to="/" className="back-button">
                    <ArrowLeft size={20} />
                    Back to Marketplace
                </Link>

                <div className="split-layout">
                    {/* Left Panel - Product Info */}
                    <div className="product-info-panel">
                        <div className="image-gallery">
                            <div className="main-image-placeholder">
                                <p>{product.brand} {product.name}</p>
                            </div>
                        </div>

                        <div className="product-details">
                            <div className="badges">
                                <span className="badge warranty">{warranty_years}y warranty</span>
                                <span className="badge ai">🤖 AI Assistant</span>
                            </div>

                            <h1 className="product-name">
                                {product.brand} {product.name}
                            </h1>
                            <p className="product-model">{model.model_name}</p>
                            <p className="product-price">${model.price}</p>

                            <div className="features">
                                <h3>Key Features</h3>
                                <ul>
                                    {model.features.map((feature, idx) => (
                                        <li key={idx}>{feature}</li>
                                    ))}
                                </ul>
                            </div>

                            {model.dimensions_cm && model.dimensions_cm.length > 0 && (
                                <div className="dimensions">
                                    <h3>Dimensions</h3>
                                    <p>{model.dimensions_cm.join(' × ')} cm</p>
                                </div>
                            )}

                            <button className="btn btn-primary">Buy Now</button>
                        </div>
                    </div>

                    {/* Right Panel - AI Assistant */}
                    <div className="assistant-panel">
                        <div className="assistant-header">
                            <div className="assistant-title">
                                <span className="status-dot online"></span>
                                <h2>AI Assistant</h2>
                            </div>

                            {/* Mode tabs */}
                            <div className="mode-tabs">
                                <button
                                    className={`mode-tab ${mode === 'PRE_PURCHASE' ? 'active' : ''}`}
                                    onClick={() => handleModeSwitch('PRE_PURCHASE')}
                                >
                                    Pre-Purchase
                                </button>
                                <button
                                    className={`mode-tab ${mode === 'POST_PURCHASE' ? 'active' : ''}`}
                                    onClick={() => handleModeSwitch('POST_PURCHASE')}
                                >
                                    Support
                                </button>
                            </div>
                        </div>

                        {/* Chat area */}
                        <div className="chat-area" ref={chatAreaRef}>
                            <div className="welcome-message">
                                <p>👋 Hello! I'm your {product.brand} {product.name} assistant. How can I help you today?</p>
                            </div>

                            {messages.map((msg, idx) => (
                                <div key={idx} className={`chat-message ${msg.role}`}>
                                    {msg.imagePreview && msg.role === 'user' && (
                                        <img
                                            src={msg.imagePreview}
                                            alt="uploaded image"
                                            className="message-image"
                                        />
                                    )}
                                    <div className="message-content">
                                        {msg.content}
                                    </div>
                                </div>
                            ))}

                            {isSending && (
                                <div className="chat-message assistant">
                                    <div className="message-content typing">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input area */}
                        <div className="input-area-wrapper">
                            {/* Image gallery preview */}
                            {imagePreviews.length > 0 && (
                                <div className="image-gallery-preview">
                                    {imagePreviews.map((preview, idx) => (
                                        <div key={idx} className="preview-item">
                                            <img src={preview} alt={`Preview ${idx + 1}`} className="preview-thumbnail" />
                                            <button
                                                className="btn-remove-preview"
                                                onClick={() => handleRemoveImage(idx)}
                                                title="Remove image"
                                            >
                                                <X size={14} />
                                            </button>
                                        </div>
                                    ))}
                                    <span className="image-count">
                                        {selectedImages.length}/{MAX_IMAGES}
                                    </span>
                                </div>
                            )}

                            {/* Upload error */}
                            {uploadError && (
                                <div className="upload-error">
                                    ❌ {uploadError}
                                </div>
                            )}

                            <div className="message-input-container">
                                {/* Hidden file input for multiple images */}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    multiple
                                    style={{ display: 'none' }}
                                    onChange={handleImageSelect}
                                />

                                {/* Camera icon button */}
                                <button
                                    className="btn-camera"
                                    onClick={() => fileInputRef.current?.click()}
                                    title="Upload image"
                                    disabled={isSending}
                                >
                                    <Camera size={20} />
                                </button>

                                <input
                                    type="text"
                                    placeholder="Ask about size, features, warranty..."
                                    className="message-input"
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                />
                                <button
                                    className="btn-send"
                                    onClick={handleSendMessage}
                                    disabled={isSending || (!inputMessage.trim() && selectedImages.length === 0)}
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
