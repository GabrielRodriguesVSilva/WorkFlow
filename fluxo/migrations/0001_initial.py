# Generated by Django 5.1.6 on 2025-03-02 20:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_omie', models.IntegerField(unique=True)),
                ('empresa', models.CharField(max_length=255, unique=True)),
                ('nome_fantasia', models.CharField(max_length=255)),
                ('documento', models.CharField(max_length=255)),
                ('tipo', models.CharField(blank=True, max_length=255, null=True)),
                ('nome_contato', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(blank=True, max_length=20, null=True)),
                ('cep', models.CharField(blank=True, max_length=255, null=True)),
                ('estado', models.CharField(blank=True, max_length=255, null=True)),
                ('cidade', models.CharField(blank=True, max_length=255, null=True)),
                ('bairro', models.CharField(blank=True, max_length=255, null=True)),
                ('logradouro', models.CharField(blank=True, max_length=255, null=True)),
                ('instituicao', models.CharField(blank=True, max_length=255, null=True)),
                ('contribuinte', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField()),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.IntegerField(choices=[(0, 'Análise'), (1, 'Atendimento'), (2, 'APC'), (3, 'APV'), (4, 'Orçamento'), (5, 'Follow-Up'), (6, 'Finalizado')], default=0)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fluxo.cliente')),
                ('usuario', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='perfil_fotos/')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
