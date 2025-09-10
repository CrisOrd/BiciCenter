from django.shortcuts import render

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