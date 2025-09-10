from django.contrib import admin
from django.urls import path
from  menu import views
from django.contrib import admin



urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicioSesion/', views.inicioPage, name='InicioSesion'),
    path('registro/', views.registrarPage, name='registrar'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
    path('recuperarContraseña/', views.recuperarContraseñaPage, name='recuperarContraseña'),
    path('tienda/', views.tienda, name='tienda'),
    path('registrobici/', views.registroBicicleta, name='registrobici'),
    path('carrito/', views.carrito, name='carrito'),
    path('bicicletas/', views.BicicletasListView.as_view(), name='bicicletas'), 
    path('', views.MasterListView.as_view(), name='master'),  # Página principal
    path('repuestos/', views.RepuestosListView.as_view(), name='repuestos'),
    path('accesorios/', views.AccesoriosListView.as_view(), name='accesorios'),

]