"""
Configuración de usuarios para Villa Marina.

Ejecuta esto UNA VEZ antes de usar la app, y cada vez que quieras crear un
usuario nuevo o resetear una contraseña:

    python setup_usuarios.py

Las contraseñas se piden por teclado (ocultas, no se ven en pantalla) y se
guardan como hash en villa_marina.db. Nunca quedan en texto plano ni en
el código.
"""
import getpass
from database import init_db, crear_o_actualizar_usuario

ROLES_VALIDOS = ["admin", "supervisor", "vendedor"]


def main():
    init_db()
    print("=== Configuración de usuarios - Villa Marina ===")
    print("Deja el nombre de usuario vacío y presiona Enter para terminar.\n")

    while True:
        username = input("Nombre de usuario (ej. jackeline): ").strip()
        if not username:
            break

        nombre = input("Nombre para mostrar (ej. Jackeline): ").strip()

        rol = ""
        while rol not in ROLES_VALIDOS:
            rol = input(f"Rol {ROLES_VALIDOS}: ").strip().lower()

        password = getpass.getpass("Contraseña: ")
        confirmar = getpass.getpass("Confirmar contraseña: ")
        if password != confirmar:
            print("❌ Las contraseñas no coinciden, intenta de nuevo.\n")
            continue
        if len(password) < 6:
            print("❌ Usa al menos 6 caracteres.\n")
            continue

        crear_o_actualizar_usuario(username, nombre, rol, password)
        print(f"✅ Usuario '{username}' guardado.\n")

    print("Listo. Ahora puedes iniciar la app con: streamlit run app.py")


if __name__ == "__main__":
    main()
