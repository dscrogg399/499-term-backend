# Generated by Django 4.1.5 on 2023-04-14 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thermostat',
            name='max_temp',
        ),
        migrations.RemoveField(
            model_name='thermostat',
            name='min_temp',
        ),
    ]
