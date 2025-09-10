# admin.py
from django.contrib import admin
from .models import (Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente,
                     ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento)

@admin.register(Bicicleta)
class BicicletaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modelo', 'precio')
    search_fields = ('nombre', 'modelo')

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)

@admin.register(Accesorio)
class AccesorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'email')
    search_fields = ('nombre', 'apellido', 'rut', 'email')

@admin.register(BicicletaCliente)
class BicicletaClienteAdmin(admin.ModelAdmin):
    # Campos corregidos para coincidir con models.py
    list_display = ('cliente', 'marca', 'color', 'tipo')
    search_fields = ('cliente__nombre', 'marca', 'color', 'tipo')
    list_filter = ('tipo',)

@admin.register(ServicioMantenimiento)
class ServicioMantenimientoAdmin(admin.ModelAdmin):
    # Campos corregidos para coincidir con models.py
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)

@admin.register(OrdenMantenimiento)
class OrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'bicicleta', 'fecha_creacion', 'estado', 'total')
    search_fields = ('cliente__nombre', 'bicicleta__marca')
    list_filter = ('estado', 'fecha_creacion')

@admin.register(ItemOrdenMantenimiento)
class ItemOrdenMantenimientoAdmin(admin.ModelAdmin):
    list_display = ('orden', 'servicio', 'precio')
    search_fields = ('orden__cliente__nombre', 'servicio__nombre')