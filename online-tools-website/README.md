# Online Tools Hub

A comprehensive collection of free online tools for text manipulation, conversions, generators, and more. Built with pure HTML, CSS, and JavaScript - no server-side processing required.

## 🚀 Features

- **100% Client-Side**: All tools run in your browser for maximum privacy and security
- **No Installation Required**: Works instantly in any modern web browser
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Fast & Efficient**: Instant results with no server delays
- **Modern UI**: Clean, intuitive interface with smooth animations
- **Free Forever**: All tools are completely free to use

## 🛠️ Available Tools

### Text Tools
- **Case Converter**: Convert text between uppercase, lowercase, title case, camelCase, and more
- **Word Counter**: Count words, characters, sentences, paragraphs with reading time estimates
- **Text Reverser**: Reverse text characters or words
- **Duplicate Line Remover**: Remove duplicate lines from text
- **Text to Slug**: Convert text to URL-friendly slugs

### Converter Tools
- **Base64 Encoder/Decoder**: Encode and decode Base64 strings
- **URL Encoder/Decoder**: Encode and decode URLs
- **JSON Formatter**: Format and validate JSON data
- **Color Converter**: Convert between HEX, RGB, HSL color formats
- **Unit Converter**: Convert between various units of measurement

### Generator Tools
- **Password Generator**: Generate secure passwords with custom settings
- **UUID Generator**: Generate unique identifiers
- **Hash Generator**: Generate MD5, SHA-1, SHA-256 hashes
- **Lorem Ipsum Generator**: Generate placeholder text
- **QR Code Generator**: Create QR codes for text, URLs, and more

### Developer Tools
- **HTML Minifier**: Compress HTML code
- **CSS Minifier**: Compress CSS code
- **JavaScript Minifier**: Compress JavaScript code
- **SQL Formatter**: Format SQL queries
- **Regex Tester**: Test regular expressions

### Image Tools
- **Image Resizer**: Resize images online
- **Image Compressor**: Compress images without quality loss
- **Image Converter**: Convert between image formats
- **Image to Base64**: Convert images to Base64 strings
- **Color Picker**: Pick colors from images

### Calculator Tools
- **Percentage Calculator**: Calculate percentages
- **Age Calculator**: Calculate age from date of birth
- **BMI Calculator**: Calculate Body Mass Index
- **Loan Calculator**: Calculate loan payments
- **Tip Calculator**: Calculate tips and split bills

## 📁 Project Structure

```
online-tools-website/
├── index.html              # Main homepage
├── css/
│   └── style.css          # Main stylesheet
├── js/
│   └── main.js            # Core JavaScript functionality
└── tools/
    ├── text/              # Text manipulation tools
    ├── converter/         # Conversion tools
    ├── generator/         # Generator tools
    ├── developer/         # Developer tools
    ├── image/            # Image tools
    └── calculator/       # Calculator tools
```

## 🚀 Getting Started

1. Clone or download the repository
2. Open `index.html` in your web browser
3. No server setup required - it works locally!

### For Development

If you want to run a local server for development:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js
npx http-server

# Using PHP
php -S localhost:8000
```

Then navigate to `http://localhost:8000`

## 🎨 Customization

### Changing Colors

Edit the CSS variables in `css/style.css`:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #1e40af;
    --accent-color: #3b82f6;
    /* ... other colors ... */
}
```

### Adding New Tools

1. Create a new HTML file in the appropriate category folder
2. Use the existing tool template structure
3. Add the tool link to the homepage (`index.html`)
4. Implement the tool logic in the page's script section

## 🔧 Technical Details

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **Icons**: Font Awesome 6.0
- **Fonts**: System fonts for optimal performance
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! To add a new tool:

1. Fork the repository
2. Create a new branch for your tool
3. Follow the existing code structure and style
4. Test thoroughly on different devices
5. Submit a pull request

## 💡 Future Enhancements

- [ ] Add more tools based on user requests
- [ ] Implement tool favorites/bookmarking
- [ ] Add dark mode toggle
- [ ] Create tool usage statistics
- [ ] Add more language support
- [ ] Implement tool chaining/workflows

## 📞 Contact

For questions, suggestions, or bug reports, please open an issue on GitHub or contact us at contact@onlinetoolshub.com

---

Made with ❤️ by the Online Tools Hub team