'use client'
import { useState, useEffect, useRef } from 'react';
import { useTranslation, getCurrentLanguage, setCurrentLanguage } from '@/lib/i18n';
import { sendChatMessage, getSessionId } from '@/lib/chatApi';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LanguageToggle from './LanguageToggle';
import { MessageSquare } from 'lucide-react';

const ProductChatWidget = ({ product }) => {
    const [mounted, setMounted] = useState(false);
    const [language, setLanguage] = useState('en');
    const [mode, setMode] = useState('PRE_PURCHASE');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState('');
    const messagesEndRef = useRef(null);
    const { t } = useTranslation(language);

    // Prevent SSR hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    // Initialize language and session (client-only)
    useEffect(() => {
        if (!mounted) return;

        const savedLanguage = getCurrentLanguage();
        setLanguage(savedLanguage);
        setSessionId(getSessionId(product.id));
    }, [mounted, product.id]);

    // Add welcome message after session is ready
    useEffect(() => {
        if (sessionId && messages.length === 0) {
            setMessages([
                {
                    id: 'welcome',
                    text: t('chat.welcome'),
                    isUser: false,
                    timestamp: new Date(),
                },
            ]);
        }
    }, [sessionId, t]);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleLanguageChange = (newLanguage) => {
        setLanguage(newLanguage);
        setCurrentLanguage(newLanguage);
    };

    const handleSendMessage = async ({ message, image }) => {
        if (!message.trim() && !image) return;

        // Add user message
        const userMessage = {
            id: Date.now().toString(),
            text: message,
            isUser: true,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Send to backend with current mode
            const response = await sendChatMessage({
                productId: product.id,
                message: message,
                sessionId: sessionId,
                language: language,
                mode: mode,
                images: image ? [image] : [],
            });

            // Add AI response
            const aiMessage = {
                id: (Date.now() + 1).toString(),
                text: response.response || response.message || 'I received your message.',
                isUser: false,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            // Add error message
            const errorMessage = {
                id: (Date.now() + 1).toString(),
                text: t('chat.error'),
                isUser: false,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    // Don't render until mounted on client (prevents SSR hydration errors)
    if (!mounted) {
        return null;
    }

    return (
        <div className="my-18">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div className="flex items-center gap-3">
                    <div className="bg-green-500 rounded-full p-2">
                        <MessageSquare size={20} className="text-white" />
                    </div>
                    <h2 className="text-2xl font-semibold text-slate-800">{t('chat.title')}</h2>
                </div>
                <div className="flex items-center gap-3">
                    {/* Mode Toggle */}
                    <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
                        <button
                            onClick={() => setMode('PRE_PURCHASE')}
                            className={`px-3 py-1.5 text-xs font-medium rounded transition ${mode === 'PRE_PURCHASE'
                                    ? 'bg-blue-500 text-white shadow-sm'
                                    : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            🛒 Shopping
                        </button>
                        <button
                            onClick={() => setMode('POST_PURCHASE')}
                            className={`px-3 py-1.5 text-xs font-medium rounded transition ${mode === 'POST_PURCHASE'
                                    ? 'bg-orange-500 text-white shadow-sm'
                                    : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            🔧 Support
                        </button>
                    </div>
                    {/* Language Toggle */}
                    <LanguageToggle currentLanguage={language} onLanguageChange={handleLanguageChange} />
                </div>
            </div>

            {/* Mode Indicator */}
            <div className="mb-4">
                <p className="text-xs text-slate-500">
                    {mode === 'PRE_PURCHASE'
                        ? '💡 Shopping mode: Ask about features, pricing, and recommendations'
                        : '🛠️ Support mode: Get help with setup, troubleshooting, and maintenance'}
                </p>
            </div>

            {/* Chat Container */}
            <div className="bg-slate-50 rounded-lg border border-slate-200 p-6">
                {/* Messages */}
                <div className="h-96 overflow-y-auto mb-4 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100">
                    {messages.length === 0 ? (
                        <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                            {t('chat.noMessages')}
                        </div>
                    ) : (
                        messages.map((msg) => (
                            <ChatMessage
                                key={msg.id}
                                message={msg.text}
                                isUser={msg.isUser}
                                isLoading={false}
                            />
                        ))
                    )}
                    {isLoading && <ChatMessage isLoading={true} />}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <ChatInput
                    onSend={handleSendMessage}
                    disabled={isLoading}
                    placeholder={t('chat.placeholder')}
                />
            </div>

            {/* Product Context Info */}
            <p className="text-xs text-slate-400 mt-3">
                Chatting about: {product.name}
            </p>
        </div>
    );
};

export default ProductChatWidget;
