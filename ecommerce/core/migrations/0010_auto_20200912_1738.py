# Generated by Django 3.1.1 on 2020-09-12 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200911_0600'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productcart',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='productcart',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='productcart',
            name='product',
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'carrinho', 'verbose_name_plural': 'carrinhos'},
        ),
        migrations.AlterModelOptions(
            name='productorder',
            options={'verbose_name': 'inclusão', 'verbose_name_plural': 'inclusões'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.AddField(
            model_name='order',
            name='content',
            field=models.ManyToManyField(blank=True, through='core.ProductOrder', to='core.Product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='core.customer'),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='core.order', verbose_name='carrinho'),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart', to='core.product', verbose_name='produto'),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='quantidade'),
        ),
        migrations.AlterUniqueTogether(
            name='productorder',
            unique_together={('order', 'product')},
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='ProductCart',
        ),
    ]
