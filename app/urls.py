from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('denuncia/', views.enviar_denuncia,  name='enviar_denuncia'),
    path('denunciar/<int:denuncia_id>/', views.denunciar_existente, name='denunciar_existente'),
    path('denunciar_modal/<int:denuncia_id>/', views.denunciar_existente_modal, name='denunciar_existente_modal'),
    path('checkout/', views.checkout, name='checkout' )

]