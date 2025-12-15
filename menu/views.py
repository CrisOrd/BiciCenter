from django.shortcuts import render, redirect
from django.contrib.auth import logout
# Eliminamos login_required porque valida contra la BD local, usaremos validación de sesión
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from django.utils.http import url_has_allowed_host_and_scheme
from .api_client import APIClient, get_api_client, save_token_to_session, clear_token_from_session
from django.http import HttpResponse
from decimal import Decimal
import requests
import json
from django.conf import settings
# En menu/views.py

def inicioPage(request):
    if request.session.get('authenticated'):
        return redirect('master')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        next_url = request.POST.get('next', 'master')

        api_client = APIClient() # Aquí no necesitamos token todavía
        response = api_client.login(usuario, clave)

        token = None
        # Intentamos sacar el token de la respuesta
        if response.get('success') and 'data' in response:
            token = response['data'].get('token')
        elif 'token' in response:
            token = response['token']
        
        if token:
            # ========================================================
            # ¡ESTA ES LA LÍNEA QUE FALTABA O FALLABA!
            # Guardamos el token explícitamente en la sesión
            request.session['token'] = token  
            # ========================================================
            
            request.session['authenticated'] = True
            request.session['username'] = usuario
            
            # Recuperamos datos del perfil para que la cita no salga vacía
            # Usamos el token recién conseguido
            try:
                # Instanciamos cliente CON el token
                client_with_token = APIClient(token)
                
                # Buscamos 'usuario/' o 'users/me/' según tu API
                # Si esto falla, verifica la URL en utils.py o settings
                url_perfil = settings.API_BASE_URL + 'usuario/' 
                header_auth = {'Authorization': f'Token {token}'}
                
                user_res = requests.get(url_perfil, headers=header_auth)
                
                if user_res.status_code == 200:
                    datos = user_res.json()
                    # A veces viene en 'data', a veces directo
                    request.session['user_data'] = datos.get('data', datos)
                else:
                    request.session['user_data'] = {'first_name': usuario, 'id': None}
            except:
                 request.session['user_data'] = {'first_name': usuario, 'id': None}

            messages.success(request, f'¡Bienvenido, {usuario}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales incorrectas')

    return render(request, 'inicioSesion.html')

def registroPage(request):
    if request.session.get('authenticated'):
        return redirect('master')

    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password2')
        username = request.POST.get('username')
        
        if pass1 != pass2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registro.html')

        data = {
            'username': username,
            'email': request.POST.get('email'),
            'password': pass1,
            'first_name': request.POST.get('nombre'),
            'last_name': request.POST.get('apellido'),
            'rut': request.POST.get('rut'),
            'telefono': request.POST.get('telefono', ''),
            'direccion': request.POST.get('direccion', ''),
        }

        api_client = APIClient()
        response = api_client.register(data) 

        if response.get('success') or response.get('id'):
            messages.success(request, 'Registro exitoso. Iniciando sesión...')
            
            # AUTO-LOGIN
            login_res = api_client.login(username, pass1)
            token = None
            if login_res.get('success') and 'data' in login_res:
                token = login_res['data'].get('token')
            
            if token:
                # ====================================================
                # GUARDADO OBLIGATORIO DEL TOKEN
                request.session['token'] = token
                # ====================================================
                request.session['authenticated'] = True
                request.session['username'] = username
                
                # Intentamos obtener datos del usuario recién creado
                try:
                    header_auth = {'Authorization': f'Token {token}'}
                    url_perfil = settings.API_BASE_URL + 'usuario/'
                    user_res = requests.get(url_perfil, headers=header_auth)
                    if user_res.status_code == 200:
                        request.session['user_data'] = user_res.json().get('data', user_res.json())
                    else:
                        request.session['user_data'] = {'first_name': username, 'id': response.get('id')}
                except:
                    pass

                return redirect('master')
            
            return redirect('inicioSesion')
        else:
            errores = response.get('error', 'Error en el registro')
            messages.error(request, f"Error: {errores}")

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
# En menu/views.py (Copia y pega esto al final)

# ==========================================
# 1. FUNCIÓN DEL CARRITO (Para ver productos)
# ==========================================
def carrito(request):
    if not request.session.get('authenticated'):
        messages.warning(request, 'Debes iniciar sesión.')
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    response = api_client.get_carrito()
    
    items = []
    subtotal = 0
    total = 0
    total_items = 0
    
    # Diagnóstico: ¿Qué nos está mandando la API?
    print(f"\n>>> FRONTEND RECIBIÓ: {response}")

    if response.get('success'):
        data = response.get('data')
        
        # CASO 1: Formato Nuevo (Diccionario con 'items') <- ESTE ES EL TUYO
        if isinstance(data, dict) and 'items' in data:
            items = data.get('items', [])
            subtotal = data.get('subtotal', 0)
            total = data.get('total', 0)
            
        # CASO 2: Formato Antiguo (Lista directa)
        elif isinstance(data, list):
            items = data
            for item in items:
                # Intentamos obtener precio de varias formas por seguridad
                precio = item.get('precio_unitario', 0)
                if not precio and 'producto_detalle' in item:
                    precio = item['producto_detalle'].get('precio', 0)
                
                cant = item.get('cantidad', 1)
                subtotal += float(precio) * cant
            total = subtotal

        # Calcular cantidad total de productos
        total_items = sum(int(item.get('cantidad', 0)) for item in items)
    else:
        print(">>> ERROR: La API dijo success=False o no respondió datos válidos.")

    context = {
        'items': items,
        'subtotal': subtotal,
        'total': total,
        'total_items': total_items
    }
    
    return render(request, 'carrito.html', context)


