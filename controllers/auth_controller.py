from controllers.base_controller import BaseController
from models.user import User
import hashlib


class AuthController(BaseController):

    def login(self, username, password):
        # B-4: sanear entradas antes de procesar
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return None

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user = self.session.query(User).filter_by(username=username).first()

        # B-9: verificar explícitamente is_active; un usuario inactivo nunca inicia sesión
        if user and user.password_hash == hashed_pw and user.is_active:
            return user
        return None

    def create_admin_if_not_exists(self):
        admin = self.session.query(User).filter_by(username="admin").first()
        if not admin:
            # B-5: contraseña almacenada como hash SHA-256 (nunca en texto plano)
            hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
            new_admin = User(
                username="admin",
                password_hash=hashed_pw,
                full_name="Administrador Principal",
                role="Administrador"
            )
            self.session.add(new_admin)
            self.session.commit()
