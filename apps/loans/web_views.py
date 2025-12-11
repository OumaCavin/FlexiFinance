"""
Web views for loan application and management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Loan

User = get_user_model()

@login_required
def loan_application(request):
    """Render the loan application form"""
    return render(request, 'loans/loan-application.html')

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