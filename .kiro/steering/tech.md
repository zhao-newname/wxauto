# Technology Stack

## Build System
- **Package Manager**: setuptools with pyproject.toml configuration
- **Build Backend**: setuptools.build_meta
- **Python Version**: 3.8-3.12 (excluding 3.13+)

## Core Dependencies
- **pywin32**: Windows API access for UI automation
- **comtypes**: COM interface automation
- **pyperclip**: Clipboard operations
- **pillow**: Image processing and handling
- **psutil**: System and process utilities
- **tenacity**: Retry mechanisms and fault tolerance
- **colorama**: Terminal color output for logging

## Architecture Patterns
- **UI Automation**: Uses Windows UIAutomation framework via pywin32
- **Observer Pattern**: Message listening with callback functions
- **Abstract Base Classes**: Consistent interface design (BaseUIWnd, BaseMessage)
- **Threading**: Daemon threads for message monitoring
- **Singleton-like**: WeChat instance management

## Common Commands
```bash
# Install in development mode
pip install -e .

# Install from PyPI
pip install wxauto

# Run with logging enabled
python -c "from wxauto.param import WxParam; WxParam.ENABLE_FILE_LOGGER = True"
```

## Key Technical Notes
- Requires `pythoncom.CoInitialize()` for COM operations
- Uses Windows-specific APIs (win32gui, UIAutomation)
- Thread-safe message handling with RLock
- Configurable parameters via WxParam class
- Custom logging with colored console output