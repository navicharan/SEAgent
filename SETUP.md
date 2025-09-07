# SEAgent Setup Instructions

## Quick Setup (Any Laptop)

### 1. Clone/Copy the Project
```bash
# Copy the entire SEAgent folder to your laptop
# Or clone from Git repository
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac  
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies (Choose One Method)

#### Method A: Automatic Setup (Recommended)
```bash
python setup.py
```

#### Method B: Manual Core Installation
```bash
pip install fastapi uvicorn pydantic pydantic-settings PyYAML openai streamlit plotly requests rich
```

#### Method C: Full Requirements (May Have Conflicts)
```bash
pip install -r requirements-stable.txt
```

### 4. Configure API Key
```bash
# Create .env file or set environment variable
echo "OPENAI_API_KEY=your-key-here" > .env
```

### 5. Run the Application
```bash
python main_simple.py
```

## Troubleshooting

### Common Issues:
- **Version conflicts**: Use Method B (core installation)
- **Missing system libraries**: Install Visual C++ Build Tools (Windows) or build-essential (Linux)
- **Permission errors**: Run as administrator or use --user flag
- **Network issues**: Use --trusted-host flags for pip

### Platform-Specific Notes:
- **Windows**: May need Visual Studio Build Tools for some packages
- **Linux**: May need python3-dev and build-essential
- **Mac**: May need Xcode command line tools