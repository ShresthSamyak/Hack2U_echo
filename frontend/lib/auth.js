/**
 * Authentication service using Supabase SSR
 * Provides email magic link and Google OAuth
 */

import { createClient } from './supabase/client';

export const auth = {
    // Sign in with email (magic link)
    async signInWithEmail(email) {
        const supabase = createClient()
        return await supabase.auth.signInWithOtp({
            email,
            options: {
                emailRedirectTo: typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : ''
            }
        });
    },

    // Sign in with Google
    async signInWithGoogle() {
        const supabase = createClient()
        return await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : ''
            }
        });
    },

    // Get current user
    async getUser() {
        const supabase = createClient()
        const { data } = await supabase.auth.getUser();
        return data.user;
    },

    // Sign out
    async signOut() {
        const supabase = createClient()
        return await supabase.auth.signOut();
    },

    // Listen to auth changes
    onAuthStateChange(callback) {
        const supabase = createClient()
        return supabase.auth.onAuthStateChange(callback);
    }
};

