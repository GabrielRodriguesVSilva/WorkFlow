from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import *
from .api_omie import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Q   
from datetime import timedelta
import uuid
import os
from django.contrib.auth.decorators import login_required, user_passes_test

def is_allowed_to_view_fluxo(user):
    return user.has_perm('fluxo.pode_ver_fluxo') or user.is_superuser

def is_allowed_to_view_todos_leads(user, lead_):
    # Verifica se o usuário tem permissão para ver todos os leads ou se é superusuário
    if user.has_perm('fluxo.pode_ver_todos_leads') or user.is_superuser:
        return True
    
    # Caso contrário, verifica se o usuário é responsável ou criador do lead específico
    if lead_:
        if lead_.status == 0 and lead_.criador == user:
            return True
        elif lead_.responsavel == user:
            return True
        else:
            return False

    return False

def is_allowed_to_view_apc(user):
    return user.has_perm('fluxo.pode_modificar_apc') or user.is_superuser

def is_allowed_to_view_apv(user):
    return user.has_perm('fluxo.pode_modificar_apv') or user.is_superuser

def is_allowed_to_view_usuarios(user):
    return user.has_perm('fluxo.gerencia_usuario') or user.is_superuser


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    
    return render(request, 'Login/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu com sucesso.")
    return redirect('login') 

@login_required
def home(request):
    return render(request, 'Main/home.html')

@login_required
@user_passes_test(is_allowed_to_view_usuarios, login_url='/')
def usuarios(request):
    users = User.objects.all()
    return render(request, 'Main/Usuarios/usuarios.html', {"users": users})

@login_required
@user_passes_test(is_allowed_to_view_usuarios, login_url='/')
def add_user(request):
    grupos = Group.objects.all()  # Lista de grupos disponíveis
    if request.method == 'POST':
        # Pega os dados do formulário
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        foto = request.FILES.get('foto')  # Pega a imagem enviada no formulário
        
        # Verifica se todos os campos foram preenchidos
        if username and first_name and last_name and email and password:
            # Cria o usuário
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            user.save()
            
            # Cria o perfil com a foto, se ela foi enviada
            if foto:
                perfil = PerfilUsuario.objects.create(usuario=user, foto=foto)
                perfil.save()
            
                    # Atualizar grupo do usuário
            grupo_id = request.POST.get('grupo')
            if grupo_id:
                novo_grupo = Group.objects.get(id=grupo_id)
                user.groups.clear()  # Remove todos os grupos anteriores
                user.groups.add(novo_grupo)  # Adiciona o novo grupo
            
            

            messages.success(request, "Usuário criado com sucesso!")
        return redirect('usuarios')  # Redireciona para a página de gerenciamento de usuários


    return render(request, 'Main/Usuarios/add_user.html', {"grupos": grupos})

@login_required
@user_passes_test(is_allowed_to_view_usuarios, login_url='/')
def edit_user(request, user_id):
    user_edit = User.objects.get(id=user_id)
    grupos = Group.objects.all()  # Lista de grupos disponíveis

    # Garantir que o perfil do usuário existe
    perfil_usuario, created = PerfilUsuario.objects.get_or_create(usuario=user_edit)

    if request.method == "POST":
        # Atualizar os campos básicos do usuário
        user_edit.username = request.POST.get('username')
        user_edit.first_name = request.POST.get('first_name')
        user_edit.last_name = request.POST.get('last_name')
        user_edit.email = request.POST.get('email')
        password = request.POST.get('password')

        # Atualizar CEPs no perfil do usuário
        if request.POST.get('cep_int') and request.POST.get('cep_fim'):
            perfil_usuario.cep_inicio = request.POST.get('cep_int')
            perfil_usuario.cep_fim = request.POST.get('cep_fim')
            perfil_usuario.save()

        # Atualizar a senha se fornecida
        if password:
            user_edit.set_password(password)

        # Atualizar foto de perfil
        foto = request.FILES.get('foto')
        if foto:
            perfil_usuario.foto = foto
            perfil_usuario.save()

        # Atualizar grupo do usuário
        grupo_id = request.POST.get('grupo')
        if grupo_id:
            novo_grupo = Group.objects.get(id=grupo_id)
            user_edit.groups.clear()  # Remove todos os grupos anteriores
            user_edit.groups.add(novo_grupo)  # Adiciona o novo grupo

        user_edit.save()
        messages.success(request, "Usuário atualizado com sucesso!")
        return redirect('edit_user', user_id=user_edit.id)

    return render(request, 'Main/Usuarios/edit_user.html', {
        "user_edit": user_edit,
        "grupos": grupos,
        "grupo_atual": user_edit.groups.first()  # Obtém o primeiro grupo do usuário
    })
    

@login_required
@user_passes_test(is_allowed_to_view_fluxo, login_url='/')
def fluxo(request):
    # Verifica se o usuário tem permissão para ver todos os leads
    if request.user.has_perm('fluxo.pode_ver_todos_leads'):
        # Usuário pode ver todos os leads
        leads = Lead.objects.all()
    else:
        # Caso contrário, mostra apenas os leads que o usuário é responsável ou criou
        leads = Lead.objects.filter(
            Q(status=0, criador=request.user) | Q(responsavel=request.user)
        )

    # Organize os leads por status
    leads_por_status = {status[0]: [] for status in Lead.STATUS_CHOICES}

    for lead in leads:
        leads_por_status[lead.status].append(lead)

    context = {
        'leads_por_status': leads_por_status,
        'status_choices': dict(Lead.STATUS_CHOICES),
    }

    return render(request, 'Main/Fluxo/fluxo.html', context)


@login_required
def buscar_clientes(request):
    cnpj = request.GET.get('cliente')

    if not cnpj:
        return render(request, 'Main/Fluxo/Includes/msg_cliente_nao_encontrado.html', {"messages": "CNPJ não informado!"})
    user = request.user
    cliente_omie = add_cliente_da_omie(cnpj)
    if not cliente_omie:
        return render(request, 'Main/Fluxo/Includes/msg_cliente_nao_encontrado.html', {"messages": "Cliente não encontrado na Omie!"})

    cliente = cliente_omie  # Cliente vindo da Omie

    # Contexto incluindo os choices do modelo Lead
    context = {
        "cliente": cliente,
        "finalidade_choices": Lead.FINALIDADE_CHOICES,
        "tipo_choices": Lead.TIPO_CHOICES,
        "origem_choices": Lead.ORIGEM_CHOICES,
        "temperatura_choices": Lead.TEMPERATURA_CHOICES,
    }

    return render(request, 'Main/Fluxo/Includes/form_add_lead.html', context)

@login_required
def add_lead(request, cliente_id):
    cliente = Cliente.objects.get(id=cliente_id)

    if cliente:
        finalidade = request.POST.get('finalidade')
        tipo = request.POST.get('tipo')
        origem = request.POST.get('origem')
        temperatura = request.POST.get('temperatura')
        ticket = request.POST.get('ticket')
        cliente_final = request.POST.get('cliente_final')
        solicitacao = request.POST.get('solicitacao')
        criador = request.user


        vendedor, origem_vendedor = vendedor_indicado(cliente)

        
        # Criando o lead no banco de dados
        lead = Lead.objects.create(
            cliente=cliente,
            finalidade=finalidade,
            criador=criador,
            tipo=tipo,
            origem=origem,
            temperatura=temperatura,
            ticket=ticket,
            cliente_final=cliente_final,
            solicitacao=solicitacao,
            valor=0,
        )

        if origem_vendedor == 3:
            LeadAssignment.objects.create(lead=lead, vendedor=vendedor)
            lead.user_indicado = vendedor
            lead.vendedor_mot = origem_vendedor
            lead.save()


        #Criar Ação de Criação	
        LeadAcao.objects.create(
            lead=lead,
            usuario=criador,
            acao=0,
            descricao=f"Lead criado por {criador.username}",
        )

        #Adcionar Solicitação do Cliente
        LeadAcao.objects.create(
            lead=lead,
            usuario=criador,
            acao=3,
            descricao=solicitacao,
        )

        messages.success(request, "Lead adicionado com sucesso!")
        return redirect('fluxo')
    else:
        messages.error(request, "Cliente não encontrado na Omie!")


    return redirect('fluxo')


@login_required
def lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)

    if not lead_:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')
    

    if not is_allowed_to_view_todos_leads(request.user, lead_):
        messages.error(request, "Você não tem permissão para acessar este Lead!")
        return redirect('fluxo') 

    try:
        vendedores = User.objects.filter(groups__name__icontains="Vendas")
    except:
        vendedores = User.objects.all()

    
    # Atualizar o Lead com os dados do Omie
    if lead_.status > 4:
        if lead_.orcamento_omie:
            orcamento_omie = buscar_infos_do_orcamento(lead_.orcamento_omie)
            try:
                if orcamento_omie:
                    total = orcamento_omie.get('pedido_venda_produto')
                    if total:
                        pedido = total.get('total_pedido')
                        custo = pedido.get('valor_total_pedido')
                        lead_.valor = float(custo)
                        lead_.save()
            except:
                pass



    produtos_lead = LeadProduto.objects.filter(lead=lead_)
    context = {
        "lead": lead_,
        "vendedores": vendedores,
        "produtos_lead": produtos_lead,
        "STATUS_CHOICES": Lead.STATUS_CHOICES,
        "ACAO_CHOICES": LeadAcao.ACAO_CHOICES,
    }
    return render(request, 'Main/Fluxo/Lead/lead.html', context)

