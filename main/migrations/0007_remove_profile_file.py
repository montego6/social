# Generated by Django 4.0.4 on 2022-08-08 20:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_profile_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='file',
        ),
    ]