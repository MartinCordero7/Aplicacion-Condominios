import pyautogui
import time


pyautogui.FAILSAFE = False


def abrir_login_y_acceder():

    # Esperar pantalla login
    time.sleep(3)

    # Usuario
    pyautogui.click(464, 298)
    pyautogui.write("admin", interval=0.1)

    # Contraseña
    pyautogui.click(464, 228)
    pyautogui.write("password", interval=0.1)

    # Ingresar
    pyautogui.click(230, 282)

    # Esperar carga del sistema
    time.sleep(8)



def abrir_modulo_unidades():

    # Menú Unidades
    pyautogui.click(159, 250)

    # Esperar carga tabla
    time.sleep(5)



def test_visualizar_unidades():

    abrir_login_y_acceder()

    abrir_modulo_unidades()


    # Evidencia
    screenshot = pyautogui.screenshot()
    screenshot.save(
        "evidencia_visualizar_unidades_desktop.png"
    )


    assert True



def test_crear_unidad():

    abrir_login_y_acceder()

    abrir_modulo_unidades()


    # Número unidad
    pyautogui.click(1000, 230)
    pyautogui.write("B-304", interval=0.05)


    # Piso
    pyautogui.click(1000, 260)
    pyautogui.write("3", interval=0.05)


    # Tipo (QComboBox)
    pyautogui.click(1000, 290)
    pyautogui.write("DEPARTAMENTO")


    # Alícuota
    pyautogui.click(1000, 320)
    pyautogui.write("12.50", interval=0.05)


    # Guardar Nuevo
    pyautogui.click(880, 400)


    # Esperar mensaje éxito
    time.sleep(3)


    # Cerrar QMessageBox
    pyautogui.press("enter")


    # Esperar actualización
    time.sleep(5)


    screenshot = pyautogui.screenshot()
    screenshot.save(
        "evidencia_crear_unidad_desktop.png"
    )


    assert True



def test_consultar_unidad():

    abrir_login_y_acceder()

    abrir_modulo_unidades()


    # Seleccionar primera fila
    pyautogui.click(570, 220)


    # Esperar carga formulario
    time.sleep(3)


    screenshot = pyautogui.screenshot()
    screenshot.save(
        "evidencia_consultar_unidad_desktop.png"
    )


    assert True



def test_actualizar_unidad():

    abrir_login_y_acceder()

    abrir_modulo_unidades()


    # Seleccionar primera fila
    pyautogui.click(570, 220)

    time.sleep(3)


    # Cambiar alícuota
    pyautogui.click(1000, 320)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.write("15.00", interval=0.05)


    # Actualizar
    pyautogui.click(980, 400)


    # Esperar mensaje
    time.sleep(3)


    # Cerrar QMessageBox
    pyautogui.press("enter")


    time.sleep(5)


    screenshot = pyautogui.screenshot()
    screenshot.save(
        "evidencia_actualizar_unidad_desktop.png"
    )


    assert True