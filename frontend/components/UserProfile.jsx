'use client'
import { useState, useEffect, useRef } from 'react';
import { LogOut, User } from 'lucide-react';
import { auth } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export default function UserProfile() {
    const [user, setUser] = useState(null);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const dropdownRef = useRef(null);
    const router = useRouter();

    useEffect(() => {
        // Get initial user
        const getInitialUser = async () => {
            const currentUser = await auth.getUser();
            setUser(currentUser);
            setLoading(false);
        };

        getInitialUser();

        // Listen for auth changes
        const { data: { subscription } } = auth.onAuthStateChange((event, session) => {
            setUser(session?.user || null);
        });

        // Cleanup subscription
        return () => {
            subscription?.unsubscribe();
        };
    }, []);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSignOut = async () => {
        await auth.signOut();
        setIsOpen(false);
        router.push('/');
    };

    if (loading) {
        return (
            <div className="w-10 h-10 rounded-full bg-slate-200 animate-pulse"></div>
        );
    }

    if (!user) {
        return null;
    }

    // Get user initials or first letter of email
    const getInitials = () => {
        if (user.user_metadata?.full_name) {
            return user.user_metadata.full_name
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .slice(0, 2);
        }
        return user.email?.[0]?.toUpperCase() || 'U';
    };

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Profile Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 rounded-full hover:bg-slate-100 transition"
            >
                <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-sm font-medium">
                    {getInitials()}
                </div>
                <span className="hidden md:block text-sm text-slate-700 max-w-[150px] truncate">
                    {user.user_metadata?.full_name || user.email}
                </span>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-slate-200 overflow-hidden z-50">
                    {/* User Info */}
                    <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-medium">
                                {getInitials()}
                            </div>
                            <div className="flex-1 min-w-0">
                                {user.user_metadata?.full_name && (
                                    <p className="text-sm font-medium text-slate-900 truncate">
                                        {user.user_metadata.full_name}
                                    </p>
                                )}
                                <p className="text-xs text-slate-500 truncate">
                                    {user.email}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                router.push('/profile');
                            }}
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition"
                        >
                            <User size={16} />
                            <span>My Profile</span>
                        </button>

                        <button
                            onClick={handleSignOut}
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition"
                        >
                            <LogOut size={16} />
                            <span>Sign Out</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
