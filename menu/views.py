from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib import messages
from .models import (Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente, 
                     ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento,
                     CarritoItem)
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
        next_url = request.POST.get('next', '/')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
            return redirect(next_url if next_url else 'master')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

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
        next_url = request.POST.get('next', '/')

        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'registro.html')

        if Cliente.objects.filter(rut=rut).exists():
            messages.error(request, 'El RUT ya se encuentra registrado.')
            return render(request, 'registro.html')

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
                messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada exitosamente.')
                return redirect(next_url if next_url else 'master')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')

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


# ============= CARRITO DE COMPRAS =============

def carrito(request):
    """Vista para mostrar el carrito de compras"""
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    items = CarritoItem.objects.filter(usuario=request.user)
    
    # Calcular totales
    subtotal = sum(item.get_subtotal() for item in items)
    total = subtotal
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'total': total,
        'total_items': sum(item.cantidad for item in items)
    }
    
    return render(request, 'carrito.html', context)


def agregar_al_carrito(request, tipo, id):
    """Vista para agregar productos al carrito"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    # Validar tipo de producto
    if tipo not in ['bicicleta', 'accesorio', 'repuesto']:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')
    
    # Verificar que el producto existe
    try:
        if tipo == 'bicicleta':
            producto = Bicicleta.objects.get(id=id)
        elif tipo == 'accesorio':
            producto = Accesorio.objects.get(id=id)
        elif tipo == 'repuesto':
            producto = Repuesto.objects.get(id=id)
    except:
        messages.error(request, 'Producto no encontrado.')
        return redirect('master')
    
    # Agregar o actualizar en el carrito
    item, created = CarritoItem.objects.get_or_create(
        usuario=request.user,
        tipo_producto=tipo,
        producto_id=id,
        defaults={'cantidad': 1}
    )
    
    if not created:
        item.cantidad += 1
        item.save()
        messages.success(request, f'Se agregó otra unidad de "{producto.nombre}" al carrito.')
    else:
        messages.success(request, f'"{producto.nombre}" fue agregado al carrito.')
    
    # Redirigir de vuelta al producto o al carrito según el parámetro
    if request.GET.get('redirect') == 'carrito':
        return redirect('carrito')
    return redirect('producto_detalle', tipo=tipo, id=id)


def eliminar_del_carrito(request, item_id):
    """Vista para eliminar un item del carrito"""
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    try:
        item = CarritoItem.objects.get(id=item_id, usuario=request.user)
        producto = item.get_producto()
        item.delete()
        messages.success(request, f'"{producto.nombre}" fue eliminado del carrito.')
    except CarritoItem.DoesNotExist:
        messages.error(request, 'Item no encontrado.')
    
    return redirect('carrito')


def actualizar_cantidad_carrito(request, item_id):
    """Vista para actualizar la cantidad de un item en el carrito"""
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    if request.method == 'POST':
        try:
            item = CarritoItem.objects.get(id=item_id, usuario=request.user)
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            if nueva_cantidad > 0:
                item.cantidad = nueva_cantidad
                item.save()
                messages.success(request, 'Cantidad actualizada.')
            else:
                item.delete()
                messages.success(request, 'Producto eliminado del carrito.')
        except CarritoItem.DoesNotExist:
            messages.error(request, 'Item no encontrado.')
        except ValueError:
            messages.error(request, 'Cantidad no válida.')
    
    return redirect('carrito')


def comprar_ahora(request, tipo, id):
    """Vista para comprar directamente un producto"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    # Agregar al carrito
    agregar_al_carrito(request, tipo, id)
    
    # Redirigir al carrito
    return redirect('carrito')


def vaciar_carrito(request):
    """Vista para vaciar todo el carrito"""
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    if request.method == 'POST':
        CarritoItem.objects.filter(usuario=request.user).delete()
        messages.success(request, 'El carrito ha sido vaciado.')
    
    return redirect('carrito')


def proceder_al_pago(request):
    """Vista para proceder al pago"""
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    items = CarritoItem.objects.filter(usuario=request.user)
    
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito')
    
    # Aquí implementarías la lógica de pago
    # Por ahora, solo mostramos un mensaje de éxito
    
    subtotal = sum(item.get_subtotal() for item in items)
    messages.success(request, f'¡Compra realizada exitosamente! Total: ${subtotal}')
    
    # Vaciar el carrito después de la compra
    items.delete()
    
    return redirect('master')


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


def producto_detalle(request, tipo, id):
    """Vista para mostrar el detalle de un producto"""
    
    if tipo == 'bicicleta':
        producto = get_object_or_404(Bicicleta, id=id)
        tipo_producto = 'Bicicleta'
        tipo_url = 'bicicletas'
        productos_relacionados = Bicicleta.objects.exclude(id=id).order_by('?')[:4]
        
    elif tipo == 'accesorio':
        producto = get_object_or_404(Accesorio, id=id)
        tipo_producto = 'Accesorio'
        tipo_url = 'accesorios'
        productos_relacionados = Accesorio.objects.exclude(id=id).order_by('?')[:4]
        
    elif tipo == 'repuesto':
        producto = get_object_or_404(Repuesto, id=id)
        tipo_producto = 'Repuesto'
        tipo_url = 'repuestos'
        productos_relacionados = Repuesto.objects.exclude(id=id).order_by('?')[:4]
        
    else:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')
    
    context = {
        'producto': producto,
        'tipo_producto': tipo_producto,
        'tipo_url': tipo_url,
        'productos_relacionados': productos_relacionados,
    }
    
    return render(request, 'vistaProducto.html', context)