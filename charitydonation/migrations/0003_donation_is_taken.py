# Generated by Django 4.0.6 on 2022-08-16 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charitydonation', '0002_donation'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='is_taken',
            field=models.BooleanField(default=False, verbose_name='Odebrany'),
        ),
    ]
