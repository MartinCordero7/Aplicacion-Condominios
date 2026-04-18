import sys
import os
from PyQt6.QtWidgets import QApplication
from database.connection import init_db
from views.login_view import LoginView
from views.main_window import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.load_styles()
        
        self.main_window = None
        self.login_view = LoginView(self.on_login_success)

    def load_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), 'views', 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.app.setStyleSheet(f.read())

    def run(self):
        self.login_view.show()
        sys.exit(self.app.exec())

    def on_login_success(self, user):
        self.main_window = MainWindow(user)
        self.main_window.show()

def main():
    print("Inicializando la base de datos...")
    init_db()
    
    app_controller = AppController()
    app_controller.run()

if __name__ == "__main__":
    main()
