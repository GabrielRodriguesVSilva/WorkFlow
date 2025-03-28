from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    foto = models.ImageField(upload_to="perfil_fotos/", blank=True, null=True)
    ativo = models.BooleanField(default=True)
    cep_inicio = models.IntegerField(blank=True, null=True)
    cep_fim = models.IntegerField(blank=True, null=True)
    codigo_vendedor = models.IntegerField(blank=True, null=True)


    class Meta:
        permissions = [
            ("gerencia_usuario", "Gerencia Usuário"),
        ]

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Cliente(models.Model):
    id_omie = models.IntegerField(unique=True)
    empresa = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255)
    documento = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255, blank=True, null=True)



    nome_contato = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    
    cep = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=255, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)

    instituicao = models.CharField(max_length=255, blank=True, null=True)
    contribuinte = models.BooleanField(default=False)
    codigo_vendedor = models.IntegerField(blank=True, null=True)
    


    def __str__(self):
        return self.empresa

class Lead(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=False)
    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads_criador")
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads_responsavel", null=True)
    user_indicado = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads_indicado", null=True)
    
    STATUS_CHOICES = [
        (0, 'Análise'),
        (1, 'Atendimento'),
        (2, 'APC'),
        (3, 'APV'),
        (4, 'Orçamento'),
        (5, 'Follow-Up'),
        (6, 'Finalizado'),
    ]

    FINALIDADE_CHOICES = [
        (0, 'Consumo'),
        (1, 'Revenda'),
    ]

    TIPO_CHOICES = [
        (0, 'Serviço'),
        (1, 'Produto'),
        (2, 'Peça'),
    ]

    ORIGEM_CHOICES = [
        (0, 'Outros'),
        (1, 'WhatsApp'),
        (2, 'Telegram'),
        (3, 'Facebook'),
        (4, 'Instagram'),
        (5, 'LinkedIn'),
        (6, 'Email'),
        (7, 'Telefone'),
        (8, 'Site Icetar'),
    ]

    TEMPERATURA_CHOICES = [
        (0, 'Baixa'),
        (1, 'Normal'),
        (2, 'Alta'),
    ]

    STATUS_APC_CHOICES = [
        (0, 'Não Cotado'),
        (1, 'Aguardando Retorno'),
    ]

    MOTIVO_RECUSE_CHOICES = [
        (0, 'Outros'),
        (1, 'Preço'),
        (2, 'Parcelamento'),
        (3, 'Projeto Cancelado'),
        (4, 'Projeto Adiado'),
        (5, 'Prazo de entrega'),
        (6, 'Qualidade'),
        (7, 'Opcionais'),
        (8, 'Demora para atendimento/fluxo'),
        (9, 'Falta de relacionamento'),
        (10, 'Tecnologia'),
        (11, 'Preferência de marca'),
    ]

    VENDEDOR_MOT_CHOICES = [
        (0, 'Sem Criterios'),
        (1, 'Vendedor responsável no Omie'),
        (2, 'Vendedor com faixa de CEP'),
        (3, 'Vendedor com histórico de atribuições'),
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    finalidade = models.IntegerField(choices=FINALIDADE_CHOICES, default=0)
    tipo = models.IntegerField(choices=TIPO_CHOICES, default=0)
    origem = models.IntegerField(choices=ORIGEM_CHOICES, default=0)
    temperatura = models.IntegerField(choices=TEMPERATURA_CHOICES, default=0)
    status_apc = models.IntegerField(choices=STATUS_APC_CHOICES, default=0)
    vendedor_mot = models.IntegerField(choices=VENDEDOR_MOT_CHOICES, default=0)

    cliente_final = models.CharField(max_length=255, blank=True, null=True)
    solicitacao = models.TextField()
    ticket = models.DecimalField(max_digits=10, decimal_places=2)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    orcamento_omie = models.IntegerField(blank=True, null=True)
    forma_pagamento = models.CharField(max_length=255, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    analisado_em = models.DateTimeField(blank=True, null=True)
    atendimento_em = models.DateTimeField(blank=True, null=True)
    apc_em = models.DateTimeField(blank=True, null=True)
    apv_em = models.DateTimeField(blank=True, null=True)
    orcamento_em = models.DateTimeField(blank=True, null=True)
    follow_up_em = models.DateTimeField(blank=True, null=True)
    finalizado_em = models.DateTimeField(blank=True, null=True)

    aceitou_proposta = models.BooleanField(null=True, blank=True)
    motivo_recusa = models.CharField(max_length=50, choices=MOTIVO_RECUSE_CHOICES, blank=True, null=True)


    class Meta:
        permissions = [
            ("pode_ver_fluxo", "Pode visualizar o fluxo de Leads"),
            ("pode_modificar_analise", "Pode modificar Leads no status Análise"),
            ("pode_modificar_atendimento", "Pode modificar Leads no status Atendimento"),
            ("pode_modificar_apc", "Pode modificar Leads no status APC"),
            ("pode_modificar_apv", "Pode modificar Leads no status APV"),
            ("pode_modificar_orcamento", "Pode modificar Leads no status Orçamento"),
            ("pode_modificar_followup", "Pode modificar Leads no status Follow-up"),
            ("pode_ver_todos_leads", "Pode ver todos os Leads"),
            ("pode_declinar_lead", "Pode declinar Leads"),
            ("pode_excluir_lead", "Pode excluir Leads"),
        ]


    def __str__(self):
        return f"{self.cliente.nome_fantasia} - {dict(self.STATUS_CHOICES).get(self.status, 'Desconhecido')}"
    
class LeadAcao(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='acoes')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    ACAO_CHOICES = [
        (0, 'Criação'),
        (1, 'Comentarios'),
        (2, 'Avanço de Status'),
        (3, 'Solicitação de Cliente'),
        (4, 'Informação de Analise'),
        (5, 'Troca de Responsável'),
        (6, 'Informação para o comprador'),
        (7, 'Produto adicionado ao lead'),
        (8, 'Produto removido do lead'),
        (9, 'Produto editado'),
        (10, 'Lead agurdando Retorno'),
        (11, 'Informação para vendas'),
        (12, 'Anexar Orçamento'),
        (13, 'Anexar Imagem'),
        (14, 'Anexar PDF'),
        (15, 'Anexar arquivo'),
        (16, 'Comentario de Follow-Up'),
        (17, 'Comentario Lead'),
        (18, 'Comentario de Finalização'),
        (19, 'Satus da Proposta'),
        (20, 'Proposta Finalizada'),
        (21, 'Retorno de Status'),
        (22, 'Declinar Lead'),
    ]
    
    acao = models.CharField(max_length=20, choices=ACAO_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)
    imagem = models.FileField(upload_to="leads_arquivos/", blank=True, null=True)
    pdf_omie = models.FileField(upload_to="leads_omie/", blank=True, null=True)
    

    def __str__(self):
        return f"Ação: {self.get_acao_display()} - {self.lead} - {self.data.strftime('%d/%m/%Y %H:%M')}"

class Produto(models.Model):
    codigo_produto = models.BigIntegerField(unique=True)  # Código único do produto
    codigo_produto_integracao = models.CharField(max_length=255, blank=True, null=True)
    descricao = models.CharField(max_length=500)
    unidade = models.CharField(max_length=10, blank=True, null=True)
    ncm = models.CharField(max_length=10, blank=True, null=True)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    codigo_familia = models.BigIntegerField(blank=True, null=True)
    tipo_item = models.CharField(max_length=5, blank=True, null=True)
    peso_liq = models.FloatField(default=0)
    peso_bruto = models.FloatField(default=0)
    altura = models.FloatField(default=0)
    largura = models.FloatField(default=0)
    profundidade = models.FloatField(default=0)
    marca = models.CharField(max_length=255, blank=True, null=True)
    modelo = models.CharField(max_length=255, blank=True, null=True)
    dias_garantia = models.IntegerField(default=0)
    dias_crossdocking = models.IntegerField(default=0)
    descricao_detalhada = models.TextField(blank=True, null=True)
    quantidade_estoque = models.IntegerField(default=0)
    estoque_minimo = models.IntegerField(default=0)
    
    # Data de criação e atualização
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(blank=True, null=True)
    data_validade = models.DateTimeField(blank=True, null=True)
    validade = models.IntegerField(default=0)
    prazo = models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.codigo_produto} - {self.descricao}"
    
class Caracteristica(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="caracteristicas")
    nome = models.CharField(max_length=255)
    conteudo = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.produto.codigo_produto} - {self.nome}: {self.conteudo}"
    
class LeadProduto(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="produtos")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="leads")
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    validade = models.IntegerField(default=0)
    prazo = models.IntegerField(default=0)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.lead} - {self.produto} ({self.quantidade}x)"

    class Meta:
        unique_together = ("lead", "produto")

class LeadAssignment(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    data_atribuicao = models.DateTimeField(auto_now_add=True)
