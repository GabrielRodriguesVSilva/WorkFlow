from django.db import migrations, models
import django.utils.timezone  # Import necessário para timezone.now

class Migration(migrations.Migration):

    dependencies = [
        ('fluxo', '0011_alter_produto_valor_unitario'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadproduto',
            name='data_criacao',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=django.utils.timezone.now,
        ),
    ]
