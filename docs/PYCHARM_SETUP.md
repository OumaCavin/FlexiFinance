# FlexiFinance PyCharm Setup Guide

**Author:** Cavin Otieno  
**Date:** December 5, 2025  
**Version:** 1.0.0

## Overview

This guide provides comprehensive instructions for setting up FlexiFinance development environment in PyCharm Community or Professional edition. PyCharm offers excellent Django development features that will enhance your productivity.

## System Requirements

### PyCharm Version
- **PyCharm Community Edition 2024.1+** (Recommended for open source)
- **PyCharm Professional 2024.1+** (For advanced features)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux

### System Resources
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **Python**: Version 3.11+

## Installation

### 1. Download and Install PyCharm

#### Windows
1. Download from: https://www.jetbrains.com/pycharm/download/
2. Run the installer `pycharm-community-2024.1.exe`
3. Follow installation wizard
4. Choose "Do not import settings" for fresh installation

#### macOS
1. Download `pycharm-community-2024.1.dmg`
2. Drag PyCharm to Applications folder
3. Launch PyCharm from Applications

#### Linux (Ubuntu/Debian)
```bash
# Download and install
wget https://download.jetbrains.com/python/pycharm-community-2024.1.tar.gz
tar -xzf pycharm-community-2024.1.tar.gz
cd pycharm-community-2024.1/bin
./pycharm.sh
```

### 2. Initial PyCharm Configuration

#### First Launch Setup
1. **Import Settings**: Choose "Do not import settings"
2. **UI Theme**: Select your preferred theme (Dark or Light)
3. **Keyboard Scheme**: Choose your preferred keymap
4. **Plugin Installation**: 
   - Install "Python Community Edition" (if not bundled)
   - Install "Django" plugin
   - Install "Git Integration" plugin

## Project Setup

### 1. Clone the Repository

#### Using PyCharm
1. Open PyCharm
2. Select "Get from VCS"
3. Choose "Git"
4. Repository URL: `https://github.com/OumaCavin/FlexiFinance.git`
5. Choose directory for the project
6. Click "Clone"

#### Using Command Line
```bash
git clone https://github.com/OumaCavin/FlexiFinance.git
cd FlexiFinance
```

### 2. Open Project in PyCharm
1. Open PyCharm
2. Select "Open"
3. Navigate to the project directory
4. Select the root folder `FlexiFinance`
5. Click "Open as Project"

### 3. Configure Python Interpreter

#### Set Up Virtual Environment
1. Go to `File` → `Settings` (Windows/Linux) or `PyCharm` → `Preferences` (macOS)
2. Navigate to `Project: FlexiFinance` → `Python Interpreter`
3. Click the gear icon → `Add`
4. Choose `System Interpreter`
5. Click `Existing Environment` and select your Python 3.11+ interpreter
6. Alternatively, click `Add New Environment` and choose location for venv

#### Create Virtual Environment in PyCharm
1. Click the gear icon → `Add`
2. Choose `System Interpreter`
3. Click `Add New Environment`
4. Select location: `project_path/venv`
5. Click `OK`

### 4. Install Dependencies

#### Using PyCharm Terminal
1. Open Terminal in PyCharm (`Alt+F12`)
2. Ensure you're in the project directory
3. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### Using PyCharm Package Manager
1. Go to `File` → `Settings` → `Project: FlexiFinance` → `Python Interpreter`
2. Click the `+` button
3. Search for packages from `requirements.txt`
4. Install each package individually

## Django Configuration

### 1. Configure Django Support
1. Go to `File` → `Settings` → `Project: FlexiFinance` → `Django`
2. Check `Enable Django Support`
3. Set Django project root to the project directory
4. Set settings module to `flexifinance.settings`
5. Set manage.py to `project_root/manage.py`

### 2. Configure Run/Debug Configuration

