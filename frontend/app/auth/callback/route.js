import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase/server'

/**
 * Auth callback route handler
 * Handles redirects from Supabase after email verification and OAuth
 * This route MUST use the server client with proper cookie management
 */
export async function GET(request) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const error = requestUrl.searchParams.get('error')
    const error_code = requestUrl.searchParams.get('error_code')
    const error_description = requestUrl.searchParams.get('error_description')
    const origin = requestUrl.origin

    console.log('Auth callback called with:', { code: !!code, error, error_code, error_description })

    // Handle error cases from Supabase
    if (error || error_code) {
        console.error('Auth error from Supabase:', error_code || error, error_description)
        const errorMessage = error_description || error || 'Authentication failed'
        return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(errorMessage)}`)
    }

    // Exchange the code for a session
    if (code) {
        try {
            const supabase = await createServerSupabaseClient()

            // Exchange code for session - this sets the auth cookies
            const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)

            if (exchangeError) {
                console.error('Error exchanging code for session:', exchangeError)
                return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(exchangeError.message)}`)
            }

            console.log('Successfully authenticated user:', data.user?.email)

            // Successful authentication - redirect to home
            return NextResponse.redirect(`${origin}/`)
        } catch (err) {
            console.error('Unexpected error in auth callback:', err)
            return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent('Authentication failed')}`)
        }
    }

    // No code or error provided
    console.error('Auth callback called without code or error')
    return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent('Invalid authentication request')}`)
}