@login_required
def edit_lead_analise(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        responsavel_id = request.POST.get('vendedor')
        responsavel = User.objects.get(id=responsavel_id)
        if not responsavel:
            messages.error(request, "Responsável não encontrado!")
            return redirect('fluxo')
        lead_.responsavel = responsavel
        lead_.status = 1
        lead_.analisado_em = timezone.now()
        lead_.save()

        analise = request.POST.get('analise')

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=4,
            descricao=analise,
        )

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=5,
            descricao=f"O {request.user.username} indicou o responsável para o Lead {responsavel.username}",
        )

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=2,
            descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
        )



        messages.success(request, "Análise enviada com sucesso!")
        return redirect('lead', lead_id)

    else:
        messages.error(request, "Cliente não encontrado na Omie!")


    return redirect('fluxo')

@login_required
def buscar_produto(request, lead_id):
    codigo_produto = request.GET.get('codigo_produto')
    qnt = request.GET.get('qnt_produto')
    try:
        qnt = int(qnt)
        if qnt <= 0:
            messages.error(request, "A quantidade deve ser maior que zero.")
            return redirect('lead', lead_id)
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return render(request, 'Main/Includes/htmx_messages.html')

    # Busca ou cria o produto no banco
    produto_data = add_produto_da_omie(codigo_produto)
    if not produto_data:
        messages.error(request, "Produto não encontrado na Omie!")
        return render(request, 'Main/Includes/htmx_messages.html')

    # Busca o lead
    lead = Lead.objects.get(id=lead_id)

    # Associa o produto ao lead na tabela intermediária
    lead_produto, created = LeadProduto.objects.get_or_create(
        lead=lead,
        produto=produto_data,
        defaults={
            "quantidade": qnt, 
            "custo_unitario": produto_data.custo_unitario,
            "validade": produto_data.validade,
            "prazo": produto_data.prazo,
            }
    )

    
    LeadAcao.objects.create(
        lead=lead,
        usuario=request.user,
        acao=7,
        descricao=f"Produto {produto_data.descricao} adicionado ao lead",
    )

    if not created:
        lead_produto.quantidade += qnt  # Se já existir, soma a quantidade
        lead_produto.save()

    messages.success(request, f"Produto {produto_data.descricao} adicionado ao lead.")
    return render(request, 'Main/Fluxo/Lead/Includes/produto_lead.html', {"lead_produto": lead_produto})
    
