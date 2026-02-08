from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('careers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectorapplication',
            name='phone',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='national_id',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='driving_license_number',
            field=models.CharField(blank=True, max_length=128, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='license_class',
            field=models.CharField(blank=True, max_length=64, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='license_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='vehicle_number_plate',
            field=models.CharField(blank=True, max_length=64, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='vehicle_type',
            field=models.CharField(default='truck', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='id_photo',
            field=models.ImageField(blank=True, null=True, upload_to='kyc/'),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='license_photo',
            field=models.ImageField(blank=True, null=True, upload_to='kyc/'),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='plate_photo',
            field=models.ImageField(blank=True, null=True, upload_to='kyc/'),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='selfie_photo',
            field=models.ImageField(blank=True, null=True, upload_to='kyc/'),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='answers',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='test_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='test_passed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='collectorapplication',
            name='status',
            field=models.CharField(choices=[('PENDING_VERIFICATION', 'Pending verification'), ('FAILED_TEST', 'Failed test'), ('KYC_REVIEW', 'KYC review'), ('APPROVED_COLLECTOR', 'Approved collector'), ('REJECTED', 'Rejected')], default='PENDING_VERIFICATION', max_length=32),
        ),
    ]
