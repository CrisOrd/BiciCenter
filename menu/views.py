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


def aplicar_ordenamiento(queryset, ordenar_por):
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
    if request.user.is_authenticated:
        return redirect('master')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
            return redirect('master')  # Redirige al master
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'inicioSesion.html')

def registroPage(request):
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
                messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta ha sido creada exitosamente.')
                return redirect('master')  # Redirige al master
            else:
                messages.success(request, 'Cuenta creada exitosamente. Por favor inicia sesión.')
                return redirect('inicioSesion')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')
    return render(request, 'registro.html')

def logoutUser(request):
    next_url = request.GET.get('next', 'master')
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect(next_url)

def BicicletasListView(request):
    bicicletas = Bicicleta.objects.all()
    if marca := request.GET.get('marca', '').strip():
        bicicletas = bicicletas.filter(marca__iexact=marca)
    orden_map = {
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'modelo_asc': 'modelo',
        'modelo_desc': '-modelo',
        'marca_asc': 'marca',
        'marca_desc': '-marca',
    } 
    if orden := orden_map.get(request.GET.get('ordenar', '')):
        bicicletas = bicicletas.order_by(orden)   
    context = {
        'bicicletas': bicicletas,
        'marcas_disponibles': Bicicleta.objects.exclude(marca='').values_list('marca', flat=True).distinct().order_by('marca'),
    }
    
    return render(request, 'bicicletas.html', context)

def RepuestosListView(request):
    repuestos = Repuesto.objects.all()
    ordenar = request.GET.get('ordenar', '')
    repuestos = aplicar_ordenamiento(repuestos, ordenar)
    
    return render(request, 'repuestos.html', {'repuestos': repuestos})


def AccesoriosListView(request):
    accesorios = Accesorio.objects.all()
    ordenar = request.GET.get('ordenar', '')
    accesorios = aplicar_ordenamiento(accesorios, ordenar)
    
    return render(request, 'accesorios.html', {'accesorios': accesorios})


def Buscar(request):
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
            Q(marca__icontains=query)  
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
    model = Bicicleta
    template_name = 'master.html'
    context_object_name = 'productos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bicicletas'] = Bicicleta.objects.all()[:4]
        context['accesorios'] = Accesorio.objects.all()[:4]
        context['repuestos'] = Repuesto.objects.all()[:4]
        return context

def carrito(request):
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
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
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    if tipo not in ['bicicleta', 'accesorio', 'repuesto']:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')
    
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
    
    if request.GET.get('redirect') == 'carrito':
        return redirect('carrito')
    return redirect('producto_detalle', tipo=tipo, id=id)


def eliminar_del_carrito(request, item_id):
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
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    agregar_al_carrito(request, tipo, id)
    
    return redirect('carrito')


def vaciar_carrito(request):
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    
    if request.method == 'POST':
        CarritoItem.objects.filter(usuario=request.user).delete()
        messages.success(request, 'El carrito ha sido vaciado.')
    
    return redirect('carrito')


def proceder_al_pago(request):
    if not request.user.is_authenticated:
        return redirect('inicioSesion')
    items = CarritoItem.objects.filter(usuario=request.user)
    
    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito')

    subtotal = sum(item.get_subtotal() for item in items)
    messages.success(request, f'¡Compra realizada exitosamente! Total: ${subtotal}')
    
    items.delete()
    
    return redirect('master')

@login_required
def agendar_cita(request):
    user = request.user
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
            rut_from_form = request.POST.get('rut')
            if rut_from_form and not cliente_data.rut:
                cliente_data.rut = rut_from_form
                cliente_data.save()

            BicicletaCliente.objects.create(
                cliente=cliente_data,
                marca=request.POST.get('bike_brand'),
                color=request.POST.get('bike_color'),
                tipo=request.POST.get('bike_type'),
                anio=int(request.POST.get('bike_year')) if request.POST.get('bike_year') else None,
                notas_adicionales=request.POST.get('additional_notes', '')
            )
            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al registrar: {e}')
    
    return render(request, 'registrobici.html', {'user': user, 'cliente': cliente_data})

@login_required
def mantemientoPage(request):
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
    user = request.user
    try:
        cliente = Cliente.objects.get(email=user.email)
        ordenes = OrdenMantenimiento.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    except Cliente.DoesNotExist:
        ordenes = [] 
    return render(request, 'historial_mantenimientos.html', {'user': user, 'ordenes': ordenes})


@login_required
def finalizar_orden(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no válido.'}, status=405)
    try:
        cliente = Cliente.objects.get(email=request.user.email)
        bicicleta = BicicletaCliente.objects.filter(cliente=cliente).first()
        
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
    except Cliente.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No se encontró el cliente.'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato JSON inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})

def producto_detalle(request, tipo, id):
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