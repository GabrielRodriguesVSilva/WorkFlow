# Generated by Django 5.1.6 on 2025-03-03 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0009_leadproduto'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='custo_unitario',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
    ]
