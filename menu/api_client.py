import requests
from django.conf import settings
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class APIClient:
    
    def __init__(self, token: Optional[str] = None):
        # Lee la URL desde settings.py, por defecto usa el puerto 8001
        self.base_url = getattr(settings, 'API_BASE_URL', 'http://127.0.0.1:8001/api/')
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
        }
        if self.token:
            self.headers['Authorization'] = f'Token {self.token}'
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None):
        # Asegura que la URL no tenga doble slash //
        base = self.base_url.rstrip('/')
        path = endpoint.lstrip('/')
        url = f"{base}/{path}"
        
        # Si el endpoint no termina en barra y no tiene parámetros query, se la agregamos (estándar DRF)
        if not url.endswith('/') and '?' not in url:
            url += '/'

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json(), 'status_code': response.status_code}
            elif response.status_code == 204:
                return {'success': True, 'data': None, 'status_code': response.status_code}
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = response.text
                return {
                    'success': False, 
                    'error': error_data,
                    'status_code': response.status_code
                }
        
        except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar a la API: {url}")
            return {'success': False, 'error': 'No se pudo conectar con el servidor'}
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en la petición a: {url}")
            return {'success': False, 'error': 'La petición tardó demasiado tiempo'}
        except Exception as e:
            logger.error(f"Error en petición a {url}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # --- AUTENTICACIÓN ---
    def login(self, username: str, password: str) -> Dict:
        data = {'username': username, 'password': password}
        return self._make_request('POST', 'auth/login/', data=data)
    
    def register(self, user_data: Dict) -> Dict:
        # Ajustamos para enviar los datos como espera la API estándar (User model)
        return self._make_request('POST', 'auth/register/', data=user_data) # Si tienes endpoint de registro
        # NOTA: Si usas el Auth Token por defecto de DRF, no trae registro. 
        # Tendrías que crear ese endpoint en tu backend o crear usuarios por admin.
    
    def logout(self) -> Dict:
        return self._make_request('POST', 'auth/logout/')
    
    # --- PRODUCTOS ---
    def get_bicicletas(self, params: Dict = None) -> Dict:
        return self._make_request('GET', 'bicicletas/', params=params)
    
    def get_bicicleta(self, bicicleta_id: int) -> Dict:
        return self._make_request('GET', f'bicicletas/{bicicleta_id}/')
    
    def get_repuestos(self, params: Dict = None) -> Dict:
        return self._make_request('GET', 'repuestos/', params=params)
    
    def get_repuesto(self, repuesto_id: int) -> Dict:
        return self._make_request('GET', f'repuestos/{repuesto_id}/')
    
    def get_accesorios(self, params: Dict = None) -> Dict:
        return self._make_request('GET', 'accesorios/', params=params)
    
    def get_accesorio(self, accesorio_id: int) -> Dict:
        return self._make_request('GET', f'accesorios/{accesorio_id}/')
    
    def buscar_productos(self, query: str, params: Dict = None) -> Dict:
        if params is None:
            params = {}
        params['q'] = query
        return self._make_request('GET', 'buscar/', params=params)
    
    # --- CARRITO (Gestión local en sesión o remota si la API lo soporta) ---
    # Si la API no tiene carrito, estos métodos fallarán o tendrás que implementarlos
    # simulados en la vista. Asumimos que la API tiene endpoints de carrito.
    def get_carrito(self) -> Dict:
        return self._make_request('GET', 'carrito/')
    
    def agregar_al_carrito(self, tipo: str, producto_id: int, cantidad: int = 1) -> Dict:
        data = {
            'tipo_producto': tipo,
            'producto_id': producto_id,
            'cantidad': cantidad
        }
        return self._make_request('POST', 'carrito/agregar/', data=data)
    
    def actualizar_cantidad_carrito(self, item_id: int, cantidad: int) -> Dict:
        data = {'cantidad': cantidad}
        return self._make_request('PATCH', f'carrito/{item_id}/', data=data)
    
    def eliminar_del_carrito(self, item_id: int) -> Dict:
        return self._make_request('DELETE', f'carrito/{item_id}/')
    
    def vaciar_carrito(self) -> Dict:
        return self._make_request('DELETE', 'carrito/vaciar/')
    
    def proceder_al_pago(self) -> Dict:
        return self._make_request('POST', 'carrito/pago/')
    
    # --- SERVICIOS / CLIENTE ---
    def get_cliente_actual(self) -> Dict:
        return self._make_request('GET', 'clientes/me/')
        
    def get_bicicletas_cliente(self) -> Dict:
        return self._make_request('GET', 'bicicletas-cliente/')
    
    def registrar_bicicleta_cliente(self, data: Dict) -> Dict:
        return self._make_request('POST', 'bicicletas-cliente/', data=data)
    
    def get_servicios_mantenimiento(self) -> Dict:
        return self._make_request('GET', 'servicios-mantenimiento/')
    
    def crear_orden_mantenimiento(self, data: Dict) -> Dict:
        return self._make_request('POST', 'ordenes-mantenimiento/', data=data)
    
    def get_ordenes_mantenimiento(self) -> Dict:
        return self._make_request('GET', 'ordenes-mantenimiento/')

# --- FUNCIONES AUXILIARES ---

def get_api_client(request) -> APIClient:
    token = request.session.get('api_token')
    return APIClient(token=token)

def save_token_to_session(request, token: str):
    request.session['api_token'] = token

def clear_token_from_session(request):
    if 'api_token' in request.session:
        del request.session['api_token']