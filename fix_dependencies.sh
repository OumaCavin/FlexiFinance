#!/bin/bash
# FlexiFinance Dependency Fix Script

echo "🔧 Installing missing Python packages for FlexiFinance..."

# Install required packages
pip install django-allauth==65.13.1
pip install django-crispy-forms==2.5
pip install python-decouple==3.8
pip install python-dotenv==1.2.1
pip install djangorestframework==3.16.1
pip install djangorestframework-simplejwt==5.5.1
pip install pyjwt==2.10.1
pip install django-cors-headers==4.9.0
pip install django-filter==25.2

# Install optional packages
pip install debug-toolbar
pip install celery
pip install import-export

echo "✅ Package installation complete!"

# Fix debug_toolbar import issue
echo "🔧 Fixing debug_toolbar import issue..."
python fix_debug_toolbar.py

echo "✅ All dependencies should now be working!"