# models.py
from django.db import models
from django.utils import timezone

class CidadeDenuncia(models.Model):

    CIDADES_DISPONIVEIS = [
        ('BARAUNA', 'Baraúna'),
        ('MOSSORO', 'Mossóro'),
        # Adicione outras conforme necessário
    ]

    ESTADOS = [
        ('RN', 'Rio Grande do Norte'),
        # Adicione outros se expandir depois
    ]

    nome = models.CharField(max_length=100, choices=CIDADES_DISPONIVEIS, unique=True)
    cep = models.CharField(max_length=9)  # formato: 59690-000
    estado = models.CharField(max_length=2, choices=ESTADOS)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_nome_display()} - {self.estado}"

# Denuncias

class Denuncia(models.Model):
    STATUS_CHOICES = [
        ('NAO_RESOLVIDO', 'NÃO RESOLVIDO'),
        ('RESOLVIDO', 'RESOLVIDO'),
    ]

    foto = models.ImageField(upload_to='denuncias/', null=True, blank=False)
    nome_denunciante = models.CharField(max_length=100, blank=True, null=True)  # opcional = anônimo
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    data_registro = models.DateTimeField(default=timezone.now)
    situacao = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NAO_RESOLVIDO'
    )
    ativo = models.BooleanField(default=False)  # visível só após aprovação
    cidade = models.ForeignKey('CidadeDenuncia', on_delete=models.CASCADE)  # cidade filtrável
    contagem_denuncias = models.PositiveIntegerField(default=1)

    def nome_visivel(self):
        return self.nome_denunciante if self.nome_denunciante else "Anônimo"

    def __str__(self):
        return f"{self.nome_visivel()} - {self.endereco[:30]}..."

# denunciantes-id/models.py

class DenunciaDetalhada(models.Model):
    denuncia = models.ForeignKey('Denuncia', on_delete=models.CASCADE, related_name='denuncias_detalhadas')
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.denuncia}"