@login_required
def deletar_produto_lead(request, produto_lead_id):
    produto_lead = LeadProduto.objects.get(id=produto_lead_id)
    produto_lead.delete()

    LeadAcao.objects.create(
        lead=produto_lead.lead,
        usuario=request.user,
        acao=8,
        descricao=f"Produto {produto_lead.produto.descricao} removido do lead",
    )
    
    messages.success(request, "Produto removido com sucesso!")

    return HttpResponse("") 

@login_required
def edit_lead_atendimento(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        orcamento_omie = request.POST.get('orcamento_omie')
        if orcamento_omie:
            orc_omie = buscar_infos_do_orcamento(orcamento_omie)
            print(orc_omie)
            if not orc_omie:
                messages.error(request, "Orçamento do Omie Não Encontrado!")
                return redirect('lead', lead_id)


        forma_pagamento = request.POST.get('forma_pagamento')
        atendimento = request.POST.get('atendimento')

        if not orcamento_omie:
            messages.error(request, "O número do Orçamento do Omie é obrigatório.")
            return redirect('lead', lead_id)

        if not forma_pagamento:
            messages.error(request, "A forma de pagamento é obrigatório.")
            return redirect('lead', lead_id)

        lead_.orcamento_omie = orcamento_omie
        lead_.forma_pagamento = forma_pagamento
        lead_.status = 2
        lead_.atendimento_em = timezone.now()
        lead_.save()

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=6,
            descricao=atendimento,
        )

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=2,
            descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
        )

        messages.success(request, "Atendimento atualizado com sucesso!")
        return redirect('lead', lead_id)

