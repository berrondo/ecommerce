# Generated by Django 3.1.1 on 2020-09-23 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20200921_0555'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-id'], 'verbose_name': 'pedido', 'verbose_name_plural': 'pedidos'},
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
