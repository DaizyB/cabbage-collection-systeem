from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='pickup_qr_token',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
