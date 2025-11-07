from django.contrib import admin
from django.urls import path, include   
from menu import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('inicioSesion/', views.inicioPage, name='inicioSesion'),
    path('registro/', views.registroPage, name='registro'),
    path('logout/', views.logoutUser, name='logout'),
    # Asegurar que cualquier enlace a /accounts/logout/ use nuestra vista personalizada
    path('accounts/logout/', views.logoutUser),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Página Principal
    path('', views.MasterListView.as_view(), name='master'),
    
    # Productos con Filtros (funciones en lugar de clases)
    path('bicicletas/', views.BicicletasListView, name='bicicletas'), 
    path('repuestos/', views.RepuestosListView, name='repuestos'),
    path('accesorios/', views.AccesoriosListView, name='accesorios'),
    path('buscar/', views.Buscar, name='buscar'),
    
    # Gestión de Bicicletas y Mantenimiento
    path('registrobici/', views.agendar_cita, name='registrobici'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
    path('historial-mantenimientos/', views.historialMantenimientosPage, name='historial_mantenimientos'),
    path('finalizar-orden/', views.finalizar_orden, name='finalizar_orden'),
    # Ruta alternativa para acceder al módulo 'menu'
    path('menu/', views.MasterListView.as_view(), name='menu_home'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)