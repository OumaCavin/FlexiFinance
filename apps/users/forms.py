"""
Django Forms for FlexiFinance User Management
Professional form handling with validation and security
"""

from django import forms
from .models import User
from datetime import date

class UserFormMixin:
    """
    Mixin to share cleaning logic across multiple forms
    """
    def clean_phone_number(self):
        """Handle empty strings and format Kenyan numbers"""
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            return None  # Return None so it saves as NULL in DB (avoiding unique constraint on '')
        
        # Remove spaces/special chars
        cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Format to +254
        if cleaned_phone.startswith('0'):
            cleaned_phone = '+254' + cleaned_phone[1:]
        elif not cleaned_phone.startswith('+254'):
            cleaned_phone = '+254' + cleaned_phone
            
        # Check uniqueness (excluding current user)
        query = User.objects.filter(phone_number=cleaned_phone)
        if self.instance and self.instance.pk:
            query = query.exclude(id=self.instance.id)
            
        if query.exists():
            raise forms.ValidationError("A user with that phone number already exists.")
            
        return cleaned_phone

    def clean_national_id(self):
        """Handle empty strings for National ID"""
        national_id = self.cleaned_data.get('national_id')
        if not national_id:
            return None  # Return None for uniqueness compatibility
            
        query = User.objects.filter(national_id=national_id)
        if self.instance and self.instance.pk:
            query = query.exclude(id=self.instance.id)
            
        if query.exists():
            raise forms.ValidationError("A user with that National ID already exists.")
        return national_id

    def clean_date_of_birth(self):
        """Validate age"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (today.month, today.day))
            
            if dob > today:
                raise forms.ValidationError('Date of birth cannot be in the future')
            elif age < 18:
                raise forms.ValidationError('You must be at least 18 years old')
        return dob

    def clean_monthly_income(self):
        """Validate positive income"""
        income = self.cleaned_data.get('monthly_income')
        if income is not None and income < 0:
            raise forms.ValidationError('Monthly income cannot be negative')
        return income

    def clean_employment_duration(self):
        """Validate positive duration"""
        duration = self.cleaned_data.get('employment_duration')
        if duration is not None and duration < 0:
            raise forms.ValidationError('Employment duration cannot be negative')
        return duration

    def clean_emergency_contact_phone(self):
        """Validate emergency contact phone number doesn't conflict with existing users (except current user)"""
        phone = self.cleaned_data.get('emergency_contact_phone')
        if not phone:
            return None
        
        # Check if emergency contact phone number exists for other users (exclude current user)
        if self.instance and self.instance.pk:
            existing_user = User.objects.filter(emergency_contact_phone=phone).exclude(id=self.instance.id).first()
        else:
            existing_user = User.objects.filter(emergency_contact_phone=phone).first()
            
        if existing_user:
            raise forms.ValidationError("A user with that emergency contact phone number already exists.")
        return phone


# --- Main Forms (Now inheriting from Mixin) ---

class UserProfileForm(UserFormMixin, forms.ModelForm):
    """
    Comprehensive profile form for FlexiFinance users
    Handles all user fields with proper validation and security
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'middle_name', 'last_name', 
            'phone_number', 'date_of_birth', 'national_id',
            'address', 'city', 'county', 'country',
            'occupation', 'employer_name', 'monthly_income',
            'employment_duration',
            'emergency_contact_name', 'emergency_contact_phone', 
            'emergency_contact_relationship'
        ]
        
        # Add Bootstrap styling to all inputs
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254700000000'
            }),
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',  # Critical fix for HTML5 date inputs
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'National ID or Passport Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Physical address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City or Town'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Kenya',
                'placeholder': 'Country'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your occupation'
            }),
            'employer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employer or Company name'
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Monthly income in KES'
            }),
            'employment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Duration in months'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact full name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone number'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship (e.g., Spouse, Parent)'
            }),
        }


class IdentityForm(UserFormMixin, forms.ModelForm):
    """
    Form for Identity Details section
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'date_of_birth', 'national_id']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'date_of_birth': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'National ID or Passport Number'
            }),
        }
    # clean_national_id and clean_date_of_birth are now inherited!


class ContactForm(UserFormMixin, forms.ModelForm):
    """
    Form for Contact Information section
    """
    
    class Meta:
        model = User
        fields = ['phone_number', 'address', 'city', 'county', 'country']
        widgets = {
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kenya',
                'value': 'Kenya'  # Set default value
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set country field to not required since it has a default value
        self.fields['country'].required = False
        # Set default value if field is empty
        if not self.instance.country:
            self.fields['country'].initial = 'Kenya'
        
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0712345678',
                'maxlength': '10'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Physical address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City or Town'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Kenya',
                'placeholder': 'Country'
            }),
        }
    # clean_phone_number is now inherited!


class EmploymentForm(UserFormMixin, forms.ModelForm):
    """
    Form for Employment & Financials section
    """
    
    class Meta:
        model = User
        fields = ['occupation', 'employer_name', 'monthly_income', 'employment_duration']
        
        widgets = {
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your occupation'
            }),
            'employer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employer or Company name'
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Monthly income in KES'
            }),
            'employment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Duration in months'
            }),
        }
    # clean_monthly_income and clean_employment_duration are now inherited!


class EmergencyContactForm(UserFormMixin, forms.ModelForm):
    """
    Form for Emergency Contact section
    """
    
    class Meta:
        model = User
        fields = ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship']
        
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact full name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0712345678',
                'maxlength': '10'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship (e.g., Spouse, Parent)'
            }),
        }
    # clean_emergency_contact_phone is now inherited!


class UserCreationForm(UserFormMixin, forms.ModelForm):
    """
    Custom user creation form for FlexiFinance
    Extends Django's UserCreationForm with additional fields
    """
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., +254712345678'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        return password2

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("A user with that phone number already exists.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
