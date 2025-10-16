from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib import messages
from .models import (Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente, 
                     ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View 
import json
from decimal import Decimal

def inicioPage(request):
    # Si el usuario ya está autenticado, redirigirlo a la página principal.
    if request.user.is_authenticated:
        return redirect('master')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'master')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Retorna JSON con la URL de redirección
            return JsonResponse({'success': True, 'redirect_url': next_url, 'message': f'¡Bienvenido de nuevo, {user.first_name}!'})
        else:
            # Respuesta JSON en caso de error
            return JsonResponse({'success': False, 'message': 'Nombre de usuario o contraseña incorrectos.'})

    return render(request, 'inicioSesion.html')

def registroPage(request):
    # Si el usuario ya está autenticado, redirigirlo a la página principal.
    if request.user.is_authenticated:
        return redirect('master')

    if request.method == 'POST':
        nombre = request.POST.get('first_name')
        apellido = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        next_url = request.POST.get('next', 'master')

        if password != password2:
            return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'El nombre de usuario ya está en uso.'})

        if Cliente.objects.filter(rut=rut).exists():
            return JsonResponse({'success': False, 'message': 'El RUT ya se encuentra registrado.'})

        try:
            # Crea el objeto User
            user = User.objects.create_user(username=username, email=email, password=password, first_name=nombre, last_name=apellido)
            user.save()

            # Crea el objeto Cliente
            cliente = Cliente.objects.create(rut=rut, nombre=nombre, apellido=apellido, email=email)
            cliente.save()

            # Inicia sesión inmediatamente después de crear la cuenta
            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return JsonResponse({'success': True, 'redirect_url': next_url, 'message': f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada y has iniciado sesión exitosamente.'})
            else:
                return JsonResponse({'success': False, 'message': 'Tu cuenta fue creada, pero no se pudo iniciar sesión automáticamente. Por favor, inicia sesión manualmente.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ocurrió un error al registrar: {e}'})

    return render(request, 'registro.html')

def logoutUser(request):
    next_url = request.GET.get('next', 'master')
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect(next_url)


@login_required
def agendar_cita(request):
    """Vista para registrar la bicicleta del cliente"""
    user = request.user
    cliente_data = None
    
    try:
        # Buscar cliente por email del usuario autenticado
        cliente_data = Cliente.objects.get(email=user.email)
    except Cliente.DoesNotExist:
        # Si no existe el cliente, crear uno con los datos del usuario
        cliente_data = Cliente.objects.create(
            rut="",  # Se completará en el formulario
            nombre=user.first_name,
            apellido=user.last_name,
            email=user.email
        )

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            bike_brand = request.POST.get('bike_brand')
            bike_color = request.POST.get('bike_color')
            bike_type = request.POST.get('bike_type')
            bike_year = request.POST.get('bike_year')
            additional_notes = request.POST.get('additional_notes', '')
            rut_from_form = request.POST.get('rut') # Obtener el RUT del formulario

            # Siempre actualizar el RUT del cliente con el valor del formulario
            # Esto maneja el caso donde el RUT ya existe y el campo es "readonly"
            if rut_from_form and not cliente_data.rut:
                cliente_data.rut = rut_from_form
                cliente_data.save()

            # Crear nueva bicicleta
            nueva_bicicleta = BicicletaCliente.objects.create(
                cliente=cliente_data,
                marca=bike_brand,
                color=bike_color,
                tipo=bike_type,
                año=int(bike_year) if bike_year else None,
                notas_adicionales=additional_notes
            )
            
            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')
            
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')
    
    # Contexto con datos del usuario autenticado - IMPORTANTE: pasar request
    context = {
        'user': user,
        'cliente': cliente_data
    }
    
    return render(request, 'registrobici.html', context)

@login_required
def mantemientoPage(request):
    """Vista para mostrar la página de mantenimiento y procesar órdenes"""
    user = request.user
    cliente_data = None
    bicicleta_data = None
    
    try:
        # Obtener cliente por email del usuario autenticado
        cliente_data = Cliente.objects.get(email=user.email)
        # Obtener la última bicicleta registrada del cliente
        bicicleta_data = BicicletaCliente.objects.filter(cliente=cliente_data).last()
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil primero.')
        return redirect('registrobici')
    
    if not bicicleta_data:
        messages.error(request, 'Debes registrar tu bicicleta primero.')
        return redirect('registrobici')

    if request.method == 'POST':
        try:
            # Obtener servicios seleccionados del formulario
            servicios_seleccionados = request.POST.getlist('servicios')
            
            if not servicios_seleccionados:
                messages.error(request, 'Debes seleccionar al menos un servicio.')
                context = {
                    'user': user,
                    'cliente': cliente_data,
                    'bicicleta': bicicleta_data,
                    'servicios': ServicioMantenimiento.objects.all()
                }
                return render(request, 'mantenimiento.html', context)

            # Crear orden de mantenimiento
            orden = OrdenMantenimiento.objects.create(
                cliente=cliente_data,
                bicicleta=bicicleta_data,
                estado='pendiente'
            )

            # Crear items de la orden para cada servicio seleccionado
            for servicio_nombre in servicios_seleccionados:
                try:
                    servicio = ServicioMantenimiento.objects.get(nombre=servicio_nombre)
                    ItemOrdenMantenimiento.objects.create(
                        orden=orden,
                        servicio=servicio,
                        precio=servicio.precio
                    )
                except ServicioMantenimiento.DoesNotExist:
                    continue

            # Calcular totales automáticamente
            orden.calcular_totales()
            
            messages.success(request, f'¡Orden de mantenimiento #{orden.id} creada exitosamente! Total: ${orden.total}')
            return redirect('mantenimiento')
            
        except Exception as e:
            messages.error(request, f'Error al crear la orden: {e}')
    
    # Obtener servicios disponibles para mostrar en el template
    servicios = ServicioMantenimiento.objects.all()
    
    context = {
        'user': user,
        'cliente': cliente_data,
        'bicicleta': bicicleta_data,
        'servicios': servicios
    }
    
    return render(request, 'mantenimiento.html', context)


@login_required
def historialMantenimientosPage(request):
    """Vista para mostrar el historial de mantenimientos del usuario"""
    user = request.user
    try:
        cliente = Cliente.objects.get(email=user.email)
        ordenes = OrdenMantenimiento.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    except Cliente.DoesNotExist:
        ordenes = []
    
    context = {
        'user': user,
        'ordenes': ordenes
    }
    return render(request, 'historial_mantenimientos.html', context)

# Class-based views for product lists
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

class MasterListView(ListView):
    model = Bicicleta
    template_name = 'master.html'
    context_object_name = 'productos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bicicletas'] = Bicicleta.objects.all()[:4]
        context['accesorios'] = Accesorio.objects.all()[:4]
        context['repuestos'] = Repuesto.objects.all()[:4]
        return context

@login_required
def finalizar_orden(request):
    """
    Procesa la solicitud de finalización de una orden de mantenimiento
    y devuelve una respuesta JSON.
    """
    if request.method == 'POST':
        try:
            # 1. Obtener la bicicleta del usuario
            cliente = Cliente.objects.get(email=request.user.email)
            bicicleta = BicicletaCliente.objects.filter(cliente=cliente).first()
            if not bicicleta:
                return JsonResponse({'success': False, 'error': 'No se encontró una bicicleta registrada para este usuario.'})

            # 2. Leer los datos JSON de la solicitud
            data = json.loads(request.body)
            servicios_nombres = data.get('servicios', [])
            
            # 3. Crear la Orden de Mantenimiento
            orden = OrdenMantenimiento.objects.create(
                cliente=cliente,
                bicicleta=bicicleta,
                subtotal=Decimal(str(data.get('subtotal', 0))),
                total=Decimal(str(data.get('total', 0)))
            )

            # 4. Agregar cada servicio a la orden
            for servicio_nombre in servicios_nombres:
                try:
                    servicio = ServicioMantenimiento.objects.get(nombre=servicio_nombre)
                    ItemOrdenMantenimiento.objects.create(
                        orden=orden,
                        servicio=servicio,
                        precio=servicio.precio
                    )
                except ServicioMantenimiento.DoesNotExist:
                    # Si un servicio no existe, puedes registrar un error o ignorarlo.
                    print(f"Advertencia: Servicio '{servicio_nombre}' no encontrado.")
                    continue
            
            # Opcional: Recalcular totales en el backend si los del frontend no son fiables
            orden.calcular_totales()
            
            # 5. Devolver una respuesta JSON exitosa
            return JsonResponse({
                'success': True,
                'orden_id': orden.id,
                'total': float(orden.total)
            })

        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No se encontró un perfil de cliente para este usuario.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Formato de datos JSON inválido en la solicitud.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error interno del servidor: {str(e)}'})
    
    # 6. Manejar métodos de solicitud no permitidos (si alguien intenta un GET)
    return JsonResponse({'success': False, 'error': 'Método de solicitud no válido.'}, status=405)

class RegistroBicicletaView(View):
    """Vista basada en clase para registro de bicicletas (alternativa)"""
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('inicioSesion')
        return render(request, 'registrobici.html')

    def post(self, request):
        try:
            user = request.user
            cliente_data = Cliente.objects.get(email=user.email)
            
            marca = request.POST['bike_brand']
            color = request.POST['bike_color'] 
            tipo = request.POST['bike_type']
            año = request.POST.get('bike_year')
            notas = request.POST.get('additional_notes', '')
            
            BicicletaCliente.objects.create(
                cliente=cliente_data,
                marca=marca,
                color=color,
                tipo=tipo,
                año=int(año) if año else None,
                notas_adicionales=notas
            )
            
            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')
        
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')
            return render(request, 'registrobici.html')