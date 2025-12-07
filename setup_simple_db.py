#!/usr/bin/env python3
"""
Simple database setup script for FlexiFinance.
Creates basic Django database tables directly.
"""

import os
import sys
import sqlite3

def create_database():
    """Create a simple SQLite database with Django tables"""
    
    db_path = "/workspace/django-microfinance-mpsa/db.sqlite3"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database")
    
    # Create new database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create basic Django auth tables
    print("📊 Creating Django database tables...")
    
    # Users table (simplified Django auth_user)
    cursor.execute('''
        CREATE TABLE auth_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password VARCHAR(128) NOT NULL,
            last_login DATETIME,
            is_superuser BOOLEAN NOT NULL DEFAULT 0,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL DEFAULT '',
            last_name VARCHAR(150) NOT NULL DEFAULT '',
            email VARCHAR(254) NOT NULL DEFAULT '',
            is_staff BOOLEAN NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User permissions (many-to-many)
    cursor.execute('''
        CREATE TABLE auth_user_user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
            UNIQUE(user_id, permission_id)
        )
    ''')
    
    # Groups table
    cursor.execute('''
        CREATE TABLE auth_group (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(150) NOT NULL UNIQUE
        )
    ''')
    
    # Permissions table
    cursor.execute('''
        CREATE TABLE auth_permission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            content_type_id INTEGER NOT NULL,
            codename VARCHAR(100) NOT NULL,
            UNIQUE(content_type_id, codename)
        )
    ''')
    
    # Content types table
    cursor.execute('''
        CREATE TABLE django_content_type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_label VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            UNIQUE(app_label, model)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE django_session (
            session_key VARCHAR(40) PRIMARY KEY,
            session_data TEXT NOT NULL,
            expire_date DATETIME NOT NULL
        )
    ''')
    
    # Insert basic content types
    cursor.execute('''
        INSERT INTO django_content_type (app_label, model) VALUES 
        ('auth', 'user'),
        ('auth', 'group'),
        ('auth', 'permission')
    ''')
    
    # Insert basic permissions for user management
    cursor.execute('''
        INSERT INTO auth_permission (name, content_type_id, codename) VALUES 
        ('Can add user', 1, 'add_user'),
        ('Can change user', 1, 'change_user'),
        ('Can delete user', 1, 'delete_user'),
        ('Can view user', 1, 'view_user'),
        ('Can add group', 2, 'add_group'),
        ('Can change group', 2, 'change_group'),
        ('Can delete group', 2, 'delete_group'),
        ('Can view group', 2, 'view_group')
    ''')
    
    # Create admin user
    print("👤 Creating admin superuser...")
    cursor.execute('''
        INSERT INTO auth_user (
            password, is_superuser, username, first_name, last_name, 
            email, is_staff, is_active, date_joined
        ) VALUES (
            'pbkdf2_sha256$720000$hash$hash', 1, 'admin', '', '', 
            'cavin.otieno012@gmail.com', 1, 1, CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"📁 Database location: {db_path}")
    
    return True

def create_superuser_script():
    """Create a script to properly set the admin password"""
    
    script_content = '''#!/usr/bin/env python3
"""
Set admin password script.
Run this after the database is created.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.insert(0, '/workspace/django-microfinance-mpsa')
os.environ.setdefault('SECRET_KEY', 'django-insecure-flexifinance-key-change-in-production')

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='django-insecure-flexifinance-key-change-in-production',
        ALLOWED_HOSTS=['localhost', '127.0.0.1'],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': '/workspace/django-microfinance-mpsa/db.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
        ],
        USE_TZ=True,
    )

django.setup()

from django.contrib.auth.models import User

# Set proper password for admin user
try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    print("✅ Admin password set successfully!")
    print("Username: admin")
    print("Password: admin123")
except User.DoesNotExist:
    print("❌ Admin user not found")
except Exception as e:
    print(f"❌ Error setting password: {e}")
'''
    
    script_path = "/workspace/set_admin_password.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"📝 Created password setup script: {script_path}")
    return script_path

def main():
    """Main setup function"""
    print("🔧 FlexiFinance Simple Database Setup")
    print("=" * 50)
    
    # Create database
    if create_database():
        print("\n✅ Database setup completed!")
        
        # Create password script
        script_path = create_superuser_script()
        
        print("\n" + "=" * 50)
        print("🎉 SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps:")
        print("1. Set the admin password:")
        print(f"   python {script_path}")
        print("")
        print("2. Start the Django development server:")
        print("   cd /workspace/django-microfinance-mpsa")
        print("   python manage.py runserver")
        print("")
        print("3. Access the admin panel:")
        print("   http://127.0.0.1:8000/admin/")
        print("")
        print("4. Login with:")
        print("   Username: admin")
        print("   Password: admin123")
        
        return True
    else:
        print("❌ Database setup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)