from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import CidadeDenuncia, Denuncia, DenunciaDetalhada
from django.contrib import messages
from .forms import DenunciaDetalhadaForm
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    cidade_filtro = request.GET.get("cidade")
    page = request.GET.get("page") or 1

    try:
        page = int(page)
    except ValueError:
        page = 1

    # Aplica filtro se cidade for informada
    if cidade_filtro:
        base_query = Denuncia.objects.filter(ativo=True, endereco__icontains=cidade_filtro).order_by('-data_registro')
    else:
        base_query = Denuncia.objects.filter(ativo=True).order_by('-data_registro')

    paginator = Paginator(base_query, 7)

    # Ajax: carregar mais cards dinamicamente
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            denuncias = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            return JsonResponse({"html": ""})

        html = render_to_string("partials/_card_denuncia.html", {"denuncias": denuncias}, request=request)
        return JsonResponse({"html": html})

    try:
        denuncias = paginator.page(1)
    except (EmptyPage, PageNotAnInteger):
        denuncias = []

    cidades = CidadeDenuncia.objects.filter(ativo=True)

    context = {
        "denuncias": denuncias,
        "cidades": cidades,
        "cidade_selecionada": cidade_filtro
    }
    return render(request, "paghome.html", context)




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
        denuncia.contagem_denuncias += 1
        denuncia.save()
    return redirect('home')  # ou outra view que mostra os cards

def denunciar_existente_modal(request, denuncia_id):
    denuncia = get_object_or_404(Denuncia, pk=denuncia_id)

    if request.method == 'POST':
        form = DenunciaDetalhadaForm(request.POST)
        if form.is_valid():
            nova_denuncia = form.save(commit=False)
            nova_denuncia.denuncia = denuncia
            nova_denuncia.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'error': 'Método inválido'}, status=400)

def checkout(request):
    if request.method == 'GET':
        return render(request, 'checkout.html')