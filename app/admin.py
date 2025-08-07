# denuncia/admin.py

from django.contrib import admin
from .models import CidadeDenuncia, Denuncia, DenunciaDetalhada, Mensagem

@admin.register(CidadeDenuncia)
class CidadeDenunciaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cep', 'estado', 'ativo']
    list_filter = ['ativo', 'estado']


@admin.action(description="Aprovar denúncias selecionadas")
def aprovar_denuncias(modeladmin, request, queryset):
    updated = queryset.update(ativo=True)
    modeladmin.message_user(request, f"{updated} denúncia(s) foram aprovadas com sucesso.")


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ['nome_visivel', 'endereco', 'cidade', 'ativo', 'situacao', 'data_registro']
    list_filter = ['ativo', 'situacao', 'cidade']
    search_fields = ['nome_denunciante', 'email', 'endereco']
    readonly_fields = ['data_registro']
    actions = [aprovar_denuncias]


@admin.register(DenunciaDetalhada)
class DenunciaDetalhadaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'denuncia', 'criado_em')
    search_fields = ('nome', 'email', 'telefone')
    list_filter = ('criado_em',)
    ordering = ('-criado_em',)

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'enviado_em')
    search_fields = ('nome', 'email', 'mensagem')
    list_filter = ('enviado_em',)
    readonly_fields = ('enviado_em',)
