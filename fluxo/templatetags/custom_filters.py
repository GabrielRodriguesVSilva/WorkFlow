from django import template
from ..api_omie import *

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])


@register.filter
def calcular_preco(produto):
    try:
        codigo_produto = produto.codigo_produto
        produto_omie = buscar_produto_omie_detalhes(codigo_produto)
        if not produto_omie:
            return 0
        else:
            tabiela = produto_omie.get('produto_servico_cadastro')[0].get('tabelas_preco')
            if tabiela:
                codigo_Tabela_preco = tabiela[0].get('nCodTabPreco')
                info_tabela = buscar_infos_tabela_omie(codigo_Tabela_preco)
                prosentagem = info_tabela.get('outrasInfo').get('nPercAcrescimo')
                prosentagem_abrev = (prosentagem / 100) + 1
                custo_unitario = produto.custo_unitario
                if custo_unitario == 0:
                    return 0
                else:
                    preco_calculado = float(custo_unitario) * prosentagem_abrev
                    return round(preco_calculado, 2)
            return 0
    except:
        return 0