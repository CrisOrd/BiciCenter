from django.contrib import admin
from django.urls import path ,include   
from  menu import views
from menu.views import RegistroBicicletaView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicioSesion/', views.inicioPage, name='inicioSesion'),
    path('registro/', views.registroPage, name='registro'),
    path('logout/', views.logoutUser, name='logout'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),  # Cambiado a mantemientoPage
    path('registrobici/', RegistroBicicletaView.as_view(), name='registrobici'),
    path('bicicletas/', views.BicicletasListView.as_view(), name='bicicletas'), 
    path('repuestos/', views.RepuestosListView.as_view(), name='repuestos'),
    path('accesorios/', views.AccesoriosListView.as_view(), name='accesorios'),
    path('', views.MasterListView.as_view(), name='master'), 
    path('accounts/', include('django.contrib.auth.urls')),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('historial-mantenimientos/', views.historialMantenimientosPage, name='historial_mantenimientos'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)