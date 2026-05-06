from database.connection import get_session
from models.user import User
import hashlib

class AuthController:
    def __init__(self):
        self.session = get_session()

    def login(self, username, password):
        # Hash de contraseña usando SHA-256
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.password_hash == hashed_pw and user.is_active:
            return user
        return None

    def create_admin_if_not_exists(self):
        admin = self.session.query(User).filter_by(username="admin").first()
        if not admin:
            hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
            new_admin = User(username="admin", password_hash=hashed_pw, full_name="Administrador Principal", role="Administrador")
            self.session.add(new_admin)
            self.session.commit()
