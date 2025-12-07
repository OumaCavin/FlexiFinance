# Generated migration for Company model
from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(default='FlexiFinance Limited', max_length=200)),
                ('registration_number', models.CharField(max_length=50, unique=True)),
                ('license_number', models.CharField(max_length=100)),
                ('cbk_registration', models.CharField(help_text='Central Bank of Kenya Registration Number', max_length=100)),
                ('bank_name', models.CharField(default='Kenya Commercial Bank', max_length=200)),
                ('bank_account_name', models.CharField(default='FlexiFinance Limited', max_length=200)),
                ('bank_account_number', models.CharField(max_length=50)),
                ('physical_address', models.TextField()),
                ('postal_address', models.TextField()),
                ('city', models.CharField(default='Nairobi', max_length=100)),
                ('county', models.CharField(default='Nairobi County', max_length=100)),
                ('country', models.CharField(default='Kenya', max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField()),
                ('website', models.URLField(blank=True)),
                ('terms_version', models.CharField(default='1.0', max_length=20)),
                ('privacy_policy_version', models.CharField(default='1.0', max_length=20)),
                ('loan_agreement_version', models.CharField(default='1.0', max_length=20)),
                ('default_interest_rate', models.DecimalField(decimal_places=2, default=12.5, max_digits=5)),
                ('late_fee_fixed', models.DecimalField(decimal_places=2, default=500.0, max_digits=10)),
                ('late_fee_percentage', models.DecimalField(decimal_places=2, default=2.0, max_digits=5)),
                ('disbursement_timeframe_days', models.PositiveIntegerField(default=3)),
                ('arbitration_rules', models.CharField(default='Kenyan Centre for Arbitration Rules', max_length=200)),
                ('governing_law', models.CharField(default='Laws of Kenya', max_length=100)),
                ('jurisdiction', models.CharField(default='Nairobi, Kenya', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'company',
                'verbose_name': 'Company',
                'verbose_name_plural': 'Company Information',
            },
        ),
    ]