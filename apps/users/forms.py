"""
Django Forms for FlexiFinance User Management
Professional form handling with validation and security
"""

from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
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
                'placeholder': '+254700000000',
                'pattern': r'^(\+254)?[0-9]{9}$'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
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

    def clean_phone_number(self):
        """
        Handle empty strings for unique fields to allow null in database
        """
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            return None
        
        # Remove any spaces or special characters except +
        cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # Ensure it starts with +254 for Kenyan numbers
        if cleaned_phone.startswith('0'):
            cleaned_phone = '+254' + cleaned_phone[1:]
        elif not cleaned_phone.startswith('+254'):
            cleaned_phone = '+254' + cleaned_phone
            
        return cleaned_phone

    def clean_monthly_income(self):
        """
        Validate monthly income is a positive number
        """
        income = self.cleaned_data.get('monthly_income')
        if income is not None and income < 0:
            raise forms.ValidationError('Monthly income cannot be negative')
        return income

    def clean_employment_duration(self):
        """
        Validate employment duration is a positive integer
        """
        duration = self.cleaned_data.get('employment_duration')
        if duration is not None and duration < 0:
            raise forms.ValidationError('Employment duration cannot be negative')
        return duration

    def clean_date_of_birth(self):
        """
        Ensure date of birth is not in the future and user is not too young
        """
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from datetime import date
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if dob > today:
                raise forms.ValidationError('Date of birth cannot be in the future')
            elif age < 18:
                raise forms.ValidationError('You must be at least 18 years old')
        
        return dob