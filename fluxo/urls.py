from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('usuarios/', usuarios, name='usuarios'),
    path('add_user/', add_user, name='add_user'),
    path('user/<int:user_id>/', edit_user, name='edit_user'),
    path('fluxo/', fluxo, name='fluxo'),
    path("buscar-clientes/", buscar_clientes, name="buscar_clientes"),
    path("add_lead/<int:cliente_id>/", add_lead, name="add_lead"),
    path("lead/<int:lead_id>/", lead, name="lead"),
    path("edit_lead_analise/<int:lead_id>/", edit_lead_analise, name="edit_lead_analise"),
    path("buscar-produto/<int:lead_id>/", buscar_produto, name="buscar_produto"),
    path('deletar-produto/<int:produto_lead_id>/', deletar_produto_lead, name='deletar_produto_lead'),
    path('edit_lead_atendimento/<int:lead_id>/', edit_lead_atendimento, name='edit_lead_atendimento'),
    path('apc/', apc_view, name='apc'),
    path('apc/lead/<int:lead_id>/', apc_lead, name='apc_lead'),
    path('apc/buscar-produto/<int:lead_id>/', buscar_produto_apc, name='buscar_produto_apc'),
    path('apc/ediatr-produto/<int:produto_lead_id>/', editar_produto_lead_apc, name='editar_produto_lead_apc'),
    path("lead/<int:lead_id>/alternar-status/", alternar_status_apc, name="alternar_status_apc"),
    path("edit_lead_apc/<int:lead_id>/", edit_lead_apc, name="edit_lead_apc"),
    path('apv/', apv_view, name='apv'),
    path('apv/ediatr-produto/<int:produto_lead_id>/', editar_produto_lead_apv, name='editar_produto_lead_apv'),
    path('apv/lead/<int:lead_id>/', apv_lead, name='apv_lead'),
    path("edit_lead_apv/<int:lead_id>/", edit_lead_apv, name="edit_lead_apv"),
    path('edit_lead_orcamento/<int:lead_id>/', edit_lead_orcamento, name='edit_lead_orcamento'),
    path('comentario-lead/<int:lead_id>/', comentario_lead, name='comentario_lead'),
    path('finalizar-lead/<int:id_status_proposta>/<int:lead_id>/', get_finalizar_lead, name='get_finalizar_lead'),
    path('finalizar/<int:id_status_proposta>/<int:lead_id>/', edit_lead_finalizado, name='edit_lead_finalizado'),
    path('retorno-status/<int:lead_id>/<int:status_id>/', get_form_retorno_status, name='get_form_retorno_status'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
