from django.shortcuts import render, redirect
from django.contrib.auth import logout
# Eliminamos login_required porque valida contra la BD local, usaremos validación de sesión
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from .api_client import APIClient, get_api_client, save_token_to_session, clear_token_from_session
from decimal import Decimal
import requests
import json

def inicioPage(request):
    # Validamos contra la sesión, no contra request.user (BD local)
    if request.session.get('authenticated'):
        return redirect('master')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', 'master')

        api_client = APIClient()
        response = api_client.login(username, password)

        if response['success']:
            token = response['data'].get('token')
            save_token_to_session(request, token)
            
            # Guardamos el estado en la sesión
            request.session['authenticated'] = True
            request.session['username'] = username
            request.session['user_data'] = response['data'].get('user', {})
            
            nombre = response['data'].get('user', {}).get('first_name') or username
            messages.success(request, f'¡Bienvenido de nuevo, {nombre}!')
            return redirect(next_url)
        else:
            error_msg = response.get('error', {})
            if isinstance(error_msg, dict):
                error_msg = error_msg.get('detail', 'Credenciales incorrectas')
            messages.error(request, f'Error: {error_msg}')

    return render(request, 'inicioSesion.html')


def registroPage(request):
    # Validamos contra la sesión
    if request.session.get('authenticated'):
        return redirect('master')

    if request.method == 'POST':
        user_data = {
            'nombre': request.POST.get('nombre', '').strip(),
            'apellido': request.POST.get('apellido', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'rut': request.POST.get('rut', '').strip(),
            'password': request.POST.get('password', ''),
            'password2': request.POST.get('password2', ''),
        }
        next_url = request.POST.get('next', 'master')

        if not all([user_data['nombre'], user_data['username'], user_data['email'], 
                    user_data['rut'], user_data['password'], user_data['password2']]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'registro.html')

        if user_data['password'] != user_data['password2']:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html')

        api_data = {
            'username': user_data['username'],
            'email': user_data['email'],
            'password': user_data['password'],
            'password2': user_data['password2'],
            'first_name': user_data['nombre'],
            'last_name': user_data['apellido'],
            'rut': user_data['rut']
        }

        api_client = APIClient()
        response = api_client.register(api_data)

        if response['success']:
            login_response = api_client.login(user_data['username'], user_data['password'])
            
            if login_response['success']:
                token = login_response['data'].get('token')
                save_token_to_session(request, token)
                request.session['authenticated'] = True
                request.session['username'] = user_data['username']
                request.session['user_data'] = login_response['data'].get('user', {})
                
                messages.success(request, f'¡Bienvenido, {user_data["nombre"]}! Tu cuenta ha sido creada exitosamente.')
                return redirect(next_url)
        else:
            error_data = response.get('error', {})
            if isinstance(error_data, dict):
                for field, errors in error_data.items():
                    if isinstance(errors, list):
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                    else:
                        messages.error(request, f'{field}: {errors}')
            else:
                messages.error(request, f'Error: {error_data}')

    return render(request, 'registro.html')


def logoutUser(request):
    api_client = get_api_client(request)
    # Intentamos logout en API, pero limpiamos sesión local de todas formas
    try:
        api_client.logout()
    except:
        pass
    
    clear_token_from_session(request)
    if 'authenticated' in request.session:
        del request.session['authenticated']
    if 'username' in request.session:
        del request.session['username']
    if 'user_data' in request.session:
        del request.session['user_data']
    
    # Limpieza de sesión de Django por seguridad
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    
    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
        return redirect(next_url)
    return redirect('master')


def BicicletasListView(request):
    api_client = get_api_client(request)
    
    params = {}
    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro:
        params['tipo'] = tipo_filtro
    
    marca_filtro = request.GET.get('marca', '').strip()
    if marca_filtro:
        params['marca'] = marca_filtro
    
    ordenar = request.GET.get('ordenar', '')
    if ordenar:
        params['ordering'] = ordenar
    
    response = api_client.get_bicicletas(params=params)
    
    bicicletas = []
    tipos_disponibles = []
    marcas_disponibles = []
    
    if response['success']:
        data = response['data']
        if isinstance(data, dict) and 'results' in data:
            bicicletas = data['results']
        else:
            bicicletas = data
        
        tipos_set = set()
        marcas_set = set()
        for bici in bicicletas:
            if bici.get('tipo'):
                tipos_set.add(bici['tipo'])
            if bici.get('marca'):
                marcas_set.add(bici['marca'])
        
        tipos_disponibles = sorted(tipos_set)
        marcas_disponibles = sorted(marcas_set)
    else:
        # Si falla, enviamos lista vacía para no romper la vista
        pass 
    
    context = {
        'bicicletas': bicicletas,
        'tipos_disponibles': tipos_disponibles,
        'marcas_disponibles': marcas_disponibles,
    }
    
    return render(request, 'bicicletas.html', context)


def RepuestosListView(request):
    api_client = get_api_client(request)
    
    params = {}
    ordenar = request.GET.get('ordenar', '')
    if ordenar:
        params['ordering'] = ordenar
    
    response = api_client.get_repuestos(params=params)
    
    repuestos = []
    if response['success']:
        data = response['data']
        if isinstance(data, dict) and 'results' in data:
            repuestos = data['results']
        else:
            repuestos = data
    
    return render(request, 'repuestos.html', {'repuestos': repuestos})


def AccesoriosListView(request):
    api_client = get_api_client(request)
    
    params = {}
    ordenar = request.GET.get('ordenar', '')
    if ordenar:
        params['ordering'] = ordenar
    
    response = api_client.get_accesorios(params=params)
    
    accesorios = []
    if response['success']:
        data = response['data']
        if isinstance(data, dict) and 'results' in data:
            accesorios = data['results']
        else:
            accesorios = data
    
    return render(request, 'accesorios.html', {'accesorios': accesorios})


def Buscar(request):
    query = request.GET.get('q', '').strip()
    ordenar = request.GET.get('ordenar', '')
    
    bicicletas = []
    repuestos = []
    accesorios = []
    total_resultados = 0
    
    if query:
        api_client = get_api_client(request)
        params = {'q': query}
        if ordenar:
            params['ordering'] = ordenar
        
        response = api_client.buscar_productos(query, params=params)
        
        if response['success']:
            data = response['data']
            bicicletas = data.get('bicicletas', [])
            repuestos = data.get('repuestos', [])
            accesorios = data.get('accesorios', [])
            total_resultados = len(bicicletas) + len(repuestos) + len(accesorios)
        else:
            messages.error(request, 'Error al realizar la búsqueda.')
    
    context = {
        'query': query,
        'bicicletas': bicicletas,
        'repuestos': repuestos,
        'accesorios': accesorios,
        'total_resultados': total_resultados
    }
    
    return render(request, 'buscar.html', context)


class MasterListView(ListView):
    template_name = 'master.html'
    context_object_name = 'productos'
    
    def get_queryset(self):
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_client = get_api_client(self.request)
        
        bicicletas_response = api_client.get_bicicletas()
        accesorios_response = api_client.get_accesorios()
        repuestos_response = api_client.get_repuestos()
        
        context['bicicletas'] = []
        context['accesorios'] = []
        context['repuestos'] = []
        
        if bicicletas_response['success']:
            data = bicicletas_response['data']
            bicicletas = data['results'] if isinstance(data, dict) and 'results' in data else data
            context['bicicletas'] = bicicletas[:4]
        
        if accesorios_response['success']:
            data = accesorios_response['data']
            accesorios = data['results'] if isinstance(data, dict) and 'results' in data else data
            context['accesorios'] = accesorios[:4]
        
        if repuestos_response['success']:
            data = repuestos_response['data']
            repuestos = data['results'] if isinstance(data, dict) and 'results' in data else data
            context['repuestos'] = repuestos[:4]
        
        return context


# Eliminamos @login_required y usamos validación manual de sesión
def carrito(request):
    if not request.session.get('authenticated'):
        messages.warning(request, 'Debes iniciar sesión para ver tu carrito.')
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    response = api_client.get_carrito()
    
    items = []
    subtotal = 0
    total = 0
    total_items = 0
    
    if response['success']:
        data = response['data']
        items = data.get('items', [])
        subtotal = data.get('subtotal', 0)
        total = data.get('total', 0)
        total_items = sum(item.get('cantidad', 0) for item in items)
    else:
        # No mostrar error si el carrito está vacío o es nuevo
        pass
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'total': total,
        'total_items': total_items
    }
    
    return render(request, 'carrito.html', context)