# ==========================================
# 2. AGREGAR AL CARRITO
# ==========================================
def agregar_al_carrito(request, tipo, id):
    if not request.session.get('authenticated'):
        messages.error(request, "Debes iniciar sesión para comprar.")
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    url = f"{settings.API_BASE_URL}carrito/"
    
    # Preparamos los datos
    data = {
        'tipo_producto': tipo, 
        'producto_id': id,
        'cantidad': 1
    }
    
    print(f"\n>>> INTENTANDO AGREGAR: {data}")

    try:
        # Enviamos POST a la API
        response = requests.post(url, json=data, headers=api_client.headers)
        
        print(f">>> RESPUESTA API AGREGAR: {response.status_code} - {response.text}")
        
        if response.status_code in [200, 201]:
            messages.success(request, "¡Producto agregado!")
        else:
            try:
                err = response.json().get('error', 'Error desconocido')
            except:
                err = response.text
            messages.error(request, f"No se pudo agregar: {err}")
            
    except Exception as e:
        print(f">>> ERROR CONEXIÓN: {e}")
        messages.error(request, "Error de conexión con la API.")

    return redirect('carrito')

def agregar_al_carrito(request, tipo, id):
    if not request.session.get('authenticated'):
        messages.error(request, "Debes iniciar sesión.")
        return redirect('inicioSesion')
    
    api_client = get_api_client(request)
    url = f"{settings.API_BASE_URL}carrito/"
    
    data = {
        'tipo_producto': tipo, # ej: 'bicicleta'
        'producto_id': id,     # ej: 5
        'cantidad': 1
    }
    
    print(f"\n>>> INTENTANDO AGREGAR AL CARRITO: {data}")
    
    try:
        response = requests.post(url, json=data, headers=api_client.headers)
        
        print(f">>> CÓDIGO DE ESTADO: {response.status_code}")
        print(f">>> RESPUESTA API: {response.text}") # <--- ESTO NOS DIRÁ EL ERROR REAL
        
        # Aceptamos 200 (OK) y 201 (Creado)
        if response.status_code in [200, 201]:
            messages.success(request, "¡Producto agregado al carrito!")
        else:
            # Intentamos leer el error JSON
            try:
                error_json = response.json()
                # A veces el error viene como {'usuario': ['This field is required']}
                if isinstance(error_json, dict):
                    msg = ', '.join([f"{k}: {v}" for k,v in error_json.items()])
                else:
                    msg = str(error_json)
            except:
                msg = "Error desconocido en la API."
            
            messages.error(request, f"Error API: {msg}")
            
    except Exception as e:
        print(f">>> ERROR DE CONEXIÓN: {e}")
        messages.error(request, "Error de conexión.")

    token = request.session.get('token')
    print(f"\n>>> TOKEN EN SESIÓN: {token}")  # <--- Agrega esto
    
    api_client = get_api_client(request)
    print(f">>> HEADERS A ENVIAR: {api_client.headers}") # <--- Agrega esto

    return redirect('carrito')


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
    # 1. Seguridad
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    # 2. Procesar POST
    if request.method == 'POST':
        try:
            # Obtenemos la cantidad del botón presionado
            nueva_cantidad = int(request.POST.get('cantidad'))
            
            # Validación básica antes de llamar a la API
            if nueva_cantidad < 1:
                messages.warning(request, "La cantidad mínima es 1. Usa el botón eliminar si deseas quitarlo.")
                return redirect('carrito')

            # 3. Llamar a la API
            api_client = get_api_client(request)
            
            print(f">>> ACTUALIZANDO ITEM {item_id} A CANTIDAD: {nueva_cantidad}") # Debug
            
            response = api_client.actualizar_cantidad_carrito(item_id, nueva_cantidad)
            
            if response.get('success'):
                messages.success(request, 'Carrito actualizado.')
            else:
                # Mostrar error de stock si la API se queja
                error_msg = response.get('error', 'No se pudo actualizar.')
                # Limpiamos el mensaje de error sucio de DRF si es necesario
                if isinstance(error_msg, dict): 
                    error_msg = "Stock insuficiente."
                messages.error(request, f"Error: {error_msg}")

        except ValueError:
            messages.error(request, 'Cantidad inválida.')
    
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
    # 1. Verificar sesión
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    # 2. Verificar Token
    token = request.session.get('token')
    if not token:
        messages.error(request, "Error de seguridad: No hay token. Inicia sesión de nuevo.")
        return redirect('inicioSesion')

    # 3. Obtener ID del usuario (Dueño de la bici)
    raw_data = request.session.get('user_data', {})
    user_id = raw_data.get('id')
    
    # Si por alguna razón no tenemos ID de usuario, no podemos guardar la bici
    if not user_id:
        # Intentamos recuperarlo del token si falla la sesión
        # (Esto es un parche de seguridad)
        api_temp = APIClient(token)
        try:
            resp = requests.get(settings.API_BASE_URL + 'usuario/', headers={'Authorization': f'Token {token}'})
            if resp.status_code == 200:
                user_id = resp.json().get('id') or resp.json().get('data', {}).get('id')
        except:
            pass

    if request.method == 'POST':
        # 4. LIMPIEZA DE DATOS (CRÍTICO)
        
        # Año: Convertir a entero o None (para que no falle la API)
        anio_str = request.POST.get('bike_year', '').strip()
        anio_int = None
        if anio_str.isdigit():
            anio_int = int(anio_str)

        datos_bicicleta = {
            'marca': request.POST.get('bike_brand'),
            'color': request.POST.get('bike_color'),
            'tipo': request.POST.get('bike_type'),
            'anio': anio_int, # Enviamos número o None, NUNCA texto vacío
            'notas_adicionales': request.POST.get('additional_notes', ''),
            'cliente': user_id 
        }

        # --- DIAGNÓSTICO EN CONSOLA ---
        print("\n" + "*"*40)
        print(">>> DATOS A ENVIAR A LA API:")
        print(datos_bicicleta)
        
        # 5. ENVIAR A LA API
        api_client = APIClient(token)
        response = api_client.registrar_bicicleta_cliente(datos_bicicleta)
        
        print(">>> RESPUESTA DE LA API:")
        print(response)
        print("*"*40 + "\n")
        # -----------------------------

        if response.get('success') or (isinstance(response, dict) and 'id' in response):
            messages.success(request, '¡Bicicleta registrada correctamente!')
            return redirect('mantenimiento')
        else:
            # Mostramos el error exacto en pantalla para que sepas qué falta
            errores = response.get('error', response)
            
            # Si el error es "cliente: null", es que falta el ID
            if isinstance(errores, dict) and 'cliente' in errores:
                messages.error(request, "Error: No se pudo identificar al usuario propietario.")
            else:
                messages.error(request, f"La API rechazó los datos: {errores}")

    # Datos para mostrar en el formulario (solo visual)
    cliente_data = {
        'nombre': raw_data.get('first_name'),
        'apellido': raw_data.get('last_name'),
        'rut': raw_data.get('rut'),
        'email': raw_data.get('email')
    }
    
    return render(request, 'registrobici.html', {'cliente': cliente_data})

