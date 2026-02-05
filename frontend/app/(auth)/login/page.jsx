'use client'
import { useState, useEffect, Suspense } from 'react';
import { auth } from '@/lib/auth';
import { useRouter, useSearchParams } from 'next/navigation';

function LoginForm() {
    const [mounted, setMounted] = useState(false);
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [googleLoading, setGoogleLoading] = useState(false);
    const [message, setMessage] = useState('');
    const router = useRouter();
    const searchParams = useSearchParams();

    // Prevent SSR hydration mismatch and check for errors in URL
    useEffect(() => {
        setMounted(true);

        // Check for error in URL parameters
        const error = searchParams.get('error');
        if (error) {
            setMessage('❌ ' + decodeURIComponent(error));
        }
    }, [searchParams]);

    const handleEmailLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        const { error } = await auth.signInWithEmail(email);

        if (error) {
            setMessage('❌ Error: ' + error.message);
        } else {
            setMessage('✅ Check your email for the magic link!');
        }
        setLoading(false);
    };

    const handleGoogleLogin = async () => {
        setGoogleLoading(true);
        setMessage('');

        const { error } = await auth.signInWithGoogle();

        if (error) {
            setMessage('❌ Error: ' + error.message);
            setGoogleLoading(false);
        }
        // Note: User will be redirected to Google, so no need to setLoading(false)
    };

    const handleGoHome = () => {
        router.push('/');
    };

    if (!mounted) return null;

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="text-4xl mb-3">🛒</div>
                    <h1 className="text-3xl font-bold text-slate-800 mb-2">Welcome to GoCart</h1>
                    <p className="text-sm text-slate-500">Sign in to save your chat history and orders</p>
                </div>

                {/* Email Login Form */}
                <form onSubmit={handleEmailLogin} className="space-y-4 mb-6">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
                            Email Address
                        </label>
                        <input
                            id="email"
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            disabled={loading}
                            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-800 focus:border-transparent outline-none transition disabled:opacity-50"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-slate-800 text-white py-3 rounded-lg font-medium hover:bg-slate-900 active:scale-98 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Sending...' : 'Send Magic Link'}
                    </button>
                </form>

                {/* Divider */}
                <div className="flex items-center gap-3 my-6">
                    <div className="flex-1 border-t border-slate-200"></div>
                    <span className="text-xs text-slate-400">OR</span>
                    <div className="flex-1 border-t border-slate-200"></div>
                </div>

                {/* Google Login */}
                <button
                    onClick={handleGoogleLogin}
                    disabled={googleLoading}
                    className="w-full bg-white border-2 border-slate-200 text-slate-700 py-3 rounded-lg font-medium hover:bg-slate-50 active:scale-98 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                    </svg>
                    {googleLoading ? 'Connecting...' : 'Continue with Google'}
                </button>

                {/* Message */}
                {message && (
                    <div className={`mt-4 text-sm text-center p-3 rounded-lg ${message.startsWith('✅')
                        ? 'bg-green-50 text-green-700 border border-green-200'
                        : 'bg-red-50 text-red-700 border border-red-200'
                        }`}>
                        {message}
                    </div>
                )}

                {/* Back to Home */}
                <button
                    onClick={handleGoHome}
                    className="w-full text-sm text-slate-500 hover:text-slate-700 py-2"
                >
                    ← Back to Shopping
                </button>

                {/* Footer */}
                <p className="text-xs text-center text-slate-400 mt-6">
                    By continuing, you agree to our Terms & Privacy Policy
                </p>
            </div>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-slate-300 border-t-slate-800 rounded-full animate-spin mx-auto"></div>
                    <p className="mt-4 text-slate-600">Loading...</p>
                </div>
            </div>
        }>
            <LoginForm />
        </Suspense>
    );
}
