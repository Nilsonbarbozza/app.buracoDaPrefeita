from django.shortcuts import render, redirect, get_object_or_404
from .models import CidadeDenuncia, Denuncia
from django.contrib import messages


def home(request):
    denuncias = Denuncia.objects.filter(ativo=True).order_by('-data_registro')
    return render(request, 'paghome.html', {'denuncias': denuncias})

# views.py
def buscar_por_cidade(request):
    if request.method == 'GET':
        cidade_selecionada = request.GET.get("cidade")
        denuncias = Denuncia.objects.filter(endereco__icontains=cidade_selecionada) if cidade_selecionada else []
        cidades = CidadeDenuncia.objects.filter(ativo=True)
        return render(request, "paghome.html", {"denuncias": denuncias, "cidades": cidades})

def enviar_denuncia(request):
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        nome_denunciante = request.POST.get('nome_denunciante')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        cidade_id = request.POST.get('cidade')

        # Validações básicas (email, telefone, endereco e cidade são obrigatórios)
        if not all([foto, email, telefone, endereco, cidade_id]):
            messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
            return redirect('enviar_denuncia')

        cidade = CidadeDenuncia.objects.get(id=cidade_id)

        denuncia = Denuncia.objects.create(
            foto=foto,
            nome_denunciante=nome_denunciante or None,
            email=email,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            contagem_denuncias=1,  # padrão
            ativo=False,  # ainda não aprovado
            situacao='NAO_RESOLVIDO',  # padrão
        )

        messages.success(request, 'Denúncia enviada com sucesso! Aguarde a aprovação.')
        return redirect('home')  # redirecionar para mural ou página de sucesso

    # Método GET: renderiza o formulário
    cidades = CidadeDenuncia.objects.filter(ativo=True)
    return render(request, 'denuncia.html', {'cidades': cidades})


def denunciar_existente(request, denuncia_id):
    if request.method == 'POST':
        denuncia = get_object_or_404(Denuncia, id=denuncia_id)
        denuncia.qtd_denuncias += 1
        denuncia.save()
    return redirect('home')  # ou outra view que mostra os cards
