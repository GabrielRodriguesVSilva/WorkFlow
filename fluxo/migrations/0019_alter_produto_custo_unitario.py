# Generated by Django 5.1.6 on 2025-03-03 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0018_alter_leadacao_acao_alter_produto_data_modificacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='custo_unitario',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
