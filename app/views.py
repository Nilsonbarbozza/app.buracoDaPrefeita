from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import CidadeDenuncia, Denuncia, DenunciaDetalhada, Mensagem_Contato
from django.contrib import messages
from .forms import DenunciaDetalhadaForm
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives





def home(request):
    cidade_filtro = request.GET.get("cidade")
    cidade_selecionada = request.GET.get("cidade")
    filtro_resolvido = request.GET.get("resolvido") == "true"

    if cidade_selecionada:
        denuncias = Denuncia.objects.filter(cidade__nome=cidade_selecionada)
    else:
        denuncias = Denuncia.objects.all()

    if filtro_resolvido:
        denuncias = denuncias.filter(situacao='RESOLVIDO')
    

    total_denuncias = denuncias.count()
    cidades = CidadeDenuncia.objects.filter(ativo=True)   
    denuncias_resolvidas = denuncias.filter(situacao='RESOLVIDO').count()

    page = request.GET.get("page") or 1

    try:
        page = int(page)
    except ValueError:
        page = 1

    # Aplica filtro se cidade for informada
    denuncias_filtradas = denuncias.filter(ativo=True).order_by('-data_registro')

    paginator = Paginator(denuncias_filtradas, 7)

    # Ajax: carregar mais cards dinamicamente
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            denuncias = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            return JsonResponse({"html": ""})

        html = render_to_string("partials/_card_denuncia.html", {"denuncias": denuncias}, request=request)
        return JsonResponse({"html": html})

    # Corrigido aqui
    try:
        denuncias_paginadas = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        denuncias_paginadas = []

    cidades = CidadeDenuncia.objects.filter(ativo=True)

    context = {
        "denuncias": denuncias_paginadas,  # agora sim o template usa só os paginados corretos
        "cidades": cidades,
        "cidade_selecionada": cidade_filtro,
        "total_denuncias": total_denuncias,
        "filtro_resolvido": filtro_resolvido,
        "denuncias_resolvidas": denuncias_resolvidas,
        'request': request,
        
    }

    # Opcional: log para debug
    for denuncia in denuncias_paginadas:
        print(f"Denúncia: {denuncia.endereco}, Cidade: {denuncia.cidade.nome}")

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

        # Validação dos campos obrigatórios
        if not all([foto, email, telefone, endereco, cidade_id]):
            messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
            return redirect('enviar_denuncia')

        # Valida cidade
        try:
            cidade = CidadeDenuncia.objects.get(id=cidade_id)
        except CidadeDenuncia.DoesNotExist:
            messages.error(request, 'Cidade selecionada inválida.')
            return redirect('enviar_denuncia')

        # Cria a denúncia
        denuncia = Denuncia.objects.create(
            foto=foto,
            nome_denunciante=nome_denunciante or None,
            email=email,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            contagem_denuncias=1,
            ativo=False,
            situacao='NAO_RESOLVIDO',
        )

        # Envia o e-mail de confirmação
        assunto = "Denúncia registrada com sucesso!"
        remetente = settings.DEFAULT_FROM_EMAIL
        destinatario = [email]

        corpo_html = render_to_string("emails/denuncia.html", {
            'nome': nome_denunciante or 'Anônimo',
        })

        email_denuncia = EmailMultiAlternatives(
            subject=assunto,
            body=corpo_html,
            from_email=remetente,
            to=destinatario,
        )
        email_denuncia.attach_alternative(corpo_html, "text/html")
        email_denuncia.send()

        messages.success(request, "Denúncia enviada com sucesso! Aguarde a aprovação.")
        return redirect('home')

    # Método GET
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
    
def contato(request):
    if request.method =='GET':
        return render(request, 'contato.html')
    if request.method == 'POST':
            # Honeypot
            if request.POST.get('confirmacao_humana'):
                messages.error(request, "Erro ao enviar. Validação falhou.")
                return redirect('contato')

            nome = request.POST.get('nome')
            email = request.POST.get('email')
            telefone = request.POST.get('telefone')
            mensagem = request.POST.get('mensagem')

            if nome and email and telefone and mensagem:
                Mensagem_Contato.objects.create(
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    mensagem=mensagem
                )

                # Head email
                assunto = "Obrigado pela mensagem de contato"
                remetente = settings.DEFAULT_FROM_EMAIL
                destinatario = [email]

                corpo_html = render_to_string("emails/contato.html", {
                    'nome': nome,
                    'email': email,
                    'telefone': telefone,
                    'mensagem': mensagem,
                })

                email = EmailMultiAlternatives(
                    subject=assunto,
                    body=corpo_html,
                    from_email=remetente,
                    to=destinatario,
                )
                email.attach_alternative(corpo_html, "text/html")
                email.send()

                messages.success(request, "Mensagem enviada com sucesso!")
                return render(request, 'contato.html')            
            else:
                messages.error(request, "Preencha todos os campos obrigatórios.")

                return redirect('contato.html')


            

    

