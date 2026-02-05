'use client'

const LanguageToggle = ({ currentLanguage, onLanguageChange }) => {
    const languages = [
        { code: 'en', label: 'EN' },
        { code: 'hi', label: 'हिं' },
    ];

    return (
        <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
            {languages.map(({ code, label }) => (
                <button
                    key={code}
                    onClick={() => onLanguageChange(code)}
                    className={`px-3 py-1.5 text-sm font-medium rounded transition ${currentLanguage === code
                            ? 'bg-white text-slate-800 shadow-sm'
                            : 'text-slate-500 hover:text-slate-700'
                        }`}
                >
                    {label}
                </button>
            ))}
        </div>
    );
};

export default LanguageToggle;
