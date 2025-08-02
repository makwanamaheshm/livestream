# OnePageTools - Free Online Utilities & Tools

A modern, comprehensive collection of free online tools and utilities designed to boost productivity. Built with vanilla HTML, CSS, and JavaScript for maximum performance and compatibility.

![OnePageTools Screenshot](https://via.placeholder.com/800x400/667eea/ffffff?text=OnePageTools)

## 🌟 Features

### 🔧 Complete Tool Suite
- **50+ Professional Tools** across multiple categories
- **Lightning Fast Performance** - Everything runs client-side
- **No Downloads Required** - Works directly in your browser
- **100% Free** - No subscriptions or hidden costs
- **Mobile Responsive** - Perfect on all devices
- **Privacy First** - Your data never leaves your device

### 🎨 Modern Design
- Beautiful gradient-based UI design
- Smooth animations and transitions
- Dark/Light theme support
- Professional typography with Inter font
- Glassmorphism effects
- Floating animation elements

### 🛠️ Tool Categories

#### 📝 Text Tools
- **Word Counter** - Count words, characters, sentences, paragraphs, and reading time
- **Case Converter** - Convert to uppercase, lowercase, title case, camelCase, snake_case, etc.
- **Text Difference** - Compare two texts and highlight differences
- **Lorem Ipsum Generator** - Generate placeholder text with customizable options

#### 🖼️ Image Tools
- **Image Resizer** - Resize images while maintaining aspect ratio
- **Image Compressor** - Compress images without quality loss
- **Image Format Converter** - Convert between JPG, PNG, WebP, etc.
- **Image Cropper** - Crop images to specific dimensions

#### 🔄 Converter Tools
- **Base64 Encoder/Decoder** - Encode and decode Base64 strings
- **URL Encoder/Decoder** - Encode URLs for safe transmission
- **JSON Formatter** - Format, validate, and minify JSON data
- **Unit Converter** - Convert between different measurement units

#### ⚡ Generator Tools
- **Password Generator** - Generate secure passwords with customizable options
- **QR Code Generator** - Create QR codes with color customization
- **UUID Generator** - Generate unique identifiers
- **Color Palette Generator** - Create beautiful color schemes

#### 🧮 Calculator Tools
- **Percentage Calculator** - Calculate percentages and ratios
- **BMI Calculator** - Calculate Body Mass Index
- **Loan Calculator** - Calculate loan payments and interest
- **Age Calculator** - Calculate exact age in years, months, days

#### 💻 Developer Tools
- **HTML Encoder/Decoder** - Encode HTML entities
- **CSS Minifier** - Minify and compress CSS code
- **JavaScript Minifier** - Minify and obfuscate JS code
- **Regex Tester** - Test regular expressions with live matching

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No server requirements - runs entirely client-side

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/onepagetools.git
   cd onepagetools
   ```

2. **Open in browser**
   ```bash
   # Simply open index.html in your web browser
   open index.html
   # Or serve with a simple HTTP server
   python -m http.server 8000
   ```

3. **That's it!** No build process, no dependencies, no complex setup.

## 📁 Project Structure

```
onepagetools/
├── index.html          # Main HTML file
├── style.css           # CSS styles and responsive design
├── script.js           # JavaScript functionality and tools
├── README.md           # Project documentation
└── assets/             # Images and other assets
    └── screenshots/    # Application screenshots
```

## 🎯 Usage

### Basic Navigation
1. **Browse Tools** - Use the category tabs to filter tools by type
2. **Search** - Use the search bar to quickly find specific tools
3. **Open Tools** - Click on any tool card to open it in a modal
4. **Mobile Menu** - On mobile, use the hamburger menu for navigation

### Tool Features
- **Real-time Processing** - Most tools update results as you type
- **Copy to Clipboard** - One-click copying of results
- **Responsive Design** - Works perfectly on desktop and mobile
- **Keyboard Shortcuts** - ESC to close modals, Enter to submit forms

### Example: Using the Password Generator
1. Click on "Password Generator" in the Generator category
2. Adjust the length slider (4-128 characters)
3. Select character types (uppercase, lowercase, numbers, symbols)
4. Click "Generate Password"
5. Copy the result with one click

## 🛠️ Customization

### Adding New Tools
1. **Define the tool** in `script.js`:
   ```javascript
   'my-new-tool': {
       title: 'My New Tool',
       category: 'text',
       description: 'Description of what the tool does',
       content: `<!-- HTML content for the tool -->`,
       init: function() {
           // Initialization code
       },
       // Additional methods
   }
   ```

2. **Add tool card** in `index.html`:
   ```html
   <div class="tool-card" data-category="text" data-tool="my-new-tool">
       <div class="tool-icon">
           <i class="fas fa-icon"></i>
       </div>
       <h3>My New Tool</h3>
       <p>Description</p>
       <div class="tool-tags">
           <span class="tag">Text</span>
       </div>
   </div>
   ```

### Styling Modifications
- Edit CSS variables in `style.css` to change colors, fonts, spacing
- Modify the `--primary-gradient` variable to change the main color scheme
- Adjust `--border-radius` for different corner styles

### Adding Categories
1. Add new category tab in the HTML
2. Update the search data array in `script.js`
3. Add corresponding tool cards with the new category

## 🎨 Design System

### Color Palette
- **Primary**: `#667eea` to `#764ba2` (gradient)
- **Success**: `#10b981`
- **Warning**: `#f59e0b`
- **Error**: `#ef4444`
- **Gray Scale**: `#f9fafb` to `#111827`

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 700-800 weight
- **Body**: 400-500 weight
- **UI Elements**: 500-600 weight

### Components
- **Cards**: White background, subtle shadows, hover effects
- **Buttons**: Gradient primary, outlined secondary
- **Modals**: Blur backdrop, smooth animations
- **Forms**: Clean inputs with focus states

## 📱 Responsive Design

### Breakpoints
- **Desktop**: 1200px and above
- **Tablet**: 768px to 1199px
- **Mobile**: Below 768px
- **Small Mobile**: Below 480px

### Mobile Features
- Collapsible navigation menu
- Touch-friendly button sizes
- Optimized tool layouts
- Swipe-friendly carousels

## 🔧 Technical Details

### Performance
- **Vanilla JavaScript** - No framework overhead
- **CSS Grid & Flexbox** - Modern layout techniques
- **Optimized Images** - WebP support with fallbacks
- **Lazy Loading** - Images and content loaded on demand
- **Service Worker Ready** - Prepared for PWA implementation

### Browser Support
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile browsers

### Security
- **Client-side Processing** - No data sent to servers
- **Content Security Policy** - XSS protection
- **Input Validation** - Sanitized user inputs
- **HTTPS Ready** - Secure deployment support

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Types of Contributions
- 🐛 **Bug Reports** - Found an issue? Let us know!
- ✨ **Feature Requests** - Ideas for new tools or improvements
- 🔧 **Code Contributions** - New tools, bug fixes, improvements
- 📖 **Documentation** - Help improve our docs
- 🎨 **Design** - UI/UX improvements and suggestions

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-tool`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Coding Standards
- Use consistent indentation (2 spaces)
- Follow existing naming conventions
- Add comments for complex logic
- Ensure mobile responsiveness
- Test across different browsers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Font Awesome** - For the beautiful icons
- **Google Fonts** - For the Inter font family
- **QR Server API** - For QR code generation
- **Community Contributors** - For suggestions and feedback

## 📞 Support

### Get Help
- 📧 **Email**: hello@onepagetools.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/onepagetools/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/onepagetools/discussions)

### FAQ

**Q: Is OnePageTools really free?**
A: Yes! All tools are completely free to use with no hidden costs or subscriptions.

**Q: Do you store my data?**
A: No, all processing happens in your browser. Your data never leaves your device.

**Q: Can I use this offline?**
A: Most tools work offline once loaded. Some features like QR code generation require internet.

**Q: How do I suggest a new tool?**
A: Open an issue on GitHub or contact us via email with your suggestion.

**Q: Can I embed these tools on my website?**
A: The tools are designed for this website, but you're welcome to fork and modify under the MIT license.

## 🗺️ Roadmap

### Upcoming Features
- [ ] **PWA Support** - Install as a native app
- [ ] **Dark Mode Toggle** - System preference detection
- [ ] **More Tools** - Hash generators, image filters, etc.
- [ ] **Tool Favorites** - Save frequently used tools
- [ ] **Export Options** - Save results in various formats
- [ ] **Keyboard Shortcuts** - Power user features
- [ ] **Tool History** - Recent calculations and conversions
- [ ] **Batch Processing** - Process multiple items at once

### Long-term Goals
- Multi-language support
- Advanced image editing tools
- Team collaboration features
- API for developers
- Mobile app versions

---

<div align="center">

**Made with ❤️ for productivity**

⭐ **Star this repo if you find it useful!** ⭐

[Website](https://onepagetools.com) • [Demo](https://onepagetools.com) • [Issues](https://github.com/yourusername/onepagetools/issues) • [Contribute](CONTRIBUTING.md)

</div>