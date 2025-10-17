from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib import messages
from .models import (Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente, 
                     ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from decimal import Decimal
from django.db.models import Q


# ============= FUNCIONES AUXILIARES =============

def aplicar_ordenamiento(queryset, ordenar_por):
    """Función auxiliar para aplicar ordenamiento a un queryset"""
    orden_map = {
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'modelo_asc': 'modelo',
        'modelo_desc': '-modelo',
    }
    return queryset.order_by(orden_map[ordenar_por]) if ordenar_por in orden_map else queryset


# ============= AUTENTICACIÓN =============

def inicioPage(request):
    """Vista para inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('master')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'master')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True, 
                'redirect_url': next_url, 
                'message': f'¡Bienvenido de nuevo, {user.first_name}!'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Nombre de usuario o contraseña incorrectos.'
            })

    return render(request, 'inicioSesion.html')


def registroPage(request):
    """Vista para registro de usuarios"""
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

        # Validaciones
        if password != password2:
            return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'El nombre de usuario ya está en uso.'})

        if Cliente.objects.filter(rut=rut).exists():
            return JsonResponse({'success': False, 'message': 'El RUT ya se encuentra registrado.'})

        try:
            # Crear usuario y cliente
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password, 
                first_name=nombre, 
                last_name=apellido
            )
            Cliente.objects.create(
                rut=rut, 
                nombre=nombre, 
                apellido=apellido, 
                email=email
            )

            # Iniciar sesión automáticamente
            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return JsonResponse({
                    'success': True, 
                    'redirect_url': next_url, 
                    'message': f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada exitosamente.'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'Cuenta creada, pero no se pudo iniciar sesión. Inicia sesión manualmente.'
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ocurrió un error al registrar: {e}'})

    return render(request, 'registro.html')


def logoutUser(request):
    """Vista para cerrar sesión"""
    next_url = request.GET.get('next', 'master')
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect(next_url)


# ============= VISTAS DE PRODUCTOS CON FILTROS =============

def BicicletasListView(request):
    """Vista para listar bicicletas con filtros"""
    bicicletas = Bicicleta.objects.all()
    
    # Aplicar filtros
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        bicicletas = bicicletas.filter(tipo_bicicleta=tipo_filtro)
    
    # Aplicar ordenamiento
    ordenar = request.GET.get('ordenar', '')
    bicicletas = aplicar_ordenamiento(bicicletas, ordenar)
    
    context = {
        'bicicletas': bicicletas,
        'tipos_disponibles': Bicicleta.objects.values_list('tipo_bicicleta', flat=True).distinct(),
    }
    return render(request, 'bicicletas.html', context)


def RepuestosListView(request):
    """Vista para listar repuestos con filtros"""
    repuestos = Repuesto.objects.all()
    
    # Aplicar ordenamiento
    ordenar = request.GET.get('ordenar', '')
    repuestos = aplicar_ordenamiento(repuestos, ordenar)
    
    return render(request, 'repuestos.html', {'repuestos': repuestos})


def AccesoriosListView(request):
    """Vista para listar accesorios con filtros"""
    accesorios = Accesorio.objects.all()
    
    # Aplicar ordenamiento
    ordenar = request.GET.get('ordenar', '')
    accesorios = aplicar_ordenamiento(accesorios, ordenar)
    
    return render(request, 'accesorios.html', {'accesorios': accesorios})


def Buscar(request):
    """Vista para buscar productos con filtros"""
    query = request.GET.get('q', '').strip()
    ordenar = request.GET.get('ordenar', '')
    
    bicicletas = []
    repuestos = []
    accesorios = []
    
    if query:
        # Búsqueda en Bicicletas
        bicicletas = Bicicleta.objects.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo_bicicleta__icontains=query) |
            Q(modelo_bicicleta__icontains=query)
        )
        
        # Búsqueda en Repuestos
        repuestos = Repuesto.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Búsqueda en Accesorios
        accesorios = Accesorio.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )
        
        # Aplicar ordenamiento
        if ordenar:
            bicicletas = aplicar_ordenamiento(bicicletas, ordenar)
            repuestos = aplicar_ordenamiento(repuestos, ordenar)
            accesorios = aplicar_ordenamiento(accesorios, ordenar)
    
    context = {
        'query': query,
        'bicicletas': bicicletas,
        'repuestos': repuestos,
        'accesorios': accesorios,
        'total_resultados': len(bicicletas) + len(repuestos) + len(accesorios)
    }
    
    return render(request, 'buscar.html', context)


# ============= VISTA MASTER =============

class MasterListView(ListView):
    """Vista principal con productos destacados"""
    model = Bicicleta
    template_name = 'master.html'
    context_object_name = 'productos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bicicletas'] = Bicicleta.objects.all()[:4]
        context['accesorios'] = Accesorio.objects.all()[:4]
        context['repuestos'] = Repuesto.objects.all()[:4]
        return context


# ============= GESTIÓN DE BICICLETAS Y MANTENIMIENTO =============

@login_required
def agendar_cita(request):
    """Vista para registrar la bicicleta del cliente"""
    user = request.user
    
    # Obtener o crear cliente
    cliente_data, created = Cliente.objects.get_or_create(
        email=user.email,
        defaults={
            'rut': '',
            'nombre': user.first_name,
            'apellido': user.last_name,
        }
    )

    if request.method == 'POST':
        try:
            # Actualizar RUT si es necesario
            rut_from_form = request.POST.get('rut')
            if rut_from_form and not cliente_data.rut:
                cliente_data.rut = rut_from_form
                cliente_data.save()

            # Crear bicicleta
            BicicletaCliente.objects.create(
                cliente=cliente_data,
                marca=request.POST.get('bike_brand'),
                color=request.POST.get('bike_color'),
                tipo=request.POST.get('bike_type'),
                año=int(request.POST.get('bike_year')) if request.POST.get('bike_year') else None,
                notas_adicionales=request.POST.get('additional_notes', '')
            )
            
            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')
            
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')
    
    return render(request, 'registrobici.html', {'user': user, 'cliente': cliente_data})


@login_required
def mantemientoPage(request):
    """Vista para gestionar órdenes de mantenimiento"""
    user = request.user
    
    try:
        cliente_data = Cliente.objects.get(email=user.email)
        bicicleta_data = BicicletaCliente.objects.filter(cliente=cliente_data).last()
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil primero.')
        return redirect('registrobici')
    
    if not bicicleta_data:
        messages.error(request, 'Debes registrar tu bicicleta primero.')
        return redirect('registrobici')

    if request.method == 'POST':
        servicios_seleccionados = request.POST.getlist('servicios')
        
        if not servicios_seleccionados:
            messages.error(request, 'Debes seleccionar al menos un servicio.')
        else:
            try:
                # Crear orden
                orden = OrdenMantenimiento.objects.create(
                    cliente=cliente_data,
                    bicicleta=bicicleta_data,
                    estado='pendiente'
                )

                # Agregar servicios
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

                orden.calcular_totales()
                messages.success(request, f'¡Orden #{orden.id} creada exitosamente! Total: ${orden.total}')
                return redirect('mantenimiento')
                
            except Exception as e:
                messages.error(request, f'Error al crear la orden: {e}')
    
    context = {
        'user': user,
        'cliente': cliente_data,
        'bicicleta': bicicleta_data,
        'servicios': ServicioMantenimiento.objects.all()
    }
    
    return render(request, 'mantenimiento.html', context)


@login_required
def historialMantenimientosPage(request):
    """Vista para mostrar el historial de mantenimientos"""
    user = request.user
    try:
        cliente = Cliente.objects.get(email=user.email)
        ordenes = OrdenMantenimiento.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    except Cliente.DoesNotExist:
        ordenes = []
    
    return render(request, 'historial_mantenimientos.html', {'user': user, 'ordenes': ordenes})


@login_required
def finalizar_orden(request):
    """Procesa la finalización de una orden de mantenimiento vía AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no válido.'}, status=405)
    
    try:
        cliente = Cliente.objects.get(email=request.user.email)
        bicicleta = BicicletaCliente.objects.filter(cliente=cliente).first()
        
        if not bicicleta:
            return JsonResponse({'success': False, 'error': 'No se encontró una bicicleta registrada.'})

        data = json.loads(request.body)
        servicios_nombres = data.get('servicios', [])
        
        # Crear orden
        orden = OrdenMantenimiento.objects.create(
            cliente=cliente,
            bicicleta=bicicleta,
            subtotal=Decimal(str(data.get('subtotal', 0))),
            total=Decimal(str(data.get('total', 0)))
        )

        # Agregar servicios
        for servicio_nombre in servicios_nombres:
            try:
                servicio = ServicioMantenimiento.objects.get(nombre=servicio_nombre)
                ItemOrdenMantenimiento.objects.create(
                    orden=orden,
                    servicio=servicio,
                    precio=servicio.precio
                )
            except ServicioMantenimiento.DoesNotExist:
                continue
        
        orden.calcular_totales()
        
        return JsonResponse({
            'success': True,
            'orden_id': orden.id,
            'total': float(orden.total)
        })

    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No se encontró el cliente.'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato JSON inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})