@login_required
@user_passes_test(is_allowed_to_view_apc, login_url='/')
def apc_view(request):
    leads_em_apc = Lead.objects.filter(status=2) \
        .annotate(qnt_itens=Count('produtos')) \
        .order_by('atendimento_em') 

    context = {
        "leads_em_apc": leads_em_apc,
    }
    return render(request, 'Main/Compras/APC/apc.html', context)

@login_required
@user_passes_test(is_allowed_to_view_apc, login_url='/')
def apc_lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)

    if lead_:
        produtos_lead = LeadProduto.objects.filter(lead=lead_)
        ultimo_comentario = LeadAcao.objects.filter(acao=6, lead=lead_).order_by('-data').first()
        itens_anexos = LeadAcao.objects.filter(
            Q(acao=13) | Q(acao=14) | Q(acao=15),
            lead=lead_
        ).order_by('-data')
        context = {
            "lead": lead_,
            "produtos_lead": produtos_lead,
            "STATUS_CHOICES": Lead.STATUS_CHOICES,
            "ultimo_comentario": ultimo_comentario,
            "itens_anexos": itens_anexos,
        }
        return render(request, 'Main/Compras/APC/apc_lead.html', context)
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('apc')

@login_required
def buscar_produto_apc(request, lead_id):
    codigo_produto = request.GET.get('codigo_produto')
    qnt = request.GET.get('qnt_produto')

    try:
        qnt = int(qnt)
        if qnt <= 0:
            messages.error(request, "A quantidade deve ser maior que zero.")
            return render(request, 'Main/Includes/htmx_messages.html')
    except ValueError:
        messages.error(request, "Quantidade inválida.")
        return render(request, 'Main/Includes/htmx_messages.html')

    produto_data = add_produto_da_omie(codigo_produto)

    if not produto_data:
        messages.error(request, "Produto inválido ou vazio.")
        
        return render(request, 'Main/ncludes/htmx_messages.html')

    lead = Lead.objects.get(id=lead_id)
    lead_produto, created = LeadProduto.objects.get_or_create(
        lead=lead,
        produto=produto_data,
        defaults={"quantidade": qnt, "custo_unitario": produto_data.custo_unitario, "validade": produto_data.validade, "prazo": produto_data.prazo}
    )

    LeadAcao.objects.create(
        lead=lead,
        usuario=request.user,
        acao=7,
        descricao=f"Produto {produto_data.descricao} adicionado ao lead",
    )

    if not created:
        lead_produto.quantidade += qnt
        lead_produto.save()

    messages.success(request, f"Produto {produto_data.descricao} adicionado ao lead.")
    return render(request, 'Main/Compras/APC/produto_lead.html', {"produto_lead": lead_produto})