#### Run Development Server
1. Right-click on `manage.py` in the project tree
2. Select "Run 'manage'" or "Debug 'manage'"
3. In the run configuration, change to:
   ```
   Name: Django Server
   Script path: manage.py
   Parameters: runserver
   ```

#### Alternative: Create Django Configuration
1. Go to `Run` → `Edit Configurations`
2. Click `+` → `Django Server`
3. Configure:
   ```
   Name: Django Development
   Host: 127.0.0.1
   Port: 8000
   Additional options: --debug-mode
   ```

### 3. Configure Static Files
1. Go to `Settings` → `Project: FlexiFinance` → `Django`
2. Set "Static files (CSS, JavaScript, Images)" mapping:
   ```
   URL: /static/
   Directory: $PROJECT_DIR$/static
   ```

## Environment Configuration

### 1. Set Up Environment Variables

#### Using PyCharm Run Configuration
1. Edit Django Server run configuration
2. Go to "Environment variables" section
3. Add variables:
   ```
   DEBUG=True
   SECRET_KEY=django-insecure-flexifinance-key-change-in-production
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

#### Using .env File
1. Create `.env` file in project root:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` file with your configuration
3. PyCharm will automatically load environment variables

### 2. Configure Database

#### SQLite (Default)
```python
# No additional configuration needed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### PostgreSQL Configuration
1. Install PostgreSQL and create database
2. Set environment variables in PyCharm:
   ```
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=flexifinance_db
   DB_USER=flexifinance_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

#### MySQL Configuration
1. Install MySQL and create database
2. Set environment variables:
   ```
   DB_ENGINE=django.db.backends.mysql
   DB_NAME=flexifinance_db
   DB_USER=flexifinance_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

### 3. M-Pesa Configuration

Set up M-Pesa environment variables:
```bash
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_PASSKEY=your_passkey
MPESA_SHORTCODE=174379
MPESA_ENVIRONMENT=sandbox
```

## Database Management

### 1. Set Up Database in PyCharm

#### PostgreSQL
1. Go to `Database` panel (right sidebar)
2. Click `+` → `Data Source` → `PostgreSQL`
3. Configure connection:
   ```
   Host: localhost
   Port: 5432
   Database: flexifinance_db
   User: flexifinance_user
   Password: your_password
   ```
4. Click "Test Connection"
5. Apply and OK

#### MySQL
1. Click `+` → `Data Source` → `MySQL`
2. Configure connection:
   ```
   Host: localhost
   Port: 3306
   Database: flexifinance_db
   User: flexifinance_user
   Password: your_password
   ```
3. Test connection and apply

### 2. Database Operations

#### Run Migrations
1. Open Django Console in PyCharm
2. Run:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

#### Create Superuser
```bash
python manage.py createsuperuser
```

#### Access Database Console
1. Right-click on your database connection
2. Select "Console"
3. Execute SQL queries directly

## Git Integration

### 1. Configure Git
1. Go to `VCS` → `Enable Version Control Integration`
2. Select "Git"
3. Configure git (if not done already):
   ```bash
   git config user.name "OumaCavin"
   git config user.email "cavin.otieno012@gmail.com"
   ```

### 2. Git Workflow in PyCharm
1. **Commit Changes**: `Ctrl+K` or `Cmd+K`
2. **Push to Remote**: `Ctrl+Shift+K` or `Cmd+Shift+K`
3. **Pull Changes**: `Ctrl+T` or `Cmd+T`
4. **View History**: Right-click file → `Git` → `Show History`

### 3. Gitignore Configuration
The project includes `.gitignore` file. PyCharm will respect these settings automatically.

## Code Quality Tools

### 1. Code Inspection
1. Go to `File` → `Settings` → `Editor` → `Inspections`
2. Enable Python inspections:
   - Python inspections
   - Django inspections
   - Code style inspections

### 2. Code Formatting
1. Go to `File` → `Settings` → `Tools` → `External Tools`
2. Set up Black formatter:
   - Click `+` to add new tool
   - Name: `Black Formatter`
   - Program: `black`
   - Arguments: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

### 3. Import Sorting
1. Install isort in your virtual environment
2. Set up as external tool:
   - Name: `isort`
   - Program: `isort`
   - Arguments: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

### 4. Running Code Quality Tools
```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8 .

