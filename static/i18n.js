let translations = {};
let currentLanguage = localStorage.getItem('language') || 'de'; // Default to German

// Load translations
async function loadTranslations() {
    try {
        const response = await fetch('/static/translations.json');
        translations = await response.json();
        await setLanguage(currentLanguage);
    } catch (error) {
        console.error('Failed to load translations:', error);
    }
}

// Set language and update UI
async function setLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Language ${lang} not available`);
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = getNestedTranslation(translations[lang], key);
        if (translation) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translation;
            } else {
                element.textContent = translation;
            }
        }
    });
    
    // Update the page title
    document.title = translations[lang].title;
    
    // Update button states in language selector
    document.querySelectorAll('.btn-group button').forEach(button => {
        const buttonLang = button.getAttribute('onclick').match(/'(.+)'/)[1];
        if (buttonLang === lang) {
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-primary');
        } else {
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-primary');
        }
    });
}

// Helper to get nested translation keys (e.g., "status.currentPosition")
function getNestedTranslation(obj, path) {
    return path.split('.').reduce((p, c) => p && p[c], obj);
}

// Get translation for a key
function t(key) {
    const result = getNestedTranslation(translations[currentLanguage], key);
    if (!result) {
        console.warn(`Translation not found for key: ${key}`);
        return key;  // Return the key as fallback
    }
    return result;
}

// Initialize translations - load them synchronously by waiting
let translationsReady = false;

async function initTranslations() {
    try {
        const response = await fetch('/static/translations.json');
        translations = await response.json();
        translationsReady = true;
        await setLanguage(currentLanguage);
        console.log('Translations loaded successfully');
    } catch (error) {
        console.error('Failed to load translations:', error);
        translationsReady = false;
    }
}

// Start loading translations immediately
initTranslations();