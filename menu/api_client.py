import requests
from django.conf import settings

class APIClient:
    def __init__(self, token=None):
        self.base_url = settings.API_BASE_URL
        self.headers = {
            'Content-Type': 'application/json'
        }
        # ESTA PARTE ES LA QUE ESTABA FALLANDO:
        if token:
            self.headers['Authorization'] = f'Token {token}'

    def login(self, username, password):
        url = f'{self.base_url}auth/login/'
        try:
            response = requests.post(url, json={'username': username, 'password': password}, headers=self.headers)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def register(self, data):
        url = f'{self.base_url}auth/register/'
        try:
            response = requests.post(url, json=data, headers=self.headers)
            return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # --- MÉTODOS DE PRODUCTOS ---
    def get_bicicletas(self, params=None):
        return self._get('bicicletas/', params)

    def get_repuestos(self, params=None):
        return self._get('repuestos/', params)

    def get_accesorios(self, params=None):
        return self._get('accesorios/', params)
    
    def get_bicicleta(self, id):
        return self._get(f'bicicletas/{id}/')

    def get_repuesto(self, id):
        return self._get(f'repuestos/{id}/')

    def get_accesorio(self, id):
        return self._get(f'accesorios/{id}/')

    def buscar_productos(self, query, params=None):
        # Esta lógica depende de tu API, asumo que tienes un endpoint de búsqueda o filtras
        # Aquí un ejemplo genérico si tuvieras un endpoint de búsqueda global
        # Si no, tendrías que buscar en cada endpoint.
        # Por ahora lo dejamos simple para que no rompa:
        return {'success': False, 'error': 'Búsqueda no implementada en APIClient'}

    # --- MÉTODOS DEL CARRITO ---
    def get_carrito(self):
        return self._get('carrito/')

    def eliminar_del_carrito(self, item_id):
        url = f'{self.base_url}carrito/{item_id}/'
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code in [200, 204]:
                return {'success': True}
            return {'success': False, 'error': 'No se pudo eliminar'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def actualizar_cantidad_carrito(self, item_id, cantidad):
        url = f'{self.base_url}carrito/{item_id}/'
        try:
            # ¡IMPORTANTE! Debe ser requests.patch, NO requests.post
            response = requests.patch(url, json={'cantidad': cantidad}, headers=self.headers)
            if response.status_code == 200:
                return {'success': True}
            # Devolvemos el error real para mostrarlo en pantalla
            return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def eliminar_del_carrito(self, item_id):
        url = f'{self.base_url}carrito/{item_id}/'
        try:
            # ¡IMPORTANTE! Debe ser requests.delete, NO requests.post
            response = requests.delete(url, headers=self.headers)
            if response.status_code in [200, 204]:
                return {'success': True}
            return {'success': False, 'error': 'No se pudo eliminar'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def proceder_al_pago(self):
        url = f'{self.base_url}carrito/pago/'
        try:
            response = requests.post(url, headers=self.headers)
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json().get('data', {})}
            return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # --- MÉTODOS DE MANTENIMIENTO ---
    def get_servicios_mantenimiento(self):
        return self._get('servicios-mantenimiento/')

    def get_bicicletas_cliente(self):
        return self._get('bicicletas-cliente/')

    def registrar_bicicleta_cliente(self, data):
        url = f'{self.base_url}bicicletas-cliente/'
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def crear_orden_mantenimiento(self, data):
        url = f'{self.base_url}ordenes-mantenimiento/'
        try:
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_ordenes_mantenimiento(self):
        return self._get('ordenes-mantenimiento/')

    # --- UTILIDAD PRIVADA PARA NO REPETIR CÓDIGO ---
    def _get(self, endpoint, params=None):
        url = f'{self.base_url}{endpoint}'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f'Error {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# --- FUNCIONES AUXILIARES (VITALES) ---

def get_api_client(request):
    # AQUÍ ES DONDE SE CONECTA EL TOKEN CON LA CLASE
    token = request.session.get('token')
    return APIClient(token)

def save_token_to_session(request, token):
    request.session['token'] = token

def clear_token_from_session(request):
    if 'token' in request.session:
        del request.session['token']