# Run tests with coverage
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

## PyCharm Features for Django

### 1. Django Template Support
- **Syntax Highlighting**: HTML templates
- **Code Completion**: Django template tags
- **Navigation**: Jump between views and templates
- **Debugging**: Template debugging support

### 2. Django Model Support
- **Database Tools**: Visual database browser
- **Model Navigation**: Jump from models to admin
- **Migration Support**: Generate and manage migrations

### 3. Django Debugging
1. Set breakpoints in Python code
2. Run in debug mode (`Shift+F9`)
3. Use debug console to inspect variables
4. Step through code execution

### 4. Django Code Inspection
- **Unused Imports**: Detect unused imports
- **Django Settings**: Validate Django settings
- **Template Tags**: Check for invalid template usage

## Debugging Setup

### 1. Configure Debug Configuration
1. Go to `Run` → `Edit Configurations`
2. Select Django Server configuration
3. Check "Enable Django debugging"
4. Set breakpoints in code

### 2. Debug Django Views
1. Open a view file
2. Click in the gutter to set breakpoint
3. Run Django server in debug mode
4. Make request to the view
5. PyCharm will stop at breakpoint

### 3. Debug Django Templates
1. Enable Django template debugging
2. Set breakpoints in template files
3. Run server in debug mode
4. Navigate to template to see debug info

### 4. Debug Django ORM
1. Set breakpoints in Django ORM queries
2. Debug SQL queries being executed
3. Inspect query performance

## Testing Setup

### 1. Configure Test Runner
1. Go to `File` → `Settings` → `Project: FlexiFinance` → `Tools` → `Python Integrated Tools`
2. Set "Default test runner" to "pytest"

### 2. Run Tests
1. **Run All Tests**: Right-click project → `Run 'pytest'`
2. **Run Specific Test**: Right-click test file → `Run 'pytest in test_file.py'`
3. **Run Test with Coverage**: Use coverage package

### 3. Test Configuration
```python
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = flexifinance.settings
python_files = tests.py test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=. --cov-report=html
```

## Virtual Environment Management

### 1. Manage Virtual Environment
1. Go to `File` → `Settings` → `Project` → `Python Interpreter`
2. See installed packages
3. Install/uninstall packages
4. Upgrade packages

### 2. Requirements File Management
1. Right-click `requirements.txt`
2. Select "Install requirements"
3. PyCharm will install/update all packages

### 3. Dependency Version Control
1. Pin exact versions in `requirements.txt`
2. Use `pip freeze > requirements.txt` to update
3. Regularly update dependencies

## Performance Optimization

### 1. PyCharm Performance Settings
1. Go to `File` → `Settings` → `Appearance & Behavior` → `System Settings`
2. Enable:
   - "Save files automatically"
   - "Reopen last project on startup"
3. Disable:
   - "Sync with VCS"
   - "Power save mode"

### 2. Code Inspection Settings
1. Go to `File` → `Settings` → `Editor` → `Inspections`
2. Disable unnecessary inspections
3. Focus on Python and Django inspections

### 3. Memory Settings
1. Edit PyCharm properties file:
   - Windows: `%APPDATA%\JetBrains\PyCharm2024.1\pycharm64.exe.vmoptions`
   - macOS: `/Applications/PyCharm CE.app/Contents/bin/pycharm64.exe.vmoptions`
   - Linux: `~/.PyCharmCE2024.1/config/pycharm64.exe.vmoptions`
