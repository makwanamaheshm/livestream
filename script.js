// OnePageTools - Main JavaScript File

// Global Variables
let currentCategory = 'all';
let allTools = [];

// Tool definitions
const toolsData = {
    'word-counter': {
        title: 'Word Counter',
        category: 'text',
        description: 'Count words, characters, sentences and paragraphs in your text',
        content: `
            <div class="tool-interface">
                <div class="input-section">
                    <label for="textInput">Enter your text:</label>
                    <textarea id="textInput" placeholder="Type or paste your text here..." rows="10"></textarea>
                </div>
                <div class="output-section">
                    <div class="stats-grid">
                        <div class="stat-box">
                            <span class="stat-number" id="wordCount">0</span>
                            <span class="stat-label">Words</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number" id="charCount">0</span>
                            <span class="stat-label">Characters</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number" id="charCountNoSpaces">0</span>
                            <span class="stat-label">Characters (no spaces)</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number" id="sentenceCount">0</span>
                            <span class="stat-label">Sentences</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number" id="paragraphCount">0</span>
                            <span class="stat-label">Paragraphs</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-number" id="readingTime">0</span>
                            <span class="stat-label">Reading Time (min)</span>
                        </div>
                    </div>
                </div>
            </div>
        `,
        init: function() {
            const textInput = document.getElementById('textInput');
            textInput.addEventListener('input', this.updateStats);
        },
        updateStats: function() {
            const text = document.getElementById('textInput').value;
            
            // Words
            const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
            document.getElementById('wordCount').textContent = words;
            
            // Characters
            document.getElementById('charCount').textContent = text.length;
            document.getElementById('charCountNoSpaces').textContent = text.replace(/\s/g, '').length;
            
            // Sentences
            const sentences = text.trim() === '' ? 0 : text.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
            document.getElementById('sentenceCount').textContent = sentences;
            
            // Paragraphs
            const paragraphs = text.trim() === '' ? 0 : text.split(/\n\s*\n/).filter(p => p.trim().length > 0).length;
            document.getElementById('paragraphCount').textContent = paragraphs;
            
            // Reading time (average 200 words per minute)
            const readingTime = Math.ceil(words / 200);
            document.getElementById('readingTime').textContent = readingTime;
        }
    },
    
    'case-converter': {
        title: 'Case Converter',
        category: 'text',
        description: 'Convert text to uppercase, lowercase, title case, and more',
        content: `
            <div class="tool-interface">
                <div class="input-section">
                    <label for="caseInput">Enter your text:</label>
                    <textarea id="caseInput" placeholder="Type or paste your text here..." rows="6"></textarea>
                </div>
                <div class="button-section">
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('upper')">UPPERCASE</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('lower')">lowercase</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('title')">Title Case</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('sentence')">Sentence case</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('camel')">camelCase</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('pascal')">PascalCase</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('snake')">snake_case</button>
                    <button class="tool-button" onclick="toolsData['case-converter'].convertCase('kebab')">kebab-case</button>
                </div>
                <div class="output-section">
                    <label for="caseOutput">Result:</label>
                    <textarea id="caseOutput" placeholder="Converted text will appear here..." rows="6" readonly></textarea>
                    <button class="copy-button" onclick="copyToClipboard('caseOutput')">
                        <i class="fas fa-copy"></i> Copy Result
                    </button>
                </div>
            </div>
        `,
        convertCase: function(type) {
            const input = document.getElementById('caseInput').value;
            const output = document.getElementById('caseOutput');
            
            let result = '';
            switch(type) {
                case 'upper':
                    result = input.toUpperCase();
                    break;
                case 'lower':
                    result = input.toLowerCase();
                    break;
                case 'title':
                    result = input.replace(/\w\S*/g, (txt) => 
                        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
                    break;
                case 'sentence':
                    result = input.toLowerCase().replace(/(^\s*\w|[.!?]\s*\w)/g, (c) => c.toUpperCase());
                    break;
                case 'camel':
                    result = input.replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) =>
                        index === 0 ? word.toLowerCase() : word.toUpperCase()).replace(/\s+/g, '');
                    break;
                case 'pascal':
                    result = input.replace(/(?:^\w|[A-Z]|\b\w)/g, (word) =>
                        word.toUpperCase()).replace(/\s+/g, '');
                    break;
                case 'snake':
                    result = input.toLowerCase().replace(/\s+/g, '_');
                    break;
                case 'kebab':
                    result = input.toLowerCase().replace(/\s+/g, '-');
                    break;
            }
            
            output.value = result;
        }
    },
    
    'password-generator': {
        title: 'Password Generator',
        category: 'generator',
        description: 'Generate secure passwords with customizable options',
        content: `
            <div class="tool-interface">
                <div class="options-section">
                    <div class="option-group">
                        <label for="passwordLength">Password Length:</label>
                        <input type="range" id="passwordLength" min="4" max="128" value="16" oninput="document.getElementById('lengthValue').textContent = this.value">
                        <span id="lengthValue">16</span>
                    </div>
                    
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="includeUppercase" checked>
                            Include Uppercase Letters (A-Z)
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="includeLowercase" checked>
                            Include Lowercase Letters (a-z)
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="includeNumbers" checked>
                            Include Numbers (0-9)
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="includeSymbols">
                            Include Symbols (!@#$%^&*)
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="excludeSimilar">
                            Exclude Similar Characters (0, O, l, I, 1)
                        </label>
                    </div>
                    
                    <button class="tool-button primary" onclick="toolsData['password-generator'].generatePassword()">
                        <i class="fas fa-sync-alt"></i> Generate Password
                    </button>
                </div>
                
                <div class="output-section">
                    <label for="generatedPassword">Generated Password:</label>
                    <div class="password-output">
                        <input type="text" id="generatedPassword" readonly placeholder="Click generate to create a password">
                        <button class="copy-button" onclick="copyToClipboard('generatedPassword')">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                    
                    <div class="password-strength" id="passwordStrength">
                        <div class="strength-bar">
                            <div class="strength-fill"></div>
                        </div>
                        <span class="strength-text">Click generate to see strength</span>
                    </div>
                </div>
            </div>
        `,
        generatePassword: function() {
            const length = parseInt(document.getElementById('passwordLength').value);
            const includeUppercase = document.getElementById('includeUppercase').checked;
            const includeLowercase = document.getElementById('includeLowercase').checked;
            const includeNumbers = document.getElementById('includeNumbers').checked;
            const includeSymbols = document.getElementById('includeSymbols').checked;
            const excludeSimilar = document.getElementById('excludeSimilar').checked;
            
            let chars = '';
            if (includeUppercase) chars += excludeSimilar ? 'ABCDEFGHJKMNPQRSTUVWXYZ' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            if (includeLowercase) chars += excludeSimilar ? 'abcdefghjkmnpqrstuvwxyz' : 'abcdefghijklmnopqrstuvwxyz';
            if (includeNumbers) chars += excludeSimilar ? '23456789' : '0123456789';
            if (includeSymbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
            
            if (!chars) {
                alert('Please select at least one character type');
                return;
            }
            
            let password = '';
            for (let i = 0; i < length; i++) {
                password += chars.charAt(Math.floor(Math.random() * chars.length));
            }
            
            document.getElementById('generatedPassword').value = password;
            this.checkPasswordStrength(password);
        },
        
        checkPasswordStrength: function(password) {
            let strength = 0;
            let text = 'Very Weak';
            let color = '#ef4444';
            
            // Length check
            if (password.length >= 8) strength += 1;
            if (password.length >= 12) strength += 1;
            if (password.length >= 16) strength += 1;
            
            // Character variety
            if (/[a-z]/.test(password)) strength += 1;
            if (/[A-Z]/.test(password)) strength += 1;
            if (/[0-9]/.test(password)) strength += 1;
            if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
            // Determine strength level
            if (strength >= 7) {
                text = 'Very Strong';
                color = '#10b981';
            } else if (strength >= 5) {
                text = 'Strong';
                color = '#059669';
            } else if (strength >= 3) {
                text = 'Medium';
                color = '#f59e0b';
            } else if (strength >= 1) {
                text = 'Weak';
                color = '#f97316';
            }
            
            const strengthElement = document.getElementById('passwordStrength');
            const strengthFill = strengthElement.querySelector('.strength-fill');
            const strengthText = strengthElement.querySelector('.strength-text');
            
            strengthFill.style.width = `${(strength / 7) * 100}%`;
            strengthFill.style.backgroundColor = color;
            strengthText.textContent = text;
        }
    },
    
    'qr-generator': {
        title: 'QR Code Generator',
        category: 'generator',
        description: 'Generate QR codes for URLs, text, and other data',
        content: `
            <div class="tool-interface">
                <div class="input-section">
                    <label for="qrInput">Enter text or URL:</label>
                    <textarea id="qrInput" placeholder="Enter text, URL, email, phone number, etc." rows="4"></textarea>
                </div>
                
                <div class="options-section">
                    <div class="option-row">
                        <div class="option-group">
                            <label for="qrSize">Size:</label>
                            <select id="qrSize">
                                <option value="200">200x200</option>
                                <option value="300" selected>300x300</option>
                                <option value="400">400x400</option>
                                <option value="500">500x500</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label for="qrColor">Color:</label>
                            <input type="color" id="qrColor" value="#000000">
                        </div>
                        
                        <div class="option-group">
                            <label for="qrBackground">Background:</label>
                            <input type="color" id="qrBackground" value="#ffffff">
                        </div>
                    </div>
                    
                    <button class="tool-button primary" onclick="toolsData['qr-generator'].generateQR()">
                        <i class="fas fa-qrcode"></i> Generate QR Code
                    </button>
                </div>
                
                <div class="output-section">
                    <div id="qrResult" class="qr-display">
                        <p>Enter text above and click "Generate QR Code"</p>
                    </div>
                    <button class="tool-button" id="downloadQR" onclick="toolsData['qr-generator'].downloadQR()" style="display: none;">
                        <i class="fas fa-download"></i> Download QR Code
                    </button>
                </div>
            </div>
        `,
        generateQR: function() {
            const text = document.getElementById('qrInput').value.trim();
            if (!text) {
                alert('Please enter some text or URL');
                return;
            }
            
            const size = document.getElementById('qrSize').value;
            const color = document.getElementById('qrColor').value.replace('#', '');
            const bgColor = document.getElementById('qrBackground').value.replace('#', '');
            
            // Using QR Server API
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&color=${color}&bgcolor=${bgColor}&data=${encodeURIComponent(text)}`;
            
            const qrResult = document.getElementById('qrResult');
            qrResult.innerHTML = `
                <img src="${qrUrl}" alt="QR Code" style="max-width: 100%; height: auto;">
                <p>QR Code for: ${text.length > 50 ? text.substring(0, 50) + '...' : text}</p>
            `;
            
            document.getElementById('downloadQR').style.display = 'block';
            this.currentQRUrl = qrUrl;
        },
        
        downloadQR: function() {
            if (!this.currentQRUrl) return;
            
            const link = document.createElement('a');
            link.href = this.currentQRUrl;
            link.download = 'qrcode.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    },
    
    'base64': {
        title: 'Base64 Encoder/Decoder',
        category: 'converter',
        description: 'Encode and decode text and files to/from Base64 format',
        content: `
            <div class="tool-interface">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="toolsData['base64'].switchTab('encode')">Encode</button>
                    <button class="tab-button" onclick="toolsData['base64'].switchTab('decode')">Decode</button>
                </div>
                
                <div class="input-section">
                    <label for="base64Input" id="inputLabel">Enter text to encode:</label>
                    <textarea id="base64Input" placeholder="Enter your text here..." rows="6"></textarea>
                </div>
                
                <div class="button-section">
                    <button class="tool-button primary" onclick="toolsData['base64'].process()">
                        <i class="fas fa-exchange-alt"></i> <span id="processButton">Encode</span>
                    </button>
                    <button class="tool-button" onclick="toolsData['base64'].clear()">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
                
                <div class="output-section">
                    <label for="base64Output" id="outputLabel">Encoded result:</label>
                    <textarea id="base64Output" placeholder="Result will appear here..." rows="6" readonly></textarea>
                    <button class="copy-button" onclick="copyToClipboard('base64Output')">
                        <i class="fas fa-copy"></i> Copy Result
                    </button>
                </div>
            </div>
        `,
        currentMode: 'encode',
        
        switchTab: function(mode) {
            this.currentMode = mode;
            
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update labels and placeholders
            if (mode === 'encode') {
                document.getElementById('inputLabel').textContent = 'Enter text to encode:';
                document.getElementById('outputLabel').textContent = 'Encoded result:';
                document.getElementById('processButton').textContent = 'Encode';
                document.getElementById('base64Input').placeholder = 'Enter your text here...';
                document.getElementById('base64Output').placeholder = 'Base64 encoded result will appear here...';
            } else {
                document.getElementById('inputLabel').textContent = 'Enter Base64 to decode:';
                document.getElementById('outputLabel').textContent = 'Decoded result:';
                document.getElementById('processButton').textContent = 'Decode';
                document.getElementById('base64Input').placeholder = 'Enter Base64 encoded text here...';
                document.getElementById('base64Output').placeholder = 'Decoded result will appear here...';
            }
            
            this.clear();
        },
        
        process: function() {
            const input = document.getElementById('base64Input').value;
            const output = document.getElementById('base64Output');
            
            if (!input.trim()) {
                alert('Please enter some text');
                return;
            }
            
            try {
                if (this.currentMode === 'encode') {
                    output.value = btoa(unescape(encodeURIComponent(input)));
                } else {
                    output.value = decodeURIComponent(escape(atob(input)));
                }
            } catch (error) {
                alert('Error: Invalid input for ' + this.currentMode + 'ing');
                output.value = '';
            }
        },
        
        clear: function() {
            document.getElementById('base64Input').value = '';
            document.getElementById('base64Output').value = '';
        }
    },
    
    'json-formatter': {
        title: 'JSON Formatter',
        category: 'converter',
        description: 'Format, validate, and minify JSON data',
        content: `
            <div class="tool-interface">
                <div class="input-section">
                    <label for="jsonInput">Enter JSON:</label>
                    <textarea id="jsonInput" placeholder="Paste your JSON here..." rows="8"></textarea>
                </div>
                
                <div class="button-section">
                    <button class="tool-button primary" onclick="toolsData['json-formatter'].formatJSON()">
                        <i class="fas fa-code"></i> Format JSON
                    </button>
                    <button class="tool-button" onclick="toolsData['json-formatter'].minifyJSON()">
                        <i class="fas fa-compress"></i> Minify JSON
                    </button>
                    <button class="tool-button" onclick="toolsData['json-formatter'].validateJSON()">
                        <i class="fas fa-check"></i> Validate JSON
                    </button>
                    <button class="tool-button" onclick="toolsData['json-formatter'].clear()">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
                
                <div class="output-section">
                    <label for="jsonOutput">Result:</label>
                    <textarea id="jsonOutput" placeholder="Formatted JSON will appear here..." rows="8" readonly></textarea>
                    <div id="jsonStatus" class="status-message"></div>
                    <button class="copy-button" onclick="copyToClipboard('jsonOutput')">
                        <i class="fas fa-copy"></i> Copy Result
                    </button>
                </div>
            </div>
        `,
        
        formatJSON: function() {
            const input = document.getElementById('jsonInput').value.trim();
            const output = document.getElementById('jsonOutput');
            const status = document.getElementById('jsonStatus');
            
            if (!input) {
                this.showStatus('Please enter some JSON', 'error');
                return;
            }
            
            try {
                const parsed = JSON.parse(input);
                output.value = JSON.stringify(parsed, null, 2);
                this.showStatus('JSON formatted successfully', 'success');
            } catch (error) {
                this.showStatus('Invalid JSON: ' + error.message, 'error');
                output.value = '';
            }
        },
        
        minifyJSON: function() {
            const input = document.getElementById('jsonInput').value.trim();
            const output = document.getElementById('jsonOutput');
            
            if (!input) {
                this.showStatus('Please enter some JSON', 'error');
                return;
            }
            
            try {
                const parsed = JSON.parse(input);
                output.value = JSON.stringify(parsed);
                this.showStatus('JSON minified successfully', 'success');
            } catch (error) {
                this.showStatus('Invalid JSON: ' + error.message, 'error');
                output.value = '';
            }
        },
        
        validateJSON: function() {
            const input = document.getElementById('jsonInput').value.trim();
            
            if (!input) {
                this.showStatus('Please enter some JSON', 'error');
                return;
            }
            
            try {
                JSON.parse(input);
                this.showStatus('✓ Valid JSON', 'success');
            } catch (error) {
                this.showStatus('✗ Invalid JSON: ' + error.message, 'error');
            }
        },
        
        showStatus: function(message, type) {
            const status = document.getElementById('jsonStatus');
            status.textContent = message;
            status.className = `status-message ${type}`;
        },
        
        clear: function() {
            document.getElementById('jsonInput').value = '';
            document.getElementById('jsonOutput').value = '';
            document.getElementById('jsonStatus').textContent = '';
        }
    },
    
    'lorem-ipsum': {
        title: 'Lorem Ipsum Generator',
        category: 'text',
        description: 'Generate placeholder text for your designs and layouts',
        content: `
            <div class="tool-interface">
                <div class="options-section">
                    <div class="option-row">
                        <div class="option-group">
                            <label for="loremType">Generate:</label>
                            <select id="loremType">
                                <option value="paragraphs">Paragraphs</option>
                                <option value="sentences">Sentences</option>
                                <option value="words">Words</option>
                            </select>
                        </div>
                        
                        <div class="option-group">
                            <label for="loremCount">Count:</label>
                            <input type="number" id="loremCount" min="1" max="100" value="3">
                        </div>
                        
                        <div class="option-group">
                            <label class="checkbox-label">
                                <input type="checkbox" id="startWithLorem" checked>
                                Start with "Lorem ipsum..."
                            </label>
                        </div>
                    </div>
                    
                    <button class="tool-button primary" onclick="toolsData['lorem-ipsum'].generateLorem()">
                        <i class="fas fa-paragraph"></i> Generate Lorem Ipsum
                    </button>
                </div>
                
                <div class="output-section">
                    <label for="loremOutput">Generated Text:</label>
                    <textarea id="loremOutput" rows="12" readonly placeholder="Generated Lorem Ipsum will appear here..."></textarea>
                    <button class="copy-button" onclick="copyToClipboard('loremOutput')">
                        <i class="fas fa-copy"></i> Copy Text
                    </button>
                </div>
            </div>
        `,
        
        words: [
            'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing', 'elit',
            'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore', 'et', 'dolore',
            'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam', 'quis', 'nostrud',
            'exercitation', 'ullamco', 'laboris', 'nisi', 'aliquip', 'ex', 'ea', 'commodo',
            'consequat', 'duis', 'aute', 'irure', 'in', 'reprehenderit', 'voluptate',
            'velit', 'esse', 'cillum', 'fugiat', 'nulla', 'pariatur', 'excepteur', 'sint',
            'occaecat', 'cupidatat', 'non', 'proident', 'sunt', 'culpa', 'qui', 'officia',
            'deserunt', 'mollit', 'anim', 'id', 'est', 'laborum'
        ],
        
        generateLorem: function() {
            const type = document.getElementById('loremType').value;
            const count = parseInt(document.getElementById('loremCount').value);
            const startWithLorem = document.getElementById('startWithLorem').checked;
            
            let result = '';
            
            switch (type) {
                case 'words':
                    result = this.generateWords(count, startWithLorem);
                    break;
                case 'sentences':
                    result = this.generateSentences(count, startWithLorem);
                    break;
                case 'paragraphs':
                    result = this.generateParagraphs(count, startWithLorem);
                    break;
            }
            
            document.getElementById('loremOutput').value = result;
        },
        
        generateWords: function(count, startWithLorem) {
            let words = [];
            let wordIndex = 0;
            
            if (startWithLorem) {
                words.push('Lorem', 'ipsum', 'dolor', 'sit', 'amet');
                wordIndex = 5;
            }
            
            for (let i = wordIndex; i < count; i++) {
                words.push(this.words[Math.floor(Math.random() * this.words.length)]);
            }
            
            return words.join(' ') + '.';
        },
        
        generateSentences: function(count, startWithLorem) {
            let sentences = [];
            
            for (let i = 0; i < count; i++) {
                const sentenceLength = Math.floor(Math.random() * 15) + 5;
                let sentence = [];
                
                if (i === 0 && startWithLorem) {
                    sentence = ['Lorem', 'ipsum', 'dolor', 'sit', 'amet'];
                    for (let j = 5; j < sentenceLength; j++) {
                        sentence.push(this.words[Math.floor(Math.random() * this.words.length)]);
                    }
                } else {
                    for (let j = 0; j < sentenceLength; j++) {
                        sentence.push(this.words[Math.floor(Math.random() * this.words.length)]);
                    }
                }
                
                sentence[0] = sentence[0].charAt(0).toUpperCase() + sentence[0].slice(1);
                sentences.push(sentence.join(' ') + '.');
            }
            
            return sentences.join(' ');
        },
        
        generateParagraphs: function(count, startWithLorem) {
            let paragraphs = [];
            
            for (let i = 0; i < count; i++) {
                const sentenceCount = Math.floor(Math.random() * 5) + 3;
                paragraphs.push(this.generateSentences(sentenceCount, i === 0 && startWithLorem));
            }
            
            return paragraphs.join('\n\n');
        }
    },
    
    'url-encoder': {
        title: 'URL Encoder/Decoder',
        category: 'converter',
        description: 'Encode and decode URLs for safe transmission',
        content: `
            <div class="tool-interface">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="toolsData['url-encoder'].switchTab('encode')">URL Encode</button>
                    <button class="tab-button" onclick="toolsData['url-encoder'].switchTab('decode')">URL Decode</button>
                </div>
                
                <div class="input-section">
                    <label for="urlInput" id="urlInputLabel">Enter URL to encode:</label>
                    <textarea id="urlInput" placeholder="Enter your URL or text here..." rows="6"></textarea>
                </div>
                
                <div class="button-section">
                    <button class="tool-button primary" onclick="toolsData['url-encoder'].process()">
                        <i class="fas fa-exchange-alt"></i> <span id="urlProcessButton">Encode</span>
                    </button>
                    <button class="tool-button" onclick="toolsData['url-encoder'].clear()">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
                
                <div class="output-section">
                    <label for="urlOutput" id="urlOutputLabel">Encoded result:</label>
                    <textarea id="urlOutput" placeholder="Result will appear here..." rows="6" readonly></textarea>
                    <button class="copy-button" onclick="copyToClipboard('urlOutput')">
                        <i class="fas fa-copy"></i> Copy Result
                    </button>
                </div>
            </div>
        `,
        
        currentMode: 'encode',
        
        switchTab: function(mode) {
            this.currentMode = mode;
            
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update labels and placeholders
            if (mode === 'encode') {
                document.getElementById('urlInputLabel').textContent = 'Enter URL to encode:';
                document.getElementById('urlOutputLabel').textContent = 'Encoded result:';
                document.getElementById('urlProcessButton').textContent = 'Encode';
                document.getElementById('urlInput').placeholder = 'Enter your URL or text here...';
                document.getElementById('urlOutput').placeholder = 'URL encoded result will appear here...';
            } else {
                document.getElementById('urlInputLabel').textContent = 'Enter URL to decode:';
                document.getElementById('urlOutputLabel').textContent = 'Decoded result:';
                document.getElementById('urlProcessButton').textContent = 'Decode';
                document.getElementById('urlInput').placeholder = 'Enter URL encoded text here...';
                document.getElementById('urlOutput').placeholder = 'Decoded result will appear here...';
            }
            
            this.clear();
        },
        
        process: function() {
            const input = document.getElementById('urlInput').value;
            const output = document.getElementById('urlOutput');
            
            if (!input.trim()) {
                alert('Please enter some text');
                return;
            }
            
            try {
                if (this.currentMode === 'encode') {
                    output.value = encodeURIComponent(input);
                } else {
                    output.value = decodeURIComponent(input);
                }
            } catch (error) {
                alert('Error: Invalid input for ' + this.currentMode + 'ing');
                output.value = '';
            }
        },
        
        clear: function() {
            document.getElementById('urlInput').value = '';
            document.getElementById('urlOutput').value = '';
        }
    }
};

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    setupEventListeners();
    populateToolsList();
    setupSearch();
    setupScrollEffects();
    setupAnimations();
}

// Setup Event Listeners
function setupEventListeners() {
    // Navigation
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
    
    // Category tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            switchCategory(category);
        });
    });
    
    // Tool cards
    const toolCards = document.querySelectorAll('.tool-card');
    toolCards.forEach(card => {
        card.addEventListener('click', () => {
            const toolId = card.dataset.tool;
            openTool(toolId);
        });
    });
    
    // Modal
    const modal = document.getElementById('toolModal');
    const modalClose = document.getElementById('modalClose');
    
    if (modalClose) {
        modalClose.addEventListener('click', closeModal);
    }
    
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Back to top button
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // Contact form
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }
}

// Populate Tools List
function populateToolsList() {
    const toolsGrid = document.getElementById('toolsGrid');
    if (!toolsGrid) return;
    
    allTools = Array.from(toolsGrid.children);
}

// Setup Search Functionality
function setupSearch() {
    const searchInput = document.getElementById('toolSearch');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
    if (!searchInput) return;
    
    // Tool search data
    const searchData = [
        { name: 'Word Counter', tool: 'word-counter', category: 'text' },
        { name: 'Case Converter', tool: 'case-converter', category: 'text' },
        { name: 'Text Difference', tool: 'text-diff', category: 'text' },
        { name: 'Lorem Ipsum Generator', tool: 'lorem-ipsum', category: 'text' },
        { name: 'Password Generator', tool: 'password-generator', category: 'generator' },
        { name: 'QR Code Generator', tool: 'qr-generator', category: 'generator' },
        { name: 'UUID Generator', tool: 'uuid-generator', category: 'generator' },
        { name: 'Color Palette Generator', tool: 'color-palette', category: 'generator' },
        { name: 'Base64 Encoder/Decoder', tool: 'base64', category: 'converter' },
        { name: 'URL Encoder/Decoder', tool: 'url-encoder', category: 'converter' },
        { name: 'JSON Formatter', tool: 'json-formatter', category: 'converter' },
        { name: 'Unit Converter', tool: 'unit-converter', category: 'converter' }
    ];
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length === 0) {
            searchSuggestions.style.display = 'none';
            return;
        }
        
        const matches = searchData.filter(item =>
            item.name.toLowerCase().includes(query) ||
            item.category.toLowerCase().includes(query)
        );
        
        if (matches.length > 0) {
            searchSuggestions.innerHTML = matches.map(item =>
                `<div class="suggestion-item" onclick="openTool('${item.tool}')">${item.name}</div>`
            ).join('');
            searchSuggestions.style.display = 'block';
        } else {
            searchSuggestions.style.display = 'none';
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-box')) {
            searchSuggestions.style.display = 'none';
        }
    });
}

// Switch Category
function switchCategory(category) {
    currentCategory = category;
    
    // Update active tab
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        }
    });
    
    // Filter tools
    allTools.forEach(tool => {
        if (category === 'all' || tool.dataset.category === category) {
            tool.style.display = 'block';
            tool.classList.add('fade-in');
        } else {
            tool.style.display = 'none';
        }
    });
}

// Open Tool Modal
function openTool(toolId) {
    const tool = toolsData[toolId];
    if (!tool) return;
    
    const modal = document.getElementById('toolModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = tool.title;
    modalBody.innerHTML = tool.content;
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Initialize tool if it has an init function
    if (tool.init) {
        setTimeout(() => tool.init(), 100);
    }
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('toolModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Copy to Clipboard
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element || !element.value) {
        alert('Nothing to copy');
        return;
    }
    
    element.select();
    document.execCommand('copy');
    
    // Show feedback
    const originalText = event.target.innerHTML;
    event.target.innerHTML = '<i class="fas fa-check"></i> Copied!';
    event.target.style.background = 'var(--success-color)';
    
    setTimeout(() => {
        event.target.innerHTML = originalText;
        event.target.style.background = '';
    }, 2000);
}

// Setup Scroll Effects
function setupScrollEffects() {
    const backToTop = document.getElementById('backToTop');
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('show');
        } else {
            backToTop.classList.remove('show');
        }
    });
}

// Setup Animations
function setupAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements
    document.querySelectorAll('.tool-card, .feature-card').forEach(el => {
        observer.observe(el);
    });
}

// Handle Contact Form
function handleContactForm(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        subject: formData.get('subject'),
        message: formData.get('message')
    };
    
    // Simulate form submission
    const submitButton = e.target.querySelector('.submit-button');
    const originalText = submitButton.innerHTML;
    
    submitButton.innerHTML = '<div class="loading"></div> Sending...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        alert('Message sent successfully! We\'ll get back to you soon.');
        e.target.reset();
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }, 2000);
}

// Utility Functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add CSS for tool interfaces
const toolStyles = `
<style>
.tool-interface {
    max-width: 800px;
    margin: 0 auto;
}

.input-section, .output-section, .options-section {
    margin-bottom: 2rem;
}

.input-section label, .output-section label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--gray-700);
}

.input-section textarea, .output-section textarea, .input-section input, .output-section input {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid var(--gray-200);
    border-radius: var(--border-radius);
    font-family: inherit;
    font-size: 1rem;
    transition: var(--transition);
    resize: vertical;
}

.input-section textarea:focus, .output-section textarea:focus, .input-section input:focus, .output-section input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.button-section {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}

.tool-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: 2px solid var(--gray-300);
    background: white;
    color: var(--gray-700);
    border-radius: var(--border-radius);
    cursor: pointer;
    font-weight: 500;
    transition: var(--transition);
    text-decoration: none;
}

