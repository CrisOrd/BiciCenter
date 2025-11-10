from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils.http import url_has_allowed_host_and_scheme
from .models import (
    Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente,
    ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento,
    CarritoItem
)
from decimal import Decimal
import json
import datetime
import re


def aplicar_ordenamiento(queryset, ordenar_por):
    """Aplica ordenamiento a un queryset basado en el parámetro."""
    orden_map = {
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'modelo_asc': 'modelo',
        'modelo_desc': '-modelo',
    }
    return queryset.order_by(orden_map.get(ordenar_por, 'id'))


def inicioPage(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        return redirect('master')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', 'master')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            nombre = user.first_name or user.username
            messages.success(request, f'¡Bienvenido de nuevo, {nombre}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'inicioSesion.html')


def registroPage(request):
    """Vista de registro de usuarios."""
    if request.user.is_authenticated:
        return redirect('master')

    if request.method == 'POST':
        # Obtener y limpiar datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        next_url = request.POST.get('next', 'master')

        # Validaciones básicas
        if not all([nombre, apellido, username, email, rut, password, password2]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'registro.html')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html')

        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'registro.html')

        # Validar duplicados
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return render(request, 'registro.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'registro.html')

        # Validar y limpiar RUT
        rut_clean = rut.replace('.', '').replace('-', '').upper()
        if len(rut_clean) < 8:
            messages.error(request, 'RUT inválido.')
            return render(request, 'registro.html')

        rut_formatted = f"{rut_clean[:-1]}-{rut_clean[-1]}"

        if Cliente.objects.filter(rut=rut_formatted).exists():
            messages.error(request, 'El RUT ya se encuentra registrado.')
            return render(request, 'registro.html')

        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )

            # Crear cliente
            Cliente.objects.create(
                rut=rut_formatted,
                nombre=nombre,
                apellido=apellido,
                email=email
            )

            # Autenticar e iniciar sesión automáticamente
            user_auth = authenticate(request, username=username, password=password)
            if user_auth:
                login(request, user_auth)
                messages.success(request, f'¡Bienvenido, {nombre}! Tu cuenta ha sido creada exitosamente.')
                return redirect(next_url)

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {str(e)}')

    return render(request, 'registro.html')


def logoutUser(request):
    """Cierra la sesión del usuario."""
    next_url = request.GET.get('next')
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return redirect(next_url)
    return redirect('master')


def BicicletasListView(request):
    """Lista de bicicletas con filtros."""
    bicicletas = Bicicleta.objects.all()

    # Filtros
    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro:
        bicicletas = bicicletas.filter(tipo=tipo_filtro)

    marca_filtro = request.GET.get('marca', '').strip()
    if marca_filtro:
        bicicletas = bicicletas.filter(marca__iexact=marca_filtro)

    # Ordenamiento
    ordenar = request.GET.get('ordenar', '')
    bicicletas = aplicar_ordenamiento(bicicletas, ordenar)

    context = {
        'bicicletas': bicicletas,
        'tipos_disponibles': Bicicleta.objects.values_list('tipo', flat=True).distinct(),
        'marcas_disponibles': Bicicleta.objects.exclude(marca='').values_list('marca', flat=True).distinct().order_by('marca'),
    }

    return render(request, 'bicicletas.html', context)


def RepuestosListView(request):
    """Lista de repuestos."""
    repuestos = Repuesto.objects.all()
    ordenar = request.GET.get('ordenar', '')
    repuestos = aplicar_ordenamiento(repuestos, ordenar)

    return render(request, 'repuestos.html', {'repuestos': repuestos})


def AccesoriosListView(request):
    """Lista de accesorios."""
    accesorios = Accesorio.objects.all()
    ordenar = request.GET.get('ordenar', '')
    accesorios = aplicar_ordenamiento(accesorios, ordenar)

    return render(request, 'accesorios.html', {'accesorios': accesorios})


def Buscar(request):
    """Búsqueda global de productos."""
    query = request.GET.get('q', '').strip()
    ordenar = request.GET.get('ordenar', '')

    bicicletas = repuestos = accesorios = []

    if query:
        # Búsqueda en bicicletas
        bicicletas = Bicicleta.objects.filter(
            Q(nombre__icontains=query) |
            Q(modelo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(tipo__icontains=query) |
            Q(marca__icontains=query)
        )

        # Búsqueda en repuestos
        repuestos = Repuesto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )

        # Búsqueda en accesorios
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


class MasterListView(ListView):
    """Página principal con productos destacados."""
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
def carrito(request):
    """Vista del carrito de compras."""
    items = CarritoItem.objects.filter(usuario=request.user)
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
    """Agregar producto al carrito."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')

    # Validar tipo de producto
    modelos = {
        'bicicleta': Bicicleta,
        'accesorio': Accesorio,
        'repuesto': Repuesto
    }

    if tipo not in modelos:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')

    try:
        producto = modelos[tipo].objects.get(id=id)
    except modelos[tipo].DoesNotExist:
        messages.error(request, 'Producto no encontrado.')
        return redirect('master')

    # Agregar o actualizar item en carrito
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

    # Redireccionar
    if request.GET.get('redirect') == 'carrito':
        return redirect('carrito')
    return redirect('producto_detalle', tipo=tipo, id=id)


@login_required
def eliminar_del_carrito(request, item_id):
    """Eliminar item del carrito."""
    try:
        item = CarritoItem.objects.get(id=item_id, usuario=request.user)
        producto = item.get_producto()
        item.delete()
        if producto:
            messages.success(request, f'"{producto.nombre}" fue eliminado del carrito.')
        else:
            messages.success(request, 'Producto eliminado del carrito.')
    except CarritoItem.DoesNotExist:
        messages.error(request, 'Item no encontrado.')

    return redirect('carrito')


@login_required
def actualizar_cantidad_carrito(request, item_id):
    """Actualizar cantidad de un item en el carrito."""
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
    """Comprar producto directamente."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    agregar_al_carrito(request, tipo, id)
    return redirect('carrito')


@login_required
def vaciar_carrito(request):
    """Vaciar todo el carrito."""
    if request.method == 'POST':
        CarritoItem.objects.filter(usuario=request.user).delete()
        messages.success(request, 'El carrito ha sido vaciado.')

    return redirect('carrito')


@login_required
def proceder_al_pago(request):
    """Procesar pago y finalizar compra."""
    items = CarritoItem.objects.filter(usuario=request.user)

    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito')

    subtotal = sum(item.get_subtotal() for item in items)
    messages.success(request, f'¡Compra realizada exitosamente! Total: ${int(subtotal):,}'.replace(',', '.'))

    items.delete()
    return redirect('master')


@login_required
def agendar_cita(request):
    """Registrar bicicleta del cliente."""
    user = request.user

    # Obtener o crear cliente
    cliente, created = Cliente.objects.get_or_create(
        email=user.email,
        defaults={
            'rut': '',
            'nombre': user.first_name or '',
            'apellido': user.last_name or '',
        }
    )

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        rut_from_form = request.POST.get('rut', '').strip()
        bike_brand = request.POST.get('bike_brand', '').strip()
        bike_color = request.POST.get('bike_color', '').strip()
        bike_type = request.POST.get('bike_type', '').strip()
        bike_year = request.POST.get('bike_year', '').strip()
        additional_notes = request.POST.get('additional_notes', '').strip()

        # Validar campos obligatorios
        if not all([bike_brand, bike_color, bike_type]):
            messages.error(request, 'Debes completar marca, color y tipo de bicicleta.')
            return redirect('registrobici')

        # Validar año
        anio_val = None
        if bike_year:
            try:
                anio_val = int(bike_year)
                current_year = datetime.date.today().year
                if not (1900 <= anio_val <= current_year):
                    messages.error(request, 'Año de la bicicleta fuera de rango.')
                    return redirect('registrobici')
            except ValueError:
                messages.error(request, 'Año de la bicicleta inválido.')
                return redirect('registrobici')

        # Limpiar y validar RUT
        rut_clean = ''
        if rut_from_form:
            rut_clean = rut_from_form.replace('.', '').replace('-', '').upper()
            if len(rut_clean) >= 8:
                rut_clean = f"{rut_clean[:-1]}-{rut_clean[-1]}"
            else:
                messages.error(request, 'Formato de RUT inválido.')
                return redirect('registrobici')

        try:
            # Actualizar datos del cliente si es necesario
            if nombre:
                cliente.nombre = nombre
            if apellido:
                cliente.apellido = apellido
            if rut_clean:
                cliente.rut = rut_clean
            cliente.save()

            # Crear registro de bicicleta
            BicicletaCliente.objects.create(
                cliente=cliente,
                marca=bike_brand,
                color=bike_color,
                tipo=bike_type,
                anio=anio_val,
                notas_adicionales=additional_notes
            )

            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {str(e)}')

    return render(request, 'registrobici.html', {'user': user, 'cliente': cliente})


@login_required
def mantemientoPage(request):
    """Crear orden de mantenimiento."""
    user = request.user

    # Verificar que exista cliente
    try:
        cliente = Cliente.objects.get(email=user.email)
    except Cliente.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil primero.')
        return redirect('registrobici')

    # Verificar que exista bicicleta registrada
    bicicleta = BicicletaCliente.objects.filter(cliente=cliente).last()
    if not bicicleta:
        messages.error(request, 'Debes registrar tu bicicleta primero.')
        return redirect('registrobici')

    if request.method == 'POST':
        servicios_seleccionados = request.POST.getlist('servicios')

        if not servicios_seleccionados:
            messages.error(request, 'Debes seleccionar al menos un servicio.')
        else:
            try:
                # Crear orden de mantenimiento
                orden = OrdenMantenimiento.objects.create(
                    cliente=cliente,
                    bicicleta=bicicleta,
                    estado='pendiente'
                )

                # Agregar servicios a la orden
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
                total_formateado = f"${int(orden.total):,}".replace(',', '.')
                messages.success(request, f'¡Orden #{orden.id} creada exitosamente! Total: {total_formateado}')
                return redirect('master')

            except Exception as e:
                messages.error(request, f'Error al crear la orden: {str(e)}')

    context = {
        'user': user,
        'cliente': cliente,
        'bicicleta': bicicleta,
        'servicios': ServicioMantenimiento.objects.all()
    }

    return render(request, 'mantenimiento.html', context)


@login_required
def historialMantenimientosPage(request):
    """Historial de órdenes de mantenimiento."""
    cliente = Cliente.objects.filter(email=request.user.email).first()
    ordenes = OrdenMantenimiento.objects.filter(cliente=cliente).order_by('-fecha_creacion') if cliente else []
    
    return render(request, 'historial_mantenimientos.html', {
        'user': request.user,
        'ordenes': ordenes
    })


@login_required
def finalizar_orden(request):
    """API para finalizar orden de mantenimiento (JSON)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no válido.'}, status=405)

    try:
        cliente = Cliente.objects.filter(email=request.user.email).first()
        if not cliente:
            return JsonResponse({'success': False, 'error': 'Cliente no encontrado.'})

        bicicleta = BicicletaCliente.objects.filter(cliente=cliente).first()
        if not bicicleta:
            return JsonResponse({'success': False, 'error': 'No se encontró una bicicleta registrada.'})

        data = json.loads(request.body)
        servicios_nombres = data.get('servicios', [])

        # Crear orden
        orden = OrdenMantenimiento.objects.create(
            cliente=cliente,
            bicicleta=bicicleta,
            estado='pendiente'
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

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato JSON inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})


def producto_detalle(request, tipo, id):
    """Detalle de un producto."""
    modelos = {
        'bicicleta': (Bicicleta, 'Bicicleta', 'bicicletas'),
        'accesorio': (Accesorio, 'Accesorio', 'accesorios'),
        'repuesto': (Repuesto, 'Repuesto', 'repuestos')
    }

    if tipo not in modelos:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')

    modelo, tipo_producto, tipo_url = modelos[tipo]
    producto = get_object_or_404(modelo, id=id)
    productos_relacionados = modelo.objects.exclude(id=id).order_by('?')[:4]

    context = {
        'producto': producto,
        'tipo_producto': tipo_producto,
        'tipo_url': tipo_url,
        'productos_relacionados': productos_relacionados,
    }

    return render(request, 'vistaProducto.html', context)