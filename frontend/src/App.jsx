import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import {
  Send,
  Camera,
  RotateCcw,
  ShoppingCart,
  Wrench,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import ImageUpload from './components/ImageUpload';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('PRE_PURCHASE');
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [roomAnalysis, setRoomAnalysis] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initial greeting
    const greeting = mode === 'PRE_PURCHASE'
      ? `Hello! I'm your product intelligence assistant. I'm here to help you find the perfect product for your needs. Would you like to explore our washing machines, refrigerators, headphones, or EV batteries?`
      : `Hello! I'm here to help you with setup, troubleshooting, and getting the most out of your product. What can I assist you with today?`;

    setMessages([{ text: greeting, isUser: false }]);
  }, [mode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage = { text: message, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: message,
        conversation_id: 'default'
      });

      // Add agent response
      setMessages(prev => [...prev, {
        text: response.data.response,
        isUser: false
      }]);

      if (response.data.suggestions) {
        setSuggestions(response.data.suggestions);
      }

    } catch (error) {
      setMessages(prev => [...prev, {
        text: 'Sorry, I encountered an error. Please make sure the backend is running and try again.',
        isUser: false
      }]);
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageUpload = async (file) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/analyze-room`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setRoomAnalysis(response.data.analysis);

      // Add analysis to chat
      setMessages(prev => [...prev,
      { text: '📸 Analyzing your room...', isUser: true },
      {
        text: `**Room Analysis:**\n\n${response.data.analysis}\n\n${response.data.confidence}`,
        isUser: false
      }
      ]);

      setShowImageUpload(false);
    } catch (error) {
      setMessages(prev => [...prev, {
        text: 'Failed to analyze image. Please ensure the image is clear and try again.',
        isUser: false
      }]);
      console.error('Image analysis error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const switchMode = async (newMode) => {
    try {
      await axios.post(`${API_BASE}/mode`, { mode: newMode });
      setMode(newMode);
      setMessages([]);
      setRoomAnalysis(null);
      setSuggestions([]);
    } catch (error) {
      console.error('Mode switch error:', error);
    }
  };

  const resetConversation = async () => {
    try {
      await axios.post(`${API_BASE}/reset`);
      setMessages([]);
      setRoomAnalysis(null);
      setSuggestions([]);
    } catch (error) {
      console.error('Reset error:', error);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header glass-card">
        <div className="header-content">
          <div className="brand">
            <Sparkles size={28} className="brand-icon" />
            <h1>TechHome Assistant</h1>
          </div>

          <div className="mode-controls">
            <button
              className={`mode-btn ${mode === 'PRE_PURCHASE' ? 'active' : ''}`}
              onClick={() => switchMode('PRE_PURCHASE')}
            >
              <ShoppingCart size={18} />
              <span>Pre-Purchase</span>
            </button>
            <button
              className={`mode-btn ${mode === 'POST_PURCHASE' ? 'active' : ''}`}
              onClick={() => switchMode('POST_PURCHASE')}
            >
              <Wrench size={18} />
              <span>Support</span>
            </button>
          </div>
        </div>

        <div className={`mode-badge ${mode === 'PRE_PURCHASE' ? 'badge-pre' : 'badge-post'}`}>
          {mode === 'PRE_PURCHASE' ? '🛍️ Shopping Mode' : '🔧 Support Mode'}
        </div>
      </header>

      {/* Chat Area */}
      <main className="chat-container">
        <div className="messages-area">
          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message.text}
              isUser={message.isUser}
            />
          ))}

          {isLoading && <ChatMessage isLoading={true} />}

          {showImageUpload && (
            <div className="image-upload-overlay animate-slide-up">
              <ImageUpload
                onImageSelect={handleImageUpload}
                disabled={isLoading}
              />
              <button
                className="btn btn-secondary"
                onClick={() => setShowImageUpload(false)}
              >
                Cancel
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestions */}
        {suggestions.length > 0 && !isLoading && (
          <div className="suggestions">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-chip"
                onClick={() => handleSendMessage(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="input-area glass-card">
          <button
            className="icon-btn"
            onClick={() => setShowImageUpload(!showImageUpload)}
            disabled={isLoading}
            title="Upload room image"
          >
            <Camera size={20} />
          </button>

          <input
            type="text"
            className="message-input"
            placeholder={mode === 'PRE_PURCHASE'
              ? "Ask about products, features, warranty..."
              : "Describe your issue or ask for help..."
            }
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isLoading}
          />

          <button
            className="icon-btn send-btn"
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim()}
          >
            <Send size={20} />
          </button>

          <button
            className="icon-btn"
            onClick={resetConversation}
            disabled={isLoading}
            title="Reset conversation"
          >
            <RotateCcw size={18} />
          </button>
        </div>
      </main>

      {/* Backend Connection Warning */}
      {messages.length === 1 && (
        <div className="connection-notice">
          <AlertCircle size={16} />
          <span>Make sure the backend is running on port 8000</span>
        </div>
      )}
    </div>
  );
}

export default App;
