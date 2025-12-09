# Fix Email Settings for FlexiFinance

## Issue: Email Configuration Mismatch

Your current settings are pointing to SendGrid instead of Mailpit. Here's how to fix it:

### Step 1: Update Email Settings

In your `flexifinance/settings.py` file, find the email configuration section (around line 348) and ensure it looks exactly like this:

```python
# MAILPIT EMAIL BACKEND (Local Development with Actual Email Sending)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 2526
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'cavin.otieno012@gmail.com'
EMAIL_HOST_PASSWORD = 'oakjazoekos'
EMAIL_TIMEOUT = 30
```

**Important:** Make sure these settings are NOT using `config()` function calls, as they might be picking up different environment variables.

### Step 2: Create/Update .env File

Create a `.env` file in your project root with:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=2526
EMAIL_USE_TLS=False
EMAIL_HOST_USER=cavin.otieno012@gmail.com
EMAIL_HOST_PASSWORD=oakjazoekos
EMAIL_TIMEOUT=30

# Other settings
DEBUG=True
SECRET_KEY=django-insecure-flexifinance-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 3: Restart Django Server

After updating the settings, restart your Django development server:

```bash
python manage.py runserver
```

### Step 4: Test Email Configuration

Run the email test to verify everything works:

```bash
python smtp_success_test.py
```

If this shows "Email sent successfully!", your email configuration is working.

### Step 5: Start Mailpit (if not running)

If Mailpit is not running, start it:

```bash
# Option 1: Start Mailpit (recommended)
mailpit --http :8080 --smtp :2526

# Option 2: Use built-in SMTP test server
python smtp_test_server.py
```

You should see Mailpit UI at http://localhost:8080 and emails will be captured there.