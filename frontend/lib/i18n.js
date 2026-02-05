/**
 * Simple i18n helper for bilingual chat
 * Supports English and Hindi
 */

import enTranslations from '../i18n/en.json';
import hiTranslations from '../i18n/hi.json';

const translations = {
    en: enTranslations,
    hi: hiTranslations,
};

/**
 * Get translation for a key
 * @param {string} language - 'en' or 'hi'
 * @param {string} key - Translation key (e.g., 'chat.title')
 * @returns {string} Translated text
 */
export function useTranslation(language = 'en') {
    const t = (key) => {
        const keys = key.split('.');
        let value = translations[language] || translations.en;

        for (const k of keys) {
            value = value?.[k];
            if (!value) break;
        }

        return value || key; // Fallback to key if not found
    };

    return { t };
}

/**
 * Get current language from localStorage
 */
export function getCurrentLanguage() {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('chatLanguage') || 'en';
    }
    return 'en';
}

/**
 * Set language in localStorage
 */
export function setCurrentLanguage(language) {
    if (typeof window !== 'undefined') {
        localStorage.setItem('chatLanguage', language);
    }
}
