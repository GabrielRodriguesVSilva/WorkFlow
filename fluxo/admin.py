from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

# Inline para Caracteristicas dentro de Produto
class CaracteristicaInline(admin.TabularInline):  # Pode usar StackedInline também
    model = Caracteristica
    extra = 1  # Número de campos extras exibidos para adicionar novas características

# Configuração do Admin para Produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("codigo_produto", "descricao", "valor_unitario", "quantidade_estoque")
    search_fields = ("codigo_produto", "descricao")
    list_filter = ("marca", "tipo_item")
    inlines = [CaracteristicaInline]  # Adicionando as características dentro do Produto

# Criar um InlineAdmin para PerfilUsuario
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = "Perfil do Usuário"

# Estender o UserAdmin para incluir o Inline
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

# Remover o User padrão e registrar com o novo Admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registrando os modelos
admin.site.register(Cliente)
admin.site.register(Lead)
admin.site.register(PerfilUsuario)
admin.site.register(LeadAcao)
admin.site.register(Produto, ProdutoAdmin)
admin.site.register(LeadAssignment)

