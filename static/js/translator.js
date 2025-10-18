/**
 * JalJeevan.AI Translation System
 * Multilingual support for entire website
 */

class PageTranslator {
    constructor() {
        this.currentLang = localStorage.getItem('siteLanguage') || 'en';
        this.apiEndpoint = '/api/translate/batch/';
        this.isTranslating = false;
        
        this.init();
    }
    
    init() {
        console.log('🌍 Translation System Initialized');
        this.setupLanguageSwitcher();
        this.updateLanguageDisplay();
        
        // Auto-translate if not English
        if (this.currentLang !== 'en') {
            this.translatePage(this.currentLang);
        }
    }
    
    setupLanguageSwitcher() {
        const btn = document.getElementById('languageBtn');
        const dropdown = document.getElementById('languageDropdown');
        const options = document.querySelectorAll('.language-option');
        
        if (!btn || !dropdown) {
            console.warn('⚠️ Language switcher not found');
            return;
        }
        
        // Toggle dropdown
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });
        
        // Close on outside click
        document.addEventListener('click', () => {
            dropdown.classList.remove('show');
        });
        
        // Language selection
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                const lang = option.dataset.lang;
                const name = option.dataset.name;
                this.changeLanguage(lang, name);
                dropdown.classList.remove('show');
            });
        });
    }
    
    changeLanguage(lang, name) {
        if (this.isTranslating) return;
        
        console.log(`🔄 Switching to: ${name}`);
        
        localStorage.setItem('siteLanguage', lang);
        this.currentLang = lang;
        
        // Update button text
        document.getElementById('currentLanguage').textContent = name;
        
        if (lang === 'en') {
            location.reload(); // Reload to show original English
        } else {
            this.translatePage(lang);
        }
    }
    
    async translatePage(targetLang) {
        if (this.isTranslating) return;
        
        this.isTranslating = true;
        this.showLoadingOverlay();
        
        try {
            // Collect all text to translate
            const elements = this.getTranslatableElements();
            const texts = elements.map(el => this.getElementText(el));
            
            console.log(`📝 Found ${texts.length} elements to translate`);
            
            // Translate in batches
            const batchSize = 50;
            const allTranslations = [];
            
            for (let i = 0; i < texts.length; i += batchSize) {
                const batch = texts.slice(i, i + batchSize);
                const translations = await this.callTranslationAPI(batch, targetLang);
                allTranslations.push(...translations);
                
                console.log(`✅ Batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(texts.length/batchSize)} done`);
            }
            
            // Apply translations
            elements.forEach((el, idx) => {
                this.setElementText(el, allTranslations[idx]);
            });
            
            console.log('🎉 Page translated successfully!');
            
        } catch (error) {
            console.error('❌ Translation failed:', error);
            alert('Translation failed. Please try again or use English.');
        } finally {
            this.isTranslating = false;
            this.hideLoadingOverlay();
        }
    }
    
    getTranslatableElements() {
        // Get all text elements
        const selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'span', 'a', 'button', 'label',
            'li', 'td', 'th', '.translate'
        ];
        
        const elements = [];
        
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                const text = this.getElementText(el);
                if (text && !this.shouldSkip(el, text)) {
                    elements.push(el);
                }
            });
        });
        
        return this.removeDuplicates(elements);
    }
    
    shouldSkip(element, text) {
        // Skip if marked with data-no-translate
        if (element.hasAttribute('data-no-translate')) return true;
        
        // Skip if already translated
        if (element.hasAttribute('data-translated')) return true;
        
        // Skip numbers only
        if (/^\d+$/.test(text.trim())) return true;
        
        // Skip very short text
        if (text.trim().length < 2) return true;
        
        // Skip script/style/code
        if (element.closest('script, style, code, pre')) return true;
        
        return false;
    }
    
    getElementText(element) {
        // Get direct text only (not child elements)
        let text = '';
        element.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
                text += node.textContent;
            }
        });
        return text.trim();
    }
    
    setElementText(element, translatedText) {
        // Replace text nodes with translation
        element.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                node.textContent = translatedText;
            }
        });
        
        element.setAttribute('data-translated', 'true');
        
        // Translate placeholders
        if (element.placeholder) {
            this.callTranslationAPI([element.placeholder], this.currentLang)
                .then(t => element.placeholder = t[0]);
        }
    }
    
    removeDuplicates(elements) {
        // Remove nested elements (keep parent only)
        return elements.filter(el => {
            return !elements.some(other => 
                other !== el && other.contains(el)
            );
        });
    }
    
    async callTranslationAPI(texts, targetLang) {
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    texts: texts,
                    target_language: targetLang
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                return data.translations;
            } else {
                throw new Error(data.error || 'Translation failed');
            }
            
        } catch (error) {
            console.error('API Error:', error);
            return texts; // Return original on error
        }
    }
    
    showLoadingOverlay() {
        let overlay = document.getElementById('translationOverlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'translationOverlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.8); z-index: 99999;
                display: flex; align-items: center; justify-content: center;
            `;
            overlay.innerHTML = `
                <div style="background: white; padding: 30px; border-radius: 15px; text-align: center;">
                    <div style="font-size: 40px; margin-bottom: 15px;">🌍</div>
                    <h3 style="margin: 0 0 10px 0;">Translating page...</h3>
                    <p style="margin: 0; color: #666;">Please wait</p>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        
        overlay.style.display = 'flex';
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('translationOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    updateLanguageDisplay() {
        const langNames = {
            'en': 'English',
            'hi': 'हिन्दी',
            'bn': 'বাংলা',
            'ta': 'தமிழ்',
            'mr': 'मराठी'
        };
        
        const currentLangEl = document.getElementById('currentLanguage');
        if (currentLangEl) {
            currentLangEl.textContent = langNames[this.currentLang] || 'English';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.pageTranslator = new PageTranslator();
});
