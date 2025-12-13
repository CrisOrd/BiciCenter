from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menu import views  # Importamos solo las vistas del frontend

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # --- VISTAS DEL FRONTEND (Consumen la API externa) ---
    
    # Autenticación y Home
    path('', views.MasterListView.as_view(), name='master'),
    path('menu/', views.MasterListView.as_view(), name='menu_home'),
    path('inicioSesion/', views.inicioPage, name='inicioSesion'),
    path('registro/', views.registroPage, name='registro'),
    path('logout/', views.logoutUser, name='logout'),
    
    # Catálogo (Usan APIClient)
    path('bicicletas/', views.BicicletasListView, name='bicicletas'), 
    path('repuestos/', views.RepuestosListView, name='repuestos'),
    path('accesorios/', views.AccesoriosListView, name='accesorios'),
    path('buscar/', views.Buscar, name='buscar'),
    path('producto/<str:tipo>/<int:id>/', views.producto_detalle, name='producto_detalle'),
    
    # Carrito y Compras
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-al-carrito/<str:tipo>/<int:id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-del-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar-cantidad/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('comprar-ahora/<str:tipo>/<int:id>/', views.comprar_ahora, name='comprar_ahora'),
    path('vaciar-carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('proceder-al-pago/', views.proceder_al_pago, name='proceder_al_pago'),
    path('finalizar-orden/', views.finalizar_orden, name='finalizar_orden'),
    
    # Servicios
    path('registrobici/', views.agendar_cita, name='registrobici'),
    path('agendar_cita/', views.agendar_cita, name='agendar_cita'),
    path('mantenimiento/', views.mantemientoPage, name='mantenimiento'),
    path('historial-mantenimientos/', views.historialMantenimientosPage, name='historial_mantenimientos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)