from django import forms
from .models import DenunciaDetalhada

class DenunciaDetalhadaForm(forms.ModelForm):
    class Meta:
        model = DenunciaDetalhada
        fields = ['nome', 'email', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input'}),
        }