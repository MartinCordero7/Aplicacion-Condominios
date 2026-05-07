from database.connection import get_session


class BaseController:
    """Controlador base que provee una sesión de base de datos compartida.

    Todos los controladores concretos deben heredar de esta clase para
    evitar la repetición del patrón ``self.session = get_session()``.
    """

    def __init__(self):
        self.session = get_session()
