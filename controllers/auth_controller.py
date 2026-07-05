import requests
from models.user import User

class AuthController:
    API_URL = "https://condominio-api-2aef.onrender.com/api/v1"

    def login(self, username, password):
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return None

        response = requests.post(
            f"{self.API_URL}/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=25
        )
        
        if response.status_code in [200, 201]:
            json_data = response.json()
            data = json_data.get('data', json_data)
            
            # Crear un objeto User mockeado con los datos del JWT para mantener compatibilidad 
            user = User(
                username=data.get('username', username),
                password_hash="mock",
                full_name=data.get('username', username),
                role="Administrador" if "ROLE_ADMIN" in data.get('roles', []) else "Residente",
                is_active=True
            )
            
            # Guardar el token si se requiere en otras peticiones
            self.access_token = data.get('accessToken')
            return user
            
        elif response.status_code == 401:
            return None
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

    def create_admin_if_not_exists(self):
        pass

