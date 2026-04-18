from database.connection import get_session
from models.user import User

class AuthController:
    def __init__(self):
        self.session = get_session()

    def login(self, username, password):
        # En una app real, usar hash de contraseñas (ej. bcrypt)
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.password_hash == password:
            return user
        return None

    def create_admin_if_not_exists(self):
        admin = self.session.query(User).filter_by(username="admin").first()
        if not admin:
            new_admin = User(username="admin", password_hash="admin123", full_name="Administrador Principal", role="Administrador")
            self.session.add(new_admin)
            self.session.commit()
