# Fix Notification Templates

## Run this command to create default notification templates:

```bash
python manage.py create_default_templates
```

This will create the following templates:
- `welcome_email` - Welcome emails for new users
- `loan_approval` - Loan approval notifications
- `payment_confirmation` - Payment confirmation notifications

## What this fixes:
- Eliminates the "Failed to create notification" warnings when creating users
- Ensures welcome notifications work properly for new user registrations
- Sets up the notification system for loan and payment notifications

## After running the command:
The warning messages should disappear when you create new users or superusers.