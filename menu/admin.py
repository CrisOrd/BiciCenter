from django.contrib import admin
from.models import Bicicleta, Repuesto, Accesorio


@admin.register(Bicicleta)
class BicicletaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modelo', 'precio')
    search_fields = ('nombre', 'modelo')

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'bicicleta')
    search_fields = ('nombre',)
    list_filter = ('bicicleta',)

@admin.register(Accesorio)
class AccesorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'bicicleta')
    search_fields = ('nombre',)
    list_filter = ('bicicleta',)
