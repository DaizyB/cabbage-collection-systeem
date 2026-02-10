from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pickups', '0003_pickup_trash_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickup',
            name='verification_token',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='pickup',
            name='verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
