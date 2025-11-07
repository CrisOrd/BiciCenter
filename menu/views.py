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
import datetime
import re
from django.utils.http import url_has_allowed_host_and_scheme

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

        if password != password2:
            return JsonResponse({'success': False, 'message': 'Las contraseñas no coinciden.'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'El nombre de usuario ya está en uso.'})

        if Cliente.objects.filter(rut=rut).exists():
            return JsonResponse({'success': False, 'message': 'El RUT ya se encuentra registrado.'})

        try:
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
    next_url = request.GET.get('next')
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return redirect(next_url)
    return redirect('master')

def BicicletasListView(request):
    """Vista para listar bicicletas con filtros"""
    bicicletas = Bicicleta.objects.all()
    
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        bicicletas = bicicletas.filter(tipo=tipo_filtro)
    
    ordenar = request.GET.get('ordenar', '')
    bicicletas = aplicar_ordenamiento(bicicletas, ordenar)
    
    context = {
        'bicicletas': bicicletas,
        'tipos_disponibles': Bicicleta.objects.values_list('tipo', flat=True).distinct(),
    }
    return render(request, 'bicicletas.html', context)


def RepuestosListView(request):
    """Vista para listar repuestos con filtros"""
    repuestos = Repuesto.objects.all()
    
    ordenar = request.GET.get('ordenar', '')
    repuestos = aplicar_ordenamiento(repuestos, ordenar)
    
    return render(request, 'repuestos.html', {'repuestos': repuestos})


def AccesoriosListView(request):
    """Vista para listar accesorios con filtros"""
    accesorios = Accesorio.objects.all()
    
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
        bicicletas = Bicicleta.objects.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo__icontains=query) |
            Q(modelo__icontains=query)
        )

        repuestos = Repuesto.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )

        accesorios = Accesorio.objects.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query)
        )

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

@login_required
def agendar_cita(request):
    """Vista para registrar la bicicleta del cliente"""
    user = request.user
    
    cliente_qs = Cliente.objects.filter(email=user.email)
    cliente_data = cliente_qs.first()
    created = False
    if not cliente_data:
        cliente_data = Cliente.objects.create(
            email=user.email,
            rut='',
            nombre=user.first_name,
            apellido=user.last_name,
        )
        created = True

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        rut_from_form = request.POST.get('rut', '').strip()
        bike_brand = request.POST.get('bike_brand', '').strip()
        bike_color = request.POST.get('bike_color', '').strip()
        bike_type = request.POST.get('bike_type', '').strip()
        bike_year = request.POST.get('bike_year', '').strip()
        additional_notes = request.POST.get('additional_notes', '').strip()

        missing = []
        if not bike_brand:
            missing.append('Marca de la bicicleta')
        if not bike_color:
            missing.append('Color de la bicicleta')
        if not bike_type:
            missing.append('Tipo de bicicleta')

        if missing:
            messages.error(request, f'Debes completar: {", ".join(missing)}')
            return redirect('registrobici')
        
        anio_val = None
        if bike_year:
            try:
                anio_val = int(bike_year)
                current_year = datetime.date.today().year
                if anio_val < 1900 or anio_val > current_year:
                    messages.error(request, 'Año de la bicicleta fuera de rango.')
                    return redirect('registrobici')
            except ValueError:
                messages.error(request, 'Año de la bicicleta inválido.')
                return redirect('registrobici')

        if rut_from_form:
            rut_clean = rut_from_form.replace('.', '').upper()
            if not re.match(r'^\d{7,8}-[0-9K]$', rut_clean):
                if re.match(r'^\d{7,8}$', rut_clean):
                    rut_clean = rut_clean[:-1] + '-' + rut_clean[-1]
                else:
                    messages.error(request, 'Formato de RUT inválido. Use formato 12.345.678-9')
                    return redirect('registrobici')
        else:
            rut_clean = ''

        try:
            if cliente_data:
                updated = False
                if nombre and cliente_data.nombre != nombre:
                    cliente_data.nombre = nombre
                    updated = True
                if apellido and cliente_data.apellido != apellido:
                    cliente_data.apellido = apellido
                    updated = True
                if email and cliente_data.email != email:
                    cliente_data.email = email
                    updated = True
                if rut_clean and cliente_data.rut != rut_clean:
                    cliente_data.rut = rut_clean
                    updated = True
                if updated:
                    cliente_data.save()
            else:
                cliente_data = Cliente.objects.create(
                    nombre=nombre or user.first_name,
                    apellido=apellido or user.last_name,
                    email=email or user.email or '',
                    rut=rut_clean,
                )

            BicicletaCliente.objects.create(
                cliente=cliente_data,
                marca=bike_brand,
                color=bike_color,
                tipo=bike_type,
                anio=anio_val,
                notas_adicionales=additional_notes
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
    
    cliente_qs = Cliente.objects.filter(email=user.email)
    cliente_data = cliente_qs.first()
    if not cliente_data:
        messages.error(request, 'Debes completar tu perfil primero.')
        return redirect('registrobici')

    bicicleta_data = BicicletaCliente.objects.filter(cliente=cliente_data).last()
    
    if not bicicleta_data:
        messages.error(request, 'Debes registrar tu bicicleta primero.')
        return redirect('registrobici')

    if request.method == 'POST':
        servicios_seleccionados = request.POST.getlist('servicios')
        
        if not servicios_seleccionados:
            messages.error(request, 'Debes seleccionar al menos un servicio.')
        else:
            try:
                orden = OrdenMantenimiento.objects.create(
                    cliente=cliente_data,
                    bicicleta=bicicleta_data,
                    estado='pendiente'
                )
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
    cliente = Cliente.objects.filter(email=user.email).first()
    if cliente:
        ordenes = OrdenMantenimiento.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    else:
        ordenes = []
    
    return render(request, 'historial_mantenimientos.html', {'user': user, 'ordenes': ordenes})


@login_required
def finalizar_orden(request):
    """Procesa la finalización de una orden de mantenimiento vía AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no válido.'}, status=405)
    
    try:
        cliente = Cliente.objects.filter(email=request.user.email).first()
        bicicleta = BicicletaCliente.objects.filter(cliente=cliente).first() if cliente else None

        if not bicicleta:
            return JsonResponse({'success': False, 'error': 'No se encontró una bicicleta registrada.'})

        data = json.loads(request.body)
        servicios_nombres = data.get('servicios', [])

        orden = OrdenMantenimiento.objects.create(
            cliente=cliente,
            bicicleta=bicicleta,
            subtotal=Decimal(str(data.get('subtotal', 0))),
            total=Decimal(str(data.get('total', 0)))
        )

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

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato JSON inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})