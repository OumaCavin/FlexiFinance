"""
Contact and Newsletter Forms for FlexiFinance
"""
from django import forms
from django.core.validators import EmailValidator
from .models import Contact, NewsletterSubscription


class ContactForm(forms.ModelForm):
    """Contact form for general inquiries"""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your inquiry',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your message here...',
                'required': True
            })
        }
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Simple phone validation - you can make this more sophisticated
            if len(phone) < 10:
                raise forms.ValidationError('Please enter a valid phone number')
        return phone


class SupportForm(forms.ModelForm):
    """Support form for technical issues and support requests"""
    
    ISSUE_TYPES = [
        ('TECHNICAL', 'Technical Issue'),
        ('BILLING', 'Billing Question'),
        ('ACCOUNT', 'Account Problem'),
        ('LOAN', 'Loan Application'),
        ('GENERAL', 'General Support'),
    ]
    
    issue_type = forms.ChoiceField(
        choices=ISSUE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    priority = forms.ChoiceField(
        choices=[
            ('LOW', 'Low Priority'),
            ('MEDIUM', 'Medium Priority'),
            ('HIGH', 'High Priority'),
            ('URGENT', 'Urgent'),
        ],
        initial='MEDIUM',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Please describe your issue in detail...',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default subject based on issue type
        if 'initial' in kwargs and 'issue_type' in kwargs['initial']:
            issue_type = kwargs['initial']['issue_type']
            subject_mapping = {
                'TECHNICAL': 'Technical Support Request',
                'BILLING': 'Billing Inquiry',
                'ACCOUNT': 'Account Support',
                'LOAN': 'Loan Application Support',
                'GENERAL': 'General Support Request'
            }
            self.fields['subject'].initial = subject_mapping.get(issue_type, 'Support Request')


class NewsletterSubscriptionForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'first_name', 'last_name', 'interests']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name (optional)'
            }),
            'interests': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up interests choices
        self.fields['interests'].choices = [
            ('LOAN_UPDATES', 'Loan Updates & News'),
            ('FINANCIAL_TIPS', 'Financial Tips & Advice'),
            ('PROMOTIONS', 'Special Promotions'),
            ('PRODUCTS', 'New Product Launches'),
        ]
        # Make interests not required initially
        self.fields['interests'].required = False
    
    def clean_email(self):
        """Validate email format and uniqueness"""
        email = self.cleaned_data.get('email')
        validator = EmailValidator()
        try:
            validator(email)
        except forms.ValidationError:
            raise forms.ValidationError('Please enter a valid email address')
        
        # Check if email already exists (but allow updating existing subscriptions)
        if email:
            query = NewsletterSubscription.objects.filter(email=email)
            if self.instance and self.instance.pk:
                query = query.exclude(id=self.instance.id)
            
            if query.exists():
                raise forms.ValidationError('This email is already subscribed to our newsletter')
        
        return email
    
    def clean_interests(self):
        """Ensure interests is always a list"""
        interests = self.cleaned_data.get('interests')
        if not interests:
            return []
        return interests
    
    def save(self, commit=True):
        """Override save to handle newsletter subscription logic"""
        instance = super().save(commit=False)
        
        # Check if this email already exists
        existing = NewsletterSubscription.objects.filter(email=instance.email).first()
        if existing and (not self.instance or self.instance.pk != existing.pk):
            # Update existing subscription
            instance = existing
            instance.first_name = self.cleaned_data.get('first_name', existing.first_name)
            instance.last_name = self.cleaned_data.get('last_name', existing.last_name)
            instance.interests = self.cleaned_data.get('interests', existing.interests)
            instance.is_active = True  # Reactivate if was inactive
        
        if commit:
            instance.save()
        
        return instance


class QuickContactForm(forms.Form):
    """Quick contact form for footer and sidebar widgets"""
    
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name',
            'required': True
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email',
            'required': True
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Your message...',
            'required': True
        })
    )