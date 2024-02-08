# Generated by Django 4.2.9 on 2024-02-04 05:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('first_name', models.CharField(default='Bob', max_length=20)),
                ('last_name', models.CharField(default='Allen', max_length=20)),
                ('phone', models.CharField(default='1234567890', max_length=10)),
                ('email', models.EmailField(default='example@example.com', max_length=254)),
                ('is_driver', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DriverProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_model', models.CharField(default='Benz', max_length=20)),
                ('license_number', models.CharField(default='123ABC', max_length=20)),
                ('capacity', models.IntegerField(default=4, validators=[django.core.validators.MaxValueValidator(6)])),
                ('special_request_info', models.CharField(choices=[('Green Energy', 'Green Energy'), ('Accessibility', 'Accessibility'), ('Luxury', 'Luxury')], default='Wheelchair', max_length=20)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.userprofile')),
            ],
        ),
    ]