def agregar_al_carrito(request, tipo, id):
    if not request.session.get('authenticated'):
        messages.warning(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    tipos_validos = ['bicicleta', 'repuesto', 'accesorio']
    if tipo not in tipos_validos:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')
    
    api_client = get_api_client(request)
    response = api_client.agregar_al_carrito(tipo, id)
    
    if response['success']:
        messages.success(request, 'Producto agregado al carrito exitosamente.')
    else:
        error_msg = response.get('error', 'No se pudo agregar el producto.')
        if isinstance(error_msg, dict):
            error_msg = error_msg.get('detail', 'Error al agregar al carrito')
        messages.error(request, f'Error: {error_msg}')
    
    if request.GET.get('redirect') == 'carrito':
        return redirect('carrito')
    return redirect('producto_detalle', tipo=tipo, id=id)


def eliminar_del_carrito(request, item_id):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    response = api_client.eliminar_del_carrito(item_id)
    
    if response['success']:
        messages.success(request, 'Producto eliminado del carrito.')
    else:
        messages.error(request, 'No se pudo eliminar el producto.')
    
    return redirect('carrito')


def actualizar_cantidad_carrito(request, item_id):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            if nueva_cantidad > 0:
                api_client = get_api_client(request)
                response = api_client.actualizar_cantidad_carrito(item_id, nueva_cantidad)
                
                if response['success']:
                    messages.success(request, 'Cantidad actualizada.')
                else:
                    messages.error(request, 'No se pudo actualizar la cantidad.')
            else:
                return eliminar_del_carrito(request, item_id)
        except ValueError:
            messages.error(request, 'Cantidad no válida.')
    
    return redirect('carrito')


def comprar_ahora(request, tipo, id):
    if not request.session.get('authenticated'):
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect(f'/inicioSesion/?next=/producto/{tipo}/{id}/')
    
    agregar_al_carrito(request, tipo, id)
    return redirect('carrito')


def vaciar_carrito(request):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    if request.method == 'POST':
        api_client = get_api_client(request)
        response = api_client.vaciar_carrito()
        
        if response['success']:
            messages.success(request, 'El carrito ha sido vaciado.')
        else:
            messages.error(request, 'No se pudo vaciar el carrito.')
    
    return redirect('carrito')


def proceder_al_pago(request):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    response = api_client.proceder_al_pago()
    
    if response['success']:
        data = response['data']
        total = data.get('total', 0)
        messages.success(request, f'¡Compra realizada exitosamente! Total: ${int(total):,}'.replace(',', '.'))
        return redirect('master')
    else:
        error_msg = response.get('error', 'Error al procesar el pago')
        if isinstance(error_msg, dict):
            error_msg = error_msg.get('detail', 'Error al procesar el pago')
        messages.error(request, f'Error: {error_msg}')
        return redirect('carrito')


def agendar_cita(request):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    user_data = request.session.get('user_data', {})
    
    if request.method == 'POST':
        bici_data = {
            'marca': request.POST.get('bike_brand', '').strip(),
            'color': request.POST.get('bike_color', '').strip(),
            'tipo': request.POST.get('bike_type', '').strip(),
            'anio': request.POST.get('bike_year', '').strip() or None,
            'notas_adicionales': request.POST.get('additional_notes', '').strip()
        }
        
        if not all([bici_data['marca'], bici_data['color'], bici_data['tipo']]):
            messages.error(request, 'Debes completar marca, color y tipo de bicicleta.')
            return redirect('registrobici')
        
        api_client = get_api_client(request)
        response = api_client.registrar_bicicleta_cliente(bici_data)
        
        if response['success']:
            messages.success(request, '¡Tu bicicleta ha sido registrada exitosamente!')
            return redirect('mantenimiento')
        else:
            error_msg = response.get('error', 'Error al registrar')
            if isinstance(error_msg, dict):
                for field, errors in error_msg.items():
                    if isinstance(errors, list):
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                    else:
                        messages.error(request, f'{field}: {errors}')
            else:
                messages.error(request, f'Error: {error_msg}')
    
    context = {
        # Pasamos user_data como 'user' para que el template renderice los datos
        'user': user_data,
        'cliente': user_data
    }
    
    return render(request, 'registrobici.html', context)


def mantemientoPage(request):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    
    servicios_response = api_client.get_servicios_mantenimiento()
    servicios = []
    if servicios_response['success']:
        servicios = servicios_response['data']
    
    bicicletas_response = api_client.get_bicicletas_cliente()
    bicicleta = None
    if bicicletas_response['success']:
        bicicletas = bicicletas_response['data']
        if isinstance(bicicletas, list) and len(bicicletas) > 0:
            bicicleta = bicicletas[-1]
    
    if not bicicleta:
        messages.error(request, 'Debes registrar tu bicicleta primero.')
        return redirect('registrobici')
    
    if request.method == 'POST':
        servicios_ids = request.POST.getlist('servicios')
        
        if not servicios_ids:
            messages.error(request, 'Debes seleccionar al menos un servicio.')
        else:
            orden_data = {
                'bicicleta': bicicleta['id'],
                'servicios_ids': [int(sid) for sid in servicios_ids],
                'estado': 'pendiente'
            }
            
            response = api_client.crear_orden_mantenimiento(orden_data)
            
            if response['success']:
                orden = response['data']
                total = orden.get('total', 0)
                total_formateado = f"${int(total):,}".replace(',', '.')
                messages.success(request, f'¡Orden #{orden["id"]} creada exitosamente! Total: {total_formateado}')
                return redirect('master')
            else:
                error_msg = response.get('error', 'Error al crear la orden')
                messages.error(request, f'Error: {error_msg}')
    
    context = {
        'user': request.session.get('user_data', {}),
        'cliente': request.session.get('user_data', {}),
        'bicicleta': bicicleta,
        'servicios': servicios
    }
    
    return render(request, 'mantenimiento.html', context)


def historialMantenimientosPage(request):
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    response = api_client.get_ordenes_mantenimiento()
    
    ordenes = []
    if response['success']:
        ordenes = response['data']
        if isinstance(ordenes, dict) and 'results' in ordenes:
            ordenes = ordenes['results']
    
    return render(request, 'historial_mantenimientos.html', {
        'user': request.session.get('user_data', {}),
        'ordenes': ordenes
    })


def finalizar_orden(request):
    if not request.session.get('authenticated'):
        return JsonResponse({'success': False, 'error': 'No autenticado.'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no válido.'}, status=405)
    
    try:
        data = json.loads(request.body)
        servicios_ids = data.get('servicios', [])
        
        if not servicios_ids:
            return JsonResponse({'success': False, 'error': 'Debes seleccionar servicios.'})
        
        api_client = get_api_client(request)
        bicicletas_response = api_client.get_bicicletas_cliente()
        
        if not bicicletas_response['success']:
            return JsonResponse({'success': False, 'error': 'No se encontró bicicleta registrada.'})
        
        bicicletas = bicicletas_response['data']
        if not bicicletas:
            return JsonResponse({'success': False, 'error': 'No tienes bicicletas registradas.'})
        
        bicicleta_id = bicicletas[-1]['id']
        
        orden_data = {
            'bicicleta': bicicleta_id,
            'servicios_ids': servicios_ids,
            'estado': 'pendiente'
        }
        
        response = api_client.crear_orden_mantenimiento(orden_data)
        
        if response['success']:
            orden = response['data']
            return JsonResponse({
                'success': True,
                'orden_id': orden['id'],
                'total': orden['total']
            })
        else:
            return JsonResponse({'success': False, 'error': response.get('error', 'Error al crear orden')})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Formato JSON inválido.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})


def producto_detalle(request, tipo, id):
    tipos_validos = {
        'bicicleta': ('Bicicleta', 'bicicletas'),
        'accesorio': ('Accesorio', 'accesorios'),
        'repuesto': ('Repuesto', 'repuestos')
    }
    
    if tipo not in tipos_validos:
        messages.error(request, 'Tipo de producto no válido.')
        return redirect('master')
    
    tipo_producto, tipo_url = tipos_validos[tipo]
    
    api_client = get_api_client(request)
    
    if tipo == 'bicicleta':
        response = api_client.get_bicicleta(id)
    elif tipo == 'repuesto':
        response = api_client.get_repuesto(id)
    else:
        response = api_client.get_accesorio(id)
    
    if not response['success']:
        messages.error(request, 'Producto no encontrado.')
        return redirect('master')
    
    producto = response['data']
    
    if tipo == 'bicicleta':
        relacionados_response = api_client.get_bicicletas()
    elif tipo == 'repuesto':
        relacionados_response = api_client.get_repuestos()
    else:
        relacionados_response = api_client.get_accesorios()
    
    productos_relacionados = []
    if relacionados_response['success']:
        data = relacionados_response['data']
        todos = data['results'] if isinstance(data, dict) and 'results' in data else data
        productos_relacionados = [p for p in todos if p['id'] != id][:4]
    
    context = {
        'producto': producto,
        'tipo_producto': tipo_producto,
        'tipo_url': tipo_url,
        'productos_relacionados': productos_relacionados,
    }
    
    return render(request, 'vistaProducto.html', context)