2. Increase memory:
   ```
   -Xmx2048m
   -Xms512m
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Django Not Recognized
```bash
# In PyCharm terminal
pip install Django
```

#### 2. Database Connection Issues
- Check database credentials in `.env` file
- Verify database server is running
- Test connection with PyCharm Database tool

#### 3. Static Files Not Loading
1. Check static files configuration in settings
2. Run `python manage.py collectstatic`
3. Verify URL patterns for static files

#### 4. M-Pesa Integration Issues
1. Check M-Pesa credentials in environment
2. Verify callback URLs are accessible
3. Use M-Pesa sandbox for testing

#### 5. Import Errors
1. Ensure project root is marked as "Sources Root"
2. Check Python interpreter path
3. Verify virtual environment is activated

### Performance Issues
1. Increase PyCharm memory allocation
2. Disable unnecessary plugins
3. Indexing issues: `File` → `Invalidate Caches and Restart`
4. Large project: Enable "Power save mode"

### Git Issues
1. Authentication issues: Configure git credentials
2. Large files: Use Git LFS
3. Merge conflicts: Use PyCharm merge tool

## Useful PyCharm Shortcuts

### Navigation
- `Ctrl+N`: Search files
- `Ctrl+Shift+N`: Search everywhere
- `Ctrl+E`: Recent files
- `Ctrl+G`: Go to line
- `Alt+F12`: Toggle terminal

### Code Editing
- `Ctrl+D`: Duplicate line
- `Ctrl+Y`: Delete line
- `Ctrl+/`: Comment/uncomment
- `Ctrl+Alt+L`: Reformat code
- `Ctrl+Alt+O`: Optimize imports

### Running and Debugging
- `Shift+F10`: Run
- `Shift+F9`: Debug
- `F8`: Step over
- `F7`: Step into
- `Alt+F9`: Run to cursor

### Refactoring
- `Shift+F6`: Rename
- `Ctrl+Alt+M`: Extract method
- `Ctrl+Alt+V`: Extract variable

## Advanced PyCharm Features

### 1. Live Templates
Create custom templates for common code patterns:
1. Go to `File` → `Settings` → `Editor` → `Live Templates`
2. Create templates for:
   - Django views
   - Model definitions
   - Test cases

### 2. File Templates
Create templates for new files:
1. Go to `File` → `Settings` → `Editor` → `File and Code Templates`
2. Create templates for:
   - Django models
   - Django views
   - Test files

### 3. Database Tools
- **Query Console**: Execute SQL queries
- **Data Editor**: View and edit table data
- **Diagram**: Visualize database schema
- **Migration**: Generate SQL for migrations

### 4. Remote Development
1. Set up remote interpreter
2. Deploy to remote server
3. Debug on remote server
4. Sync files automatically

## Professional Django Development

### 1. Project Structure
PyCharm helps maintain proper Django project structure:
- Apps organization
- Template structure
- Static files management
- Media files handling

### 2. Code Quality
- **Inspection**: Continuous code quality checks
- **Formatting**: Automatic code formatting
- **Testing**: Integrated test running
- **Coverage**: Test coverage analysis

### 3. Version Control
- **Git Integration**: Built-in Git support
- **Change Tracking**: Visual change tracking
- **Merge Tool**: Advanced merge capabilities
- **Branching**: Easy branch management

### 4. Deployment
- **Remote Servers**: Configure deployment targets
- **SSH**: Connect to remote servers
- **Database**: Deploy to production databases
- **Static Files**: Automated deployment

## Conclusion

With proper PyCharm configuration, your FlexiFinance development experience will be significantly enhanced. The IDE provides powerful tools for Django development, debugging, testing, and deployment.

For additional help:
- **PyCharm Documentation**: https://www.jetbrains.com/help/pycharm/
- **Django Documentation**: https://docs.djangoproject.com/
- **FlexiFinance Support**: support@flexifinance.com

---

**Happy coding with FlexiFinance and PyCharm! 🚀**