# Generated by Django 3.1.1 on 2020-09-29 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20200927_0346'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='active',
            field=models.BooleanField(default=True, verbose_name='ativo'),
        ),
    ]