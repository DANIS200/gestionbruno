# Generated by Django 5.1 on 2024-10-05 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='matériels',
            new_name='materiels',
        ),
    ]
