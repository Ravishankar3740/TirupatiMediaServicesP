# Generated by Django 3.2 on 2022-08-20 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paging', '0002_alter_facebookpages_facebook_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookLeadDataDumping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_name', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=13)),
                ('email', models.CharField(max_length=50)),
                ('created_time', models.DateField()),
                ('city', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_leat_sent', models.BooleanField(blank=True, default=False, null=True)),
                ('facebook_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paging.facebookpages')),
            ],
        ),
    ]
