import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
from django.db import IntegrityError
import traceback


# Suas credenciais da API Omie
OMIE_URL_CLIENTE = "https://app.omie.com.br/api/v1/geral/clientes/"
OMIE_URL_PRODUTO = "https://app.omie.com.br/api/v1/geral/produtos/"
OMIE_APP_KEY = "649289350710"
OMIE_APP_SECRET = "ba03132fbeafde33d7a2f44ed2a7800d"

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

def add_cliente_da_omie(cnpj):
    """Busca o cliente na API do Omie e insere no banco de dados se não existir"""
    id_omie = buscar_por_cnpj_omie(cnpj)  # Busca o código do cliente na Omie
    if not id_omie:
        return False  # Retorna False se não encontrar o cliente na Omie

    omie_data = buscar_cliente_omie(id_omie)  # Busca os detalhes do cliente
    if not omie_data:
        return False  # Retorna False se não encontrar os detalhes do cliente

    try:
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
            }
        )
        return cliente

    except IntegrityError:
        return False

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
