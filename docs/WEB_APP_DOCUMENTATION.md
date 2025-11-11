# Web Application Support - Feature Documentation

## Overview

SEAgent now supports generating and launching web applications directly from natural language prompts. Users can create fully functional web apps that run in the browser with modern, responsive interfaces.

## Key Features

### 🌐 Web Application Generation
- **Framework**: Flask-based web applications
- **UI**: Modern, responsive HTML/CSS with JavaScript
- **Templates**: Pre-built templates for common web app types
- **Auto-detection**: Automatically detects web app requests from prompts

### 🚀 Browser Integration
- **Auto-launch**: Automatically opens generated web apps in default browser
- **URL Handling**: Provides direct URLs for easy access
- **Port Management**: Uses configurable ports (default: 5000)
- **Cross-platform**: Works on Windows, macOS, and Linux

### 📱 Responsive UI
- **Modern Design**: Clean, professional interface
- **Mobile-friendly**: Responsive design that works on all devices
- **Interactive**: Real-time updates and user interactions
- **API Backend**: RESTful API endpoints for data management

## Usage

### Via Web Interface (`/apps`)
1. Select "🌐 Web Application" from the app type dropdown
2. Enter your prompt (e.g., "todo list web app", "dashboard web app")
3. Click "Generate Application" or use "Quick Generate & Launch Web App"
4. The browser will automatically open your new web application

### Via API
```bash
# Generate web app
curl -X POST http://localhost:8000/api/v1/apps/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "todo list web app with modern interface",
    "app_type": "web_app"
  }'

# Launch web app
curl -X POST http://localhost:8000/api/v1/apps/launch \\
  -H "Content-Type: application/json" \\
  -d '{
    "executable_path": "/path/to/generated/app.py",
    "app_type": "web_app"
  }'

# Quick generate and launch
curl -X POST http://localhost:8000/api/v1/apps/generate-and-launch \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "simple dashboard web app",
    "app_type": "web_app"
  }'
```

## Example Prompts

### Todo List Application
- "todo list web app"
- "task management web application"
- "simple todo app with add, edit, delete"

### Dashboard Applications
- "simple dashboard web app"
- "data visualization dashboard"
- "admin dashboard with charts"

### Utility Applications
- "note-taking web app"
- "simple blog web application"
- "contact management web app"

## Generated Application Structure

Each generated web application includes:

```
temp_directory/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # HTML template with CSS/JS
├── requirements.txt    # Python dependencies
└── README.md          # Usage instructions
```

### Flask Application Features
- **Routing**: Clean URL routing with Flask decorators
- **API Endpoints**: RESTful API for data operations
- **Static Assets**: Embedded CSS and JavaScript
- **Error Handling**: Proper error responses and validation
- **Development Mode**: Debug mode for development

### Frontend Features
- **Modern CSS**: Gradient backgrounds, animations, responsive design
- **JavaScript**: Interactive functionality and API calls
- **Mobile Support**: Touch-friendly interface
- **Accessibility**: Semantic HTML and proper labeling

## Technical Implementation

### Generator (`ApplicationGeneratorAgent`)
- **Web App Detection**: Keyword-based detection for web application requests
- **Template System**: Pre-built Flask application templates
- **File Creation**: Generates complete application structure
- **Dependency Management**: Automatic requirements.txt generation

### Launcher (`ApplicationLauncherService`)
- **Web App Detection**: Analyzes code for web framework patterns
- **Browser Integration**: Uses `webbrowser` module for auto-opening
- **Process Management**: Monitors Flask development server
- **URL Construction**: Builds proper URLs for web access

### API Integration
- **URL Passthrough**: Web app URLs included in API responses
- **Status Tracking**: Web app status in running applications list
- **Error Handling**: Proper error responses for web app issues

## Configuration

### Default Settings
```python
DEFAULT_WEB_APP_PORT = 5000
DEFAULT_WEB_APP_HOST = "127.0.0.1"
WEB_APP_DEBUG = True
BROWSER_AUTO_OPEN = True
```

### Security Considerations
- **Local Development**: Apps run in development mode
- **Port Binding**: Bound to localhost only by default
- **Process Isolation**: Each app runs in separate process
- **Validation**: Code validation before execution

## Testing

Run the web app functionality tests:
```bash
python test_web_app_functionality.py
```

This will test:
- Web app generation
- Browser launching
- API endpoints
- Running app management

## Troubleshooting

### Common Issues

1. **Browser doesn't open**
   - Check if `webbrowser` module works: `python -c "import webbrowser; webbrowser.open('http://google.com')"`
   - Verify no firewall blocking localhost connections

2. **Port already in use**
   - Change port in generated app or stop conflicting service
   - Check with: `netstat -ano | findstr :5000` (Windows) or `lsof -i :5000` (Unix)

3. **Flask not installed**
   - Install with: `pip install flask`
   - Check requirements.txt in generated app

4. **Permission errors**
   - Ensure write permissions to temp directory
   - Check file system permissions

### Debug Mode
- Generated apps run with `debug=True` by default
- Check Flask development server output for errors
- Use browser developer tools for frontend debugging

## Future Enhancements

- **Multiple Frameworks**: Support for FastAPI, Django
- **Database Integration**: SQLite/PostgreSQL support  
- **Authentication**: User login systems
- **Deployment**: Docker containerization
- **Templates**: More pre-built application types
- **Static Files**: Better static file handling
- **Production Mode**: WSGI server deployment options