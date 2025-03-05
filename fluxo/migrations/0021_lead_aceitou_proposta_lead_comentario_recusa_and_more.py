# Generated by Django 5.1.6 on 2025-03-04 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0020_leadacao_imagem_leadacao_pdf_omie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='aceitou_proposta',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='comentario_recusa',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='motivo_recusa',
            field=models.CharField(blank=True, choices=[(0, 'Outros'), (1, 'Preço'), (2, 'Parcelamento'), (3, 'Projeto Cancelado'), (4, 'Projeto Adiado'), (5, 'Prazo de entrega'), (6, 'Qualidade'), (7, 'Opcionais'), (8, 'Demora para atendimento/fluxo'), (9, 'Falta de relacionamento'), (10, 'Tecnologia'), (11, 'Preferência de marca')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='observacao',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='leadacao',
            name='acao',
            field=models.CharField(choices=[(0, 'Criação'), (1, 'Comentarios'), (2, 'Alteração de Status'), (3, 'Solicitação de Cliente'), (4, 'Informação de Analise'), (5, 'Troca de Responsável'), (6, 'Informação para o comprador'), (7, 'Produto adicionado ao lead'), (8, 'Produto removido do lead'), (9, 'Produto editado'), (10, 'Lead agurdando Retorno'), (11, 'Informação para vendas'), (12, 'Anexar Orçamento'), (13, 'Anexar Imagem'), (14, 'Anexar PDF'), (15, 'Anexar arquivo'), (16, 'Comentario de Follow-Up'), (17, 'Comentario Lead')], max_length=20),
        ),
    ]
