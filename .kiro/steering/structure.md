# Project Structure

## Root Directory
```
wxauto/
├── wxauto/           # Main package directory
├── .kiro/            # Kiro AI assistant configuration
├── pyproject.toml    # Project configuration and dependencies
├── README.md         # Project documentation (Chinese)
├── LICENSE           # License file
└── .gitignore        # Git ignore patterns
```

## Package Organization

### Core Modules (`wxauto/`)
- `__init__.py` - Package entry point, exports WeChat, Chat, WxParam
- `wx.py` - Main WeChat automation class and Chat interface
- `param.py` - Configuration parameters and response classes
- `logger.py` - Colored logging system with file/console output
- `exceptions.py` - Custom exception classes
- `uiautomation.py` - UI automation wrapper
- `languages.py` - Multi-language support

### Message System (`wxauto/msgs/`)
- `base.py` - Base message classes and common functionality
- `msg.py` - Core message implementations
- `friend.py` - Friend-specific message handling
- `self.py` - Self-message handling
- `attr.py` - Message attributes and metadata
- `type.py` - Message type definitions

### UI Components (`wxauto/ui/`)
- `base.py` - Abstract base classes for UI windows
- `main.py` - Main WeChat window handling
- `chatbox.py` - Chat interface and message display
- `sessionbox.py` - Session/contact list management
- `navigationbox.py` - Navigation and menu handling
- `component.py` - Reusable UI components

### Utilities (`wxauto/utils/`)
- `tools.py` - General utility functions
- `win32.py` - Windows-specific utilities and helpers

## Naming Conventions
- **Classes**: PascalCase (WeChat, BaseMessage, ChatBox)
- **Methods**: snake_case (send_msg, get_all_message)
- **Constants**: UPPER_SNAKE_CASE (PROJECT_NAME, DEFAULT_SAVE_PATH)
- **Private methods**: Leading underscore (_listener_start, _lang)
- **UI Classes**: Suffix with "Wnd" for windows (WeChatMainWnd)

## Import Patterns
- Relative imports within package (`from .ui.main import`)
- TYPE_CHECKING imports for circular dependencies
- Explicit __all__ exports in __init__.py files