# En menu/views.py

# En menu/views.py

# En menu/views.py

def mantemientoPage(request):
    # 1. Seguridad
    if not request.session.get('authenticated'):
        return redirect('inicioSesion')
    
    # 2. Token
    token = request.session.get('token')
    if not token:
        messages.error(request, "Sesión inválida. Reingresa.")
        return redirect('inicioSesion')

    api_client = APIClient(token) 
    user_data = request.session.get('user_data', {})
    
    # 3. Datos previos (Servicios y Bici)
    servicios = []
    resp_servicios = api_client.get_servicios_mantenimiento()
    if resp_servicios.get('success'):
        servicios = resp_servicios.get('data', [])

    bicicleta = None
    resp_bicis = api_client.get_bicicletas_cliente()
    if resp_bicis.get('success'):
        lista = resp_bicis.get('data', [])
        if lista:
            bicicleta = lista[-1]

    if not bicicleta:
        messages.warning(request, "No se encontraron bicicletas. Intenta registrarla nuevamente.")

    # 4. Procesar Formulario (POST)
    if request.method == 'POST':
        if not bicicleta:
             messages.error(request, "Error: No hay bicicleta asociada.")
             return redirect('registrobici')

        servicios_seleccionados = request.POST.getlist('servicios')
        
        if not servicios_seleccionados:
            messages.error(request, 'Selecciona al menos un servicio.')
        else:
            ids_servicios = [int(id_s) for id_s in servicios_seleccionados]
            
            orden_data = {
                'cliente': user_data.get('id'),
                'bicicleta': bicicleta['id'],
                'servicios_ids': ids_servicios,
                'estado': 'pendiente'
            }
            
            response = api_client.crear_orden_mantenimiento(orden_data)
            
            if response.get('success') or (isinstance(response, dict) and 'id' in response):
                messages.success(request, '¡Orden creada exitosamente! Pronto te contactaremos.')
                
                # =======================================================
                # CAMBIO: Redirige a la página principal (Master)
                # =======================================================
                return redirect('master') 
                
            else:
                 messages.error(request, f"Error API: {response}")

    context = {
        'user': user_data,
        'cliente': user_data,
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