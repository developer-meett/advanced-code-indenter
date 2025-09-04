# Advanced Code Indenter

A sophisticated web application that automatically detects programming languages and formats code with intelligent indentation and styling. Built with Flask backend and modern frontend technologies.

## Features

- **🔍 Automatic Language Detection**: Intelligently identifies programming languages using pattern analysis and Pygments
- **✨ Multi-Language Formatting**: Supports 13+ programming languages with specialized formatters
- **🎯 Real-time Detection**: Auto-detects language as you type with confidence indicators
- **📋 One-Click Copy**: Copy formatted code to clipboard with visual feedback
- **🎲 Sample Code**: Load random code examples to test the functionality
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🛡️ Robust Error Handling**: Graceful handling of network issues and formatting errors

## Supported Languages

- **Python**: Uses autopep8 + black for robust two-stage formatting
- **JavaScript/TypeScript**: Prettier-based formatting
- **HTML/CSS**: Prettier-based formatting
- **C/C++/Java/C#**: Clang-format integration
- **Go**: gofmt integration
- **Ruby**: Prettier plugin support
- **PHP**: PHP-CS-Fixer integration
- **JSON**: Built-in parsing and formatting
- **XML**: Prettier XML plugin

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for some formatters like Prettier)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Code-Indenter
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install optional formatters** (for enhanced functionality)
   ```bash
   # For JavaScript/TypeScript/HTML/CSS formatting
   npm install -g prettier
   
   # For Go formatting (if Go is installed)
   # gofmt comes with Go installation
   
   # For C/C++ formatting
   # Install clang-format through your package manager
   ```

### Running Locally

1. **Start the development server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5001`

3. **Start formatting code!**
   - Paste or type code into the input area
   - Watch automatic language detection work
   - Click "Format Code" to see beautifully formatted output
   - Use "Copy Code" to copy results to clipboard

## Deployment

### Heroku Deployment

1. **Install Heroku CLI** and login
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy production version"
   git push heroku main
   ```

The `Procfile` and `requirements.txt` are already configured for Heroku deployment.

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
```

### Other Platforms

The application is compatible with:
- **Railway**: Use the provided Procfile
- **Render**: Configure with Python environment
- **DigitalOcean App Platform**: Use requirements.txt
- **AWS Elastic Beanstalk**: Deploy as Python Flask application

## API Documentation

### Language Detection

**POST** `/api/detect-language`

```json
{
  "code": "def hello():\n    print('world')"
}
```

**Response:**
```json
{
  "language": "python",
  "confidence": "high",
  "detected_by": "enhanced_patterns"
}
```

### Code Formatting

**POST** `/api/indent`

```json
{
  "code": "def hello():print('world')",
  "language": "python"
}
```

**Response:**
```json
{
  "indented_code": "def hello():\n    print(\"world\")\n"
}
```

## Architecture

### Backend (Flask)
- **Language Detection**: Hybrid approach using Pygments + custom pattern analysis
- **Formatting Pipeline**: Language-specific formatters with robust error handling
- **Logging**: Structured logging for production monitoring
- **Error Handling**: Comprehensive exception handling with user-friendly messages

### Frontend (HTML/CSS/JavaScript)
- **Modern UI**: Tailwind CSS for responsive design
- **Syntax Highlighting**: Highlight.js for code display
- **Real-time Features**: Debounced language detection
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Project Structure
```
Code-Indenter/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend interface
├── static/
│   └── background.webp   # Static assets
├── requirements.txt      # Python dependencies
├── Procfile             # Deployment configuration
└── README.md            # This file
```

### Adding New Languages

1. Add language patterns to `enhanced_pattern_detection()`
2. Create a formatter function (e.g., `format_language_with_tool()`)
3. Add language mapping in `LANGUAGE_MAPPING`
4. Update frontend language list
5. Add sample code for testing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Pygments**: For language detection capabilities
- **Black & autopep8**: For robust Python formatting
- **Prettier**: For JavaScript/TypeScript/HTML/CSS formatting
- **Tailwind CSS**: For responsive UI design
- **Highlight.js**: For syntax highlighting

---

**Made with ❤️ for the developer community**
