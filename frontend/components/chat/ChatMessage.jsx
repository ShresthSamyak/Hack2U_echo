'use client'
import { MessageCircle } from 'lucide-react';
import FormattedMessage from './FormattedMessage';

const ChatMessage = ({ message, isUser, isLoading }) => {

    if (isLoading) {
        return (
            <div className="flex gap-3 mb-4">
                <div className="bg-slate-100 rounded-full p-2 h-fit">
                    <MessageCircle size={16} className="text-slate-600" />
                </div>
                <div className="flex-1 bg-white p-4 rounded-lg border border-slate-200 max-w-lg">
                    <div className="flex gap-2">
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`flex gap-3 mb-6 ${isUser ? 'flex-row-reverse' : ''}`}>
            {!isUser && (
                <div className="bg-green-50 rounded-full p-2.5 h-fit ring-2 ring-green-100">
                    <MessageCircle size={18} className="text-green-600" />
                </div>
            )}
            <div
                className={`flex-1 px-5 py-4 rounded-2xl max-w-2xl shadow-sm ${isUser
                    ? 'bg-slate-800 text-white ml-auto'
                    : 'bg-white border border-slate-100 text-slate-800'
                    }`}
            >
                {isUser ? (
                    <p className="text-[15px] leading-relaxed">{message}</p>
                ) : (
                    <FormattedMessage text={message} />
                )}
            </div>
        </div>
    );
};

export default ChatMessage;

