# Company Model Documentation

## Overview

The Company model provides centralized storage for all legal and business information used across the FlexiFinance platform, particularly for loan agreements and other legal documents.

## Features

### Legal Information
- **Registration Details**: Company registration number, license number, CBK registration
- **Banking Information**: Bank account details for loan disbursement and repayment
- **Contact Information**: Physical address, postal address, phone, email
- **Legal Terms**: Governing law, arbitration rules, jurisdiction

### Loan Configuration
- **Default Interest Rate**: Standard interest rate for loans (default: 12.5%)
- **Late Payment Fees**: Both fixed amount (default: KSh 500) and percentage (default: 2%)
- **Disbursement Timeline**: Default timeframe for loan disbursement (default: 3 days)
- **Document Versions**: Track versions of terms, privacy policy, and loan agreements

## Usage

### In Templates

The Company model data is automatically available in the `LoanAgreementView`:

```html
<!-- Company name -->
{{ company.company_name }}

<!-- Interest rate with fallback -->
{{ company.default_interest_rate|default:12.5 }}%

<!-- Late fees with number formatting -->
KSh {{ company.late_fee_fixed|default:500|intcomma }}

<!-- Legal information -->
{{ company.governing_law|default:"Laws of Kenya" }}
{{ company.jurisdiction|default:"Nairobi, Kenya" }}
{{ company.arbitration_rules|default:"Kenyan Centre for Arbitration Rules" }}
```

### Default Company Instance

The model includes a `get_default_company()` class method that automatically creates a default company instance if none exists:

```python
from apps.core.models import Company

# Get or create default company
company = Company.get_default_company()
```

### Database Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `company_name` | CharField | Legal company name | "FlexiFinance Limited" |
| `registration_number` | CharField | Company registration number | Required |
| `license_number` | CharField | Business license number | Required |
| `cbk_registration` | CharField | Central Bank of Kenya registration | Required |
| `default_interest_rate` | DecimalField | Default annual interest rate | 12.5 |
| `late_fee_fixed` | DecimalField | Fixed late payment fee | 500.00 |
| `late_fee_percentage` | DecimalField | Percentage late payment fee | 2.0 |
| `disbursement_timeframe_days` | Integer | Days for loan disbursement | 3 |
| `governing_law` | CharField | Applicable law | "Laws of Kenya" |
| `arbitration_rules` | CharField | Arbitration body | "Kenyan Centre for Arbitration Rules" |

## Administration

Access the Django admin interface to manage company information:

1. Navigate to `/admin/`
2. Click on "Company Information"
3. Add or edit company details

## Migration

The Company model includes a migration file at `apps/core/migrations/0001_initial.py`. After deployment, run:

```bash
python manage.py migrate
```

## Template Integration

All loan agreement templates now pull real data from the Company model:

- Interest rates and fees
- Legal compliance information
- Company contact details
- Banking information
- Document version tracking

This ensures all legal documents are always up-to-date with the current company information.