@login_required
def editar_produto_lead_apc(request, produto_lead_id):
    produto_lead = LeadProduto.objects.get(id=produto_lead_id)
    if not produto_lead:
        messages.error(request, "Produto não encontrado!")
        return redirect('apc_lead', produto_lead.lead.id)
    
    qnt = int(request.POST.get("qnt", produto_lead.quantidade) or produto_lead.produto.quantidade)
    prazo = int(request.POST.get("prazo", produto_lead.prazo) or produto_lead.produto.prazo)
    val = int(request.POST.get("val", produto_lead.validade) or produto_lead.produto.validade)
    custo = float((request.POST.get("custo", produto_lead.custo_unitario) or str(produto_lead.produto.custo_unitario)).replace(",", "."))

    data_proxima_validade = timezone.now() + timedelta(days=val)
    
    # Editando produtos do lead
    produto_lead.quantidade = qnt
    produto_lead.prazo = prazo
    produto_lead.validade = val
    produto_lead.custo_unitario = custo
    produto_lead.data_validade = data_proxima_validade
    produto_lead.save()

    # Editando produto
    produto_lead.produto.prazo = prazo
    produto_lead.produto.validade = val
    produto_lead.produto.custo_unitario = custo
    produto_lead.produto.data_validade = data_proxima_validade
    produto_lead.produto.data_modificacao = timezone.now()
    produto_lead.produto.save()
    
    LeadAcao.objects.create(
        lead=produto_lead.lead,
        usuario=request.user,
        acao=9,
        descricao=f"Produto {produto_lead.produto.descricao} editado",
    )

    messages.success(request, f"Produto {produto_lead.produto.descricao} editado.")

    # Renderizar apenas a linha atualizada
    return render(request, 'Main/Compras/APC/produto_lead.html', {"produto_lead": produto_lead})

@login_required
def alternar_status_apc(request, lead_id):
    lead = Lead.objects.get(id=lead_id)

    # Alterna o status entre 0 e 1
    lead.status_apc = 1 if lead.status_apc == 0 else 0
    lead.save()

    LeadAcao.objects.create(
        lead=lead,
        usuario=request.user,
        acao=10,
        descricao=f"Lead agurando Retorno dos fornecedores",
    )

    # Renderiza o novo HTML do badge
    return render(request, "Main/Compras/APC/status_badge.html", {"lead": lead})

@login_required
def edit_lead_apc(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        apc_analise = request.POST.get('apc_analise')

        lead_.status = 3
        lead_.apc_em = timezone.now()
        lead_.save()
        if apc_analise:
            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=11,
                descricao=apc_analise,
            )

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=2,
            descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
        )

        messages.success(request, "Lead enviado para APV")
        return redirect('apc')
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('apc')
    
@login_required
@user_passes_test(is_allowed_to_view_apv, login_url='/')
def apv_view(request):
    leads_em_apv = Lead.objects.filter(status=3).annotate(qnt_itens=Count('produtos')).order_by('apc_em')
    context = {"leads_em_apv": leads_em_apv,}
    return render(request, 'Main/Compras/APV/apv.html', context)

@login_required
@user_passes_test(is_allowed_to_view_apv, login_url='/')
def apv_lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        produtos_lead = LeadProduto.objects.filter(lead=lead_)
        context = {
            "lead": lead_,
            "produtos_lead": produtos_lead,
            "STATUS_CHOICES": Lead.STATUS_CHOICES,
        }
        return render(request, 'Main/Compras/APV/apv_lead.html', context)
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('apv')

