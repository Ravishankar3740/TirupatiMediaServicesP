# Generated by Django 3.2 on 2022-08-20 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paging', '0003_facebookleaddatadumping'),
    ]

    operations = [
        migrations.AddField(
            model_name='facebookleaddatadumping',
            name='lead_id',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]