.tool-button:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.tool-button.primary {
    background: var(--primary-gradient);
    border-color: transparent;
    color: white;
}

.tool-button.primary:hover {
    transform: translateY(-1px);
    box-shadow: var(--box-shadow-lg);
}

.copy-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--success-color);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    font-weight: 500;
    transition: var(--transition);
    margin-top: 0.5rem;
}

.copy-button:hover {
    background: #059669;
    transform: translateY(-1px);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.stat-box {
    background: var(--gray-50);
    padding: 1rem;
    border-radius: var(--border-radius);
    text-align: center;
    border: 1px solid var(--gray-200);
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 0.25rem;
}

.stat-label {
    font-size: 0.9rem;
    color: var(--gray-600);
}

.option-group {
    margin-bottom: 1rem;
}

.option-row {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: end;
}

.option-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--gray-700);
}

.option-group select, .option-group input {
    padding: 0.5rem;
    border: 2px solid var(--gray-200);
    border-radius: var(--border-radius);
    font-family: inherit;
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin: 1rem 0;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-weight: 400 !important;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.password-output {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.password-output input {
    flex: 1;
}

.password-strength {
    margin-top: 1rem;
}

.strength-bar {
    width: 100%;
    height: 8px;
    background: var(--gray-200);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.strength-fill {
    height: 100%;
    width: 0%;
    transition: var(--transition);
    border-radius: 4px;
}

.strength-text {
    font-size: 0.9rem;
    font-weight: 500;
}

.qr-display {
    text-align: center;
    padding: 2rem;
    border: 2px dashed var(--gray-300);
    border-radius: var(--border-radius);
    margin-bottom: 1rem;
}

.qr-display img {
    margin-bottom: 1rem;
}

.tab-buttons {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.tab-button {
    padding: 0.75rem 1.5rem;
    border: 2px solid var(--gray-200);
    background: white;
    color: var(--gray-600);
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition);
    font-weight: 500;
}

.tab-button:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.tab-button.active {
    background: var(--primary-gradient);
    border-color: transparent;
    color: white;
}

.status-message {
    margin-top: 0.5rem;
    padding: 0.5rem;
    border-radius: var(--border-radius);
    font-weight: 500;
}

.status-message.success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-message.error {
    background: rgba(239, 68, 68, 0.1);
    color: var(--error-color);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

@media (max-width: 768px) {
    .option-row {
        flex-direction: column;
        gap: 1rem;
    }
    
    .button-section {
        flex-direction: column;
    }
    
    .tool-button {
        justify-content: center;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .password-output {
        flex-direction: column;
    }
}
</style>
`;

// Inject tool styles
document.head.insertAdjacentHTML('beforeend', toolStyles);