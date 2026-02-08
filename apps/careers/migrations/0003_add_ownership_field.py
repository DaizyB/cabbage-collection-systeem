from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0002_add_kyc_and_test_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectorapplication',
            name='ownership',
            field=models.CharField(choices=[('company', 'Company-owned'), ('personal', 'Personal / third-party')], default='personal', max_length=16),
            preserve_default=False,
        ),
    ]
