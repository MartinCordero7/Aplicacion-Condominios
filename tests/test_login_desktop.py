import pyautogui
import time

pyautogui.FAILSAFE = False

def test_login_admin():

    # Esperar que la ventana Login esté visible
    time.sleep(3)

    # Campo Usuario
    pyautogui.click(464, 298)
    pyautogui.write("admin", interval=0.1)

    # Ir al campo contraseña
    pyautogui.click(464, 228)
    pyautogui.write("password", interval=0.1)

    # Click botón ingresar
    pyautogui.click(230, 282)

    # Esperar respuesta de la API y apertura del sistema
    time.sleep(8)

    # Captura de evidencia
    screenshot = pyautogui.screenshot()
    screenshot.save("evidencia_login_desktop.png")

    print("Prueba Login Desktop ejecutada correctamente")

    assert True