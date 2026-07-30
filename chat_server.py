"""
chat_server.py
Se ejecuta en la VM de Ubuntu (rol servidor).
Hace bind() sobre la IP de la red interna "labchat" y el puerto 5000,
queda escuchando con accept() y usa hilos (threading) para poder
enviar y recibir mensajes al mismo tiempo, sin cerrar la conexión.
"""

import socket
import threading
import sys

HOST = "192.168.50.10"   # IP de la VM Ubuntu en la red interna "labchat"
PORT = 5000               # Puerto TCP acordado por el grupo

conexion_activa = True


def recibir_mensajes(conn):
    """Hilo dedicado a escuchar mensajes entrantes del cliente."""
    global conexion_activa
    while conexion_activa:
        try:
            datos = conn.recv(1024)
            if not datos:
                print("\n[Info] El otro extremo cerró la conexión.")
                conexion_activa = False
                break
            mensaje = datos.decode("utf-8")
            print(f"\nCliente: {mensaje}\nServidor: ", end="", flush=True)
        except (ConnectionResetError, OSError):
            conexion_activa = False
            break


def enviar_mensajes(conn):
    """Hilo principal: lee lo que escribe el usuario y lo envía."""
    global conexion_activa
    while conexion_activa:
        try:
            mensaje = input("Servidor: ")
        except EOFError:
            break
        if not conexion_activa:
            break
        if mensaje.strip().lower() == "salir":
            conexion_activa = False
            break
        try:
            conn.sendall(mensaje.encode("utf-8"))
        except OSError:
            conexion_activa = False
            break


def main():
    global conexion_activa
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor.bind((HOST, PORT))
    except OSError as e:
        print(f"[Error] No se pudo hacer bind en {HOST}:{PORT} -> {e}")
        sys.exit(1)

    servidor.listen(1)
    print(f"[Servidor] Escuchando en {HOST}:{PORT} ... esperando conexión.")

    conn, addr = servidor.accept()
    print(f"[Servidor] Cliente conectado desde {addr[0]}:{addr[1]}")
    print("Escribe un mensaje y presiona Enter. Escribe 'salir' para terminar.\n")

    hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(conn,), daemon=True)
    hilo_recepcion.start()

    enviar_mensajes(conn)

    conexion_activa = False
    conn.close()
    servidor.close()
    print("\n[Servidor] Conexión cerrada.")


if __name__ == "__main__":
    main()
"""
chat_client.py
Se ejecuta en la VM de Windows (rol cliente).
Usa connect() para dirigirse a la IP y el puerto donde el servidor
(Ubuntu) está escuchando, y usa hilos (threading) para poder enviar
y recibir mensajes al mismo tiempo, sin cerrar la conexión.
"""

import socket
import threading
import sys

SERVER_HOST = "192.168.50.10"   # IP de la VM Ubuntu (servidor)
SERVER_PORT = 5000               # Puerto TCP acordado por el grupo

conexion_activa = True


def recibir_mensajes(conn):
    """Hilo dedicado a escuchar mensajes entrantes del servidor."""
    global conexion_activa
    while conexion_activa:
        try:
            datos = conn.recv(1024)
            if not datos:
                print("\n[Info] El otro extremo cerró la conexión.")
                conexion_activa = False
                break
            mensaje = datos.decode("utf-8")
            print(f"\nServidor: {mensaje}\nCliente: ", end="", flush=True)
        except (ConnectionResetError, OSError):
            conexion_activa = False
            break


def enviar_mensajes(conn):
    """Hilo principal: lee lo que escribe el usuario y lo envía."""
    global conexion_activa
    while conexion_activa:
        try:
            mensaje = input("Cliente: ")
        except EOFError:
            break
        if not conexion_activa:
            break
        if mensaje.strip().lower() == "salir":
            conexion_activa = False
            break
        try:
            conn.sendall(mensaje.encode("utf-8"))
        except OSError:
            conexion_activa = False
            break


def main():
    global conexion_activa
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"[Cliente] Conectando a {SERVER_HOST}:{SERVER_PORT} ...")
    try:
        cliente.connect((SERVER_HOST, SERVER_PORT))
    except OSError as e:
        print(f"[Error] No se pudo conectar a {SERVER_HOST}:{SERVER_PORT} -> {e}")
        sys.exit(1)

    print("[Cliente] Conectado al servidor.")
    print("Escribe un mensaje y presiona Enter. Escribe 'salir' para terminar.\n")

    hilo_recepcion = threading.Thread(target=recibir_mensajes, args=(cliente,), daemon=True)
    hilo_recepcion.start()

    enviar_mensajes(cliente)

    conexion_activa = False
    cliente.close()
    print("\n[Cliente] Conexión cerrada.")


if __name__ == "__main__":
    main()