@login_required
def editar_produto_lead_apv(request, produto_lead_id):
    produto_lead = LeadProduto.objects.get(id=produto_lead_id)

    if request.method == "POST":
        valor_unitario_str = request.POST.get("valor_unitario", "").strip()

        if valor_unitario_str:  # Evita erro se o campo estiver vazio
            try:
                valor_unitario = float(valor_unitario_str.replace(",", "."))
                produto_lead.valor_unitario = valor_unitario
                produto_lead.save()
                produto_lead.produto.save()  # Se necessário
            except ValueError:
                return JsonResponse({"error": "Valor inválido"}, status=400)

        return JsonResponse({"message": "Recebido com sucesso", "valor_unitario": valor_unitario_str}, status=200)


    return JsonResponse({"error": "Método não permitido"}, status=405)

@login_required
def edit_lead_apv(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        apc_analise = request.POST.get('apv_analise')

        lead_.status = 4
        lead_.apv_em = timezone.now()
        lead_.save()
        if apc_analise:
            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=11,
                descricao=apc_analise,
            )

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=2,
            descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
        )

        messages.success(request, "Lead enviado para Orçamento")
        return redirect('apv')
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('apv')
    
@login_required
def edit_lead_orcamento(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        pdf_omie = request.FILES.get("pdf_omie")
        lead_.status = 5
        lead_.orcamento_em = timezone.now()
        lead_.save()

        if pdf_omie:
            # Gerar um nome de arquivo único
            ext = os.path.splitext(pdf_omie.name)[1]  # Pega a extensão do arquivo
            unique_filename = f"{uuid.uuid4()}{ext}"

            # Salva o arquivo no campo `pdf_omie` com o novo nome
            lead_acao = LeadAcao.objects.create(
                usuario=request.user,
                lead=lead_,
                pdf_omie=pdf_omie,
                acao=12,
                descricao=f"O {request.user.username} anexou o orçamento no Lead {lead_.cliente.nome_fantasia}",
            )
            lead_acao.pdf_omie.save(f"leads_omie/{unique_filename}", pdf_omie)  # ✅ Salva corretamente
            lead_acao.save()

            # Registra a alteração de status
            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=2,
                descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
            )

            messages.success(request, "Orçametno enviado com sucesso!")
            return redirect('lead', lead_id)
        else:
            messages.error(request, "Nenhum arquivo selecionado!")
            return redirect('lead', lead_id)
    else:
        messages.error(request, "Lead não encontrado!")

        return redirect('fluxo')

@login_required
def comentario_lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        descricao_cmt = request.POST.get('descricao_cmt')
        arquivo = request.FILES.get("arquivo")
        if arquivo:
            ext = os.path.splitext(arquivo.name)[1].lower()

            ext = os.path.splitext(arquivo.name)[1].lower()  # Obtém a extensão do arquivo

            if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                acao_tipo = "13"
            elif ext == ".pdf":
                acao_tipo = "14"
            else:
                acao_tipo = "15"
        else:
            if lead_.status == 5:
                acao_tipo = "16"
            else:
                acao_tipo = "1"

        LeadAcao.objects.create(
            usuario=request.user,
            lead=lead_,
            acao=acao_tipo,
            descricao=descricao_cmt,
            imagem=arquivo,
        )
        referer = request.META.get("HTTP_REFERER", "Página desconhecida")

        if "/apc/lead/" in referer:
            messages.success(request, "Comentário enviado com sucesso!")
            return redirect('apc_lead', lead_id)
        elif "/apv/lead/" in referer:
            messages.success(request, "Comentário enviado com sucesso!")
            return redirect('apv_lead', lead_id)
        elif "/lead/" in referer:
            messages.success(request, "Comentário enviado com sucesso!")
            return redirect('lead', lead_id)
        else:
            messages.success(request, "Comentário enviado com sucesso!")
            return redirect('home')
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')

