import React from 'react';
import { User, Bot, Loader2 } from 'lucide-react';
import './ChatMessage.css';

const ChatMessage = ({ message, isUser, isLoading }) => {
    if (isLoading) {
        return (
            <div className="message-container agent-message">
                <div className="message-avatar agent-avatar">
                    <Bot size={20} />
                </div>
                <div className="message-bubble glass-card">
                    <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`message-container ${isUser ? 'user-message' : 'agent-message'} animate-slide-up`}>
            <div className={`message-avatar ${isUser ? 'user-avatar' : 'agent-avatar'}`}>
                {isUser ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className={`message-bubble ${isUser ? '' : 'glass-card'}`}>
                <div className="message-content">
                    {message}
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
