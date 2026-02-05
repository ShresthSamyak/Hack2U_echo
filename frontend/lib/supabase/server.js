/**
 * Server-side Supabase client
 * Use this ONLY in server components, route handlers, and server actions
 * DO NOT import this in client components
 */

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createServerSupabaseClient() {
    const cookieStore = await cookies()

    return createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll()
                },
                setAll(cookiesToSet) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) => {
                            cookieStore.set(name, value, options)
                        })
                    } catch (error) {
                        // Handle cookie errors (can happen in some server contexts)
                        console.error('Error setting cookies:', error)
                    }
                }
            }
        }
    )
}
