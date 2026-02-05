'use client'
import { Send, ImageIcon, X } from 'lucide-react';
import { useState, useRef } from 'react';

const ChatInput = ({ onSend, disabled, placeholder }) => {
    const [message, setMessage] = useState('');
    const [selectedImage, setSelectedImage] = useState(null);
    const fileInputRef = useRef(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!message.trim() && !selectedImage) return;

        onSend({ message: message.trim(), image: selectedImage });
        setMessage('');
        setSelectedImage(null);
    };

    const handleImageSelect = (e) => {
        const file = e.target.files?.[0];
        if (file && file.type.startsWith('image/')) {
            setSelectedImage(file);
        }
    };

    return (
        <div className="space-y-3">
            {/* Image Preview - Shows ABOVE input when image selected */}
            {selectedImage && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-3">
                    <img
                        src={URL.createObjectURL(selectedImage)}
                        alt="Preview"
                        className="w-16 h-16 object-cover rounded border-2 border-blue-300"
                    />
                    <div className="flex-1">
                        <p className="text-sm font-medium text-slate-800">📷 Image attached</p>
                        <p className="text-xs text-slate-500 truncate">{selectedImage.name}</p>
                    </div>
                    <button
                        type="button"
                        onClick={() => setSelectedImage(null)}
                        className="text-slate-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition"
                        title="Remove image"
                    >
                        <X size={18} />
                    </button>
                </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex gap-2">
                <div className="flex-1 flex gap-2 bg-white border border-slate-200 rounded-lg p-2">
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder={placeholder}
                        disabled={disabled}
                        className="flex-1 resize-none outline-none text-sm text-slate-800 placeholder:text-slate-400 min-h-[40px] max-h-[120px]"
                        rows={1}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                    />
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleImageSelect}
                        accept="image/*"
                        className="hidden"
                    />
                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={disabled}
                        className={`p-2 rounded transition ${selectedImage
                                ? 'text-blue-500 bg-blue-50 hover:bg-blue-100'
                                : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100'
                            }`}
                        title="Upload image"
                    >
                        <ImageIcon size={18} />
                    </button>
                </div>
                <button
                    type="submit"
                    disabled={disabled || (!message.trim() && !selectedImage)}
                    className="bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-900 active:scale-95 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Send message"
                >
                    <Send size={18} />
                </button>
            </form>
        </div>
    );
};

export default ChatInput;
