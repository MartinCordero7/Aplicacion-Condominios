import pyautogui
import time

print("Mueve el mouse y observa las coordenadas")

while True:
    x, y = pyautogui.position()
    print(f"X={x} Y={y}", end="\r")
    time.sleep(0.5)
