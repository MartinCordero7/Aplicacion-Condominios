from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from controllers.auth_controller import AuthController

from PyQt6.QtCore import QThread, pyqtSignal

class LoginWorker(QThread):
    finished = pyqtSignal(object)  # Retorna el user o None
    error = pyqtSignal(str)

    def __init__(self, auth_controller, username, password):
        super().__init__()
        self.auth_controller = auth_controller
        self.username = username
        self.password = password

    def run(self):
        try:
            user = self.auth_controller.login(self.username, self.password)
            self.finished.emit(user)
        except Exception as e:
            self.error.emit(str(e))

class LoginView(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth_controller = AuthController()
        
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

        if not username or not password:
            QMessageBox.warning(self, "Error", "Ingrese usuario y contraseña")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Conectando con servidor...")

        self.worker = LoginWorker(self.auth_controller, username, password)
        self.worker.finished.connect(self.on_login_finished)
        self.worker.error.connect(self.on_login_error)
        self.worker.start()

    def on_login_finished(self, user):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Ingresar")
        
        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos")

    def on_login_error(self, error_msg):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Ingresar")
        QMessageBox.warning(self, "Error de Conexión", f"No se pudo contactar al API:\n{error_msg}")

