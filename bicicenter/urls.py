from django.contrib import admin
from django.urls import path
from  menu import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', views.mainPage, name='menu'),
    path('inicioSesion/', views.inicioPage, name='InicioSesion'),
    path('registro/', views.registrarPage, name='registrar'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
    path('recuperarContraseña/', views.recuperarContraseñaPage, name='recuperarContraseña'),
    path('tienda/', views.tienda, name='tienda'),
    path('registrobici/', views.registroBicicleta, name='registrobici'),
    path('carrito/', views.carrito, name='carrito'),
]