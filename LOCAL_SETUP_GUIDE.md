# FlexiFinance Local Setup Guide

## Quick Setup for Registration to Work Locally

When you pull the FlexiFinance repository from GitHub, registration won't work immediately because some files are intentionally excluded for security. Follow these steps:

### 1. Create Your Environment File

The `.env` file is excluded from Git for security reasons. You need to create it:

```bash
# Copy the example file
cp .env.example .env
```

Then edit the `.env` file with your local settings:

```bash
# Basic Django Configuration for Testing
SECRET_KEY=django-insecure-flexifinance-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Basic Database (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS=True
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if you use virtual environments
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up the Database

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
```

### 4. Collect Static Files

```bash
# Collect static files for CSS, JS, images
python manage.py collectstatic --noinput
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Now visit `http://127.0.0.1:8000/register` and registration should work!

## Why These Files Are Missing

### Files Excluded from Git (in `.gitignore`):
- `.env` - Environment variables and API keys
- `db.sqlite3` - Database file
- `__pycache__/` - Python cache files
- `*.log` - Log files
- `.pytest_cache/` - Test cache

### Files That Should Be in Git:
- ✅ All Python source code
- ✅ All HTML templates
- ✅ All CSS/JavaScript files
- ✅ Requirements.txt
- ✅ Database migration files
- ✅ Configuration files (settings.py, urls.py, etc.)

## Common Issues and Solutions

### Issue: "ModuleNotFoundError" when running the server
**Solution:** Install dependencies with `pip install -r requirements.txt`

### Issue: "OperationalError: no such table"
**Solution:** Run `python manage.py migrate` to create database tables

### Issue: "CSRF verification failed"
**Solution:** Make sure your `.env` file has `CORS_ALLOW_ALL_ORIGINS=True`

### Issue: Static files not loading (CSS/JS missing)
**Solution:** Run `python manage.py collectstatic --noinput`

### Issue: Registration form not submitting
**Solution:** 
1. Check browser console for JavaScript errors
2. Ensure the `.env` file exists and has proper settings
3. Run `python manage.py migrate` to set up database

## Environment File Template

Your `.env` file should look like this:

```env
# Basic Django Configuration for Testing
SECRET_KEY=django-insecure-flexifinance-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Basic Database (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS=True

# Optional: Email settings (for registration confirmation)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your_email@gmail.com
# EMAIL_HOST_PASSWORD=your_app_password
```

## Testing Registration

1. Start the server: `python manage.py runserver`
2. Go to: `http://127.0.0.1:8000/register`
3. Fill out the registration form
4. Submit and check for any errors

If registration still doesn't work, check:
- Browser developer console for JavaScript errors
- Django server terminal for any error messages
- Ensure all migrations have been applied: `python manage.py showmigrations`

## Getting Help

If you encounter issues:
1. Check the Django server output for error messages
2. Check browser console for JavaScript errors
3. Verify all steps above were completed
4. Ensure Python dependencies are installed correctly

The registration functionality is identical in both cloud and local environments - the only difference is the missing configuration files!