@login_required
def get_finalizar_lead(request, id_status_proposta, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    id_status_proposta = int(id_status_proposta)
    if lead_:
        if id_status_proposta == 0: # Não aceitou a proposta
            context = {
                "lead": lead_,
                "MOTIVO_RECUSE_CHOICES": Lead.MOTIVO_RECUSE_CHOICES,
            }
            return render(request, 'Main/Fluxo/Includes/form_declinar_lead.html', context)
        elif id_status_proposta == 1: # Aceitou a proposta
            context = {
                "lead": lead_,
            }
            return render(request, 'Main/Fluxo/Includes/form_aprovado_lead.html', context)
        else:
            messages.error(request, "Status inválido!")
            return redirect('lead', lead_id)
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')
    
@login_required
def edit_lead_finalizado(request, id_status_proposta, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    id_status_proposta = int(id_status_proposta)
    if lead_:
        if id_status_proposta == 0: # Não aceitou a proposta
            motivo_recusa = request.POST.get('motivo_recusa')
            comentario = request.POST.get('comentario')
            # Editar o status do Lead
            lead_.status = 6
            lead_.aceitou_proposta = False
            lead_.motivo_recusa = motivo_recusa
            lead_.save()

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=18,
                descricao=comentario,
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=2,
                descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=19,
                descricao=f"O Lead foi Reprovado",
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=20,
                descricao=f"Lead Finalizado",
            )

            messages.success(request, "Lead finalizado com sucesso!")
            return redirect('lead', lead_id)
        
        elif id_status_proposta == 1: # Aceitou a proposta
            comentario = request.POST.get('comentario')
            # Editar o status do Lead
            lead_.status = 6
            lead_.aceitou_proposta = True
            lead_.save()

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=18,
                descricao=comentario,
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=2,
                descricao=f"O Status do Lead foi alterado para {lead_.get_status_display()}",
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=19,
                descricao=f"O Lead foi Aprovado",
            )

            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=20,
                descricao=f"Lead Finalizado",
            )

            messages.success(request, "Lead finalizado com sucesso!")
            return redirect('lead', lead_id)
        else:
            messages.error(request, "Status inválido!")
            return redirect('lead', lead_id)
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')

@login_required
def get_form_retorno_status(request, lead_id, status_id):
    lead_ = Lead.objects.get(id=lead_id)
    
    # Criar um dicionário de status para fácil acesso
    status_dict = dict(Lead.STATUS_CHOICES)
    
    # Pega o nome do status correspondente ao status_id
    status_label = status_dict.get(int(status_id), "Status desconhecido")

    if not lead_:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')
    
    if request.method == "POST":
        motivo_retorno = request.POST.get('motivo_retorno')
        referer = request.META.get("HTTP_REFERER", "Página desconhecida")
        # Editar o status do Lead
        lead_.status = int(status_id)
        lead_.save()

        LeadAcao.objects.create(
            lead=lead_,
            usuario=request.user,
            acao=21,
            descricao=motivo_retorno,
        )
        messages.success(request, f"O status do Lead foi alterado para {status_label}")
        if "/apc/lead/" in referer:
            return redirect('apc')
        elif "/apv/lead/" in referer:
            return redirect('apv')
        elif "/lead/" in referer:
            return redirect('lead', lead_id)
        
    return render(request, 'Main/Fluxo/Includes/from_retorno_lead.html', {"lead": lead_, "status_id": status_id, "status_label": status_label})

@login_required
def deletar_lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        if request.user.has_perm('fluxo.pode_excluir_lead'):
            lead_.delete()
            messages.success(request, "Lead deletado com sucesso!")
            return redirect('fluxo')
        else:
            messages.error(request, "Você não tem permissão para deletar o Lead!")
            return redirect('fluxo')
    else:
        messages.error(request, "Lead não encontrado!")
        return redirect('fluxo')

@login_required
def declinar_lead(request, lead_id):
    lead_ = Lead.objects.get(id=lead_id)
    if lead_:
        if request.user.has_perm('fluxo.pode_modificar_declinar'):
            lead_.status = 6
            lead_.save()
            LeadAcao.objects.create(
                lead=lead_,
                usuario=request.user,
                acao=22,
                descricao=f"O Lead foi Declinado",
            )
            messages.success(request, "Lead declinado com sucesso!")
            return redirect('fluxo')
        else:
            messages.error(request, "Você não tem permissão para deletar o Lead!")
            return redirect('fluxo')


