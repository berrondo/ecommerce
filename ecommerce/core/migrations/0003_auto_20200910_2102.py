# Generated by Django 3.1.1 on 2020-09-10 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200910_2026'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='contents',
            new_name='content',
        ),
    ]
