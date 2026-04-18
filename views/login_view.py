from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from controllers.auth_controller import AuthController

class LoginView(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_controller = AuthController()
        
        self.auth_controller.create_admin_if_not_exists()
        
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Inicio de Sesión - Condominios")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("Acceso al Sistema")
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario (ej. admin)")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña (ej. admin123)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Ingresar")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        user = self.auth_controller.login(username, password)
        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")
