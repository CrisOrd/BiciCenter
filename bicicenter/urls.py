from django.contrib import admin
from django.urls import path, include   
from menu import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicioSesion/', views.inicioPage, name='inicioSesion'),
    path('registro/', views.registroPage, name='registro'),
    path('logout/', views.logoutUser, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.MasterListView.as_view(), name='master'),
    path('bicicletas/', views.BicicletasListView, name='bicicletas'), 
    path('repuestos/', views.RepuestosListView, name='repuestos'),
    path('accesorios/', views.AccesoriosListView, name='accesorios'),
    path('buscar/', views.Buscar, name='buscar'),
    path('producto/<str:tipo>/<int:id>/', views.producto_detalle, name='producto_detalle'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-al-carrito/<str:tipo>/<int:id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-del-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar-cantidad/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('comprar-ahora/<str:tipo>/<int:id>/', views.comprar_ahora, name='comprar_ahora'),
    path('vaciar-carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('proceder-al-pago/', views.proceder_al_pago, name='proceder_al_pago'),
    path('registrobici/', views.agendar_cita, name='registrobici'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
    path('historial-mantenimientos/', views.historialMantenimientosPage, name='historial_mantenimientos'),
    path('finalizar-orden/', views.finalizar_orden, name='finalizar_orden'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)