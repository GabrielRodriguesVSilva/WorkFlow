import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Count, Min
from django.db import IntegrityError
from django.db.models import Max
import traceback
from django.contrib.auth.models import User


# Suas credenciais da API Omie
OMIE_URL_CLIENTE = "https://app.omie.com.br/api/v1/geral/clientes/"
OMIE_URL_PRODUTO = "https://app.omie.com.br/api/v1/geral/produtos/"
OMIE_URL_CUSTO = "https://app.omie.com.br/api/v1/produtos/tabelaprecos/"
OMIE_URL_PEDIDO = "https://app.omie.com.br/api/v1/produtos/pedido/"
OMIE_URL_VENDEDOR = "https://app.omie.com.br/api/v1/geral/vendedores/"

OMIE_APP_KEY = "649289350710"
OMIE_APP_SECRET = "11329593b619e2bfff80f2beabb845df"

def buscar_por_cnpj_omie(cnpj):
    """Busca o priemio da lista cliente pelo CNPJ na API do Omie"""
    payload = json.dumps({
        "call": "ListarClientesResumido",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [
                    {
                        "pagina": 1,
                        "registros_por_pagina": 1,
                        "apenas_importado_api": "N",
                        "ClientesFiltro": {
                            "cnpj_cpf": cnpj
                        }
                    }
                ]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_CLIENTE, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        id_omie = omie_data.get('clientes_cadastro_resumido')[0].get('codigo_cliente')
        return id_omie
    return None

def buscar_cliente_omie(id_omie):
    """Busca o cliente na API do Omie pelo ID"""
    payload = json.dumps({
        "call": "ConsultarCliente",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{"codigo_cliente_omie": id_omie}]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_CLIENTE, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None

def buscar_vendedor_omie(codigo_vendedor):
    """Busca o vendedor na API do Omie pelo Código"""
    payload = json.dumps({
        "call": "ConsultarVendedor",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{"codigo": codigo_vendedor}]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_VENDEDOR, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None

def add_cliente_da_omie(cnpj):
    """Busca o cliente na API do Omie e insere no banco de dados se não existir"""
    id_omie = buscar_por_cnpj_omie(cnpj)  # Busca o código do cliente na Omie
    if not id_omie:
        return False  # Retorna False se não encontrar o cliente na Omie



    omie_data = buscar_cliente_omie(id_omie)  # Busca os detalhes do cliente
    if not omie_data:
        return False  # Retorna False se não encontrar os detalhes do cliente
    # try:
    cliente, created = Cliente.objects.update_or_create(
        id_omie=omie_data.get("codigo_cliente_omie"),
        defaults={
            "empresa": omie_data.get("razao_social", ""),
            "nome_fantasia": omie_data.get("nome_fantasia", ""),
            "documento": omie_data.get("cnpj_cpf", ""),
            "tipo": "PJ" if omie_data.get("pessoa_fisica") == "N" else "PF",
            "nome_contato": omie_data.get("contato", ""),
            "email": omie_data.get("email", ""),
            "telefone": f"{omie_data.get('telefone1_ddd', '')} {omie_data.get('telefone1_numero', '')}".strip(),
            "cep": omie_data.get("cep", ""),
            "estado": omie_data.get("estado", ""),
            "cidade": omie_data.get("cidade", ""),
            "bairro": omie_data.get("bairro", ""),
            "logradouro": omie_data.get("endereco", ""),
            "instituicao": omie_data.get("inscricao_estadual", ""),
            "contribuinte": omie_data.get("contribuinte") == "S",
            "codigo_vendedor": omie_data.get('recomendacoes').get('codigo_vendedor', 0),
        }
    )

    print("CLIENTE", cliente)

    return cliente

    # except IntegrityError:
    #     return False

def vendedor_indicado(cliente):
    """Busca o vendedor pelo código, faixa de CEP ou round-robin com histórico."""
    codigo_vendedor = cliente.codigo_vendedor
    # 1. Busca pelo código do vendedor
    if codigo_vendedor:
        user_vendedor = PerfilUsuario.objects.filter(codigo_vendedor=codigo_vendedor).first()
        if user_vendedor:
            return user_vendedor.usuario, 1
        else:
            vendedor_omie = buscar_vendedor_omie(codigo_vendedor)
            if vendedor_omie:
                email = vendedor_omie.get('email', '')
                if email:
                    user_vendedor = User.objects.filter(email=email).first()
                    if user_vendedor:
                        perfil_usuario, _ = PerfilUsuario.objects.get_or_create(usuario=user_vendedor)
                        perfil_usuario.codigo_vendedor = codigo_vendedor
                        perfil_usuario.save()
                        return user_vendedor, 1

    # 2. Busca por faixa de CEP
    cep_cliente = int(str(cliente.cep)[:5])
    vendedor_cep = PerfilUsuario.objects.filter(
        usuario__groups__name__icontains="Vendas",
        cep_inicio__lte=cep_cliente,
        cep_fim__gte=cep_cliente,
        ativo=True
    ).first()

    if vendedor_cep:
        return vendedor_cep.usuario, 2

    # 3. Busca pelo round-robin com histórico
    vendedores = PerfilUsuario.objects.filter(
        usuario__groups__name__icontains="Vendas",
        ativo=True
    ).annotate(
        total_leads=Count('usuario__leadassignment')
    ).order_by('total_leads', 'usuario__leadassignment__data_atribuicao')

    if vendedores.exists():
        return vendedores.first().usuario, 3


    # 4. O Laercio
    vendedor_laercio = User.objects.filter(first_name__icontains="Laercio").first()
    return vendedor_laercio, 0

def buscar_produto_omie(codigo_produto):
    """Busca o produto na API do Omie pelo Código"""
    payload = json.dumps({
        "call": "ConsultarProduto",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{"codigo_produto": 0, "codigo_produto_integracao": "", "codigo": codigo_produto}]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_PRODUTO, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None

def add_produto_da_omie(codigo_produto):
    """Busca o produto na API do Omie e insere no banco de dados se não existir"""
    produto_omie = buscar_produto_omie(codigo_produto)  # Busca o produto na Omie
    if not produto_omie:
        return False

    try:
        # Criar ou atualizar o produto
        produto, created = Produto.objects.update_or_create(
            codigo_produto=produto_omie.get("codigo"),
            defaults={
                "codigo_produto_integracao": produto_omie.get("codigo_produto", ""),
                "descricao": produto_omie.get("descricao", ""),
                "unidade": produto_omie.get("unidade", ""),
                "ncm": produto_omie.get("ncm", ""),
                "codigo_familia": produto_omie.get("codigo_familia", ""),
                "tipo_item": produto_omie.get("tipoItem", ""),
                "peso_liq": produto_omie.get("peso_liq", 0),
                "peso_bruto": produto_omie.get("peso_bruto", 0),
                "altura": produto_omie.get("altura", 0),
                "largura": produto_omie.get("largura", 0),
                "profundidade": produto_omie.get("profundidade", 0),
                "marca": produto_omie.get("marca", ""),
                "modelo": produto_omie.get("modelo", ""),
                "dias_garantia": produto_omie.get("dias_garantia", 0),
                "dias_crossdocking": produto_omie.get("dias_crossdocking", 0),
                "descricao_detalhada": produto_omie.get("descr_detalhada", ""),
                "quantidade_estoque": produto_omie.get("quantidade_estoque", 0),
                "estoque_minimo": produto_omie.get("estoque_minimo", 0),
            }
        )

        # Atualizar as características
        caracteristicas = produto_omie.get("caracteristicas", [])
        if caracteristicas:
            for caract in caracteristicas:
                Caracteristica.objects.update_or_create(
                    produto=produto,
                    nome=caract.get("cNomeCaract", ""),
                    defaults={"conteudo": caract.get("cConteudo", "")}
                )

        return produto

    except Exception as e:
        print("Detalhes do erro:", str(e))
        return False

def buscar_produto_omie_detalhes(codigo_produto):
    """Busca o produto na API do Omie pelo Código"""
    payload = json.dumps({
        "call": "ListarProdutos",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [            {
                "pagina": 1,
                "registros_por_pagina": 50,
                "apenas_importado_api": "N",
                "filtrar_apenas_omiepdv": "N",
                "exibir_tabelas_preco": "S",
                "produtosPorCodigo": {
                    "codigo": str(codigo_produto)
                }
            }]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_PRODUTO, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None

def buscar_infos_tabela_omie(codigo_Tabela_preco):
    """Busca o produto na API do Omie pelo Código"""
    payload = json.dumps({
        "call": "ConsultarTabelaPreco",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [
                {
                    "nCodTabPreco": codigo_Tabela_preco,
                    "cCodIntTabPreco": ""
                }
        ]
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_CUSTO, headers=headers, data=payload)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None

def buscar_infos_do_orcamento(orcamento_id):
    """Busca os detalhes do orçamento pelo ID"""
    payload = json.dumps({
        "call": "ConsultarPedido",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{"numero_pedido": int(orcamento_id)}]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(OMIE_URL_PEDIDO, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code == 200:
        omie_data = response.json()
        return omie_data
    return None


