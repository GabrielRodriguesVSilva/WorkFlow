# Generated by Django 5.1.7 on 2025-03-13 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0028_perfilusuario_codigo_vendedor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='cep_fim',
            field=models.IntegerField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='cep_inicio',
            field=models.IntegerField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='perfilusuario',
            name='codigo_vendedor',
            field=models.IntegerField(blank=True, max_length=50, null=True),
        ),
    ]
