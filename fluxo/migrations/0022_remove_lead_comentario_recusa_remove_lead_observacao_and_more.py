# Generated by Django 5.1.6 on 2025-03-04 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0021_lead_aceitou_proposta_lead_comentario_recusa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='comentario_recusa',
        ),
        migrations.RemoveField(
            model_name='lead',
            name='observacao',
        ),
        migrations.AlterField(
            model_name='leadacao',
            name='acao',
            field=models.CharField(choices=[(0, 'Criação'), (1, 'Comentarios'), (2, 'Alteração de Status'), (3, 'Solicitação de Cliente'), (4, 'Informação de Analise'), (5, 'Troca de Responsável'), (6, 'Informação para o comprador'), (7, 'Produto adicionado ao lead'), (8, 'Produto removido do lead'), (9, 'Produto editado'), (10, 'Lead agurdando Retorno'), (11, 'Informação para vendas'), (12, 'Anexar Orçamento'), (13, 'Anexar Imagem'), (14, 'Anexar PDF'), (15, 'Anexar arquivo'), (16, 'Comentario de Follow-Up'), (17, 'Comentario Lead'), (18, 'Comentario de Finalização'), (19, 'Aprovação de Proposta'), (20, 'Proposta de Finalizada')], max_length=20),
        ),
    ]
