// Main JavaScript file for Online Tools Hub

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Tool search functionality
const toolSearch = document.getElementById('toolSearch');
const toolCategories = document.querySelectorAll('.tool-category');

if (toolSearch) {
    toolSearch.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        
        toolCategories.forEach(category => {
            const tools = category.querySelectorAll('.tool-list a');
            let hasMatch = false;
            
            tools.forEach(tool => {
                const toolName = tool.textContent.toLowerCase();
                if (toolName.includes(searchTerm)) {
                    tool.style.display = 'block';
                    hasMatch = true;
                } else {
                    tool.style.display = 'none';
                }
            });
            
            // Show/hide entire category based on matches
            if (hasMatch || searchTerm === '') {
                category.style.display = 'block';
            } else {
                category.style.display = 'none';
            }
        });
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Copy to clipboard functionality (for tool pages)
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.backgroundColor = '#10b981';
        
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

// Common utility functions for tools
const ToolUtils = {
    // Text manipulation utilities
    convertCase: function(text, caseType) {
        switch(caseType) {
            case 'upper':
                return text.toUpperCase();
            case 'lower':
                return text.toLowerCase();
            case 'title':
                return text.replace(/\w\S*/g, (txt) => 
                    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
                );
            case 'camel':
                return text.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => 
                    index === 0 ? word.toLowerCase() : word.toUpperCase()
                ).replace(/\s+/g, '');
            case 'pascal':
                return text.replace(/(?:^\w|[A-Z]|\b\w)/g, (word) => 
                    word.toUpperCase()
                ).replace(/\s+/g, '');
            case 'snake':
                return text.toLowerCase().replace(/\s+/g, '_');
            case 'kebab':
                return text.toLowerCase().replace(/\s+/g, '-');
            default:
                return text;
        }
    },
    
    // Word and character counting
    countWords: function(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    },
    
    countCharacters: function(text, includeSpaces = true) {
        return includeSpaces ? text.length : text.replace(/\s/g, '').length;
    },
    
    // Base64 encoding/decoding
    base64Encode: function(text) {
        try {
            return btoa(unescape(encodeURIComponent(text)));
        } catch (e) {
            return 'Error: Invalid input for Base64 encoding';
        }
    },
    
    base64Decode: function(text) {
        try {
            return decodeURIComponent(escape(atob(text)));
        } catch (e) {
            return 'Error: Invalid Base64 input';
        }
    },
    
    // URL encoding/decoding
    urlEncode: function(text) {
        return encodeURIComponent(text);
    },
    
    urlDecode: function(text) {
        try {
            return decodeURIComponent(text);
        } catch (e) {
            return 'Error: Invalid URL-encoded input';
        }
    },
    
    // Generate random password
    generatePassword: function(length = 12, options = {}) {
        const defaults = {
            uppercase: true,
            lowercase: true,
            numbers: true,
            symbols: true
        };
        
        const settings = { ...defaults, ...options };
        let charset = '';
        
        if (settings.lowercase) charset += 'abcdefghijklmnopqrstuvwxyz';
        if (settings.uppercase) charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        if (settings.numbers) charset += '0123456789';
        if (settings.symbols) charset += '!@#$%^&*()_+-=[]{}|;:,.<>?';
        
        if (!charset) return 'Error: No character types selected';
        
        let password = '';
        for (let i = 0; i < length; i++) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        
        return password;
    },
    
    // Generate UUID
    generateUUID: function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },
    
    // Hash functions (simple demonstration - for real use, implement proper libraries)
    simpleHash: function(text, algorithm = 'MD5') {
        // This is a placeholder - in real implementation, use proper crypto libraries
        let hash = 0;
        for (let i = 0; i < text.length; i++) {
            const char = text.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(16).padStart(8, '0');
    },
    
    // JSON formatting
    formatJSON: function(text) {
        try {
            const parsed = JSON.parse(text);
            return JSON.stringify(parsed, null, 2);
        } catch (e) {
            return 'Error: Invalid JSON input';
        }
    },
    
    // Minify JSON
    minifyJSON: function(text) {
        try {
            const parsed = JSON.parse(text);
            return JSON.stringify(parsed);
        } catch (e) {
            return 'Error: Invalid JSON input';
        }
    }
};

// Export utilities for use in tool pages
window.ToolUtils = ToolUtils;
window.copyToClipboard = copyToClipboard;