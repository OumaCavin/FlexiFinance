# FlexiFinance Email & User Registration Troubleshooting Guide

## Step 1: Check if Mailpit SMTP Server is Running

Mailpit must be running for email functionality to work. Run this command:

```bash
# Check if Mailpit is running
ps aux | grep mailpit

# Or check if port 2526 is in use
netstat -tlnp | grep 2526
```

### If Mailpit is NOT running:

**Option A: Install and start Mailpit**
```bash
# Install Mailpit (if not installed)
curl -fsSL https://raw.githubusercontent.com/axllent/mailpit/develop/install.sh | sh

# Start Mailpit
mailpit --http :8080 --smtp :2526
```

**Option B: Use the built-in SMTP test server**
```bash
# Start the built-in test SMTP server
python smtp_test_server.py
```

### If Mailpit IS running:
- It should be accessible at http://localhost:8080
- SMTP port should be 2526

## Step 2: Test Email Configuration

Run the email test script to verify everything is working:

```bash
python smtp_success_test.py
```

This will test your SMTP configuration and send a test email.

## Step 3: Create Notification Templates

Before testing user registration, create the notification templates:

```bash
python manage.py create_default_templates
```

Expected output:
```
Successfully created X default notification templates
```

## Step 4: Fix User Registration URL Configuration

The users app has been restructured:

**Check the current URL configuration:**

Edit `apps/users/urls.py` and verify it uses the correct view:

```python
from apps.users import views  # This contains all web functionality

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('payment-history/', views.payment_history, name='payment_history'),
    # ... other URLs
]
```

## Step 5: Test User Registration

### Test via Django Shell:
```bash
python manage.py shell
```

```python
from apps.users.models import User

# Create a test user
user = User.objects.create_user(
    username='test@example.com',
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

print(f"User created: {user.username}")
print(f"User can login: {user.check_password('testpass123')}")

# Check if notification preferences were created
from apps.notifications.models import UserNotificationPreference
prefs = UserNotificationPreference.objects.filter(user=user)
print(f"Notification preferences created: {len(prefs) > 0}")

exit()
```

### Test via Web Interface:
1. Go to http://localhost:8000/dashboard/register/
2. Fill out the registration form
3. Check for any error messages
4. Check Mailpit UI at http://localhost:8080 for received emails

## Step 6: Check User Login Issues

### Test admin user login:
1. Go to http://localhost:8000/admin/
2. Try logging in with your superuser credentials
3. Use **username** (not email) for login

### Check user status via shell:
```bash
python manage.py shell
```

```python
from apps.users.models import User

# Check your admin user
admin_user = User.objects.get(username='admin')
print(f"Username: {admin_user.username}")
print(f"Email: {admin_user.email}")
print(f"Is active: {admin_user.is_active}")
print(f"Is staff: {admin_user.is_staff}")
print(f"Is superuser: {admin_user.is_superuser}")
print(f"Can login: {admin_user.check_password('your_password')}")

exit()
```

### Fix admin user if needed:
```bash
python manage.py shell
```

```python
from apps.users.models import User

# Get or create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'cavin.otieno012@gmail.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

# Set password
admin_user.set_password('admin123')
admin_user.save()

print(f"Admin user updated. Can login: {admin_user.check_password('admin123')}")
exit()
```

## Step 7: Check Django Logs

Monitor Django logs for errors during user registration:

```bash
# Run Django with log output
python manage.py runserver 0.0.0.0:8000
```

Look for:
- Signal firing messages
- Email sending errors
- Database errors
- Authentication errors

## Step 8: Verify Signal Registration

Check if signals are properly connected:

```bash
python manage.py shell
```

```python
from apps.users.signals import *
from apps.notifications.signals import *

# This will import and register the signals
print("Signals imported successfully")

exit()
```

## Common Issues & Solutions

### Issue: "Failed to create notification" warning
**Solution:** Run `python manage.py create_default_templates`

### Issue: User registration form doesn't work
**Solution:** Check URL configuration in `web_urls.py` - ensure it uses the correct view

### Issue: User can't login after registration
**Solution:** Check if password is being hashed properly in the User model

### Issue: No emails received
**Solutions:**
1. Check if Mailpit is running
2. Check Django logs for SMTP errors
3. Test email configuration with test script

### Issue: User created in admin but can't login
**Solutions:**
1. Use username (not email) for login
2. Check `is_active`, `is_staff`, `is_superuser` flags
3. Reset password if needed

## Testing Checklist

- [ ] Mailpit running on port 2526
- [ ] Notification templates created
- [ ] Email test script works
- [ ] User registration creates users in database
- [ ] Welcome emails are sent (check Mailpit)
- [ ] Users can login after registration
- [ ] Admin user can login
- [ ] Django logs show no errors

## Next Steps

After following this guide, test the complete flow:
1. Create user via registration form
2. Verify user appears in database
3. Check Mailpit for welcome email
4. Try logging in with the new user
5. Test admin login functionality