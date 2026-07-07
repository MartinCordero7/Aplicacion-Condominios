import sys
import os

sys.path.insert(0, "/home/xavo/GitHub/Personal/Aplicacion-Condominios")

from controllers.auth_controller import AuthController

def main():
    print("Testing login...")
    auth = AuthController()
    try:
        user = auth.login("admin", "password")
        if user:
            print(f"Success! Logged in as: {user.username}, Role: {user.role}")
        else:
            print("Failed: Invalid credentials (returned None)")
    except Exception as e:
        print(f"Exception during login: {e}")

if __name__ == "__main__":
    main()
