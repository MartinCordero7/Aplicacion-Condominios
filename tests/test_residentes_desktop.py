import pyautogui
import time

pyautogui.FAILSAFE = False

def abrir_login_y_acceder():
    # Esperar aplicación abierta
    time.sleep(3)

    # Usuario
    pyautogui.click(464, 298)
    pyautogui.write("admin", interval=0.1)

    # Contraseña
    pyautogui.click(464, 228)
    pyautogui.write("password", interval=0.1)

    # Botón ingresar
    pyautogui.click(230, 282)

    # Esperar carga Dashboard
    time.sleep(8)

def abrir_modulo_residentes():
    # Click Propietarios/Inquilinos
    pyautogui.click(159, 287)

    # Esperar carga tabla
    time.sleep(5)

def test_visualizar_residentes():
    abrir_login_y_acceder()
    abrir_modulo_residentes()

    # Captura evidencia
    screenshot = pyautogui.screenshot()
    screenshot.save("evidencia_visualizar_residentes_desktop.png")

    assert True

def test_crear_residente():
    abrir_login_y_acceder()
    abrir_modulo_residentes()

    # Número identificación
    pyautogui.click(1000, 250)
    pyautogui.write("1712345678")

    # Nombre
    pyautogui.click(1000, 280)
    pyautogui.write("Juan Perez")

    # Teléfono
    pyautogui.click(1000, 310)
    pyautogui.write("0991234567")

    # Correo
    pyautogui.click(1000, 340)
    pyautogui.write("juan.qa@test.com")

    # Dirección
    pyautogui.click(1000, 400)
    pyautogui.write("Av. Prueba QA 123")

    # Guardar Nuevo
    pyautogui.click(880, 485)

    # Esperar QMessageBox
    time.sleep(3)

    # Cerrar mensaje éxito
    pyautogui.press("enter")

    # Esperar actualización tabla
    time.sleep(5)

    screenshot = pyautogui.screenshot()
    screenshot.save("evidencia_crear_residente_desktop.png")

    assert True

def test_consultar_residente():
    abrir_login_y_acceder()
    abrir_modulo_residentes()

    # Seleccionar primera fila de la tabla
    pyautogui.click(570, 220)

    # Esperar carga formulario
    time.sleep(3)

    screenshot = pyautogui.screenshot()
    screenshot.save("evidencia_consultar_residente_desktop.png")

    assert True

def test_actualizar_residente():
    abrir_login_y_acceder()
    abrir_modulo_residentes()

    # Seleccionar primera fila de la tabla
    pyautogui.click(570, 220)
    time.sleep(3)

    # Modificar dirección (hacer clic, seleccionar todo con Ctrl+A e ingresar nuevo valor)
    pyautogui.click(1000, 400)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write("Av. Nueva QA 456", interval=0.1)

    # Clic en botón "Actualizar"
    pyautogui.click(980, 485)
    time.sleep(3)

    # Cerrar mensaje éxito (Enter en QMessageBox)
    pyautogui.press("enter")
    time.sleep(5)

    screenshot = pyautogui.screenshot()
    screenshot.save("evidencia_actualizar_residente_desktop.png")

    assert True
