"""
Web views for loan application and management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Loan
from .forms import LoanApplicationForm, LoanProductForm

User = get_user_model()

@login_required
def loan_application(request):
    """Handle loan application form submission and display"""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            try:
                # Create loan application
                loan = form.save(commit=False)
                loan.user = request.user
                
                # Set default values
                loan.processing_fee = loan.principal_amount * 0.02  # 2% processing fee
                loan.remaining_balance = loan.total_amount
                loan.status = 'SUBMITTED'
                
                # Validate and save
                loan.full_clean()
                loan.save()
                
                messages.success(
                    request, 
                    f'Your loan application has been submitted successfully! Reference: {loan.loan_reference}'
                )
                return redirect('loans:loan_detail', loan_id=loan.id)
                
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate form with user's profile data
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            # You can pre-populate fields based on user profile
            
        form = LoanApplicationForm(initial=initial_data)
    
    context = {
        'form': form,
        'page_title': 'Loan Application',
        'user': request.user
    }
    return render(request, 'loans/loan-application.html', context)

@login_required
def loan_detail(request, loan_id):
    """Show loan details after successful submission"""
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    context = {
        'loan': loan,
        'page_title': f'Loan Details - {loan.loan_reference}'
    }
    return render(request, 'loans/loan_detail.html', context)

@login_required
def my_loans(request):
    """List all loans for the current user"""
    loans = Loan.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'loans': loans,
        'page_title': 'My Loans'
    }
    return render(request, 'users/my_loans.html', context)