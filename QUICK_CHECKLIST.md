# FlexiFinance Quick Fix Checklist

## ✅ Step-by-Step Checklist

Use this checklist to systematically fix all issues:

### **Phase 1: Setup Environment**

- [ ] **Install missing packages:**
  ```bash
  pip install django-allauth==65.13.1 django-crispy-forms==2.5 python-decouple==3.8 python-dotenv==1.2.1 djangorestframework==3.16.1 djangorestframework-simplejwt==5.5.1 pyjwt==2.10.1 django-cors-headers==4.9.0 django-filter==25.2
  ```

- [ ] **Start Mailpit SMTP server:**
  ```bash
  mailpit --http :8080 --smtp :2526
  ```
  OR if Mailpit not installed:
  ```bash
  python smtp_test_server.py
  ```

### **Phase 2: Fix Configuration**

- [ ] **Update email settings in `flexifinance/settings.py`:**
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'localhost'
  EMAIL_PORT = 2526
  EMAIL_USE_TLS = False
  EMAIL_HOST_USER = 'cavin.otieno012@gmail.com'
  EMAIL_HOST_PASSWORD = 'oakjazoekos'
  EMAIL_TIMEOUT = 30
  ```

- [ ] **Comment out debug_toolbar in settings.py:**
  ```python
  # INSTALLED_APPS += ['debug_toolbar']
  # MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
  ```

### **Phase 3: Setup Database**

- [ ] **Create notification templates:**
  ```bash
  python manage.py create_default_templates
  ```

- [ ] **Verify Django starts without errors:**
  ```bash
  python manage.py runserver
  ```

### **Phase 4: Test Functionality**

- [ ] **Test email configuration:**
  ```bash
  python smtp_success_test.py
  ```
  ✅ Should show "Email sent successfully!"

- [ ] **Test Mailpit access:**
  - Go to: http://localhost:8080
  - ✅ Should see Mailpit web interface

- [ ] **Test user registration:**
  - Go to: http://localhost:8000/dashboard/register/
  - Fill form and submit
  - ✅ Should show success message
  - ✅ Check Mailpit for welcome email

- [ ] **Test user login:**
  - Go to: http://localhost:8000/dashboard/login/
  - Login with registered user
  - ✅ Should redirect to dashboard

- [ ] **Test admin login:**
  - Go to: http://localhost:8000/admin/
  - Login with admin credentials
  - ✅ Should access admin panel

### **Phase 5: Verification**

- [ ] **Check Django logs** - No error messages
- [ ] **Verify notification preferences** created for new users
- [ ] **Test complete user flow** - Register → Email → Login → Dashboard

## 🚨 If Something Goes Wrong

### Issue: "Failed to create notification" still appears
**Solution:** Run `python manage.py create_default_templates` again

### Issue: User registration form doesn't work
**Solution:** Check URL configuration - ensure `urls.py` imports from correct view

### Issue: No emails received
**Solution:** 
1. Verify Mailpit is running: `ps aux | grep mailpit`
2. Check Mailpit UI at http://localhost:8080
3. Verify SMTP settings in Django

### Issue: Users can't login after registration
**Solution:**
1. Check Django logs for authentication errors
2. Verify password is being hashed correctly
3. Check if user is_active flag is set

### Issue: Django won't start
**Solution:**
1. Comment out debug_toolbar in settings.py
2. Check for missing dependencies
3. Verify all required apps are installed

## 📝 Quick Commands Reference

```bash
# Start everything
python manage.py runserver                    # Django server
mailpit --http :8080 --smtp :2526            # Mailpit (in separate terminal)

# Test functionality
python smtp_success_test.py                   # Test email
python manage.py create_default_templates     # Create templates
python simple_diagnostic.py                   # Run diagnostics

# Access URLs
http://localhost:8000/                        # Django app
http://localhost:8000/dashboard/register/     # Registration
http://localhost:8000/dashboard/login/        # Login
http://localhost:8000/admin/                  # Admin panel
http://localhost:8080                         # Mailpit UI
```

## ✅ Success Indicators

When everything is working correctly, you should see:

- ✅ Django server starts without errors
- ✅ Email test sends successfully
- ✅ User registration creates users and shows success message
- ✅ Welcome emails appear in Mailpit UI
- ✅ Users can login after registration
- ✅ Admin panel accessible
- ✅ No "Failed to create notification" warnings
- ✅ Clean Django logs with no errors