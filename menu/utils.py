import requests
from django.conf import settings

class APIClient:
    def __init__(self, token=None):
        self.base_url = settings.API_BASE_URL
        self.headers = {
            'Content-Type': 'application/json'
        }
        # AQUÍ ESTÁ LA CLAVE: Si recibimos token, lo pegamos en el header
        if token:
            self.headers['Authorization'] = f'Token {token}'

    def get_api_client(request):
        token = request.session.get('token') # Intenta sacar el token de la sesión
        return APIClient(token) # Se lo pasa al cliente

    def registrar_bicicleta_cliente(self, data):
        url = f'{self.base_url}bicicletas-cliente/'
        try:
            # Usamos self.headers que ya tiene el token
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            
            # Si falla, devolvemos el error y el código de estado para depurar
            return {
                'success': False, 
                'error': response.json(), 
                'status_code': response.status_code
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ... Tus otros métodos (login, register, etc) se mantienen igual ...
    def login(self, username, password):
        url = f'{self.base_url}auth/login/'
        return requests.post(url, json={'username': username, 'password': password}).json()

    def get_servicios_mantenimiento(self):
        # TIENE QUE TENER: headers=self.headers
        url = f'{self.base_url}servicios-mantenimiento/'
        try:
            # ¡OJO AQUÍ! headers=self.headers es obligatorio
            response = requests.get(url, headers=self.headers) 
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': response.json(), 'status': response.status_code}
        except Exception as e:
             return {'success': False, 'error': str(e)}

    def get_bicicletas_cliente(self):
        url = f'{self.base_url}bicicletas-cliente/'
        try:
            # ¡OJO AQUÍ TAMBIÉN! headers=self.headers
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': response.json(), 'status': response.status_code}
        except Exception as e:
             return {'success': False, 'error': str(e)}
    def crear_orden_mantenimiento(self, data):
        return requests.post(f'{self.base_url}ordenes-mantenimiento/', json=data, headers=self.headers).json()

# Funciones auxiliares para la sesión
def save_token_to_session(request, token):
    request.session['token'] = token

def get_api_client(request):
    token = request.session.get('token')
    return APIClient(token)