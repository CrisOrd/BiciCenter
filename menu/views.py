from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from.models import Bicicleta, Repuesto, Accesorio

def mainPage(request):
    return render(request, 'master.html')

def inicioPage(request):
    return render(request, 'inicioSesion.html')

def registrarPage(request):
    return render(request, 'registro.html')

def mantemientoPage(request):
    return render(request, 'mantenimiento.html')

def recuperarContraseñaPage(request):
    return render(request, 'recuperarContraseña.html')

def tienda(request):
    return render(request, 'tienda.html')


def registroBicicleta(request):
    return render(request, 'registrobici.html')

def carrito(request):
    return render(request, 'carrito.html')

def repuesto(request):
    return render(request, 'repuestos.html')

def accesorios(request):
    return render(request, 'accesorios.html')

def bicicletas(request):
    return render(request, 'bicicletas.html')

class BicicletasListView(ListView):
    model = Bicicleta
    template_name = 'bicicletas.html'
    context_object_name = 'bicicletas'

class RepuestosListView(ListView):
    model = Repuesto
    template_name = 'repuestos.html'
    context_object_name = 'repuestos'

class AccesoriosListView(ListView):
    model = Accesorio
    template_name = 'accesorios.html'
    context_object_name = 'accesorios'

# Vista para la página maestra que muestra todos los tipos de productos
class MasterListView(ListView):
    model = Bicicleta
    template_name = 'master.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bicicletas'] = Bicicleta.objects.all()
        context['repuestos'] = Repuesto.objects.all()
        context['accesorios'] = Accesorio.objects.all()
        return context


class BicicletaCreateView(CreateView):
    model = Bicicleta
    fields = ['nombre', 'modelo', 'descripcion', 'precio', 'imagen']
    template_name = 'formulario_bici.html'
    success_url = reverse_lazy('mantenimiento')

class RepuestosListView(ListView):
    model = Repuesto
    template_name = 'repuestos.html'
    context_object_name = 'repuestos'

class AccesoriosListView(ListView):
    model = Accesorio
    template_name = 'accesorios.html'
    context_object_name = 'accesorios'