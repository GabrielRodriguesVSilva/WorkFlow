# Generated by Django 5.1.6 on 2025-03-05 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0022_remove_lead_comentario_recusa_remove_lead_observacao_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='leadacao',
            name='acao',
            field=models.CharField(choices=[(0, 'Criação'), (1, 'Comentarios'), (2, 'Avanço de Status'), (3, 'Solicitação de Cliente'), (4, 'Informação de Analise'), (5, 'Troca de Responsável'), (6, 'Informação para o comprador'), (7, 'Produto adicionado ao lead'), (8, 'Produto removido do lead'), (9, 'Produto editado'), (10, 'Lead agurdando Retorno'), (11, 'Informação para vendas'), (12, 'Anexar Orçamento'), (13, 'Anexar Imagem'), (14, 'Anexar PDF'), (15, 'Anexar arquivo'), (16, 'Comentario de Follow-Up'), (17, 'Comentario Lead'), (18, 'Comentario de Finalização'), (19, 'Satus da Proposta'), (20, 'Proposta Finalizada'), (21, 'Retorno de Status')], max_length=20),
        ),
    ]
