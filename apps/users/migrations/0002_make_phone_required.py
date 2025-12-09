# Generated migration to make phone_number required for M-Pesa
from django.db import migrations, models
from django.core.validators import RegexValidator

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # First, set a temporary default value for existing NULL entries
        migrations.RunSQL(
            sql="UPDATE users_user SET phone_number = '+254000000000' WHERE phone_number IS NULL;",
            reverse_sql="UPDATE users_user SET phone_number = NULL WHERE phone_number = '+254000000000';"
        ),
        
        # Then alter the field to be non-nullable
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(
                help_text='M-Pesa registered phone number',
                max_length=15,
                unique=True,
                validators=[RegexValidator(
                    message='Enter a valid phone number starting with + and followed by 9-15 digits.',
                    regex='^\\+?1?\\d{9,15}$'
                )]
            ),
        ),
    ]