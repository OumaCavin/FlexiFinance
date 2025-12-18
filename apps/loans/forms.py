"""
Loan Application Forms
"""
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Loan, LoanProduct


class LoanApplicationForm(forms.ModelForm):
    """Form for loan application"""
    
    class Meta:
        model = Loan
        fields = [
            'loan_type',
            'principal_amount',
            'loan_tenure',
            'purpose',
            'description',
            'interest_rate'
        ]
        widgets = {
            'loan_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'loan_type'
            }),
            'principal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'principal_amount',
                'min': '1000',
                'max': '1000000',
                'step': '100',
                'placeholder': 'Enter loan amount'
            }),
            'loan_tenure': forms.Select(attrs={
                'class': 'form-control',
                'id': 'loan_tenure'
            }),
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'purpose',
                'rows': 3,
                'placeholder': 'Explain the purpose of this loan'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'rows': 3,
                'placeholder': 'Additional details (optional)'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'interest_rate',
                'min': '5',
                'max': '30',
                'step': '0.1',
                'placeholder': 'Interest rate (%)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add default tenure options
        self.fields['loan_tenure'].choices = [
            (1, '1 month'),
            (3, '3 months'),
            (6, '6 months'),
            (12, '12 months'),
            (18, '18 months'),
            (24, '24 months'),
            (36, '36 months'),
        ]
        
        # Set default interest rate based on loan type
        if 'initial' in kwargs and 'loan_type' in kwargs['initial']:
            loan_type = kwargs['initial']['loan_type']
            default_rates = {
                'QUICK_CASH': 15.0,
                'BUSINESS': 12.0,
                'EMERGENCY': 18.0,
                'PERSONAL': 14.0,
                'EDUCATION': 10.0
            }
            self.fields['interest_rate'].initial = default_rates.get(loan_type, 15.0)
    
    def clean_principal_amount(self):
        """Validate loan amount"""
        amount = self.cleaned_data.get('principal_amount')
        if amount and amount < 1000:
            raise forms.ValidationError('Minimum loan amount is KES 1,000')
        if amount and amount > 1000000:
            raise forms.ValidationError('Maximum loan amount is KES 1,000,000')
        return amount
    
    def clean_loan_tenure(self):
        """Validate loan tenure"""
        tenure = self.cleaned_data.get('loan_tenure')
        if tenure and tenure not in [1, 3, 6, 12, 18, 24, 36]:
            raise forms.ValidationError('Invalid loan tenure selected')
        return tenure
    
    def clean_interest_rate(self):
        """Validate interest rate"""
        rate = self.cleaned_data.get('interest_rate')
        if rate and (rate < 5 or rate > 30):
            raise forms.ValidationError('Interest rate must be between 5% and 30%')
        return rate


class LoanProductSelectionForm(forms.Form):
    """Form for selecting loan product"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get active loan products
        products = LoanProduct.objects.filter(is_active=True)
        choices = [('', 'Select a loan product')] + [
            (product.id, f"{product.name} - {product.description[:50]}...")
            for product in products
        ]
        
        self.fields['product'] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'loan_product'
            })
        )


class LoanProductForm(forms.ModelForm):
    """Form for creating/editing loan products (Admin use)"""
    
    class Meta:
        model = LoanProduct
        fields = [
            'product_code', 'name', 'description',
            'min_amount', 'max_amount', 'min_tenure', 'max_tenure',
            'interest_rate', 'processing_fee', 'late_fee_rate',
            'min_income', 'min_employment_duration', 'min_credit_score',
            'is_active', 'requires_documents'
        ]
        widgets = {
            'product_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique product code (e.g., QUICK_CASH)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Product description'
            }),
            'min_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Minimum loan amount'
            }),
            'max_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Maximum loan amount'
            }),
            'min_tenure': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Minimum tenure in months'
            }),
            'max_tenure': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Maximum tenure in months'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': 'Annual interest rate (%)'
            }),
            'processing_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Processing fee'
            }),
            'late_fee_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': 'Late fee rate (%)'
            }),
            'min_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Minimum monthly income'
            }),
            'min_employment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Minimum employment duration (months)'
            }),
            'min_credit_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '300',
                'max': '850',
                'placeholder': 'Minimum credit score'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'requires_documents': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')
        min_tenure = cleaned_data.get('min_tenure')
        max_tenure = cleaned_data.get('max_tenure')
        
        # Validate amount range
        if min_amount and max_amount and min_amount >= max_amount:
            raise forms.ValidationError('Maximum amount must be greater than minimum amount')
        
        # Validate tenure range
        if min_tenure and max_tenure and min_tenure >= max_tenure:
            raise forms.ValidationError('Maximum tenure must be greater than minimum tenure')
        
        # Validate interest rate range
        interest_rate = cleaned_data.get('interest_rate')
        if interest_rate and (interest_rate < 0 or interest_rate > 100):
            raise forms.ValidationError('Interest rate must be between 0% and 100%')
        
        return cleaned_data
    
    def clean_product_code(self):
        product_code = self.cleaned_data.get('product_code')
        if product_code:
            # Check uniqueness (excluding current instance during edit)
            query = LoanProduct.objects.filter(product_code=product_code)
            if self.instance and self.instance.pk:
                query = query.exclude(id=self.instance.id)
            
            if query.exists():
                raise forms.ValidationError('A loan product with this code already exists')
        return product_code